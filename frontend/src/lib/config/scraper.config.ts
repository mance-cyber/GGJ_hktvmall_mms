// ==================== 统一爬虫配置 ====================
// 用途: 根据环境自动切换 Clawdbot (本地) 或 Firecrawl (云端)
// 架构: 开发环境 → Clawdbot | 生产环境 → Firecrawl
// ✅ FIXED: CRIT-4 - API Key 不再存儲在配置對象中，僅從環境變量讀取

export type ScraperType = 'clawdbot' | 'firecrawl';

export interface ScraperConfig {
  type: ScraperType;
  endpoint: string;
  // ❌ 移除: apiKey?: string;  (不再存儲 API Key)
  timeout: number;
  retryAttempts: number;
  rateLimitPerMinute: number;
}

// ==================== 安全的 API Key 管理 ====================

/**
 * 安全獲取 API Key（僅在需要時從環境變量讀取，不緩存）
 * @returns API Key 或 undefined
 */
export function getAPIKeySafe(): string | undefined {
  // 🔒 每次調用時從環境變量讀取，避免內存中存儲敏感信息
  return process.env.FIRECRAWL_API_KEY;
}

/**
 * 驗證 API Key 是否已配置
 * @returns 是否已配置
 */
export function hasAPIKey(): boolean {
  return !!process.env.FIRECRAWL_API_KEY;
}

/**
 * 獲取 API Key 的遮蔽版本（用於日誌）
 * @returns 遮蔽後的 API Key（例如：sk_***********1234）
 */
export function getMaskedAPIKey(): string {
  const apiKey = getAPIKeySafe();
  if (!apiKey) return '未配置';
  
  // 只顯示前 3 個和後 4 個字符
  if (apiKey.length < 8) return '***';
  return `${apiKey.substring(0, 3)}***${apiKey.substring(apiKey.length - 4)}`;
}

// ==================== 环境配置 ====================

const SCRAPER_CONFIGS: Record<string, ScraperConfig> = {
  // 开发环境: 使用本地 Clawdbot (免费, 完全自定义)
  development: {
    type: 'clawdbot',
    endpoint: process.env.CLAWDBOT_GATEWAY_URL || 'ws://127.0.0.1:18789',
    timeout: 60000, // 60 秒
    retryAttempts: 3,
    rateLimitPerMinute: 30,
  },

  // 测试环境: 可配置使用哪个服务
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
    rateLimitPerMinute: 60, // Firecrawl 支持更高并发
  },
};

// ==================== 获取当前配置 ====================

/**
 * 根据当前环境自动选择爬虫配置
 * @returns 当前环境的爬虫配置（不包含 API Key）
 */
export function getScraperConfig(): ScraperConfig {
  const env = process.env.NODE_ENV || 'development';
  const config = SCRAPER_CONFIGS[env];

  if (!config) {
    console.warn(`⚠️ 未找到环境 "${env}" 的配置，使用开发环境配置`);
    return SCRAPER_CONFIGS.development;
  }

  // 🔒 驗證生產環境必需的 API Key（但不返回它）
  if (config.type === 'firecrawl' && !hasAPIKey()) {
    throw new Error(
      '❌ 生产环境需要配置 FIRECRAWL_API_KEY 环境变量'
    );
  }

  console.log(`🔧 爬虫配置: ${config.type} (${env} 环境)`);
  return config;
}

// ==================== 手动覆盖配置 ====================

/**
 * 手动指定使用的爬虫类型 (用于测试或特殊场景)
 * @param type 爬虫类型
 * @returns 指定类型的爬虫配置
 */
export function forceScraperType(type: ScraperType): ScraperConfig {
  const baseConfig =
    type === 'clawdbot'
      ? SCRAPER_CONFIGS.development
      : SCRAPER_CONFIGS.production;

  console.log(`🔧 强制使用爬虫: ${type}`);
  return baseConfig;
}

// ==================== 配置验证 ====================

/**
 * 验证配置是否完整
 * @param config 爬虫配置
 * @returns 是否有效
 */
export function validateScraperConfig(config: ScraperConfig): boolean {
  // 检查必填字段
  if (!config.type || !config.endpoint) {
    console.error('❌ 爬虫配置缺少必填字段: type, endpoint');
    return false;
  }

  // 🔒 檢查 Firecrawl 必需的 API Key（從環境變量）
  if (config.type === 'firecrawl' && !hasAPIKey()) {
    console.error('❌ Firecrawl 需要配置 FIRECRAWL_API_KEY 環境變量');
    return false;
  }

  // 检查 Clawdbot WebSocket 连接
  if (config.type === 'clawdbot' && !config.endpoint.startsWith('ws')) {
    console.error('❌ Clawdbot 需要 WebSocket 连接 (ws:// 或 wss://)');
    return false;
  }

  return true;
}

// ==================== 配置信息输出（安全版本）====================

/**
 * 打印当前配置信息 (用于调试) - 不顯示完整 API Key
 */
export function printScraperConfig(): void {
  const config = getScraperConfig();

  console.log('\n==================== 爬虫配置 ====================');
  console.log(`环境: ${process.env.NODE_ENV || 'development'}`);
  console.log(`类型: ${config.type}`);
  console.log(`端点: ${config.endpoint}`);
  console.log(`API Key: ${getMaskedAPIKey()}`); // 🔒 顯示遮蔽版本
  console.log(`超时: ${config.timeout}ms`);
  console.log(`重试: ${config.retryAttempts} 次`);
  console.log(`速率: ${config.rateLimitPerMinute} req/min`);
  console.log('===============================================\n');
}

// ==================== 安全使用 API Key 的工具函數 ====================

/**
 * 使用 API Key 執行操作（確保 API Key 不會洩漏到日誌）
 * @param operation 需要 API Key 的操作
 * @returns 操作結果
 */
export async function withAPIKey<T>(
  operation: (apiKey: string) => Promise<T>
): Promise<T> {
  const apiKey = getAPIKeySafe();
  
  if (!apiKey) {
    throw new Error('API Key 未配置');
  }

  try {
    return await operation(apiKey);
  } catch (error) {
    // 🔒 確保錯誤信息中不包含 API Key
    if (error instanceof Error && error.message.includes(apiKey)) {
      throw new Error(error.message.replace(apiKey, getMaskedAPIKey()));
    }
    throw error;
  }
}
