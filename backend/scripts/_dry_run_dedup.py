"""Dry-run with global dedup to see actual unique competitor count"""
import sys, os, asyncio, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
logging.disable(logging.CRITICAL)

from sqlalchemy import select
from app.models.database import async_session_maker
from app.models.product import Product
from app.models.competitor import Competitor
from app.connectors.hktv_api import HKTVApiClient
from app.services.product_competitor_finder import (
    ProductCompetitorFinder, MAX_HITS_PER_QUERY, MAX_PAGES_PER_QUERY
)

async def main():
    finder = ProductCompetitorFinder()
    
    async with async_session_maker() as db:
        stmt = select(Product).where(
            Product.status == "active",
            Product.category_tag.isnot(None),
        )
        result = await db.execute(stmt)
        products = result.scalars().all()

    # Track all unique relevant URLs globally
    global_urls = set()
    product_unique = {}

    for product in products:
        queries = finder._generate_queries(product)
        seen_urls = set()
        relevant_urls = set()

        for query in queries:
            for page in range(MAX_PAGES_PER_QUERY):
                hits = await finder.client.search_products(
                    keyword=query, page_size=MAX_HITS_PER_QUERY, page=page
                )
                if not hits:
                    break
                for hit in hits:
                    if not hit.url or hit.url in seen_urls:
                        continue
                    seen_urls.add(hit.url)
                    if finder._is_relevant(hit):
                        relevant_urls.add(hit.url)
                if len(hits) < MAX_HITS_PER_QUERY:
                    break

        new_unique = relevant_urls - global_urls
        global_urls.update(relevant_urls)
        product_unique[product.name[:40]] = {
            "tags": f"{product.category_tag}/{product.sub_tag}",
            "relevant": len(relevant_urls),
            "new_unique": len(new_unique),
        }

    await finder.close()

    out = {
        "total_unique_competitors": len(global_urls),
        "per_product": product_unique,
    }
    sys.stdout.buffer.write(json.dumps(out, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")

asyncio.run(main())
