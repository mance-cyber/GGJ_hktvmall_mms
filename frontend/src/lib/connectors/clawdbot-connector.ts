// ==================== GoGoJap Clawdbot 連接器 ====================
// 用途: 連接到本地 clawdbot WebSocket Gateway，執行瀏覽器自動化抓取任務
// 架構: GoGoJap Backend ←→ ClawdbotConnector ←→ Clawdbot Gateway ←→ Browser Pool

import WebSocket from 'ws';

// ==================== 類型定義 ====================

export interface ClawdbotConfig {
  gatewayUrl: string;           // WebSocket Gateway URL
  apiKey?: string;              // API Key (如果需要)
  timeout: number;              // 任務超時時間 (毫秒)
  retryAttempts: number;        // 失敗重試次數
  rateLimitPerMinute: number;   // 每分鐘最大請求數
}

export interface ScrapeTask {
  id: string;
  type: 'product' | 'seo-rank' | 'competitor' | 'custom';
  url: string;
  config?: ScrapeTaskConfig;
}

export interface ScrapeTaskConfig {
  waitForSelector?: string;      // 等待特定元素加載
  actions?: BrowserAction[];     // 瀏覽器操作序列
  extractors?: DataExtractor[];  // 數據提取規則
  screenshot?: boolean;          // 是否截圖
  useProxy?: boolean;            // 是否使用代理
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
  multiple?: boolean;  // 是否提取多個元素
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

// ==================== Clawdbot 連接器 ====================

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

  // ==================== 連接管理 ====================

  /**
   * 連接到 Clawdbot WebSocket Gateway
   */
  async connect(): Promise<void> {
    if (this.connected && this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.config.gatewayUrl);

        this.ws.on('open', () => {
          console.log('✅ 已連接到 Clawdbot Gateway:', this.config.gatewayUrl);
          this.connected = true;
          resolve();
        });

        this.ws.on('message', (data: WebSocket.Data) => {
          this.handleMessage(data.toString());
        });

        this.ws.on('error', (error) => {
          console.error('❌ Clawdbot WebSocket 錯誤:', error);
          this.connected = false;
          reject(error);
        });

        this.ws.on('close', () => {
          console.log('🔌 Clawdbot 連接已關閉');
          this.connected = false;
        });

        // 連接超時
        setTimeout(() => {
          if (!this.connected) {
            reject(new Error('Clawdbot 連接超時'));
          }
        }, 10000);
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * 斷開連接
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.connected = false;
    }
  }

  /**
   * 處理 WebSocket 消息
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
      console.error('解析 Clawdbot 消息失敗:', error);
    }
  }

  // ==================== 速率限制 ====================

  /**
   * 檢查速率限制
   */
  private async checkRateLimit(): Promise<void> {
    const now = new Date();
    const timeElapsed = now.getTime() - this.requestWindow.getTime();

    // 重置計數器 (每分鐘)
    if (timeElapsed > 60000) {
      this.requestCount = 0;
      this.requestWindow = now;
    }

    // 檢查是否超過限制
    if (this.requestCount >= this.config.rateLimitPerMinute) {
      const waitTime = 60000 - timeElapsed;
      console.log(`⏳ 達到速率限制，等待 ${waitTime}ms`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
      this.requestCount = 0;
      this.requestWindow = new Date();
    }

    this.requestCount++;
  }

  // ==================== 核心抓取方法 ====================

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
        reject(new Error('抓取任務超時'));
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

  // ==================== HKTVmall 專用方法 ====================

  /**
   * 抓取 HKTVmall 商品資訊
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
   * 抓取 HKTVmall 搜尋排名
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
          { type: 'scroll', value: 2000 },  // 加載更多結果
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

    // 後處理: 找到目標 URL 的排名
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
   * 批量抓取商品
   */
  async scrapeBatch(urls: string[]): Promise<ScrapeResult[]> {
    const results: ScrapeResult[] = [];

    for (const url of urls) {
      try {
        const result = await this.scrapeHKTVProduct(url);
        results.push(result);

        // 添加隨機延遲，避免被檢測
        await this.randomDelay(2000, 5000);
      } catch (error) {
        console.error(`抓取失敗: ${url}`, error);
        results.push({
          success: false,
          taskId: this.generateTaskId(),
          url,
          data: null,
          error: error instanceof Error ? error.message : '未知錯誤',
          durationMs: 0,
          scrapedAt: new Date().toISOString(),
        });
      }
    }

    return results;
  }

  // ==================== 工具方法 ====================

  /**
   * 生成任務 ID
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
   * 健康檢查
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

// ==================== 單例導出 ====================

let connectorInstance: ClawdbotConnector | null = null;

export function getClawdbotConnector(config?: Partial<ClawdbotConfig>): ClawdbotConnector {
  if (!connectorInstance) {
    connectorInstance = new ClawdbotConnector(config);
  }
  return connectorInstance;
}
