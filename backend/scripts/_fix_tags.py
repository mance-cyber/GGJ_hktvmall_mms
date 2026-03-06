"""Fix incorrect product tags"""
import sys, os, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import update
from app.models.database import async_session_maker
from app.models.product import Product

FIXES = [
    # (product_id, new_category_tag, new_sub_tag)
    ("a76bbaf8-6dca-4a94-ba3f-14af0ac1d639", "魚", "刺身"),      # 左口裙邊剌身片: 牛/其他 → 魚/刺身
    ("53205e78-6990-4dc6-97b1-bcf24d6ba8e8", "牛", "和牛"),       # A5和牛火鍋套餐: 牛/其他 → 牛/和牛
    ("4ccabbb6-1656-497f-a081-e791b9b7afc1", "豬", "香腸"),       # 豬肉香腸: 豬/其他 → 豬/香腸
    ("5868eeb7-b2aa-4ebd-a8d9-99d9c0fd8df2", "牛", "雜位"),       # 雜位(牛): 牛/其他 → 牛/雜位
    ("7a26a7ec-28ff-47dd-830f-956944029db9", "豬", "豬扒"),       # 豚肉眼薄片: 豬/其他 → 豬/豬扒
    ("cba76152-24fd-4f61-a808-cf9e5a2e8d02", "魚", "魚肝"),       # 鮟鱇魚肝: 魚/其他 → 魚/魚肝
]

async def main():
    async with async_session_maker() as db:
        for pid, cat, sub in FIXES:
            stmt = (
                update(Product)
                .where(Product.id == pid)
                .values(category_tag=cat, sub_tag=sub)
            )
            await db.execute(stmt)
            print(f"Fixed {pid[:8]}... -> {cat}/{sub}")
        await db.commit()
        print(f"\nDone: {len(FIXES)} products updated")

asyncio.run(main())
