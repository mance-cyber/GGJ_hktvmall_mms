// ==================== URL 安全驗證工具 ====================
// 用途: 防止 SSRF 攻擊，確保只抓取允許的域名
// 安全級別: CRITICAL

/**
 * 允許的域名白名單
 * 只允許抓取 HKTVmall 官方域名
 */
const ALLOWED_DOMAINS = [
  'hktvmall.com',
  'www.hktvmall.com',
  'm.hktvmall.com',
] as const;

/**
 * 禁止訪問的內部網絡範圍（防止 SSRF）
 */
const BLOCKED_IP_RANGES = [
  /^127\./,           // localhost
  /^10\./,            // 私有網絡 10.0.0.0/8
  /^172\.(1[6-9]|2[0-9]|3[01])\./,  // 私有網絡 172.16.0.0/12
  /^192\.168\./,      // 私有網絡 192.168.0.0/16
  /^169\.254\./,      // Link-local
  /^0\./,             // 無效地址
  /^224\./,           // 組播地址
  /^255\./,           // 廣播地址
];

/**
 * URL 驗證結果
 */
export interface URLValidationResult {
  isValid: boolean;
  error?: string;
  sanitizedUrl?: string;
}

/**
 * 驗證 URL 是否安全可抓取
 * @param url 待驗證的 URL
 * @returns 驗證結果
 */
export function validateScraperURL(url: string): URLValidationResult {
  try {
    // 1. 基本格式驗證
    if (!url || typeof url !== 'string') {
      return {
        isValid: false,
        error: 'URL 不能為空',
      };
    }

    // 2. 解析 URL
    let parsedUrl: URL;
    try {
      parsedUrl = new URL(url);
    } catch {
      return {
        isValid: false,
        error: 'URL 格式無效',
      };
    }

    // 3. 協議驗證 - 只允許 HTTPS
    if (parsedUrl.protocol !== 'https:') {
      return {
        isValid: false,
        error: '只允許 HTTPS 協議',
      };
    }

    // 4. 域名白名單驗證
    const hostname = parsedUrl.hostname.toLowerCase();
    const isAllowedDomain = ALLOWED_DOMAINS.some(
      (domain) => hostname === domain || hostname.endsWith(`.${domain}`)
    );

    if (!isAllowedDomain) {
      return {
        isValid: false,
        error: `域名 "${hostname}" 不在白名單中，只允許 ${ALLOWED_DOMAINS.join(', ')}`,
      };
    }

    // 5. IP 地址檢測（防止直接使用 IP 繞過域名檢查）
    if (/^\d+\.\d+\.\d+\.\d+$/.test(hostname)) {
      // 檢查是否為內部 IP
      const isBlocked = BLOCKED_IP_RANGES.some((pattern) => pattern.test(hostname));
      if (isBlocked) {
        return {
          isValid: false,
          error: '不允許訪問內部網絡地址',
        };
      }
    }

    // 6. 路徑驗證 - 防止目錄遍歷
    if (parsedUrl.pathname.includes('..')) {
      return {
        isValid: false,
        error: '路徑包含非法字符',
      };
    }

    // 7. 長度限制
    if (url.length > 2048) {
      return {
        isValid: false,
        error: 'URL 長度超過限制（最多 2048 字符）',
      };
    }

    // 驗證通過，返回清理後的 URL
    return {
      isValid: true,
      sanitizedUrl: parsedUrl.toString(),
    };
  } catch (error) {
    return {
      isValid: false,
      error: error instanceof Error ? error.message : 'URL 驗證失敗',
    };
  }
}

/**
 * 批量驗證 URL
 * @param urls URL 列表
 * @returns 驗證結果列表
 */
export function validateScraperURLs(
  urls: string[]
): { validUrls: string[]; invalidUrls: { url: string; error: string }[] } {
  const validUrls: string[] = [];
  const invalidUrls: { url: string; error: string }[] = [];

  for (const url of urls) {
    const result = validateScraperURL(url);
    if (result.isValid && result.sanitizedUrl) {
      validUrls.push(result.sanitizedUrl);
    } else {
      invalidUrls.push({
        url,
        error: result.error || '未知錯誤',
      });
    }
  }

  return { validUrls, invalidUrls };
}

/**
 * 檢查 URL 是否為 HKTVmall 商品頁面
 * @param url URL
 * @returns 是否為商品頁面
 */
export function isHKTVProductURL(url: string): boolean {
  const validation = validateScraperURL(url);
  if (!validation.isValid || !validation.sanitizedUrl) {
    return false;
  }

  try {
    const parsedUrl = new URL(validation.sanitizedUrl);
    // HKTVmall 商品頁面路徑格式: /p/H*_*
    return /^\/p\/H\d+_/.test(parsedUrl.pathname);
  } catch {
    return false;
  }
}

/**
 * 檢查 URL 是否為 HKTVmall 搜尋頁面
 * @param url URL
 * @returns 是否為搜尋頁面
 */
export function isHKTVSearchURL(url: string): boolean {
  const validation = validateScraperURL(url);
  if (!validation.isValid || !validation.sanitizedUrl) {
    return false;
  }

  try {
    const parsedUrl = new URL(validation.sanitizedUrl);
    // HKTVmall 搜尋頁面路徑格式: /search 或 /search?q=...
    return parsedUrl.pathname === '/search' || parsedUrl.pathname.startsWith('/search/');
  } catch {
    return false;
  }
}
