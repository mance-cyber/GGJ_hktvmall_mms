# =============================================
# 槽位管理器
# 負責槽位提取、驗證和填充
# =============================================

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .taxonomy import (
    PRODUCT_TAXONOMY,
    TIME_RANGE_OPTIONS,
    ANALYSIS_DIMENSIONS,
    normalize_product_name,
    get_product_clarification_questions,
)


class SlotStatus(Enum):
    """槽位狀態"""
    EMPTY = "empty"           # 未填充
    PARTIAL = "partial"       # 部分填充
    COMPLETE = "complete"     # 完整填充
    AMBIGUOUS = "ambiguous"   # 有歧義


@dataclass
class ProductDetail:
    """產品細節槽位"""
    parts: List[str] = field(default_factory=list)
    types: List[str] = field(default_factory=list)
    origin: List[str] = field(default_factory=list)
    brands: List[str] = field(default_factory=list)
    price_range: Optional[Tuple[float, float]] = None
    grades: List[str] = field(default_factory=list)


@dataclass
class ScheduleSlots:
    """排程槽位"""
    # 頻率
    frequency: Optional[str] = None  # daily, weekly, monthly
    # 執行時間
    schedule_time: Optional[str] = None  # HH:MM
    # 執行日 (週幾/月幾號)
    schedule_day: Optional[int] = None
    # 報告類型
    report_type: Optional[str] = None
    # 產品列表
    products: List[str] = field(default_factory=list)
    # 排程名稱
    name: Optional[str] = None
    # 交付渠道
    delivery_channel: Optional[str] = None  # telegram, email

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frequency": self.frequency,
            "schedule_time": self.schedule_time,
            "schedule_day": self.schedule_day,
            "report_type": self.report_type,
            "products": self.products,
            "name": self.name,
            "delivery_channel": self.delivery_channel,
        }


@dataclass
class AnalysisSlots:
    """分析查詢的槽位"""
    
    # 必填：產品列表
    products: List[str] = field(default_factory=list)
    
    # 產品細節（可選）
    product_details: Dict[str, ProductDetail] = field(default_factory=dict)
    
    # 時間範圍
    time_range: str = "30d"
    
    # 分析維度
    analysis_dimensions: List[str] = field(default_factory=lambda: [
        "price_overview",
        "price_trend",
        "competitor_compare",
    ])
    
    # 競爭對手
    include_competitors: bool = True
    competitor_ids: List[str] = field(default_factory=list)
    
    # 輸出格式
    output_format: str = "report"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "products": self.products,
            "product_details": {
                k: {
                    "parts": v.parts,
                    "types": v.types,
                    "origin": v.origin,
                    "brands": v.brands,
                    "grades": v.grades,
                }
                for k, v in self.product_details.items()
            },
            "time_range": self.time_range,
            "analysis_dimensions": self.analysis_dimensions,
            "include_competitors": self.include_competitors,
            "output_format": self.output_format,
        }


@dataclass
class SlotCompleteness:
    """槽位完整性檢查結果"""
    is_complete: bool
    missing_slots: List[str]
    ambiguous_slots: List[str]
    clarification_needed: List[Dict[str, Any]]
    confidence: float


@dataclass
class ClarificationQuestion:
    """澄清問題"""
    slot_name: str
    question: str
    options: List[Dict[str, str]]
    question_type: str = "single"  # single, multi, text


class SlotManager:
    """
    槽位管理器
    
    負責：
    1. 從用戶輸入中提取槽位值
    2. 檢查槽位完整性
    3. 生成澄清問題
    4. 合併槽位
    """
    
    def __init__(self):
        self.taxonomy = PRODUCT_TAXONOMY
    
    def extract_slots(self, message: str, entities: List[str] = None) -> AnalysisSlots:
        """
        從用戶訊息中提取槽位
        
        Args:
            message: 用戶訊息
            entities: 已識別的實體
        
        Returns:
            提取的槽位
        """
        slots = AnalysisSlots()
        message_lower = message.lower()
        
        # 提取產品
        products = self._extract_products(message, entities)
        slots.products = products
        
        # 提取時間範圍
        time_range = self._extract_time_range(message)
        if time_range:
            slots.time_range = time_range
        
        # 提取產品細節
        for product in products:
            detail = self._extract_product_detail(message, product)
            if detail:
                slots.product_details[product] = detail
        
        # 提取分析維度
        dimensions = self._extract_dimensions(message)
        if dimensions:
            slots.analysis_dimensions = dimensions
        
        # 檢查是否需要競爭對手比較
        if "競爭" in message or "對手" in message or "百佳" in message or "惠康" in message or "比較" in message:
            slots.include_competitors = True
        
        return slots
    
    def _extract_products(self, message: str, entities: List[str] = None) -> List[str]:
        """提取產品名稱"""
        products = []
        message_lower = message.lower()
        
        # 先從 entities 中提取
        if entities:
            for entity in entities:
                normalized = normalize_product_name(entity)
                if normalized not in products:
                    products.append(normalized)
        
        # 從知識庫中匹配
        for product_name, data in self.taxonomy.items():
            if product_name.lower() in message_lower:
                if product_name not in products:
                    products.append(product_name)
                continue
            
            # 檢查別名
            for alias in data.get("aliases", []):
                if alias.lower() in message_lower:
                    if product_name not in products:
                        products.append(product_name)
                    break
        
        return products
    
    def _extract_time_range(self, message: str) -> Optional[str]:
        """提取時間範圍"""
        message_lower = message.lower()

        # 檢查具體時間詞 (順序很重要，更具體的先匹配)
        time_patterns = {
            "today": ["今日", "今天", "當日", "當天"],
            "this_week": ["本週", "本周", "呢個星期", "這週", "這周"],
            "this_month": ["本月", "呢個月", "這個月"],
            "last_month": ["上個月", "上月"],
            "7d": ["7日", "七日", "一週", "一周", "7天", "七天"],
            "30d": ["30日", "三十日", "一個月", "30天"],
            "90d": ["90日", "三個月", "季度", "90天"],
            "1y": ["一年", "12個月", "全年"],
            "all": ["全部", "所有時間", "歷史"],
        }

        for time_code, patterns in time_patterns.items():
            for pattern in patterns:
                if pattern in message_lower:
                    return time_code

        return None
    
    def _extract_product_detail(self, message: str, product: str) -> Optional[ProductDetail]:
        """提取產品細節"""
        detail = ProductDetail()
        message_lower = message.lower()
        
        taxonomy = self.taxonomy.get(product, {})
        
        # 提取部位
        for part in taxonomy.get("parts", []):
            if part.lower() in message_lower:
                detail.parts.append(part)
        
        # 提取類型
        for type_ in taxonomy.get("types", []):
            if type_.lower() in message_lower:
                detail.types.append(type_)
        
        # 提取產地
        for origin in taxonomy.get("origins", []):
            if origin.lower() in message_lower:
                detail.origin.append(origin)
        
        # 提取品牌
        for brand in taxonomy.get("brands", []):
            if brand.lower() in message_lower:
                detail.brands.append(brand)
        
        # 提取等級
        for grade in taxonomy.get("grades", []):
            if grade.lower() in message_lower:
                detail.grades.append(grade)
        
        # 檢查是否有任何細節
        if any([detail.parts, detail.types, detail.origin, detail.brands, detail.grades]):
            return detail
        
        return None
    
    def _extract_dimensions(self, message: str) -> List[str]:
        """提取分析維度"""
        dimensions = []
        message_lower = message.lower()
        
        dimension_keywords = {
            "price_overview": ["價格", "幾錢", "幾多錢"],
            "price_trend": ["趨勢", "變化", "走勢"],
            "competitor_compare": ["競爭", "對手", "比較", "比較"],
            "brand_analysis": ["品牌", "牌子"],
            "top_products": ["熱門", "最受歡迎", "最好賣"],
            "stock_status": ["庫存", "有貨", "缺貨"],
        }
        
        for dim, keywords in dimension_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
                    if dim not in dimensions:
                        dimensions.append(dim)
                    break
        
        return dimensions if dimensions else None
    
    def check_completeness(self, slots: AnalysisSlots) -> SlotCompleteness:
        """
        檢查槽位完整性
        
        Args:
            slots: 當前槽位
        
        Returns:
            完整性檢查結果
        """
        missing = []
        ambiguous = []
        clarifications = []
        
        # 檢查必填：產品
        if not slots.products:
            missing.append("products")
            clarifications.append({
                "slot_name": "products",
                "question": "你想分析邊啲產品？",
                "question_type": "text",
                "options": []
            })
        
        # 檢查產品細節是否需要澄清
        for product in slots.products:
            taxonomy = self.taxonomy.get(product, {})
            questions = taxonomy.get("clarification_questions", [])
            
            # 檢查是否已有細節
            detail = slots.product_details.get(product)
            
            for q in questions:
                slot = q.get("slot")
                
                # 檢查該細節是否已填充
                if detail:
                    if slot == "parts" and detail.parts:
                        continue
                    if slot == "types" and detail.types:
                        continue
                    if slot == "origin" and detail.origin:
                        continue
                
                # 需要澄清
                clarifications.append({
                    "slot_name": f"{product}.{slot}",
                    "question": q.get("question"),
                    "question_type": "single",
                    "options": q.get("options", [])
                })
        
        # 計算信心度
        confidence = 1.0
        if missing:
            confidence -= 0.4
        if clarifications:
            confidence -= 0.1 * min(len(clarifications), 3)
        
        is_complete = not missing and len(clarifications) == 0
        
        return SlotCompleteness(
            is_complete=is_complete,
            missing_slots=missing,
            ambiguous_slots=ambiguous,
            clarification_needed=clarifications,
            confidence=max(0, confidence)
        )
    
    def merge_slots(self, existing: AnalysisSlots, new: AnalysisSlots) -> AnalysisSlots:
        """
        合併槽位
        
        Args:
            existing: 現有槽位
            new: 新提取的槽位
        
        Returns:
            合併後的槽位
        """
        # 合併產品（去重）
        products = list(set(existing.products + new.products))
        
        # 合併產品細節
        details = existing.product_details.copy()
        for product, detail in new.product_details.items():
            if product in details:
                # 合併細節
                existing_detail = details[product]
                existing_detail.parts = list(set(existing_detail.parts + detail.parts))
                existing_detail.types = list(set(existing_detail.types + detail.types))
                existing_detail.origin = list(set(existing_detail.origin + detail.origin))
                existing_detail.brands = list(set(existing_detail.brands + detail.brands))
            else:
                details[product] = detail
        
        # 使用新的時間範圍（如果有）
        time_range = new.time_range if new.time_range != "30d" else existing.time_range
        
        # 合併分析維度
        dimensions = list(set(existing.analysis_dimensions + new.analysis_dimensions))
        
        return AnalysisSlots(
            products=products,
            product_details=details,
            time_range=time_range,
            analysis_dimensions=dimensions,
            include_competitors=existing.include_competitors or new.include_competitors,
            competitor_ids=list(set(existing.competitor_ids + new.competitor_ids)),
            output_format=new.output_format or existing.output_format,
        )
    
    def update_slot(self, slots: AnalysisSlots, slot_name: str, value: Any) -> AnalysisSlots:
        """
        更新特定槽位
        
        Args:
            slots: 當前槽位
            slot_name: 槽位名稱（支持嵌套，如 "和牛.parts"）
            value: 新值
        
        Returns:
            更新後的槽位
        """
        if "." in slot_name:
            # 嵌套槽位（產品細節）
            product, field = slot_name.split(".", 1)
            
            if product not in slots.product_details:
                slots.product_details[product] = ProductDetail()
            
            detail = slots.product_details[product]
            
            if field == "parts":
                detail.parts = value if isinstance(value, list) else [value]
            elif field == "types":
                detail.types = value if isinstance(value, list) else [value]
            elif field == "origin":
                detail.origin = value if isinstance(value, list) else [value]
        else:
            # 頂層槽位
            if slot_name == "products":
                slots.products = value if isinstance(value, list) else [value]
            elif slot_name == "time_range":
                slots.time_range = value
            elif slot_name == "analysis_dimensions":
                slots.analysis_dimensions = value if isinstance(value, list) else [value]
        
        return slots
    
    def generate_clarification_message(self, questions: List[Dict]) -> Dict[str, Any]:
        """
        生成澄清問題訊息

        Args:
            questions: 澄清問題列表

        Returns:
            格式化的訊息
        """
        if not questions:
            return {"message": "", "options": []}

        message_parts = ["好！想再確認幾樣嘢：\n"]
        formatted_options = []

        for i, q in enumerate(questions, 1):
            message_parts.append(f"\n{i}. {q['question']}")

            formatted_options.append({
                "slot_name": q["slot_name"],
                "label": q["question"],
                "type": q.get("question_type", "single"),
                "options": q.get("options", [])
            })

        return {
            "message": "".join(message_parts),
            "options": formatted_options
        }

    # =============================================
    # 排程槽位提取
    # =============================================

    def extract_schedule_slots(self, message: str, entities: List[str] = None) -> ScheduleSlots:
        """
        從用戶訊息中提取排程槽位

        Args:
            message: 用戶訊息
            entities: 已識別的實體

        Returns:
            提取的排程槽位
        """
        slots = ScheduleSlots()
        message_lower = message.lower()

        # 提取頻率
        slots.frequency = self._extract_frequency(message_lower)

        # 提取時間
        slots.schedule_time = self._extract_schedule_time(message_lower)

        # 提取執行日
        slots.schedule_day = self._extract_schedule_day(message_lower, slots.frequency)

        # 提取報告類型
        slots.report_type = self._extract_report_type(message_lower)

        # 提取產品
        slots.products = self._extract_products(message, entities)

        # 提取交付渠道
        slots.delivery_channel = self._extract_delivery_channel(message_lower)

        # 自動生成名稱
        if slots.products and slots.frequency:
            slots.name = self._generate_schedule_name(slots)

        return slots

    def _extract_frequency(self, message: str) -> Optional[str]:
        """提取排程頻率"""
        frequency_patterns = {
            "daily": ["每日", "每天", "daily", "每朝", "每晚"],
            "weekly": ["每週", "每周", "weekly", "每星期", "每禮拜"],
            "monthly": ["每月", "每個月", "monthly"],
        }

        for freq, patterns in frequency_patterns.items():
            for pattern in patterns:
                if pattern in message:
                    return freq

        return None

    def _extract_schedule_time(self, message: str) -> Optional[str]:
        """提取執行時間"""
        import re

        # 嘗試匹配 HH:MM 格式
        time_match = re.search(r'(\d{1,2})[:\s點](\d{2})?', message)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return f"{hour:02d}:{minute:02d}"

        # 時間詞彙映射
        time_words = {
            "早上": "09:00",
            "朝早": "09:00",
            "上午": "10:00",
            "中午": "12:00",
            "下午": "14:00",
            "傍晚": "18:00",
            "晚上": "20:00",
        }

        for word, time in time_words.items():
            if word in message:
                return time

        return None

    def _extract_schedule_day(self, message: str, frequency: str = None) -> Optional[int]:
        """提取執行日期"""
        import re

        if frequency == "weekly":
            # 週幾
            weekday_patterns = {
                1: ["週一", "周一", "星期一", "禮拜一", "monday"],
                2: ["週二", "周二", "星期二", "禮拜二", "tuesday"],
                3: ["週三", "周三", "星期三", "禮拜三", "wednesday"],
                4: ["週四", "周四", "星期四", "禮拜四", "thursday"],
                5: ["週五", "周五", "星期五", "禮拜五", "friday"],
                6: ["週六", "周六", "星期六", "禮拜六", "saturday"],
                7: ["週日", "周日", "星期日", "禮拜日", "sunday"],
            }

            for day, patterns in weekday_patterns.items():
                for pattern in patterns:
                    if pattern in message:
                        return day

        elif frequency == "monthly":
            # 月幾號
            day_match = re.search(r'(\d{1,2})[號日]', message)
            if day_match:
                day = int(day_match.group(1))
                if 1 <= day <= 31:
                    return day

        return None

    def _extract_report_type(self, message: str) -> Optional[str]:
        """提取報告類型"""
        report_patterns = {
            "price_analysis": ["價格分析", "價格報告", "price analysis", "價錢"],
            "competitor_report": ["競品分析", "競品報告", "競爭對手", "competitor"],
            "sales_summary": ["銷售報告", "銷售摘要", "營收報告", "sales"],
            "inventory_alert": ["庫存報告", "庫存警報", "inventory"],
        }

        for report_type, patterns in report_patterns.items():
            for pattern in patterns:
                if pattern in message:
                    return report_type

        return "price_analysis"  # 默認價格分析

    def _extract_delivery_channel(self, message: str) -> Optional[str]:
        """提取交付渠道"""
        if any(word in message for word in ["telegram", "tg", "電報"]):
            return "telegram"
        if any(word in message for word in ["email", "郵件", "電郵"]):
            return "email"
        return "telegram"  # 默認 Telegram

    def _generate_schedule_name(self, slots: ScheduleSlots) -> str:
        """自動生成排程名稱"""
        freq_names = {
            "daily": "每日",
            "weekly": "每週",
            "monthly": "每月",
        }

        freq_name = freq_names.get(slots.frequency, "定時")
        products_str = "、".join(slots.products[:2])
        if len(slots.products) > 2:
            products_str += f" 等 {len(slots.products)} 個產品"

        return f"{freq_name}{products_str}報告"

    def check_schedule_completeness(self, slots: ScheduleSlots) -> SlotCompleteness:
        """
        檢查排程槽位完整性

        Args:
            slots: 當前排程槽位

        Returns:
            完整性檢查結果
        """
        missing = []
        clarifications = []

        # 檢查頻率
        if not slots.frequency:
            missing.append("frequency")
            clarifications.append({
                "slot_name": "frequency",
                "question": "你想幾耐收到報告？",
                "question_type": "single",
                "options": [
                    {"label": "每日", "value": "daily"},
                    {"label": "每週", "value": "weekly"},
                    {"label": "每月", "value": "monthly"},
                ]
            })

        # 檢查時間
        if not slots.schedule_time:
            missing.append("schedule_time")
            clarifications.append({
                "slot_name": "schedule_time",
                "question": "想幾點鐘收到報告？",
                "question_type": "single",
                "options": [
                    {"label": "早上 9 點", "value": "09:00"},
                    {"label": "中午 12 點", "value": "12:00"},
                    {"label": "下午 6 點", "value": "18:00"},
                ]
            })

        # 檢查產品
        if not slots.products:
            missing.append("products")
            clarifications.append({
                "slot_name": "products",
                "question": "你想分析邊啲產品？",
                "question_type": "text",
                "options": []
            })

        confidence = 1.0 - (len(missing) * 0.3)
        is_complete = len(missing) == 0

        return SlotCompleteness(
            is_complete=is_complete,
            missing_slots=missing,
            ambiguous_slots=[],
            clarification_needed=clarifications,
            confidence=max(0, confidence)
        )
