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

    # 營運類 - 訂單
    ORDER_STATS = "order_stats"
    ORDER_SEARCH = "order_search"

    # 營運類 - 財務
    FINANCE_SUMMARY = "finance_summary"
    SETTLEMENT_QUERY = "settlement_query"

    # 營運類 - 警報
    ALERT_QUERY = "alert_query"
    ALERT_ACTION = "alert_action"

    # 營運類 - 通知
    SEND_NOTIFICATION = "send_notification"

    # 營運類 (舊，保留向後兼容)
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
        # 訂單相關
        IntentType.ORDER_STATS: [
            "幾多單", "訂單統計", "未出貨", "待處理", "訂單數", "today order",
            "今日訂單", "今日幾多", "幾張單", "order stats", "pending orders"
        ],
        IntentType.ORDER_SEARCH: [
            "搵訂單", "查訂單", "訂單號", "order number", "order search",
            "訂單詳情", "邊張單", "which order", "搵單", "查單",
            "order id", "order #"
        ],
        # 財務相關
        IntentType.FINANCE_SUMMARY: [
            "營收", "收入", "利潤", "淨利", "賺幾多", "財務摘要", "賺錢",
            "revenue", "profit", "income", "earnings", "財務報告"
        ],
        IntentType.SETTLEMENT_QUERY: [
            "結算", "結算單", "settlement", "結帳", "對帳", "帳單"
        ],
        # 警報相關
        IntentType.ALERT_QUERY: [
            "警報", "提醒", "價格警報", "庫存警報", "alert", "警示",
            "price alert", "缺貨提醒", "有咩警報"
        ],
        IntentType.ALERT_ACTION: [
            "標記已讀", "全部已讀", "mark read", "清除警報", "dismiss"
        ],
        # 通知相關
        IntentType.SEND_NOTIFICATION: [
            "發通知", "發telegram", "send notification", "通知我",
            "提醒我", "發訊息", "send message", "telegram"
        ],
        # 舊意圖 (保留向後兼容)
        IntentType.FINANCE_ANALYSIS: [
            "利潤分析", "財務分析", "sales analysis"
        ],
        IntentType.ORDER_QUERY: [
            "訂單查詢"
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
- ORDER_STATS: 訂單統計（例：「今日有幾多單？」「未出貨訂單」「待處理幾多單？」）
- ORDER_SEARCH: 訂單搜索（例：「幫我搵訂單 1234567」「查下呢張單」）
- FINANCE_SUMMARY: 財務摘要（例：「上個月營收幾多？」「今月賺幾多？」「利潤率」）
- SETTLEMENT_QUERY: 結算查詢（例：「最近嘅結算單」「上期結算幾多？」）
- ALERT_QUERY: 警報查詢（例：「有咩價格警報？」「有無缺貨提醒？」）
- ALERT_ACTION: 警報操作（例：「全部標記已讀」「清除警報」）
- SEND_NOTIFICATION: 發送通知（例：「發個 Telegram 通知」「提醒我」）
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
            print(f"[IntentClassifier] 規則信心度 {rule_result.confidence} < 0.8，嘗試 AI 識別...")
            ai_result = await self._classify_by_ai(message, context)
            print(f"[IntentClassifier] AI 結果: intent={ai_result.intent.value}, confidence={ai_result.confidence}")

            # 選擇信心度更高的結果
            if ai_result.confidence > rule_result.confidence:
                print(f"[IntentClassifier] 採用 AI 結果 (AI {ai_result.confidence} > Rule {rule_result.confidence})")
                return ai_result
            else:
                print(f"[IntentClassifier] 採用規則結果 (Rule {rule_result.confidence} >= AI {ai_result.confidence})")

        print(f"[IntentClassifier] 最終結果: intent={rule_result.intent.value}, entities={rule_result.entities}")
        return rule_result
    
    def _classify_by_rules(self, message: str) -> IntentResult:
        """
        使用規則識別意圖
        """
        message_lower = message.lower()

        # 提取實體
        entities = self._extract_entities(message)

        # Debug logging
        print(f"[IntentClassifier] 輸入: {message}")
        print(f"[IntentClassifier] 提取實體: {entities}")
        print(f"[IntentClassifier] 產品名稱庫大小: {len(self.product_names)}")
        
        # 計算每個意圖的匹配分數
        scores = {}
        matched_keywords = []
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    score += 1
                    matched_keywords.append((intent.value, keyword))
            if score > 0:
                scores[intent] = score

        print(f"[IntentClassifier] 匹配關鍵詞: {matched_keywords}")
        print(f"[IntentClassifier] 意圖分數: {[(k.value, v) for k, v in scores.items()]}")

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
            print(f"[IntentClassifier] 調用 AI API...")
            response = await self.ai_service.call_ai(prompt)
            print(f"[IntentClassifier] AI 回應 success={response.success}, content長度={len(response.content) if response.content else 0}")

            if not response.success:
                print(f"[IntentClassifier] AI 調用失敗: {response.error}")
                return IntentResult(
                    intent=IntentType.UNKNOWN,
                    entities=[],
                    confidence=0,
                    reasoning=f"AI 調用失敗: {response.error}"
                )

            # 解析 JSON
            # 嘗試提取 JSON
            json_match = re.search(r'\{[^{}]*\}', response.content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(response.content)

            print(f"[IntentClassifier] AI JSON 解析成功: {result}")

            intent_str = result.get("intent", "UNKNOWN")
            try:
                intent = IntentType(intent_str)
            except ValueError:
                # 嘗試大小寫轉換
                try:
                    intent = IntentType(intent_str.lower())
                except ValueError:
                    print(f"[IntentClassifier] 無法識別意圖類型: {intent_str}")
                    intent = IntentType.UNKNOWN

            entities = result.get("entities", [])
            confidence = result.get("confidence", 0.7)
            reasoning = result.get("reasoning", "")

            return IntentResult(
                intent=intent,
                entities=entities,
                confidence=confidence,
                reasoning=reasoning
            )
        except Exception as e:
            print(f"[IntentClassifier] AI 識別異常: {type(e).__name__}: {str(e)}")
            return IntentResult(
                intent=IntentType.UNKNOWN,
                entities=[],
                confidence=0,
                reasoning=f"AI 識別失敗: {str(e)}"
            )
