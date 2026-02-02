# =============================================
# 意圖識別器
# =============================================

import json
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from .taxonomy import get_all_product_names, normalize_product_name

logger = logging.getLogger(__name__)


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

    # CRUD 操作類
    ADD_COMPETITOR = "add_competitor"       # 新增競爭對手
    ADD_PRODUCT = "add_product"             # 新增產品/監控項目
    NAVIGATE = "navigate"                   # 導航到特定功能頁面

    # 營運類 (舊，保留向後兼容)
    FINANCE_ANALYSIS = "finance_analysis"
    ORDER_QUERY = "order_query"
    INVENTORY_QUERY = "inventory_query"

    # 工作流類 - 審批相關
    CREATE_APPROVAL_TASK = "create_approval_task"  # 創建改價審批任務
    CONFIRM_ACTION = "confirm_action"              # 確認執行動作
    DECLINE_ACTION = "decline_action"              # 拒絕執行動作

    # 工作流類 - 排程相關
    CREATE_SCHEDULED_REPORT = "create_scheduled_report"  # 創建排程報告
    PAUSE_SCHEDULED_REPORT = "pause_scheduled_report"    # 暫停排程
    RESUME_SCHEDULED_REPORT = "resume_scheduled_report"  # 恢復排程
    DELETE_SCHEDULED_REPORT = "delete_scheduled_report"  # 刪除排程
    LIST_SCHEDULES = "list_schedules"                    # 列出排程

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
        # CRUD 操作相關 (需要高優先級匹配)
        IntentType.ADD_COMPETITOR: [
            "加入競爭", "新增競爭", "加競爭對手", "add competitor",
            "加入對手", "新增對手", "監控對手", "追蹤對手",
            "加入一個競爭", "想加入競爭", "想新增競爭",
            # 動作詞 + 對象組合 (增加匹配機會)
            "想加入", "我想加", "想新增", "我想新增",
            "幫我加", "幫我新增", "加多個", "加一個"
        ],
        IntentType.ADD_PRODUCT: [
            "加入產品", "新增產品", "加產品", "add product",
            "加入貨品", "新增貨品", "監控產品", "追蹤產品",
            "加入商品", "新增商品", "想加入產品", "想新增產品",
            # 動作詞組合
            "想加入", "我想加", "想新增", "我想新增",
            "幫我加", "幫我新增"
        ],
        IntentType.NAVIGATE: [
            "點去", "去邊", "邊度可以", "喺邊度", "where is",
            "how to", "點樣", "點開", "navigate", "go to",
            "打開", "開啟", "進入", "跳轉"
        ],
        # 工作流審批相關
        IntentType.CREATE_APPROVAL_TASK: [
            "創建審批", "創建改價", "幫我創建", "開個任務", "開審批",
            "create approval", "create task", "改價任務", "提交審批",
            "開改價", "建議改價", "改呢個價", "幫我改價",
            "申請改價", "提交改價", "想改價", "要改價"
        ],
        IntentType.CONFIRM_ACTION: [
            "好", "係", "確認", "confirm", "yes", "ok", "得",
            "冇問題", "同意", "批准", "proceed", "執行", "做啦"
        ],
        IntentType.DECLINE_ACTION: [
            "唔好", "唔係", "取消", "cancel", "no", "算", "唔要",
            "唔同意", "拒絕", "reject", "decline", "算啦", "唔做"
        ],
        # 排程報告相關
        IntentType.CREATE_SCHEDULED_REPORT: [
            "排程", "定時", "schedule", "每日", "每週", "每月",
            "daily", "weekly", "monthly", "自動發送", "定期報告",
            "創建排程", "設定排程", "新增排程", "建立排程",
            "每日報告", "每週報告", "每月報告", "自動報告"
        ],
        IntentType.PAUSE_SCHEDULED_REPORT: [
            "暫停排程", "停止排程", "pause schedule", "stop schedule",
            "暫停報告", "停止報告", "暫停自動", "停止自動"
        ],
        IntentType.RESUME_SCHEDULED_REPORT: [
            "恢復排程", "繼續排程", "resume schedule", "restart schedule",
            "重啟排程", "恢復報告", "繼續報告"
        ],
        IntentType.DELETE_SCHEDULED_REPORT: [
            "刪除排程", "移除排程", "delete schedule", "remove schedule",
            "取消排程", "刪除報告排程"
        ],
        IntentType.LIST_SCHEDULES: [
            "我的排程", "查看排程", "排程列表", "list schedules",
            "有咩排程", "有邊啲排程", "顯示排程", "所有排程"
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
- ADD_COMPETITOR: 新增競爭對手（例：「我想加入一個競爭對手」「幫我新增對手」「監控百佳」）
- ADD_PRODUCT: 新增產品/監控項目（例：「加入新產品」「想監控呢個商品」「新增貨品」）
- NAVIGATE: 導航到特定功能（例：「點去加競爭對手？」「喺邊度可以新增產品？」「how to add competitor」）
- INVENTORY_QUERY: 庫存查詢（例：「邊啲貨就快賣曬？」）
- CREATE_APPROVAL_TASK: 創建改價審批任務（例：「幫我創建改價任務」「申請改呢個價」「建議改價到 $99」）
- CONFIRM_ACTION: 確認執行動作（例：「好」「確認」「係」「執行」）
- DECLINE_ACTION: 拒絕執行動作（例：「唔好」「取消」「算啦」）
- CREATE_SCHEDULED_REPORT: 創建排程報告（例：「每日早上 9 點發送和牛價格報告」「設定每週競品分析」）
- PAUSE_SCHEDULED_REPORT: 暫停排程報告（例：「暫停呢個排程」「停止自動報告」）
- RESUME_SCHEDULED_REPORT: 恢復排程報告（例：「恢復排程」「繼續自動報告」）
- DELETE_SCHEDULED_REPORT: 刪除排程報告（例：「刪除呢個排程」「移除自動報告」）
- LIST_SCHEDULES: 列出排程（例：「我有咩排程？」「顯示所有排程」）
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
            logger.debug(f"規則信心度 {rule_result.confidence} < 0.8，嘗試 AI 識別...")
            ai_result = await self._classify_by_ai(message, context)
            logger.debug(f"AI 結果: intent={ai_result.intent.value}, confidence={ai_result.confidence}")

            # 選擇信心度更高的結果
            if ai_result.confidence > rule_result.confidence:
                logger.debug(f"採用 AI 結果 (AI {ai_result.confidence} > Rule {rule_result.confidence})")
                return ai_result
            else:
                logger.debug(f"採用規則結果 (Rule {rule_result.confidence} >= AI {ai_result.confidence})")

        logger.debug(f"最終結果: intent={rule_result.intent.value}, entities={rule_result.entities}")
        return rule_result
    
    def _classify_by_rules(self, message: str) -> IntentResult:
        """
        使用規則識別意圖
        """
        message_lower = message.lower()

        # 提取實體
        entities = self._extract_entities(message)

        # Debug logging
        logger.debug(f"輸入: {message}")
        logger.debug(f"提取實體: {entities}")
        logger.debug(f"產品名稱庫大小: {len(self.product_names)}")
        
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

        logger.debug(f"匹配關鍵詞: {matched_keywords}")
        logger.debug(f"意圖分數: {[(k.value, v) for k, v in scores.items()]}")

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
            logger.debug("調用 AI API...")
            response = await self.ai_service.call_ai(prompt)
            logger.debug(f"AI 回應 success={response.success}, content長度={len(response.content) if response.content else 0}")

            if not response.success:
                logger.warning(f"AI 調用失敗: {response.error}")
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

            logger.debug(f"AI JSON 解析成功: {result}")

            intent_str = result.get("intent", "UNKNOWN")
            try:
                intent = IntentType(intent_str)
            except ValueError:
                # 嘗試大小寫轉換
                try:
                    intent = IntentType(intent_str.lower())
                except ValueError:
                    logger.warning(f"無法識別意圖類型: {intent_str}")
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
            logger.error(f"AI 識別異常: {type(e).__name__}: {str(e)}", exc_info=True)
            return IntentResult(
                intent=IntentType.UNKNOWN,
                entities=[],
                confidence=0,
                reasoning=f"AI 識別失敗: {str(e)}"
            )
