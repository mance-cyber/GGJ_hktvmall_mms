// ==================== Clawdbot 抓取 API ====================
// 端點: POST /api/v1/scrape/clawdbot
// 用途: 使用 clawdbot 執行BrowserAuto化抓取任務
// Security級別: CRITICAL - 已加入 SSRF 防護、Authentication、速率Limit

import { NextRequest, NextResponse } from 'next/server';
import { getClawdbotConnector, ScrapeTask } from '@/lib/connectors/clawdbot-connector';
import { validateScraperURL, validateScraperURLs } from '@/lib/security/url-validator';
import { withAuth, logAPIAccess, AuthResult } from '@/lib/security/api-auth';

// ==================== SecurityConfiguration ====================

const MAX_BATCH_SIZE = 50; // 批量抓取最大Quantity
const TIMEOUT_MS = 60000; // 單個任務TimeoutTime（60秒）
const MAX_CONCURRENT_TASKS = 5; // 最大並發任務數

// ==================== API Handler（已加Authentication）====================

async function handlePOST(request: NextRequest, authResult: AuthResult) {
  try {
    const body = await request.json();
    const { action, params } = body;

    // Record API 訪問
    logAPIAccess(request, authResult, action, { params });

    const connector = getClawdbotConnector();

    // EnsureConnection
    const isHealthy = await connector.healthCheck();
    if (!isHealthy) {
      return NextResponse.json(
        {
          success: false,
          error: 'Clawdbot 服務不可用，Please confirm clawdbot is running',
        },
        { status: 503 }
      );
    }

    // 根據不同的 action 執行不同Operation
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
            error: `不Support的Operation: ${action}`,
          },
          { status: 400 }
        );
    }
  } catch (error) {
    console.error('Clawdbot API Error:', error);
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : 'UnknownError',
      },
      { status: 500 }
    );
  }
}

// Export帶Authentication的 POST handler
export const POST = withAuth(handlePOST, {
  rateLimit: 60, // 每minutes最多 60 個Request
  requireAuth: true,
});

// ==================== Action Handlers（已加 URL Validate）====================

/**
 * 抓取單個products
 * ✅ FIXED: CRIT-1 - 添加 URL Validate，Prevent SSRF
 */
async function handleScrapeProduct(connector: any, params: any) {
  const { url } = params;

  if (!url) {
    return NextResponse.json(
      { success: false, error: '缺少 url Parameter' },
      { status: 400 }
    );
  }

  // 🔒 SecurityCheck：Validate URL
  const validation = validateScraperURL(url);
  if (!validation.isValid) {
    return NextResponse.json(
      { 
        success: false, 
        error: `URL ValidateFailed: ${validation.error}`,
        securityReason: 'SSRF_PROTECTION',
      },
      { status: 400 }
    );
  }

  // 使用Clean up後的 URL
  const safeUrl = validation.sanitizedUrl!;

  // 🔒 Timeout保護
  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error('抓取Timeout')), TIMEOUT_MS)
  );

  try {
    const result = await Promise.race([
      connector.scrapeHKTVProduct(safeUrl),
      timeoutPromise,
    ]) as any;

    return NextResponse.json({
      success: result.success,
      data: result.data,
      error: result.error,
      metadata: {
        taskId: result.taskId,
        durationMs: result.durationMs,
        scrapedAt: result.scrapedAt,
        url: safeUrl, // BackClean up後的 URL
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : '抓取Failed',
      },
      { status: 500 }
    );
  }
}

/**
 * 抓取SearchRanking
 * ✅ FIXED: CRIT-1 - 添加 URL Validate
 */
async function handleScrapeSearchRank(connector: any, params: any) {
  const { keyword, targetUrl } = params;

  if (!keyword || !targetUrl) {
    return NextResponse.json(
      { success: false, error: '缺少 keyword 或 targetUrl Parameter' },
      { status: 400 }
    );
  }

  // 🔒 SecurityCheck：ValidateTarget URL
  const validation = validateScraperURL(targetUrl);
  if (!validation.isValid) {
    return NextResponse.json(
      { 
        success: false, 
        error: `URL ValidateFailed: ${validation.error}`,
        securityReason: 'SSRF_PROTECTION',
      },
      { status: 400 }
    );
  }

  const safeUrl = validation.sanitizedUrl!;

  // 🔒 關鍵字Validate
  if (keyword.length > 100) {
    return NextResponse.json(
      { success: false, error: '關鍵字長度不能超過 100 字符' },
      { status: 400 }
    );
  }

  try {
    const result = await connector.scrapeHKTVSearchRank(keyword, safeUrl);

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
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : '抓取Failed',
      },
      { status: 500 }
    );
  }
}

/**
 * 批量抓取
 * ✅ FIXED: CRIT-1 - 添加 URL Validate
 * ✅ FIXED: CRIT-3 - Limit批量大小為 50
 */
async function handleScrapeBatch(connector: any, params: any) {
  const { urls } = params;

  if (!urls || !Array.isArray(urls)) {
    return NextResponse.json(
      { success: false, error: 'urls Required是數組' },
      { status: 400 }
    );
  }

  // 🔒 批量大小Limit
  if (urls.length === 0) {
    return NextResponse.json(
      { success: false, error: 'urls 數組不能為空' },
      { status: 400 }
    );
  }

  if (urls.length > MAX_BATCH_SIZE) {
    return NextResponse.json(
      { 
        success: false, 
        error: `批量抓取最多Support ${MAX_BATCH_SIZE} 個 URL，當前Provide了 ${urls.length} 個`,
        maxBatchSize: MAX_BATCH_SIZE,
      },
      { status: 400 }
    );
  }

  // 🔒 批量 URL Validate
  const { validUrls, invalidUrls } = validateScraperURLs(urls);

  if (invalidUrls.length > 0) {
    return NextResponse.json(
      {
        success: false,
        error: `有 ${invalidUrls.length} 個Invalid URL`,
        invalidUrls,
        validCount: validUrls.length,
      },
      { status: 400 }
    );
  }

  if (validUrls.length === 0) {
    return NextResponse.json(
      { success: false, error: '沒有Valid的 URL' },
      { status: 400 }
    );
  }

  try {
    // 使用Clean up後的 URL 進行抓取
    const results = await connector.scrapeBatch(validUrls);

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
      metadata: {
        maxBatchSize: MAX_BATCH_SIZE,
        processedUrls: validUrls.length,
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : '批量抓取Failed',
      },
      { status: 500 }
    );
  }
}

/**
 * Custom抓取任務
 * ✅ FIXED: CRIT-1 - 添加 URL Validate
 */
async function handleScrapeCustom(connector: any, params: any) {
  const task: ScrapeTask = params.task;

  if (!task || !task.url) {
    return NextResponse.json(
      { success: false, error: '缺少 task Parameter或 task.url' },
      { status: 400 }
    );
  }

  // 🔒 SecurityCheck：Validate URL
  const validation = validateScraperURL(task.url);
  if (!validation.isValid) {
    return NextResponse.json(
      { 
        success: false, 
        error: `URL ValidateFailed: ${validation.error}`,
        securityReason: 'SSRF_PROTECTION',
      },
      { status: 400 }
    );
  }

  // 使用Clean up後的 URL
  task.url = validation.sanitizedUrl!;

  // Generate任務 ID
  if (!task.id) {
    task.id = `custom_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // 🔒 Timeout保護
  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error('抓取Timeout')), TIMEOUT_MS)
  );

  try {
    const result = await Promise.race([
      connector.scrape(task),
      timeoutPromise,
    ]) as any;

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
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : '抓取Failed',
      },
      { status: 500 }
    );
  }
}

// ==================== GET: 健康Check（不NeedAuthentication）====================

export async function GET() {
  try {
    const connector = getClawdbotConnector();
    const isHealthy = await connector.healthCheck();

    return NextResponse.json({
      success: isHealthy,
      service: 'clawdbot',
      status: isHealthy ? 'connected' : 'disconnected',
      timestamp: new Date().toISOString(),
      security: {
        authRequired: true,
        maxBatchSize: MAX_BATCH_SIZE,
        timeout: TIMEOUT_MS,
        allowedDomains: ['hktvmall.com'],
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        service: 'clawdbot',
        status: 'error',
        error: error instanceof Error ? error.message : 'UnknownError',
      },
      { status: 500 }
    );
  }
}
