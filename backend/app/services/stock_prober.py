# =============================================
# Stock Prober — 產品頁 SSR 庫存探測
# =============================================
# 從 HKTVmall 產品頁 SSR HTML 讀取 stockLevel
# 無需 cookie / session，直接 GET 即可

import asyncio
import logging
import re
from dataclasses import dataclass
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

BASE_URL = "https://www.hktvmall.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
}


@dataclass
class StockResult:
    sku: str
    stock_level: Optional[int]  # None = couldn't read, -1 = has stock but unknown qty
    in_stock: Optional[bool]
    error: Optional[str] = None


def _build_url(sku: str) -> str:
    store = sku.split("_S_")[0] if "_S_" in sku else sku
    return f"{BASE_URL}/hktv/zh/main/search/s/{store}/p/{sku}"


def _parse_stock(html: str) -> tuple[Optional[int], Optional[str]]:
    """Parse stockLevel from product page SSR HTML.
    Returns (stock_level, stock_status)"""
    levels = re.findall(r'"stockLevel"\s*:\s*(\d+)', html)
    stock_level = int(levels[0]) if levels else None

    statuses = re.findall(
        r'"stockLevelStatus"\s*:\s*\{[^}]*"code"\s*:\s*"(\w+)"', html
    )
    if not statuses:
        statuses = re.findall(r'"stockLevelStatus"\s*:\s*"(\w+)"', html)
    stock_status = statuses[0] if statuses else None

    return stock_level, stock_status


async def probe_stock(sku: str, client: httpx.AsyncClient) -> StockResult:
    """Probe stock for a single SKU via product page."""
    try:
        url = _build_url(sku)
        resp = await client.get(url, headers=HEADERS, follow_redirects=True, timeout=15)

        if resp.status_code == 404:
            return StockResult(sku=sku, stock_level=None, in_stock=None, error="404")

        resp.raise_for_status()
        stock_level, stock_status = _parse_stock(resp.text)

        if stock_level is not None:
            return StockResult(sku=sku, stock_level=stock_level, in_stock=stock_level > 0)
        elif stock_status:
            in_stock = stock_status.lower() == "instock"
            return StockResult(sku=sku, stock_level=-1 if in_stock else 0, in_stock=in_stock)
        else:
            return StockResult(sku=sku, stock_level=None, in_stock=None, error="no_ssr_data")

    except Exception as e:
        return StockResult(sku=sku, stock_level=None, in_stock=None, error=str(e)[:200])


async def probe_stocks_batch(
    skus: list[str],
    concurrency: int = 5,
    delay: float = 0.5,
) -> dict[str, StockResult]:
    """
    Probe stock for multiple SKUs with rate limiting.

    Returns: {sku: StockResult}
    """
    results: dict[str, StockResult] = {}
    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient() as client:
        async def _probe_one(sku: str):
            async with semaphore:
                r = await probe_stock(sku, client)
                results[sku] = r
                if delay > 0:
                    await asyncio.sleep(delay)

        tasks = [_probe_one(sku) for sku in skus]
        await asyncio.gather(*tasks, return_exceptions=True)

    ok = sum(1 for r in results.values() if r.stock_level is not None)
    err = sum(1 for r in results.values() if r.error)
    logger.info(f"Stock probe: {ok}/{len(skus)} success, {err} errors")

    return results
