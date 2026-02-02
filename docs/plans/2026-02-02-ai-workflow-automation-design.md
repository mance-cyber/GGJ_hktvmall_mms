# AI 對話工作流自動化設計

> 日期：2026-02-02
> 狀態：Draft
> 作者：Claude + User

## 1. 概述

### 1.1 背景

現有 AI 對話系統（Jap仔）提供產品分析、價格趨勢、競品比較等功能，但係「問完即走」模式，缺乏與業務流程嘅整合。

### 1.2 目標

將 AI 對話能力與業務工作流深度整合，實現：
- 對話觸發自動化任務
- 減少人手操作
- 提升運營效率

### 1.3 範圍

本階段專注「工作流自動化」，包括：
1. 改價審批流程
2. 告警響應流程
3. 報告排程

知識管理（標籤、摘要、知識庫）及對話質素（評分、A/B 測試）留待下一輪。

---

## 2. 整體架構

```
┌─────────────────────────────────────────────────────────┐
│                    AI 對話介面                           │
│                  (現有 AgentPage)                        │
└─────────────────┬───────────────────────────────────────┘
                  │ 觸發工作流
                  ▼
┌─────────────────────────────────────────────────────────┐
│              Workflow Engine (新增)                      │
│  ┌─────────────┬─────────────┬─────────────┐           │
│  │ 改價審批    │ 告警響應    │ 報告排程    │           │
│  │ Trigger     │ Trigger     │ Trigger     │           │
│  └──────┬──────┴──────┬──────┴──────┬──────┘           │
│         │             │             │                   │
│         ▼             ▼             ▼                   │
│  ┌─────────────────────────────────────────┐           │
│  │         Action Executor                  │           │
│  │  • 創建審批任務                          │           │
│  │  • 發送 Telegram                         │           │
│  │  • 排程 Celery Task                      │           │
│  └─────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              現有系統整合                                │
│  • PricingApproval (改價審批 UI)                        │
│  • Telegram Bot (通知)                                  │
│  • Celery + Redis (排程任務)                            │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 功能設計

### 3.1 改價審批流程

#### 觸發場景

用戶喺 AI 對話中講類似「幫我建議和牛改價」或「分析完覺得應該加價」，AI 生成改價建議後，自動創建審批任務。

#### 流程

```
用戶: 「分析吓 A5 和牛應該點定價」
  │
  ▼
AI Agent 分析 → 建議由 $1,280 加到 $1,380
  │
  ▼
AI 回覆: 「建議加價 7.8%，理由係...」
        「想唔想我幫你開個審批任務？」
  │
  ▼
用戶: 「好，開啦」
  │
  ▼
Workflow 觸發:
  1. 創建 PriceProposal (status=pending)
  2. 關聯 conversation_id (可追溯來源)
  3. 推送 Telegram 通知審批人
  4. 喺對話顯示「✅ 已創建審批任務 #123」
```

#### 數據模型擴展

```python
# PriceProposal 新增欄位
class PriceProposal:
    # ... 現有欄位 ...

    # 新增：對話來源追溯
    source_conversation_id: Optional[str]  # 來自邊個 AI 對話
    source_type: str = "manual"  # manual | ai_suggestion | auto_alert

    # 新增：審批流程
    assigned_to: Optional[UUID]  # 指定審批人
    due_date: Optional[datetime]  # 審批期限
    reminder_sent: bool = False   # 已發提醒
```

#### 前端整合

- 改價審批 UI 顯示「來源：AI 對話 #xxx」連結
- 點擊可跳返原本對話，睇晒完整分析過程

---

### 3.2 告警響應流程

#### 觸發場景

系統偵測到競品價格變動，自動觸發 AI 分析，並將結果推送通知。

#### 流程

```
競品監測系統偵測到：百佳 A5 和牛降價 15%
  │
  ▼
Alert Trigger 自動啟動:
  1. 調用 AI Agent 分析影響
  2. 計算我方應對策略
  3. 生成簡報式摘要
  │
  ▼
推送 Telegram:
  ┌────────────────────────────────┐
  │ 🚨 競品價格異動                 │
  │                                │
  │ 百佳 A5 和牛                    │
  │ $1,480 → $1,258 (-15%)         │
  │                                │
  │ 📊 AI 分析：                    │
  │ • 預計影響我方銷量 12%          │
  │ • 建議跟進降價至 $1,298         │
  │                                │
  │ [查看詳情] [創建改價任務]        │
  └────────────────────────────────┘
  │
  ▼
用戶點擊 [創建改價任務]
  → 跳轉到 AI 對話，預填改價建議
  → 或直接創建審批任務
```

#### 配置模型

```python
class AlertWorkflowConfig(Base):
    """告警工作流配置"""
    __tablename__ = "alert_workflow_configs"

    id: UUID
    name: str                    # 配置名稱
    alert_types: List[str]       # 觸發告警類型 ["price_drop", "price_increase"]
    threshold_percent: Decimal   # 觸發閾值 (e.g. 10%)

    # 響應動作
    auto_analyze: bool = True    # 自動 AI 分析
    notify_telegram: bool = True # 推送 Telegram
    notify_users: List[UUID]     # 通知邊啲用戶
    auto_create_proposal: bool = False  # 自動創建改價提案

    # 排程
    quiet_hours_start: Optional[time]  # 靜音開始 (e.g. 22:00)
    quiet_hours_end: Optional[time]    # 靜音結束 (e.g. 08:00)

    is_active: bool = True
    created_at: datetime
```

#### 與現有系統整合

- 複用現有 `PriceAlert` 模型作為觸發源
- 複用現有 Telegram Bot 發送通知
- AI 分析複用 `AgentService` 嘅能力

---

### 3.3 報告排程

#### 觸發場景

用戶喺 AI 對話中設定定期報告，系統自動執行並發送。

#### 流程

```
用戶: 「每個禮拜一朝早 9 點出份和牛市場報告」
  │
  ▼
AI Agent 解析：
  • 報告類型：市場分析
  • 產品：和牛
  • 頻率：每週
  • 時間：週一 09:00
  │
  ▼
AI 回覆: 「收到！我會喺每個禮拜一 9:00 自動生成報告」
        「報告會發送到 Telegram，你亦可以喺呢度睇返」
  │
  ▼
Celery Beat 註冊排程任務
  │
  ▼
每週一 09:00 執行：
  1. 調用 ReportGenerator 生成報告
  2. 儲存到 ScheduledReport 表
  3. 推送 Telegram (附 PDF)
  4. 可選：發送 Email
```

#### 數據模型

```python
class ScheduledReport(Base):
    """排程報告配置"""
    __tablename__ = "scheduled_reports"

    id: UUID
    name: str                      # 報告名稱
    description: Optional[str]

    # 報告內容
    report_type: str               # price_analysis | competitor | trend
    products: List[str]            # 產品列表
    competitors: Optional[List[UUID]]

    # 排程設定
    schedule_type: str             # daily | weekly | monthly
    schedule_day: Optional[int]    # 週幾 (1-7) 或 幾號 (1-31)
    schedule_time: time            # 執行時間
    timezone: str = "Asia/Hong_Kong"

    # 發送設定
    notify_telegram: bool = True
    notify_email: Optional[str]

    # 來源追溯
    created_from_conversation: Optional[str]
    created_by: Optional[UUID]

    # 狀態
    is_active: bool = True
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]


class ReportExecution(Base):
    """報告執行記錄"""
    __tablename__ = "report_executions"

    id: UUID
    scheduled_report_id: UUID

    status: str                    # pending | running | success | failed
    started_at: datetime
    completed_at: Optional[datetime]

    # 結果
    report_markdown: Optional[str]
    report_pdf_url: Optional[str]
    error_message: Optional[str]
```

#### 排程管理

用戶可以透過對話或 UI 管理排程：

**對話方式：**
```
用戶: 「取消和牛市場週報」
AI: 「已暫停『和牛市場週報』排程。想恢復隨時話我知。」
```

**UI 方式（我的排程面板）：**
```
┌─────────────────────────────────────┐
│ 📅 我的排程報告                      │
├─────────────────────────────────────┤
│ 🟢 和牛市場週報                      │
│    每週一 09:00 · 下次：2月3日       │
│    [暫停] [編輯] [刪除]              │
├─────────────────────────────────────┤
│ 🟢 競品價格日報                      │
│    每日 08:00 · 下次：明天           │
│    [暫停] [編輯] [刪除]              │
├─────────────────────────────────────┤
│ [+ 新增排程]                         │
└─────────────────────────────────────┘
```

#### 自動暫停機制

- 如果報告連續執行失敗 3 次 → 自動暫停 + 通知用戶
- 避免無限重試浪費資源

---

## 4. 技術實現

### 4.1 新增後端模組

```
backend/app/
├── models/
│   └── workflow.py              # 新增：AlertWorkflowConfig, ScheduledReport, ReportExecution
│
├── services/
│   └── workflow/                # 新增：工作流引擎
│       ├── __init__.py
│       ├── engine.py            # WorkflowEngine 主類
│       ├── triggers.py          # 觸發器：改價、告警、排程
│       ├── actions.py           # 執行器：創建任務、發通知、生成報告
│       └── scheduler.py         # Celery Beat 排程管理
│
├── api/v1/
│   └── workflow.py              # 新增：排程 CRUD API
│
└── tasks/
    └── workflow_tasks.py        # 新增：Celery 異步任務
```

### 4.2 新增 API 端點

| 方法 | 路徑 | 描述 |
|------|------|------|
| GET | `/api/v1/workflow/schedules` | 獲取我的排程列表 |
| POST | `/api/v1/workflow/schedules` | 創建排程 |
| PATCH | `/api/v1/workflow/schedules/{id}` | 編輯/暫停/恢復 |
| DELETE | `/api/v1/workflow/schedules/{id}` | 刪除排程 |
| GET | `/api/v1/workflow/executions` | 執行歷史記錄 |
| POST | `/api/v1/workflow/alert-configs` | 配置告警響應規則 |

### 4.3 前端新增

```
frontend/src/
├── app/
│   └── agent/
│       └── components/
│           ├── SchedulePanel.tsx      # 我的排程面板
│           ├── ScheduleEditor.tsx     # 排程編輯對話框
│           └── ExecutionHistory.tsx   # 執行記錄
│
└── lib/api/
    └── workflow.ts                    # API 客戶端
```

### 4.4 數據庫遷移

需要新增以下表：
- `alert_workflow_configs`
- `scheduled_reports`
- `report_executions`

需要修改以下表：
- `price_proposals` - 新增 `source_conversation_id`, `source_type`, `assigned_to`, `due_date`, `reminder_sent` 欄位

---

## 5. 實現計劃

### Phase 1：改價審批流程（優先）

**範圍：**
- 擴展 `PriceProposal` 模型
- AI Agent 新增「創建審批任務」意圖
- 整合現有 Pricing Approval UI
- Telegram 通知審批人

**交付物：**
- 數據庫遷移
- `backend/app/services/workflow/` 基礎結構
- Agent 意圖擴展
- 前端對話來源顯示

### Phase 2：報告排程

**範圍：**
- 新增 `ScheduledReport` + `ReportExecution` 模型
- Celery Beat 排程任務
- 前端排程管理面板
- 對話中設定排程

**交付物：**
- 排程相關數據庫表
- Celery 任務
- 前端 SchedulePanel 組件
- Agent 排程意圖

### Phase 3：告警響應流程

**範圍：**
- 新增 `AlertWorkflowConfig` 模型
- 整合現有 `PriceAlert` 觸發
- 自動 AI 分析 + Telegram 推送
- 前端告警配置 UI

**交付物：**
- 告警工作流配置表
- Alert → Workflow 觸發邏輯
- 自動分析 + 通知
- 配置管理 UI

---

## 6. 未來擴展

下一輪將處理：

### 知識管理
- 對話標籤 + 搜索
- 智能摘要
- 知識庫累積

### 對話質素管理
- 對話評分（👍👎）
- A/B 測試框架

---

## 7. 附錄

### 相關文件

- 現有 Agent 服務：`backend/app/services/agent/`
- 現有定價模型：`backend/app/models/pricing.py`
- 現有 Telegram 服務：`backend/app/services/telegram_service.py`
- 現有 Celery 配置：`backend/app/tasks/`

### 參考

- 改價審批 UI：`frontend/src/app/pricing-approval/`
- AI 對話頁面：`frontend/src/app/agent/page.tsx`
