// =============================================
// SEO 排名追蹤 API 服務
// =============================================
//
// 功能：
//   - 關鍵詞配置 CRUD
//   - 排名查詢與歷史
//   - 排行榜
//   - 警報管理
//   - 抓取任務
//   - 儀表板數據
// =============================================

import { get, post, patch, del, buildUrl } from "./client";

// =============================================
// 類型定義
// =============================================

// 關鍵詞類型
export type KeywordType = "primary" | "secondary" | "long_tail" | "brand" | "competitor";

// 排名來源
export type RankingSource = "google_hk" | "hktvmall";

// 報告類型
export type ReportType = "weekly" | "monthly" | "quarterly" | "custom";

// 警報嚴重程度
export type AlertSeverity = "info" | "warning" | "critical";

// 抓取任務狀態
export type ScrapeJobStatus = "pending" | "running" | "completed" | "failed";

// =============================================
// 關鍵詞配置
// =============================================

export interface KeywordConfig {
  id: string;
  product_id: string | null;
  keyword: string;
  keyword_normalized: string;
  keyword_type: KeywordType;
  track_google: boolean;
  track_hktvmall: boolean;
  is_active: boolean;
  target_google_rank: number | null;
  target_hktvmall_rank: number | null;
  baseline_google_rank: number | null;
  baseline_hktvmall_rank: number | null;
  latest_google_rank: number | null;
  latest_hktvmall_rank: number | null;
  latest_tracked_at: string | null;
  track_competitors: boolean;
  competitor_product_ids: string[];
  notes: string | null;
  tags: string[];
  created_at: string;
  updated_at: string;
  // 計算字段
  google_rank_change: number | null;
  hktvmall_rank_change: number | null;
  google_target_gap: number | null;
  hktvmall_target_gap: number | null;
}

export interface KeywordConfigCreate {
  product_id?: string;
  keyword: string;
  keyword_type: KeywordType;
  track_google?: boolean;
  track_hktvmall?: boolean;
  target_google_rank?: number;
  target_hktvmall_rank?: number;
  track_competitors?: boolean;
  competitor_product_ids?: string[];
  notes?: string;
  tags?: string[];
}

export interface KeywordConfigUpdate {
  keyword_type?: KeywordType;
  track_google?: boolean;
  track_hktvmall?: boolean;
  is_active?: boolean;
  target_google_rank?: number | null;
  target_hktvmall_rank?: number | null;
  track_competitors?: boolean;
  competitor_product_ids?: string[];
  notes?: string;
  tags?: string[];
}

export interface KeywordConfigListResponse {
  data: KeywordConfig[];
  total: number;
  page: number;
  page_size: number;
}

export interface KeywordConfigBatchCreate {
  product_id?: string;
  keywords: string[];
  keyword_type: KeywordType;
  track_google?: boolean;
  track_hktvmall?: boolean;
}

export interface KeywordConfigBatchResponse {
  created: number;
  skipped: number;
  errors: string[];
  configs: KeywordConfig[];
}

// =============================================
// 排名記錄
// =============================================

export interface KeywordRanking {
  id: string;
  keyword_config_id: string;
  product_id: string | null;
  keyword: string;
  google_rank: number | null;
  google_page: number | null;
  google_url: string | null;
  google_rank_change: number | null;
  hktvmall_rank: number | null;
  hktvmall_page: number | null;
  hktvmall_rank_change: number | null;
  competitor_rankings: Record<string, any> | null;
  serp_features: Record<string, boolean> | null;
  source: RankingSource;
  tracked_at: string;
  scrape_success: boolean;
}

export interface RankingHistorySummary {
  total_records: number;
  date_range: {
    start: string | null;
    end: string | null;
  };
  google_avg_rank: number | null;
  google_best_rank: number | null;
  google_worst_rank: number | null;
  google_trend: string | null;
  hktvmall_avg_rank: number | null;
  hktvmall_best_rank: number | null;
  hktvmall_worst_rank: number | null;
  hktvmall_trend: string | null;
}

export interface KeywordRankingHistoryResponse {
  keyword: string;
  keyword_config_id: string;
  records: KeywordRanking[];
  summary: RankingHistorySummary;
}

// =============================================
// 排行榜
// =============================================

export interface LeaderboardEntry {
  rank: number;
  keyword_config_id: string;
  keyword: string;
  keyword_type: KeywordType;
  product_id: string | null;
  product_name: string | null;
  current_rank: number | null;
  previous_rank: number | null;
  rank_change: number | null;
  target_rank: number | null;
  target_gap: number | null;
  last_tracked_at: string | null;
}

export interface LeaderboardSummary {
  total_keywords: number;
  ranked_keywords: number;
  unranked_keywords: number;
  top_10_count: number;
  top_30_count: number;
  avg_rank: number | null;
  improved_count: number;
  declined_count: number;
}

export interface RankingLeaderboardResponse {
  source: RankingSource;
  generated_at: string;
  entries: LeaderboardEntry[];
  summary: LeaderboardSummary;
}

// =============================================
// 警報
// =============================================

export interface RankingAlert {
  id: string;
  keyword_config_id: string;
  product_id: string | null;
  alert_type: string;
  severity: AlertSeverity;
  keyword: string;
  source: RankingSource;
  previous_rank: number | null;
  current_rank: number | null;
  rank_change: number | null;
  message: string;
  details: Record<string, any> | null;
  is_read: boolean;
  is_resolved: boolean;
  resolved_at: string | null;
  created_at: string;
}

export interface RankingAlertListResponse {
  data: RankingAlert[];
  total: number;
  unread_count: number;
}

// =============================================
// 抓取任務
// =============================================

export interface RankingScrapeJob {
  id: string;
  job_type: string;
  status: ScrapeJobStatus;
  total_keywords: number;
  processed_keywords: number;
  successful_keywords: number;
  failed_keywords: number;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  errors: string[];
  triggered_by: string;
  created_at: string;
  progress_percent: number;
  success_rate: number | null;
}

export interface RankingScrapeJobListResponse {
  data: RankingScrapeJob[];
  total: number;
}

// =============================================
// 儀表板
// =============================================

export interface DashboardOverview {
  total_keywords: number;
  active_keywords: number;
  keywords_with_data: number;
  improved_keywords: number;
  declined_keywords: number;
  unchanged_keywords: number;
  seo_health_score: number;
  last_scrape_at: string | null;
}

export interface RankingSummaryBySource {
  source: RankingSource;
  total_keywords: number;
  ranked_keywords: number;
  avg_rank: number | null;
  top_10_count: number;
  top_30_count: number;
  best_keyword: { keyword: string; rank: number } | null;
  worst_keyword: { keyword: string; rank: number } | null;
}

export interface RankingTrendPoint {
  date: string;
  google_avg_rank: number | null;
  hktvmall_avg_rank: number | null;
  google_top_10: number;
  hktvmall_top_10: number;
}

export interface SEODashboardResponse {
  overview: DashboardOverview;
  google_rankings: RankingSummaryBySource;
  hktvmall_rankings: RankingSummaryBySource;
  ranking_trends: RankingTrendPoint[];
  recent_alerts: RankingAlert[];
  recent_jobs: RankingScrapeJob[];
}

// =============================================
// 報告
// =============================================

export interface SEOReport {
  id: string;
  product_id: string | null;
  report_type: ReportType;
  report_title: string;
  report_period_start: string;
  report_period_end: string;
  google_summary: Record<string, any> | null;
  hktvmall_summary: Record<string, any> | null;
  keyword_details: Record<string, any>[] | null;
  competitor_comparison: Record<string, any> | null;
  recommendations: string[] | null;
  improvement_score: number | null;
  status: string;
  generated_at: string;
}

export interface SEOReportListResponse {
  data: SEOReport[];
  total: number;
}

// =============================================
// Query Keys（用於 React Query 緩存管理）
// =============================================

export const seoRankingKeys = {
  all: ["seo-ranking"] as const,
  // 關鍵詞
  keywords: () => [...seoRankingKeys.all, "keywords"] as const,
  keywordsList: (params?: Record<string, any>) =>
    [...seoRankingKeys.keywords(), "list", params] as const,
  keywordDetail: (id: string) =>
    [...seoRankingKeys.keywords(), "detail", id] as const,
  // 排名
  rankings: () => [...seoRankingKeys.all, "rankings"] as const,
  rankingHistory: (configId: string) =>
    [...seoRankingKeys.rankings(), "history", configId] as const,
  rankingLatest: (params?: Record<string, any>) =>
    [...seoRankingKeys.rankings(), "latest", params] as const,
  // 排行榜
  leaderboard: (source: RankingSource, params?: Record<string, any>) =>
    [...seoRankingKeys.all, "leaderboard", source, params] as const,
  // 警報
  alerts: () => [...seoRankingKeys.all, "alerts"] as const,
  alertsList: (params?: Record<string, any>) =>
    [...seoRankingKeys.alerts(), "list", params] as const,
  // 抓取任務
  scrapeJobs: () => [...seoRankingKeys.all, "scrape-jobs"] as const,
  scrapeJobsList: (params?: Record<string, any>) =>
    [...seoRankingKeys.scrapeJobs(), "list", params] as const,
  scrapeJobDetail: (id: string) =>
    [...seoRankingKeys.scrapeJobs(), "detail", id] as const,
  // 儀表板
  dashboard: (params?: Record<string, any>) =>
    [...seoRankingKeys.all, "dashboard", params] as const,
  // 報告
  reports: () => [...seoRankingKeys.all, "reports"] as const,
  reportsList: (params?: Record<string, any>) =>
    [...seoRankingKeys.reports(), "list", params] as const,
  reportDetail: (id: string) =>
    [...seoRankingKeys.reports(), "detail", id] as const,
};

// =============================================
// API 函數
// =============================================

const BASE_URL = "/api/v1/seo-ranking";

// ==================== 關鍵詞配置 ====================

export async function createKeywordConfig(
  data: KeywordConfigCreate
): Promise<KeywordConfig> {
  return post<KeywordConfig>(`${BASE_URL}/keywords`, data);
}

export async function batchCreateKeywordConfigs(
  data: KeywordConfigBatchCreate
): Promise<KeywordConfigBatchResponse> {
  return post<KeywordConfigBatchResponse>(`${BASE_URL}/keywords/batch`, data);
}

export async function getKeywordConfigs(params?: {
  product_id?: string;
  keyword_type?: KeywordType;
  is_active?: boolean;
  search?: string;
  page?: number;
  page_size?: number;
}): Promise<KeywordConfigListResponse> {
  const url = buildUrl(`${BASE_URL}/keywords`, params);
  return get<KeywordConfigListResponse>(url);
}

export async function getKeywordConfig(id: string): Promise<KeywordConfig> {
  return get<KeywordConfig>(`${BASE_URL}/keywords/${id}`);
}

export async function updateKeywordConfig(
  id: string,
  data: KeywordConfigUpdate
): Promise<KeywordConfig> {
  return patch<KeywordConfig>(`${BASE_URL}/keywords/${id}`, data);
}

export async function deleteKeywordConfig(
  id: string
): Promise<{ message: string; id: string }> {
  return del<{ message: string; id: string }>(`${BASE_URL}/keywords/${id}`);
}

// ==================== 排名查詢 ====================

export async function getRankingHistory(
  configId: string,
  params?: {
    start_date?: string;
    end_date?: string;
    limit?: number;
  }
): Promise<KeywordRankingHistoryResponse> {
  const url = buildUrl(`${BASE_URL}/rankings/${configId}/history`, params);
  return get<KeywordRankingHistoryResponse>(url);
}

export async function getLatestRankings(params?: {
  product_id?: string;
  keyword_type?: KeywordType;
  source?: RankingSource;
  limit?: number;
}): Promise<{ data: KeywordRanking[]; total: number }> {
  const url = buildUrl(`${BASE_URL}/rankings/latest`, params);
  return get<{ data: KeywordRanking[]; total: number }>(url);
}

// ==================== 排行榜 ====================

export async function getLeaderboard(params?: {
  source?: RankingSource;
  keyword_type?: KeywordType;
  product_id?: string;
  sort_by?: "rank_asc" | "rank_desc" | "change_asc" | "change_desc";
  limit?: number;
  include_unranked?: boolean;
}): Promise<RankingLeaderboardResponse> {
  const url = buildUrl(`${BASE_URL}/leaderboard`, params);
  return get<RankingLeaderboardResponse>(url);
}

// ==================== 警報 ====================

export async function getAlerts(params?: {
  is_read?: boolean;
  severity?: AlertSeverity;
  product_id?: string;
  limit?: number;
}): Promise<RankingAlertListResponse> {
  const url = buildUrl(`${BASE_URL}/alerts`, params);
  return get<RankingAlertListResponse>(url);
}

export async function markAlertRead(
  alertId: string
): Promise<{ message: string }> {
  return patch<{ message: string }>(`${BASE_URL}/alerts/${alertId}/read`, {});
}

export async function resolveAlert(
  alertId: string,
  resolution_notes?: string
): Promise<{ message: string }> {
  return patch<{ message: string }>(`${BASE_URL}/alerts/${alertId}/resolve`, {
    resolution_notes,
  });
}

export async function batchAlertAction(data: {
  alert_ids: string[];
  action: "mark_read" | "mark_unread" | "resolve";
  resolution_notes?: string;
}): Promise<{ message: string }> {
  return post<{ message: string }>(`${BASE_URL}/alerts/batch`, data);
}

// ==================== 抓取任務 ====================

export async function triggerScrape(data: {
  job_type?: string;
  keyword_config_ids?: string[];
  product_id?: string;
}): Promise<RankingScrapeJob> {
  return post<RankingScrapeJob>(`${BASE_URL}/scrape`, data);
}

export async function getScrapeJobs(params?: {
  status?: ScrapeJobStatus;
  limit?: number;
}): Promise<RankingScrapeJobListResponse> {
  const url = buildUrl(`${BASE_URL}/scrape/jobs`, params);
  return get<RankingScrapeJobListResponse>(url);
}

export async function getScrapeJob(id: string): Promise<RankingScrapeJob> {
  return get<RankingScrapeJob>(`${BASE_URL}/scrape/jobs/${id}`);
}

// ==================== 儀表板 ====================

export async function getDashboard(params?: {
  product_id?: string;
  days?: number;
}): Promise<SEODashboardResponse> {
  const url = buildUrl(`${BASE_URL}/dashboard`, params);
  return get<SEODashboardResponse>(url);
}

// ==================== 報告 ====================

export async function generateReport(data: {
  product_id?: string;
  report_type: ReportType;
  period_days?: number;
}): Promise<SEOReport> {
  return post<SEOReport>(`${BASE_URL}/reports/generate`, data);
}

export async function getReports(params?: {
  product_id?: string;
  report_type?: ReportType;
  limit?: number;
}): Promise<SEOReportListResponse> {
  const url = buildUrl(`${BASE_URL}/reports`, params);
  return get<SEOReportListResponse>(url);
}

export async function getReport(id: string): Promise<SEOReport> {
  return get<SEOReport>(`${BASE_URL}/reports/${id}`);
}
