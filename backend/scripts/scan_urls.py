"""
掃描數據庫中的競品商品 URL，找出格式問題（只讀模式）
用法: cd backend && python -X utf8 scripts/scan_urls.py
"""
import sys
import ssl
import asyncio
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

sys.path.insert(0, ".")


def _build_engine():
    """構建 async engine（帶重試友好的連接池配置）"""
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

    connect_args = {}
    if needs_ssl:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        connect_args["ssl"] = ssl_ctx

    # Neon cold start 可能需要較長超時
    connect_args["timeout"] = 30

    return create_async_engine(
        clean_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=1,
        connect_args=connect_args,
    )


async def main():
    from app.connectors.hktv_scraper import HKTVUrlParser
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

    engine = _build_engine()
    session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # 重試連接（Neon cold start）
    for attempt in range(3):
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            print(f"DB connected (attempt {attempt + 1})")
            break
        except Exception as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                print("Retrying in 5s (Neon cold start)...")
                await asyncio.sleep(5)
            else:
                print("Cannot connect to database after 3 attempts.")
                return

    # 直接用 SQL 查詢（避免 ORM 模型載入問題）
    async with session_maker() as db:
        result = await db.execute(text(
            "SELECT id, name, url, sku FROM competitor_products ORDER BY created_at"
        ))
        rows = result.fetchall()
        print(f"\nTotal competitor products: {len(rows)}")

        hktv_count = sum(1 for r in rows if "hktvmall.com" in r.url.lower())
        print(f"HKTVmall products: {hktv_count}")
        print()

        issues = []
        for row in rows:
            pid, name, url, sku = row.id, row.name, row.url, row.sku
            problems = []
            is_hktv = "hktvmall.com" in url.lower()

            if is_hktv:
                if not HKTVUrlParser.is_product_url(url):
                    problems.append("missing /p/H{SKU}")
                normalized = HKTVUrlParser.normalize_url(url)
                if normalized != url and HKTVUrlParser.is_product_url(url):
                    problems.append("tracking params")
                extracted = HKTVUrlParser.extract_sku(url)
                if extracted and sku != extracted:
                    problems.append(f"SKU mismatch (db={sku}, url={extracted})")
            else:
                if not url.startswith("http"):
                    problems.append("invalid URL")

            if problems:
                issues.append({
                    "id": str(pid),
                    "name": name,
                    "url": url,
                    "sku": sku,
                    "problems": problems,
                    "fixable": is_hktv and HKTVUrlParser.is_product_url(url),
                    "is_hktv": is_hktv,
                })

        # 報告
        sep = "=" * 70
        print(sep)
        print(f"SCAN: {len(issues)} issues / {len(rows)} products")
        print(sep)

        if not issues:
            print("All URLs OK!")
            print()
            for row in rows:
                sku_tag = f" [{row.sku}]" if row.sku else ""
                print(f"  - {row.name}{sku_tag}")
                print(f"    {row.url}")
        else:
            for i, iss in enumerate(issues, 1):
                tag = "[FIXABLE]" if iss["fixable"] else "[MANUAL]"
                print(f"\n#{i} {tag} {iss['name']}")
                print(f"   URL:      {iss['url']}")
                print(f"   SKU(db):  {iss['sku']}")
                print(f"   Problems: {' | '.join(iss['problems'])}")
                if iss["fixable"]:
                    n = HKTVUrlParser.normalize_url(iss["url"])
                    s = HKTVUrlParser.extract_sku(iss["url"])
                    print(f"   --> Fix URL: {n}")
                    print(f"   --> Fix SKU: {s}")
                elif iss["is_hktv"]:
                    print(f"   --> Cannot auto-fix: need correct product URL with /p/H{{SKU}}")

            fc = sum(1 for i in issues if i["fixable"])
            mc = len(issues) - fc
            print(f"\nSummary: {fc} auto-fixable, {mc} manual")

        # OK products
        bad_ids = {i["id"] for i in issues}
        ok = [r for r in rows if str(r.id) not in bad_ids]
        if ok and issues:
            print(f"\nOK products ({len(ok)}):")
            for r in ok:
                tag = f" [{r.sku}]" if r.sku else ""
                u = r.url[:75] + "..." if len(r.url) > 75 else r.url
                print(f"  - {r.name}{tag}: {u}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
