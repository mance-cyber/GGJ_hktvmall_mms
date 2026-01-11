# =============================================
# M-05: URL 安全驗證 (SSRF 防護)
# =============================================

import ipaddress
import socket
from urllib.parse import urlparse
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


# 允許的電商平台域名白名單
ALLOWED_DOMAINS: List[str] = [
    # HKTVmall
    "hktvmall.com",
    "www.hktvmall.com",
    # Watsons
    "watsons.com.hk",
    "www.watsons.com.hk",
    # Mannings
    "mannings.com.hk",
    "www.mannings.com.hk",
    # PARKnSHOP
    "parknshop.com",
    "www.parknshop.com",
    # Wellcome
    "wellcome.com.hk",
    "www.wellcome.com.hk",
    # JD
    "jd.hk",
    "www.jd.hk",
    "jd.com",
    "www.jd.com",
    # Taobao / Tmall
    "taobao.com",
    "world.taobao.com",
    "tmall.com",
    "tmall.hk",
    # Amazon
    "amazon.com",
    "www.amazon.com",
    "amazon.co.jp",
    "www.amazon.co.jp",
    # Sasa
    "sasa.com",
    "www.sasa.com",
    # 其他可以動態添加的平台
]

# 保留/私有 IP 範圍
PRIVATE_IP_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # Link-local
    ipaddress.ip_network("::1/128"),  # IPv6 loopback
    ipaddress.ip_network("fe80::/10"),  # IPv6 link-local
    ipaddress.ip_network("fc00::/7"),  # IPv6 unique local
]


class URLSecurityError(Exception):
    """URL 安全驗證失敗"""
    pass


def is_private_ip(ip_str: str) -> bool:
    """
    檢查 IP 地址是否為私有/保留地址

    Args:
        ip_str: IP 地址字符串

    Returns:
        True 如果是私有地址
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        for network in PRIVATE_IP_RANGES:
            if ip in network:
                return True
        return False
    except ValueError:
        # 無法解析的 IP 視為不安全
        return True


def resolve_hostname(hostname: str) -> Optional[str]:
    """
    解析域名到 IP 地址

    Args:
        hostname: 域名

    Returns:
        IP 地址或 None
    """
    try:
        # 設置超時以防止 DNS 放大攻擊
        socket.setdefaulttimeout(5)
        ip = socket.gethostbyname(hostname)
        return ip
    except socket.error:
        return None


def is_domain_allowed(domain: str, extra_allowed: List[str] = None) -> bool:
    """
    檢查域名是否在白名單中

    Args:
        domain: 要檢查的域名
        extra_allowed: 額外允許的域名列表

    Returns:
        True 如果域名被允許
    """
    domain = domain.lower().strip()
    allowed = ALLOWED_DOMAINS.copy()

    if extra_allowed:
        allowed.extend(extra_allowed)

    for allowed_domain in allowed:
        if domain == allowed_domain or domain.endswith("." + allowed_domain):
            return True

    return False


def validate_url(
    url: str,
    require_https: bool = False,
    check_whitelist: bool = True,
    extra_allowed_domains: List[str] = None,
    resolve_dns: bool = True
) -> Tuple[bool, str]:
    """
    驗證 URL 是否安全

    Args:
        url: 要驗證的 URL
        require_https: 是否要求 HTTPS
        check_whitelist: 是否檢查域名白名單
        extra_allowed_domains: 額外允許的域名
        resolve_dns: 是否解析 DNS 檢查 IP

    Returns:
        (is_valid, error_message) 元組
    """
    if not url or not isinstance(url, str):
        return False, "URL 為空或無效"

    url = url.strip()

    # 基本格式檢查
    if not url.startswith(("http://", "https://")):
        return False, "URL 必須使用 HTTP 或 HTTPS 協議"

    if require_https and not url.startswith("https://"):
        return False, "URL 必須使用 HTTPS 協議"

    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"無法解析 URL: {e}"

    # 檢查 scheme
    if parsed.scheme not in ("http", "https"):
        return False, f"不支持的協議: {parsed.scheme}"

    # 檢查是否有主機名
    hostname = parsed.hostname
    if not hostname:
        return False, "URL 缺少主機名"

    # 阻止 localhost 和常見內部域名
    hostname_lower = hostname.lower()
    blocked_hostnames = [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "::1",
        "[::1]",
        "internal",
        "intranet",
        "local",
    ]
    if hostname_lower in blocked_hostnames or hostname_lower.endswith(".local"):
        return False, "不允許訪問本地或內部地址"

    # 檢查是否為 IP 地址
    try:
        ip = ipaddress.ip_address(hostname)
        if is_private_ip(str(ip)):
            return False, "不允許訪問私有 IP 地址"
    except ValueError:
        # 不是 IP 地址，是域名
        pass

    # DNS 解析檢查（防止 DNS 重綁定攻擊）
    if resolve_dns:
        resolved_ip = resolve_hostname(hostname)
        if resolved_ip:
            if is_private_ip(resolved_ip):
                logger.warning(
                    f"URL 安全警告: {hostname} 解析到私有 IP {resolved_ip}"
                )
                return False, "域名解析到私有 IP 地址，拒絕訪問"

    # 白名單檢查
    if check_whitelist:
        if not is_domain_allowed(hostname, extra_allowed_domains):
            return False, f"域名 {hostname} 不在允許的白名單中"

    # 阻止特殊端口（可選）
    port = parsed.port
    if port and port not in (80, 443, 8080, 8443):
        # 允許常見 HTTP 端口，阻止其他端口
        # 這可以防止訪問內部服務
        return False, f"不允許使用端口 {port}"

    return True, ""


def validate_url_strict(url: str, extra_allowed_domains: List[str] = None) -> str:
    """
    嚴格驗證 URL，失敗時拋出異常

    Args:
        url: 要驗證的 URL
        extra_allowed_domains: 額外允許的域名

    Returns:
        清理後的 URL

    Raises:
        URLSecurityError: 如果 URL 不安全
    """
    is_valid, error = validate_url(
        url,
        require_https=False,
        check_whitelist=True,
        extra_allowed_domains=extra_allowed_domains,
        resolve_dns=True
    )

    if not is_valid:
        logger.warning(f"URL 安全驗證失敗: {url} - {error}")
        raise URLSecurityError(error)

    return url.strip()


def validate_urls_batch(
    urls: List[str],
    extra_allowed_domains: List[str] = None
) -> Tuple[List[str], List[Tuple[str, str]]]:
    """
    批量驗證 URL

    Args:
        urls: URL 列表
        extra_allowed_domains: 額外允許的域名

    Returns:
        (valid_urls, invalid_urls_with_errors) 元組
    """
    valid_urls = []
    invalid_urls = []

    for url in urls:
        is_valid, error = validate_url(
            url,
            check_whitelist=True,
            extra_allowed_domains=extra_allowed_domains
        )

        if is_valid:
            valid_urls.append(url.strip())
        else:
            invalid_urls.append((url, error))

    return valid_urls, invalid_urls
