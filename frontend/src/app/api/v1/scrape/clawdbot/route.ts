// ==================== Clawdbot 抓取 API ====================
// 端點: POST /api/v1/scrape/clawdbot
// 用途: 使用 clawdbot 執行瀏覽器自動化抓取任務

import { NextRequest, NextResponse } from 'next/server';
import { getClawdbotConnector, ScrapeTask } from '@/lib/connectors/clawdbot-connector';

// ==================== API Handler ====================

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, params } = body;

    const connector = getClawdbotConnector();

    // 確保連接
    const isHealthy = await connector.healthCheck();
    if (!isHealthy) {
      return NextResponse.json(
        {
          success: false,
          error: 'Clawdbot 服務不可用，請確認 clawdbot 已啟動',
        },
        { status: 503 }
      );
    }

    // 根據不同的 action 執行不同操作
    switch (action) {
      case 'scrape_product':
        return await handleScrapeProduct(connector, params);

      case 'scrape_search_rank':
        return await handleScrapeSearchRank(connector, params);

      case 'scrape_batch':
        return await handleScrapeBatch(connector, params);

      case 'scrape_custom':
        return await handleScrapeCustom(connector, params);

      default:
        return NextResponse.json(
          {
            success: false,
            error: `不支持的操作: ${action}`,
          },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error('Clawdbot API 錯誤:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : '未知錯誤',
      },
      { status: 500 }
    );
  }
}

// ==================== Action Handlers ====================

/**
 * 抓取單個商品
 */
async function handleScrapeProduct(connector: any, params: any) {
  const { url } = params;

  if (!url) {
    return NextResponse.json(
      { success: false, error: '缺少 url 參數' },
      { status: 400 }
    );
  }

  const result = await connector.scrapeHKTVProduct(url);

  return NextResponse.json({
    success: result.success,
    data: result.data,
    error: result.error,
    metadata: {
      taskId: result.taskId,
      durationMs: result.durationMs,
      scrapedAt: result.scrapedAt,
    },
  });
}

/**
 * 抓取搜尋排名
 */
async function handleScrapeSearchRank(connector: any, params: any) {
  const { keyword, targetUrl } = params;

  if (!keyword || !targetUrl) {
    return NextResponse.json(
      { success: false, error: '缺少 keyword 或 targetUrl 參數' },
      { status: 400 }
    );
  }

  const result = await connector.scrapeHKTVSearchRank(keyword, targetUrl);

  return NextResponse.json({
    success: result.success,
    data: result.data,
    error: result.error,
    metadata: {
      taskId: result.taskId,
      durationMs: result.durationMs,
      scrapedAt: result.scrapedAt,
    },
  });
}

/**
 * 批量抓取
 */
async function handleScrapeBatch(connector: any, params: any) {
  const { urls } = params;

  if (!urls || !Array.isArray(urls)) {
    return NextResponse.json(
      { success: false, error: 'urls 必須是數組' },
      { status: 400 }
    );
  }

  const results = await connector.scrapeBatch(urls);

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
 * 自定義抓取任務
 */
async function handleScrapeCustom(connector: any, params: any) {
  const task: ScrapeTask = params.task;

  if (!task || !task.url) {
    return NextResponse.json(
      { success: false, error: '缺少 task 參數' },
      { status: 400 }
    );
  }

  // 生成任務 ID
  if (!task.id) {
    task.id = `custom_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  const result = await connector.scrape(task);

  return NextResponse.json({
    success: result.success,
    data: result.data,
    error: result.error,
    metadata: {
      taskId: result.taskId,
      durationMs: result.durationMs,
      scrapedAt: result.scrapedAt,
    },
  });
}

// ==================== GET: 健康檢查 ====================

export async function GET() {
  try {
    const connector = getClawdbotConnector();
    const isHealthy = await connector.healthCheck();

    return NextResponse.json({
      success: isHealthy,
      service: 'clawdbot',
      status: isHealthy ? 'connected' : 'disconnected',
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        service: 'clawdbot',
        status: 'error',
        error: error instanceof Error ? error.message : '未知錯誤',
      },
      { status: 500 }
    );
  }
}
