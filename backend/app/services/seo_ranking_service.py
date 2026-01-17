# =============================================
# SEO 排名抓取服務
# =============================================
#
# 功能：
#   - HKTVmall 站內搜尋排名抓取
#   - Google SERP 排名抓取
#   - 排名記錄與分析
#   - 警報生成
# =============================================

import re
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from dataclasses import dataclass

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.seo_ranking import (
    KeywordConfig, KeywordRanking, RankingAlert, RankingScrapeJob,
    KeywordType, RankingSource, AlertSeverity
)
from app.models.product import Product
from app.connectors.firecrawl import FirecrawlConnector
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# =============================================
# 數據類型
# =============================================

@dataclass
class SearchResult:
    """搜尋結果項目"""
    position: int           # 在搜尋結果中的位置（1-based）
    page: int              # 結果頁碼
    url: str               # 結果 URL
    title: Optional[str] = None
    snippet: Optional[str] = None


@dataclass
class SERPData:
    """SERP 抓取結果"""
    keyword: str
    source: str            # google_hk, hktvmall
    our_rank: Optional[int] = None
    our_page: Optional[int] = None
    our_url: Optional[str] = None
    total_results: Optional[int] = None
    serp_features: Optional[Dict[str, bool]] = None
    competitor_rankings: Optional[Dict[str, SearchResult]] = None
    error: Optional[str] = None
    scrape_duration_ms: int = 0


# =============================================
# HKTVmall 搜尋抓取器
# =============================================

class HKTVmallSearchScraper:
    """
    HKTVmall 站內搜尋排名抓取器

    使用 Firecrawl 抓取 HKTVmall 搜尋結果頁面，
    分析我們產品的排名位置。
    """

    # HKTVmall 搜尋 URL 模板
    SEARCH_URL_TEMPLATE = "https://www.hktvmall.com/hktv/zh/main/search/cid/all?q={keyword}&page={page}"

    # 每頁結果數（HKTVmall 默認）
    RESULTS_PER_PAGE = 40

    # 最大搜尋頁數
    MAX_PAGES = 5

    # HKTVmall 產品 URL 模式
    PRODUCT_URL_PATTERN = re.compile(r'/p/(H\d+)')

    def __init__(self):
        self.firecrawl = FirecrawlConnector()

    async def scrape_keyword_ranking(
        self,
        keyword: str,
        target_product_id: Optional[str] = None,
        target_sku: Optional[str] = None,
        max_pages: int = 3,
        competitor_skus: Optional[List[str]] = None
    ) -> SERPData:
        """
        抓取關鍵詞在 HKTVmall 的排名

        Args:
            keyword: 搜尋關鍵詞
            target_product_id: 目標產品的 HKTVmall Product ID (如 H1234567)
            target_sku: 目標產品的 SKU
            max_pages: 最大搜尋頁數
            competitor_skus: 競品 SKU 列表

        Returns:
            SERPData: 排名數據
        """
        import time
        start_time = time.time()

        result = SERPData(
            keyword=keyword,
            source="hktvmall"
        )

        try:
            all_products = []
            total_results = 0

            # 逐頁抓取
            for page in range(1, max_pages + 1):
                search_url = self.SEARCH_URL_TEMPLATE.format(
                    keyword=keyword,
                    page=page
                )

                logger.info(f"抓取 HKTVmall 搜尋: {keyword}, 頁 {page}")

                # 使用 Firecrawl 抓取頁面
                page_data = await self._scrape_search_page(search_url)

                if not page_data:
                    logger.warning(f"抓取頁面失敗: {search_url}")
                    break

                products_on_page = page_data.get("products", [])
                if not products_on_page:
                    break

                # 計算該頁產品的全局位置
                for idx, product in enumerate(products_on_page):
                    position = (page - 1) * self.RESULTS_PER_PAGE + idx + 1
                    product["position"] = position
                    product["page"] = page
                    all_products.append(product)

                # 獲取總結果數（首頁）
                if page == 1 and "total_results" in page_data:
                    total_results = page_data["total_results"]

                # 延遲避免被封
                await asyncio.sleep(1.5)

            result.total_results = total_results or len(all_products)

            # 查找目標產品排名
            if target_product_id or target_sku:
                for product in all_products:
                    product_id = product.get("product_id", "")
                    sku = product.get("sku", "")

                    # 匹配目標產品
                    if (target_product_id and target_product_id in product_id) or \
                       (target_sku and target_sku == sku):
                        result.our_rank = product["position"]
                        result.our_page = product["page"]
                        result.our_url = product.get("url", "")
                        break

            # 查找競品排名
            if competitor_skus:
                result.competitor_rankings = {}
                for product in all_products:
                    sku = product.get("sku", "")
                    if sku in competitor_skus:
                        result.competitor_rankings[sku] = SearchResult(
                            position=product["position"],
                            page=product["page"],
                            url=product.get("url", ""),
                            title=product.get("name", "")
                        )

        except Exception as e:
            logger.error(f"HKTVmall 搜尋抓取失敗: {keyword}, 錯誤: {e}")
            result.error = str(e)

        result.scrape_duration_ms = int((time.time() - start_time) * 1000)
        return result

    async def _scrape_search_page(self, url: str) -> Optional[Dict[str, Any]]:
        """
        抓取單頁搜尋結果

        使用 Firecrawl 的 JSON Mode 結構化提取產品列表
        """
        try:
            # 抓取頁面
            raw_data = self.firecrawl.scrape_url(
                url,
                use_json_mode=False,
                wait_for=5000  # HKTVmall 需要更長等待時間
            )

            if not raw_data:
                return None

            # 從 HTML/Markdown 中提取產品信息
            html_content = raw_data.get("html", "")
            markdown_content = raw_data.get("markdown", "")

            products = self._extract_products_from_content(html_content, markdown_content)

            # 嘗試提取總結果數
            total_results = self._extract_total_results(html_content, markdown_content)

            return {
                "products": products,
                "total_results": total_results
            }

        except Exception as e:
            logger.error(f"抓取搜尋頁面失敗: {url}, 錯誤: {e}")
            return None

    def _extract_products_from_content(
        self,
        html: str,
        markdown: str
    ) -> List[Dict[str, Any]]:
        """
        從頁面內容中提取產品列表

        使用正則表達式匹配產品 URL 模式
        """
        products = []
        seen_ids = set()

        # 從 HTML 中提取產品 URL
        # HKTVmall 產品 URL 格式: /hktv/zh/p/H1234567
        product_urls = re.findall(
            r'href=["\']([^"\']*?/p/(H\d+)[^"\']*)["\']',
            html
        )

        for url, product_id in product_urls:
            if product_id not in seen_ids:
                seen_ids.add(product_id)

                # 補全 URL
                full_url = url if url.startswith("http") else f"https://www.hktvmall.com{url}"

                products.append({
                    "product_id": product_id,
                    "url": full_url,
                    "name": "",  # 需要從詳情頁獲取
                    "sku": product_id
                })

        return products

    def _extract_total_results(self, html: str, markdown: str) -> Optional[int]:
        """提取搜尋總結果數"""
        # 嘗試匹配常見的結果數格式
        patterns = [
            r'(\d+)\s*個商品',
            r'共\s*(\d+)\s*件',
            r'(\d+)\s*results?',
            r'找到\s*(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, html + " " + markdown)
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    continue

        return None


# =============================================
# Google SERP 抓取器
# =============================================

class GoogleSERPScraper:
    """
    Google SERP 排名抓取器

    使用 Playwright 直接抓取 Google 香港搜尋結果
    """

    # Google 香港搜尋 URL
    SEARCH_URL_TEMPLATE = "https://www.google.com.hk/search?q={keyword}&hl=zh-TW&gl=HK"

    # 每頁結果數
    RESULTS_PER_PAGE = 10

    # 最大搜尋頁數
    MAX_PAGES = 10

    def __init__(self):
        self._browser = None
        self._context = None

    async def scrape_keyword_ranking(
        self,
        keyword: str,
        target_domain: str = "hktvmall.com",
        target_url_pattern: Optional[str] = None,
        max_pages: int = 3,
        competitor_domains: Optional[List[str]] = None
    ) -> SERPData:
        """
        抓取關鍵詞在 Google 香港的排名

        Args:
            keyword: 搜尋關鍵詞
            target_domain: 目標網域（如 hktvmall.com）
            target_url_pattern: 目標 URL 模式（正則表達式）
            max_pages: 最大搜尋頁數
            competitor_domains: 競品網域列表

        Returns:
            SERPData: 排名數據
        """
        import time
        start_time = time.time()

        result = SERPData(
            keyword=keyword,
            source="google_hk",
            serp_features={}
        )

        try:
            # 初始化瀏覽器
            await self._ensure_browser()

            all_results = []

            for page in range(1, max_pages + 1):
                logger.info(f"抓取 Google 搜尋: {keyword}, 頁 {page}")

                page_results, serp_features = await self._scrape_search_page(
                    keyword,
                    page
                )

                if not page_results:
                    break

                # 計算全局位置
                for idx, item in enumerate(page_results):
                    position = (page - 1) * self.RESULTS_PER_PAGE + idx + 1
                    item["position"] = position
                    item["page"] = page
                    all_results.append(item)

                # 首頁收集 SERP 特徵
                if page == 1 and serp_features:
                    result.serp_features = serp_features

                # 延遲避免被封
                await asyncio.sleep(2)

            result.total_results = len(all_results)

            # 查找目標網域排名
            for item in all_results:
                url = item.get("url", "")
                if target_domain in url:
                    # 如果有更精確的 URL 模式匹配
                    if target_url_pattern:
                        if re.search(target_url_pattern, url):
                            result.our_rank = item["position"]
                            result.our_page = item["page"]
                            result.our_url = url
                            break
                    else:
                        result.our_rank = item["position"]
                        result.our_page = item["page"]
                        result.our_url = url
                        break

            # 查找競品排名
            if competitor_domains:
                result.competitor_rankings = {}
                for item in all_results:
                    url = item.get("url", "")
                    for domain in competitor_domains:
                        if domain in url and domain not in result.competitor_rankings:
                            result.competitor_rankings[domain] = SearchResult(
                                position=item["position"],
                                page=item["page"],
                                url=url,
                                title=item.get("title", ""),
                                snippet=item.get("snippet", "")
                            )

        except Exception as e:
            logger.error(f"Google 搜尋抓取失敗: {keyword}, 錯誤: {e}")
            result.error = str(e)

        finally:
            await self._close_browser()

        result.scrape_duration_ms = int((time.time() - start_time) * 1000)
        return result

    async def _ensure_browser(self):
        """確保瀏覽器已初始化"""
        if self._browser is None:
            try:
                from playwright.async_api import async_playwright

                playwright = await async_playwright().start()
                self._browser = await playwright.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage"
                    ]
                )
                self._context = await self._browser.new_context(
                    viewport={"width": 1920, "height": 1080},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    locale="zh-TW"
                )
            except ImportError:
                logger.error("Playwright 未安裝，請運行: pip install playwright && playwright install chromium")
                raise

    async def _close_browser(self):
        """關閉瀏覽器"""
        if self._context:
            await self._context.close()
            self._context = None
        if self._browser:
            await self._browser.close()
            self._browser = None

    async def _scrape_search_page(
        self,
        keyword: str,
        page: int
    ) -> Tuple[List[Dict[str, Any]], Dict[str, bool]]:
        """
        抓取單頁 Google 搜尋結果

        Returns:
            Tuple[搜尋結果列表, SERP 特徵字典]
        """
        results = []
        serp_features = {
            "featured_snippet": False,
            "local_pack": False,
            "shopping_ads": False,
            "image_pack": False,
            "video_results": False,
            "people_also_ask": False
        }

        try:
            page_obj = await self._context.new_page()

            # 構造搜尋 URL
            start = (page - 1) * self.RESULTS_PER_PAGE
            url = f"{self.SEARCH_URL_TEMPLATE.format(keyword=keyword)}&start={start}"

            # 訪問頁面
            await page_obj.goto(url, wait_until="networkidle", timeout=30000)

            # 等待搜尋結果載入
            await page_obj.wait_for_selector("#search", timeout=10000)

            # 提取搜尋結果
            search_results = await page_obj.query_selector_all("#search .g")

            for result in search_results:
                try:
                    # 提取標題和連結
                    link_elem = await result.query_selector("a")
                    title_elem = await result.query_selector("h3")
                    snippet_elem = await result.query_selector(".VwiC3b")

                    if link_elem and title_elem:
                        href = await link_elem.get_attribute("href")
                        title = await title_elem.inner_text()
                        snippet = await snippet_elem.inner_text() if snippet_elem else ""

                        # 過濾廣告和非標準結果
                        if href and href.startswith("http") and "/url?" not in href:
                            results.append({
                                "url": href,
                                "title": title,
                                "snippet": snippet
                            })

                except Exception as e:
                    logger.debug(f"提取搜尋結果項目失敗: {e}")
                    continue

            # 首頁檢測 SERP 特徵
            if page == 1:
                serp_features = await self._detect_serp_features(page_obj)

            await page_obj.close()

        except Exception as e:
            logger.error(f"抓取 Google 搜尋頁面失敗: {e}")

        return results, serp_features

    async def _detect_serp_features(self, page) -> Dict[str, bool]:
        """檢測 SERP 特徵"""
        features = {
            "featured_snippet": False,
            "local_pack": False,
            "shopping_ads": False,
            "image_pack": False,
            "video_results": False,
            "people_also_ask": False
        }

        try:
            # Featured Snippet
            featured = await page.query_selector(".xpdopen, .kp-blk")
            features["featured_snippet"] = featured is not None

            # Local Pack
            local = await page.query_selector(".VkpGBb, [data-hveid] .cXedhc")
            features["local_pack"] = local is not None

            # Shopping Ads
            shopping = await page.query_selector(".cu-container, .commercial-unit-desktop-top")
            features["shopping_ads"] = shopping is not None

            # Image Pack
            images = await page.query_selector(".ivg-i")
            features["image_pack"] = images is not None

            # Video Results
            video = await page.query_selector(".RzdJxc")
            features["video_results"] = video is not None

            # People Also Ask
            paa = await page.query_selector(".related-question-pair")
            features["people_also_ask"] = paa is not None

        except Exception as e:
            logger.debug(f"檢測 SERP 特徵失敗: {e}")

        return features


# =============================================
# 排名追蹤服務
# =============================================

class SEORankingService:
    """
    SEO 排名追蹤服務

    整合 HKTVmall 和 Google 排名抓取，
    管理排名記錄和警報生成。
    """

    # 排名變化警報閾值
    RANK_DROP_WARNING_THRESHOLD = 5   # 下降 5 名觸發警告
    RANK_DROP_CRITICAL_THRESHOLD = 10  # 下降 10 名觸發嚴重警告

    def __init__(self, db: AsyncSession):
        self.db = db
        self.hktvmall_scraper = HKTVmallSearchScraper()
        self.google_scraper = GoogleSERPScraper()

    async def track_keyword(
        self,
        keyword_config: KeywordConfig,
        track_google: bool = True,
        track_hktvmall: bool = True
    ) -> KeywordRanking:
        """
        追蹤單個關鍵詞的排名

        Args:
            keyword_config: 關鍵詞配置
            track_google: 是否追蹤 Google
            track_hktvmall: 是否追蹤 HKTVmall

        Returns:
            KeywordRanking: 排名記錄
        """
        # 獲取產品信息
        product = None
        if keyword_config.product_id:
            product = await self.db.get(Product, keyword_config.product_id)

        # 準備目標識別信息
        hktv_product_id = product.hktv_product_id if product else None
        target_sku = product.sku if product else None

        # 抓取 HKTVmall 排名
        hktvmall_data = None
        if track_hktvmall and keyword_config.track_hktvmall:
            hktvmall_data = await self.hktvmall_scraper.scrape_keyword_ranking(
                keyword=keyword_config.keyword,
                target_product_id=hktv_product_id,
                target_sku=target_sku,
                max_pages=3
            )

        # 抓取 Google 排名
        google_data = None
        if track_google and keyword_config.track_google:
            # 如果有產品，使用產品 URL 模式匹配
            url_pattern = None
            if hktv_product_id:
                url_pattern = f"/p/{hktv_product_id}"

            google_data = await self.google_scraper.scrape_keyword_ranking(
                keyword=keyword_config.keyword,
                target_domain="hktvmall.com",
                target_url_pattern=url_pattern,
                max_pages=3
            )

        # 獲取上次排名（用於計算變化）
        previous_ranking = await self._get_previous_ranking(keyword_config.id)

        # 計算排名變化
        google_rank_change = None
        hktvmall_rank_change = None

        if google_data and google_data.our_rank:
            if previous_ranking and previous_ranking.google_rank:
                google_rank_change = previous_ranking.google_rank - google_data.our_rank

        if hktvmall_data and hktvmall_data.our_rank:
            if previous_ranking and previous_ranking.hktvmall_rank:
                hktvmall_rank_change = previous_ranking.hktvmall_rank - hktvmall_data.our_rank

        # 創建排名記錄
        ranking = KeywordRanking(
            keyword_config_id=keyword_config.id,
            product_id=keyword_config.product_id,
            keyword=keyword_config.keyword,
            # Google 數據
            google_rank=google_data.our_rank if google_data else None,
            google_page=google_data.our_page if google_data else None,
            google_url=google_data.our_url if google_data else None,
            google_total_results=google_data.total_results if google_data else None,
            google_rank_change=google_rank_change,
            # HKTVmall 數據
            hktvmall_rank=hktvmall_data.our_rank if hktvmall_data else None,
            hktvmall_page=hktvmall_data.our_page if hktvmall_data else None,
            hktvmall_total_results=hktvmall_data.total_results if hktvmall_data else None,
            hktvmall_rank_change=hktvmall_rank_change,
            # SERP 特徵
            serp_features=google_data.serp_features if google_data else None,
            # 抓取元數據
            source=RankingSource.GOOGLE_HK,
            scrape_duration_ms=(
                (google_data.scrape_duration_ms if google_data else 0) +
                (hktvmall_data.scrape_duration_ms if hktvmall_data else 0)
            ),
            scrape_success=(
                (not google_data or not google_data.error) and
                (not hktvmall_data or not hktvmall_data.error)
            ),
            scrape_error=(
                google_data.error if google_data and google_data.error else
                hktvmall_data.error if hktvmall_data and hktvmall_data.error else None
            )
        )

        self.db.add(ranking)

        # 更新關鍵詞配置的最新排名
        keyword_config.latest_google_rank = ranking.google_rank
        keyword_config.latest_hktvmall_rank = ranking.hktvmall_rank
        keyword_config.latest_tracked_at = datetime.utcnow()

        # 首次記錄設為基準
        if not keyword_config.baseline_google_rank and ranking.google_rank:
            keyword_config.baseline_google_rank = ranking.google_rank
        if not keyword_config.baseline_hktvmall_rank and ranking.hktvmall_rank:
            keyword_config.baseline_hktvmall_rank = ranking.hktvmall_rank

        await self.db.commit()
        await self.db.refresh(ranking)

        # 檢查是否需要生成警報
        await self._check_and_create_alerts(keyword_config, ranking, previous_ranking)

        return ranking

    async def track_all_keywords(
        self,
        product_id: Optional[UUID] = None,
        keyword_type: Optional[KeywordType] = None
    ) -> RankingScrapeJob:
        """
        批量追蹤關鍵詞排名

        Args:
            product_id: 限制特定產品
            keyword_type: 限制特定類型

        Returns:
            RankingScrapeJob: 抓取任務記錄
        """
        # 查詢要追蹤的關鍵詞
        query = select(KeywordConfig).where(KeywordConfig.is_active == True)

        if product_id:
            query = query.where(KeywordConfig.product_id == product_id)
        if keyword_type:
            query = query.where(KeywordConfig.keyword_type == keyword_type)

        result = await self.db.execute(query)
        configs = result.scalars().all()

        # 創建任務記錄
        job = RankingScrapeJob(
            job_type="full",
            status="running",
            total_keywords=len(configs),
            triggered_by="api",
            started_at=datetime.utcnow()
        )
        self.db.add(job)
        await self.db.commit()

        # 逐個追蹤
        errors = []
        for idx, config in enumerate(configs):
            try:
                await self.track_keyword(config)
                job.successful_keywords += 1
            except Exception as e:
                logger.error(f"追蹤關鍵詞失敗: {config.keyword}, 錯誤: {e}")
                job.failed_keywords += 1
                errors.append({
                    "keyword": config.keyword,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })

            job.processed_keywords = idx + 1
            await self.db.commit()

            # 延遲避免過於頻繁
            await asyncio.sleep(2)

        # 完成任務
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.duration_seconds = int((job.completed_at - job.started_at).total_seconds())
        job.errors = errors

        await self.db.commit()
        await self.db.refresh(job)

        return job

    async def _get_previous_ranking(
        self,
        keyword_config_id: UUID
    ) -> Optional[KeywordRanking]:
        """獲取上次排名記錄"""
        query = (
            select(KeywordRanking)
            .where(KeywordRanking.keyword_config_id == keyword_config_id)
            .order_by(KeywordRanking.tracked_at.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _check_and_create_alerts(
        self,
        keyword_config: KeywordConfig,
        current: KeywordRanking,
        previous: Optional[KeywordRanking]
    ):
        """檢查排名變化並生成警報"""
        if not previous:
            return

        # 檢查 Google 排名變化
        if current.google_rank and previous.google_rank:
            change = previous.google_rank - current.google_rank
            if change <= -self.RANK_DROP_CRITICAL_THRESHOLD:
                await self._create_alert(
                    keyword_config=keyword_config,
                    alert_type="rank_drop",
                    severity=AlertSeverity.CRITICAL,
                    source=RankingSource.GOOGLE_HK,
                    previous_rank=previous.google_rank,
                    current_rank=current.google_rank,
                    message=f"關鍵詞 '{keyword_config.keyword}' 在 Google 排名大幅下降 {abs(change)} 名"
                )
            elif change <= -self.RANK_DROP_WARNING_THRESHOLD:
                await self._create_alert(
                    keyword_config=keyword_config,
                    alert_type="rank_drop",
                    severity=AlertSeverity.WARNING,
                    source=RankingSource.GOOGLE_HK,
                    previous_rank=previous.google_rank,
                    current_rank=current.google_rank,
                    message=f"關鍵詞 '{keyword_config.keyword}' 在 Google 排名下降 {abs(change)} 名"
                )
            elif change >= self.RANK_DROP_WARNING_THRESHOLD:
                await self._create_alert(
                    keyword_config=keyword_config,
                    alert_type="rank_improve",
                    severity=AlertSeverity.INFO,
                    source=RankingSource.GOOGLE_HK,
                    previous_rank=previous.google_rank,
                    current_rank=current.google_rank,
                    message=f"關鍵詞 '{keyword_config.keyword}' 在 Google 排名上升 {change} 名"
                )

        # 檢查 HKTVmall 排名變化（邏輯類似）
        if current.hktvmall_rank and previous.hktvmall_rank:
            change = previous.hktvmall_rank - current.hktvmall_rank
            if change <= -self.RANK_DROP_CRITICAL_THRESHOLD:
                await self._create_alert(
                    keyword_config=keyword_config,
                    alert_type="rank_drop",
                    severity=AlertSeverity.CRITICAL,
                    source=RankingSource.HKTVMALL,
                    previous_rank=previous.hktvmall_rank,
                    current_rank=current.hktvmall_rank,
                    message=f"關鍵詞 '{keyword_config.keyword}' 在 HKTVmall 排名大幅下降 {abs(change)} 名"
                )
            elif change <= -self.RANK_DROP_WARNING_THRESHOLD:
                await self._create_alert(
                    keyword_config=keyword_config,
                    alert_type="rank_drop",
                    severity=AlertSeverity.WARNING,
                    source=RankingSource.HKTVMALL,
                    previous_rank=previous.hktvmall_rank,
                    current_rank=current.hktvmall_rank,
                    message=f"關鍵詞 '{keyword_config.keyword}' 在 HKTVmall 排名下降 {abs(change)} 名"
                )

        # 檢查是否達成目標排名
        if keyword_config.target_google_rank and current.google_rank:
            if current.google_rank <= keyword_config.target_google_rank:
                if not previous.google_rank or previous.google_rank > keyword_config.target_google_rank:
                    await self._create_alert(
                        keyword_config=keyword_config,
                        alert_type="target_achieved",
                        severity=AlertSeverity.INFO,
                        source=RankingSource.GOOGLE_HK,
                        previous_rank=previous.google_rank if previous else None,
                        current_rank=current.google_rank,
                        message=f"恭喜！關鍵詞 '{keyword_config.keyword}' 在 Google 達成目標排名 Top {keyword_config.target_google_rank}"
                    )

    async def _create_alert(
        self,
        keyword_config: KeywordConfig,
        alert_type: str,
        severity: AlertSeverity,
        source: RankingSource,
        previous_rank: Optional[int],
        current_rank: Optional[int],
        message: str
    ):
        """創建排名警報"""
        rank_change = 0
        if previous_rank and current_rank:
            rank_change = previous_rank - current_rank

        alert = RankingAlert(
            keyword_config_id=keyword_config.id,
            product_id=keyword_config.product_id,
            alert_type=alert_type,
            severity=severity,
            keyword=keyword_config.keyword,
            source=source,
            previous_rank=previous_rank,
            current_rank=current_rank,
            rank_change=rank_change,
            message=message
        )
        self.db.add(alert)
        await self.db.commit()

        logger.info(f"生成排名警報: {message}")
