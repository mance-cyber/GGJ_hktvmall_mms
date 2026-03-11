// ==================== Clawdbot Hook ====================
// 用途: 在Frontend調用 clawdbot 抓取Feature

import { useState, useEffect } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';

// ==================== Type definitions ====================

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

// ==================== API 調用Function ====================

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
    throw new Error(error.error || '抓取Failed');
  }

  return response.json();
}

/**
 * Check Clawdbot health status
 */
async function checkClawdbotHealth(): Promise<ClawdbotHealthStatus> {
  const response = await fetch('/api/v1/scrape/clawdbot');
  return response.json();
}

// ==================== Hook ====================

export function useClawdbot() {
  const [isConnected, setIsConnected] = useState(false);

  // 健康Check
  const { data: healthStatus, refetch: checkHealth } = useQuery({
    queryKey: ['clawdbot', 'health'],
    queryFn: checkClawdbotHealth,
    refetchInterval: 30000, // 每 30 秒Check一次
  });

  // React Query v5: 使用 useEffect ResponseData變化
  useEffect(() => {
    if (healthStatus) {
      setIsConnected(healthStatus.status === 'connected');
    }
  }, [healthStatus]);

  // 抓取單個products
  const scrapeProductMutation = useMutation({
    mutationFn: (url: string) =>
      callClawdbotAPI('scrape_product', { url }),
  });

  // 抓取SearchRanking
  const scrapeSearchRankMutation = useMutation({
    mutationFn: ({ keyword, targetUrl }: { keyword: string; targetUrl: string }) =>
      callClawdbotAPI('scrape_search_rank', { keyword, targetUrl }),
  });

  // 批量抓取
  const scrapeBatchMutation = useMutation({
    mutationFn: (urls: string[]) =>
      callClawdbotAPI('scrape_batch', { urls }),
  });

  // Custom抓取
  const scrapeCustomMutation = useMutation({
    mutationFn: (task: any) =>
      callClawdbotAPI('scrape_custom', { task }),
  });

  return {
    // State
    isConnected,
    healthStatus,

    // Method
    checkHealth,
    scrapeProduct: scrapeProductMutation.mutateAsync,
    scrapeSearchRank: scrapeSearchRankMutation.mutateAsync,
    scrapeBatch: scrapeBatchMutation.mutateAsync,
    scrapeCustom: scrapeCustomMutation.mutateAsync,

    // Loading State (React Query v5: isLoading → isPending)
    isScrapingProduct: scrapeProductMutation.isPending,
    isScrapingSearchRank: scrapeSearchRankMutation.isPending,
    isScrapingBatch: scrapeBatchMutation.isPending,
    isScrapingCustom: scrapeCustomMutation.isPending,

    // Error
    productError: scrapeProductMutation.error,
    searchRankError: scrapeSearchRankMutation.error,
    batchError: scrapeBatchMutation.error,
    customError: scrapeCustomMutation.error,
  };
}
