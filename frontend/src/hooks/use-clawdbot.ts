// ==================== Clawdbot Hook ====================
// 用途: 在前端調用 clawdbot 抓取功能

import { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';

// ==================== 類型定義 ====================

export interface ClawdbotScrapeResult {
  success: boolean;
  data: Record<string, any> | null;
  error: string | null;
  metadata: {
    taskId: string;
    durationMs: number;
    scrapedAt: string;
  };
}

export interface ClawdbotHealthStatus {
  success: boolean;
  service: string;
  status: 'connected' | 'disconnected' | 'error';
  timestamp: string;
  error?: string;
}

// ==================== API 調用函數 ====================

/**
 * 調用 Clawdbot API
 */
async function callClawdbotAPI(
  action: string,
  params: Record<string, any>
): Promise<ClawdbotScrapeResult> {
  const response = await fetch('/api/v1/scrape/clawdbot', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ action, params }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || '抓取失敗');
  }

  return response.json();
}

/**
 * 檢查 Clawdbot 健康狀態
 */
async function checkClawdbotHealth(): Promise<ClawdbotHealthStatus> {
  const response = await fetch('/api/v1/scrape/clawdbot');
  return response.json();
}

// ==================== Hook ====================

export function useClawdbot() {
  const [isConnected, setIsConnected] = useState(false);

  // 健康檢查
  const { data: healthStatus, refetch: checkHealth } = useQuery({
    queryKey: ['clawdbot', 'health'],
    queryFn: checkClawdbotHealth,
    refetchInterval: 30000, // 每 30 秒檢查一次
    onSuccess: (data) => {
      setIsConnected(data.status === 'connected');
    },
  });

  // 抓取單個商品
  const scrapeProductMutation = useMutation({
    mutationFn: (url: string) =>
      callClawdbotAPI('scrape_product', { url }),
  });

  // 抓取搜尋排名
  const scrapeSearchRankMutation = useMutation({
    mutationFn: ({ keyword, targetUrl }: { keyword: string; targetUrl: string }) =>
      callClawdbotAPI('scrape_search_rank', { keyword, targetUrl }),
  });

  // 批量抓取
  const scrapeBatchMutation = useMutation({
    mutationFn: (urls: string[]) =>
      callClawdbotAPI('scrape_batch', { urls }),
  });

  // 自定義抓取
  const scrapeCustomMutation = useMutation({
    mutationFn: (task: any) =>
      callClawdbotAPI('scrape_custom', { task }),
  });

  return {
    // 狀態
    isConnected,
    healthStatus,

    // 方法
    checkHealth,
    scrapeProduct: scrapeProductMutation.mutateAsync,
    scrapeSearchRank: scrapeSearchRankMutation.mutateAsync,
    scrapeBatch: scrapeBatchMutation.mutateAsync,
    scrapeCustom: scrapeCustomMutation.mutateAsync,

    // Loading 狀態
    isScrapingProduct: scrapeProductMutation.isLoading,
    isScrapingSearchRank: scrapeSearchRankMutation.isLoading,
    isScrapingBatch: scrapeBatchMutation.isLoading,
    isScrapingCustom: scrapeCustomMutation.isLoading,

    // 錯誤
    productError: scrapeProductMutation.error,
    searchRankError: scrapeSearchRankMutation.error,
    batchError: scrapeBatchMutation.error,
    customError: scrapeCustomMutation.error,
  };
}
