# =============================================
# 混合標籤引擎（規則 + AI 兜底）
# 為競品商品和自家商品打分類標籤
# =============================================

import re
import json
import logging
from typing import Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.competitor import CompetitorProduct
from app.models.product import Product
from app.config import get_settings

logger = logging.getLogger(__name__)


# =============================================
# 標籤體系定義
# =============================================

# 匹配順序：具體品類優先（貝/蟹/蝦 在 魚 前面，避免「鮑魚」被「魚」搶走）
_CATEGORY_ORDER = ["貝", "蟹", "蝦", "牛", "豬", "羊", "雞鴨", "魚"]

TAG_RULES: dict[str, dict] = {
    "牛": {
        "keywords": ["牛", "beef", "wagyu", "和牛", "安格斯", "angus"],
        "sub_tags": {
            "西冷": ["西冷", "sirloin", "striploin", "strip loin"],
            "肉眼": ["肉眼", "ribeye", "rib eye", "rib-eye"],
            "牛柳": ["牛柳", "tenderloin", "filet", "fillet"],
            "牛仔骨": ["牛仔骨", "short rib", "shortrib"],
            "牛肋": ["牛肋", "牛小排", "rib"],
            "和牛片": ["和牛片", "火鍋片", "shabu"],
            "漢堡扒": ["漢堡", "burger", "hamburg", "patty", "patties"],
        },
    },
    "豬": {
        "keywords": ["豬", "pork", "黑豚"],
        "sub_tags": {
            "豬扒": ["豬扒", "pork chop", "豬排"],
            "豬腩": ["豬腩", "belly", "五花"],
            "排骨": ["排骨", "spare rib", "sparerib", "肋排"],
            "豬柳": ["豬柳", "pork loin", "里脊"],
        },
    },
    "羊": {
        "keywords": ["羊", "lamb", "mutton"],
        "sub_tags": {
            "羊架": ["羊架", "rack", "lamb rack"],
            "羊腿": ["羊腿", "leg", "lamb leg"],
        },
    },
    "雞鴨": {
        "keywords": ["雞", "鴨", "chicken", "duck", "poultry"],
        "sub_tags": {
            "雞全隻": ["全雞", "whole chicken", "光雞", "春雞"],
            "雞翼": ["雞翼", "chicken wing", "wing"],
            "雞胸": ["雞胸", "chicken breast", "breast"],
            "雞腿": ["雞腿", "chicken leg", "leg quarter", "drumstick"],
            "鴨": ["鴨", "duck"],
        },
    },
    "魚": {
        "keywords": ["魚", "fish", "salmon", "三文", "鯛", "鰻", "tuna", "吞拿"],
        "sub_tags": {
            "三文魚": ["三文魚", "salmon", "鮭"],
            "鯛魚": ["鯛", "snapper", "sea bream", "tai"],
            "鰻魚": ["鰻", "eel", "unagi"],
            "吞拿魚": ["吞拿", "tuna", "鮪"],
            "魚柳": ["魚柳", "fish fillet", "fillet"],
        },
    },
    "蝦": {
        "keywords": ["蝦", "shrimp", "prawn"],
        "sub_tags": {
            "蝦": ["蝦", "shrimp", "prawn"],
        },
    },
    "蟹": {
        "keywords": ["蟹", "crab"],
        "sub_tags": {
            "蟹": ["蟹", "crab"],
            "蟹肉": ["蟹肉", "crab meat", "蟹棒"],
        },
    },
    "貝": {
        "keywords": ["帶子", "鮑魚", "蠔", "scallop", "abalone", "oyster", "clam", "mussel"],
        "sub_tags": {
            "帶子": ["帶子", "scallop"],
            "鮑魚": ["鮑魚", "abalone"],
            "蠔": ["蠔", "oyster"],
        },
    },
}

# 排除關鍵詞：匹配到這些詞的商品不是生鮮肉類/海鮮
EXCLUDE_KEYWORDS = [
    "味", "醬", "乾", "餅", "粉", "麵", "湯", "罐",
    "調味", "即食", "零食", "狗", "貓", "寵物",
    "curry", "sauce", "dried", "instant", "pet",
    "蝦片", "蝦餅", "蝦醬",
    "牛肉味", "牛肉醬", "牛肉乾",
    "雞粉", "雞精",
]

# 所有合法的大類標籤
VALID_CATEGORIES = set(TAG_RULES.keys()) | {"其他"}

# 所有合法的細分標籤（按大類索引）
VALID_SUB_TAGS: dict[str, set[str]] = {
    cat: set(data["sub_tags"].keys()) | {"其他"}
    for cat, data in TAG_RULES.items()
}


# =============================================
# 規則引擎
# =============================================

def tag_by_rules(product_name: str) -> tuple[str, str] | None:
    """
    規則引擎打標，返回 (category_tag, sub_tag) 或 None

    純函數，不依賴 DB/IO。
    邏輯：排除詞檢查 → 大類匹配（按優先順序）→ 細分匹配（長詞優先）。
    """
    if not product_name:
        return None

    name_lower = product_name.lower()

    # 排除非生鮮商品
    for kw in EXCLUDE_KEYWORDS:
        if kw in name_lower:
            return None

    # 按 _CATEGORY_ORDER 匹配大類（具體品類優先）
    for category in _CATEGORY_ORDER:
        rule = TAG_RULES[category]
        if not _any_keyword_in(rule["keywords"], name_lower):
            continue

        # 匹配細分：找到所有命中的 sub_tag，取最長匹配關鍵詞的那個
        best_sub: str | None = None
        best_kw_len = 0
        for sub_tag, sub_keywords in rule["sub_tags"].items():
            for kw in sub_keywords:
                if kw.lower() in name_lower and len(kw) > best_kw_len:
                    best_sub = sub_tag
                    best_kw_len = len(kw)
        if best_sub:
            return (category, best_sub)

        # 大類命中但無細分匹配
        return (category, "其他")

    return None


def _any_keyword_in(keywords: list[str], text: str) -> bool:
    """檢查任一關鍵詞是否出現在文本中（大小寫不敏感，text 已 lower）"""
    return any(kw.lower() in text for kw in keywords)


# =============================================
# AI 兜底
# =============================================

# 合法標籤清單（供 prompt 使用）
_CATEGORY_LIST = "牛 / 豬 / 羊 / 雞鴨 / 魚 / 蝦 / 蟹 / 貝 / 其他"
_SUB_TAG_SPEC = """牛：西冷 / 肉眼 / 牛柳 / 牛仔骨 / 牛肋 / 和牛片 / 漢堡扒 / 其他
豬：豬扒 / 豬腩 / 排骨 / 豬柳 / 其他
羊：羊架 / 羊腿 / 其他
雞鴨：雞全隻 / 雞翼 / 雞胸 / 雞腿 / 鴨 / 其他
魚：三文魚 / 鯛魚 / 鰻魚 / 吞拿魚 / 魚柳 / 其他
蝦：蝦 / 其他
蟹：蟹 / 蟹肉 / 其他
貝：帶子 / 鮑魚 / 蠔 / 其他"""

_AI_TAG_PROMPT = """你是一位香港生鮮食材分類專家。請為以下商品名稱分類。

分類體系：
大類（category_tag）：{categories}

細分（sub_tag，按大類選擇）：
{sub_tags}

規則：
1. 只分類「生鮮肉類/海鮮」，加工食品（醬料、零食、乾貨、即食品）回傳 null
2. 如果商品不屬於任何大類，回傳 null
3. 如果屬於某大類但無法確定細分，sub_tag 填 "其他"

商品清單：
{product_list}

請以 JSON 數組回傳，每項格式：
{{"index": 1, "category_tag": "牛", "sub_tag": "西冷"}}
如果不是生鮮肉類/海鮮：
{{"index": 1, "category_tag": null, "sub_tag": null}}

只輸出 JSON 數組，不要其他內容。"""


async def tag_by_ai(
    product_names: list[str],
) -> list[tuple[str, str] | None]:
    """
    AI 批量打標（Claude Haiku）

    每次最多處理 20 個商品名。
    返回列表長度與 product_names 一致，對應位置為標籤或 None。
    """
    if not product_names:
        return []

    from app.connectors.claude import ClaudeConnector

    settings = get_settings()
    # 標籤任務用最輕量模型
    model = settings.ai_model_simple
    connector = ClaudeConnector(model=model)

    if not connector.client:
        logger.warning("AI 打標失敗：無可用的 Claude API 客戶端")
        return [None] * len(product_names)

    # 構建商品清單文本
    lines = [f"#{i+1} {name}" for i, name in enumerate(product_names)]
    product_list_text = "\n".join(lines)

    prompt = _AI_TAG_PROMPT.format(
        categories=_CATEGORY_LIST,
        sub_tags=_SUB_TAG_SPEC,
        product_list=product_list_text,
    )

    try:
        max_tokens = 4000 if "thinking" in model else 1500
        message = connector.client.messages.create(
            model=connector.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )

        # thinking 模型返回多個 block，取最後一個 text block
        response_text = ""
        for block in message.content:
            if getattr(block, "type", None) == "text":
                response_text = block.text
        if not response_text:
            response_text = message.content[0].text if message.content else "[]"

        # 解析 JSON 數組
        json_match = re.search(r'\[[\s\S]*\]', response_text)
        if not json_match:
            logger.warning(f"AI 打標返回格式異常: {response_text[:200]}")
            return [None] * len(product_names)

        results_array = json.loads(json_match.group())
        if not isinstance(results_array, list):
            logger.warning(f"AI 打標返回非數組: {type(results_array)}")
            return [None] * len(product_names)

        # 按 index 映射回結果
        output: list[tuple[str, str] | None] = [None] * len(product_names)
        for item in results_array:
            idx = item.get("index", 0) - 1  # 1-based → 0-based
            if not (0 <= idx < len(product_names)):
                continue
            cat = item.get("category_tag")
            sub = item.get("sub_tag")
            if cat and sub:
                output[idx] = (cat, sub)

        tagged_count = sum(1 for r in output if r is not None)
        logger.info(
            f"AI 打標完成: {tagged_count}/{len(product_names)} 個商品已標記"
        )
        return output

    except Exception as e:
        logger.error(f"AI 打標異常: {e}", exc_info=True)
        return [None] * len(product_names)


# =============================================
# 主服務：協調規則引擎 + AI 兜底 + DB 寫入
# =============================================

AI_BATCH_SIZE = 20


async def tag_products(
    db: AsyncSession,
    product_ids: list[str] | None = None,
) -> dict:
    """
    為指定商品打標（同時處理 competitor_products 和 products 兩張表）

    如果 product_ids 為 None，處理所有未打標商品。
    返回統計摘要。
    """
    stats = {"rule_tagged": 0, "ai_tagged": 0, "skipped": 0, "failed": 0}

    # 收集未打標的競品商品
    cp_query = select(CompetitorProduct).where(CompetitorProduct.is_active == True)
    if product_ids:
        cp_query = cp_query.where(CompetitorProduct.id.in_(product_ids))
    else:
        cp_query = cp_query.where(CompetitorProduct.category_tag.is_(None))
    result = await db.execute(cp_query)
    competitor_products = list(result.scalars().all())

    # 收集未打標的自家商品
    p_query = select(Product)
    if product_ids:
        p_query = p_query.where(Product.id.in_(product_ids))
    else:
        p_query = p_query.where(Product.category_tag.is_(None))
    result = await db.execute(p_query)
    own_products = list(result.scalars().all())

    # 統一處理：(object, name, table_type)
    items: list[tuple] = []
    for cp in competitor_products:
        items.append((cp, cp.name, "competitor"))
    for p in own_products:
        # 自家商品優先用 name_zh，回退到 name
        name = p.name_zh or p.name or ""
        items.append((p, name, "product"))

    if not items:
        logger.info("無未打標商品")
        return stats

    logger.info(f"開始打標: {len(items)} 個商品（競品 {len(competitor_products)}, 自家 {len(own_products)}）")

    # ==================== Step 1：規則引擎 ====================
    ai_pending: list[tuple] = []  # 規則引擎無法處理的

    for obj, name, table_type in items:
        result = tag_by_rules(name)
        if result:
            cat, sub = result
            obj.category_tag = cat
            obj.sub_tag = sub
            if hasattr(obj, "tag_source"):
                obj.tag_source = "rule"
            stats["rule_tagged"] += 1
        else:
            ai_pending.append((obj, name, table_type))

    logger.info(
        f"規則引擎: {stats['rule_tagged']} 已標記, "
        f"{len(ai_pending)} 待 AI 處理"
    )

    # ==================== Step 2：AI 兜底（批量） ====================
    for batch_start in range(0, len(ai_pending), AI_BATCH_SIZE):
        batch = ai_pending[batch_start : batch_start + AI_BATCH_SIZE]
        names = [name for _, name, _ in batch]

        ai_results = await tag_by_ai(names)

        for (obj, name, table_type), ai_result in zip(batch, ai_results):
            if ai_result:
                cat, sub = ai_result
                obj.category_tag = cat
                obj.sub_tag = sub
                if hasattr(obj, "tag_source"):
                    obj.tag_source = "ai"
                stats["ai_tagged"] += 1
            else:
                stats["skipped"] += 1

    # ==================== Step 3：持久化 ====================
    try:
        await db.flush()
        logger.info(
            f"打標完成: rule={stats['rule_tagged']}, "
            f"ai={stats['ai_tagged']}, skipped={stats['skipped']}"
        )
    except Exception as e:
        logger.error(f"打標持久化失敗: {e}", exc_info=True)
        stats["failed"] = stats["rule_tagged"] + stats["ai_tagged"]
        stats["rule_tagged"] = 0
        stats["ai_tagged"] = 0

    return stats


async def tag_all_untagged(db: AsyncSession) -> dict:
    """為所有未打標的商品打標（tag_products 的便捷入口）"""
    return await tag_products(db, product_ids=None)


async def retag_product(db: AsyncSession, product_name: str, obj) -> None:
    """
    重新打標單個商品（名稱變更時觸發）

    先嘗試規則引擎，失敗則 AI 兜底。
    直接修改 obj 的 category_tag / sub_tag / tag_source。
    """
    result = tag_by_rules(product_name)
    if result:
        obj.category_tag, obj.sub_tag = result
        if hasattr(obj, "tag_source"):
            obj.tag_source = "rule"
        return

    ai_results = await tag_by_ai([product_name])
    if ai_results and ai_results[0]:
        obj.category_tag, obj.sub_tag = ai_results[0]
        if hasattr(obj, "tag_source"):
            obj.tag_source = "ai"
    else:
        obj.category_tag = None
        obj.sub_tag = None
        if hasattr(obj, "tag_source"):
            obj.tag_source = None
