#!/usr/bin/env python
# =============================================
# 圖片生成手動測試腳本
# =============================================

"""
圖片生成功能手動測試腳本

用法：
    python scripts/test_image_generation.py --image path/to/image.jpg --mode white_bg_topview
    python scripts/test_image_generation.py --image path/to/image.jpg --mode professional_photo --style "溫暖陽光"

前提：
    - 後端服務器運行中 (uvicorn app.main:app)
    - Celery worker 運行中 (celery -A app.tasks.celery_app worker)
    - Redis 運行中
    - 已配置 NANO_BANANA_API_KEY
"""

import argparse
import time
import sys
from pathlib import Path
import requests


API_BASE = "http://localhost:8000/api/v1"


def main():
    parser = argparse.ArgumentParser(description="測試圖片生成功能")
    parser.add_argument("--image", required=True, help="輸入圖片路徑")
    parser.add_argument(
        "--mode",
        required=True,
        choices=["white_bg_topview", "professional_photo"],
        help="生成模式"
    )
    parser.add_argument("--style", help="風格描述（可選）")
    parser.add_argument("--token", help="認證 Token（可選）")

    args = parser.parse_args()

    # 驗證圖片文件存在
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"❌ 錯誤：圖片文件不存在: {image_path}")
        sys.exit(1)

    # 準備請求頭
    headers = {}
    if args.token:
        headers["Authorization"] = f"Bearer {args.token}"

    print("=" * 60)
    print("圖片生成測試")
    print("=" * 60)

    try:
        # Step 1: 創建任務
        print("\n[1/5] 創建圖片生成任務...")
        create_data = {
            "mode": args.mode,
        }
        if args.style:
            create_data["style_description"] = args.style

        response = requests.post(
            f"{API_BASE}/image-generation/tasks",
            json=create_data,
            headers=headers
        )
        response.raise_for_status()
        task = response.json()
        task_id = task["id"]
        print(f"✓ 任務已創建")
        print(f"  - 任務 ID: {task_id}")
        print(f"  - 模式: {task['mode']}")

        # Step 2: 上傳圖片
        print("\n[2/5] 上傳圖片...")
        with open(image_path, "rb") as f:
            files = {"files": (image_path.name, f, "image/jpeg")}
            response = requests.post(
                f"{API_BASE}/image-generation/tasks/{task_id}/upload",
                files=files,
                headers=headers
            )
        response.raise_for_status()
        uploaded = response.json()
        print(f"✓ 已上傳 {len(uploaded)} 張圖片")
        for img in uploaded:
            print(f"  - {img['file_name']} ({img['file_size']} bytes)")

        # Step 3: 開始生成
        print("\n[3/5] 開始圖片生成...")
        response = requests.post(
            f"{API_BASE}/image-generation/tasks/{task_id}/start",
            headers=headers
        )
        response.raise_for_status()
        task = response.json()
        print(f"✓ 生成已開始")
        print(f"  - Celery 任務: {task.get('celery_task_id')}")

        # Step 4: 輪詢狀態
        print("\n[4/5] 等待生成完成...")
        max_wait = 180  # 3 分鐘
        poll_interval = 3  # 每 3 秒
        elapsed = 0

        while elapsed < max_wait:
            response = requests.get(
                f"{API_BASE}/image-generation/tasks/{task_id}",
                headers=headers
            )
            response.raise_for_status()
            task = response.json()

            status = task["status"]
            progress = task["progress"]

            # 進度條
            bar_length = 30
            filled = int(bar_length * progress / 100)
            bar = "█" * filled + "░" * (bar_length - filled)

            print(f"\r  {bar} {progress}% ({status})", end="", flush=True)

            if status == "completed":
                print("\n✓ 生成完成！")
                break
            elif status == "failed":
                print(f"\n❌ 生成失敗: {task.get('error_message')}")
                sys.exit(1)

            time.sleep(poll_interval)
            elapsed += poll_interval

        if elapsed >= max_wait:
            print("\n❌ 超時：任務未在 3 分鐘內完成")
            sys.exit(1)

        # Step 5: 顯示結果
        print("\n[5/5] 生成結果:")
        print(f"✓ 成功生成 {len(task['output_images'])} 張圖片\n")

        for idx, img in enumerate(task["output_images"], 1):
            print(f"圖片 {idx}:")
            print(f"  - 檔名: {img['file_name']}")
            print(f"  - 路徑: {img['file_path']}")
            if img.get('file_size'):
                size_mb = img['file_size'] / 1024 / 1024
                print(f"  - 大小: {size_mb:.2f} MB")
            print()

        print("=" * 60)
        print("測試完成！")
        print("=" * 60)

    except requests.HTTPError as e:
        print(f"\n❌ HTTP 錯誤: {e}")
        if e.response is not None:
            print(f"響應內容: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
