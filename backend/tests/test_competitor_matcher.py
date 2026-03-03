"""競品匹配放寬：核心品類提取 + Cataloger per-store 上限"""
import pytest


# =============================================
# extract_core_category 測試
# =============================================

class TestExtractCoreCategory:
    """從商品名提取核心品類詞"""

    def test_wagyu_with_origin(self):
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("宮崎 A5 和牛西冷") == "和牛"

    def test_salmon(self):
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("挪威三文魚柳") == "三文魚"

    def test_scallop_sashimi(self):
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("北海道帶子刺身") == "帶子"

    def test_no_match(self):
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("有機蔬菜沙律") is None

    def test_empty_string(self):
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("") is None

    def test_pork_chop(self):
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("鹿兒島黑豚豬扒") == "豬扒"

    def test_priority_specific_over_generic(self):
        """和牛 should match before 牛肉 (more specific first)"""
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("澳洲和牛牛肉") == "和牛"

    def test_kagoshima_wagyu(self):
        """鹿兒島 A5 和牛 — 確認產地不影響提取"""
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("鹿兒島 A5 和牛") == "和牛"

    def test_crab(self):
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("北海道毛蟹") == "蟹"

    def test_sea_urchin(self):
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("馬糞海膽") == "海膽"


# =============================================
# Cataloger per-store 上限
# =============================================

class TestCatalogerStoreLimit:
    """Cataloger per-store 上限常量"""

    def test_constant_exists(self):
        from app.services.cataloger import HKTV_MAX_PRODUCTS_PER_STORE
        assert HKTV_MAX_PRODUCTS_PER_STORE == 200

    def test_constant_is_reasonable(self):
        from app.services.cataloger import HKTV_MAX_PRODUCTS_PER_STORE
        assert 50 <= HKTV_MAX_PRODUCTS_PER_STORE <= 500
