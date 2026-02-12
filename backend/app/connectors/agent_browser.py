# =============================================
# Agent Browser Connector
# 使用 Playwright 進行瀏覽器自動化（含瀏覽器池）
# 專門用於 HKTVmall 搜索頁面的商品 URL 發現
# =============================================
"""
為什麼用 Playwright 而非 agent-browser CLI：
agent-browser 的 Go binary 在 Windows 上無法自動啟動 Node daemon（已知兼容性問題），
而 Playwright Python 直接驅動 Chromium，零依賴外部進程，更穩定可靠。

架構職責：
- 本模塊只負責 URL 發現（搜索頁 SPA 渲染 + lazy load 觸發 + 商品連結提取）
- 價格提取仍由 Firecrawl / hktv_scraper 處理

瀏覽器池策略：
- 懶啟動：首次請求時才創建 Chromium 進程
- 持久化：進程在請求間復用（省去 ~5s 啟動時間）
- 空閒超時：無請求時自動關閉（省資源）
- 崩潰恢復：偵測斷線後自動重建
- 請求隔離：每次搜索用獨立的 BrowserContext
"""

import time
import logging
import asyncio
import threading
from typing import List, Optional

logger = logging.getLogger(__name__)

# 瀏覽器端 JS：提取所有商品連結（O(n) Set 去重）
_JS_EXTRACT_PRODUCT_URLS = """() => {
    return Array.from(
        new Set(
            Array.from(document.querySelectorAll('a[href*="/p/"]'))
                .map(a => a.href.split('?')[0])
        )
    );
}"""


class AgentBrowserConnector:
    """
    Playwright 瀏覽器自動化 — HKTVmall 搜索頁專用（含瀏覽器池）

    scroll_2x 策略（已驗證穩定）：
    1. 打開搜索頁，等 JS 渲染 (15s)
    2. 滾動兩次觸發 lazy load
    3. 在瀏覽器端用 JS 直接提取商品 URL
    """

    # 滾動策略參數
    INITIAL_WAIT_MS = 15000
    SCROLL_DISTANCE_PX = 1000
    SCROLL_PAUSE_MS = 2000
    FINAL_WAIT_MS = 3000
    # 整體操作超時（防止無限掛起）
    TOTAL_TIMEOUT_S = 60
    # 瀏覽器空閒超時（5 分鐘無請求則自動關閉）
    BROWSER_IDLE_S = 300

    def __init__(self):
        self._pw = None
        self._browser = None
        self._lock = asyncio.Lock()
        self._last_used = 0.0

    # =============================================
    # 瀏覽器池管理
    # =============================================

    async def _ensure_browser(self):
        """確保瀏覽器可用（懶啟動 + 空閒超時 + 崩潰恢復）"""
        async with self._lock:
            now = time.monotonic()

            # 空閒超時：回收長時間未用的瀏覽器
            if (self._browser is not None
                    and self._last_used > 0
                    and now - self._last_used > self.BROWSER_IDLE_S):
                logger.info("playwright: 空閒超時，關閉瀏覽器")
                await self._shutdown()

            # 崩潰恢復：進程斷開時重建
            if self._browser is not None and not self._browser.is_connected():
                logger.warning("playwright: 瀏覽器斷開，重新啟動")
                await self._shutdown()

            # 懶啟動
            if self._browser is None:
                from playwright.async_api import async_playwright
                self._pw = await async_playwright().start()
                self._browser = await self._pw.chromium.launch(headless=True)
                logger.info("playwright: 瀏覽器已啟動")

            self._last_used = now
            return self._browser

    async def _shutdown(self):
        """安全關閉瀏覽器和 Playwright（不加鎖，由調用方持鎖）"""
        if self._browser is not None:
            try:
                await self._browser.close()
            except Exception:
                pass
            self._browser = None

        if self._pw is not None:
            try:
                await self._pw.stop()
            except Exception:
                pass
            self._pw = None

    async def close(self):
        """外部調用：關閉所有資源（FastAPI shutdown 時用）"""
        async with self._lock:
            await self._shutdown()
            logger.info("playwright: 資源已釋放")

    # =============================================
    # URL 發現
    # =============================================

    async def discover_hktv_products(
        self, search_url: str, max_products: int = 50
    ) -> List[str]:
        """搜索頁商品 URL 發現（帶整體超時保護）"""
        if not search_url.startswith("https://www.hktvmall.com"):
            raise ValueError(f"非法搜索 URL: {search_url}")

        logger.info(f"playwright: 開始搜索 {search_url}")

        try:
            return await asyncio.wait_for(
                self._do_discover(search_url, max_products),
                timeout=self.TOTAL_TIMEOUT_S,
            )
        except asyncio.TimeoutError:
            logger.error(
                f"playwright: 搜索超時 ({self.TOTAL_TIMEOUT_S}s): {search_url}"
            )
            raise

    async def _do_discover(self, search_url: str, max_products: int) -> List[str]:
        """瀏覽器搜索核心邏輯（復用瀏覽器，每次搜索獨立 context）"""
        browser = await self._ensure_browser()

        # 獨立 context → 隔離 cookies / session state
        context = await browser.new_context()
        page = None
        try:
            page = await context.new_page()

            # 步驟 1: 打開搜索頁（30s 導航超時）
            await page.goto(
                search_url, wait_until="domcontentloaded", timeout=30000
            )

            # 步驟 2: 等待 JS 渲染（HKTVmall 商品列表是動態加載）
            await page.wait_for_timeout(self.INITIAL_WAIT_MS)

            # 步驟 3: 第一次滾動 + 等待（觸發 lazy load）
            await page.evaluate(f"window.scrollBy(0, {self.SCROLL_DISTANCE_PX})")
            await page.wait_for_timeout(self.SCROLL_PAUSE_MS)

            # 步驟 4: 第二次滾動 + 等待
            await page.evaluate(f"window.scrollBy(0, {self.SCROLL_DISTANCE_PX})")
            await page.wait_for_timeout(self.FINAL_WAIT_MS)

            # 步驟 5: 在瀏覽器端直接提取商品 URL
            urls = await page.evaluate(_JS_EXTRACT_PRODUCT_URLS)

            logger.info(f"playwright: 發現 {len(urls)} 個商品 URL")
            return urls[:max_products]

        finally:
            if page is not None:
                await page.close()
            await context.close()


# =============================================
# 單例工廠
# =============================================

_connector: Optional[AgentBrowserConnector] = None
_connector_lock = threading.Lock()


def get_agent_browser_connector() -> AgentBrowserConnector:
    """獲取 AgentBrowserConnector 單例（線程安全）"""
    global _connector
    if _connector is None:
        with _connector_lock:
            if _connector is None:
                _connector = AgentBrowserConnector()
    return _connector
