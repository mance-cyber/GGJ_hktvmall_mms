"""
測試快取快速回覆功能
"""

import asyncio
import time
import sys

# 修復 Windows console 編碼問題
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from app.models.database import async_session_maker
from app.services.agent.quick_cache import QuickCacheService


async def test_quick_cache():
    print("=" * 50)
    print("測試 QuickCacheService")
    print("=" * 50)

    async with async_session_maker() as db:
        cache_service = QuickCacheService(db)

        # 測試各種意圖
        test_intents = ["order_stats", "finance_summary", "alert_query"]

        for intent in test_intents:
            print(f"\n--- 測試 intent: {intent} ---")

            # 第一次調用（需要刷新快取）
            start = time.time()
            response1 = await cache_service.get_quick_response(intent)
            time1 = (time.time() - start) * 1000

            if response1:
                print(f"第一次調用: {time1:.2f}ms")
                print(f"回覆長度: {len(response1.message)} 字")
                print(f"回覆預覽: {response1.message[:100]}...")
            else:
                print(f"無快取回覆")

            # 第二次調用（應該從快取讀取）
            start = time.time()
            response2 = await cache_service.get_quick_response(intent)
            time2 = (time.time() - start) * 1000

            if response2:
                print(f"第二次調用: {time2:.2f}ms (快取)")
                print(f"加速比: {time1/max(time2, 0.01):.1f}x")
            else:
                print(f"無快取回覆")

    print("\n" + "=" * 50)
    print("測試完成！")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_quick_cache())
