# =============================================
# 排程報告 E2E 測試
# =============================================
#
# 測試完整流程：
# 1. 通過對話創建排程
# 2. 列出排程
# 3. 暫停/恢復排程
# 4. 刪除排程
# 5. 驗證 Celery 任務註冊
# =============================================

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import UUID
from unittest.mock import patch, AsyncMock, MagicMock

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.workflow import ScheduledReport, ScheduleStatus, ReportExecution
from app.services.workflow.scheduler import SchedulerService


# =============================================
# Fixtures
# =============================================

@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture
async def async_client():
    """創建異步測試客戶端"""
    from httpx import ASGITransport
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client


# =============================================
# E2E: 通過對話創建排程
# =============================================

class TestCreateScheduleViaConversation:
    """測試通過對話創建排程"""

    @pytest.mark.asyncio
    async def test_create_daily_schedule_via_chat(self, async_client, test_db):
        """測試通過對話創建每日排程"""
        # 發送創建排程的對話
        response = await async_client.post(
            "/api/v1/agent/chat",
            json={
                "content": "幫我設定每日早上 9 點發送價格分析報告"
            }
        )

        assert response.status_code == 200
        data = response.json()

        # 驗證回應類型
        assert data["type"] in ["message", "report"]

        # 驗證排程是否創建成功（通過回應內容判斷）
        assert "排程" in data["content"] or "已創建" in data["content"]

    @pytest.mark.asyncio
    async def test_create_weekly_schedule_via_chat(self, async_client, test_db):
        """測試通過對話創建每週排程"""
        response = await async_client.post(
            "/api/v1/agent/chat",
            json={
                "content": "設定每週一早上 10 點發送競品分析報告"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["type"] in ["message", "report", "clarification"]


# =============================================
# E2E: 排程 API 端點
# =============================================

class TestScheduleAPIEndpoints:
    """測試排程 API 端點"""

    @pytest.mark.asyncio
    async def test_create_schedule_endpoint(self, async_client, test_db):
        """測試創建排程 API"""
        response = await async_client.post(
            "/api/v1/workflow/schedules",
            json={
                "name": "E2E 測試排程",
                "report_type": "price_analysis",
                "frequency": "daily",
                "schedule_time": "09:00",
                "timezone": "Asia/Hong_Kong",
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["name"] == "E2E 測試排程"
        assert data["status"] == "active"
        assert data["next_run_at"] is not None

        # 保存 ID 供後續測試使用
        return data["id"]

    @pytest.mark.asyncio
    async def test_list_schedules_endpoint(self, async_client, test_db):
        """測試列出排程 API"""
        # 先創建一個排程
        await async_client.post(
            "/api/v1/workflow/schedules",
            json={
                "name": "列表測試排程",
                "frequency": "daily",
            }
        )

        # 列出排程
        response = await async_client.get("/api/v1/workflow/schedules")

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_get_schedule_endpoint(self, async_client, test_db):
        """測試獲取單個排程 API"""
        # 先創建排程
        create_response = await async_client.post(
            "/api/v1/workflow/schedules",
            json={
                "name": "獲取測試排程",
                "frequency": "weekly",
                "schedule_day": 1,
            }
        )
        schedule_id = create_response.json()["id"]

        # 獲取排程
        response = await async_client.get(f"/api/v1/workflow/schedules/{schedule_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == schedule_id
        assert data["name"] == "獲取測試排程"

    @pytest.mark.asyncio
    async def test_pause_schedule_endpoint(self, async_client, test_db):
        """測試暫停排程 API"""
        # 創建排程
        create_response = await async_client.post(
            "/api/v1/workflow/schedules",
            json={
                "name": "暫停測試排程",
                "frequency": "daily",
            }
        )
        schedule_id = create_response.json()["id"]

        # 暫停排程
        response = await async_client.post(
            f"/api/v1/workflow/schedules/{schedule_id}/pause"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["schedule"]["status"] == "paused"

    @pytest.mark.asyncio
    async def test_resume_schedule_endpoint(self, async_client, test_db):
        """測試恢復排程 API"""
        # 創建並暫停排程
        create_response = await async_client.post(
            "/api/v1/workflow/schedules",
            json={
                "name": "恢復測試排程",
                "frequency": "daily",
            }
        )
        schedule_id = create_response.json()["id"]

        await async_client.post(f"/api/v1/workflow/schedules/{schedule_id}/pause")

        # 恢復排程
        response = await async_client.post(
            f"/api/v1/workflow/schedules/{schedule_id}/resume"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["schedule"]["status"] == "active"

    @pytest.mark.asyncio
    async def test_delete_schedule_endpoint(self, async_client, test_db):
        """測試刪除排程 API"""
        # 創建排程
        create_response = await async_client.post(
            "/api/v1/workflow/schedules",
            json={
                "name": "刪除測試排程",
                "frequency": "daily",
            }
        )
        schedule_id = create_response.json()["id"]

        # 刪除排程
        response = await async_client.delete(
            f"/api/v1/workflow/schedules/{schedule_id}"
        )

        assert response.status_code == 200

        # 驗證已刪除
        get_response = await async_client.get(
            f"/api/v1/workflow/schedules/{schedule_id}"
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_trigger_schedule_endpoint(self, async_client, test_db):
        """測試立即觸發排程 API"""
        # 創建排程
        create_response = await async_client.post(
            "/api/v1/workflow/schedules",
            json={
                "name": "觸發測試排程",
                "frequency": "daily",
            }
        )
        schedule_id = create_response.json()["id"]

        # 立即觸發
        with patch('app.tasks.workflow_tasks.execute_scheduled_report.delay') as mock_task:
            mock_task.return_value = MagicMock(id="task-123")

            response = await async_client.post(
                f"/api/v1/workflow/schedules/{schedule_id}/trigger"
            )

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True

    @pytest.mark.asyncio
    async def test_preview_next_runs_endpoint(self, async_client, test_db):
        """測試預覽下次執行時間 API"""
        # 創建排程
        create_response = await async_client.post(
            "/api/v1/workflow/schedules",
            json={
                "name": "預覽測試排程",
                "frequency": "daily",
                "schedule_time": "09:00",
            }
        )
        schedule_id = create_response.json()["id"]

        # 預覽下次執行
        response = await async_client.get(
            f"/api/v1/workflow/schedules/{schedule_id}/preview?count=5"
        )

        assert response.status_code == 200
        data = response.json()

        assert "next_runs" in data
        assert len(data["next_runs"]) == 5


# =============================================
# E2E: 執行歷史
# =============================================

class TestExecutionHistory:
    """測試執行歷史"""

    @pytest.mark.asyncio
    async def test_list_executions_endpoint(self, async_client, test_db):
        """測試列出執行記錄 API"""
        response = await async_client.get("/api/v1/workflow/executions")

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_list_executions_by_schedule(self, async_client, test_db):
        """測試按排程篩選執行記錄"""
        # 創建排程
        create_response = await async_client.post(
            "/api/v1/workflow/schedules",
            json={
                "name": "執行記錄測試排程",
                "frequency": "daily",
            }
        )
        schedule_id = create_response.json()["id"]

        # 按排程篩選
        response = await async_client.get(
            f"/api/v1/workflow/executions?schedule_id={schedule_id}"
        )

        assert response.status_code == 200
        data = response.json()

        assert "items" in data


# =============================================
# E2E: Celery 任務驗證
# =============================================

class TestCeleryTaskIntegration:
    """測試 Celery 任務集成"""

    @pytest.mark.asyncio
    async def test_celery_beat_schedule_registered(self):
        """測試 Celery Beat 排程是否註冊"""
        from app.tasks.celery_app import celery_app

        # 檢查 beat 排程配置
        beat_schedule = celery_app.conf.beat_schedule

        assert "check-due-scheduled-reports" in beat_schedule
        assert beat_schedule["check-due-scheduled-reports"]["task"] == \
            "app.tasks.workflow_tasks.check_and_execute_due_schedules"

    @pytest.mark.asyncio
    async def test_check_due_schedules_task(self, test_db):
        """測試檢查到期排程任務"""
        from app.tasks.workflow_tasks import _async_check_due_schedules

        # 創建一個到期的排程
        scheduler = SchedulerService(test_db)

        schedule = await scheduler.create_schedule(
            name="到期測試排程",
            frequency="daily",
            schedule_time="09:00",
        )

        # 手動設置 next_run_at 為過去時間
        schedule.next_run_at = datetime.utcnow() - timedelta(minutes=5)
        await test_db.commit()

        # 執行檢查任務
        with patch('app.tasks.workflow_tasks.execute_scheduled_report.delay') as mock_execute:
            result = await _async_check_due_schedules()

            assert result["checked"] >= 1
            assert result["triggered"] >= 1
            mock_execute.assert_called()

    @pytest.mark.asyncio
    async def test_execute_scheduled_report_task(self, test_db):
        """測試執行排程報告任務"""
        from app.tasks.workflow_tasks import _async_execute_scheduled_report

        # 創建排程
        scheduler = SchedulerService(test_db)
        schedule = await scheduler.create_schedule(
            name="執行測試排程",
            frequency="daily",
            report_type="price_analysis",
        )

        # Mock Telegram 發送
        with patch('app.tasks.workflow_tasks.get_telegram_notifier') as mock_notifier:
            mock_instance = AsyncMock()
            mock_instance.send_scheduled_report.return_value = {"ok": True}
            mock_notifier.return_value = mock_instance

            result = await _async_execute_scheduled_report(schedule.id)

            assert result["success"] is True
            assert "execution_id" in result


# =============================================
# E2E: 錯誤處理
# =============================================

class TestErrorHandling:
    """測試錯誤處理"""

    @pytest.mark.asyncio
    async def test_get_nonexistent_schedule(self, async_client, test_db):
        """測試獲取不存在的排程"""
        from uuid import uuid4

        response = await async_client.get(
            f"/api/v1/workflow/schedules/{uuid4()}"
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_schedule_invalid_frequency(self, async_client, test_db):
        """測試創建無效頻率的排程"""
        response = await async_client.post(
            "/api/v1/workflow/schedules",
            json={
                "name": "無效頻率排程",
                "frequency": "invalid_frequency",
            }
        )

        # 應該返回驗證錯誤
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_pause_already_paused_schedule(self, async_client, test_db):
        """測試暫停已暫停的排程"""
        # 創建並暫停排程
        create_response = await async_client.post(
            "/api/v1/workflow/schedules",
            json={
                "name": "重複暫停測試",
                "frequency": "daily",
            }
        )
        schedule_id = create_response.json()["id"]

        await async_client.post(f"/api/v1/workflow/schedules/{schedule_id}/pause")

        # 再次暫停
        response = await async_client.post(
            f"/api/v1/workflow/schedules/{schedule_id}/pause"
        )

        # 應該仍然成功（冪等操作）
        assert response.status_code == 200


# =============================================
# E2E: 完整流程測試
# =============================================

class TestFullWorkflow:
    """測試完整工作流程"""

    @pytest.mark.asyncio
    async def test_complete_schedule_lifecycle(self, async_client, test_db):
        """測試排程完整生命週期"""
        # 1. 創建排程
        create_response = await async_client.post(
            "/api/v1/workflow/schedules",
            json={
                "name": "生命週期測試排程",
                "description": "測試完整流程",
                "report_type": "price_analysis",
                "frequency": "daily",
                "schedule_time": "09:00",
                "delivery_channels": {
                    "telegram": {"enabled": True}
                }
            }
        )
        assert create_response.status_code == 200
        schedule_id = create_response.json()["id"]

        # 2. 驗證創建成功
        get_response = await async_client.get(
            f"/api/v1/workflow/schedules/{schedule_id}"
        )
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "active"

        # 3. 暫停排程
        pause_response = await async_client.post(
            f"/api/v1/workflow/schedules/{schedule_id}/pause"
        )
        assert pause_response.status_code == 200
        assert pause_response.json()["schedule"]["status"] == "paused"

        # 4. 恢復排程
        resume_response = await async_client.post(
            f"/api/v1/workflow/schedules/{schedule_id}/resume"
        )
        assert resume_response.status_code == 200
        assert resume_response.json()["schedule"]["status"] == "active"

        # 5. 更新排程
        update_response = await async_client.patch(
            f"/api/v1/workflow/schedules/{schedule_id}",
            json={
                "name": "更新後的排程名稱",
                "schedule_time": "10:00"
            }
        )
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "更新後的排程名稱"

        # 6. 預覽執行時間
        preview_response = await async_client.get(
            f"/api/v1/workflow/schedules/{schedule_id}/preview?count=3"
        )
        assert preview_response.status_code == 200
        assert len(preview_response.json()["next_runs"]) == 3

        # 7. 刪除排程
        delete_response = await async_client.delete(
            f"/api/v1/workflow/schedules/{schedule_id}"
        )
        assert delete_response.status_code == 200

        # 8. 驗證已刪除
        final_get = await async_client.get(
            f"/api/v1/workflow/schedules/{schedule_id}"
        )
        assert final_get.status_code == 404
