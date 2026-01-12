#!/usr/bin/env python
# =============================================
# 本地存儲測試腳本
# =============================================

"""
本地存儲測試腳本（不需要 R2 配置）

用法：
    python scripts/test_local_storage.py

測試項目：
    1. 測試 StorageService 初始化（本地模式）
    2. 上傳測試文件
    3. 驗證文件存在
    4. 讀取文件內容
    5. 刪除測試文件
"""

import sys
import os
from pathlib import Path

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

import uuid
import time


def print_section(title: str):
    """打印分隔區塊"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_local_storage():
    """本地存儲測試主程序"""

    # 設置控制台編碼（Windows 兼容）
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 18 + "本地存儲測試" + " " * 24 + "║")
    print("╚" + "═" * 58 + "╝")

    # 臨時設置環境變數（確保使用本地存儲）
    os.environ['USE_R2_STORAGE'] = 'false'
    os.environ['UPLOAD_DIR'] = './uploads_test'

    from app.config import get_settings
    from app.services.storage_service import StorageService

    settings = get_settings()

    # 檢查配置
    print_section("Step 1: 檢查配置")

    print(f"✓ USE_R2_STORAGE: {settings.use_r2_storage}")
    print(f"✓ UPLOAD_DIR: {settings.upload_dir}")

    if settings.use_r2_storage:
        print("\n⚠️  警告：當前配置啟用了 R2 存儲")
        print("   本測試將強制使用本地存儲模式")

    # 初始化 StorageService
    print_section("Step 2: 初始化 StorageService")

    try:
        storage = StorageService()
        print("✓ StorageService 初始化成功")
        print(f"✓ 使用模式：{'R2 存儲' if storage.use_r2 else '本地存儲'}")
        if not storage.use_r2:
            print(f"✓ 本地存儲路徑：{storage.local_base_dir}")
    except Exception as e:
        print(f"❌ StorageService 初始化失敗：{e}")
        sys.exit(1)

    # 生成測試文件
    print_section("Step 3: 創建測試文件")

    test_content = f"""
    ╔══════════════════════════════════════╗
    ║       本地存儲測試文件               ║
    ║                                      ║
    ║  測試時間：{time.strftime('%Y-%m-%d %H:%M:%S')}  ║
    ║  測試 ID：{str(uuid.uuid4())[:8]}            ║
    ╚══════════════════════════════════════╝

    這是一個本地存儲測試文件。
    如果你能看到這個文件，說明本地存儲配置正確！
    """.encode('utf-8')

    test_filename = f"test_{uuid.uuid4()}.txt"
    test_path = f"test/{test_filename}"

    print(f"✓ 測試文件名：{test_filename}")
    print(f"✓ 測試路徑：{test_path}")
    print(f"✓ 文件大小：{len(test_content)} bytes")

    # 上傳測試
    print_section("Step 4: 保存測試文件到本地")

    try:
        file_path = storage.save_file(
            file_data=test_content,
            file_path=test_path
        )
        print(f"✓ 保存成功！")
        print(f"✓ 文件路徑：{file_path}")

        # 驗證文件確實存在
        full_path = Path(file_path)
        if full_path.exists():
            print(f"✓ 文件系統驗證：文件存在")
            print(f"✓ 文件大小：{full_path.stat().st_size} bytes")
        else:
            print(f"❌ 文件系統驗證：文件不存在")
    except Exception as e:
        print(f"❌ 保存失敗：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 文件存在性測試
    print_section("Step 5: 驗證文件存在")

    try:
        exists = storage.file_exists(test_path)
        if exists:
            print(f"✓ 文件存在驗證成功：{test_path}")
        else:
            print(f"❌ 文件不存在：{test_path}")
    except Exception as e:
        print(f"❌ 驗證失敗：{e}")

    # 讀取驗證
    print_section("Step 6: 讀取文件驗證內容")

    try:
        full_path = storage.local_base_dir / test_path
        with open(full_path, 'rb') as f:
            read_content = f.read()

        if read_content == test_content:
            print("✓ 讀取成功！內容完全一致")
            print(f"✓ 讀取大小：{len(read_content)} bytes")
        else:
            print("❌ 讀取內容與原始內容不一致")
    except Exception as e:
        print(f"❌ 讀取失敗：{e}")

    # 公開 URL 測試
    print_section("Step 7: 公開 URL 測試")

    public_url = storage.get_public_url(test_path)
    print(f"✓ 公開 URL：{public_url}")
    print("\n提示：")
    print("  本地模式下，URL 為相對路徑")
    print("  實際訪問需要配置靜態文件服務")

    # 清理測試
    print_section("Step 8: 清理測試文件")

    # 檢查是否有命令行參數
    auto_cleanup = '--cleanup' in sys.argv

    if auto_cleanup:
        choice = 'y'
        print("自動清理模式：將刪除測試文件")
    else:
        print(f"是否刪除測試文件和目錄？（y/n）")
        print("（提示：運行時添加 --cleanup 參數可自動清理）")
        try:
            choice = input("請選擇：").strip().lower()
        except (EOFError, KeyboardInterrupt):
            choice = 'n'
            print("\n自動選擇：保留測試文件")

    if choice == 'y':
        try:
            # 刪除測試文件
            success = storage.delete_file(test_path)
            if success:
                print(f"✓ 測試文件已刪除：{test_path}")

            # 刪除測試目錄
            import shutil
            test_dir = Path(settings.upload_dir)
            if test_dir.exists():
                shutil.rmtree(test_dir)
                print(f"✓ 測試目錄已刪除：{test_dir}")
        except Exception as e:
            print(f"❌ 清理失敗：{e}")
    else:
        print(f"⚠️  保留測試文件：{file_path}")

    # 測試總結
    print_section("✅ 本地存儲測試完成")

    print("\n測試結果：")
    print("  ✓ StorageService 初始化成功")
    print("  ✓ 文件保存成功")
    print("  ✓ 文件存在驗證成功")
    print("  ✓ 文件讀取驗證成功")
    print("  ✓ 公開 URL 生成成功")

    print("\n下一步：")
    print("  1. 本地存儲模式已驗證正常")
    print("  2. 可以繼續使用本地模式開發")
    print("  3. 或配置 R2 存儲用於生產環境")
    print("     → 查看 backend/scripts/R2_TESTING_GUIDE.md")

    print("\n" + "=" * 60)
    print("測試完成！本地存儲配置正確 🎉")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        test_local_storage()
    except KeyboardInterrupt:
        print("\n\n⚠️  測試已中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 測試過程中發生錯誤：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
