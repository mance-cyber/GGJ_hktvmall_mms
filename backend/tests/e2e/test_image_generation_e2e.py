# =============================================
# 圖片生成 E2E 測試
# =============================================

import pytest
import time
from pathlib import Path
from io import BytesIO
from PIL import Image
import httpx


class TestImageGenerationE2E:
    """圖片生成端到端測試"""

    @pytest.fixture
    def api_base_url(self):
        """API 基礎 URL"""
        return "http://localhost:8000/api/v1"

    @pytest.fixture
    def auth_token(self, api_base_url):
        """
        獲取認證 Token
        注意：這裡應該使用測試用戶登入
        """
        # TODO: 實現測試用戶登入
        # 暫時返回 None，實際測試時需要真實 token
        return None

    @pytest.fixture
    def test_image_file(self, tmp_path):
        """創建測試圖片"""
        # 創建一個簡單的測試圖片
        img = Image.new('RGB', (800, 600), color='red')
        img_path = tmp_path / "test_product.jpg"
        img.save(img_path)
        return img_path

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要運行中的 API 服務器和 Celery worker")
    async def test_complete_image_generation_flow(
        self,
        api_base_url,
        auth_token,
        test_image_file
    ):
        """
        測試完整的圖片生成流程：
        1. 創建任務
        2. 上傳圖片
        3. 開始生成
        4. 輪詢狀態
        5. 驗證結果
        """
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        async with httpx.AsyncClient() as client:
            # Step 1: 創建任務
            print("\n[Step 1] 創建圖片生成任務...")
            create_response = await client.post(
                f"{api_base_url}/image-generation/tasks",
                json={
                    "mode": "white_bg_topview",
                    "style_description": None
                },
                headers=headers
            )
            assert create_response.status_code == 200
            task_data = create_response.json()
            task_id = task_data["id"]
            print(f"✓ 任務已創建: {task_id}")

            # Step 2: 上傳圖片
            print("\n[Step 2] 上傳測試圖片...")
            with open(test_image_file, "rb") as f:
                files = {"files": ("test.jpg", f, "image/jpeg")}
                upload_response = await client.post(
                    f"{api_base_url}/image-generation/tasks/{task_id}/upload",
                    files=files,
                    headers=headers
                )
            assert upload_response.status_code == 200
            uploaded_images = upload_response.json()
            assert len(uploaded_images) == 1
            print(f"✓ 已上傳 {len(uploaded_images)} 張圖片")

            # Step 3: 開始生成
            print("\n[Step 3] 開始圖片生成...")
            start_response = await client.post(
                f"{api_base_url}/image-generation/tasks/{task_id}/start",
                headers=headers
            )
            assert start_response.status_code == 200
            task_data = start_response.json()
            assert task_data["status"] == "processing"
            print(f"✓ 生成已開始，Celery 任務: {task_data.get('celery_task_id')}")

            # Step 4: 輪詢狀態（最多等待 2 分鐘）
            print("\n[Step 4] 輪詢任務狀態...")
            max_wait_time = 120  # 2 分鐘
            poll_interval = 2  # 每 2 秒檢查一次
            elapsed_time = 0

            while elapsed_time < max_wait_time:
                status_response = await client.get(
                    f"{api_base_url}/image-generation/tasks/{task_id}",
                    headers=headers
                )
                assert status_response.status_code == 200
                task_data = status_response.json()

                status = task_data["status"]
                progress = task_data["progress"]

                print(f"  狀態: {status}, 進度: {progress}%")

                if status == "completed":
                    print("✓ 生成完成！")
                    break
                elif status == "failed":
                    pytest.fail(f"任務失敗: {task_data.get('error_message')}")

                time.sleep(poll_interval)
                elapsed_time += poll_interval

            if elapsed_time >= max_wait_time:
                pytest.fail("任務超時（超過 2 分鐘）")

            # Step 5: 驗證結果
            print("\n[Step 5] 驗證生成結果...")
            assert task_data["status"] == "completed"
            assert task_data["progress"] == 100
            assert len(task_data["output_images"]) > 0

            output_images = task_data["output_images"]
            print(f"✓ 成功生成 {len(output_images)} 張圖片")

            for idx, img in enumerate(output_images):
                print(f"  圖片 {idx + 1}:")
                print(f"    - 檔名: {img['file_name']}")
                print(f"    - 路徑: {img['file_path']}")
                print(f"    - 大小: {img.get('file_size', 'N/A')} bytes")

                # 驗證圖片文件存在
                img_path = Path(img['file_path'])
                if img_path.exists():
                    print(f"    - 文件存在: ✓")
                else:
                    print(f"    - 文件存在: ✗ (可能使用 R2 存儲)")

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要運行中的 API 服務器")
    async def test_professional_photo_mode(
        self,
        api_base_url,
        auth_token,
        test_image_file
    ):
        """測試專業攝影模式（應生成 3 張圖片）"""
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        async with httpx.AsyncClient() as client:
            # 創建任務（專業攝影模式）
            create_response = await client.post(
                f"{api_base_url}/image-generation/tasks",
                json={
                    "mode": "professional_photo",
                    "style_description": "溫暖陽光、木質餐桌背景"
                },
                headers=headers
            )
            assert create_response.status_code == 200
            task_id = create_response.json()["id"]

            # 上傳圖片
            with open(test_image_file, "rb") as f:
                files = {"files": ("test.jpg", f, "image/jpeg")}
                upload_response = await client.post(
                    f"{api_base_url}/image-generation/tasks/{task_id}/upload",
                    files=files,
                    headers=headers
                )
            assert upload_response.status_code == 200

            # 開始生成
            start_response = await client.post(
                f"{api_base_url}/image-generation/tasks/{task_id}/start",
                headers=headers
            )
            assert start_response.status_code == 200

            # 注意：這裡不等待完成，只驗證任務已開始
            task_data = start_response.json()
            assert task_data["status"] == "processing"
            assert task_data["mode"] == "professional_photo"
            assert task_data["style_description"] == "溫暖陽光、木質餐桌背景"


    def test_api_client_integration(self):
        """
        測試前端 API 客戶端集成
        這是一個單元測試，不需要運行的服務器
        """
        # 驗證 TypeScript 類型定義正確
        # 這裡可以添加對 API 客戶端的單元測試
        pass


# =============================================
# 手動測試指引
# =============================================
"""
運行 E2E 測試前的準備：

1. 啟動後端服務器：
   cd backend
   uvicorn app.main:app --reload

2. 啟動 Celery worker：
   cd backend
   celery -A app.tasks.celery_app worker --loglevel=info

3. 啟動 Redis：
   redis-server

4. 創建測試用戶並獲取 token

5. 運行測試：
   pytest tests/e2e/test_image_generation_e2e.py -v -s

注意：
- E2E 測試需要真實的 API 服務和 Celery worker
- 圖片生成可能需要 30 秒到 2 分鐘
- 確保 NANO_BANANA_API_KEY 已配置
"""
