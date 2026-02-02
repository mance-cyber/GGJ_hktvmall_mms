## Why

現有 AI 對話系統（Jap仔）係「問完即走」模式，用戶分析完數據後要手動創建任務、設定提醒。呢個斷裂嘅流程降低咗運營效率，AI 分析結果未能直接轉化為業務行動。

## What Changes

- **新增 Workflow Engine**：統一管理對話觸發嘅自動化流程
- **改價審批流程**：AI 建議改價後，可一鍵創建審批任務並通知審批人
- **告警響應流程**：競品價格異動時，自動觸發 AI 分析並推送 Telegram
- **報告排程**：用戶可喺對話中設定定期報告，系統自動執行並發送
- **擴展 PriceProposal 模型**：新增對話來源追溯欄位

## Capabilities

### New Capabilities

- `workflow-engine`: 工作流引擎核心，管理觸發器、執行器、狀態追蹤
- `pricing-approval-workflow`: 改價審批流程，從 AI 建議到創建審批任務
- `alert-response-workflow`: 告警響應流程，自動分析並推送通知
- `report-scheduling`: 報告排程功能，支持對話設定 + 定時執行

### Modified Capabilities

- `ai-agent`: 新增工作流相關意圖識別（創建審批、設定排程、取消排程）

## Impact

**後端：**
- 新增 `backend/app/models/workflow.py`
- 新增 `backend/app/services/workflow/` 模組
- 新增 `backend/app/api/v1/workflow.py`
- 新增 `backend/app/tasks/workflow_tasks.py`
- 修改 `backend/app/models/pricing.py` (PriceProposal 擴展)
- 修改 `backend/app/services/agent/` (意圖擴展)

**前端：**
- 新增 `frontend/src/app/agent/components/SchedulePanel.tsx`
- 新增 `frontend/src/lib/api/workflow.ts`
- 修改改價審批 UI 顯示對話來源

**整合：**
- Celery Beat 排程任務
- Telegram Bot 通知擴展
- 現有 PriceAlert 觸發整合
