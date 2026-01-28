// ==================== API 認證中間件 ====================
// 用途: 保護 API 端點，防止未授權訪問
// 安全級別: CRITICAL

import { NextRequest, NextResponse } from 'next/server';

/**
 * API 認證結果
 */
export interface AuthResult {
  isAuthorized: boolean;
  error?: string;
  userId?: string;
}

/**
 * 驗證 API Key
 * @param request HTTP 請求
 * @returns 認證結果
 */
export function validateAPIKey(request: NextRequest): AuthResult {
  // 1. 從 header 獲取 API Key
  const apiKey = request.headers.get('x-api-key') || request.headers.get('authorization')?.replace('Bearer ', '');

  if (!apiKey) {
    return {
      isAuthorized: false,
      error: '缺少 API Key（請在 header 中提供 x-api-key 或 Authorization: Bearer <key>）',
    };
  }

  // 2. 驗證 API Key 格式
  if (apiKey.length < 32) {
    return {
      isAuthorized: false,
      error: 'API Key 格式無效',
    };
  }

  // 3. 檢查 API Key 是否有效
  const validApiKeys = getValidAPIKeys();
  
  if (!validApiKeys.includes(apiKey)) {
    return {
      isAuthorized: false,
      error: 'API Key 無效',
    };
  }

  // 4. 認證成功
  return {
    isAuthorized: true,
    userId: getUserIdFromAPIKey(apiKey),
  };
}

/**
 * 獲取有效的 API Keys
 * 從環境變量讀取，支持多個 API Key（用逗號分隔）
 */
function getValidAPIKeys(): string[] {
  const apiKeysEnv = process.env.SCRAPER_API_KEYS || process.env.API_KEYS;
  
  if (!apiKeysEnv) {
    console.error('❌ 未配置 SCRAPER_API_KEYS 環境變量！');
    return [];
  }

  return apiKeysEnv.split(',').map((key) => key.trim()).filter(Boolean);
}

/**
 * 從 API Key 獲取用戶 ID（用於審計日誌）
 */
function getUserIdFromAPIKey(apiKey: string): string {
  // 簡單實現：使用 API Key 的前 8 個字符作為用戶標識
  // 生產環境應該使用數據庫映射
  return apiKey.substring(0, 8);
}

/**
 * 驗證速率限制
 * @param userId 用戶 ID
 * @param limit 每分鐘最大請求數
 * @returns 是否允許請求
 */
export function checkRateLimit(userId: string, limit: number = 60): boolean {
  // TODO: 實現 Redis 或內存速率限制
  // 這裡是簡單示例，生產環境需要使用 Redis
  
  const now = Date.now();
  const key = `ratelimit:${userId}`;
  
  // 簡單內存緩存（注意：多實例部署時需要使用 Redis）
  if (!global.rateLimitCache) {
    global.rateLimitCache = new Map();
  }
  
  const cache = global.rateLimitCache as Map<string, { count: number; resetAt: number }>;
  const record = cache.get(key);
  
  // 重置計數器（每分鐘）
  if (!record || now > record.resetAt) {
    cache.set(key, {
      count: 1,
      resetAt: now + 60000, // 60 秒後重置
    });
    return true;
  }
  
  // 檢查是否超過限制
  if (record.count >= limit) {
    return false;
  }
  
  // 增加計數
  record.count++;
  cache.set(key, record);
  
  return true;
}

/**
 * API 認證中間件（包裝 handler）
 * @param handler API handler
 * @param options 選項
 * @returns 包裝後的 handler
 */
export function withAuth(
  handler: (request: NextRequest, authResult: AuthResult) => Promise<NextResponse>,
  options: {
    rateLimit?: number; // 每分鐘最大請求數
    requireAuth?: boolean; // 是否必須認證（默認 true）
  } = {}
) {
  const { rateLimit = 60, requireAuth = true } = options;

  return async (request: NextRequest): Promise<NextResponse> => {
    // 1. 驗證 API Key
    const authResult = validateAPIKey(request);

    // 2. 如果要求認證但未通過
    if (requireAuth && !authResult.isAuthorized) {
      return NextResponse.json(
        {
          success: false,
          error: authResult.error || '認證失敗',
        },
        { status: 401 }
      );
    }

    // 3. 速率限制檢查
    if (authResult.userId) {
      const isAllowed = checkRateLimit(authResult.userId, rateLimit);
      if (!isAllowed) {
        return NextResponse.json(
          {
            success: false,
            error: `速率限制：每分鐘最多 ${rateLimit} 個請求`,
          },
          { status: 429 }
        );
      }
    }

    // 4. 調用原始 handler
    return handler(request, authResult);
  };
}

/**
 * 記錄 API 訪問日誌
 * @param request HTTP 請求
 * @param authResult 認證結果
 * @param action 操作類型
 * @param metadata 額外元數據
 */
export function logAPIAccess(
  request: NextRequest,
  authResult: AuthResult,
  action: string,
  metadata?: Record<string, any>
) {
  const log = {
    timestamp: new Date().toISOString(),
    userId: authResult.userId || 'anonymous',
    action,
    method: request.method,
    path: new URL(request.url).pathname,
    ip: request.headers.get('x-forwarded-for') || request.headers.get('x-real-ip') || 'unknown',
    userAgent: request.headers.get('user-agent'),
    ...metadata,
  };

  console.log('API Access:', JSON.stringify(log));
  
  // TODO: 生產環境應該寫入日誌文件或發送到日誌服務
}
