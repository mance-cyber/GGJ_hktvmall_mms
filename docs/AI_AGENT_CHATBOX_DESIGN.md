# AI Agent Chatbox 設計文檔

> 版本：1.0  
> 創建日期：2025-01-07  
> 狀態：設計中

---

## 目錄

1. [概述](#1-概述)
2. [系統架構](#2-系統架構)
3. [核心概念](#3-核心概念)
4. [數據流程](#4-數據流程)
5. [後端設計](#5-後端設計)
6. [前端設計](#6-前端設計)
7. [對話示例](#7-對話示例)
8. [實現計劃](#8-實現計劃)

---

## 1. 概述

### 1.1 目標

建立一個智能對話式 AI Agent，讓用戶可以用自然語言查詢和分析 HKTVmall 產品數據，無需編寫 SQL 或了解數據結構。

### 1.2 核心功能

| 功能 | 描述 |
|------|------|
| **自然語言查詢** | 用戶用日常語言描述需求 |
| **智能澄清** | AI 主動詢問缺失或模糊的參數 |
| **多維度分析** | 價格、趨勢、競爭對手、評論等 |
| **報告生成** | 自動生成結構化分析報告 |

### 1.3 設計原則

```
┌─────────────────────────────────────────────────────────────┐
│  原則 1：SQL First, Token Efficient                         │
│  - 所有數據查詢通過 SQL 執行                                  │
│  - AI 只處理聚合後的數據，節省 Token                          │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  原則 2：Progressive Disclosure                             │
│  - 簡單查詢直接執行                                          │
│  - 複雜查詢才進行 Slot Filling                               │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│  原則 3：Graceful Degradation                               │
│  - 無數據時給出明確提示                                       │
│  - API 錯誤時提供替代方案                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 系統架構

### 2.1 整體架構圖

```
┌─────────────────────────────────────────────────────────────────────┐
│                           前端 (Next.js)                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                      Chat UI 組件                              │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │  │
│  │  │ 訊息列表     │  │ 輸入框      │  │ Slot Filling UI      │   │  │
│  │  │ (歷史對話)   │  │ (語音/文字) │  │ (互動式選項)         │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                │                                    │
│                                ▼                                    │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    Report 展示組件                             │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │  │
│  │  │ Markdown    │  │ 圖表        │  │ 數據表格             │   │  │
│  │  │ 渲染器      │  │ (Recharts)  │  │                     │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ WebSocket / REST API
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           後端 (FastAPI)                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                      Agent 核心引擎                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │  │
│  │  │ Intent      │  │ Slot        │  │ Tool                 │   │  │
│  │  │ Classifier  │  │ Manager     │  │ Executor             │   │  │
│  │  │ (意圖識別)   │  │ (槽位管理)  │  │ (工具執行)           │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                │                                    │
│                                ▼                                    │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                      工具層 (Tools)                            │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │  │
│  │  │ 產品搜索     │  │ 價格趨勢    │  │ 競爭對手分析         │   │  │
│  │  │ Tool        │  │ Tool        │  │ Tool                 │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘   │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │  │
│  │  │ 市場概覽     │  │ 品牌分析    │  │ 報告生成             │   │  │
│  │  │ Tool        │  │ Tool        │  │ Tool                 │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                │                                    │
│                                ▼                                    │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                      數據層                                    │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │  │
│  │  │ PostgreSQL  │  │ AI Service  │  │ Cache (Redis)        │   │  │
│  │  │ (產品數據)   │  │ (中轉站)    │  │ (對話歷史)           │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 技術棧

| 層級 | 技術 | 用途 |
|------|------|------|
| 前端 | Next.js 14 + TypeScript | Chat UI |
| 前端 | Framer Motion | 動畫效果 |
| 前端 | Recharts | 圖表展示 |
| 後端 | FastAPI | API 服務 |
| 後端 | SQLAlchemy | ORM |
| 後端 | httpx | AI API 調用 |
| 數據庫 | PostgreSQL | 產品/價格數據 |
| 緩存 | Redis (可選) | 對話歷史 |

---

## 3. 核心概念

### 3.1 意圖類型 (Intent Types)

```python
class IntentType(Enum):
    # 產品查詢
    PRODUCT_SEARCH = "product_search"           # 搜索特定產品
    PRODUCT_DETAIL = "product_detail"           # 查看產品詳情
    
    # 分析類
    PRICE_ANALYSIS = "price_analysis"           # 價格分析
    TREND_ANALYSIS = "trend_analysis"           # 趨勢分析
    COMPETITOR_ANALYSIS = "competitor_analysis" # 競爭對手分析
    BRAND_ANALYSIS = "brand_analysis"           # 品牌分析
    MARKET_OVERVIEW = "market_overview"         # 市場概覽
    
    # 報告類
    GENERATE_REPORT = "generate_report"         # 生成報告
    MARKETING_STRATEGY = "marketing_strategy"   # Marketing 策略
    
    # 對話類
    CLARIFICATION = "clarification"             # 用戶澄清
    FOLLOWUP = "followup"                       # 追問
    GREETING = "greeting"                       # 問候
    UNKNOWN = "unknown"                         # 未知意圖
```

### 3.2 槽位定義 (Slot Definitions)

```python
@dataclass
class AnalysisSlots:
    """分析查詢的槽位"""
    
    # === 必填槽位 ===
    products: List[str] = field(default_factory=list)
    # 例：["A5和牛", "三文魚"]
    
    # === 可選槽位（有預設值）===
    
    # 產品細節
    product_details: Dict[str, ProductDetail] = field(default_factory=dict)
    # 例：{
    #   "A5和牛": {"parts": ["西冷", "肉眼"], "origin": ["日本"]},
    #   "三文魚": {"types": ["刺身"], "origin": ["挪威", "智利"]}
    # }
    
    # 時間範圍
    time_range: str = "30d"  # 7d, 30d, 90d, 1y, all
    
    # 分析維度
    analysis_dimensions: List[str] = field(default_factory=lambda: [
        "price_overview",      # 價格概覽
        "price_trend",         # 價格趨勢
        "competitor_compare",  # 競爭對手比較
    ])
    
    # 競爭對手
    include_competitors: bool = True
    competitor_ids: List[str] = field(default_factory=list)  # 空 = 全部
    
    # 輸出格式
    output_format: str = "report"  # report, table, chart, raw

@dataclass
class ProductDetail:
    """產品細節槽位"""
    parts: List[str] = field(default_factory=list)      # 部位：西冷、肉眼
    types: List[str] = field(default_factory=list)      # 類型：刺身、煙燻
    origin: List[str] = field(default_factory=list)     # 產地：日本、挪威
    brands: List[str] = field(default_factory=list)     # 品牌
    price_range: Tuple[float, float] = None             # 價格範圍
    grade: List[str] = field(default_factory=list)      # 等級：A5, A4
```

### 3.3 槽位填充狀態

```python
class SlotStatus(Enum):
    EMPTY = "empty"           # 未填充
    PARTIAL = "partial"       # 部分填充
    COMPLETE = "complete"     # 完整填充
    AMBIGUOUS = "ambiguous"   # 有歧義，需確認

@dataclass
class SlotState:
    """槽位狀態追蹤"""
    slots: AnalysisSlots
    status: Dict[str, SlotStatus]
    missing_required: List[str]
    ambiguous_slots: List[str]
    confidence: float  # 0.0 - 1.0
```

### 3.4 產品分類知識庫

```python
PRODUCT_TAXONOMY = {
    "和牛": {
        "aliases": ["wagyu", "日本牛", "A5牛"],
        "parts": ["西冷", "肉眼", "牛柳", "牛肋骨", "火鍋片", "燒肉片", "漢堡扒"],
        "grades": ["A5", "A4", "A3"],
        "origins": ["日本", "澳洲", "美國"],
        "brands": ["鹿兒島", "宮崎", "神戶", "松阪", "近江", "飛驒"],
        "clarification_questions": [
            "想分析邊個部位？（西冷/肉眼/牛柳/全部）",
            "要包埋邊個產地？（日本/澳洲/美國/全部）"
        ]
    },
    "三文魚": {
        "aliases": ["salmon", "鮭魚"],
        "types": ["刺身", "三文魚腩", "三文魚頭", "三文魚柳", "煙燻三文魚", "三文魚子"],
        "origins": ["挪威", "智利", "蘇格蘭", "日本", "加拿大"],
        "clarification_questions": [
            "想睇邊類三文魚？（刺身/魚腩/魚頭/全部）",
            "有冇特定產地偏好？"
        ]
    },
    "海膽": {
        "aliases": ["uni", "海胆"],
        "types": ["馬糞海膽", "紫海膽", "赤海膽", "海膽醬"],
        "origins": ["北海道", "青森", "利尻", "加拿大"],
        "grades": ["特選", "A級", "B級"],
        "clarification_questions": [
            "想分析邊種海膽？（馬糞/紫海膽/全部）"
        ]
    },
    "蟹": {
        "aliases": ["crab"],
        "types": ["帝王蟹", "松葉蟹", "毛蟹", "花蟹", "蟹腳", "蟹肉"],
        "origins": ["北海道", "鳥取", "俄羅斯", "阿拉斯加"],
        "clarification_questions": [
            "想睇邊種蟹？（帝王蟹/松葉蟹/毛蟹/全部）"
        ]
    },
    # ... 更多產品分類
}
```

---

## 4. 數據流程

### 4.1 完整對話流程

```
用戶輸入 ──────────────────────────────────────────────────────────────►
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Step 1: 意圖識別 (Intent Classification)                            │
│ ───────────────────────────────────────────────────────────────────│
│ 輸入: "我想睇 A5 和牛同三文魚嘅資料"                                   │
│ 輸出: {                                                             │
│   intent: "MARKET_OVERVIEW",                                        │
│   entities: ["A5和牛", "三文魚"],                                    │
│   confidence: 0.92                                                  │
│ }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Step 2: 槽位提取 (Slot Extraction)                                  │
│ ───────────────────────────────────────────────────────────────────│
│ 從用戶輸入中提取已知槽位:                                             │
│ - products: ["A5和牛", "三文魚"] ✓                                   │
│ - time_range: 未指定 → 用預設 "30d"                                  │
│ - parts: 未指定 → 需要詢問                                           │
│ - analysis_dimensions: 未指定 → 用預設                               │
└─────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Step 3: 槽位完整性檢查                                               │
│ ───────────────────────────────────────────────────────────────────│
│ 檢查規則:                                                           │
│ - 如果產品有多個子分類 → 詢問用戶                                     │
│ - 如果查詢範圍太廣 → 建議收窄                                         │
│ - 如果信心度 < 0.8 → 確認理解                                        │
│                                                                     │
│ 決定: 需要詢問和牛部位和三文魚類型                                     │
└─────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Step 4: 生成澄清問題                                                 │
│ ───────────────────────────────────────────────────────────────────│
│ AI 回應:                                                            │
│ "好！想再確認幾樣嘢：                                                 │
│  1. 和牛方面，想分析邊個部位？                                        │
│     □ 全部  □ 西冷  □ 肉眼  □ 牛柳  □ 火鍋片                         │
│  2. 三文魚方面，想睇邊類產品？                                        │
│     □ 全部  □ 刺身  □ 魚腩  □ 魚頭  □ 煙燻"                          │
└─────────────────────────────────────────────────────────────────────┘
    │
    ▼
◄────────────────────────────────────────────────────────── 用戶回應
    │ "全部和牛，三文魚淨係睇刺身"
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Step 5: 更新槽位                                                    │
│ ───────────────────────────────────────────────────────────────────│
│ slots.product_details = {                                           │
│   "A5和牛": {"parts": ["全部"]},                                     │
│   "三文魚": {"types": ["刺身"]}                                      │
│ }                                                                   │
│ slot_status: COMPLETE                                               │
└─────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Step 6: 執行工具調用                                                 │
│ ───────────────────────────────────────────────────────────────────│
│ 並行執行:                                                           │
│ - Tool: product_overview(products=["A5和牛"], parts=["全部"])        │
│ - Tool: product_overview(products=["三文魚"], types=["刺身"])        │
│ - Tool: price_trend(products=[...], days=30)                        │
│ - Tool: competitor_compare(products=[...])                          │
└─────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Step 7: 數據聚合                                                    │
│ ───────────────────────────────────────────────────────────────────│
│ 合併所有工具返回的數據:                                               │
│ {                                                                   │
│   "產品概覽": {...},                                                 │
│   "價格趨勢": {...},                                                 │
│   "競爭對手": {...}                                                  │
│ }                                                                   │
│ 總 Token: ~1,500 (vs 直接傳原始數據 ~125,000)                        │
└─────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Step 8: 報告生成                                                    │
│ ───────────────────────────────────────────────────────────────────│
│ 調用 AI 生成結構化報告:                                               │
│ - Markdown 格式                                                     │
│ - 包含表格、趨勢分析、建議                                            │
│ - 可視化數據（前端渲染圖表）                                          │
└─────────────────────────────────────────────────────────────────────┘
    │
    ▼
──────────────────────────────────────────────────────────► 顯示報告
```

### 4.2 簡單查詢流程（無需澄清）

```
用戶: "明治牛奶而家幾錢？"
    │
    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 意圖: PRODUCT_DETAIL                                                │
│ 槽位: {product: "明治牛奶"}                                          │
│ 完整度: 100% ✓                                                      │
│ → 直接執行，無需澄清                                                  │
└─────────────────────────────────────────────────────────────────────┘
    │
    ▼
執行 SQL → 返回結果 → 格式化回答
```

---

## 5. 後端設計

### 5.1 目錄結構

```
backend/app/
├── services/
│   ├── ai_service.py           # 現有 AI 服務
│   └── agent/                  # 新增 Agent 模組
│       ├── __init__.py
│       ├── agent_service.py    # Agent 主服務
│       ├── intent_classifier.py # 意圖識別
│       ├── slot_manager.py     # 槽位管理
│       ├── tool_executor.py    # 工具執行器
│       ├── report_generator.py # 報告生成
│       ├── conversation.py     # 對話管理
│       └── tools/              # 工具定義
│           ├── __init__.py
│           ├── base.py         # 工具基類
│           ├── product_tools.py # 產品相關工具
│           ├── price_tools.py   # 價格相關工具
│           ├── competitor_tools.py # 競爭對手工具
│           └── report_tools.py  # 報告工具
├── api/v1/
│   └── agent.py                # Agent API 端點
└── models/
    └── conversation.py         # 對話模型（可選）
```

### 5.2 核心類設計

#### 5.2.1 Agent 主服務

```python
# backend/app/services/agent/agent_service.py

from typing import AsyncGenerator
from dataclasses import dataclass
from enum import Enum

class AgentResponse:
    """Agent 響應類型"""
    class Type(Enum):
        MESSAGE = "message"           # 普通訊息
        CLARIFICATION = "clarification"  # 需要澄清
        REPORT = "report"             # 分析報告
        ERROR = "error"               # 錯誤
        THINKING = "thinking"         # 思考中（用於串流）

@dataclass
class AgentState:
    """Agent 狀態"""
    conversation_id: str
    messages: List[dict]
    slots: AnalysisSlots
    slot_status: Dict[str, SlotStatus]
    current_intent: IntentType
    pending_clarifications: List[str]


class AgentService:
    """AI Agent 主服務"""
    
    def __init__(self, db: AsyncSession, ai_service: AIAnalysisService):
        self.db = db
        self.ai_service = ai_service
        self.intent_classifier = IntentClassifier(ai_service)
        self.slot_manager = SlotManager()
        self.tool_executor = ToolExecutor(db)
        self.report_generator = ReportGenerator(ai_service)
    
    async def process_message(
        self,
        message: str,
        conversation_id: str = None,
        state: AgentState = None
    ) -> AsyncGenerator[AgentResponse, None]:
        """
        處理用戶訊息（串流響應）
        
        流程：
        1. 載入或創建對話狀態
        2. 識別意圖
        3. 提取/更新槽位
        4. 檢查槽位完整性
        5. 如需澄清 → 生成問題
        6. 如已完整 → 執行工具 → 生成報告
        """
        # 初始化狀態
        if state is None:
            state = AgentState(
                conversation_id=conversation_id or str(uuid.uuid4()),
                messages=[],
                slots=AnalysisSlots(),
                slot_status={},
                current_intent=None,
                pending_clarifications=[]
            )
        
        # 添加用戶訊息
        state.messages.append({"role": "user", "content": message})
        
        # Step 1: 意圖識別
        yield AgentResponse(type=AgentResponse.Type.THINKING, content="分析緊你嘅問題...")
        
        intent_result = await self.intent_classifier.classify(
            message=message,
            context=state.messages[-5:]  # 最近 5 條訊息作為上下文
        )
        state.current_intent = intent_result.intent
        
        # Step 2: 槽位提取
        extracted_slots = await self.slot_manager.extract_slots(
            message=message,
            intent=intent_result.intent,
            existing_slots=state.slots
        )
        state.slots = self.slot_manager.merge_slots(state.slots, extracted_slots)
        
        # Step 3: 檢查完整性
        completeness = self.slot_manager.check_completeness(
            slots=state.slots,
            intent=intent_result.intent
        )
        
        if not completeness.is_complete:
            # 需要澄清
            clarification = await self._generate_clarification(
                missing=completeness.missing_slots,
                ambiguous=completeness.ambiguous_slots,
                slots=state.slots
            )
            yield AgentResponse(
                type=AgentResponse.Type.CLARIFICATION,
                content=clarification.message,
                options=clarification.options,
                state=state
            )
            return
        
        # Step 4: 執行工具
        yield AgentResponse(type=AgentResponse.Type.THINKING, content="查詢緊數據...")
        
        tool_results = await self.tool_executor.execute_for_intent(
            intent=state.current_intent,
            slots=state.slots
        )
        
        # Step 5: 生成報告
        yield AgentResponse(type=AgentResponse.Type.THINKING, content="生成緊報告...")
        
        report = await self.report_generator.generate(
            intent=state.current_intent,
            slots=state.slots,
            data=tool_results
        )
        
        yield AgentResponse(
            type=AgentResponse.Type.REPORT,
            content=report.markdown,
            charts=report.charts,
            tables=report.tables,
            state=state
        )
```

#### 5.2.2 意圖識別器

```python
# backend/app/services/agent/intent_classifier.py

class IntentClassifier:
    """意圖識別器"""
    
    INTENT_PROMPT = """你是一個意圖識別系統。根據用戶輸入，識別其意圖。

可能的意圖類型：
- PRODUCT_SEARCH: 搜索特定產品（例：「有冇 A5 和牛？」）
- PRODUCT_DETAIL: 查看產品詳情（例：「明治牛奶幾錢？」）
- PRICE_ANALYSIS: 價格分析（例：「分析和牛價格」）
- TREND_ANALYSIS: 趨勢分析（例：「呢個月價格趨勢點？」）
- COMPETITOR_ANALYSIS: 競爭對手分析（例：「同百佳比邊個平？」）
- BRAND_ANALYSIS: 品牌分析（例：「邊個牌子最受歡迎？」）
- MARKET_OVERVIEW: 市場概覽（例：「我想睇和牛同海膽嘅資料」）
- GENERATE_REPORT: 生成報告（例：「幫我出份報告」）
- MARKETING_STRATEGY: Marketing 策略（例：「點樣推廣呢個產品？」）
- CLARIFICATION: 用戶回答澄清問題
- FOLLOWUP: 追問（例：「仲有呢？」「詳細啲？」）
- GREETING: 問候（例：「你好」）
- UNKNOWN: 無法識別

用戶輸入：{message}

對話歷史：
{context}

請以 JSON 格式返回：
{
  "intent": "意圖類型",
  "entities": ["識別到的實體"],
  "confidence": 0.0-1.0,
  "reasoning": "判斷理由"
}
"""

    async def classify(self, message: str, context: List[dict]) -> IntentResult:
        """識別意圖"""
        prompt = self.INTENT_PROMPT.format(
            message=message,
            context=self._format_context(context)
        )
        
        response = await self.ai_service.call_ai(prompt)
        result = json.loads(response.content)
        
        return IntentResult(
            intent=IntentType(result["intent"]),
            entities=result["entities"],
            confidence=result["confidence"]
        )
```

#### 5.2.3 工具定義

```python
# backend/app/services/agent/tools/product_tools.py

from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    """工具基類"""
    
    name: str
    description: str
    parameters: Dict[str, Any]
    
    @abstractmethod
    async def execute(self, **kwargs) -> Dict[str, Any]:
        pass


class ProductOverviewTool(BaseTool):
    """產品概覽工具"""
    
    name = "product_overview"
    description = "獲取產品概覽數據，包括 SKU 數量、價格範圍、評分等"
    parameters = {
        "products": {"type": "list", "required": True, "description": "產品名稱列表"},
        "parts": {"type": "list", "required": False, "description": "部位篩選"},
        "types": {"type": "list", "required": False, "description": "類型篩選"},
        "origin": {"type": "list", "required": False, "description": "產地篩選"}
    }
    
    async def execute(self, db: AsyncSession, **kwargs) -> Dict[str, Any]:
        products = kwargs.get("products", [])
        parts = kwargs.get("parts", [])
        
        # 構建動態 SQL
        conditions = []
        for product in products:
            # 使用產品分類知識庫中的 aliases
            aliases = PRODUCT_TAXONOMY.get(product, {}).get("aliases", [])
            all_names = [product] + aliases
            
            name_conditions = " OR ".join([
                f"name ILIKE '%{name}%'" for name in all_names
            ])
            conditions.append(f"({name_conditions})")
        
        where_clause = " OR ".join(conditions)
        
        # 執行聚合查詢
        query = f"""
            SELECT 
                CASE 
                    WHEN name ILIKE '%和牛%' OR name ILIKE '%wagyu%' THEN '和牛'
                    WHEN name ILIKE '%三文魚%' OR name ILIKE '%salmon%' THEN '三文魚'
                    ELSE '其他'
                END as product_type,
                COUNT(*) as sku_count,
                ROUND(AVG(price)::numeric, 0) as avg_price,
                MIN(price) as min_price,
                MAX(price) as max_price,
                ROUND(AVG(rating)::numeric, 2) as avg_rating,
                SUM(review_count) as total_reviews,
                COUNT(*) FILTER (WHERE stock_status = 'in_stock') as in_stock_count,
                COUNT(*) FILTER (WHERE discount_percent > 0) as on_sale_count
            FROM category_products
            WHERE {where_clause}
            GROUP BY product_type
        """
        
        result = await db.execute(text(query))
        rows = result.fetchall()
        
        return {
            "type": "product_overview",
            "data": [dict(row._mapping) for row in rows]
        }


class PriceTrendTool(BaseTool):
    """價格趨勢工具"""
    
    name = "price_trend"
    description = "獲取產品價格趨勢數據"
    parameters = {
        "products": {"type": "list", "required": True},
        "days": {"type": "int", "required": False, "default": 30}
    }
    
    async def execute(self, db: AsyncSession, **kwargs) -> Dict[str, Any]:
        products = kwargs.get("products", [])
        days = kwargs.get("days", 30)
        
        query = """
            SELECT 
                DATE_TRUNC('week', cps.scraped_at) as week,
                CASE 
                    WHEN cp.name ILIKE '%和牛%' THEN '和牛'
                    WHEN cp.name ILIKE '%三文魚%' THEN '三文魚'
                    ELSE '其他'
                END as product_type,
                ROUND(AVG(cps.price)::numeric, 0) as avg_price,
                COUNT(DISTINCT cp.id) as product_count
            FROM category_price_snapshots cps
            JOIN category_products cp ON cps.category_product_id = cp.id
            WHERE cps.scraped_at > NOW() - INTERVAL '{days} days'
            GROUP BY week, product_type
            ORDER BY week
        """
        
        result = await db.execute(text(query.format(days=days)))
        rows = result.fetchall()
        
        return {
            "type": "price_trend",
            "data": [dict(row._mapping) for row in rows]
        }


class CompetitorCompareTool(BaseTool):
    """競爭對手比較工具"""
    
    name = "competitor_compare"
    description = "比較不同平台的產品價格"
    parameters = {
        "products": {"type": "list", "required": True},
        "competitors": {"type": "list", "required": False}
    }
    
    async def execute(self, db: AsyncSession, **kwargs) -> Dict[str, Any]:
        products = kwargs.get("products", [])
        
        # 查詢 HKTVmall（我們的數據）
        our_query = """
            SELECT 
                'HKTVmall' as platform,
                CASE 
                    WHEN name ILIKE '%和牛%' THEN '和牛'
                    WHEN name ILIKE '%三文魚%' THEN '三文魚'
                    ELSE '其他'
                END as product_type,
                COUNT(*) as sku_count,
                ROUND(AVG(price)::numeric, 0) as avg_price,
                MIN(price) as min_price
            FROM category_products
            WHERE name ILIKE '%和牛%' OR name ILIKE '%三文魚%'
            GROUP BY product_type
        """
        
        # 查詢競爭對手
        competitor_query = """
            SELECT 
                c.name as platform,
                CASE 
                    WHEN cp.name ILIKE '%和牛%' THEN '和牛'
                    WHEN cp.name ILIKE '%三文魚%' THEN '三文魚'
                    ELSE '其他'
                END as product_type,
                COUNT(*) as sku_count,
                ROUND(AVG(ps.price)::numeric, 0) as avg_price,
                MIN(ps.price) as min_price
            FROM competitor_products cp
            JOIN competitors c ON cp.competitor_id = c.id
            JOIN price_snapshots ps ON cp.id = ps.competitor_product_id
            WHERE (cp.name ILIKE '%和牛%' OR cp.name ILIKE '%三文魚%')
              AND ps.scraped_at = (
                  SELECT MAX(scraped_at) FROM price_snapshots 
                  WHERE competitor_product_id = cp.id
              )
            GROUP BY c.name, product_type
        """
        
        our_result = await db.execute(text(our_query))
        comp_result = await db.execute(text(competitor_query))
        
        return {
            "type": "competitor_compare",
            "our_data": [dict(row._mapping) for row in our_result.fetchall()],
            "competitor_data": [dict(row._mapping) for row in comp_result.fetchall()]
        }


class TopProductsTool(BaseTool):
    """熱門產品工具"""
    
    name = "top_products"
    description = "獲取評論最多或評分最高的產品"
    parameters = {
        "products": {"type": "list", "required": True},
        "sort_by": {"type": "str", "required": False, "default": "review_count"},
        "limit": {"type": "int", "required": False, "default": 5}
    }
    
    async def execute(self, db: AsyncSession, **kwargs) -> Dict[str, Any]:
        products = kwargs.get("products", [])
        sort_by = kwargs.get("sort_by", "review_count")
        limit = kwargs.get("limit", 5)
        
        query = f"""
            SELECT 
                name,
                brand,
                price,
                original_price,
                discount_percent,
                rating,
                review_count,
                stock_status
            FROM category_products
            WHERE name ILIKE '%和牛%' OR name ILIKE '%三文魚%'
            ORDER BY {sort_by} DESC NULLS LAST
            LIMIT {limit}
        """
        
        result = await db.execute(text(query))
        
        return {
            "type": "top_products",
            "data": [dict(row._mapping) for row in result.fetchall()]
        }
```

### 5.3 API 端點設計

```python
# backend/app/api/v1/agent.py

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()


class ChatMessage(BaseModel):
    """聊天訊息"""
    content: str
    conversation_id: Optional[str] = None


class SlotOption(BaseModel):
    """槽位選項"""
    slot_name: str
    value: str


class ClarificationResponse(BaseModel):
    """澄清回應"""
    conversation_id: str
    selected_options: List[SlotOption]


class ChatResponse(BaseModel):
    """聊天響應"""
    type: str  # message, clarification, report, error
    content: str
    conversation_id: str
    options: Optional[List[dict]] = None  # 用於澄清問題
    charts: Optional[List[dict]] = None   # 圖表數據
    tables: Optional[List[dict]] = None   # 表格數據


# =============================================
# REST API（簡單模式）
# =============================================

@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    db: AsyncSession = Depends(get_db)
):
    """
    發送聊天訊息（非串流）
    
    適用於簡單查詢，直接返回完整響應
    """
    agent = AgentService(db, get_ai_service(db))
    
    # 收集所有響應
    final_response = None
    async for response in agent.process_message(
        message=message.content,
        conversation_id=message.conversation_id
    ):
        final_response = response
    
    return ChatResponse(
        type=final_response.type.value,
        content=final_response.content,
        conversation_id=final_response.state.conversation_id,
        options=getattr(final_response, 'options', None),
        charts=getattr(final_response, 'charts', None),
        tables=getattr(final_response, 'tables', None)
    )


@router.post("/clarify", response_model=ChatResponse)
async def clarify(
    response: ClarificationResponse,
    db: AsyncSession = Depends(get_db)
):
    """
    處理用戶對澄清問題的回應
    """
    agent = AgentService(db, get_ai_service(db))
    
    # 載入對話狀態
    state = await agent.load_state(response.conversation_id)
    
    # 更新槽位
    for option in response.selected_options:
        state.slots = agent.slot_manager.update_slot(
            state.slots,
            option.slot_name,
            option.value
        )
    
    # 繼續處理
    final_response = None
    async for resp in agent.process_message(
        message="",  # 空訊息，只處理槽位
        state=state
    ):
        final_response = resp
    
    return ChatResponse(...)


# =============================================
# WebSocket API（串流模式）
# =============================================

@router.websocket("/ws/{conversation_id}")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket 聊天（串流響應）
    
    適用於複雜查詢，實時顯示思考過程
    """
    await websocket.accept()
    
    agent = AgentService(db, get_ai_service(db))
    state = None
    
    try:
        while True:
            # 接收訊息
            data = await websocket.receive_json()
            message = data.get("content", "")
            
            # 處理訊息（串流響應）
            async for response in agent.process_message(
                message=message,
                conversation_id=conversation_id,
                state=state
            ):
                await websocket.send_json({
                    "type": response.type.value,
                    "content": response.content,
                    "options": getattr(response, 'options', None),
                    "charts": getattr(response, 'charts', None)
                })
                
                # 更新狀態
                if hasattr(response, 'state'):
                    state = response.state
    
    except WebSocketDisconnect:
        pass
```

---

## 6. 前端設計

### 6.1 組件結構

```
frontend/src/
├── app/
│   └── agent/                    # Agent 頁面
│       └── page.tsx
├── components/
│   └── agent/                    # Agent 組件
│       ├── ChatContainer.tsx     # 聊天容器
│       ├── MessageList.tsx       # 訊息列表
│       ├── MessageBubble.tsx     # 訊息氣泡
│       ├── ChatInput.tsx         # 輸入框
│       ├── ClarificationCard.tsx # 澄清問題卡片
│       ├── SlotSelector.tsx      # 槽位選擇器
│       ├── ReportView.tsx        # 報告展示
│       ├── ChartRenderer.tsx     # 圖表渲染
│       └── ThinkingIndicator.tsx # 思考中指示器
└── lib/
    └── agent-api.ts              # Agent API 客戶端
```

### 6.2 核心組件設計

#### 6.2.1 聊天容器

```tsx
// frontend/src/components/agent/ChatContainer.tsx

'use client'

import { useState, useRef, useEffect } from 'react'
import { MessageList } from './MessageList'
import { ChatInput } from './ChatInput'
import { ClarificationCard } from './ClarificationCard'
import { ReportView } from './ReportView'
import { ThinkingIndicator } from './ThinkingIndicator'

interface Message {
  id: string
  role: 'user' | 'assistant'
  type: 'message' | 'clarification' | 'report' | 'thinking'
  content: string
  options?: ClarificationOption[]
  charts?: ChartData[]
  tables?: TableData[]
  timestamp: Date
}

interface ClarificationOption {
  slot_name: string
  label: string
  options: { value: string; label: string }[]
  type: 'single' | 'multi' | 'text'
}

export function ChatContainer() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [pendingClarification, setPendingClarification] = useState<Message | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  // WebSocket 連接
  const wsRef = useRef<WebSocket | null>(null)
  
  useEffect(() => {
    // 建立 WebSocket 連接
    const ws = new WebSocket(`ws://localhost:8000/api/v1/agent/ws/${conversationId || 'new'}`)
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      handleAgentResponse(data)
    }
    
    wsRef.current = ws
    
    return () => ws.close()
  }, [conversationId])
  
  const handleAgentResponse = (response: any) => {
    switch (response.type) {
      case 'thinking':
        // 更新思考狀態
        setMessages(prev => {
          const last = prev[prev.length - 1]
          if (last?.type === 'thinking') {
            return [...prev.slice(0, -1), { ...last, content: response.content }]
          }
          return [...prev, {
            id: Date.now().toString(),
            role: 'assistant',
            type: 'thinking',
            content: response.content,
            timestamp: new Date()
          }]
        })
        break
        
      case 'clarification':
        // 顯示澄清問題
        const clarificationMsg: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          type: 'clarification',
          content: response.content,
          options: response.options,
          timestamp: new Date()
        }
        setMessages(prev => [...prev.filter(m => m.type !== 'thinking'), clarificationMsg])
        setPendingClarification(clarificationMsg)
        setIsLoading(false)
        break
        
      case 'report':
        // 顯示報告
        const reportMsg: Message = {
          id: Date.now().toString(),
          role: 'assistant',
          type: 'report',
          content: response.content,
          charts: response.charts,
          tables: response.tables,
          timestamp: new Date()
        }
        setMessages(prev => [...prev.filter(m => m.type !== 'thinking'), reportMsg])
        setIsLoading(false)
        break
    }
  }
  
  const handleSend = async (content: string) => {
    // 添加用戶訊息
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role: 'user',
      type: 'message',
      content,
      timestamp: new Date()
    }])
    
    setIsLoading(true)
    setPendingClarification(null)
    
    // 發送到 WebSocket
    wsRef.current?.send(JSON.stringify({ content }))
  }
  
  const handleClarificationSubmit = (selections: Record<string, string | string[]>) => {
    // 轉換選項為文字描述
    const description = Object.entries(selections)
      .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
      .join('; ')
    
    handleSend(description)
  }
  
  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-slate-50 to-white">
      {/* 頭部 */}
      <div className="flex items-center gap-3 p-4 border-b bg-white/80 backdrop-blur">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
          <span className="text-white text-lg">🤖</span>
        </div>
        <div>
          <h2 className="font-semibold text-slate-800">AI 分析助手</h2>
          <p className="text-xs text-slate-500">隨時為你分析市場數據</p>
        </div>
      </div>
      
      {/* 訊息區域 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <WelcomeMessage onSuggestionClick={handleSend} />
        )}
        
        <MessageList messages={messages} />
        
        {isLoading && <ThinkingIndicator />}
        
        {pendingClarification && (
          <ClarificationCard
            message={pendingClarification.content}
            options={pendingClarification.options!}
            onSubmit={handleClarificationSubmit}
          />
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* 輸入區域 */}
      <ChatInput
        onSend={handleSend}
        disabled={isLoading}
        placeholder="例如：我想睇 A5 和牛同海膽嘅資料"
      />
    </div>
  )
}

function WelcomeMessage({ onSuggestionClick }: { onSuggestionClick: (text: string) => void }) {
  const suggestions = [
    "分析 A5 和牛嘅價格趨勢",
    "比較我哋同百佳嘅海鮮價格",
    "邊啲日本零食最受歡迎？",
    "出份本月市場報告"
  ]
  
  return (
    <div className="text-center py-12">
      <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
        <span className="text-3xl">🤖</span>
      </div>
      <h3 className="text-xl font-semibold text-slate-800 mb-2">你好！我係 AI 分析助手</h3>
      <p className="text-slate-500 mb-6">我可以幫你分析 HKTVmall 嘅產品數據，試下問我：</p>
      
      <div className="flex flex-wrap justify-center gap-2">
        {suggestions.map((suggestion, i) => (
          <button
            key={i}
            onClick={() => onSuggestionClick(suggestion)}
            className="px-4 py-2 rounded-full bg-purple-50 text-purple-700 hover:bg-purple-100 transition-colors text-sm"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  )
}
```

#### 6.2.2 澄清問題卡片

```tsx
// frontend/src/components/agent/ClarificationCard.tsx

'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Check, ChevronRight } from 'lucide-react'

interface ClarificationOption {
  slot_name: string
  label: string
  options: { value: string; label: string }[]
  type: 'single' | 'multi' | 'text'
}

interface Props {
  message: string
  options: ClarificationOption[]
  onSubmit: (selections: Record<string, string | string[]>) => void
}

export function ClarificationCard({ message, options, onSubmit }: Props) {
  const [selections, setSelections] = useState<Record<string, string | string[]>>({})
  
  const handleSelect = (slotName: string, value: string, type: 'single' | 'multi') => {
    if (type === 'single') {
      setSelections(prev => ({ ...prev, [slotName]: value }))
    } else {
      setSelections(prev => {
        const current = (prev[slotName] as string[]) || []
        if (current.includes(value)) {
          return { ...prev, [slotName]: current.filter(v => v !== value) }
        }
        return { ...prev, [slotName]: [...current, value] }
      })
    }
  }
  
  const isComplete = options.every(opt => {
    const selection = selections[opt.slot_name]
    if (opt.type === 'multi') {
      return Array.isArray(selection) && selection.length > 0
    }
    return !!selection
  })
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl border border-purple-100 shadow-lg overflow-hidden"
    >
      {/* 頭部訊息 */}
      <div className="p-4 bg-gradient-to-r from-purple-50 to-blue-50 border-b border-purple-100">
        <p className="text-slate-700">{message}</p>
      </div>
      
      {/* 選項區域 */}
      <div className="p-4 space-y-6">
        {options.map((option, idx) => (
          <div key={idx}>
            <label className="block text-sm font-medium text-slate-700 mb-3">
              {option.label}
            </label>
            
            {option.type === 'text' ? (
              <input
                type="text"
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="輸入..."
                onChange={(e) => setSelections(prev => ({ ...prev, [option.slot_name]: e.target.value }))}
              />
            ) : (
              <div className="flex flex-wrap gap-2">
                {option.options.map((opt) => {
                  const isSelected = option.type === 'single'
                    ? selections[option.slot_name] === opt.value
                    : ((selections[option.slot_name] as string[]) || []).includes(opt.value)
                  
                  return (
                    <button
                      key={opt.value}
                      onClick={() => handleSelect(option.slot_name, opt.value, option.type)}
                      className={`
                        px-4 py-2 rounded-full text-sm font-medium transition-all
                        ${isSelected
                          ? 'bg-purple-600 text-white shadow-md'
                          : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                        }
                      `}
                    >
                      {isSelected && <Check className="w-4 h-4 inline mr-1" />}
                      {opt.label}
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        ))}
      </div>
      
      {/* 提交按鈕 */}
      <div className="p-4 bg-slate-50 border-t">
        <button
          onClick={() => onSubmit(selections)}
          disabled={!isComplete}
          className={`
            w-full py-3 rounded-xl font-medium flex items-center justify-center gap-2
            transition-all
            ${isComplete
              ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:shadow-lg'
              : 'bg-slate-200 text-slate-400 cursor-not-allowed'
            }
          `}
        >
          開始分析
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </motion.div>
  )
}
```

#### 6.2.3 報告展示組件

```tsx
// frontend/src/components/agent/ReportView.tsx

'use client'

import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { motion } from 'framer-motion'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { Download, Copy, Share2, Check } from 'lucide-react'

interface Props {
  content: string
  charts?: ChartData[]
  tables?: TableData[]
}

interface ChartData {
  type: 'line' | 'bar'
  title: string
  data: any[]
  config: {
    xKey: string
    yKeys: { key: string; color: string; name: string }[]
  }
}

export function ReportView({ content, charts, tables }: Props) {
  const [copied, setCopied] = useState(false)
  
  const handleCopy = async () => {
    await navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl border shadow-lg overflow-hidden"
    >
      {/* 工具欄 */}
      <div className="flex items-center justify-between p-3 bg-slate-50 border-b">
        <span className="text-sm font-medium text-slate-600">分析報告</span>
        <div className="flex gap-2">
          <button
            onClick={handleCopy}
            className="p-2 rounded-lg hover:bg-slate-200 transition-colors"
            title="複製"
          >
            {copied ? <Check className="w-4 h-4 text-green-600" /> : <Copy className="w-4 h-4 text-slate-500" />}
          </button>
          <button
            className="p-2 rounded-lg hover:bg-slate-200 transition-colors"
            title="下載"
          >
            <Download className="w-4 h-4 text-slate-500" />
          </button>
          <button
            className="p-2 rounded-lg hover:bg-slate-200 transition-colors"
            title="分享"
          >
            <Share2 className="w-4 h-4 text-slate-500" />
          </button>
        </div>
      </div>
      
      {/* Markdown 內容 */}
      <div className="p-6 prose prose-slate max-w-none">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            // 自定義表格樣式
            table: ({ children }) => (
              <div className="overflow-x-auto my-4">
                <table className="min-w-full divide-y divide-slate-200">
                  {children}
                </table>
              </div>
            ),
            th: ({ children }) => (
              <th className="px-4 py-3 bg-slate-50 text-left text-sm font-semibold text-slate-700">
                {children}
              </th>
            ),
            td: ({ children }) => (
              <td className="px-4 py-3 text-sm text-slate-600 border-b border-slate-100">
                {children}
              </td>
            ),
            // 自定義代碼塊
            code: ({ className, children }) => {
              const isInline = !className
              if (isInline) {
                return <code className="px-1 py-0.5 bg-slate-100 rounded text-purple-600">{children}</code>
              }
              return <code className={className}>{children}</code>
            }
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
      
      {/* 圖表區域 */}
      {charts && charts.length > 0 && (
        <div className="px-6 pb-6 space-y-6">
          {charts.map((chart, idx) => (
            <div key={idx} className="bg-slate-50 rounded-xl p-4">
              <h4 className="text-sm font-medium text-slate-700 mb-4">{chart.title}</h4>
              <ResponsiveContainer width="100%" height={300}>
                {chart.type === 'line' ? (
                  <LineChart data={chart.data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey={chart.config.xKey} stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip />
                    <Legend />
                    {chart.config.yKeys.map(y => (
                      <Line
                        key={y.key}
                        type="monotone"
                        dataKey={y.key}
                        stroke={y.color}
                        name={y.name}
                        strokeWidth={2}
                        dot={{ fill: y.color }}
                      />
                    ))}
                  </LineChart>
                ) : (
                  <BarChart data={chart.data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey={chart.config.xKey} stroke="#64748b" fontSize={12} />
                    <YAxis stroke="#64748b" fontSize={12} />
                    <Tooltip />
                    <Legend />
                    {chart.config.yKeys.map(y => (
                      <Bar key={y.key} dataKey={y.key} fill={y.color} name={y.name} />
                    ))}
                  </BarChart>
                )}
              </ResponsiveContainer>
            </div>
          ))}
        </div>
      )}
    </motion.div>
  )
}
```

---

## 7. 對話示例

### 7.1 簡單查詢（無需澄清）

```
👤 用戶：明治牛奶而家幾錢？

🤖 AI：明治牛奶目前價格：

| 產品 | 現價 | 原價 | 折扣 |
|------|------|------|------|
| 明治牛奶 1L | $28 | $32 | -12.5% |
| 明治低脂牛奶 1L | $30 | $30 | - |
| 明治特濃牛奶 946ml | $35 | $38 | -7.9% |

💡 目前明治牛奶 1L 有折扣，係最抵嘅選擇！
```

### 7.2 複雜查詢（需要澄清）

```
👤 用戶：我想睇和牛同海膽嘅資料

🤖 AI：好！想再確認幾樣嘢：

📦 和牛方面
┌─────────────────────────────────┐
│ 部位：                          │
│ ○ 全部部位                      │
│ ○ 西冷 / 肉眼 / 牛柳            │
│ ○ 火鍋片 / 燒肉片               │
└─────────────────────────────────┘

🦐 海膽方面
┌─────────────────────────────────┐
│ 類型：                          │
│ ○ 全部類型                      │
│ ○ 馬糞海膽                      │
│ ○ 紫海膽                        │
│ ○ 海膽醬                        │
└─────────────────────────────────┘

⏰ 時間範圍
┌─────────────────────────────────┐
│ ○ 過去 7 日                     │
│ ● 過去 30 日（推薦）             │
│ ○ 過去 90 日                    │
└─────────────────────────────────┘

👤 用戶：全部和牛，海膽淨係睇馬糞，30日

🤖 AI：明白！分析緊... ⏳

🤖 AI：[生成完整報告，包含表格和圖表]
```

### 7.3 追問對話

```
👤 用戶：邊個牌子最受歡迎？

🤖 AI：基於評論數量，最受歡迎嘅品牌：

**和牛**
1. 🥇 鹿兒島 - 2,340 評論
2. 🥈 宮崎 - 1,890 評論
3. 🥉 神戶 - 1,456 評論

**海膽**
1. 🥇 北海道 - 1,234 評論
2. 🥈 青森 - 876 評論

👤 用戶：鹿兒島有啲咩產品？

🤖 AI：鹿兒島和牛產品列表：

| 產品 | 價格 | 評分 | 評論 |
|------|------|------|------|
| 鹿兒島A5和牛西冷 200g | $480 | ⭐4.8 | 892 |
| 鹿兒島A5和牛肉眼 150g | $420 | ⭐4.7 | 654 |
| 鹿兒島和牛火鍋片 300g | $380 | ⭐4.6 | 432 |
| ... | | | |

共 12 款產品，平均評分 4.7
```

---

## 8. 實現計劃

### 8.1 階段劃分

| 階段 | 任務 | 預計時間 |
|------|------|----------|
| **A: 後端基礎** | | |
| A1 | 定義 Agent Tools (SQL 查詢工具) | 2 小時 |
| A2 | 實現 Slot Filling 邏輯 | 2 小時 |
| A3 | 實現 Agent 對話 API | 2 小時 |
| A4 | 實現報告生成服務 | 1 小時 |
| **B: 前端實現** | | |
| B1 | Chat UI 組件 | 2 小時 |
| B2 | 互動式 Slot Filling UI | 2 小時 |
| B3 | 報告展示組件 | 1 小時 |
| **C: 整合測試** | | |
| C1 | 整合測試 + 優化 | 2 小時 |

### 8.2 檔案清單

#### 後端新增檔案

```
backend/app/services/agent/
├── __init__.py
├── agent_service.py        # 主服務
├── intent_classifier.py    # 意圖識別
├── slot_manager.py         # 槽位管理
├── tool_executor.py        # 工具執行
├── report_generator.py     # 報告生成
├── conversation.py         # 對話管理
├── taxonomy.py             # 產品分類知識庫
└── tools/
    ├── __init__.py
    ├── base.py             # 工具基類
    ├── product_tools.py    # 產品工具
    ├── price_tools.py      # 價格工具
    ├── competitor_tools.py # 競爭對手工具
    └── report_tools.py     # 報告工具

backend/app/api/v1/
└── agent.py                # API 端點
```

#### 前端新增檔案

```
frontend/src/app/agent/
└── page.tsx                # Agent 頁面

frontend/src/components/agent/
├── ChatContainer.tsx       # 聊天容器
├── MessageList.tsx         # 訊息列表
├── MessageBubble.tsx       # 訊息氣泡
├── ChatInput.tsx           # 輸入框
├── ClarificationCard.tsx   # 澄清卡片
├── SlotSelector.tsx        # 槽位選擇器
├── ReportView.tsx          # 報告展示
├── ChartRenderer.tsx       # 圖表渲染
└── ThinkingIndicator.tsx   # 思考指示器

frontend/src/lib/
└── agent-api.ts            # API 客戶端
```

### 8.3 依賴項

#### 後端

```
# 無需新增依賴，使用現有的：
- fastapi
- sqlalchemy
- httpx (已有，用於 AI 調用)
```

#### 前端

```bash
# 可能需要新增：
npm install react-markdown remark-gfm
# recharts 應該已有
```

---

## 附錄

### A. 產品分類完整知識庫

見 `backend/app/services/agent/taxonomy.py`

### B. SQL 查詢模板庫

見各 Tool 實現

### C. 報告模板

見 `report_generator.py`

---

> 文檔結束  
> 下一步：開始實現 A1 - 定義 Agent Tools
