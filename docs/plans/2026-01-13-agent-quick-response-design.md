# Agent 快速回覆系統設計

## 需求摘要

用戶希望 AI 助手能「秒回」常用查詢，實現方式：
1. **預計算快取 (Layer 1)**：常用數據預先計算好，即時返回 (<50ms)
2. **查詢快取 (Layer 2)**：按需查詢的數據快取，首次稍慢，之後快速返回

## 架構設計

```
用戶輸入 → Intent Classification (Rule-based)
                    ↓
         ┌───────────────────────┐
         │   快速回覆路由器       │
         └───────────────────────┘
                    ↓
    ┌─────────────────┼─────────────────┐
    ↓                 ↓                 ↓
 [Layer 1]       [Layer 2]        [Layer 3]
 預計算快取      查詢快取          完整流程

 • 今日訂單      • 產品價格        • AI 深度分析
 • 警報統計      • 競品數據        • 報告生成
 • 財務數據      • 歷史趨勢        • Marketing 策略
 • 導航指引

   <50ms          100-500ms         2-10s
```

## Layer 1：預計算快取清單

| 類別 | 數據項目 | 快取 Key | 更新觸發 | 回覆範例 |
|------|----------|----------|----------|----------|
| **訂單** | 今日訂單統計 | `quick:orders:today` | 訂單變動 | 「今日 42 單，營收 $12,580」|
| | 待處理訂單 | `quick:orders:pending` | 訂單狀態變動 | 「7 單待出貨，3 單待確認」|
| | 本週/本月統計 | `quick:orders:week/month` | 每小時 | 「本週 280 單，比上週 +15%」|
| **財務** | 今日營收 | `quick:finance:today` | 訂單變動 | 「今日營收 $12,580」|
| | 本月利潤 | `quick:finance:month` | 每小時 | 「本月毛利 $45,000，利潤率 32%」|
| | 結算狀態 | `quick:finance:settlement` | 每日 | 「最近一期結算 $120,000 已入帳」|
| **警報** | 警報統計 | `quick:alerts:summary` | 警報變動 | 「3 個警報，1 個緊急」|
| | 緊急事項 | `quick:alerts:urgent` | 警報變動 | 「競爭對手 X 減價 20%！」|
| **競品** | 價格變動摘要 | `quick:competitors:changes` | 爬蟲完成 | 「今日 5 個競品有價格變動」|
| | 缺貨機會 | `quick:competitors:stockout` | 爬蟲完成 | 「百佳 3 款產品缺貨中」|
| **產品** | 熱門產品狀態 | `quick:products:top10` | 每小時 | 「A5 和牛 $580，庫存 23」|
| | 低庫存警告 | `quick:products:lowstock` | 庫存變動 | 「5 款產品即將賣完」|
| **導航** | 功能導引 | 硬編碼 | N/A | 「去競品監察按呢度」|

## 實現計劃

### Step 1: 建立 QuickCacheService

**文件**: `backend/app/services/agent/quick_cache.py`

```python
class QuickCacheService:
    """預計算快取服務"""

    CACHE_KEYS = {
        "orders_today": "quick:orders:today",
        "orders_pending": "quick:orders:pending",
        "finance_today": "quick:finance:today",
        "finance_month": "quick:finance:month",
        "alerts_summary": "quick:alerts:summary",
        "competitors_changes": "quick:competitors:changes",
        "products_lowstock": "quick:products:lowstock",
    }

    # Intent 到快取 Key 的映射
    INTENT_CACHE_MAP = {
        "order_stats": ["orders_today", "orders_pending"],
        "finance_summary": ["finance_today", "finance_month"],
        "alert_query": ["alerts_summary"],
        "navigate": None,  # 硬編碼回覆
    }

    async def get_quick_response(self, intent: str) -> Optional[dict]:
        """根據意圖獲取快取數據，返回格式化的回覆"""
        ...

    async def refresh_cache(self, key: str) -> None:
        """刷新特定快取"""
        ...
```

### Step 2: 修改 AgentService 集成快取

**文件**: `backend/app/services/agent/agent_service_db.py`

在 `process_message` 開頭加入快取檢查：

```python
async def process_message(self, message: str, conversation_id: str = None):
    # 1. Intent Classification (Rule-based only for speed)
    intent_result = self._classify_by_rules(message)

    # 2. 嘗試快取回覆
    if intent_result.confidence >= 0.8:
        quick_response = await self.quick_cache.get_quick_response(
            intent_result.intent.value
        )
        if quick_response:
            yield AgentResponse(
                type=ResponseType.MESSAGE,
                content=quick_response["message"],
                conversation_id=conversation_id,
                suggestions=quick_response.get("suggestions"),
            )
            return

    # 3. 原有流程...
```

### Step 3: 建立快取更新機制

**選項 A**: Signal-based（推薦）
- 訂單/警報變動時發送 Signal
- Signal Handler 更新對應快取

**選項 B**: Periodic Task
- Celery Beat 定時刷新所有快取
- 每分鐘/每小時執行

### Step 4: 添加回覆模板

**文件**: `backend/app/services/agent/quick_templates.py`

```python
QUICK_RESPONSE_TEMPLATES = {
    "orders_today": """📦 **今日訂單**

• 總訂單數：{count} 單
• 營收：${revenue:,.0f}
• 平均單價：${avg_price:,.0f}

{comparison}""",

    "alerts_summary": """🚨 **警報摘要**

• 總警報：{total} 個
• 緊急：{urgent} 個
• 價格變動：{price_alerts} 個
• 缺貨提醒：{stockout_alerts} 個

{urgent_items}""",
}
```

## 文件修改清單

| 文件 | 操作 | 說明 |
|------|------|------|
| `backend/app/services/agent/quick_cache.py` | 新增 | 快取服務核心 |
| `backend/app/services/agent/quick_templates.py` | 新增 | 回覆模板 |
| `backend/app/services/agent/agent_service_db.py` | 修改 | 集成快取邏輯 |
| `backend/app/services/agent/__init__.py` | 修改 | 導出新服務 |

## 驗證計劃

1. 測試常用查詢回覆時間 <100ms
2. 測試快取過期後自動刷新
3. 測試數據準確性

---

*設計日期：2026-01-13*
