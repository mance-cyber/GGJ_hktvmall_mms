// ==================== 统一爬虫接口 ====================
// 用途: 提供统一的 API，自动路由到 Clawdbot 或 Firecrawl
// 架构: UnifiedScraper → ClawdbotConnector / FirecrawlConnector

import {
  ClawdbotConnector,
  ScrapeTask,
  ScrapeResult,
} from './clawdbot-connector';
import { getScraperConfig, ScraperType, getAPIKeySafe } from '../config/scraper.config';

// ==================== 统一任务接口 ====================

export interface UnifiedScrapeTask {
  url: string;
  type?: 'product' | 'seo-rank' | 'competitor' | 'custom';
  config?: {
    waitForSelector?: string;
    actions?: any[];
    extractors?: any[];
    screenshot?: boolean;
    useProxy?: boolean;
  };
}

export interface UnifiedScrapeResult {
  success: boolean;
  url: string;
  data: Record<string, any> | null;
  error: string | null;
  durationMs: number;
  scrapedAt: string;
  screenshot?: string;
  metadata?: {
    scraper: ScraperType;
    taskId: string;
    retries?: number;
  };
}

// ==================== Firecrawl Connector ====================

class FirecrawlConnector {
  private apiUrl: string;
  private apiKey: string;
  private timeout: number;
  private retryAttempts: number;

  constructor(config: {
    apiUrl: string;
    apiKey: string;
    timeout: number;
    retryAttempts: number;
  }) {
    this.apiUrl = config.apiUrl;
    this.apiKey = config.apiKey;
    this.timeout = config.timeout;
    this.retryAttempts = config.retryAttempts;
  }

  /**
   * 使用 Firecrawl 抓取页面
   */
  async scrape(task: UnifiedScrapeTask): Promise<UnifiedScrapeResult> {
    const startTime = Date.now();
    const taskId = this.generateTaskId();

    let lastError: Error | null = null;
    let retries = 0;

    // 重试机制
    for (let attempt = 0; attempt < this.retryAttempts; attempt++) {
      try {
        const response = await fetch(`${this.apiUrl}/scrape`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${this.apiKey}`,
          },
          body: JSON.stringify({
            url: task.url,
            formats: ['html', 'markdown'],
            waitFor: task.config?.waitForSelector ? 5000 : 0,
            screenshot: task.config?.screenshot || false,
            timeout: this.timeout,
          }),
          signal: AbortSignal.timeout(this.timeout),
        });

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(`Firecrawl API 错误 (${response.status}): ${errorText}`);
        }

        const result = await response.json();

        // 成功返回
        return {
          success: true,
          url: task.url,
          data: this.transformFirecrawlData(result.data),
          error: null,
          durationMs: Date.now() - startTime,
          scrapedAt: new Date().toISOString(),
          screenshot: result.data?.screenshot,
          metadata: {
            scraper: 'firecrawl',
            taskId,
            retries,
          },
        };
      } catch (error) {
        lastError = error as Error;
        retries++;
        console.error(
          `❌ Firecrawl 抓取失败 (尝试 ${attempt + 1}/${this.retryAttempts}):`,
          error
        );

        // 最后一次尝试，直接抛出错误
        if (attempt === this.retryAttempts - 1) {
          break;
        }

        // 等待后重试 (指数退避)
        await new Promise((resolve) =>
          setTimeout(resolve, Math.pow(2, attempt) * 1000)
        );
      }
    }

    // 所有重试都失败
    return {
      success: false,
      url: task.url,
      data: null,
      error: lastError?.message || '未知错误',
      durationMs: Date.now() - startTime,
      scrapedAt: new Date().toISOString(),
      metadata: {
        scraper: 'firecrawl',
        taskId,
        retries,
      },
    };
  }

  /**
   * 转换 Firecrawl 数据格式为统一格式
   */
  private transformFirecrawlData(data: any): Record<string, any> {
    return {
      html: data.html,
      markdown: data.markdown,
      metadata: data.metadata,
      links: data.links,
      // 提取常见字段
      title: data.metadata?.title,
      description: data.metadata?.description,
      ogImage: data.metadata?.ogImage,
    };
  }

  private generateTaskId(): string {
    return `firecrawl_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// ==================== 统一爬虫类 ====================

export class UnifiedScraper {
  private config = getScraperConfig();
  private clawdbotConnector: ClawdbotConnector | null = null;
  private firecrawlConnector: FirecrawlConnector | null = null;

  constructor() {
    this.initializeConnector();
  }

  /**
   * 根据配置初始化对应的连接器
   */
  private initializeConnector(): void {
    if (this.config.type === 'clawdbot') {
      console.log('🤖 初始化 Clawdbot 连接器');
      this.clawdbotConnector = new ClawdbotConnector({
        gatewayUrl: this.config.endpoint,
        timeout: this.config.timeout,
        retryAttempts: this.config.retryAttempts,
        rateLimitPerMinute: this.config.rateLimitPerMinute,
      });
    } else {
      console.log('🔥 初始化 Firecrawl 连接器');
      const apiKey = getAPIKeySafe();
      if (!apiKey) {
        throw new Error('FIRECRAWL_API_KEY 環境變量未配置');
      }
      this.firecrawlConnector = new FirecrawlConnector({
        apiUrl: this.config.endpoint,
        apiKey: apiKey,
        timeout: this.config.timeout,
        retryAttempts: this.config.retryAttempts,
      });
    }
  }

  // ==================== 核心方法 ====================

  /**
   * 抓取单个页面
   */
  async scrape(task: UnifiedScrapeTask): Promise<UnifiedScrapeResult> {
    if (this.config.type === 'clawdbot' && this.clawdbotConnector) {
      return this.scrapeWithClawdbot(task);
    } else if (this.config.type === 'firecrawl' && this.firecrawlConnector) {
      return this.firecrawlConnector.scrape(task);
    } else {
      throw new Error('❌ 爬虫连接器未初始化');
    }
  }

  /**
   * 使用 Clawdbot 抓取
   */
  private async scrapeWithClawdbot(
    task: UnifiedScrapeTask
  ): Promise<UnifiedScrapeResult> {
    const clawdbotTask: ScrapeTask = {
      id: `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: task.type || 'custom',
      url: task.url,
      config: task.config,
    };

    const result = await this.clawdbotConnector!.scrape(clawdbotTask);

    return {
      success: result.success,
      url: result.url,
      data: result.data,
      error: result.error,
      durationMs: result.durationMs,
      scrapedAt: result.scrapedAt,
      screenshot: result.screenshot,
      metadata: {
        scraper: 'clawdbot',
        taskId: result.taskId,
      },
    };
  }

  /**
   * 批量抓取
   */
  async scrapeBatch(urls: string[]): Promise<UnifiedScrapeResult[]> {
    const results: UnifiedScrapeResult[] = [];

    for (const url of urls) {
      try {
        const result = await this.scrape({ url });
        results.push(result);

        // 随机延迟，避免触发速率限制
        await this.randomDelay(1000, 3000);
      } catch (error) {
        console.error(`❌ 批量抓取失败: ${url}`, error);
        results.push({
          success: false,
          url,
          data: null,
          error: error instanceof Error ? error.message : '未知错误',
          durationMs: 0,
          scrapedAt: new Date().toISOString(),
          metadata: {
            scraper: this.config.type,
            taskId: `batch_${Date.now()}`,
          },
        });
      }
    }

    return results;
  }

  // ==================== HKTVmall 专用方法 ====================

  /**
   * 抓取 HKTVmall 商品
   */
  async scrapeHKTVProduct(productUrl: string): Promise<UnifiedScrapeResult> {
    return this.scrape({
      url: productUrl,
      type: 'product',
      config: {
        waitForSelector: '.product-details',
        actions: [
          { type: 'wait', delay: 2000 },
          { type: 'scroll', value: 500 },
        ],
        extractors: [
          { field: 'name', selector: '.product-title', transform: 'trim' },
          { field: 'price', selector: '.current-price', transform: 'number' },
          {
            field: 'originalPrice',
            selector: '.original-price',
            transform: 'number',
          },
          { field: 'discountPercent', selector: '.discount-badge' },
          { field: 'stockStatus', selector: '.stock-status' },
          {
            field: 'imageUrl',
            selector: '.product-image img',
            attribute: 'src',
          },
          { field: 'rating', selector: '.rating-score', transform: 'number' },
          {
            field: 'reviewCount',
            selector: '.review-count',
            transform: 'number',
          },
        ],
        screenshot: true,
      },
    });
  }

  /**
   * 抓取 HKTVmall 搜索排名
   */
  async scrapeHKTVSearchRank(
    keyword: string,
    targetUrl: string
  ): Promise<UnifiedScrapeResult> {
    const searchUrl = `https://www.hktvmall.com/search?q=${encodeURIComponent(keyword)}`;

    const result = await this.scrape({
      url: searchUrl,
      type: 'seo-rank',
      config: {
        waitForSelector: '.search-results',
        actions: [
          { type: 'wait', delay: 3000 },
          { type: 'scroll', value: 2000 },
        ],
        extractors: [
          {
            field: 'searchResults',
            selector: '.product-item',
            multiple: true,
          },
        ],
      },
    });

    // 后处理: 计算排名
    if (result.success && result.data?.searchResults) {
      const products = result.data.searchResults as any[];
      const targetIndex = products.findIndex((p) => p.url === targetUrl);

      result.data = {
        keyword,
        targetUrl,
        currentRank: targetIndex >= 0 ? targetIndex + 1 : null,
        totalResults: products.length,
        topCompetitors: products.slice(0, 10),
      };
    }

    return result;
  }

  // ==================== 工具方法 ====================

  /**
   * 健康检查
   */
  async healthCheck(): Promise<boolean> {
    try {
      if (this.config.type === 'clawdbot' && this.clawdbotConnector) {
        return await this.clawdbotConnector.healthCheck();
      } else if (this.config.type === 'firecrawl' && this.firecrawlConnector) {
        // Firecrawl 健康检查: 尝试获取配额
        const apiKey = getAPIKeySafe();
        if (!apiKey) return false;
        const response = await fetch(`${this.config.endpoint}/health`, {
          headers: {
            Authorization: `Bearer ${apiKey}`,
          },
        });
        return response.ok;
      }
      return false;
    } catch {
      return false;
    }
  }

  /**
   * 获取当前使用的爬虫类型
   */
  getScraperType(): ScraperType {
    return this.config.type;
  }

  /**
   * 随机延迟
   */
  private async randomDelay(min: number, max: number): Promise<void> {
    const delay = Math.floor(Math.random() * (max - min + 1)) + min;
    await new Promise((resolve) => setTimeout(resolve, delay));
  }
}

// ==================== 单例导出 ====================

let scraperInstance: UnifiedScraper | null = null;

export function getUnifiedScraper(): UnifiedScraper {
  if (!scraperInstance) {
    scraperInstance = new UnifiedScraper();
  }
  return scraperInstance;
}

// ==================== 便捷方法导出 ====================

/**
 * 快速抓取单个页面
 */
export async function scrapeUrl(url: string): Promise<UnifiedScrapeResult> {
  const scraper = getUnifiedScraper();
  return scraper.scrape({ url });
}

/**
 * 快速抓取 HKTVmall 商品
 */
export async function scrapeHKTVProduct(
  productUrl: string
): Promise<UnifiedScrapeResult> {
  const scraper = getUnifiedScraper();
  return scraper.scrapeHKTVProduct(productUrl);
}

/**
 * 快速抓取搜索排名
 */
export async function scrapeSearchRank(
  keyword: string,
  targetUrl: string
): Promise<UnifiedScrapeResult> {
  const scraper = getUnifiedScraper();
  return scraper.scrapeHKTVSearchRank(keyword, targetUrl);
}
