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
import { RankingSource } from "@/lib/api/seo-ranking";
import { LeaderboardTable } from "./components/LeaderboardTable";
import { AlertsList } from "./components/AlertsList";
import { ScrapeJobsList } from "./components/ScrapeJobsList";

export default function SEORankingPage() {
  const [selectedSource, setSelectedSource] = useState<RankingSource>("google_hk");
  const [days, setDays] = useState(7);

  // 獲取儀表板數據
  const { data: dashboard, isLoading, error, refetch } = useSEODashboard({ days });

  // 獲取排行榜數據
  const { data: leaderboard, isLoading: isLoadingLeaderboard } = useLeaderboard({
    source: selectedSource,
    include_unranked: true,
    limit: 10,
  });

  // 觸發抓取
  const triggerScrape = useTriggerScrape();

  const handleRefresh = () => {
    refetch();
  };

  const handleTriggerScrape = () => {
    triggerScrape.mutate({ job_type: "full" });
  };

  // 加載狀態
  if (isLoading) {
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

  // 錯誤狀態
  if (error) {
    return (
      <PageTransition>
        <div className="p-6">
          <HoloCard className="p-8 text-center">
            <AlertTriangle className="w-12 h-12 text-amber-500 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">載入失敗</h2>
            <p className="text-gray-400 mb-4">無法獲取 SEO 排名數據</p>
            <HoloButton onClick={handleRefresh}>重試</HoloButton>
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
        {/* ==================== 頁面標題 ==================== */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Search className="w-6 h-6 text-cyan-400" />
              SEO 排名追蹤
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
