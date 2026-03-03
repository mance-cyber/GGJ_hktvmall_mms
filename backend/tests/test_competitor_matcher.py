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

    def test_none_input(self):
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category(None) is None

    def test_fish_fillet_without_salmon(self):
        """魚柳 without 三文魚 prefix should match 魚柳"""
        from app.services.competitor_matcher import extract_core_category
        assert extract_core_category("日式魚柳") == "魚柳"

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
# _dynamic_threshold 測試
# =============================================

class TestDynamicThreshold:
    """動態匹配閾值"""

    def test_few_candidates(self):
        from app.services.competitor_matcher import _dynamic_threshold
        assert _dynamic_threshold(1) == 0.3
        assert _dynamic_threshold(3) == 0.3

    def test_moderate_candidates(self):
        from app.services.competitor_matcher import _dynamic_threshold
        assert _dynamic_threshold(4) == 0.4
        assert _dynamic_threshold(8) == 0.4

    def test_many_candidates(self):
        from app.services.competitor_matcher import _dynamic_threshold
        assert _dynamic_threshold(9) == 0.5
        assert _dynamic_threshold(50) == 0.5

    def test_zero_candidates(self):
        from app.services.competitor_matcher import _dynamic_threshold
        assert _dynamic_threshold(0) == 0.3


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
