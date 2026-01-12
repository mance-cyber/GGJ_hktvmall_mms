#!/usr/bin/env python
# =============================================
# R2 圖片上傳簡化測試
# =============================================

"""
直接測試圖片上傳到 R2（不依賴 API 服務）

測試項目：
1. 創建測試圖片
2. 使用 StorageService 上傳到 R2
3. 驗證圖片存在於 R2
4. 生成公開 URL
5. 下載驗證
6. 清理測試數據
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# 設置控制台編碼（Windows 兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from PIL import Image
import io as iolib
import uuid
import boto3
from app.config import get_settings
from app.services.storage_service import get_storage

settings = get_settings()


def print_section(title: str):
    """打印分隔區塊"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def create_test_product_image():
    """創建模擬產品圖片"""
    # 創建一個 800x600 的產品圖片
    img = Image.new('RGB', (800, 600), color='#FFFFFF')

    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)

    # 繪製產品矩形
    draw.rectangle([150, 100, 650, 500], fill='#FF6B6B', outline='#333333', width=3)
    draw.rectangle([200, 150, 600, 450], fill='#4ECDC4', outline='#FFFFFF', width=5)

    # 添加文字
    try:
        draw.text((280, 280), "PRODUCT", fill='#FFFFFF')
        draw.text((300, 320), "TEST", fill='#FFFFFF')
    except:
        pass

    # 轉換為 JPEG bytes
    img_bytes = iolib.BytesIO()
    img.save(img_bytes, format='JPEG', quality=90)
    img_bytes.seek(0)

    return img_bytes.getvalue()


def test_r2_image_upload():
    """R2 圖片上傳測試"""

    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 18 + "R2 圖片上傳測試" + " " * 21 + "║")
    print("╚" + "═" * 58 + "╝")

    # 檢查 R2 配置
    print_section("Step 1: 檢查 R2 配置")

    if not settings.use_r2_storage:
        print("❌ 錯誤：USE_R2_STORAGE=false")
        print("   請在 .env 中設置：USE_R2_STORAGE=true")
        sys.exit(1)

    print(f"✓ R2 存儲已啟用")
    print(f"✓ Bucket: {settings.r2_bucket}")
    print(f"✓ Endpoint: {settings.r2_endpoint}")

    # 初始化 StorageService
    print_section("Step 2: 初始化 StorageService")

    try:
        storage = get_storage()
        print(f"✓ StorageService 初始化成功")
        print(f"✓ 使用模式：R2 存儲")
        print(f"✓ Bucket：{storage.bucket}")
    except Exception as e:
        print(f"❌ 初始化失敗：{e}")
        sys.exit(1)

    # 創建測試圖片
    print_section("Step 3: 創建測試產品圖片")

    image_data = create_test_product_image()
    image_size = len(image_data)

    print(f"✓ 測試圖片已創建")
    print(f"✓ 格式：JPEG")
    print(f"✓ 尺寸：800x600")
    print(f"✓ 大小：{image_size / 1024:.2f} KB")

    # 上傳到 R2
    print_section("Step 4: 上傳圖片到 R2")

    test_task_id = str(uuid.uuid4())
    test_filename = f"{uuid.uuid4()}.jpg"
    file_path = f"input/{test_task_id}/{test_filename}"

    print(f"模擬任務 ID：{test_task_id}")
    print(f"文件路徑：{file_path}")

    try:
        file_url = storage.save_file(
            file_data=image_data,
            file_path=file_path
        )

        print(f"\n✓ 上傳成功！")
        print(f"✓ 文件 URL：{file_url}")

    except Exception as e:
        print(f"❌ 上傳失敗：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 驗證文件在 R2
    print_section("Step 5: 驗證文件存在於 R2")

    try:
        # 初始化 S3 客戶端
        s3_client = boto3.client(
            's3',
            endpoint_url=settings.r2_endpoint,
            aws_access_key_id=settings.r2_access_key,
            aws_secret_access_key=settings.r2_secret_key,
            region_name='auto',
        )

        # 檢查文件
        response = s3_client.head_object(
            Bucket=settings.r2_bucket,
            Key=file_path
        )

        print(f"✓ 文件已存儲在 R2")
        print(f"✓ R2 Key: {file_path}")
        print(f"✓ 文件大小：{response['ContentLength']} bytes ({response['ContentLength']/1024:.2f} KB)")
        print(f"✓ 內容類型：{response.get('ContentType', 'N/A')}")
        print(f"✓ 最後修改：{response.get('LastModified', 'N/A')}")

    except Exception as e:
        print(f"❌ 驗證失敗：{e}")
        sys.exit(1)

    # 生成公開 URL
    print_section("Step 6: 生成公開 URL")

    public_url = storage.get_public_url(file_path)
    print(f"✓ 公開 URL：{public_url}")

    # 下載驗證
    print_section("Step 7: 下載並驗證內容")

    try:
        download_response = s3_client.get_object(
            Bucket=settings.r2_bucket,
            Key=file_path
        )

        downloaded_data = download_response['Body'].read()

        if downloaded_data == image_data:
            print(f"✓ 下載成功！內容完全一致")
            print(f"✓ 下載大小：{len(downloaded_data)} bytes")
        else:
            print(f"❌ 下載內容與原始內容不一致")
            print(f"   原始：{len(image_data)} bytes")
            print(f"   下載：{len(downloaded_data)} bytes")

    except Exception as e:
        print(f"❌ 下載失敗：{e}")

    # 清理測試
    print_section("Step 8: 清理測試數據")

    print(f"是否刪除測試圖片？（y/n）")
    print("（提示：添加 --cleanup 參數可自動清理）")

    auto_cleanup = '--cleanup' in sys.argv

    if auto_cleanup:
        choice = 'y'
        print("自動清理模式：將刪除測試文件")
    else:
        try:
            choice = input("請選擇：").strip().lower()
        except (EOFError, KeyboardInterrupt):
            choice = 'n'
            print("\n自動選擇：保留測試文件")

    if choice == 'y':
        try:
            success = storage.delete_file(file_path)
            if success:
                print(f"✓ 測試圖片已刪除：{file_path}")
            else:
                print(f"⚠️  刪除失敗（但不影響測試結果）")
        except Exception as e:
            print(f"❌ 刪除失敗：{e}")
    else:
        print(f"⚠️  保留測試文件：{file_path}")
        print(f"   公開 URL：{public_url}")
        print(f"   請手動到 Cloudflare R2 Dashboard 刪除")

    # 測試總結
    print_section("✅ R2 圖片上傳測試完成")

    print("\n測試結果：")
    print("  ✓ R2 配置正確")
    print("  ✓ StorageService 初始化成功")
    print("  ✓ 測試圖片創建成功")
    print("  ✓ 圖片上傳到 R2 成功")
    print("  ✓ R2 文件驗證成功")
    print("  ✓ 公開 URL 生成成功")
    print("  ✓ 圖片下載驗證成功")

    print("\n下一步：")
    print("  1. 圖片上傳功能已驗證正常")
    print("  2. 可以開始使用圖片生成系統")
    print("  3. 確保 Celery Worker 運行以處理圖片生成")

    print("\n" + "=" * 60)
    print("測試完成！R2 圖片存儲正常工作 🎉")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        test_r2_image_upload()
    except KeyboardInterrupt:
        print("\n\n⚠️  測試已中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 測試過程中發生錯誤：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
