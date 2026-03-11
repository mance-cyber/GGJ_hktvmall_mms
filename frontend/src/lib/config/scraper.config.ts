// ==================== 统一爬虫Configuration ====================
// 用途: 根据环境自动切换 Clawdbot (本地) 或 Firecrawl (云端)
// 架构: 开发环境 → Clawdbot | 生产环境 → Firecrawl
// ✅ FIXED: CRIT-4 - API Key No longer stored in config object, only read from env vars

export type ScraperType = 'clawdbot' | 'firecrawl';

export interface ScraperConfig {
  type: ScraperType;
  endpoint: string;
  // ❌ 移除: apiKey?: string;  (不再存儲 API Key)
  timeout: number;
  retryAttempts: number;
  rateLimitPerMinute: number;
}

// ==================== Security的 API Key Management ====================

/**
 * Securely fetch API Key (read from env vars only when needed, no caching)
 * @returns API Key 或 undefined
 */
export function getAPIKeySafe(): string | undefined {
  // 🔒 Read from env vars on each call, avoid storing sensitive info in memory
  return process.env.FIRECRAWL_API_KEY;
}

/**
 * Verify if API Key is configured
 * @returns whether已Configuration
 */
export function hasAPIKey(): boolean {
  return !!process.env.FIRECRAWL_API_KEY;
}

/**
 * Get masked API Key version (for logging)
 * @returns 遮蔽後的 API Key（例如：sk_***********1234）
 */
export function getMaskedAPIKey(): string {
  const apiKey = getAPIKeySafe();
  if (!apiKey) return '未Configuration';
  
  // 只Display前 3 個和後 4 個字符
  if (apiKey.length < 8) return '***';
  return `${apiKey.substring(0, 3)}***${apiKey.substring(apiKey.length - 4)}`;
}

// ==================== 环境Configuration ====================

const SCRAPER_CONFIGS: Record<string, ScraperConfig> = {
  // 开发环境: 使用本地 Clawdbot (免费, 完全自定义)
  development: {
    type: 'clawdbot',
    endpoint: process.env.CLAWDBOT_GATEWAY_URL || 'ws://127.0.0.1:18789',
    timeout: 60000, // 60 秒
    retryAttempts: 3,
    rateLimitPerMinute: 30,
  },

  // 测试环境: 可Configuration使用哪个服务
  test: {
    type: (process.env.SCRAPER_TYPE as ScraperType) || 'clawdbot',
    endpoint:
      process.env.SCRAPER_ENDPOINT ||
      process.env.CLAWDBOT_GATEWAY_URL ||
      'ws://127.0.0.1:18789',
    timeout: 60000,
    retryAttempts: 3,
    rateLimitPerMinute: 30,
  },

  // 生产环境: 使用 Firecrawl (稳定, 云端服务)
  production: {
    type: 'firecrawl',
    endpoint: process.env.FIRECRAWL_API_URL || 'https://api.firecrawl.dev/v1',
    // ❌ 移除: apiKey: process.env.FIRECRAWL_API_KEY,
    timeout: 120000, // 120 秒 (生产环境更保守)
    retryAttempts: 5, // 生产环境更多重试
    rateLimitPerMinute: 60, // Firecrawl Support更高并发
  },
};

// ==================== 获取当前Configuration ====================

/**
 * 根据当前环境自动选择爬虫Configuration
 * @returns 当前环境的爬虫Configuration（不Include API Key）
 */
export function getScraperConfig(): ScraperConfig {
  const env = process.env.NODE_ENV || 'development';
  const config = SCRAPER_CONFIGS[env];

  if (!config) {
    console.warn(`⚠️ 未找到环境 "${env}" 的Configuration，使用开发环境Configuration`);
    return SCRAPER_CONFIGS.development;
  }

  // 🔒 Validate生產Environment必需的 API Key（但不Back它）
  if (config.type === 'firecrawl' && !hasAPIKey()) {
    throw new Error(
      '❌ 生产环境NeedConfiguration FIRECRAWL_API_KEY 环境变量'
    );
  }

  console.log(`🔧 爬虫Configuration: ${config.type} (${env} 环境)`);
  return config;
}

// ==================== 手动覆盖Configuration ====================

/**
 * 手动指定使用的爬虫类型 (用于测试或特殊场景)
 * @param type 爬虫类型
 * @returns 指定类型的爬虫Configuration
 */
export function forceScraperType(type: ScraperType): ScraperConfig {
  const baseConfig =
    type === 'clawdbot'
      ? SCRAPER_CONFIGS.development
      : SCRAPER_CONFIGS.production;

  console.log(`🔧 强制使用爬虫: ${type}`);
  return baseConfig;
}

// ==================== Configuration验证 ====================

/**
 * 验证Configurationwhether完整
 * @param config 爬虫Configuration
 * @returns whetherValid
 */
export function validateScraperConfig(config: ScraperConfig): boolean {
  // 检查必填字段
  if (!config.type || !config.endpoint) {
    console.error('❌ 爬虫Configuration缺少必填字段: type, endpoint');
    return false;
  }

  // 🔒 Check required Firecrawl API Key (from env vars)
  if (config.type === 'firecrawl' && !hasAPIKey()) {
    console.error('❌ Firecrawl Requires FIRECRAWL_API_KEY environment variable');
    return false;
  }

  // 检查 Clawdbot WebSocket 连接
  if (config.type === 'clawdbot' && !config.endpoint.startsWith('ws')) {
    console.error('❌ Clawdbot Need WebSocket 连接 (ws:// 或 wss://)');
    return false;
  }

  return true;
}

// ==================== Configuration信息输出（SecurityVersion）====================

/**
 * 打印当前Configuration信息 (用于调试) - 不Display完整 API Key
 */
export function printScraperConfig(): void {
  const config = getScraperConfig();

  console.log('\n==================== 爬虫Configuration ====================');
  console.log(`环境: ${process.env.NODE_ENV || 'development'}`);
  console.log(`类型: ${config.type}`);
  console.log(`端点: ${config.endpoint}`);
  console.log(`API Key: ${getMaskedAPIKey()}`); // 🔒 Display遮蔽Version
  console.log(`超时: ${config.timeout}ms`);
  console.log(`重试: ${config.retryAttempts} 次`);
  console.log(`速率: ${config.rateLimitPerMinute} req/min`);
  console.log('===============================================\n');
}

// ==================== Utility functions for secure API Key usage ====================

/**
 * 使用 API Key 執行Operation（Ensure API Key 不會洩漏到Log）
 * @param operation Need API Key 的Operation
 * @returns OperationResult
 */
export async function withAPIKey<T>(
  operation: (apiKey: string) => Promise<T>
): Promise<T> {
  const apiKey = getAPIKeySafe();
  
  if (!apiKey) {
    throw new Error('API Key 未Configuration');
  }

  try {
    return await operation(apiKey);
  } catch (error) {
    // 🔒 EnsureError信息中不Include API Key
    if (error instanceof Error && error.message.includes(apiKey)) {
      throw new Error(error.message.replace(apiKey, getMaskedAPIKey()));
    }
    throw error;
  }
}
