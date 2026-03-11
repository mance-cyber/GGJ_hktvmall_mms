// ==================== API Authentication中間items ====================
// 用途: Protect API endpoints, prevent unauthorized access
// Security級別: CRITICAL

import { NextRequest, NextResponse } from 'next/server';

// Extend globalThis types to support rateLimitCache
declare global {
  // eslint-disable-next-line no-var
  var rateLimitCache: Map<string, { count: number; resetAt: number }> | undefined;
}

/**
 * API AuthenticationResult
 */
export interface AuthResult {
  isAuthorized: boolean;
  error?: string;
  userId?: string;
}

/**
 * Validate API Key
 * @param request HTTP Request
 * @returns AuthenticationResult
 */
export function validateAPIKey(request: NextRequest): AuthResult {
  // 1. 從 header Fetch API Key
  const apiKey = request.headers.get('x-api-key') || request.headers.get('authorization')?.replace('Bearer ', '');

  if (!apiKey) {
    return {
      isAuthorized: false,
      error: 'Missing API Key (please provide x-api-key in header or Authorization: Bearer <key>）',
    };
  }

  // 2. Validate API Key format
  if (apiKey.length < 32) {
    return {
      isAuthorized: false,
      error: 'API Key FormatInvalid',
    };
  }

  // 3. Check API Key whetherValid
  const validApiKeys = getValidAPIKeys();
  
  if (!validApiKeys.includes(apiKey)) {
    return {
      isAuthorized: false,
      error: 'API Key Invalid',
    };
  }

  // 4. AuthenticationSuccess
  return {
    isAuthorized: true,
    userId: getUserIdFromAPIKey(apiKey),
  };
}

/**
 * FetchValid的 API Keys
 * 從EnvironmentVariable讀取，Support多個 API Key（用逗號分隔）
 */
function getValidAPIKeys(): string[] {
  const apiKeysEnv = process.env.SCRAPER_API_KEYS || process.env.API_KEYS;
  
  if (!apiKeysEnv) {
    console.error('❌ 未Configuration SCRAPER_API_KEYS EnvironmentVariable！');
    return [];
  }

  return apiKeysEnv.split(',').map((key) => key.trim()).filter(Boolean);
}

/**
 * 從 API Key Fetch用戶 ID（用於審計Log）
 */
function getUserIdFromAPIKey(apiKey: string): string {
  // 簡單實現：使用 API Key 的前 8 個字符作為用戶標識
  // 生產Environment應該使用Data庫Map
  return apiKey.substring(0, 8);
}

/**
 * Validate速率Limit
 * @param userId 用戶 ID
 * @param limit Max requests per minute
 * @returns whetherAllowRequest
 */
export function checkRateLimit(userId: string, limit: number = 60): boolean {
  // TODO: Implement Redis or memory rate limit
  // This is a simple example, production requires Redis
  
  const now = Date.now();
  const key = `ratelimit:${userId}`;
  
  // Simple memory cache (note: multi-instance deployments need Redis)
  if (!global.rateLimitCache) {
    global.rateLimitCache = new Map();
  }
  
  const cache = global.rateLimitCache as Map<string, { count: number; resetAt: number }>;
  const record = cache.get(key);
  
  // Reset counter (per minute)
  if (!record || now > record.resetAt) {
    cache.set(key, {
      count: 1,
      resetAt: now + 60000, // 60 秒後Reset
    });
    return true;
  }
  
  // Checkwhether超過Limit
  if (record.count >= limit) {
    return false;
  }
  
  // 增加計數
  record.count++;
  cache.set(key, record);
  
  return true;
}

/**
 * API Auth middleware (wrapping handler)
 * @param handler API handler
 * @param options Option
 * @returns 包裝後的 handler
 */
export function withAuth(
  handler: (request: NextRequest, authResult: AuthResult) => Promise<NextResponse>,
  options: {
    rateLimit?: number; // Max requests per minute
    requireAuth?: boolean; // whetherRequires authentication (default true)
  } = {}
) {
  const { rateLimit = 60, requireAuth = true } = options;

  return async (request: NextRequest): Promise<NextResponse> => {
    // 1. Validate API Key
    const authResult = validateAPIKey(request);

    // 2. 如果要求Authentication但未通過
    if (requireAuth && !authResult.isAuthorized) {
      return NextResponse.json(
        {
          success: false,
          error: authResult.error || 'AuthenticationFailed',
        },
        { status: 401 }
      );
    }

    // 3. 速率LimitCheck
    if (authResult.userId) {
      const isAllowed = checkRateLimit(authResult.userId, rateLimit);
      if (!isAllowed) {
        return NextResponse.json(
          {
            success: false,
            error: `速率Limit：每minutes最多 ${rateLimit} 個Request`,
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
 * Record API 訪問Log
 * @param request HTTP Request
 * @param authResult AuthenticationResult
 * @param action OperationType
 * @param metadata 額外元Data
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
  
  // TODO: 生產Environment應該寫入Log文items或發送到Log服務
}
