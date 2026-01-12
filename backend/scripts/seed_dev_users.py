"""
開發環境測試帳號種子腳本
Development User Seed Script

創建測試用的管理員、操作員和檢視者帳號
僅用於開發環境，生產環境請勿執行
"""

import asyncio
import sys
from pathlib import Path

# 添加專案路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.user import User, UserRole
from app.core.security import get_password_hash

# 開發測試帳號
DEV_USERS = [
    {
        "email": "admin@dev.local",
        "password": "admin123",
        "full_name": "開發管理員",
        "role": UserRole.ADMIN,
        "is_active": True,
    },
    {
        "email": "operator@dev.local",
        "password": "operator123",
        "full_name": "開發操作員",
        "role": UserRole.OPERATOR,
        "is_active": True,
    },
    {
        "email": "viewer@dev.local",
        "password": "viewer123",
        "full_name": "開發檢視者",
        "role": UserRole.VIEWER,
        "is_active": True,
    },
]


async def seed_dev_users():
    """創建開發測試帳號"""

    # 創建異步資料庫引擎
    engine = create_async_engine(settings.database_url, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        print("🌱 開始創建開發測試帳號...")

        for user_data in DEV_USERS:
            # 檢查帳號是否已存在
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"⚠️  帳號已存在: {user_data['email']} ({user_data['role'].value})")
                # 更新密碼（以防密碼被改過）
                existing_user.hashed_password = get_password_hash(user_data["password"])
                existing_user.role = user_data["role"]
                existing_user.is_active = user_data["is_active"]
                print(f"✅ 已更新帳號: {user_data['email']}")
            else:
                # 創建新帳號
                new_user = User(
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"]),
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    is_active=user_data["is_active"],
                )
                session.add(new_user)
                print(f"✅ 已創建帳號: {user_data['email']} ({user_data['role'].value})")

        await session.commit()
        print("\n🎉 開發測試帳號創建完成！")
        print("\n📋 可用帳號：")
        for user_data in DEV_USERS:
            print(f"  📧 {user_data['email']}")
            print(f"     密碼: {user_data['password']}")
            print(f"     角色: {user_data['role'].value}")
            print()

    await engine.dispose()


async def remove_dev_users():
    """刪除所有開發測試帳號"""

    engine = create_async_engine(settings.database_url, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        print("🗑️  開始刪除開發測試帳號...")

        from sqlalchemy import select
        for user_data in DEV_USERS:
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            user = result.scalar_one_or_none()

            if user:
                await session.delete(user)
                print(f"✅ 已刪除: {user_data['email']}")
            else:
                print(f"⚠️  帳號不存在: {user_data['email']}")

        await session.commit()
        print("\n🎉 開發測試帳號已全部刪除！")

    await engine.dispose()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="開發測試帳號管理")
    parser.add_argument(
        "action",
        choices=["seed", "remove"],
        help="seed: 創建帳號 | remove: 刪除帳號"
    )

    args = parser.parse_args()

    if args.action == "seed":
        print("=" * 50)
        print("🚀 GoGoJap 開發測試帳號種子腳本")
        print("=" * 50)
        asyncio.run(seed_dev_users())
    elif args.action == "remove":
        print("=" * 50)
        print("🗑️  GoGoJap 開發測試帳號刪除腳本")
        print("=" * 50)
        confirm = input("⚠️  確定要刪除所有開發測試帳號？(yes/no): ")
        if confirm.lower() == "yes":
            asyncio.run(remove_dev_users())
        else:
            print("❌ 已取消操作")
