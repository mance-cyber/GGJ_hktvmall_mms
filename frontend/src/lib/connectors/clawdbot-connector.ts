// ==================== GoGoJap Clawdbot Connection器 ====================
// 用途: Connect to local clawdbot WebSocket Gateway for browser automation抓取任務
// 架構: GoGoJap Backend ←→ ClawdbotConnector ←→ Clawdbot Gateway ←→ Browser Pool

import WebSocket from 'ws';

// ==================== Type definitions ====================

export interface ClawdbotConfig {
  gatewayUrl: string;           // WebSocket Gateway URL
  apiKey?: string;              // API Key (如果Need)
  timeout: number;              // 任務TimeoutTime (毫秒)
  retryAttempts: number;        // FailedRetry次數
  rateLimitPerMinute: number;   // Max requests per minute
}

export interface ScrapeTask {
  id: string;
  type: 'product' | 'seo-rank' | 'competitor' | 'custom';
  url: string;
  config?: ScrapeTaskConfig;
}

export interface ScrapeTaskConfig {
  waitForSelector?: string;      // Waiting特定元素Loading
  actions?: BrowserAction[];     // Browser action sequence
  extractors?: DataExtractor[];  // Data提取規則
  screenshot?: boolean;          // whether截圖
  useProxy?: boolean;            // whether使用代理
}

export interface BrowserAction {
  type: 'wait' | 'click' | 'scroll' | 'input' | 'screenshot';
  selector?: string;
  value?: string | number;
  delay?: number;
}

export interface DataExtractor {
  field: string;
  selector: string;
  attribute?: string;  // 提取屬性 (href, src, etc.)
  multiple?: boolean;  // whether提取多個元素
  transform?: 'number' | 'trim' | 'lowercase';
}

export interface ScrapeResult {
  success: boolean;
  taskId: string;
  url: string;
  data: Record<string, any> | null;
  error: string | null;
  durationMs: number;
  scrapedAt: string;
  screenshot?: string;  // Base64 encoded screenshot
}

// ==================== Clawdbot Connection器 ====================

export class ClawdbotConnector {
  private config: ClawdbotConfig;
  private ws: WebSocket | null = null;
  private connected: boolean = false;
  private taskQueue: Map<string, (result: ScrapeResult) => void> = new Map();
  private requestCount: number = 0;
  private requestWindow: Date = new Date();

  constructor(config: Partial<ClawdbotConfig> = {}) {
    this.config = {
      gatewayUrl: config.gatewayUrl || 'ws://127.0.0.1:18789',
      timeout: config.timeout || 60000,  // 60 秒
      retryAttempts: config.retryAttempts || 3,
      rateLimitPerMinute: config.rateLimitPerMinute || 30,
      ...config,
    };
  }

  // ==================== ConnectionManagement ====================

  /**
   * Connection到 Clawdbot WebSocket Gateway
   */
  async connect(): Promise<void> {
    if (this.connected && this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.config.gatewayUrl);

        this.ws.on('open', () => {
          console.log('✅ 已Connection到 Clawdbot Gateway:', this.config.gatewayUrl);
          this.connected = true;
          resolve();
        });

        this.ws.on('message', (data: WebSocket.Data) => {
          this.handleMessage(data.toString());
        });

        this.ws.on('error', (error) => {
          console.error('❌ Clawdbot WebSocket Error:', error);
          this.connected = false;
          reject(error);
        });

        this.ws.on('close', () => {
          console.log('🔌 Clawdbot Connection已Close');
          this.connected = false;
        });

        // ConnectionTimeout
        setTimeout(() => {
          if (!this.connected) {
            reject(new Error('Clawdbot ConnectionTimeout'));
          }
        }, 10000);
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * DisconnectedConnection
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.connected = false;
    }
  }

  /**
   * Processing WebSocket 消息
   */
  private handleMessage(message: string): void {
    try {
      const response = JSON.parse(message);

      if (response.type === 'task_result') {
        const resolver = this.taskQueue.get(response.taskId);
        if (resolver) {
          resolver(response.result);
          this.taskQueue.delete(response.taskId);
        }
      }
    } catch (error) {
      console.error('Parse Clawdbot 消息Failed:', error);
    }
  }

  // ==================== 速率Limit ====================

  /**
   * Check速率Limit
   */
  private async checkRateLimit(): Promise<void> {
    const now = new Date();
    const timeElapsed = now.getTime() - this.requestWindow.getTime();

    // Reset計數器 (每minutes)
    if (timeElapsed > 60000) {
      this.requestCount = 0;
      this.requestWindow = now;
    }

    // Checkwhether超過Limit
    if (this.requestCount >= this.config.rateLimitPerMinute) {
      const waitTime = 60000 - timeElapsed;
      console.log(`⏳ 達到速率Limit，Waiting ${waitTime}ms`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
      this.requestCount = 0;
      this.requestWindow = new Date();
    }

    this.requestCount++;
  }

  // ==================== 核心抓取Method ====================

  /**
   * 執行抓取任務
   */
  async scrape(task: ScrapeTask): Promise<ScrapeResult> {
    await this.checkRateLimit();

    if (!this.connected) {
      await this.connect();
    }

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.taskQueue.delete(task.id);
        reject(new Error('抓取任務Timeout'));
      }, this.config.timeout);

      this.taskQueue.set(task.id, (result: ScrapeResult) => {
        clearTimeout(timeout);
        resolve(result);
      });

      // 發送任務到 Clawdbot
      const message = JSON.stringify({
        type: 'scrape_task',
        task,
      });

      this.ws?.send(message);
    });
  }

  // ==================== HKTVmall 專用Method ====================

  /**
   * 抓取 HKTVmall productsInformation
   */
  async scrapeHKTVProduct(productUrl: string): Promise<ScrapeResult> {
    const taskId = this.generateTaskId();

    const task: ScrapeTask = {
      id: taskId,
      type: 'product',
      url: productUrl,
      config: {
        waitForSelector: '.product-details',
        actions: [
          { type: 'wait', delay: 2000 },
          { type: 'scroll', value: 500 },
          { type: 'click', selector: '.show-more-btn' },
        ],
        extractors: [
          { field: 'name', selector: '.product-title', transform: 'trim' },
          { field: 'price', selector: '.current-price', transform: 'number' },
          { field: 'originalPrice', selector: '.original-price', transform: 'number' },
          { field: 'discountPercent', selector: '.discount-badge' },
          { field: 'stockStatus', selector: '.stock-status' },
          { field: 'imageUrl', selector: '.product-image img', attribute: 'src' },
          { field: 'sku', selector: '.product-sku' },
          { field: 'brand', selector: '.brand-name' },
          { field: 'rating', selector: '.rating-score', transform: 'number' },
          { field: 'reviewCount', selector: '.review-count', transform: 'number' },
          { field: 'promotionText', selector: '.promotion-text' },
          { field: 'description', selector: '.product-description' },
        ],
        screenshot: true,
      },
    };

    return this.scrape(task);
  }

  /**
   * 抓取 HKTVmall SearchRanking
   */
  async scrapeHKTVSearchRank(keyword: string, targetUrl: string): Promise<ScrapeResult> {
    const taskId = this.generateTaskId();
    const searchUrl = `https://www.hktvmall.com/search?q=${encodeURIComponent(keyword)}`;

    const task: ScrapeTask = {
      id: taskId,
      type: 'seo-rank',
      url: searchUrl,
      config: {
        waitForSelector: '.search-results',
        actions: [
          { type: 'wait', delay: 3000 },
          { type: 'scroll', value: 2000 },  // Loading更多Result
        ],
        extractors: [
          {
            field: 'searchResults',
            selector: '.product-item',
            multiple: true,
          },
        ],
      },
    };

    const result = await this.scrape(task);

    // 後Processing: Find target URL ranking
    if (result.success && result.data?.searchResults) {
      const products = result.data.searchResults as any[];
      const targetIndex = products.findIndex(p => p.url === targetUrl);

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

  /**
   * 批量抓取products
   */
  async scrapeBatch(urls: string[]): Promise<ScrapeResult[]> {
    const results: ScrapeResult[] = [];

    for (const url of urls) {
      try {
        const result = await this.scrapeHKTVProduct(url);
        results.push(result);

        // 添加隨機延遲，Avoid被檢測
        await this.randomDelay(2000, 5000);
      } catch (error) {
        console.error(`抓取Failed: ${url}`, error);
        results.push({
          success: false,
          taskId: this.generateTaskId(),
          url,
          data: null,
          error: error instanceof Error ? error.message : 'UnknownError',
          durationMs: 0,
          scrapedAt: new Date().toISOString(),
        });
      }
    }

    return results;
  }

  // ==================== 工具Method ====================

  /**
   * Generate任務 ID
   */
  private generateTaskId(): string {
    return `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * 隨機延遲
   */
  private async randomDelay(min: number, max: number): Promise<void> {
    const delay = Math.floor(Math.random() * (max - min + 1)) + min;
    await new Promise(resolve => setTimeout(resolve, delay));
  }

  /**
   * 健康Check
   */
  async healthCheck(): Promise<boolean> {
    try {
      if (!this.connected) {
        await this.connect();
      }
      return this.ws?.readyState === WebSocket.OPEN;
    } catch {
      return false;
    }
  }
}

// ==================== 單例Export ====================

let connectorInstance: ClawdbotConnector | null = null;

export function getClawdbotConnector(config?: Partial<ClawdbotConfig>): ClawdbotConnector {
  if (!connectorInstance) {
    connectorInstance = new ClawdbotConnector(config);
  }
  return connectorInstance;
}
