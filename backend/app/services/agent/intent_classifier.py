# =============================================
# 意圖識別器
# =============================================

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import json
import re

from .taxonomy import get_all_product_names, normalize_product_name


class IntentType(Enum):
    """意圖類型"""
    # 產品查詢
    PRODUCT_SEARCH = "product_search"
    PRODUCT_DETAIL = "product_detail"
    
    # 分析類
    PRICE_ANALYSIS = "price_analysis"
    TREND_ANALYSIS = "trend_analysis"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    BRAND_ANALYSIS = "brand_analysis"
    MARKET_OVERVIEW = "market_overview"
    
    # 報告類
    GENERATE_REPORT = "generate_report"
    MARKETING_STRATEGY = "marketing_strategy"
    
    # 營運類 (New)
    FINANCE_ANALYSIS = "finance_analysis"
    ORDER_QUERY = "order_query"
    INVENTORY_QUERY = "inventory_query"
    
    # 對話類
    CLARIFICATION = "clarification"
    FOLLOWUP = "followup"
    GREETING = "greeting"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class IntentResult:
    """意圖識別結果"""
    intent: IntentType
    entities: List[str]
    confidence: float
    reasoning: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent.value,
            "entities": self.entities,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
        }


class IntentClassifier:
    """
    意圖識別器
    
    使用規則 + AI 混合方式識別用戶意圖
    """
    
    # 意圖關鍵詞映射
    INTENT_KEYWORDS = {
        IntentType.PRODUCT_SEARCH: [
            "有冇", "有無", "有沒有", "搵", "找", "search", "查",
        ],
        IntentType.PRODUCT_DETAIL: [
            "幾錢", "幾多錢", "價格", "價錢", "多少錢", "price",
        ],
        IntentType.PRICE_ANALYSIS: [
            "價格分析", "分析價格", "價錢分析",
        ],
        IntentType.TREND_ANALYSIS: [
            "趨勢", "走勢", "變化", "trend", "變動",
        ],
        IntentType.COMPETITOR_ANALYSIS: [
            "競爭", "對手", "比較", "百佳", "惠康", "competitor", "compare",
        ],
        IntentType.BRAND_ANALYSIS: [
            "品牌", "牌子", "brand", "邊個牌",
        ],
        IntentType.MARKET_OVERVIEW: [
            "資料", "數據", "情況", "概覽", "overview", "分析",
        ],
        IntentType.GENERATE_REPORT: [
            "報告", "report", "出份", "生成",
        ],
        IntentType.MARKETING_STRATEGY: [
            "marketing", "推廣", "策略", "點樣賣", "點推",
        ],
        IntentType.FINANCE_ANALYSIS: [
            "利潤", "賺", "收入", "營收", "profit", "revenue", "sales", "財務", "賺錢"
        ],
        IntentType.ORDER_QUERY: [
            "訂單", "order", "未出貨", "待處理", "shipping", "ship"
        ],
        IntentType.INVENTORY_QUERY: [
            "庫存", "存貨", "stock", "inventory", "缺貨", "無貨"
        ],
        IntentType.GREETING: [
            "你好", "hello", "hi", "哈囉", "早晨", "午安",
        ],
        IntentType.HELP: [
            "幫助", "help", "點用", "教我", "可以做咩",
        ],
        IntentType.FOLLOWUP: [
            "仲有", "繼續", "詳細", "more", "再講", "然後",
        ],
    }
    
    # AI 提示模板
    INTENT_PROMPT = """你是一個意圖識別系統。根據用戶輸入，識別其意圖和實體。

可能的意圖類型：
- PRODUCT_SEARCH: 搜索特定產品（例：「有冇 A5 和牛？」）
- PRODUCT_DETAIL: 查看產品詳情/價格（例：「明治牛奶幾錢？」）
- PRICE_ANALYSIS: 價格分析（例：「分析和牛價格」）
- TREND_ANALYSIS: 趨勢分析（例：「呢個月價格趨勢點？」）
- COMPETITOR_ANALYSIS: 競爭對手分析（例：「同百佳比邊個平？」）
- BRAND_ANALYSIS: 品牌分析（例：「邊個牌子最受歡迎？」）
- MARKET_OVERVIEW: 市場概覽（例：「我想睇和牛同海膽嘅資料」）
- GENERATE_REPORT: 生成報告（例：「幫我出份報告」）
- MARKETING_STRATEGY: Marketing 策略（例：「點樣推廣呢個產品？」）
- FINANCE_ANALYSIS: 財務分析（例：「上個月賺幾多？」「利潤趨勢」）
- ORDER_QUERY: 訂單查詢（例：「有幾多單未出貨？」「今日幾多單？」）
- INVENTORY_QUERY: 庫存查詢（例：「邊啲貨就快賣曬？」）
- CLARIFICATION: 用戶回答澄清問題（例：「全部部位」「淨係睇刺身」）
- FOLLOWUP: 追問（例：「仲有呢？」「詳細啲？」）
- GREETING: 問候（例：「你好」）
- HELP: 求助（例：「你可以做咩？」）
- UNKNOWN: 無法識別

用戶輸入：{message}

對話歷史：
{context}

請以 JSON 格式返回：
{{
  "intent": "意圖類型",
  "entities": ["識別到的產品/品牌實體"],
  "confidence": 0.0-1.0,
  "reasoning": "判斷理由"
}}
"""
    
    def __init__(self, ai_service=None):
        """
        初始化意圖識別器
        
        Args:
            ai_service: AI 服務（可選，用於複雜識別）
        """
        self.ai_service = ai_service
        self.product_names = get_all_product_names()
    
    async def classify(
        self,
        message: str,
        context: List[Dict] = None,
        use_ai: bool = False
    ) -> IntentResult:
        """
        識別意圖
        
        Args:
            message: 用戶訊息
            context: 對話歷史
            use_ai: 是否使用 AI 識別
        
        Returns:
            意圖識別結果
        """
        # 首先嘗試規則識別
        rule_result = self._classify_by_rules(message)
        
        if rule_result.confidence >= 0.8:
            return rule_result
        
        # 如果規則識別信心度不夠且有 AI 服務，使用 AI
        if use_ai and self.ai_service:
            ai_result = await self._classify_by_ai(message, context)
            
            # 選擇信心度更高的結果
            if ai_result.confidence > rule_result.confidence:
                return ai_result
        
        return rule_result
    
    def _classify_by_rules(self, message: str) -> IntentResult:
        """
        使用規則識別意圖
        """
        message_lower = message.lower()
        
        # 提取實體
        entities = self._extract_entities(message)
        
        # 計算每個意圖的匹配分數
        scores = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    score += 1
            if score > 0:
                scores[intent] = score
        
        # 如果沒有匹配
        if not scores:
            # 檢查是否只有產品名稱（默認為市場概覽）
            if entities:
                return IntentResult(
                    intent=IntentType.MARKET_OVERVIEW,
                    entities=entities,
                    confidence=0.7,
                    reasoning="檢測到產品名稱，默認為市場概覽"
                )
            
            return IntentResult(
                intent=IntentType.UNKNOWN,
                entities=entities,
                confidence=0.3,
                reasoning="無法識別意圖"
            )
        
        # 選擇分數最高的意圖
        best_intent = max(scores, key=scores.get)
        max_score = scores[best_intent]
        
        # 計算信心度
        confidence = min(0.5 + max_score * 0.15, 0.95)
        
        return IntentResult(
            intent=best_intent,
            entities=entities,
            confidence=confidence,
            reasoning=f"匹配關鍵詞數: {max_score}"
        )
    
    def _extract_entities(self, message: str) -> List[str]:
        """提取實體（產品名稱）"""
        entities = []
        message_lower = message.lower()
        
        for name in self.product_names:
            if name.lower() in message_lower:
                normalized = normalize_product_name(name)
                if normalized not in entities:
                    entities.append(normalized)
        
        return entities
    
    async def _classify_by_ai(
        self,
        message: str,
        context: List[Dict] = None
    ) -> IntentResult:
        """
        使用 AI 識別意圖
        """
        if not self.ai_service:
            return IntentResult(
                intent=IntentType.UNKNOWN,
                entities=[],
                confidence=0,
                reasoning="無 AI 服務"
            )
        
        # 格式化上下文
        context_str = ""
        if context:
            for msg in context[-5:]:  # 最近 5 條
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                context_str += f"{role}: {content}\n"
        
        prompt = self.INTENT_PROMPT.format(
            message=message,
            context=context_str or "（無）"
        )
        
        try:
            response = await self.ai_service.call_ai(prompt)
            
            # 解析 JSON
            # 嘗試提取 JSON
            json_match = re.search(r'\{[^{}]*\}', response.content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(response.content)
            
            intent_str = result.get("intent", "UNKNOWN")
            try:
         
