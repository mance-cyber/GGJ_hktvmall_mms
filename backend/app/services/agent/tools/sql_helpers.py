# =============================================
# SQL 安全輔助函數
# =============================================
# 防止 SQL 注入攻擊

import re
from typing import List, Dict, Any, Tuple


def escape_like_pattern(value: str) -> str:
    """
    轉義 LIKE 模式中的特殊字符

    Args:
        value: 用戶輸入的搜索值

    Returns:
        安全的 LIKE 模式字符串
    """
    if not value:
        return ""

    # 轉義 LIKE 特殊字符: % _ \
    escaped = value.replace("\\", "\\\\")
    escaped = escaped.replace("%", "\\%")
    escaped = escaped.replace("_", "\\_")

    # 移除可能的 SQL 注入字符
    # 移除單引號、雙引號、分號、註釋符號等
    escaped = re.sub(r"['\";\\-]+", "", escaped)

    return escaped


def escape_identifier(value: str) -> str:
    """
    轉義 SQL 標識符（如列名、別名）

    Args:
        value: 標識符

    Returns:
        安全的標識符
    """
    if not value:
        return "unknown"

    # 只允許字母、數字、下劃線、中文字符
    # 移除其他所有字符
    cleaned = re.sub(r"[^a-zA-Z0-9_\u4e00-\u9fff]", "", value)

    return cleaned[:50] if cleaned else "unknown"  # 限制長度


def validate_integer(value: Any, default: int = 0, min_val: int = None, max_val: int = None) -> int:
    """
    驗證並返回安全的整數值

    Args:
        value: 輸入值
        default: 默認值
        min_val: 最小值
        max_val: 最大值

    Returns:
        安全的整數
    """
    try:
        result = int(value)
        if min_val is not None:
            result = max(result, min_val)
        if max_val is not None:
            result = min(result, max_val)
        return result
    except (TypeError, ValueError):
        return default


def validate_float(value: Any, default: float = 0.0) -> float:
    """
    驗證並返回安全的浮點數值

    Args:
        value: 輸入值
        default: 默認值

    Returns:
        安全的浮點數
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def validate_sort_column(value: str, allowed: List[str], default: str = None) -> str:
    """
    驗證排序列名（白名單驗證）

    Args:
        value: 用戶輸入的列名
        allowed: 允許的列名列表
        default: 默認列名

    Returns:
        安全的列名
    """
    if value in allowed:
        return value
    return default or (allowed[0] if allowed else "id")


def validate_group_by(value: str, allowed: List[str] = None) -> str:
    """
    驗證 GROUP BY 值（白名單驗證）

    Args:
        value: 用戶輸入
        allowed: 允許的值列表

    Returns:
        安全的 GROUP BY 值
    """
    if allowed is None:
        allowed = ["day", "week", "month"]

    return value if value in allowed else "week"


def build_safe_like_condition(
    column: str,
    value: str,
    table_alias: str = None
) -> Tuple[str, Dict[str, str]]:
    """
    構建安全的 LIKE 條件

    Args:
        column: 列名
        value: 搜索值
        table_alias: 表別名

    Returns:
        (SQL 條件, 參數字典) 元組
    """
    safe_value = escape_like_pattern(value)
    safe_column = escape_identifier(column)

    col_ref = f"{table_alias}.{safe_column}" if table_alias else safe_column
    param_name = f"like_{safe_column}_{abs(hash(value)) % 10000}"

    return f"{col_ref} ILIKE :{param_name}", {param_name: f"%{safe_value}%"}


def build_safe_in_list(values: List[str]) -> Tuple[str, Dict[str, str]]:
    """
    構建安全的 IN 列表

    Args:
        values: 值列表

    Returns:
        (佔位符字符串, 參數字典) 元組
    """
    params = {}
    placeholders = []

    for i, val in enumerate(values):
        param_name = f"in_val_{i}"
        safe_val = escape_identifier(val)
        params[param_name] = safe_val
        placeholders.append(f":{param_name}")

    return ", ".join(placeholders), params


def build_product_search_conditions(
    products: List[str],
    column: str = "name",
    table_alias: str = None
) -> Tuple[str, Dict[str, Any]]:
    """
    構建產品搜索條件（安全版本）

    Args:
        products: 產品名稱列表
        column: 搜索列名
        table_alias: 表別名

    Returns:
        (WHERE 條件, 參數字典) 元組
    """
    conditions = []
    all_params = {}

    col_ref = f"{table_alias}.{column}" if table_alias else column

    for i, product in enumerate(products):
        safe_product = escape_like_pattern(product)
        param_name = f"product_{i}"
        conditions.append(f"{col_ref} ILIKE :{param_name}")
        all_params[param_name] = f"%{safe_product}%"

    where_clause = " OR ".join(f"({c})" for c in conditions) if conditions else "1=1"
    return where_clause, all_params


def build_product_case_statement(
    products: List[str],
    column: str = "name",
    table_alias: str = None
) -> Tuple[str, Dict[str, Any]]:
    """
    構建產品分類 CASE 語句（安全版本）

    由於 PostgreSQL 的 CASE WHEN 不支持參數綁定在 LIKE 中，
    我們需要在 Python 層面驗證和清理輸入

    Args:
        products: 產品名稱列表
        column: 搜索列名
        table_alias: 表別名

    Returns:
        (CASE 語句, 空參數字典) 元組
    """
    cases = []
    col_ref = f"{table_alias}.{column}" if table_alias else column

    for product in products:
        # 嚴格清理：只保留安全字符
        safe_product = escape_like_pattern(product)
        safe_label = escape_identifier(product)

        if safe_product and safe_label:
            # 使用清理後的值構建 CASE
            cases.append(f"WHEN {col_ref} ILIKE '%{safe_product}%' THEN '{safe_label}'")

    if cases:
        return f"CASE {' '.join(cases)} ELSE '其他' END", {}

    return "'未分類'", {}


def build_interval_days(days: int) -> str:
    """
    構建安全的 INTERVAL 表達式

    Args:
        days: 天數

    Returns:
        安全的天數字符串
    """
    safe_days = validate_integer(days, default=30, min_val=1, max_val=3650)
    return str(safe_days)
