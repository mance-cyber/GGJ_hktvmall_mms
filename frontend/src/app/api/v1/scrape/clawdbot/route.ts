// ==================== Clawdbot 抓取 API ====================
// 端點: POST /api/v1/scrape/clawdbot
// 用途: 使用 clawdbot 執行瀏覽器自動化抓取任務
// 安全級別: CRITICAL - 已加入 SSRF 防護、認證、速率限制

import { NextRequest, NextResponse } from 'next/server';
import { getClawdbotConnector, ScrapeTask } from '@/lib/connectors/clawdbot-connector';
import { validateScraperURL, validateScraperURLs } from '@/lib/security/url-validator';
import { withAuth, logAPIAccess, AuthResult } from '@/lib/security/api-auth';

// ==================== 安全配置 ====================

const MAX_BATCH_SIZE = 50; // 批量抓取最大數量
const TIMEOUT_MS = 60000; // 單個任務超時時間（60秒）
const MAX_CONCURRENT_TASKS = 5; // 最大並發任務數

// ==================== API Handler（已加認證）====================

async function handlePOST(request: NextRequest, authResult: AuthResult) {
  try {
    const body = await request.json();
    const { action, params } = body;

    // 記錄 API 訪問
    logAPIAccess(request, authResult, action, { params });

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

// 導出帶認證的 POST handler
export const POST = withAuth(handlePOST, {
  rateLimit: 60, // 每分鐘最多 60 個請求
  requireAuth: true,
});

// ==================== Action Handlers（已加 URL 驗證）====================

/**
 * 抓取單個商品
 * ✅ FIXED: CRIT-1 - 添加 URL 驗證，防止 SSRF
 */
async function handleScrapeProduct(connector: any, params: any) {
  const { url } = params;

  if (!url) {
    return NextResponse.json(
      { success: false, error: '缺少 url 參數' },
      { status: 400 }
    );
  }

  // 🔒 安全檢查：驗證 URL
  const validation = validateScraperURL(url);
  if (!validation.isValid) {
    return NextResponse.json(
      { 
        success: false, 
        error: `URL 驗證失敗: ${validation.error}`,
        securityReason: 'SSRF_PROTECTION',
      },
      { status: 400 }
    );
  }

  // 使用清理後的 URL
  const safeUrl = validation.sanitizedUrl!;

  // 🔒 超時保護
  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error('抓取超時')), TIMEOUT_MS)
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
        url: safeUrl, // 返回清理後的 URL
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : '抓取失敗',
      },
      { status: 500 }
    );
  }
}

/**
 * 抓取搜尋排名
 * ✅ FIXED: CRIT-1 - 添加 URL 驗證
 */
async function handleScrapeSearchRank(connector: any, params: any) {
  const { keyword, targetUrl } = params;

  if (!keyword || !targetUrl) {
    return NextResponse.json(
      { success: false, error: '缺少 keyword 或 targetUrl 參數' },
      { status: 400 }
    );
  }

  // 🔒 安全檢查：驗證目標 URL
  const validation = validateScraperURL(targetUrl);
  if (!validation.isValid) {
    return NextResponse.json(
      { 
        success: false, 
        error: `URL 驗證失敗: ${validation.error}`,
        securityReason: 'SSRF_PROTECTION',
      },
      { status: 400 }
    );
  }

  const safeUrl = validation.sanitizedUrl!;

  // 🔒 關鍵字驗證
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
        error: error instanceof Error ? error.message : '抓取失敗',
      },
      { status: 500 }
    );
  }
}

/**
 * 批量抓取
 * ✅ FIXED: CRIT-1 - 添加 URL 驗證
 * ✅ FIXED: CRIT-3 - 限制批量大小為 50
 */
async function handleScrapeBatch(connector: any, params: any) {
  const { urls } = params;

  if (!urls || !Array.isArray(urls)) {
    return NextResponse.json(
      { success: false, error: 'urls 必須是數組' },
      { status: 400 }
    );
  }

  // 🔒 批量大小限制
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
        error: `批量抓取最多支持 ${MAX_BATCH_SIZE} 個 URL，當前提供了 ${urls.length} 個`,
        maxBatchSize: MAX_BATCH_SIZE,
      },
      { status: 400 }
    );
  }

  // 🔒 批量 URL 驗證
  const { validUrls, invalidUrls } = validateScraperURLs(urls);

  if (invalidUrls.length > 0) {
    return NextResponse.json(
      {
        success: false,
        error: `有 ${invalidUrls.length} 個無效 URL`,
        invalidUrls,
        validCount: validUrls.length,
      },
      { status: 400 }
    );
  }

  if (validUrls.length === 0) {
    return NextResponse.json(
      { success: false, error: '沒有有效的 URL' },
      { status: 400 }
    );
  }

  try {
    // 使用清理後的 URL 進行抓取
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
        error: error instanceof Error ? error.message : '批量抓取失敗',
      },
      { status: 500 }
    );
  }
}

/**
 * 自定義抓取任務
 * ✅ FIXED: CRIT-1 - 添加 URL 驗證
 */
async function handleScrapeCustom(connector: any, params: any) {
  const task: ScrapeTask = params.task;

  if (!task || !task.url) {
    return NextResponse.json(
      { success: false, error: '缺少 task 參數或 task.url' },
      { status: 400 }
    );
  }

  // 🔒 安全檢查：驗證 URL
  const validation = validateScraperURL(task.url);
  if (!validation.isValid) {
    return NextResponse.json(
      { 
        success: false, 
        error: `URL 驗證失敗: ${validation.error}`,
        securityReason: 'SSRF_PROTECTION',
      },
      { status: 400 }
    );
  }

  // 使用清理後的 URL
  task.url = validation.sanitizedUrl!;

  // 生成任務 ID
  if (!task.id) {
    task.id = `custom_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  // 🔒 超時保護
  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error('抓取超時')), TIMEOUT_MS)
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
        error: error instanceof Error ? error.message : '抓取失敗',
      },
      { status: 500 }
    );
  }
}

// ==================== GET: 健康檢查（不需要認證）====================

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
        error: error instanceof Error ? error.message : '未知錯誤',
      },
      { status: 500 }
    );
  }
}
