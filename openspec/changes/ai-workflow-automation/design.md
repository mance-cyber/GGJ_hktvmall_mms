## Context

現有 AI 對話系統提供產品分析、價格趨勢、競品比較等功能，但係「問完即走」模式。用戶完成分析後，需要手動：
1. 去改價審批頁面創建任務
2. 設定 Telegram 告警
3. 定期手動執行報告

系統已有嘅基礎設施：
- `AgentService` - AI 對話核心服務
- `PriceProposal` - 改價提案模型
- `PriceAlert` - 競品價格告警
- Celery + Redis - 異步任務
- Telegram Bot - 通知服務

## Goals / Non-Goals

**Goals:**
- AI 對話可觸發創建改價審批任務
- 競品告警可自動觸發 AI 分析並推送結果
- 用戶可喺對話中設定定期報告
- 所有工作流可追溯返原本嘅對話

**Non-Goals:**
- 唔會取代現有嘅手動操作流程（保留）
- 唔會實現複雜嘅審批鏈（只支持單人審批）
- 唔會支持自定義工作流編排（固定流程）
- 知識管理、對話評分留待下一輪

## Decisions

### 1. 架構：獨立 Workflow Engine vs 擴展 AgentService

**決定：獨立 Workflow Engine**

```
AgentService → WorkflowEngine → Action Executors
```

**理由：**
- 職責分離：Agent 負責對話理解，Workflow 負責流程執行
- 可測試性：Workflow 可獨立單元測試
- 可擴展性：未來可支持非對話觸發（API、定時）

**否決方案：** 直接喺 AgentService 加 workflow 邏輯 → 會令 Agent 過於臃腫

### 2. 觸發機制：確認式 vs 自動式

**決定：確認式（用戶確認後才執行）**

```
AI: 「建議加價 7.8%，想唔想我幫你開個審批任務？」
用戶: 「好」
→ 觸發 workflow
```

**理由：**
- 避免誤操作
- 用戶保持控制權
- 符合 Human-in-the-Loop 原則

**例外：** 告警響應流程可配置為全自動（用戶預先設定）

### 3. 排程實現：Celery Beat vs APScheduler

**決定：Celery Beat**

**理由：**
- 已有 Celery 基礎設施
- 支持分佈式執行
- 任務持久化到 Redis

### 4. 數據模型：新表 vs 擴展現有表

**決定：混合方案**
- 新表：`scheduled_reports`, `report_executions`, `alert_workflow_configs`
- 擴展：`price_proposals` 新增 `source_conversation_id`, `source_type`

**理由：**
- 新功能用新表，保持清晰
- 現有功能嘅擴展用新欄位，保持向後兼容

## Risks / Trade-offs

| 風險 | 影響 | 緩解措施 |
|------|------|----------|
| 排程任務執行失敗 | 用戶收唔到報告 | 連續失敗 3 次自動暫停 + 通知 |
| AI 分析成本增加 | API 費用上升 | 告警響應加閾值過濾，避免頻繁觸發 |
| Celery Beat 單點故障 | 排程停止執行 | 監控 + 告警 + 考慮 Celery Beat HA |
| 對話來源追溯斷裂 | 無法追返原因 | soft delete 對話，保留 90 日 |

## Data Models

### ScheduledReport

```python
class ScheduledReport(Base):
    __tablename__ = "scheduled_reports"

    id: UUID
    name: str
    report_type: str       # price_analysis | competitor | trend
    products: List[str]

    schedule_type: str     # daily | weekly | monthly
    schedule_day: Optional[int]
    schedule_time: time
    timezone: str = "Asia/Hong_Kong"

    notify_telegram: bool = True
    created_from_conversation: Optional[str]

    is_active: bool = True
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
```

### AlertWorkflowConfig

```python
class AlertWorkflowConfig(Base):
    __tablename__ = "alert_workflow_configs"

    id: UUID
    name: str
    alert_types: List[str]      # ["price_drop", "price_increase"]
    threshold_percent: Decimal  # 觸發閾值

    auto_analyze: bool = True
    notify_telegram: bool = True
    auto_create_proposal: bool = False

    quiet_hours_start: Optional[time]
    quiet_hours_end: Optional[time]

    is_active: bool = True
```

### PriceProposal 擴展

```python
# 新增欄位
source_conversation_id: Optional[str]
source_type: str = "manual"  # manual | ai_suggestion | auto_alert
assigned_to: Optional[UUID]
due_date: Optional[datetime]
```

## API Design

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/workflow/schedules` | 獲取排程列表 |
| POST | `/api/v1/workflow/schedules` | 創建排程 |
| PATCH | `/api/v1/workflow/schedules/{id}` | 編輯/暫停/恢復 |
| DELETE | `/api/v1/workflow/schedules/{id}` | 刪除排程 |
| GET | `/api/v1/workflow/executions` | 執行歷史 |
| POST | `/api/v1/workflow/alert-configs` | 配置告警規則 |

## Implementation Phases

1. **Phase 1: 改價審批流程** - 擴展 PriceProposal + Agent 意圖
2. **Phase 2: 報告排程** - 新增 ScheduledReport + Celery 任務
3. **Phase 3: 告警響應** - 新增 AlertWorkflowConfig + 觸發邏輯
