"""Quick dry-run summary (JSON output, no emoji)"""
import sys, os, asyncio, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['PYTHONIOENCODING'] = 'utf-8'

import logging
logging.disable(logging.CRITICAL)  # suppress all logs

from app.models.database import async_session_maker
from app.services.product_competitor_finder import ProductCompetitorFinder

async def main():
    finder = ProductCompetitorFinder()
    async with async_session_maker() as db:
        result = await finder.find_all(db, dry_run=True)
    
    summary = {
        "products_processed": result["products_processed"],
        "queries_sent": result["queries_sent"],
        "hits_total": result["hits_total"],
        "hits_relevant": result["hits_relevant"],
        "hits_filtered": result["hits_filtered"],
        "per_product": [{
            "name": p["product_name"][:50],
            "tags": f"{p['category_tag']}/{p.get('sub_tag','-')}",
            "queries": p["queries"],
            "relevant": p["relevant"],
            "total": p["total"],
        } for p in result.get("per_product", [])]
    }
    sys.stdout.buffer.write(json.dumps(summary, ensure_ascii=False, indent=2).encode("utf-8"))
    sys.stdout.buffer.write(b"\n")

asyncio.run(main())
