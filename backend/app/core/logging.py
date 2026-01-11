# =============================================
# H-04: 日誌敏感數據過濾
# =============================================

import re
import logging
from typing import ClassVar


class SensitiveDataFilter(logging.Filter):
    """
    過濾日誌中的敏感數據

    自動檢測並遮蔽：
    - API 密鑰
    - Token (JWT, Bearer, etc.)
    - 密碼
    - Secret
    - 信用卡號
    - 郵箱地址 (部分遮蔽)
    """

    # 敏感數據匹配模式
    PATTERNS: ClassVar[list[tuple[re.Pattern, str]]] = [
        # API Keys (各種格式)
        (re.compile(r'(api[_-]?key["\s:=]+)["\']?[\w-]{16,}["\']?', re.I), r'\1***REDACTED***'),
        (re.compile(r'(x-api-key["\s:]+)["\']?[\w-]{16,}["\']?', re.I), r'\1***REDACTED***'),
        # Bearer Token
        (re.compile(r'(Bearer\s+)[\w.-]{20,}', re.I), r'\1***REDACTED***'),
        # JWT Token (完整格式)
        (re.compile(r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'), '***JWT_REDACTED***'),
        # 密碼
        (re.compile(r'(password["\s:=]+)["\']?[^\s",}{]+["\']?', re.I), r'\1***REDACTED***'),
        (re.compile(r'(pwd["\s:=]+)["\']?[^\s",}{]+["\']?', re.I), r'\1***REDACTED***'),
        # Token 通用
        (re.compile(r'(token["\s:=]+)["\']?[\w.-]{20,}["\']?', re.I), r'\1***REDACTED***'),
        (re.compile(r'(access_token["\s:=]+)["\']?[\w.-]{20,}["\']?', re.I), r'\1***REDACTED***'),
        (re.compile(r'(refresh_token["\s:=]+)["\']?[\w.-]{20,}["\']?', re.I), r'\1***REDACTED***'),
        # Secret
        (re.compile(r'(secret[_-]?key?["\s:=]+)["\']?[\w-]{10,}["\']?', re.I), r'\1***REDACTED***'),
        # Anthropic API Key
        (re.compile(r'sk-ant-[\w-]+', re.I), '***ANTHROPIC_KEY_REDACTED***'),
        # OpenAI API Key
        (re.compile(r'sk-[\w-]{40,}', re.I), '***OPENAI_KEY_REDACTED***'),
        # AWS 密鑰
        (re.compile(r'(AKIA|ABIA|ACCA|ASIA)[A-Z0-9]{16}', re.I), '***AWS_KEY_REDACTED***'),
        # 信用卡號 (基本格式)
        (re.compile(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b'), '***CARD_REDACTED***'),
        # 連接字符串中的密碼
        (re.compile(r'(://[^:]+:)[^@]+(@)', re.I), r'\1***@'),
        # Authorization header
        (re.compile(r'(Authorization["\s:]+)["\']?[\w\s.-]+["\']?', re.I), r'\1***REDACTED***'),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """過濾敏感數據"""
        # 處理消息
        if isinstance(record.msg, str):
            record.msg = self._sanitize(record.msg)

        # 處理參數
        if record.args:
            sanitized_args = tuple(
                self._sanitize(str(arg)) if isinstance(arg, str) else arg
                for arg in record.args
            )
            record.args = sanitized_args

        return True

    def _sanitize(self, text: str) -> str:
        """對文本應用所有過濾規則"""
        for pattern, replacement in self.PATTERNS:
            text = pattern.sub(replacement, text)
        return text


def setup_logging(debug: bool = False) -> None:
    """
    配置應用日誌

    Args:
        debug: 是否為調試模式
    """
    level = logging.DEBUG if debug else logging.INFO

    # 配置格式
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 配置根日誌器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 清除現有處理器
    root_logger.handlers.clear()

    # 添加控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(SensitiveDataFilter())
    root_logger.addHandler(console_handler)

    # 設置第三方庫日誌級別
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    獲取已配置的日誌器

    Args:
        name: 日誌器名稱（通常使用 __name__）

    Returns:
        配置好的日誌器實例
    """
    logger = logging.getLogger(name)
    # 確保過濾器已添加
    if not any(isinstance(f, SensitiveDataFilter) for f in logger.filters):
        logger.addFilter(SensitiveDataFilter())
    return logger
