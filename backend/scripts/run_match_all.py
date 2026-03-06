"""
全產品重新匹配競品
用法: python scripts/run_match_all.py [--limit 50] [--platform hktvmall] [--rematch]
"""
import asyncio, argparse, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def main(limit, platform, rematch):
    from sqlalchemy import select
    from app.models.database import async_session_maker, init_db
    from app.models.product import Product, ProductCompetitorMapping
    from app.models.competitor import Competitor, CompetitorProduct
    from app.services.competitor_matcher import CompetitorMatcherService
    await init_db()
    async with async_session_maker() as session:
        if rematch:
            query = select(Product).limit(limit)
            print(f"Re-match mode: up to {limit} products")
        else:
            subquery = (
                select(ProductCompetitorMapping.product_id)
                .join(CompetitorProduct, ProductCompetitorMapping.competitor_product_id == CompetitorProduct.id)
                .join(Competitor, CompetitorProduct.competitor_id == Competitor.id)
                .where(Competitor.platform == platform)
            )
            query = select(Product).where(~Product.id.in_(subquery)).limit(limit)
            print(f"New products mode: up to {limit}")
        result = await session.execute(query)
        products = result.scalars().all()
        if not products:
            print("All products already matched")
            return
        print(f"Found {len(products)} products\n")
        service = CompetitorMatcherService()
        total_matches = total_saved = 0
        for i, product in enumerate(products, 1):
            name = product.name_zh or product.name or "?"
            print(f"[{i}/{len(products)}] {name}")
            try:
                results = await service.find_competitors_for_product(db=session, product=product, platform=platform, max_candidates=25)
                matches = [r for r in results if r.is_match]
                total_matches += len(matches)
                saved = 0
                for match in matches:
                    try:
                        await service.save_match_to_db(db=session, product_id=str(product.id), match_result=match, platform=platform)
                        saved += 1
                    except Exception as e:
                        print(f"  Warning save fail: {match.candidate_name[:30]} - {e}")
                total_saved += saved
                print(f"  -> {len(results)} candidates, {len(matches)} matched, {saved} saved")
                await session.commit()
            except Exception as e:
                print(f"  FAIL: {e}")
                await session.rollback()
        print(f"\nDone! {len(products)} products, {total_matches} matches, {total_saved} saved")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--platform", default="hktvmall")
    p.add_argument("--rematch", action="store_true")
    args = p.parse_args()
    asyncio.run(main(args.limit, args.platform, args.rematch))
