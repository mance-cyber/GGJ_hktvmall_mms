// ==================== 统一抓取 API (混合架构) ====================
// 端点: POST /api/v1/scrape
// 用途: 根据环境自动选择 Clawdbot (开发) 或 Firecrawl (生产)
// 架构: 开发环境 → Clawdbot | 生产环境 → Firecrawl

import { NextRequest, NextResponse } from 'next/server';
import {
  getUnifiedScraper,
  UnifiedScrapeTask,
} from '@/lib/connectors/unified-scraper';
import { getScraperConfig } from '@/lib/config/scraper.config';

// ==================== API Handler ====================

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, params } = body;

    const scraper = getUnifiedScraper();
    const config = getScraperConfig();

    console.log(`🔧 使用爬虫: ${config.type} (${process.env.NODE_ENV})`);

    // 健康检查
    const isHealthy = await scraper.healthCheck();
    if (!isHealthy) {
      return NextResponse.json(
        {
          success: false,
          error: `${config.type} 服务不可用`,
          details:
            config.type === 'clawdbot'
              ? '请确认 clawdbot 已启动 (ws://127.0.0.1:18789)'
              : '请检查 FIRECRAWL_API_KEY 是否配置正确',
        },
        { status: 503 }
      );
    }

    // 路由到不同的处理函数
    switch (action) {
      case 'scrape_product':
        return await handleScrapeProduct(scraper, params);

      case 'scrape_search_rank':
        return await handleScrapeSearchRank(scraper, params);

      case 'scrape_batch':
        return await handleScrapeBatch(scraper, params);

      case 'scrape_custom':
        return await handleScrapeCustom(scraper, params);

      case 'scrape_url':
        return await handleScrapeUrl(scraper, params);

      default:
        return NextResponse.json(
          {
            success: false,
            error: `不支持的操作: ${action}`,
            supportedActions: [
              'scrape_product',
              'scrape_search_rank',
              'scrape_batch',
              'scrape_custom',
              'scrape_url',
            ],
          },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error('❌ 统一抓取 API 错误:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : '未知错误',
      },
      { status: 500 }
    );
  }
}

// ==================== Action Handlers ====================

/**
 * 抓取单个商品
 */
async function handleScrapeProduct(scraper: any, params: any) {
  const { url } = params;

  if (!url) {
    return NextResponse.json(
      { success: false, error: '缺少 url 参数' },
      { status: 400 }
    );
  }

  console.log(`🛍️ 抓取商品: ${url}`);
  const result = await scraper.scrapeHKTVProduct(url);

  return NextResponse.json({
    success: result.success,
    data: result.data,
    error: result.error,
    metadata: {
      scraper: result.metadata?.scraper,
      taskId: result.metadata?.taskId,
      durationMs: result.durationMs,
      scrapedAt: result.scrapedAt,
    },
  });
}

/**
 * 抓取搜索排名
 */
async function handleScrapeSearchRank(scraper: any, params: any) {
  const { keyword, targetUrl } = params;

  if (!keyword || !targetUrl) {
    return NextResponse.json(
      { success: false, error: '缺少 keyword 或 targetUrl 参数' },
      { status: 400 }
    );
  }

  console.log(`🔍 抓取搜索排名: ${keyword} → ${targetUrl}`);
  const result = await scraper.scrapeHKTVSearchRank(keyword, targetUrl);

  return NextResponse.json({
    success: result.success,
    data: result.data,
    error: result.error,
    metadata: {
      scraper: result.metadata?.scraper,
      taskId: result.metadata?.taskId,
      durationMs: result.durationMs,
      scrapedAt: result.scrapedAt,
    },
  });
}

/**
 * 批量抓取
 */
async function handleScrapeBatch(scraper: any, params: any) {
  const { urls } = params;

  if (!urls || !Array.isArray(urls)) {
    return NextResponse.json(
      { success: false, error: 'urls 必须是数组' },
      { status: 400 }
    );
  }

  console.log(`📦 批量抓取: ${urls.length} 个 URL`);
  const results = await scraper.scrapeBatch(urls);

  const successCount = results.filter((r: any) => r.success).length;
  const failCount = results.length - successCount;

  return NextResponse.json({
    success: true,
    data: {
      total: results.length,
      successCount,
      failCount,
      results,
    },
  });
}

/**
 * 自定义抓取任务
 */
async function handleScrapeCustom(scraper: any, params: any) {
  const task: UnifiedScrapeTask = params.task;

  if (!task || !task.url) {
    return NextResponse.json(
      { success: false, error: '缺少 task 参数' },
      { status: 400 }
    );
  }

  console.log(`🔧 自定义抓取: ${task.url}`);
  const result = await scraper.scrape(task);

  return NextResponse.json({
    success: result.success,
    data: result.data,
    error: result.error,
    metadata: {
      scraper: result.metadata?.scraper,
      taskId: result.metadata?.taskId,
      durationMs: result.durationMs,
      scrapedAt: result.scrapedAt,
    },
  });
}

/**
 * 抓取任意 URL (最简单的用法)
 */
async function handleScrapeUrl(scraper: any, params: any) {
  const { url } = params;

  if (!url) {
    return NextResponse.json(
      { success: false, error: '缺少 url 参数' },
      { status: 400 }
    );
  }

  console.log(`🌐 抓取 URL: ${url}`);
  const result = await scraper.scrape({ url });

  return NextResponse.json({
    success: result.success,
    data: result.data,
    error: result.error,
    metadata: {
      scraper: result.metadata?.scraper,
      taskId: result.metadata?.taskId,
      durationMs: result.durationMs,
      scrapedAt: result.scrapedAt,
    },
  });
}

// ==================== GET: 健康检查 & 配置信息 ====================

export async function GET() {
  try {
    const scraper = getUnifiedScraper();
    const config = getScraperConfig();
    const isHealthy = await scraper.healthCheck();

    return NextResponse.json({
      success: true,
      scraper: {
        type: config.type,
        status: isHealthy ? 'connected' : 'disconnected',
        endpoint: config.endpoint,
        hasApiKey: config.type === 'firecrawl' && !!process.env.FIRECRAWL_API_KEY,
      },
      environment: process.env.NODE_ENV || 'development',
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : '未知错误',
      },
      { status: 500 }
    );
  }
}
