# Agent Team 模組

## 架構概述

事件驅動的 6-Agent 協同運營系統。Agent 之間通過 EventBus 通訊，不直接互調。

```
EventBus (進程內異步 pub/sub)
    ├── Commander  — 指揮官：排程協調、錯誤監控、人類上報閘門
    ├── Scout      — 偵察兵：競品發現、價格變動分析
    ├── Pricer     — 定價師：改價提案生成、利潤底線保護
    ├── Writer     — 文案官：AI 內容包生成（文案+SEO+GEO）
    ├── Ops        — 運營官：訂單同步、異常監控
    └── Strategist — 軍師：AI 市場簡報、搶市機會分析
```

## 文件職責

| 文件 | 用途 |
|------|------|
| `events.py` | EventBus + Event 數據結構 + Events 常量（白名單） |
| `base.py` | AgentBase 抽象類 — AOP handler wrapping、DB session、Telegram 上報 |
| `commander.py` | 指揮官 — 排程表、靜默時段、錯誤/完成事件處理 |
| `scout.py` | 偵察兵 — 接入 CompetitorMatcherService、PriceAlert 分類發射 |
| `pricer.py` | 定價師 — 接入 PricingService、安全底價計算、人類審批閘門 |
| `writer.py` | 文案官 — 接入 ContentPipelineService、智能字段變更檢測 |
| `ops.py` | 運營官 — 接入 OrderService、訂單超時預警 |
| `strategist.py` | 軍師 — 接入 AnalyticsService + AIAnalysisService 雙串聯 |
| `__init__.py` | 生命週期管理 — startup/shutdown/get_agent/get_team_status |

## 核心設計

- **AOP 包裝**: `_wrap_handler()` 自動處理 enable/disable 閘門 + 日誌 + 異常捕獲
- **Fail-silent**: EventBus 捕獲 handler 異常，發射 `agent.error` 事件，不阻塞其他 handler
- **啟用狀態**: 雙層 — DB `SystemSetting` 持久化 + 內存 `_enabled` 緩存
- **事件白名單**: `_VALID_EVENTS` 防止注入偽造事件
- **Session 安全**: `get_db_session()` 自動 commit/rollback
- **HTML 轉義**: `escalate_to_human()` 所有輸入經 `html.escape` 防注入

## 事件流（關鍵路徑）

```
[Celery Beat] → schedule.ops.daily_sync → Ops._on_daily_sync
    → OrderService.sync_orders() → daily_data.ready → Strategist._on_daily_data_ready

[Celery Beat] → schedule.pricer.batch → Pricer._on_schedule_batch
    → PricingService.generate_proposals()

scrape.completed → Scout._on_scrape_completed
    → PriceAlert 分類 → competitor.price_drop → Pricer._on_competitor_drop
        → PricingService.create_proposal() → escalate_to_human

product.created → Scout._on_product_created + Writer._on_product_created
```

## Celery Beat 排程

| 時間 | 任務 | Agent |
|------|------|-------|
| 08:00 | `trigger_ops_daily_sync` | Ops |
| 09:30 | `trigger_scout_analyze` | Scout |
| 10:00 | `trigger_pricer_batch` | Pricer |
| 11:00 | `trigger_strategist_briefing` | Strategist |

## API 端點

- `GET /api/v1/agent-team/status` — 團隊狀態
- `POST /api/v1/agent-team/{name}/enable` — 啟用 Agent
- `POST /api/v1/agent-team/{name}/disable` — 停用 Agent
- `POST /api/v1/agent-team/emit/{event_type}` — 手動觸發事件
- `GET /api/v1/agent-team/events?limit=50` — 事件日誌
