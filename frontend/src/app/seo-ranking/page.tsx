"use client";

// =============================================
// SEO 排名追蹤儀表板頁面
// =============================================

import { useState } from "react";
import { RefreshCw, TrendingUp, TrendingDown, Target, Search, AlertTriangle, Clock } from "lucide-react";
import {
  PageTransition,
  HoloCard,
  DataMetric,
  HoloPanelHeader,
  HoloButton,
  HoloBadge,
  HoloSkeleton,
  ProgressRing,
  TechDivider,
  StaggerContainer,
} from "@/components/ui/future-tech";
import { useSEODashboard, useLeaderboard, useTriggerScrape } from "./hooks/useSEORanking";
import { RankingSource, SEODashboardResponse, RankingLeaderboardResponse } from "@/lib/api/seo-ranking";
import { LeaderboardTable } from "./components/LeaderboardTable";
import { AlertsList } from "./components/AlertsList";
import { ScrapeJobsList } from "./components/ScrapeJobsList";

// =============================================
// Mock 數據（開發/演示用）
// =============================================

const MOCK_DASHBOARD: SEODashboardResponse = {
  overview: {
    total_keywords: 42,
    active_keywords: 38,
    keywords_with_data: 35,
    improved_keywords: 12,
    declined_keywords: 5,
    unchanged_keywords: 21,
    seo_health_score: 76,
    last_scrape_at: new Date().toISOString(),
  },
  google_rankings: {
    source: "google_hk",
    total_keywords: 42,
    ranked_keywords: 35,
    top_10_count: 8,
    top_30_count: 22,
    avg_rank: 18.5,
    best_keyword: { keyword: "日本零食", rank: 3 },
    worst_keyword: { keyword: "進口糖果批發", rank: 67 },
  },
  hktvmall_rankings: {
    source: "hktvmall",
    total_keywords: 42,
    ranked_keywords: 32,
    top_10_count: 15,
    top_30_count: 28,
    avg_rank: 12.3,
    best_keyword: { keyword: "抹茶餅乾", rank: 1 },
    worst_keyword: { keyword: "日式調味料", rank: 45 },
  },
  ranking_trends: [],
  recent_alerts: [
    {
      id: "alert-1",
      keyword_config_id: "kw-1",
      product_id: null,
      keyword: "日本零食",
      source: "google_hk",
      alert_type: "rank_improved",
      severity: "info",
      message: "排名從第 8 名上升至第 3 名",
      previous_rank: 8,
      current_rank: 3,
      rank_change: 5,
      details: null,
      is_read: false,
      is_resolved: false,
      resolved_at: null,
      created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: "alert-2",
      keyword_config_id: "kw-2",
      product_id: null,
      keyword: "進口糖果",
      source: "hktvmall",
      alert_type: "rank_dropped",
      severity: "warning",
      message: "排名從第 5 名下降至第 12 名",
      previous_rank: 5,
      current_rank: 12,
      rank_change: -7,
      details: null,
      is_read: false,
      is_resolved: false,
      resolved_at: null,
      created_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: "alert-3",
      keyword_config_id: "kw-3",
      product_id: null,
      keyword: "韓國拉麵",
      source: "google_hk",
      alert_type: "rank_dropped",
      severity: "critical",
      message: "排名從第 15 名下降至第 42 名",
      previous_rank: 15,
      current_rank: 42,
      rank_change: -27,
      details: null,
      is_read: true,
      is_resolved: false,
      resolved_at: null,
      created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    },
  ],
  recent_jobs: [
    {
      id: "job-1",
      job_type: "full",
      status: "completed",
      total_keywords: 42,
      processed_keywords: 42,
      successful_keywords: 40,
      failed_keywords: 2,
      progress_percent: 100,
      success_rate: 95.2,
      duration_seconds: 245,
      errors: [],
      triggered_by: "system",
      created_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      started_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      completed_at: new Date(Date.now() - 56 * 60 * 1000).toISOString(),
    },
    {
      id: "job-2",
      job_type: "google_only",
      status: "running",
      total_keywords: 38,
      processed_keywords: 24,
      successful_keywords: 24,
      failed_keywords: 0,
      progress_percent: 63,
      success_rate: 100,
      duration_seconds: null,
      errors: [],
      triggered_by: "user",
      created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      started_at: new Date(Date.now() - 4 * 60 * 1000).toISOString(),
      completed_at: null,
    },
  ],
};

const MOCK_LEADERBOARD_GOOGLE: RankingLeaderboardResponse = {
  source: "google_hk",
  generated_at: new Date().toISOString(),
  summary: {
    total_keywords: 42,
    ranked_keywords: 35,
    unranked_keywords: 7,
    top_10_count: 8,
    top_30_count: 22,
    avg_rank: 18.5,
    improved_count: 12,
    declined_count: 5,
  },
  entries: [
    { rank: 1, keyword_config_id: "kw-1", keyword: "日本零食", keyword_type: "primary", product_id: null, product_name: null, current_rank: 3, previous_rank: 8, rank_change: 5, target_rank: 5, target_gap: -2, last_tracked_at: new Date().toISOString() },
    { rank: 2, keyword_config_id: "kw-2", keyword: "抹茶餅乾", keyword_type: "primary", product_id: null, product_name: null, current_rank: 5, previous_rank: 5, rank_change: 0, target_rank: 3, target_gap: 2, last_tracked_at: new Date().toISOString() },
    { rank: 3, keyword_config_id: "kw-3", keyword: "日本糖果", keyword_type: "secondary", product_id: null, product_name: null, current_rank: 7, previous_rank: 12, rank_change: 5, target_rank: 10, target_gap: -3, last_tracked_at: new Date().toISOString() },
    { rank: 4, keyword_config_id: "kw-4", keyword: "進口零食", keyword_type: "primary", product_id: null, product_name: null, current_rank: 11, previous_rank: 9, rank_change: -2, target_rank: 10, target_gap: 1, last_tracked_at: new Date().toISOString() },
    { rank: 5, keyword_config_id: "kw-5", keyword: "韓國拉麵", keyword_type: "secondary", product_id: null, product_name: null, current_rank: 15, previous_rank: 15, rank_change: 0, target_rank: 10, target_gap: 5, last_tracked_at: new Date().toISOString() },
    { rank: 6, keyword_config_id: "kw-6", keyword: "日式調味料", keyword_type: "long_tail", product_id: null, product_name: null, current_rank: 18, previous_rank: 25, rank_change: 7, target_rank: 15, target_gap: 3, last_tracked_at: new Date().toISOString() },
    { rank: 7, keyword_config_id: "kw-7", keyword: "抹茶粉", keyword_type: "primary", product_id: null, product_name: null, current_rank: 22, previous_rank: 19, rank_change: -3, target_rank: 15, target_gap: 7, last_tracked_at: new Date().toISOString() },
    { rank: 8, keyword_config_id: "kw-8", keyword: "日本飲料", keyword_type: "secondary", product_id: null, product_name: null, current_rank: 28, previous_rank: 32, rank_change: 4, target_rank: 20, target_gap: 8, last_tracked_at: new Date().toISOString() },
  ],
};

const MOCK_LEADERBOARD_HKTVMALL: RankingLeaderboardResponse = {
  source: "hktvmall",
  generated_at: new Date().toISOString(),
  summary: {
    total_keywords: 42,
    ranked_keywords: 32,
    unranked_keywords: 10,
    top_10_count: 15,
    top_30_count: 28,
    avg_rank: 12.3,
    improved_count: 10,
    declined_count: 6,
  },
  entries: [
    { rank: 1, keyword_config_id: "kw-1", keyword: "抹茶餅乾", keyword_type: "primary", product_id: null, product_name: null, current_rank: 1, previous_rank: 2, rank_change: 1, target_rank: 1, target_gap: 0, last_tracked_at: new Date().toISOString() },
    { rank: 2, keyword_config_id: "kw-2", keyword: "日本零食", keyword_type: "primary", product_id: null, product_name: null, current_rank: 2, previous_rank: 1, rank_change: -1, target_rank: 1, target_gap: 1, last_tracked_at: new Date().toISOString() },
    { rank: 3, keyword_config_id: "kw-3", keyword: "進口糖果", keyword_type: "secondary", product_id: null, product_name: null, current_rank: 4, previous_rank: 3, rank_change: -1, target_rank: 3, target_gap: 1, last_tracked_at: new Date().toISOString() },
    { rank: 4, keyword_config_id: "kw-4", keyword: "韓國零食", keyword_type: "primary", product_id: null, product_name: null, current_rank: 6, previous_rank: 8, rank_change: 2, target_rank: 5, target_gap: 1, last_tracked_at: new Date().toISOString() },
    { rank: 5, keyword_config_id: "kw-5", keyword: "日本糖果", keyword_type: "secondary", product_id: null, product_name: null, current_rank: 8, previous_rank: 6, rank_change: -2, target_rank: 5, target_gap: 3, last_tracked_at: new Date().toISOString() },
    { rank: 6, keyword_config_id: "kw-6", keyword: "抹茶粉", keyword_type: "primary", product_id: null, product_name: null, current_rank: 9, previous_rank: 12, rank_change: 3, target_rank: 8, target_gap: 1, last_tracked_at: new Date().toISOString() },
    { rank: 7, keyword_config_id: "kw-7", keyword: "日式零食禮盒", keyword_type: "long_tail", product_id: null, product_name: null, current_rank: 12, previous_rank: 15, rank_change: 3, target_rank: 10, target_gap: 2, last_tracked_at: new Date().toISOString() },
    { rank: 8, keyword_config_id: "kw-8", keyword: "進口餅乾", keyword_type: "secondary", product_id: null, product_name: null, current_rank: 15, previous_rank: 14, rank_change: -1, target_rank: 10, target_gap: 5, last_tracked_at: new Date().toISOString() },
  ],
};

export default function SEORankingPage() {
  const [selectedSource, setSelectedSource] = useState<RankingSource>("google_hk");
  const [days, setDays] = useState(7);
  const [useMockData, setUseMockData] = useState(false);

  // 獲取儀表板數據
  const { data: apiDashboard, isLoading, error, refetch } = useSEODashboard({ days });

  // 獲取排行榜數據
  const { data: apiLeaderboard, isLoading: isLoadingLeaderboard } = useLeaderboard({
    source: selectedSource,
    include_unranked: true,
    limit: 10,
  });

  // 觸發抓取
  const triggerScrape = useTriggerScrape();

  // 使用 mock 數據或 API 數據
  const dashboard = useMockData || error ? MOCK_DASHBOARD : apiDashboard;
  const leaderboard = useMockData || error
    ? (selectedSource === "google_hk" ? MOCK_LEADERBOARD_GOOGLE : MOCK_LEADERBOARD_HKTVMALL)
    : apiLeaderboard;

  const handleRefresh = () => {
    if (useMockData) {
      setUseMockData(false);
    }
    refetch();
  };

  const handleTriggerScrape = () => {
    triggerScrape.mutate({ job_type: "full" });
  };

  const handleUseMockData = () => {
    setUseMockData(true);
  };

  // 加載狀態
  if (isLoading && !useMockData) {
    return (
      <PageTransition>
        <div className="space-y-6 p-6">
          <div className="flex items-center justify-between">
            <HoloSkeleton className="h-8 w-48" />
            <HoloSkeleton className="h-10 w-32" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <HoloSkeleton key={i} className="h-32" />
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <HoloSkeleton className="h-96" />
            <HoloSkeleton className="h-96" />
          </div>
        </div>
      </PageTransition>
    );
  }

  // 錯誤狀態 - 提供使用 mock 數據的選項
  if (error && !useMockData) {
    return (
      <PageTransition>
        <div className="p-6">
          <HoloCard className="p-8 text-center">
            <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">載入失敗</h2>
            <p className="text-gray-400 mb-4">無法獲取 SEO 排名數據</p>
            <div className="flex justify-center gap-3">
              <HoloButton onClick={handleRefresh}>重試</HoloButton>
              <HoloButton variant="secondary" onClick={handleUseMockData}>
                使用演示數據
              </HoloButton>
            </div>
          </HoloCard>
        </div>
      </PageTransition>
    );
  }

  const overview = dashboard?.overview;
  const googleRankings = dashboard?.google_rankings;
  const hktvmallRankings = dashboard?.hktvmall_rankings;

  return (
    <PageTransition>
      <div className="space-y-6 p-6">
        {/* ==================== Mock 數據提示 ==================== */}
        {useMockData && (
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span className="text-amber-200 text-sm">
                目前顯示演示數據，數據僅供展示用途
              </span>
            </div>
            <button
              onClick={handleRefresh}
              className="text-amber-400 hover:text-amber-300 text-sm underline"
            >
              嘗試重新載入
            </button>
          </div>
        )}

        {/* ==================== 頁面標題 ==================== */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Search className="w-6 h-6 text-cyan-400" />
              SEO 排名追蹤
              {useMockData && (
                <HoloBadge variant="warning" size="sm">演示模式</HoloBadge>
              )}
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              監控關鍵詞在 Google 香港和 HKTVmall 的排名表現
            </p>
          </div>
          <div className="flex items-center gap-3">
            {/* 時間範圍選擇 */}
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500"
            >
              <option value={7}>最近 7 天</option>
              <option value={14}>最近 14 天</option>
              <option value={30}>最近 30 天</option>
              <option value={90}>最近 90 天</option>
            </select>
            {/* 觸發抓取 */}
            <HoloButton
              variant="secondary"
              onClick={handleTriggerScrape}
              disabled={triggerScrape.isPending}
            >
              {triggerScrape.isPending ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  抓取中...
                </>
              ) : (
                <>
                  <Target className="w-4 h-4 mr-2" />
                  開始抓取
                </>
              )}
            </HoloButton>
            {/* 刷新 */}
            <HoloButton variant="ghost" onClick={handleRefresh}>
              <RefreshCw className="w-4 h-4" />
            </HoloButton>
          </div>
        </div>

        {/* ==================== 概覽指標 ==================== */}
        <StaggerContainer className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* SEO 健康分數 */}
          <HoloCard className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-xs uppercase tracking-wider">SEO 健康分數</p>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-3xl font-bold text-white">
                    {overview?.seo_health_score || 0}
                  </span>
                  <span className="text-gray-500 text-sm">/ 100</span>
                </div>
              </div>
              <ProgressRing
                progress={overview?.seo_health_score || 0}
                size={56}
                strokeWidth={4}
                color={
                  (overview?.seo_health_score || 0) >= 70
                    ? "green"
                    : (overview?.seo_health_score || 0) >= 40
                    ? "cyan"
                    : "purple"
                }
              />
            </div>
          </HoloCard>

          {/* 追蹤關鍵詞數 */}
          <HoloCard className="p-4">
            <DataMetric
              label="追蹤關鍵詞"
              value={overview?.total_keywords || 0}
              suffix={` / ${overview?.active_keywords || 0} 啟用`}
              color="cyan"
            />
          </HoloCard>

          {/* 排名上升 */}
          <HoloCard className="p-4">
            <DataMetric
              label="排名上升"
              value={overview?.improved_keywords || 0}
              icon={<TrendingUp className="w-5 h-5" />}
              color="green"
            />
          </HoloCard>

          {/* 排名下降 */}
          <HoloCard className="p-4">
            <DataMetric
              label="排名下降"
              value={overview?.declined_keywords || 0}
              icon={<TrendingDown className="w-5 h-5" />}
              color="orange"
            />
          </HoloCard>
        </StaggerContainer>

        {/* ==================== 排名摘要卡片 ==================== */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Google 排名摘要 */}
          <HoloCard>
            <HoloPanelHeader
              title="Google 香港"
              subtitle="搜尋引擎排名表現"
              icon={<Search className="w-5 h-5" />}
            />
            <div className="p-4 space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-cyan-400">
                    {googleRankings?.ranked_keywords || 0}
                  </p>
                  <p className="text-xs text-gray-500">已有排名</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-400">
                    {googleRankings?.top_10_count || 0}
                  </p>
                  <p className="text-xs text-gray-500">Top 10</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-400">
                    {googleRankings?.avg_rank?.toFixed(1) || "-"}
                  </p>
                  <p className="text-xs text-gray-500">平均排名</p>
                </div>
              </div>
              <TechDivider />
              <div className="flex justify-between text-sm">
                <div>
                  <span className="text-gray-500">最佳關鍵詞: </span>
                  {googleRankings?.best_keyword ? (
                    <span className="text-green-400">
                      {googleRankings.best_keyword.keyword} (#{googleRankings.best_keyword.rank})
                    </span>
                  ) : (
                    <span className="text-gray-600">-</span>
                  )}
                </div>
              </div>
            </div>
          </HoloCard>

          {/* HKTVmall 排名摘要 */}
          <HoloCard>
            <HoloPanelHeader
              title="HKTVmall"
              subtitle="站內搜尋排名表現"
              icon={<Target className="w-5 h-5" />}
            />
            <div className="p-4 space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-cyan-400">
                    {hktvmallRankings?.ranked_keywords || 0}
                  </p>
                  <p className="text-xs text-gray-500">已有排名</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-400">
                    {hktvmallRankings?.top_10_count || 0}
                  </p>
                  <p className="text-xs text-gray-500">Top 10</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-purple-400">
                    {hktvmallRankings?.avg_rank?.toFixed(1) || "-"}
                  </p>
                  <p className="text-xs text-gray-500">平均排名</p>
                </div>
              </div>
              <TechDivider />
              <div className="flex justify-between text-sm">
                <div>
                  <span className="text-gray-500">最佳關鍵詞: </span>
                  {hktvmallRankings?.best_keyword ? (
                    <span className="text-green-400">
                      {hktvmallRankings.best_keyword.keyword} (#{hktvmallRankings.best_keyword.rank})
                    </span>
                  ) : (
                    <span className="text-gray-600">-</span>
                  )}
                </div>
              </div>
            </div>
          </HoloCard>
        </div>

        {/* ==================== 排行榜 ==================== */}
        <HoloCard>
          <HoloPanelHeader
            title="關鍵詞排行榜"
            subtitle="按當前排名排序"
            icon={<TrendingUp className="w-5 h-5" />}
            action={
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setSelectedSource("google_hk")}
                  className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                    selectedSource === "google_hk"
                      ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/50"
                      : "text-gray-400 hover:text-white"
                  }`}
                >
                  Google
                </button>
                <button
                  onClick={() => setSelectedSource("hktvmall")}
                  className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
                    selectedSource === "hktvmall"
                      ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/50"
                      : "text-gray-400 hover:text-white"
                  }`}
                >
                  HKTVmall
                </button>
              </div>
            }
          />
          <div className="p-4">
            <LeaderboardTable
              entries={leaderboard?.entries || []}
              isLoading={isLoadingLeaderboard}
              source={selectedSource}
            />
          </div>
        </HoloCard>

        {/* ==================== 警報與任務 ==================== */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 最近警報 */}
          <HoloCard>
            <HoloPanelHeader
              title="排名警報"
              subtitle="需要關注的排名變化"
              icon={<AlertTriangle className="w-5 h-5" />}
              action={
                dashboard?.recent_alerts?.filter((a) => !a.is_read).length ? (
                  <HoloBadge variant="warning" pulse>
                    {dashboard.recent_alerts.filter((a) => !a.is_read).length} 未讀
                  </HoloBadge>
                ) : null
              }
            />
            <div className="p-4">
              <AlertsList alerts={dashboard?.recent_alerts || []} />
            </div>
          </HoloCard>

          {/* 最近任務 */}
          <HoloCard>
            <HoloPanelHeader
              title="抓取任務"
              subtitle="最近的排名抓取任務"
              icon={<Clock className="w-5 h-5" />}
            />
            <div className="p-4">
              <ScrapeJobsList jobs={dashboard?.recent_jobs || []} />
            </div>
          </HoloCard>
        </div>

        {/* ==================== 最後抓取時間 ==================== */}
        {overview?.last_scrape_at && (
          <div className="text-center text-sm text-gray-500">
            最後抓取時間:{" "}
            {new Date(overview.last_scrape_at).toLocaleString("zh-TW", {
              year: "numeric",
              month: "2-digit",
              day: "2-digit",
              hour: "2-digit",
              minute: "2-digit",
            })}
          </div>
        )}
      </div>
    </PageTransition>
  );
}
