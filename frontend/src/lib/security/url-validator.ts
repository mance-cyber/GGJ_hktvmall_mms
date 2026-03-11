// ==================== URL SecurityValidate工具 ====================
// 用途: Prevent SSRF Attack，Ensure只抓取Allow的域名
// Security級別: CRITICAL

/**
 * Allow的域名白名單
 * 只Allow抓取 HKTVmall 官方域名
 */
const ALLOWED_DOMAINS = [
  'hktvmall.com',
  'www.hktvmall.com',
  'm.hktvmall.com',
] as const;

/**
 * Block訪問的內部網絡Range（Prevent SSRF）
 */
const BLOCKED_IP_RANGES = [
  /^127\./,           // localhost
  /^10\./,            // 私有網絡 10.0.0.0/8
  /^172\.(1[6-9]|2[0-9]|3[01])\./,  // 私有網絡 172.16.0.0/12
  /^192\.168\./,      // 私有網絡 192.168.0.0/16
  /^169\.254\./,      // Link-local
  /^0\./,             // Invalid地址
  /^224\./,           // 組播地址
  /^255\./,           // 廣播地址
];

/**
 * URL ValidateResult
 */
export interface URLValidationResult {
  isValid: boolean;
  error?: string;
  sanitizedUrl?: string;
}

/**
 * Validate URL whetherSecurity可抓取
 * @param url 待Validate的 URL
 * @returns ValidateResult
 */
export function validateScraperURL(url: string): URLValidationResult {
  try {
    // 1. 基本FormatValidate
    if (!url || typeof url !== 'string') {
      return {
        isValid: false,
        error: 'URL 不能為空',
      };
    }

    // 2. Parse URL
    let parsedUrl: URL;
    try {
      parsedUrl = new URL(url);
    } catch {
      return {
        isValid: false,
        error: 'URL FormatInvalid',
      };
    }

    // 3. 協議Validate - 只Allow HTTPS
    if (parsedUrl.protocol !== 'https:') {
      return {
        isValid: false,
        error: 'Only allow HTTPS protocol',
      };
    }

    // 4. 域名白名單Validate
    const hostname = parsedUrl.hostname.toLowerCase();
    const isAllowedDomain = ALLOWED_DOMAINS.some(
      (domain) => hostname === domain || hostname.endsWith(`.${domain}`)
    );

    if (!isAllowedDomain) {
      return {
        isValid: false,
        error: `域名 "${hostname}" 不在白名單中，只Allow ${ALLOWED_DOMAINS.join(', ')}`,
      };
    }

    // 5. IP 地址檢測（Prevent直接使用 IP 繞過域名Check）
    if (/^\d+\.\d+\.\d+\.\d+$/.test(hostname)) {
      // Checkwhether為內部 IP
      const isBlocked = BLOCKED_IP_RANGES.some((pattern) => pattern.test(hostname));
      if (isBlocked) {
        return {
          isValid: false,
          error: '不Allow訪問內部網絡地址',
        };
      }
    }

    // 6. 路徑Validate - Prevent目錄Iterate
    if (parsedUrl.pathname.includes('..')) {
      return {
        isValid: false,
        error: '路徑Include非法字符',
      };
    }

    // 7. 長度Limit
    if (url.length > 2048) {
      return {
        isValid: false,
        error: 'URL 長度超過Limit（最多 2048 字符）',
      };
    }

    // Validation passed, return cleaned URL
    return {
      isValid: true,
      sanitizedUrl: parsedUrl.toString(),
    };
  } catch (error) {
    return {
      isValid: false,
      error: error instanceof Error ? error.message : 'URL ValidateFailed',
    };
  }
}

/**
 * 批量Validate URL
 * @param urls URL List
 * @returns ValidateResultList
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
        error: result.error || 'UnknownError',
      });
    }
  }

  return { validUrls, invalidUrls };
}

/**
 * Check if URL is HKTVmall product page
 * @param url URL
 * @returns whether為productspage
 */
export function isHKTVProductURL(url: string): boolean {
  const validation = validateScraperURL(url);
  if (!validation.isValid || !validation.sanitizedUrl) {
    return false;
  }

  try {
    const parsedUrl = new URL(validation.sanitizedUrl);
    // HKTVmall productspage路徑Format: /p/H*_*
    return /^\/p\/H\d+_/.test(parsedUrl.pathname);
  } catch {
    return false;
  }
}

/**
 * Check URL whether為 HKTVmall Searchpage
 * @param url URL
 * @returns whether為Searchpage
 */
export function isHKTVSearchURL(url: string): boolean {
  const validation = validateScraperURL(url);
  if (!validation.isValid || !validation.sanitizedUrl) {
    return false;
  }

  try {
    const parsedUrl = new URL(validation.sanitizedUrl);
    // HKTVmall Searchpage路徑Format: /search 或 /search?q=...
    return parsedUrl.pathname === '/search' || parsedUrl.pathname.startsWith('/search/');
  } catch {
    return false;
  }
}
