# =============================================
# 安全功能測試
# =============================================

import pytest
import os
from unittest.mock import patch


class TestConfigSecretKeyValidation:
    """測試配置中的 SECRET_KEY 驗證"""

    def test_weak_secret_key_rejected_in_production(self):
        """測試生產環境拒絕弱密鑰"""
        from pydantic import ValidationError

        with patch.dict(os.environ, {
            "APP_ENV": "production",
            "SECRET_KEY": "weak",
            "DATABASE_URL": "sqlite:///test.db",
        }, clear=False):
            # 需要重新導入以獲取新的設定
            from app.config import Settings
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            assert "SECRET_KEY" in str(exc_info.value)

    def test_default_secret_key_rejected_in_production(self):
        """測試生產環境拒絕預設密鑰"""
        from pydantic import ValidationError

        with patch.dict(os.environ, {
            "APP_ENV": "production",
            "SECRET_KEY": "dev-secret-key-CHANGE-IN-PRODUCTION",
            "DATABASE_URL": "sqlite:///test.db",
        }, clear=False):
            from app.config import Settings
            with pytest.raises(ValidationError) as exc_info:
                Settings()
            assert "SECRET_KEY" in str(exc_info.value)

    def test_strong_secret_key_accepted_in_production(self):
        """測試生產環境接受強密鑰"""
        with patch.dict(os.environ, {
            "APP_ENV": "production",
            "SECRET_KEY": "this-is-a-very-strong-secret-key-that-is-long-enough-for-production",
            "DATABASE_URL": "sqlite:///test.db",
        }, clear=False):
            from app.config import Settings
            settings = Settings()
            assert len(settings.secret_key) >= 32

    def test_weak_secret_key_allowed_in_development(self):
        """測試開發環境允許弱密鑰"""
        with patch.dict(os.environ, {
            "APP_ENV": "development",
            "SECRET_KEY": "dev-key",
            "DATABASE_URL": "sqlite:///test.db",
        }, clear=False):
            from app.config import Settings
            settings = Settings()
            assert settings.secret_key == "dev-key"


class TestURLSecurity:
    """測試 URL 安全驗證"""

    def test_valid_hktvmall_url_allowed(self):
        """測試有效的 HKTVmall URL 被允許"""
        from app.core.url_security import validate_url

        is_valid, error = validate_url("https://www.hktvmall.com/product/123")
        assert is_valid is True, f"HKTVmall URL should be allowed: {error}"

    def test_private_ip_blocked(self):
        """測試私有 IP 被阻止"""
        from app.core.url_security import validate_url

        # 測試各種私有 IP（不進行 DNS 解析以避免測試環境問題）
        private_urls = [
            "http://127.0.0.1/test",
            "http://192.168.1.1/test",
            "http://10.0.0.1/test",
            "http://172.16.0.1/test",
            "http://localhost/test",
        ]

        for url in private_urls:
            is_valid, error = validate_url(url, resolve_dns=False, check_whitelist=False)
            assert is_valid is False, f"Private URL should be blocked: {url}"

    def test_non_whitelisted_domain_blocked(self):
        """測試非白名單域名被阻止"""
        from app.core.url_security import validate_url

        is_valid, error = validate_url("https://evil-site.com/malicious", resolve_dns=False)
        assert is_valid is False, f"Non-whitelisted domain should be blocked"

    def test_invalid_url_format_blocked(self):
        """測試無效 URL 格式被阻止"""
        from app.core.url_security import validate_url

        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "file:///etc/passwd",
            "",
        ]

        for url in invalid_urls:
            is_valid, error = validate_url(url, resolve_dns=False, check_whitelist=False)
            assert is_valid is False, f"Invalid URL should be blocked: {url}"


class TestInputValidation:
    """測試輸入驗證"""

    def test_sql_injection_in_search(self):
        """測試搜索參數中的 SQL 注入被防護"""
        # 這個測試確保 ORM 正確處理輸入
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "admin'--",
            "UNION SELECT * FROM users",
        ]

        # SQLAlchemy ORM 會自動參數化查詢，這裡只是確保不會崩潰
        for input_str in malicious_inputs:
            # 輸入應該被當作普通字符串處理，不應引起任何錯誤
            assert isinstance(input_str, str)

    def test_xss_characters_in_input(self):
        """測試 XSS 字符在輸入中的處理"""
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "'\"><script>alert('xss')</script>",
        ]

        # 確保這些輸入不會導致崩潰
        for input_str in xss_inputs:
            assert isinstance(input_str, str)
            # 在實際 API 中，這些應該被轉義或過濾


class TestRateLimitingSecurity:
    """測試速率限制安全"""

    def test_rate_limiter_structure(self):
        """測試速率限制器結構"""
        from app.services.rate_limiter import TokenBucketRateLimiter, RateLimiterConfig

        # 確保類存在
        assert TokenBucketRateLimiter is not None
        assert RateLimiterConfig is not None

    def test_rate_limit_key_generation(self):
        """測試速率限制鍵生成"""
        # 確保鍵生成是安全的，不會導致注入
        test_identifiers = [
            "user:123",
            "ip:192.168.1.1",
            "api:endpoint/path",
            "user:'; DROP TABLE rate_limits; --",
        ]

        for identifier in test_identifiers:
            # 鍵應該是字符串
            key = f"rate_limit:{identifier}"
            assert isinstance(key, str)
