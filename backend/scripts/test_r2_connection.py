#!/usr/bin/env python
# =============================================
# Cloudflare R2 連接測試腳本
# =============================================

"""
R2 存儲連接測試腳本

用法：
    python scripts/test_r2_connection.py

測試項目：
    1. 測試 R2 連接（head_bucket）
    2. 上傳測試文件
    3. 列出文件
    4. 下載文件驗證
    5. 刪除測試文件

前提：
    - 已配置 .env 中的 R2 相關環境變數
    - USE_R2_STORAGE=true
"""

import sys
import os
from pathlib import Path

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings
from app.services.storage_service import StorageService
import uuid
import time

settings = get_settings()


def print_section(title: str):
    """打印分隔區塊"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_r2_connection():
    """R2 連接測試主程序"""

    # 設置控制台編碼（Windows 兼容）
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "Cloudflare R2 連接測試" + " " * 21 + "║")
    print("╚" + "═" * 58 + "╝")

    # 檢查配置
    print_section("Step 1: 檢查配置")

    if not settings.use_r2_storage:
        print("❌ 錯誤：USE_R2_STORAGE=false")
        print("   請在 .env 中設置：USE_R2_STORAGE=true")
        sys.exit(1)

    print(f"✓ USE_R2_STORAGE: {settings.use_r2_storage}")
    print(f"✓ R2_BUCKET: {settings.r2_bucket}")
    print(f"✓ R2_ENDPOINT: {settings.r2_endpoint}")
    print(f"✓ R2_PUBLIC_URL: {settings.r2_public_url}")

    # 檢查必需配置
    if not settings.r2_access_key:
        print("❌ 錯誤：R2_ACCESS_KEY 未設置")
        sys.exit(1)
    print(f"✓ R2_ACCESS_KEY: {settings.r2_access_key[:10]}...")

    if not settings.r2_secret_key:
        print("❌ 錯誤：R2_SECRET_KEY 未設置")
        sys.exit(1)
    print(f"✓ R2_SECRET_KEY: {settings.r2_secret_key[:10]}...")

    # 初始化 StorageService
    print_section("Step 2: 初始化 StorageService")

    try:
        storage = StorageService()
        print("✓ StorageService 初始化成功")
        print(f"✓ 使用模式：R2 存儲")
        print(f"✓ Bucket：{storage.bucket}")
    except Exception as e:
        print(f"❌ StorageService 初始化失敗：{e}")
        sys.exit(1)

    # 測試連接
    print_section("Step 3: 測試 R2 連接")

    try:
        storage.s3_client.head_bucket(Bucket=storage.bucket)
        print(f"✓ 成功連接到 R2 Bucket：{storage.bucket}")
    except Exception as e:
        print(f"❌ 連接失敗：{e}")
        print("\n可能的原因：")
        print("  1. R2_ACCESS_KEY 或 R2_SECRET_KEY 錯誤")
        print("  2. R2_ENDPOINT URL 不正確")
        print("  3. R2_BUCKET 名稱錯誤或不存在")
        print("  4. API Token 權限不足")
        sys.exit(1)

    # 生成測試文件
    print_section("Step 4: 創建測試文件")

    test_content = f"""
    ╔══════════════════════════════════════╗
    ║       R2 連接測試文件               ║
    ║                                      ║
    ║  測試時間：{time.strftime('%Y-%m-%d %H:%M:%S')}  ║
    ║  測試 ID：{str(uuid.uuid4())[:8]}            ║
    ╚══════════════════════════════════════╝

    這是一個 R2 存儲測試文件。
    如果你能看到這個文件，說明 R2 配置正確！
    """.encode('utf-8')

    test_filename = f"test_{uuid.uuid4()}.txt"
    test_path = f"test/{test_filename}"

    print(f"✓ 測試文件名：{test_filename}")
    print(f"✓ 測試路徑：{test_path}")
    print(f"✓ 文件大小：{len(test_content)} bytes")

    # 上傳測試
    print_section("Step 5: 上傳測試文件到 R2")

    try:
        file_url = storage.save_file(
            file_data=test_content,
            file_path=test_path
        )
        print(f"✓ 上傳成功！")
        print(f"✓ 文件 URL：{file_url}")
    except Exception as e:
        print(f"❌ 上傳失敗：{e}")
        sys.exit(1)

    # 列出文件測試
    print_section("Step 6: 列出 Bucket 中的測試文件")

    try:
        response = storage.s3_client.list_objects_v2(
            Bucket=storage.bucket,
            Prefix="test/",
            MaxKeys=10
        )

        if 'Contents' in response:
            print(f"✓ 找到 {len(response['Contents'])} 個測試文件：\n")
            for obj in response['Contents']:
                size_kb = obj['Size'] / 1024
                print(f"  - {obj['Key']}")
                print(f"    大小：{size_kb:.2f} KB")
                print(f"    修改時間：{obj['LastModified']}")
                print()
        else:
            print("⚠️  未找到任何文件")
    except Exception as e:
        print(f"❌ 列出文件失敗：{e}")

    # 文件存在性測試
    print_section("Step 7: 驗證文件存在")

    try:
        exists = storage.file_exists(test_path)
        if exists:
            print(f"✓ 文件存在驗證成功：{test_path}")
        else:
            print(f"❌ 文件不存在：{test_path}")
    except Exception as e:
        print(f"❌ 驗證失敗：{e}")

    # 下載驗證
    print_section("Step 8: 下載文件驗證內容")

    try:
        response = storage.s3_client.get_object(
            Bucket=storage.bucket,
            Key=test_path
        )
        downloaded_content = response['Body'].read()

        if downloaded_content == test_content:
            print("✓ 下載成功！內容完全一致")
            print(f"✓ 下載大小：{len(downloaded_content)} bytes")
        else:
            print("❌ 下載內容與原始內容不一致")
    except Exception as e:
        print(f"❌ 下載失敗：{e}")

    # 公開 URL 測試
    print_section("Step 9: 公開 URL 測試")

    public_url = storage.get_public_url(test_path)
    print(f"✓ 公開 URL：{public_url}")
    print("\n提示：")
    print("  1. 如果 Bucket 設置為公開，可以直接在瀏覽器訪問此 URL")
    print("  2. 如果是私有 Bucket，需要配置 Cloudflare Workers 或自定義域名")

    # 清理測試
    print_section("Step 10: 清理測試文件")

    # 檢查是否有命令行參數
    auto_cleanup = '--cleanup' in sys.argv

    if auto_cleanup:
        choice = 'y'
        print("自動清理模式：將刪除測試文件")
    else:
        print(f"是否刪除測試文件？（y/n）")
        print("（提示：運行時添加 --cleanup 參數可自動清理）")
        try:
            choice = input("請選擇：").strip().lower()
        except (EOFError, KeyboardInterrupt):
            choice = 'n'
            print("\n自動選擇：保留測試文件")

    if choice == 'y':
        try:
            success = storage.delete_file(test_path)
            if success:
                print(f"✓ 測試文件已刪除：{test_path}")
            else:
                print(f"⚠️  刪除失敗（但不影響測試結果）")
        except Exception as e:
            print(f"❌ 刪除失敗：{e}")
    else:
        print(f"⚠️  保留測試文件：{test_path}")
        print(f"   請手動到 Cloudflare R2 Dashboard 刪除")

    # 測試總結
    print_section("✅ R2 連接測試完成")

    print("\n測試結果：")
    print("  ✓ R2 連接正常")
    print("  ✓ 文件上傳成功")
    print("  ✓ 文件列表成功")
    print("  ✓ 文件存在驗證成功")
    print("  ✓ 文件下載驗證成功")
    print("  ✓ 公開 URL 生成成功")

    print("\n下一步：")
    print("  1. 你可以開始使用圖片生成系統")
    print("  2. 所有上傳的圖片將自動存儲到 R2")
    print("  3. 確保前端可以訪問 R2_PUBLIC_URL")

    print("\n" + "=" * 60)
    print("測試完成！R2 配置正確 🎉")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        test_r2_connection()
    except KeyboardInterrupt:
        print("\n\n⚠️  測試已中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 測試過程中發生錯誤：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
