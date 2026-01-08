# =============================================
# 產品分類知識庫
# 用於意圖識別和槽位填充
# =============================================

from typing import Dict, List, Any

# 產品分類定義
PRODUCT_TAXONOMY: Dict[str, Dict[str, Any]] = {
    # =============================================
    # 肉類
    # =============================================
    "和牛": {
        "aliases": ["wagyu", "日本牛", "A5牛", "A4牛", "日本和牛"],
        "parts": ["西冷", "肉眼", "牛柳", "牛肋骨", "火鍋片", "燒肉片", "漢堡扒", "牛小排"],
        "grades": ["A5", "A4", "A3"],
        "origins": ["日本", "澳洲", "美國"],
        "brands": ["鹿兒島", "宮崎", "神戶", "松阪", "近江", "飛驒", "米澤"],
        "search_patterns": [
            "name ILIKE '%和牛%'",
            "name ILIKE '%wagyu%'",
            "name ILIKE '%A5%' AND name ILIKE '%牛%'",
        ],
        "clarification_questions": [
            {
                "slot": "parts",
                "question": "想分析邊個部位？",
                "options": [
                    {"value": "all", "label": "全部部位"},
                    {"value": "sirloin", "label": "西冷"},
                    {"value": "ribeye", "label": "肉眼"},
                    {"value": "tenderloin", "label": "牛柳"},
                    {"value": "hotpot", "label": "火鍋片/燒肉片"},
                ]
            },
            {
                "slot": "origin",
                "question": "要包埋邊個產地？",
                "options": [
                    {"value": "all", "label": "全部產地"},
                    {"value": "japan", "label": "日本"},
                    {"value": "australia", "label": "澳洲"},
                    {"value": "usa", "label": "美國"},
                ]
            }
        ]
    },
    
    # =============================================
    # 海鮮 - 魚類
    # =============================================
    "三文魚": {
        "aliases": ["salmon", "鮭魚", "三文鱼"],
        "types": ["刺身", "三文魚腩", "三文魚頭", "三文魚柳", "煙燻三文魚", "三文魚子", "三文魚扒"],
        "origins": ["挪威", "智利", "蘇格蘭", "日本", "加拿大", "法羅群島"],
        "search_patterns": [
            "name ILIKE '%三文魚%'",
            "name ILIKE '%salmon%'",
            "name ILIKE '%鮭魚%'",
        ],
        "clarification_questions": [
            {
                "slot": "types",
                "question": "想睇邊類三文魚？",
                "options": [
                    {"value": "all", "label": "全部類型"},
                    {"value": "sashimi", "label": "刺身"},
                    {"value": "belly", "label": "三文魚腩"},
                    {"value": "head", "label": "三文魚頭"},
                    {"value": "fillet", "label": "三文魚柳"},
                    {"value": "smoked", "label": "煙燻三文魚"},
                ]
            }
        ]
    },
    
    "吞拿魚": {
        "aliases": ["tuna", "金槍魚", "鮪魚", "吞拿"],
        "types": ["刺身", "吞拿魚腩", "赤身", "中拖羅", "大拖羅", "罐頭"],
        "origins": ["日本", "西班牙", "地中海"],
        "search_patterns": [
            "name ILIKE '%吞拿%'",
            "name ILIKE '%tuna%'",
            "name ILIKE '%金槍%'",
            "name ILIKE '%鮪魚%'",
        ],
        "clarification_questions": [
            {
                "slot": "types",
                "question": "想睇邊種吞拿魚？",
                "options": [
                    {"value": "all", "label": "全部"},
                    {"value": "sashimi", "label": "刺身"},
                    {"value": "otoro", "label": "大拖羅"},
                    {"value": "chutoro", "label": "中拖羅"},
                    {"value": "akami", "label": "赤身"},
                ]
            }
        ]
    },
    
    # =============================================
    # 海鮮 - 貝類/甲殼類
    # =============================================
    "海膽": {
        "aliases": ["uni", "海胆", "雲丹"],
        "types": ["馬糞海膽", "紫海膽", "赤海膽", "海膽醬", "海膽刺身"],
        "origins": ["北海道", "青森", "利尻", "加拿大", "俄羅斯"],
        "grades": ["特選", "A級", "B級"],
        "search_patterns": [
            "name ILIKE '%海膽%'",
            "name ILIKE '%海胆%'",
            "name ILIKE '%uni%'",
        ],
        "clarification_questions": [
            {
                "slot": "types",
                "question": "想分析邊種海膽？",
                "options": [
                    {"value": "all", "label": "全部"},
                    {"value": "bafun", "label": "馬糞海膽"},
                    {"value": "murasaki", "label": "紫海膽"},
                    {"value": "sauce", "label": "海膽醬"},
                ]
            }
        ]
    },
    
    "蟹": {
        "aliases": ["crab", "蟹類"],
        "types": ["帝王蟹", "松葉蟹", "毛蟹", "花蟹", "蟹腳", "蟹肉", "蟹膏"],
        "origins": ["北海道", "鳥取", "俄羅斯", "阿拉斯加"],
        "search_patterns": [
            "name ILIKE '%蟹%'",
            "name ILIKE '%crab%'",
        ],
        "clarification_questions": [
            {
                "slot": "types",
                "question": "想睇邊種蟹？",
                "options": [
                    {"value": "all", "label": "全部"},
                    {"value": "king", "label": "帝王蟹"},
                    {"value": "snow", "label": "松葉蟹"},
                    {"value": "hairy", "label": "毛蟹"},
                    {"value": "leg", "label": "蟹腳"},
                ]
            }
        ]
    },
    
    "帶子": {
        "aliases": ["scallop", "扇貝", "干貝"],
        "types": ["刺身帶子", "急凍帶子", "乾瑤柱", "帶子刺身"],
        "origins": ["北海道", "青森", "日本"],
        "search_patterns": [
            "name ILIKE '%帶子%'",
            "name ILIKE '%scallop%'",
            "name ILIKE '%扇貝%'",
            "name ILIKE '%干貝%'",
            "name ILIKE '%瑤柱%'",
        ],
        "clarification_questions": []
    },
    
    "蝦": {
        "aliases": ["shrimp", "prawn", "蝦類"],
        "types": ["甜蝦", "牡丹蝦", "虎蝦", "草蝦", "白蝦", "櫻花蝦"],
        "origins": ["日本", "越南", "泰國", "阿根廷"],
        "search_patterns": [
            "name ILIKE '%蝦%'",
            "name ILIKE '%shrimp%'",
            "name ILIKE '%prawn%'",
        ],
        "clarification_questions": [
            {
                "slot": "types",
                "question": "想睇邊種蝦？",
                "options": [
                    {"value": "all", "label": "全部"},
                    {"value": "sweet", "label": "甜蝦"},
                    {"value": "botan", "label": "牡丹蝦"},
                    {"value": "tiger", "label": "虎蝦"},
                ]
            }
        ]
    },
    
    # =============================================
    # 乳製品
    # =============================================
    "牛奶": {
        "aliases": ["milk", "鮮奶", "牛乳"],
        "types": ["全脂", "低脂", "脫脂", "特濃", "有機"],
        "brands": ["明治", "森永", "北海道", "雪印", "十勝"],
        "search_patterns": [
            "name ILIKE '%牛奶%'",
            "name ILIKE '%milk%'",
            "name ILIKE '%鮮奶%'",
            "name ILIKE '%牛乳%'",
        ],
        "clarification_questions": []
    },
    
    # =============================================
    # 零食
    # =============================================
    "日本零食": {
        "aliases": ["japanese snack", "日式零食"],
        "types": ["薯片", "餅乾", "糖果", "朱古力", "米餅", "仙貝"],
        "brands": ["Calbee", "Glico", "Meiji", "Lotte", "Morinaga", "不二家"],
        "search_patterns": [
            "(name ILIKE '%日本%' OR brand ILIKE '%日本%') AND (category ILIKE '%零食%' OR category ILIKE '%snack%')",
        ],
        "clarification_questions": [
            {
                "slot": "types",
                "question": "想睇邊類零食？",
                "options": [
                    {"value": "all", "label": "全部"},
                    {"value": "chips", "label": "薯片"},
                    {"value": "biscuit", "label": "餅乾"},
                    {"value": "candy", "label": "糖果"},
                    {"value": "chocolate", "label": "朱古力"},
                ]
            }
        ]
    },
    
    # =============================================
    # 即食麵
    # =============================================
    "即食麵": {
        "aliases": ["instant noodle", "公仔麵", "杯麵", "泡麵"],
        "types": ["袋裝", "杯麵", "碗麵", "拉麵"],
        "brands": ["日清", "出前一丁", "公仔", "農心", "三養"],
        "search_patterns": [
            "name ILIKE '%即食麵%'",
            "name ILIKE '%杯麵%'",
            "name ILIKE '%泡麵%'",
            "name ILIKE '%拉麵%'",
            "name ILIKE '%出前一丁%'",
        ],
        "clarification_questions": []
    },
}

# 時間範圍選項
TIME_RANGE_OPTIONS = [
    {"value": "7d", "label": "過去 7 日", "days": 7},
    {"value": "30d", "label": "過去 30 日", "days": 30},
    {"value": "90d", "label": "過去 90 日", "days": 90},
    {"value": "1y", "label": "過去 1 年", "days": 365},
    {"value": "all", "label": "全部時間", "days": None},
]

# 分析維度選項
ANALYSIS_DIMENSIONS = [
    {"value": "price_overview", "label": "價格概覽", "description": "平均價、最高/最低價"},
    {"value": "price_trend", "label": "價格趨勢", "description": "價格隨時間變化"},
    {"value": "competitor_compare", "label": "競爭對手比較", "description": "同其他平台比較"},
    {"value": "brand_analysis", "label": "品牌分析", "description": "各品牌表現"},
    {"value": "top_products", "label": "熱門產品", "description": "最多評論/最高評分"},
    {"value": "stock_status", "label": "庫存狀態", "description": "有貨/缺貨情況"},
]


def get_product_search_conditions(product_name: str) -> List[str]:
    """
    根據產品名稱獲取 SQL 搜索條件

    注意：此函數返回的是預定義的安全模式，不應用於動態用戶輸入。
    對於用戶輸入，請使用 tools.sql_helpers.build_product_search_conditions()

    Args:
        product_name: 產品名稱（如 "和牛"、"三文魚"）

    Returns:
        SQL WHERE 條件列表（預定義的安全模式）
    """
    # 檢查是否在知識庫中
    for key, data in PRODUCT_TAXONOMY.items():
        if product_name == key or product_name in data.get("aliases", []):
            return data.get("search_patterns", [])

    # 不在知識庫，返回空列表
    # 注意：不再返回動態構建的 SQL，以防止 SQL 注入
    # 調用方應使用 sql_helpers 中的安全函數
    return []


def get_product_clarification_questions(product_name: str) -> List[dict]:
    """
    獲取產品的澄清問題
    
    Args:
        product_name: 產品名稱
    
    Returns:
        澄清問題列表
    """
    for key, data in PRODUCT_TAXONOMY.items():
        if product_name == key or product_name in data.get("aliases", []):
            return data.get("clarification_questions", [])
    return []


def normalize_product_name(query: str) -> str:
    """
    將用戶輸入標準化為知識庫中的產品名稱
    
    Args:
        query: 用戶輸入（如 "wagyu"、"A5牛"）
    
    Returns:
        標準化產品名稱（如 "和牛"）
    """
    query_lower = query.lower()
    
    for key, data in PRODUCT_TAXONOMY.items():
        # 檢查主名稱
        if key.lower() in query_lower or query_lower in key.lower():
            return key
        
        # 檢查別名
        for alias in data.get("aliases", []):
            if alias.lower() in query_lower or query_lower in alias.lower():
                return key
    
    # 無法匹配，返回原始輸入
    return query


def get_all_product_names() -> List[str]:
    """獲取所有產品名稱（用於意圖識別）"""
    names = list(PRODUCT_TAXONOMY.keys())
    for data in PRODUCT_TAXONOMY.values():
        names.extend(data.get("aliases", []))
    return names
