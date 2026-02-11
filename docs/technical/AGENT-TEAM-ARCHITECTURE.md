# GoGoJap Agent Team 架構設計

> 日期：2026-02-11
> 狀態：設計完成，待實現
> 版本：v1.0

---

## 一、項目背景與分析總結

### 1.1 系統現狀

經過對 **27+ API 模組、30+ 服務模組、4 個 Connector、54 張數據表、完整前端** 的徹底分析，GoGoJap 系統已具備完整的電商運營能力，但核心問題是：

**系統有完整的能力，但缺乏「主動性」** — 每個功能都等人按按鈕。

### 1.2 現有自動化 vs 手動操作

```
已自動化 (Celery Beat)                 完全手動 (8 大缺口)
─────────────────────────              ──────────────────────────
每天 09:00 競品爬取                     AI 價格分析 → 需按鈕觸發
每天 03:00 圖片清理                     AI 文案生成 → 需按鈕觸發
每天 06:00 SEO 排名追蹤                 SEO 內容生成 → 需按鈕觸發
每週一 08:00 SEO 週報                   訂單/財務同步 → 需按鈕觸發
每分鐘排程檢查                          HKTVmall 商品同步 → 需按鈕觸發
                                        競品自動匹配 → 需按鈕觸發
                                        促銷建議生成 → 需按鈕觸發
                                        價格提案審批 → 純手動
```

### 1.3 現有基礎設施

| 組件 | 說明 |
|------|------|
| **Celery Beat** | 5 個定時任務已運行 |
| **AI Agent「Jap仔」** | 意圖識別 + 工具執行 + 澄清系統 + 對話持久化 |
| **AIAnalysisService** | 中心 AI 服務，6+ 服務依賴 |
| **三層抓取** | HTTP metadata (0 credit) → Firecrawl price (1 credit) → Firecrawl full |
| **Workflow Engine** | 排程報告 + 告警工作流 |
| **Telegram** | 通知推送 + 按鈕回調（改價審批） |
| **Human-in-the-Loop** | PriceProposal 表完整實現 AI 提案 → 人工審批 → 執行閉環 |

---

## 二、Agent Team 設計

### 2.1 設計哲學

> 不是造一堆獨立機器人，而是建立一個有分工、有協作、有上下級的團隊。
> 每個 Agent 只做一件事，做到極致。指揮官負責協調。

**核心原則**：
1. **Agent 是現有服務的編排者，不是替代者** — 不重寫邏輯，只自動觸發
2. **事件驅動而非輪詢** — 用事件匯流排連接 Agent，而不是每個 Agent 自己設定時器
3. **人類永遠是最終決策者** — 所有涉及金錢的操作必須經過審批
4. **漸進式啟用** — 每個 Agent 有獨立開關，可逐個啟用，出問題立即關閉

### 2.2 架構總覽

```
                    ┌─────────────────────────┐
                    │    賣家（人類）           │
                    │  Telegram / 前端 / Agent │
                    └────────────┬────────────┘
                                 │ 審批 / 指令 / 反饋
                                 ▼
                    ┌─────────────────────────┐
                    │  Commander（指揮官）      │
                    │  協調、排程、衝突仲裁     │
                    │  人類上報閘門             │
                    └────────────┬────────────┘
                                 │
          ┌──────────┬───────────┼───────────┬──────────┐
          ▼          ▼           ▼           ▼          ▼
    ┌──────────┐┌──────────┐┌──────────┐┌──────────┐┌──────────┐
    │  Scout   ││  Pricer  ││  Writer  ││   Ops    ││  Strat   │
    │  偵察兵   ││  定價師   ││  文案官   ││  運營官   ││  軍師     │
    └──────────┘└──────────┘└──────────┘└──────────┘└──────────┘
```

---

## 三、Agent 詳細設計

### 3.1 Commander（指揮官）— 中央協調

**職責**：排程、事件路由、衝突仲裁、人類上報閘門

**每日排程表**：

| 時間 | 動作 | Agent |
|------|------|-------|
| 08:00 | 同步 HKTVmall 數據（訂單/庫存） | Ops |
| 09:00 | 爬取所有活躍競品（已有 Celery） | Scout |
| 09:30 | 分析競品價格變動 | Scout |
| 10:00 | 批量分析所有商品定價 | Pricer |
| 11:00 | 生成每日市場簡報 → Telegram | Strategist |

**事件路由表**：

| 事件 | 目標 Agent |
|------|-----------|
| `product.created` | Scout（搜索競品）+ Writer（生成文案） |
| `product.updated` | Writer（刷新內容） |
| `scrape.completed` | Scout（分析變動） |
| `price_alert.created` | Pricer（評估改價） |
| `competitor.stockout` | Strategist（搶市機會分析） |
| `daily_data.ready` | Strategist（生成每日簡報） |

**核心邏輯**：

```python
class CommanderAgent:
    """指揮官：Agent 團隊的中央神經系統"""

    DAILY_SCHEDULE = {
        "08:00": ["ops.daily_sync"],
        "09:00": ["scout.scrape_all"],          # 已有 Celery 任務
        "09:30": ["scout.analyze_changes"],
        "10:00": ["pricer.batch_analyze"],
        "11:00": ["strategist.daily_briefing"],
    }

    EVENT_ROUTES = {
        "product.created":     ["scout.find_competitors", "writer.generate_content"],
        "product.updated":     ["writer.refresh_content"],
        "scrape.completed":    ["scout.analyze_changes"],
        "price_alert.created": ["pricer.evaluate"],
        "competitor.stockout": ["strategist.opportunity"],
        "daily_data.ready":    ["strategist.daily_briefing"],
    }

    async def handle_event(self, event_type: str, payload: dict):
        """統一事件路由"""
        targets = self.EVENT_ROUTES.get(event_type, [])
        for target in targets:
            agent_name, method = target.split(".")
            await dispatch_to_agent(agent_name, method, payload)

    async def escalate_to_human(self, source: str, data: dict):
        """上報人類決策"""
        await telegram.send_approval_request(source, data)
        await create_notification(source, data)
```

---

### 3.2 Scout（偵察兵）— 競品情報

**職責**：自動發現、監測、匹配競品，提供第一手市場情報

**觸發條件**：

| 觸發 | 動作 | 現有 API |
|------|------|----------|
| 每天 09:00（已有） | 爬取所有活躍競品價格 | `scrape_all_competitors` |
| 新商品上架時 | 自動搜索 HKTVmall 同類競品 | `POST /market-response/batch/find-competitors` |
| 爬取完成後 | 分析價格變動趨勢、生成情報摘要 | `AIAnalysisService.generate_data_insights()` |
| 週一 08:00 | 生成週度競品報告 | 新增 |

**核心邏輯**：

```python
class ScoutAgent:
    """偵察兵：競品情報自動化"""

    async def on_product_created(self, payload):
        """新商品上架 → 自動搜索競品"""
        product = await get_product(payload["product_id"])
        matches = await competitor_matcher.find_competitors(product)
        if matches:
            await notify_commander("scout.matches_found", {
                "product": product.name,
                "matches": len(matches),
                "cheapest_delta": calculate_delta(product, matches)
            })

    async def on_scrape_completed(self, payload):
        """爬取完成 → 分析變動 → 通知相關 Agent"""
        alerts = analyze_price_changes(payload["results"])

        for alert in alerts:
            if alert.change_percent > 10:
                # 通知定價師：競品大幅降價
                await notify_agent("pricer", "competitor_price_drop", alert)
            if alert.stock_status == "out_of_stock":
                # 通知軍師：競品缺貨（搶市機會）
                await notify_agent("strategist", "competitor_stockout", alert)
```

**依賴的現有服務**：
- `CompetitorMatcherService` — 三層抓取（HTTP → Firecrawl price → Claude 匹配）
- `HKTVScraper.smart_scrape_product()` — 智能抓取
- Celery Beat `scrape-all-competitors-daily` — 定時任務

---

### 3.3 Pricer（定價師）— 智能定價

**職責**：基於市場情報生成定價建議，保護利潤底線

**觸發條件**：

| 觸發 | 動作 | 現有 API |
|------|------|----------|
| Scout 報告競品降價 | 生成改價提案 | `PricingService.generate_proposals()` |
| 每天 10:00（爬取後） | 批量分析所有商品定價 | `POST /pricing/analyze` |
| 人工審批後 | 執行改價到 HKTVmall | `HKTVMallClient.update_price()` |
| 改價 48h 後 | 評估改價效果 | 新增 |

**安全防護規則**：

```python
class PricerAgent:
    """定價師：永遠不自己改價，只提案"""

    RULES = {
        "min_margin": 0.05,        # 最低 5% 利潤率
        "max_drop_percent": 15,    # 單次最大降幅 15%
        "auto_approve_below": 10,  # 降幅 <$10 可自動批准（需用戶開啟）
        "require_human": True,     # 預設需要人工審批
    }

    async def on_competitor_price_drop(self, alert):
        """競品降價 → 生成定價提案"""
        proposal = await pricing_service.generate_proposal(
            product_id=alert.product_id,
            trigger="competitor_drop",
            competitor_price=alert.new_price,
        )

        if proposal.price_change_abs < self.RULES["auto_approve_below"]:
            await notify_commander("pricer.minor_proposal", proposal)
        else:
            await escalate_to_human("pricer.major_proposal", proposal)
```

**Human-in-the-Loop（已有）**：
- `PriceProposal` 表 → `status: pending/approved/rejected`
- Telegram 按鈕回調 → 一鍵審批
- 前端 `/pricing-approval` 頁面 → 批量審批

**依賴的現有服務**：
- `PricingService` — AI 提案生成 + 審批工作流
- `HKTVMallClient.update_price()` — 執行改價

---

### 3.4 Writer（文案官）— AI 內容生成

**職責**：自動為商品生成完整內容包（文案 + SEO + GEO）

**觸發條件**：

| 觸發 | 動作 | 現有 API |
|------|------|----------|
| 新商品上架 | 自動生成多語言文案+SEO | `ContentPipelineService.run()` |
| 商品更新 | 重新生成受影響內容 | `ContentPipelineService.run()` |
| 每月 1 日 | 審計所有內容新鮮度 | `SEOService.content_audit()` |
| 季節更替 | 批量更新季節性商品文案 | `BatchContentService` |

**核心邏輯**：

```python
class WriterAgent:
    """文案官：一次生成完整內容包"""

    async def on_product_created(self, payload):
        """新商品 → 自動生成完整內容包"""
        result = await content_pipeline.run(
            product_id=payload["product_id"],
            languages=["zh-HK", "zh-CN", "en"],
            tone="professional",
            include_faq=True,
        )
        await notify_commander("writer.content_ready", {
            "product_id": payload["product_id"],
            "content_ids": result.content_ids,
            "seo_ids": result.seo_content_ids,
        })

    async def monthly_content_audit(self):
        """月度內容審計：找出過時內容"""
        stale = await seo_service.find_stale_content(days=60)
        if stale:
            await content_pipeline.run_batch(
                product_ids=[c.product_id for c in stale],
                max_concurrent=3,
            )
```

**依賴的現有服務**：
- `ContentPipelineService` — 一次 AI 調用生成多語言（文案+SEO+GEO）
- `BatchContentService` — 批量生成（同步 ≤10 / 異步 >10）
- `ContentOptimizer` — 對話式優化
- 三角色 Prompt：文案總監 + 銷售心理專家 + 消費者代言人

---

### 3.5 Ops（運營官）— 訂單與庫存

**職責**：自動同步 HKTVmall 數據，監控運營狀態

**觸發條件**：

| 觸發 | 動作 | 現有 API |
|------|------|----------|
| 每天 08:00 | 同步 HKTVmall 訂單 | `OrderService` → HKTVmall API |
| 每天 08:30 | 同步 HKTVmall 商品庫存 | `POST /hktvmall/sync/products` |
| 每週一 | 同步財務結算數據 | `FinanceService` |
| 庫存 < 閾值 | 低庫存警報 → Telegram | `Telegram.send()` |
| 訂單異常 | 緊急通知（超時未出貨） | 新增 |

**核心邏輯**：

```python
class OpsAgent:
    """運營官：數據同步 + 異常監控"""

    LOW_STOCK_THRESHOLD = 5

    async def daily_sync(self):
        """每日同步三件套：訂單 → 商品 → 庫存"""
        orders = await order_service.sync_from_hktv()
        products = await hktv_client.sync_products()
        stock = await hktv_client.get_stock(all_skus)

        low_stock = [s for s in stock if s["quantity"] < self.LOW_STOCK_THRESHOLD]
        if low_stock:
            await escalate_to_human("ops.low_stock", low_stock)

        # 通知軍師：今日運營數據已更新
        await notify_agent("strategist", "daily_data_ready", {
            "orders_count": len(orders),
            "revenue": sum(o.total for o in orders),
        })
```

**依賴的現有服務**：
- `HKTVMallClient` — 訂單/商品/庫存/價格 API
- `OrderService` — 訂單處理
- `FinanceService` — 結算統計

---

### 3.6 Strategist（軍師）— 市場策略

**職責**：綜合所有數據生成策略建議，識別市場機會

**觸發條件**：

| 觸發 | 動作 | 現有 API |
|------|------|----------|
| 每天 11:00 | 生成每日市場簡報 | `AIAnalysisService` |
| Ops 同步完成 | 分析銷售趨勢 | `generate_data_insights()` |
| Scout 發現競品缺貨 | 生成搶市策略 | `generate_marketing_strategy()` |
| 每週一 09:00 | 生成週度策略報告 | 新增 |
| 促銷節日前 7 天 | 生成促銷建議 | `PromotionService.generate()` |

**核心邏輯**：

```python
class StrategistAgent:
    """軍師：數據驅動策略建議"""

    # 香港電商日曆
    PROMO_CALENDAR = {
        "01-01": "新年",     "02-14": "情人節",
        "05-01": "勞動節",   "06-18": "618",
        "11-11": "雙十一",   "12-12": "雙十二",
        "12-25": "聖誕",
    }

    async def daily_briefing(self):
        """每日市場簡報"""
        data = await analytics_service.get_command_center_data()
        insights = await ai_service.generate_data_insights(data)
        strategy = await ai_service.generate_marketing_strategy(
            insights=insights.content,
            context={"store": "GogoJap", "platform": "HKTVmall"}
        )
        await telegram.send_report(format_daily_briefing(insights, strategy))

    async def on_competitor_stockout(self, event):
        """競品缺貨 → 搶市機會"""
        await notify_commander("strategist.opportunity", {
            "type": "competitor_stockout",
            "competitor": event.competitor_name,
            "product": event.product_name,
            "recommendation": "考慮提高曝光或微調價格搶佔市場",
        })

    async def check_upcoming_promos(self):
        """促銷日曆：提前 7 天生成建議"""
        today = datetime.now().strftime("%m-%d")
        for date_str, event_name in self.PROMO_CALENDAR.items():
            days_until = (parse_date(date_str) - datetime.now()).days
            if 0 < days_until <= 7:
                await promotion_service.generate_suggestions(event_name)
```

**依賴的現有服務**：
- `AIAnalysisService` — 雙 AI 串聯（Insights → Strategy）
- `AnalyticsService.get_command_center_data()` — Dashboard 數據聚合
- `PromotionService` — 促銷建議生成
- Telegram 通知 — 多渠道交付

---

## 四、事件匯流排設計

### 4.1 EventBus 核心

```python
# backend/app/agents/events.py

class EventBus:
    """輕量級進程內事件匯流排"""

    _handlers: Dict[str, List[Callable]] = defaultdict(list)

    @classmethod
    def on(cls, event_type: str):
        """裝飾器：註冊事件處理器"""
        def decorator(func):
            cls._handlers[event_type].append(func)
            return func
        return decorator

    @classmethod
    async def emit(cls, event_type: str, payload: dict):
        """發送事件"""
        logger.info(f"Event: {event_type} → {len(cls._handlers.get(event_type, []))} handlers")
        for handler in cls._handlers.get(event_type, []):
            try:
                await handler(payload)
            except Exception as e:
                logger.error(f"Event handler failed: {event_type} → {e}")
```

### 4.2 事件定義

```python
# backend/app/agents/events.py

class Events:
    """所有事件類型常量"""

    # 商品生命週期
    PRODUCT_CREATED = "product.created"
    PRODUCT_UPDATED = "product.updated"
    PRODUCT_DELETED = "product.deleted"

    # 抓取生命週期
    SCRAPE_STARTED = "scrape.started"
    SCRAPE_COMPLETED = "scrape.completed"
    SCRAPE_FAILED = "scrape.failed"

    # 價格告警
    PRICE_ALERT_CREATED = "price_alert.created"
    COMPETITOR_PRICE_DROP = "competitor.price_drop"
    COMPETITOR_STOCKOUT = "competitor.stockout"

    # 內容生命週期
    CONTENT_GENERATED = "content.generated"
    CONTENT_APPROVED = "content.approved"

    # 運營數據
    DAILY_DATA_READY = "daily_data.ready"
    ORDER_SYNCED = "order.synced"

    # Agent 內部通訊
    AGENT_TASK_COMPLETED = "agent.task_completed"
    AGENT_ESCALATION = "agent.escalation"
```

### 4.3 與現有 Celery 任務的對接

改動最小化 — 只需在現有任務完成處加一行 `EventBus.emit()`：

```python
# 修改 backend/app/tasks/scrape_tasks.py（現有文件）
# 在爬取完成後加一行：
await EventBus.emit(Events.SCRAPE_COMPLETED, {
    "competitor_id": competitor_id,
    "results": results,
    "alerts_created": len(new_alerts),
})
```

---

## 五、Agent 間通訊矩陣

```
           Commander  Scout  Pricer  Writer  Ops  Strategist
Commander     -        ✓      ✓       ✓      ✓      ✓        (下發指令)
Scout         ✓        -      ✓       -      -      ✓        (情報共享)
Pricer        ✓        -      -       -      -      -        (提案上報)
Writer        ✓        -      -       -      -      -        (完成通知)
Ops           ✓        -      -       -      -      ✓        (數據就緒)
Strategist    ✓        -      -       -      -      -        (報告上報)
```

**通訊規則**：
1. 所有 Agent 都向 Commander 匯報
2. Scout → Pricer：競品降價情報直達
3. Scout → Strategist：競品缺貨機會直達
4. Ops → Strategist：運營數據就緒直達
5. Agent 之間不得直接修改數據庫，必須通過現有 Service 層

---

## 六、Human-in-the-Loop 決策點

| Agent | AI 自動決策 | 人工介入點 | 上報條件 |
|-------|-----------|----------|---------|
| **Scout** | 自動匹配競品（confidence ≥ 0.5） | 可選審核匹配結果 | 新增 ≥5 個匹配 |
| **Pricer** | 生成改價提案 | **必須審批** | 所有改價 |
| **Writer** | 自動生成文案 | 可選審核 | 無（全自動） |
| **Ops** | 自動同步數據 | 低庫存警報 | 庫存 < 5 |
| **Strategist** | 生成策略報告 | 促銷建議需確認 | 促銷節日前 |

---

## 七、數據庫模型讀寫矩陣

| Agent | 讀取（通過 Service） | 寫入（通過 Service） |
|-------|---------------------|---------------------|
| **Scout** | `Product`, `CompetitorProduct`, `PriceSnapshot` | `ProductCompetitorMapping` |
| **Pricer** | `Product`, `CompetitorProduct`, `PriceProposal` | `PriceProposal`, `AuditLog` |
| **Writer** | `Product` | `AIContent`, `SEOContent`, `StructuredData`, `PipelineSession` |
| **Ops** | `Order`, `Settlement` | `Order`, `OrderItem`, `SyncLog` |
| **Strategist** | `Order`, `PriceAlert`, `Settlement`, `PriceAnalytics` | `Notification` |

---

## 八、實現路徑

### Phase 1：事件驅動骨架（1-2 天）

**新增文件**：

```
backend/app/agents/
├── __init__.py         # Agent 註冊與初始化
├── base.py             # AgentBase 基類（事件註冊、日誌、通知）
├── commander.py        # 指揮官（事件路由 + 排程）
├── scout.py            # 偵察兵
├── pricer.py           # 定價師
├── writer.py           # 文案官
├── ops.py              # 運營官
├── strategist.py       # 軍師
└── events.py           # 事件定義 + 事件匯流排
```

**核心任務**：
1. 定義 `EventBus` 類
2. 定義所有事件常量
3. 實現 `AgentBase` 基類（日誌、通知、開關控制）
4. 實現 `CommanderAgent`（事件路由 + 排程表）

### Phase 2：接入現有服務（2-3 天）

每個 Agent 只是現有 Service 的**薄封裝**：

1. `ScoutAgent` — 封裝 `CompetitorMatcherService` + `scrape_tasks`
2. `PricerAgent` — 封裝 `PricingService`
3. `WriterAgent` — 封裝 `ContentPipelineService` + `BatchContentService`
4. `OpsAgent` — 封裝 `OrderService` + `HKTVMallClient` + `FinanceService`
5. `StrategistAgent` — 封裝 `AIAnalysisService` + `AnalyticsService`

### Phase 3：Celery 排程整合（1 天）

在現有 `celery_app.py` 的 `beat_schedule` 中新增 Agent 排程：

```python
# 新增排程（不影響現有的 5 個）
"ops-daily-sync":        {"task": "agents.ops.daily_sync",       "schedule": crontab(hour=8, minute=0)},
"pricer-batch-analyze":  {"task": "agents.pricer.batch_analyze", "schedule": crontab(hour=10, minute=0)},
"strategist-briefing":   {"task": "agents.strategist.briefing",  "schedule": crontab(hour=11, minute=0)},
"writer-monthly-audit":  {"task": "agents.writer.monthly_audit", "schedule": crontab(day_of_month=1, hour=2)},
```

### Phase 4：前端 Agent Dashboard（2-3 天）

新增 `/agents` 頁面：
- Agent 狀態面板（在線/離線/執行中）
- 今日事件流（時間線視圖）
- 待人工處理的決策隊列
- Agent 配置（開關、閾值調整）

---

## 九、技術決策

### 9.1 為什麼不用 LangChain / CrewAI / AutoGen？

| 方案 | 問題 |
|------|------|
| LangChain | 抽象太重，系統已有完整 AI 服務層 |
| CrewAI | 通用框架，無法利用現有 30+ 服務模組 |
| AutoGen | 多 Agent 對話模式，不適合電商定時任務場景 |
| **自建輕量架構** | **直接封裝現有服務，改動最小，掌控力最高** |

### 9.2 EventBus vs Message Queue

| 方案 | 適用場景 | 選擇理由 |
|------|---------|---------|
| 進程內 EventBus | 單機部署，Agent 數量 <10 | **Phase 1 選擇**：最簡單，零外部依賴 |
| Redis Pub/Sub | 多進程 / 多機器 | Phase 2 遷移目標（已有 Redis） |
| RabbitMQ / Kafka | 高吞吐量、持久化 | 過度工程，當前不需要 |

### 9.3 Agent 狀態管理

| 方案 | 說明 |
|------|------|
| 無狀態 | 每次事件觸發獨立執行，不保留 Agent 內部狀態 |
| 數據庫狀態 | Agent 的配置（開關、閾值）存 `SystemSetting` 表 |
| 內存狀態 | 僅用於短期任務追蹤（如批量處理進度），進程重啟後丟失 |

---

## 十、風險與緩解

| 風險 | 影響 | 緩解措施 |
|------|------|---------|
| AI API 限流 | Agent 批量調用被拒 | 併發控制（MAX_CONCURRENT=3）+ 指數退避 |
| 錯誤級聯 | Scout 失敗 → Pricer/Strategist 無數據 | 每個 Agent 獨立 try/catch，失敗不阻塞其他 Agent |
| 重複執行 | 同一事件觸發多次 | 冪等設計 + 事件去重（event_id） |
| 成本失控 | Firecrawl/AI API 過度消耗 | 每日配額限制 + 成本追蹤（ScrapeQuotaUsage 表） |
| 人工疲勞 | 太多通知打擾賣家 | 靜默時段（23:00-08:00）+ 通知聚合（批量而非逐條） |

---

## 十一、成功指標

| 指標 | 目標 | 衡量方式 |
|------|------|---------|
| 手動操作減少 | 80% 日常操作自動化 | 對比前後按鈕點擊次數 |
| 改價響應速度 | 競品降價後 < 2 小時生成提案 | PriceProposal.created_at - PriceAlert.created_at |
| 文案覆蓋率 | 100% 商品有 AI 文案 | AIContent 表 vs Product 表 |
| 數據新鮮度 | 訂單/庫存延遲 < 12 小時 | last_synced_at 時差 |
| 每日簡報交付 | 100% 工作日準時交付 | Telegram 發送記錄 |

---

## 附錄 A：系統分析數據摘要

### A.1 後端規模

- **API 路由模組**：27+
- **服務模組**：30+
- **Connector**：4 個（Claude、Firecrawl、HKTVmall HTTP、HKTVmall Scraper）
- **數據表**：54 張
- **索引**：88 個
- **JSONB 欄位**：44 個
- **Alembic 遷移**：9 個

### A.2 前端規模

- **頁面**：9 個主要路由
- **API 方法**：60+ 個
- **UI 組件**：30+ 個（含 Future Tech 設計系統）
- **設計系統**：shadcn/ui + Radix UI + Tailwind CSS + Framer Motion

### A.3 AI 整合點

- **AI 子系統**：8 個
- **Prompt 策略**：角色堆疊、示例驅動、結構化輸出、品牌注入
- **LLM 支持**：Claude + OpenAI 兼容（中轉站）
- **Agent「Jap仔」**：意圖識別（規則+AI 混合）+ 7 個工具 + 澄清系統

### A.4 現有 Celery 定時任務

| 任務 | 排程 | 說明 |
|------|------|------|
| `scrape-all-competitors-daily` | 每天 09:00 | 爬取所有活躍競品 |
| `cleanup-old-image-tasks-daily` | 每天 03:00 | 清理 7 天前圖片任務 |
| `track-all-keyword-rankings-daily` | 每天 06:00 | SEO 排名追蹤 |
| `generate-weekly-seo-reports` | 每週一 08:00 | 生成 SEO 週報 |
| `check-due-scheduled-reports` | 每分鐘 | 檢查到期排程 |
