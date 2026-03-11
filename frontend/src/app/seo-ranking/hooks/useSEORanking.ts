// =============================================
// SEO RankingTrack React Query Hooks
// =============================================

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  // API Function
  getKeywordConfigs,
  getKeywordConfig,
  createKeywordConfig,
  batchCreateKeywordConfigs,
  updateKeywordConfig,
  deleteKeywordConfig,
  getRankingHistory,
  getLatestRankings,
  getLeaderboard,
  getAlerts,
  markAlertRead,
  resolveAlert,
  batchAlertAction,
  triggerScrape,
  getScrapeJobs,
  getScrapeJob,
  getDashboard,
  generateReport,
  getReports,
  getReport,
  // Query Keys
  seoRankingKeys,
  // Type
  KeywordType,
  RankingSource,
  AlertSeverity,
  ScrapeJobStatus,
  ReportType,
  KeywordConfigCreate,
  KeywordConfigUpdate,
  KeywordConfigBatchCreate,
} from "@/lib/api/seo-ranking";

// =============================================
// 關鍵詞Configuration Hooks
// =============================================

/**
 * Get keyword configList
 */
export function useKeywordConfigs(params?: {
  product_id?: string;
  keyword_type?: KeywordType;
  is_active?: boolean;
  search?: string;
  page?: number;
  page_size?: number;
}) {
  return useQuery({
    queryKey: seoRankingKeys.keywordsList(params),
    queryFn: () => getKeywordConfigs(params),
  });
}

/**
 * Fetch單個關鍵詞Configuration
 */
export function useKeywordConfig(id: string | null) {
  return useQuery({
    queryKey: seoRankingKeys.keywordDetail(id || ""),
    queryFn: () => getKeywordConfig(id!),
    enabled: !!id,
  });
}

/**
 * Create keyword config
 */
export function useCreateKeywordConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: KeywordConfigCreate) => createKeywordConfig(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: seoRankingKeys.keywords() });
      queryClient.invalidateQueries({ queryKey: seoRankingKeys.dashboard() });
    },
  });
}

/**
 * Batch create keyword configurations
 */
export function useBatchCreateKeywordConfigs() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: KeywordConfigBatchCreate) =>
      batchCreateKeywordConfigs(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: seoRankingKeys.keywords() });
      queryClient.invalidateQueries({ queryKey: seoRankingKeys.dashboard() });
    },
  });
}

/**
 * Update關鍵詞Configuration
 */
export function useUpdateKeywordConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: KeywordConfigUpdate }) =>
      updateKeywordConfig(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: seoRankingKeys.keywords() });
      queryClient.invalidateQueries({
        queryKey: seoRankingKeys.keywordDetail(variables.id),
      });
    },
  });
}

/**
 * Delete關鍵詞Configuration
 */
export function useDeleteKeywordConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteKeywordConfig(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: seoRankingKeys.keywords() });
      queryClient.invalidateQueries({ queryKey: seoRankingKeys.dashboard() });
    },
  });
}

// =============================================
// RankingQuery Hooks
// =============================================

/**
 * Get keyword ranking history
 */
export function useRankingHistory(
  configId: string | null,
  params?: {
    start_date?: string;
    end_date?: string;
    limit?: number;
  }
) {
  return useQuery({
    queryKey: seoRankingKeys.rankingHistory(configId || ""),
    queryFn: () => getRankingHistory(configId!, params),
    enabled: !!configId,
  });
}

/**
 * Fetch最新RankingData
 */
export function useLatestRankings(params?: {
  product_id?: string;
  keyword_type?: KeywordType;
  source?: RankingSource;
  limit?: number;
}) {
  return useQuery({
    queryKey: seoRankingKeys.rankingLatest(params),
    queryFn: () => getLatestRankings(params),
  });
}

// =============================================
// 排行榜 Hooks
// =============================================

/**
 * FetchRanking排行榜
 */
export function useLeaderboard(params?: {
  source?: RankingSource;
  keyword_type?: KeywordType;
  product_id?: string;
  sort_by?: "rank_asc" | "rank_desc" | "change_asc" | "change_desc";
  limit?: number;
  include_unranked?: boolean;
}) {
  const source = params?.source || "google_hk";
  return useQuery({
    queryKey: seoRankingKeys.leaderboard(source, params),
    queryFn: () => getLeaderboard(params),
  });
}

// =============================================
// Alert Hooks
// =============================================

/**
 * FetchRankingAlert list
 */
export function useRankingAlerts(params?: {
  is_read?: boolean;
  severity?: AlertSeverity;
  product_id?: string;
  limit?: number;
}) {
  return useQuery({
    queryKey: seoRankingKeys.alertsList(params),
    queryFn: () => getAlerts(params),
    refetchInterval: 60000, // 每minutesAutoRefresh
  });
}

/**
 * 標記Alert為已讀
 */
export function useMarkAlertRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (alertId: string) => markAlertRead(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: seoRankingKeys.alerts() });
    },
  });
}

/**
 * 解決Alert
 */
export function useResolveAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      alertId,
      resolution_notes,
    }: {
      alertId: string;
      resolution_notes?: string;
    }) => resolveAlert(alertId, resolution_notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: seoRankingKeys.alerts() });
    },
  });
}

/**
 * 批量ProcessingAlert
 */
export function useBatchAlertAction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      alert_ids: string[];
      action: "mark_read" | "mark_unread" | "resolve";
      resolution_notes?: string;
    }) => batchAlertAction(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: seoRankingKeys.alerts() });
    },
  });
}

// =============================================
// 抓取任務 Hooks
// =============================================

/**
 * Fetch抓取任務List
 */
export function useScrapeJobs(params?: {
  status?: ScrapeJobStatus;
  limit?: number;
}) {
  return useQuery({
    queryKey: seoRankingKeys.scrapeJobsList(params),
    queryFn: () => getScrapeJobs(params),
  });
}

/**
 * Fetch單個抓取任務
 */
export function useScrapeJob(id: string | null) {
  return useQuery({
    queryKey: seoRankingKeys.scrapeJobDetail(id || ""),
    queryFn: () => getScrapeJob(id!),
    enabled: !!id,
    refetchInterval: (query) => {
      // When task is in progress, refresh every 5 seconds
      const data = query.state.data;
      if (data?.status === "running" || data?.status === "pending") {
        return 5000;
      }
      return false;
    },
  });
}

/**
 * Trigger抓取任務
 */
export function useTriggerScrape() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      job_type?: string;
      keyword_config_ids?: string[];
      product_id?: string;
    }) => triggerScrape(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: seoRankingKeys.scrapeJobs() });
    },
  });
}

// =============================================
// 儀表板 Hooks
// =============================================

/**
 * Get SEO dashboard data
 */
export function useSEODashboard(params?: {
  product_id?: string;
  days?: number;
}) {
  return useQuery({
    queryKey: seoRankingKeys.dashboard(params),
    queryFn: () => getDashboard(params),
    refetchInterval: 300000, // 每 5 minutesAutoRefresh
  });
}

// =============================================
// Report Hooks
// =============================================

/**
 * FetchReportList
 */
export function useSEOReports(params?: {
  product_id?: string;
  report_type?: ReportType;
  limit?: number;
}) {
  return useQuery({
    queryKey: seoRankingKeys.reportsList(params),
    queryFn: () => getReports(params),
  });
}

/**
 * Fetch單個Report
 */
export function useSEOReport(id: string | null) {
  return useQuery({
    queryKey: seoRankingKeys.reportDetail(id || ""),
    queryFn: () => getReport(id!),
    enabled: !!id,
  });
}

/**
 * GenerateReport
 */
export function useGenerateReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: {
      product_id?: string;
      report_type: ReportType;
      period_days?: number;
    }) => generateReport(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: seoRankingKeys.reports() });
    },
  });
}
