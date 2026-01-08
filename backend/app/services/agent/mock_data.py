# =============================================
# AI Agent 模擬數據
# 用於測試 AI 助手回覆，不影響正式系統運作
# 刪除此文件即可完全移除模擬數據功能
# =============================================

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import random
from datetime import datetime, timedelta


# =============================================
# 模擬產品數據
# =============================================

MOCK_PRODUCTS = {
    "和牛": {
        "products": [
            {
                "id": "mock-wagyu-001",
                "name": "日本 A5 和牛西冷 (200g)",
                "sku": "WAGYU-A5-SIRLOIN-200",
                "brand": "鹿兒島黑毛和牛",
                "price": 688.00,
                "original_price": 788.00,
                "discount_percent": 12.7,
                "stock_status": "in_stock",
                "rating": 4.8,
                "review_count": 156,
                "image_url": "https://example.com/wagyu-sirloin.jpg",
            },
            {
                "id": "mock-wagyu-002",
                "name": "澳洲 M9 和牛肉眼扒 (250g)",
                "sku": "WAGYU-M9-RIBEYE-250",
                "brand": "Blackmore",
                "price": 458.00,
                "original_price": 528.00,
                "discount_percent": 13.3,
                "stock_status": "in_stock",
                "rating": 4.6,
                "review_count": 89,
                "image_url": "https://example.com/wagyu-ribeye.jpg",
            },
            {
                "id": "mock-wagyu-003",
                "name": "日本 A4 和牛燒肉片 (300g)",
                "sku": "WAGYU-A4-BBQ-300",
                "brand": "宮崎牛",
                "price": 388.00,
                "original_price": 438.00,
                "discount_percent": 11.4,
                "stock_status": "low_stock",
                "rating": 4.7,
                "review_count": 234,
                "image_url": "https://example.com/wagyu-bbq.jpg",
            },
        ],
        "price_range": {"min": 388, "max": 1288, "avg": 588},
        "brands": ["鹿兒島黑毛和牛", "宮崎牛", "Blackmore", "Rangers Valley"],
    },
    "海膽": {
        "products": [
            {
                "id": "mock-uni-001",
                "name": "北海道馬糞海膽 (100g)",
                "sku": "UNI-BAFUN-100",
                "brand": "北海道直送",
                "price": 288.00,
                "original_price": 328.00,
                "discount_percent": 12.2,
                "stock_status": "in_stock",
                "rating": 4.9,
                "review_count": 312,
                "image_url": "https://example.com/uni-bafun.jpg",
            },
            {
                "id": "mock-uni-002",
                "name": "紫海膽刺身 (80g)",
                "sku": "UNI-MURASAKI-80",
                "brand": "利尻島",
                "price": 198.00,
                "original_price": 238.00,
                "discount_percent": 16.8,
                "stock_status": "in_stock",
                "rating": 4.7,
                "review_count": 178,
                "image_url": "https://example.com/uni-murasaki.jpg",
            },
        ],
        "price_range": {"min": 168, "max": 488, "avg": 268},
        "brands": ["北海道直送", "利尻島", "禮文島"],
    },
    "三文魚": {
        "products": [
            {
                "id": "mock-salmon-001",
                "name": "挪威三文魚刺身 (250g)",
                "sku": "SALMON-NORWAY-250",
                "brand": "MOWI",
                "price": 128.00,
                "original_price": 148.00,
                "discount_percent": 13.5,
                "stock_status": "in_stock",
                "rating": 4.5,
                "review_count": 567,
                "image_url": "https://example.com/salmon-sashimi.jpg",
            },
            {
                "id": "mock-salmon-002",
                "name": "蘇格蘭煙燻三文魚 (200g)",
                "sku": "SALMON-SMOKED-200",
                "brand": "Loch Duart",
                "price": 98.00,
                "original_price": 118.00,
                "discount_percent": 16.9,
                "stock_status": "in_stock",
                "rating": 4.6,
                "review_count": 234,
                "image_url": "https://example.com/salmon-smoked.jpg",
            },
        ],
        "price_range": {"min": 68, "max": 268, "avg": 128},
        "brands": ["MOWI", "Loch Duart", "Bakkafrost"],
    },
    "日本零食": {
        "products": [
            {
                "id": "mock-snack-001",
                "name": "Royce 生巧克力 (20片)",
                "sku": "ROYCE-NAMA-20",
                "brand": "Royce'",
                "price": 128.00,
                "original_price": 148.00,
                "discount_percent": 13.5,
                "stock_status": "in_stock",
                "rating": 4.9,
                "review_count": 1234,
                "image_url": "https://example.com/royce-choco.jpg",
            },
            {
                "id": "mock-snack-002",
                "name": "白色戀人餅乾 (24枚)",
                "sku": "SHIROI-KOIBITO-24",
                "brand": "石屋製菓",
                "price": 168.00,
                "original_price": 188.00,
                "discount_percent": 10.6,
                "stock_status": "in_stock",
                "rating": 4.8,
                "review_count": 987,
                "image_url": "https://example.com/shiroi-koibito.jpg",
            },
            {
                "id": "mock-snack-003",
                "name": "東京香蕉蛋糕 (8個)",
                "sku": "TOKYO-BANANA-8",
                "brand": "東京ばな奈",
                "price": 98.00,
                "original_price": 108.00,
                "discount_percent": 9.3,
                "stock_status": "low_stock",
                "rating": 4.7,
                "review_count": 654,
                "image_url": "https://example.com/tokyo-banana.jpg",
            },
        ],
        "price_range": {"min": 38, "max": 268, "avg": 128},
        "brands": ["Royce'", "石屋製菓", "東京ばな奈", "六花亭"],
    },
}


# =============================================
# 模擬競爭對手數據
# =============================================

MOCK_COMPETITORS = {
    "百佳": {
        "id": "mock-competitor-parknshop",
        "name": "百佳",
        "platform": "parknshop",
        "products": {
            "和牛": {"avg_price": 628, "price_diff_percent": 8.5},
            "海膽": {"avg_price": 298, "price_diff_percent": -3.4},
            "三文魚": {"avg_price": 138, "price_diff_percent": -7.2},
            "日本零食": {"avg_price": 138, "price_diff_percent": -7.0},
        },
    },
    "惠康": {
        "id": "mock-competitor-wellcome",
        "name": "惠康",
        "platform": "wellcome",
        "products": {
            "和牛": {"avg_price": 658, "price_diff_percent": 3.8},
            "海膽": {"avg_price": 278, "price_diff_percent": 3.6},
            "三文魚": {"avg_price": 132, "price_diff_percent": -3.0},
            "日本零食": {"avg_price": 132, "price_diff_percent": -3.0},
        },
    },
    "AEON": {
        "id": "mock-competitor-aeon",
        "name": "AEON",
        "platform": "aeon",
        "products": {
            "和牛": {"avg_price": 598, "price_diff_percent": 12.2},
            "海膽": {"avg_price": 268, "price_diff_percent": 7.5},
            "三文魚": {"avg_price": 118, "price_diff_percent": 8.5},
            "日本零食": {"avg_price": 118, "price_diff_percent": 8.5},
        },
    },
}


# =============================================
# 模擬價格趨勢數據
# =============================================

def generate_mock_price_trend(product_name: str, days: int = 30) -> List[Dict]:
    """生成模擬價格趨勢數據"""
    base_prices = {
        "和牛": 588,
        "海膽": 268,
        "三文魚": 128,
        "日本零食": 128,
    }
    
    base_price = base_prices.get(product_name, 200)
    trend_data = []
    
    today = datetime.now()
    for i in range(days, 0, -1):
        date = today - timedelta(days=i)
        # 添加一些隨機波動 (±15%)
        variation = random.uniform(-0.15, 0.15)
        price = round(base_price * (1 + variation), 2)
        
        trend_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "price": price,
            "original_price": round(price * 1.15, 2),
            "discount_percent": round(random.uniform(5, 20), 1),
        })
    
    return trend_data


# =============================================
# 模擬報告數據
# =============================================

MOCK_REPORTS = {
    "price_analysis": {
        "title": "價格分析報告",
        "sections": [
            "## 📊 價格概覽\n\n根據過去 30 日數據：",
            "## 📈 價格趨勢\n\n整體價格呈現穩定趨勢，部分產品有促銷活動。",
            "## ⚔️ 競爭對手比較\n\n我哋嘅價格喺市場上具有競爭力。",
            "## 💡 建議\n\n建議密切關注競爭對手定價策略。",
        ],
    },
    "market_overview": {
        "title": "市場概覽報告",
        "sections": [
            "## 🏪 市場概況\n\n",
            "## 🔥 熱門產品\n\n",
            "## 📊 銷售趨勢\n\n",
            "## 🎯 機會分析\n\n",
        ],
    },
}


# =============================================
# 模擬 AI 回覆生成器
# =============================================

class MockResponseGenerator:
    """模擬 AI 回覆生成器"""
    
    @staticmethod
    def get_product_overview(product_names: List[str]) -> Dict[str, Any]:
        """獲取產品概覽模擬數據"""
        result = {
            "products": [],
            "summary": {},
            "brands": [],
        }
        
        for name in product_names:
            if name in MOCK_PRODUCTS:
                data = MOCK_PRODUCTS[name]
                result["products"].extend(data["products"])
                result["summary"][name] = data["price_range"]
                result["brands"].extend(data["brands"])
        
        result["brands"] = list(set(result["brands"]))
        return result
    
    @staticmethod
    def get_price_trend(product_names: List[str], days: int = 30) -> Dict[str, Any]:
        """獲取價格趨勢模擬數據"""
        result = {}
        for name in product_names:
            result[name] = {
                "trend_data": generate_mock_price_trend(name, days),
                "statistics": {
                    "min_price": round(random.uniform(100, 200), 2),
                    "max_price": round(random.uniform(500, 800), 2),
                    "avg_price": round(random.uniform(300, 500), 2),
                    "price_change_percent": round(random.uniform(-10, 10), 1),
                },
            }
        return result
    
    @staticmethod
    def get_competitor_comparison(
        product_names: List[str],
        competitor_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """獲取競爭對手比較模擬數據"""
        competitors_to_use = competitor_names or list(MOCK_COMPETITORS.keys())
        
        result = {
            "our_prices": {},
            "competitors": {},
            "analysis": [],
        }
        
        for product in product_names:
            if product in MOCK_PRODUCTS:
                result["our_prices"][product] = MOCK_PRODUCTS[product]["price_range"]["avg"]
        
        for comp_name in competitors_to_use:
            if comp_name in MOCK_COMPETITORS:
                comp = MOCK_COMPETITORS[comp_name]
                result["competitors"][comp_name] = {}
                for product in product_names:
                    if product in comp["products"]:
                        result["competitors"][comp_name][product] = comp["products"][product]
        
        # 生成分析
        result["analysis"] = [
            f"• 喺 {product_names[0]} 方面，我哋嘅價格比市場平均低約 5%",
            "• 建議密切關注 AEON 嘅定價策略",
            "• 整體而言，我哋嘅定價具有競爭力",
        ]
        
        return result
    
    @staticmethod
    def get_top_products(category: Optional[str] = None) -> List[Dict]:
        """獲取熱門產品模擬數據"""
        all_products = []
        
        for cat, data in MOCK_PRODUCTS.items():
            if category is None or cat == category:
                all_products.extend(data["products"])
        
        # 按評分排序
        sorted_products = sorted(
            all_products,
            key=lambda x: (x.get("rating", 0), x.get("review_count", 0)),
            reverse=True
        )
        
        return sorted_products[:10]
    
    @staticmethod
    def generate_mock_report(
        product_names: List[str],
        report_type: str = "price_analysis"
    ) -> Dict[str, Any]:
        """生成模擬報告"""
        products_str = "、".join(product_names)
        
        # 生成模擬 Markdown 報告
        markdown = f"""# {products_str} 分析報告

> 📅 報告生成時間：{datetime.now().strftime('%Y-%m-%d %H:%M')}
> 🤖 此為 **模擬數據** 用於測試 AI 助手

---

## 📊 價格概覽

| 產品 | 平均價格 | 最低價 | 最高價 | 品牌數 |
|------|---------|--------|--------|--------|
"""
        
        for name in product_names:
            if name in MOCK_PRODUCTS:
                pr = MOCK_PRODUCTS[name]["price_range"]
                brands = len(MOCK_PRODUCTS[name]["brands"])
                markdown += f"| {name} | ${pr['avg']} | ${pr['min']} | ${pr['max']} | {brands} |\n"
        
        markdown += """
---

## 📈 價格趨勢

過去 30 日價格走勢整體平穩，部分產品因促銷活動出現短期波動。

### 主要發現：
- ✅ 和牛價格穩定在 $500-700 區間
- ✅ 海膽受季節影響，價格略有上升
- ⚠️ 競爭對手百佳近期有促銷活動

---

## ⚔️ 競爭對手分析

| 平台 | 價格競爭力 | 建議 |
|------|-----------|------|
| 百佳 | 較高 | 關注促銷 |
| 惠康 | 持平 | 維持現狀 |
| AEON | 較低 | 可適度提價 |

---

## 💡 營運建議

1. **短期**：關注百佳嘅促銷活動，適時跟進
2. **中期**：考慮推出組合優惠套裝
3. **長期**：建立會員專屬價格體系

---

*此報告由 AI 助手生成（模擬數據）*
"""
        
        # 生成模擬圖表數據
        charts = [
            {
                "type": "line",
                "title": f"{products_str} 價格趨勢",
                "data": generate_mock_price_trend(product_names[0] if product_names else "和牛", 30),
                "config": {
                    "xKey": "date",
                    "yKeys": [
                        {"key": "price", "color": "#8b5cf6", "name": "價格"},
                    ],
                },
            },
            {
                "type": "bar",
                "title": "競爭對手價格比較",
                "data": [
                    {"name": "我哋", "price": 588},
                    {"name": "百佳", "price": 628},
                    {"name": "惠康", "price": 658},
                    {"name": "AEON", "price": 598},
                ],
                "config": {
                    "xKey": "name",
                    "yKeys": [
                        {"key": "price", "color": "#3b82f6", "name": "平均價格"},
                    ],
                },
            },
        ]
        
        return {
            "title": f"{products_str} 分析報告",
            "markdown": markdown,
            "charts": charts,
            "tables": [],
            "summary": f"分析咗 {len(product_names)} 個產品類別，整體市場表現穩定。",
            "generated_at": datetime.now().isoformat(),
        }


# =============================================
# Mock 服務開關
# =============================================

def is_mock_mode_enabled() -> bool:
    """檢查是否啟用模擬模式"""
    import os
    return os.getenv("AGENT_MOCK_MODE", "false").lower() == "true"


def get_mock_response_for_intent(
    intent: str,
    slots: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    根據意圖獲取模擬回覆
    
    Args:
        intent: 意圖類型
        slots: 槽位數據
    
    Returns:
        模擬回覆數據，若未啟用模擬模式則返回 None
    """
    if not is_mock_mode_enabled():
        return None
    
    products = slots.get("products", ["和牛"])
    
    generator = MockResponseGenerator()
    
    if intent in ["price_analysis", "product_detail"]:
        return {
            "type": "report",
            "data": generator.generate_mock_report(products, "price_analysis"),
        }
    
    if intent == "trend_analysis":
        return {
            "type": "report",
            "data": generator.generate_mock_report(products, "price_analysis"),
            "extra": generator.get_price_trend(products),
        }
    
    if intent == "competitor_analysis":
        return {
            "type": "report",
            "data": generator.generate_mock_report(products, "price_analysis"),
            "extra": generator.get_competitor_comparison(products),
        }
    
    if intent in ["market_overview", "generate_report"]:
        return {
            "type": "report",
            "data": generator.generate_mock_report(products, "market_overview"),
        }
    
    # 默認回覆
    return {
        "type": "message",
        "content": f"（模擬回覆）我收到咗你嘅查詢：{products}。呢個係測試數據，實際系統會連接真實數據庫。",
    }
