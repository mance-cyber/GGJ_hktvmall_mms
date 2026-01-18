// =============================================
// SEO 排名追蹤 React Query Hooks
// =============================================

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  // API 函數
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
  // 類型
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
// 關鍵詞配置 Hooks
// =============================================

/**
 * 獲取關鍵詞配置列表
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
 * 獲取單個關鍵詞配置
 */
export function useKeywordConfig(id: string | null) {
  return useQuery({
    queryKey: seoRankingKeys.keywordDetail(id || ""),
    queryFn: () => getKeywordConfig(id!),
    enabled: !!id,
  });
}

/**
 * 創建關鍵詞配置
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
 * 批量創建關鍵詞配置
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
 * 更新關鍵詞配置
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
 * 刪除關鍵詞配置
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
// 排名查詢 Hooks
// =============================================

/**
 * 獲取關鍵詞排名歷史
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
 * 獲取最新排名數據
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
 * 獲取排名排行榜
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
// 警報 Hooks
// =============================================

/**
 * 獲取排名警報列表
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
    refetchInterval: 60000, // 每分鐘自動刷新
  });
}

/**
 * 標記警報為已讀
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
 * 解決警報
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
 * 批量處理警報
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
 * 獲取抓取任務列表
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
 * 獲取單個抓取任務
 */
export function useScrapeJob(id: string | null) {
  return useQuery({
    queryKey: seoRankingKeys.scrapeJobDetail(id || ""),
    queryFn: () => getScrapeJob(id!),
    enabled: !!id,
    refetchInterval: (query) => {
      // 任務進行中時，每 5 秒刷新一次
      const data = query.state.data;
      if (data?.status === "running" || data?.status === "pending") {
        return 5000;
      }
      return false;
    },
  });
}

/**
 * 觸發抓取任務
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
 * 獲取 SEO 儀表板數據
 */
export function useSEODashboard(params?: {
  product_id?: string;
  days?: number;
}) {
  return useQuery({
    queryKey: seoRankingKeys.dashboard(params),
    queryFn: () => getDashboard(params),
    refetchInterval: 300000, // 每 5 分鐘自動刷新
  });
}

// =============================================
// 報告 Hooks
// =============================================

/**
 * 獲取報告列表
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
 * 獲取單個報告
 */
export function useSEOReport(id: string | null) {
  return useQuery({
    queryKey: seoRankingKeys.reportDetail(id || ""),
    queryFn: () => getReport(id!),
    enabled: !!id,
  });
}

/**
 * 生成報告
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
