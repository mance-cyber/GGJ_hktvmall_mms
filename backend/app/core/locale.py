# =============================================
# Locale 依賴注入
# =============================================
#
# 從請求中提取用戶語言偏好。
# 優先級：query param > Accept-Language header > 預設值
# =============================================

from typing import Literal, Optional
from fastapi import Query, Request

Locale = Literal["zh-HK", "en", "ja"]

DEFAULT_LOCALE: Locale = "zh-HK"

# Accept-Language 標頭中的語言標籤 → 內部 locale 映射
_LANG_TAG_MAP: dict[str, Locale] = {
    "zh": "zh-HK",
    "zh-hk": "zh-HK",
    "zh-tw": "zh-HK",
    "zh-hant": "zh-HK",
    "en": "en",
    "en-us": "en",
    "en-gb": "en",
    "ja": "ja",
}


def _parse_accept_language(header: str) -> Optional[Locale]:
    """
    解析 Accept-Language 標頭，返回最佳匹配的 locale。

    僅取最高優先級的語言標籤（忽略 q 值排序，
    因為前端發送的標頭通常只有一個值）。
    """
    for part in header.split(","):
        tag = part.split(";")[0].strip().lower()
        if tag in _LANG_TAG_MAP:
            return _LANG_TAG_MAP[tag]
    return None


def get_locale(
    request: Request,
    locale: Optional[str] = Query(
        default=None,
        alias="locale",
        description="語言偏好：zh-HK, en, ja",
        pattern="^(zh-HK|en|ja)$",
    ),
) -> Locale:
    """
    FastAPI 依賴：從請求提取 locale。

    用法：
        @router.get("/items")
        async def list_items(locale: Locale = Depends(get_locale)):
            ...
    """
    # 1. Query parameter 最優先
    if locale:
        return locale  # type: ignore[return-value]

    # 2. Accept-Language 標頭
    accept_lang = request.headers.get("Accept-Language", "")
    if accept_lang:
        parsed = _parse_accept_language(accept_lang)
        if parsed:
            return parsed

    # 3. 預設值
    return DEFAULT_LOCALE
