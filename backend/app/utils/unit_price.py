# =============================================
# 單位價格計算工具
# =============================================
# 從商品名稱/描述中提取重量/容量，計算每 100g/100ml 單位價格

import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class UnitInfo:
    """單位信息"""
    value: Decimal          # 數值（如 500）
    unit: str               # 單位（如 g, ml, kg）
    normalized_value: Decimal  # 標準化為 g 或 ml
    unit_type: str          # per_100g 或 per_100ml


class UnitPriceCalculator:
    """單位價格計算器"""

    # 重量單位轉換（轉為克）
    WEIGHT_UNITS = {
        'kg': Decimal('1000'),
        '公斤': Decimal('1000'),
        'g': Decimal('1'),
        '克': Decimal('1'),
        'gm': Decimal('1'),
        'gram': Decimal('1'),
        'grams': Decimal('1'),
        'mg': Decimal('0.001'),
        '毫克': Decimal('0.001'),
        'oz': Decimal('28.3495'),
        'lb': Decimal('453.592'),
        '磅': Decimal('453.592'),
    }

    # 容量單位轉換（轉為毫升）
    VOLUME_UNITS = {
        'l': Decimal('1000'),
        'L': Decimal('1000'),
        '升': Decimal('1000'),
        '公升': Decimal('1000'),
        'ml': Decimal('1'),
        'ML': Decimal('1'),
        '毫升': Decimal('1'),
        'cc': Decimal('1'),
        'fl oz': Decimal('29.5735'),
    }

    # 數量單位（用於計算每件價格）
    COUNT_UNITS = {
        '件': 1,
        '個': 1,
        '包': 1,
        '盒': 1,
        '片': 1,
        '粒': 1,
        '顆': 1,
        '入': 1,
        'pcs': 1,
        'pc': 1,
        'pack': 1,
        'packs': 1,
    }

    @classmethod
    def extract_quantity(cls, text: str) -> Optional[UnitInfo]:
        """
        從文本中提取數量和單位

        支持格式：
        - 500g, 500 g, 500克
        - 1.5kg, 1.5 kg, 1.5公斤
        - 250ml, 250 ml, 250毫升
        - 2L, 2 L, 2升
        - 500g x 2, 500g*2（多件裝）
        """
        if not text:
            return None

        # 先處理多件裝格式：500g x 2 或 500g*2
        multi_patterns = [
            r'(\d+(?:\.\d+)?)\s*(g|kg|ml|l|克|公斤|毫升|升)\s*[x×*]\s*(\d+)',
            r'(\d+(?:\.\d+)?)\s*(g|kg|ml|l|克|公斤|毫升|升)\s*[（(](\d+)[入件個包片)）]',
        ]

        for pattern in multi_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = Decimal(match.group(1))
                unit = match.group(2).lower()
                count = int(match.group(3))
                total_value = value * count
                return cls._create_unit_info(total_value, unit)

        # 標準單個單位格式
        # 先嘗試匹配帶小數的數字
        patterns = [
            r'(\d+(?:\.\d+)?)\s*(kg|g|gm|mg|公斤|克|毫克)',  # 重量
            r'(\d+(?:\.\d+)?)\s*(l|ml|L|ML|cc|升|公升|毫升)',  # 容量
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = Decimal(match.group(1))
                unit = match.group(2).lower()
                return cls._create_unit_info(value, unit)

        return None

    @classmethod
    def _create_unit_info(cls, value: Decimal, unit: str) -> Optional[UnitInfo]:
        """創建標準化的單位信息"""
        unit_lower = unit.lower()

        # 檢查是否為重量單位
        if unit_lower in cls.WEIGHT_UNITS:
            multiplier = cls.WEIGHT_UNITS[unit_lower]
            normalized = value * multiplier
            return UnitInfo(
                value=value,
                unit=unit,
                normalized_value=normalized,
                unit_type='per_100g'
            )

        # 檢查是否為容量單位
        if unit_lower in cls.VOLUME_UNITS:
            multiplier = cls.VOLUME_UNITS[unit_lower]
            normalized = value * multiplier
            return UnitInfo(
                value=value,
                unit=unit,
                normalized_value=normalized,
                unit_type='per_100ml'
            )

        return None

    @classmethod
    def calculate_unit_price(
        cls,
        price: Decimal,
        text: str,
        per_unit: int = 100
    ) -> Tuple[Optional[Decimal], Optional[str]]:
        """
        計算單位價格

        Args:
            price: 商品總價
            text: 商品名稱或描述（用於提取數量）
            per_unit: 每多少單位的價格（預設 100，即每 100g 或 100ml）

        Returns:
            (unit_price, unit_type) 或 (None, None)
        """
        if not price or price <= 0:
            return None, None

        unit_info = cls.extract_quantity(text)
        if not unit_info:
            return None, None

        if unit_info.normalized_value <= 0:
            return None, None

        # 計算每 per_unit 單位的價格
        unit_price = (price * per_unit / unit_info.normalized_value).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        return unit_price, unit_info.unit_type

    @classmethod
    def format_unit_price(cls, unit_price: Decimal, unit_type: str) -> str:
        """格式化單位價格顯示"""
        if unit_type == 'per_100g':
            return f"HK${unit_price}/100g"
        elif unit_type == 'per_100ml':
            return f"HK${unit_price}/100ml"
        else:
            return f"HK${unit_price}"


# =============================================
# 便捷函數
# =============================================

def calculate_unit_price(price: Decimal, product_name: str) -> Tuple[Optional[Decimal], Optional[str]]:
    """計算單位價格的便捷函數"""
    return UnitPriceCalculator.calculate_unit_price(price, product_name)


def extract_quantity(text: str) -> Optional[UnitInfo]:
    """提取數量的便捷函數"""
    return UnitPriceCalculator.extract_quantity(text)
