"""
修復競品商品錯誤 URL：
1. 自動修復 SKU 不同步（FIXABLE）
2. 用 Google 搜尋 site:hktvmall.com 找正確商品 URL（MANUAL）

用法:
  cd backend
  python -X utf8 scripts/fix_urls.py              # 預覽模式
  python -X utf8 scripts/fix_urls.py --confirm     # 執行修復
"""
import sys
import ssl
import asyncio
import re
import json
import httpx
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote

sys.path.insert(0, ".")


def _build_engine():
    from app.config import get_settings
    from sqlalchemy.ext.asyncio import create_async_engine
    settings = get_settings()
    url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    needs_ssl = "sslmode" in params and params["sslmode"][0] in (
        "require", "verify-ca", "verify-full"
    )
    for key in ("sslmode", "channel_binding"):
        params.pop(key, None)
    clean_url = urlunparse(parsed._replace(query=urlencode(params, doseq=True)))
    connect_args = {"timeout": 30}
    if needs_ssl:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_ctx
    return create_async_engine(clean_url, echo=False, pool_pre_ping=True, pool_size=1, connect_args=connect_args)


PRODUCT_URL_RE = re.compile(r"hktvmall\.com.*?/p/(H\d{7,}[A-Za-z0-9_-]*)", re.IGNORECASE)


async def google_search_hktv(client: httpx.AsyncClient, product_name: str) -> str | None:
    """
    用 Google 搜尋 site:hktvmall.com "{product_name}"
    從搜尋結果中提取 /p/H{SKU} 格式的 URL
    """
    # 精簡搜尋關鍵字
    clean = re.sub(r"[（\(][^）\)]*[）\)]", "", product_name).strip()
    clean = re.sub(r"\s*(急凍|冷凍|解凍|日本直送).*$", "", clean).strip()
    query = f'site:hktvmall.com/p/ "{clean[:40]}"'

    search_url = f"https://www.google.com/search?q={quote(query)}&num=5&hl=zh-TW"
    try:
        resp = await client.get(search_url, timeout=15)
        text = resp.text

        # 從 Google 結果中提取 HKTVmall 商品 URL
        urls = PRODUCT_URL_RE.findall(text)
        if urls:
            sku = urls[0]
            return f"https://www.hktvmall.com/hktv/zh/p/{sku}"
    except Exception as e:
        print(f"      Google search error: {e}")
    return None


async def hktv_algolia_search(client: httpx.AsyncClient, product_name: str) -> str | None:
    """
    嘗試 HKTVmall 的公開搜尋 API
    HKTVmall 前端搜尋時會調用內部 API，嘗試複製該行為
    """
    clean = re.sub(r"[（\(][^）\)]*[）\)]", "", product_name).strip()
    keywords = clean[:25]

    # HKTVmall 內部搜尋 API（從前端 network 分析得到）
    api_url = "https://www.hktvmall.com/api/search/v1/product"
    try:
        resp = await client.get(
            api_url,
            params={"q": keywords, "page": 0, "size": 3},
            timeout=15,
        )
        if resp.status_code == 200:
            data = resp.json()
            products = data.get("products", data.get("items", []))
            for p in products:
                url = p.get("url", "")
                if PRODUCT_URL_RE.search(url):
                    return url
                # 嘗試從 SKU 構建
                sku = p.get("sku", p.get("productCode", ""))
                if sku and sku.startswith("H"):
                    return f"https://www.hktvmall.com/hktv/zh/p/{sku}"
    except Exception:
        pass  # API 可能不公開，靜默跳過
    return None


async def try_og_url_from_page(client: httpx.AsyncClient, url: str) -> str | None:
    """
    訪問 /product/xxx 頁面，從 HTML 的 og:url / canonical 提取正確 URL
    HKTVmall SPA 的 SSR 可能在 HTML 裡包含正確的 meta tag
    """
    try:
        resp = await client.get(url, follow_redirects=True, timeout=15)
        html = resp.text[:8000]

        # og:url
        match = re.search(r'property="og:url"\s+content="([^"]+)"', html, re.I)
        if not match:
            match = re.search(r'content="([^"]+)"\s+property="og:url"', html, re.I)
        if match:
            og_url = match.group(1)
            if PRODUCT_URL_RE.search(og_url):
                return og_url

        # canonical
        match = re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"', html, re.I)
        if match:
            canonical = match.group(1)
            if PRODUCT_URL_RE.search(canonical):
                return canonical

        # 最終 URL（如果重導向到正確格式）
        final = str(resp.url)
        if PRODUCT_URL_RE.search(final):
            return final

    except Exception as e:
        print(f"      Page fetch error: {e}")
    return None


async def main():
    from app.connectors.hktv_scraper import HKTVUrlParser
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

    confirm = "--confirm" in sys.argv

    engine = _build_engine()
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # 連接 DB
    for attempt in range(3):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            print(f"DB connected (attempt {attempt + 1})")
            break
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                await asyncio.sleep(5)
            else:
                print("Cannot connect.")
                return

    async with session_maker() as db:
        result = await db.execute(text(
            "SELECT id, name, url, sku FROM competitor_products ORDER BY created_at"
        ))
        rows = result.fetchall()

        fixable = []
        manual = []

        for row in rows:
            pid, name, url, sku = row.id, row.name, row.url, row.sku
            is_hktv = "hktvmall.com" in url.lower()
            if not is_hktv:
                continue
            if not HKTVUrlParser.is_product_url(url):
                manual.append({"id": pid, "name": name, "url": url, "sku": sku})
            else:
                extracted = HKTVUrlParser.extract_sku(url)
                if extracted and sku != extracted:
                    fixable.append({"id": pid, "name": name, "url": url, "sku": sku, "correct_sku": extracted})

        print(f"\nTotal: {len(rows)} products")
        print(f"FIXABLE (SKU sync): {len(fixable)}")
        print(f"MANUAL (wrong URL): {len(manual)}")

        # ==================== FIXABLE ====================
        if fixable:
            print(f"\n{'='*60}")
            print("FIXABLE - SKU sync:")
            print(f"{'='*60}")
            for f in fixable:
                print(f"  {f['name']}")
                print(f"    {f['sku']} -> {f['correct_sku']}")

        # ==================== MANUAL ====================
        resolved = []
        failed = []
        if manual:
            print(f"\n{'='*60}")
            print(f"MANUAL - Resolving {len(manual)} wrong URLs...")
            print(f"{'='*60}")

            async with httpx.AsyncClient(
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
                },
                verify=False,
            ) as client:
                for i, m in enumerate(manual, 1):
                    print(f"\n  [{i}/{len(manual)}] {m['name']}")
                    print(f"    Old: {m['url']}")

                    new_url = None

                    # 策略 1: 從原 URL 頁面的 og:url 提取
                    new_url = await try_og_url_from_page(client, m["url"])
                    if new_url:
                        source = "og:url"
                    else:
                        # 策略 2: Google 搜尋
                        new_url = await google_search_hktv(client, m["name"])
                        if new_url:
                            source = "google"
                        else:
                            # 策略 3: HKTVmall 搜尋 API
                            new_url = await hktv_algolia_search(client, m["name"])
                            if new_url:
                                source = "hktv-api"

                    if new_url:
                        normalized = HKTVUrlParser.normalize_url(new_url)
                        new_sku = HKTVUrlParser.extract_sku(normalized)
                        print(f"    New: {normalized} (via {source})")
                        print(f"    SKU: {new_sku}")
                        resolved.append({
                            "id": m["id"],
                            "name": m["name"],
                            "old_url": m["url"],
                            "new_url": normalized,
                            "new_sku": new_sku,
                            "source": source,
                        })
                    else:
                        print(f"    FAILED: no match found")
                        failed.append(m)

                    await asyncio.sleep(2)  # 禮貌間隔

        # ==================== SUMMARY ====================
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"  SKU fixes:     {len(fixable)}")
        print(f"  URL resolved:  {len(resolved)} / {len(manual)}")
        if failed:
            print(f"  FAILED:        {len(failed)}")
            for f in failed:
                print(f"    - {f['name']}")

        # ==================== APPLY ====================
        if not confirm:
            print(f"\n  >> DRY RUN. Use --confirm to apply.")
        else:
            print(f"\n  >> APPLYING...")
            count = 0
            for f in fixable:
                await db.execute(text(
                    "UPDATE competitor_products SET sku = :sku WHERE id = :id"
                ), {"sku": f["correct_sku"], "id": f["id"]})
                count += 1
            for r in resolved:
                await db.execute(text(
                    "UPDATE competitor_products SET url = :url, sku = :sku WHERE id = :id"
                ), {"url": r["new_url"], "sku": r["new_sku"], "id": r["id"]})
                count += 1
            await db.commit()
            print(f"  >> {count} records updated.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
