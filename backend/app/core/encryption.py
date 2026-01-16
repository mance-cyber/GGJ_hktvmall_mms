# =============================================
# 數據加密工具
# =============================================
# 用於敏感數據（如 API Key、Webhook Secret）的加密存儲

import base64
import hashlib
import os
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import get_settings


def _derive_key(secret_key: str, salt: bytes) -> bytes:
    """
    從 SECRET_KEY 派生加密密鑰

    使用 PBKDF2 進行密鑰派生，增強安全性
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = kdf.derive(secret_key.encode())
    return base64.urlsafe_b64encode(key)


def _get_fernet(salt: bytes) -> Fernet:
    """獲取 Fernet 加密實例"""
    settings = get_settings()
    key = _derive_key(settings.secret_key, salt)
    return Fernet(key)


# =============================================
# 公開 API
# =============================================

def encrypt_value(plaintext: str) -> str:
    """
    加密敏感值

    Args:
        plaintext: 明文字符串

    Returns:
        加密後的字符串（格式：base64(salt) + '.' + base64(ciphertext)）
    """
    if not plaintext:
        return ""

    # 生成隨機 salt（每次加密不同）
    salt = os.urandom(16)
    fernet = _get_fernet(salt)

    # 加密
    ciphertext = fernet.encrypt(plaintext.encode())

    # 組合 salt 和密文
    salt_b64 = base64.urlsafe_b64encode(salt).decode()
    cipher_b64 = base64.urlsafe_b64encode(ciphertext).decode()

    return f"{salt_b64}.{cipher_b64}"


def decrypt_value(encrypted: str) -> Optional[str]:
    """
    解密敏感值

    Args:
        encrypted: 加密後的字符串

    Returns:
        解密後的明文，失敗返回 None
    """
    if not encrypted:
        return None

    try:
        # 分離 salt 和密文
        parts = encrypted.split(".", 1)
        if len(parts) != 2:
            return None

        salt_b64, cipher_b64 = parts
        salt = base64.urlsafe_b64decode(salt_b64)
        ciphertext = base64.urlsafe_b64decode(cipher_b64)

        # 解密
        fernet = _get_fernet(salt)
        plaintext = fernet.decrypt(ciphertext)

        return plaintext.decode()
    except (ValueError, InvalidToken, Exception):
        return None


def is_encrypted(value: str) -> bool:
    """
    檢查值是否已加密

    通過檢查格式來判斷（格式：base64.base64）
    """
    if not value:
        return False

    parts = value.split(".", 1)
    if len(parts) != 2:
        return False

    try:
        # 嘗試解碼 base64
        base64.urlsafe_b64decode(parts[0])
        base64.urlsafe_b64decode(parts[1])
        return True
    except (ValueError, Exception):
        return False


def hash_value(value: str, salt: Optional[str] = None) -> str:
    """
    對值進行單向哈希（用於不需要解密的場景）

    Args:
        value: 原始值
        salt: 可選的 salt，如果不提供會生成新的

    Returns:
        格式：salt$hash
    """
    if salt is None:
        salt = base64.urlsafe_b64encode(os.urandom(16)).decode()

    hash_obj = hashlib.pbkdf2_hmac(
        "sha256",
        value.encode(),
        salt.encode(),
        100000
    )
    hash_b64 = base64.urlsafe_b64encode(hash_obj).decode()

    return f"{salt}${hash_b64}"


def verify_hash(value: str, hashed: str) -> bool:
    """
    驗證哈希值

    Args:
        value: 原始值
        hashed: 哈希後的值（格式：salt$hash）

    Returns:
        是否匹配
    """
    try:
        parts = hashed.split("$", 1)
        if len(parts) != 2:
            return False

        salt = parts[0]
        expected = hash_value(value, salt)
        return expected == hashed
    except Exception:
        return False
