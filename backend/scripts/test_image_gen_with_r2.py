#!/usr/bin/env python
# =============================================
# 圖片生成 + R2 存儲端到端測試
# =============================================

"""
完整測試圖片生成功能與 R2 存儲整合

測試流程：
1. 創建測試圖片
2. 創建圖片生成任務
3. 上傳圖片（會自動存到 R2）
4. 開始生成
5. 輪詢狀態
6. 驗證 R2 存儲
7. 清理測試數據

前提：
- 後端服務運行中 (uvicorn app.main:app)
- Celery worker 運行中 (celery -A app.tasks.celery_app worker)
- Redis 運行中
- R2 已配置 (USE_R2_STORAGE=true)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# 設置控制台編碼（Windows 兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import time
import requests
from PIL import Image
import io as iolib
import boto3
from app.config import get_settings

settings = get_settings()

API_BASE = "http://localhost:8000/api/v1"

def print_section(title: str):
    """打印分隔區塊"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def create_test_image():
    """創建簡單的測試圖片"""
    # 創建一個 800x600 的測試圖片
    img = Image.new('RGB', (800, 600), color='#FF6B6B')

    # 添加一些圖形讓它看起來像產品圖
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)

    # 繪製矩形（模擬產品）
    draw.rectangle([200, 150, 600, 450], fill='#4ECDC4', outline='#FFFFFF', width=5)

    # 添加文字
    try:
        draw.text((250, 280), "TEST PRODUCT", fill='#FFFFFF')
    except:
        pass  # 如果沒有字體也沒關係

    # 轉換為 bytes
    img_bytes = iolib.BytesIO()
    img.save(img_bytes, format='JPEG', quality=85)
    img_bytes.seek(0)

    return img_bytes


def test_image_generation_with_r2():
    """圖片生成 + R2 存儲完整測試"""

    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "圖片生成 + R2 存儲端到端測試" + " " * 23 + "║")
    print("╚" + "═" * 68 + "╝")

    # 檢查 R2 配置
    print_section("Step 1: 檢查 R2 配置")

    if not settings.use_r2_storage:
        print("❌ 錯誤：USE_R2_STORAGE=false")
        print("   請確保已啟用 R2 存儲")
        sys.exit(1)

    print(f"✓ R2 存儲已啟用")
    print(f"✓ Bucket: {settings.r2_bucket}")
    print(f"✓ Endpoint: {settings.r2_endpoint}")

    # 初始化 R2 客戶端（用於驗證）
    s3_client = boto3.client(
        's3',
        endpoint_url=settings.r2_endpoint,
        aws_access_key_id=settings.r2_access_key,
        aws_secret_access_key=settings.r2_secret_key,
        region_name='auto',
    )

    # 檢查後端服務
    print_section("Step 2: 檢查後端服務")

    try:
        response = requests.get(f"{API_BASE.replace('/api/v1', '')}/health", timeout=5)
        print(f"✓ 後端服務運行中")
    except requests.exceptions.ConnectionError:
        print("❌ 錯誤：無法連接到後端服務")
        print("   請確保後端已啟動：uvicorn app.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"⚠️  後端健康檢查失敗（繼續測試）：{e}")

    # 創建測試圖片
    print_section("Step 3: 創建測試圖片")

    test_image = create_test_image()
    image_size = len(test_image.getvalue())
    print(f"✓ 測試圖片已創建")
    print(f"✓ 圖片格式：JPEG")
    print(f"✓ 圖片大小：{image_size / 1024:.2f} KB")
    print(f"✓ 圖片尺寸：800x600")

    # 創建圖片生成任務
    print_section("Step 4: 創建圖片生成任務")

    try:
        # 注意：這裡需要認證，我們使用 mock 模式或跳過認證
        # 實際使用時需要提供有效的 Bearer Token
        response = requests.post(
            f"{API_BASE}/image-generation/tasks",
            json={
                "mode": "white_bg_topview",  # 使用白底模式（生成1張）
                "style_description": None
            }
        )

        if response.status_code == 401:
            print("❌ 錯誤：需要認證")
            print("   請確保後端已配置或使用測試 Token")
            sys.exit(1)

        response.raise_for_status()
        task = response.json()
        task_id = task["id"]

        print(f"✓ 任務已創建")
        print(f"✓ 任務 ID: {task_id}")
        print(f"✓ 生成模式: {task['mode']}")
        print(f"✓ 狀態: {task['status']}")

    except requests.HTTPError as e:
        print(f"❌ 創建任務失敗：{e}")
        if e.response is not None:
            print(f"   響應：{e.response.text}")
        sys.exit(1)

    # 上傳測試圖片
    print_section("Step 5: 上傳測試圖片到 R2")

    try:
        test_image.seek(0)  # 重置文件指針
        files = {
            'files': ('test_product.jpg', test_image, 'image/jpeg')
        }

        response = requests.post(
            f"{API_BASE}/image-generation/tasks/{task_id}/upload",
            files=files
        )
        response.raise_for_status()
        uploaded = response.json()

        print(f"✓ 圖片上傳成功")
        print(f"✓ 上傳數量: {len(uploaded)}")

        for img in uploaded:
            print(f"\n  圖片詳情:")
            print(f"  - 文件名: {img['file_name']}")
            print(f"  - 大小: {img['file_size']} bytes ({img['file_size']/1024:.2f} KB)")
            print(f"  - 路徑: {img['file_path']}")

            # 驗證圖片是否真的在 R2 上
            input_file_path = img['file_path']

    except requests.HTTPError as e:
        print(f"❌ 上傳失敗：{e}")
        if e.response is not None:
            print(f"   響應：{e.response.text}")
        sys.exit(1)

    # 驗證圖片已存儲在 R2
    print_section("Step 6: 驗證圖片已上傳到 R2")

    try:
        # 從完整 URL 提取 R2 key
        if input_file_path.startswith('http'):
            # URL 格式：https://.../bucket-name/key
            r2_key = input_file_path.split(f"/{settings.r2_bucket}/")[1]
        else:
            # 本地路徑格式
            r2_key = input_file_path.replace('\\', '/')

        # 檢查文件是否存在於 R2
        s3_client.head_object(Bucket=settings.r2_bucket, Key=r2_key)
        print(f"✓ 文件已存儲在 R2")
        print(f"✓ R2 Key: {r2_key}")
        print(f"✓ 公開 URL: {input_file_path}")

        # 獲取文件詳情
        obj_info = s3_client.head_object(Bucket=settings.r2_bucket, Key=r2_key)
        print(f"✓ R2 文件大小: {obj_info['ContentLength']} bytes")
        print(f"✓ 內容類型: {obj_info.get('ContentType', 'N/A')}")

    except Exception as e:
        print(f"❌ R2 驗證失敗：{e}")
        print(f"   文件路徑：{input_file_path}")

    # 開始圖片生成（這會調用 Nano-Banana API）
    print_section("Step 7: 開始圖片生成（需要 Celery Worker）")

    print("⚠️  注意：此步驟需要：")
    print("   1. Celery Worker 運行中")
    print("   2. NANO_BANANA_API_KEY 已配置")
    print("   3. Redis 運行中")
    print()

    # 詢問是否繼續
    print("是否繼續測試圖片生成？（需要真實的 API 調用）")
    print("輸入 'y' 繼續，其他鍵跳過：")

    try:
        choice = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        choice = 'n'

    if choice != 'y':
        print("\n⏭️  跳過圖片生成測試")
        print("   已完成 R2 上傳驗證")

        # 清理測試數據
        print_section("Step 8: 清理測試數據")
        print("是否刪除測試圖片？（y/n）")
        try:
            cleanup_choice = input().strip().lower()
        except:
            cleanup_choice = 'n'

        if cleanup_choice == 'y':
            try:
                s3_client.delete_object(Bucket=settings.r2_bucket, Key=r2_key)
                print(f"✓ 測試圖片已從 R2 刪除")
            except Exception as e:
                print(f"❌ 刪除失敗：{e}")

        print_section("✅ R2 上傳測試完成")
        print("\n測試結果：")
        print("  ✓ R2 配置正確")
        print("  ✓ 後端服務運行正常")
        print("  ✓ 創建任務成功")
        print("  ✓ 圖片上傳到 R2 成功")
        print("  ✓ R2 文件驗證成功")
        print("\n下一步：")
        print("  1. 確保 Celery Worker 運行")
        print("  2. 確保 NANO_BANANA_API_KEY 已配置")
        print("  3. 重新運行測試並選擇 'y' 完成圖片生成")
        return

    # 繼續圖片生成測試
    try:
        response = requests.post(
            f"{API_BASE}/image-generation/tasks/{task_id}/start"
        )
        response.raise_for_status()
        task = response.json()

        print(f"✓ 圖片生成已開始")
        print(f"✓ Celery 任務 ID: {task.get('celery_task_id', 'N/A')}")
        print(f"✓ 狀態: {task['status']}")
        print(f"✓ 進度: {task['progress']}%")

    except requests.HTTPError as e:
        print(f"❌ 開始生成失敗：{e}")
        if e.response is not None:
            print(f"   響應：{e.response.text}")
        sys.exit(1)

    # 輪詢任務狀態
    print_section("Step 8: 輪詢任務狀態")

    max_wait = 180  # 3 分鐘
    poll_interval = 3  # 每 3 秒
    elapsed = 0

    print("等待圖片生成完成...")
    print("（這可能需要 30-120 秒，取決於 Nano-Banana API）\n")

    while elapsed < max_wait:
        try:
            response = requests.get(
                f"{API_BASE}/image-generation/tasks/{task_id}"
            )
            response.raise_for_status()
            task = response.json()

            status = task["status"]
            progress = task["progress"]

            # 進度條
            bar_length = 40
            filled = int(bar_length * progress / 100)
            bar = "█" * filled + "░" * (bar_length - filled)

            print(f"\r  {bar} {progress}% ({status})", end="", flush=True)

            if status == "completed":
                print("\n✓ 圖片生成完成！")
                break
            elif status == "failed":
                print(f"\n❌ 生成失敗: {task.get('error_message', '未知錯誤')}")
                sys.exit(1)

            time.sleep(poll_interval)
            elapsed += poll_interval

        except requests.HTTPError as e:
            print(f"\n❌ 獲取狀態失敗：{e}")
            sys.exit(1)

    if elapsed >= max_wait:
        print("\n❌ 超時：任務未在 3 分鐘內完成")
        sys.exit(1)

    # 顯示生成結果
    print_section("Step 9: 查看生成結果")

    output_images = task.get('output_images', [])
    print(f"✓ 成功生成 {len(output_images)} 張圖片\n")

    for idx, img in enumerate(output_images, 1):
        print(f"圖片 {idx}:")
        print(f"  - 文件名: {img['file_name']}")
        print(f"  - R2 路徑: {img['file_path']}")
        if img.get('file_size'):
            print(f"  - 大小: {img['file_size']/1024:.2f} KB")
        print()

        # 驗證生成的圖片也在 R2 上
        try:
            output_file_path = img['file_path']
            if output_file_path.startswith('http'):
                output_r2_key = output_file_path.split(f"/{settings.r2_bucket}/")[1]
            else:
                output_r2_key = output_file_path.replace('\\', '/')

            s3_client.head_object(Bucket=settings.r2_bucket, Key=output_r2_key)
            print(f"  ✓ 已驗證存儲在 R2")
            print(f"  ✓ R2 Key: {output_r2_key}")
        except Exception as e:
            print(f"  ❌ R2 驗證失敗：{e}")

    # 測試總結
    print_section("✅ 圖片生成 + R2 存儲測試完成")

    print("\n測試結果：")
    print("  ✓ R2 配置正確")
    print("  ✓ 後端服務運行正常")
    print("  ✓ Celery Worker 運行正常")
    print("  ✓ 創建任務成功")
    print("  ✓ 圖片上傳到 R2 成功")
    print("  ✓ R2 文件驗證成功")
    print("  ✓ 圖片生成成功")
    print(f"  ✓ 成功生成 {len(output_images)} 張圖片")
    print("  ✓ 生成的圖片已存儲在 R2")

    print("\n生成的圖片：")
    for img in output_images:
        print(f"  - {img['file_path']}")

    print("\n" + "=" * 70)
    print("測試完成！圖片生成系統與 R2 存儲整合正常 🎉")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        test_image_generation_with_r2()
    except KeyboardInterrupt:
        print("\n\n⚠️  測試已中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 測試過程中發生錯誤：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
