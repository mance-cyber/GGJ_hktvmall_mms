"use client";

// =============================================
// 抓取任務列表組件
// =============================================

import { Clock, CheckCircle, XCircle, Loader2, PlayCircle } from "lucide-react";
import { HoloBadge, ProgressRing } from "@/components/ui/future-tech";
import { RankingScrapeJob } from "@/lib/api/seo-ranking";

// 時間格式化工具
function formatTimeAgo(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) return "剛剛";
  if (diffMin < 60) return `${diffMin} 分鐘前`;
  if (diffHour < 24) return `${diffHour} 小時前`;
  if (diffDay < 30) return `${diffDay} 天前`;
  return date.toLocaleDateString("zh-TW");
}

interface ScrapeJobsListProps {
  jobs: RankingScrapeJob[];
}

export function ScrapeJobsList({ jobs }: ScrapeJobsListProps) {
  if (jobs.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Clock className="w-8 h-8 mx-auto mb-2 text-gray-600" />
        <p>暫無抓取任務</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {jobs.map((job) => (
        <div
          key={job.id}
          className="p-3 rounded-lg bg-white border border-slate-200 hover:border-cyan-400 hover:shadow-sm transition-colors"
        >
          <div className="flex items-center gap-3">
            {/* 狀態圖標 */}
            <div className="flex-shrink-0">
              <StatusIcon status={job.status} progress={job.progress_percent} />
            </div>

            {/* 內容 */}
            <div className="flex-1 min-w-0">
              {/* 標題行 */}
              <div className="flex items-center gap-2 mb-1">
                <span className="text-slate-800 font-medium text-sm">
                  {getJobTypeLabel(job.job_type)}
                </span>
                <StatusBadge status={job.status} />
              </div>

              {/* 進度信息 */}
              <div className="flex items-center gap-4 text-xs text-slate-500">
                <span>
                  {job.processed_keywords} / {job.total_keywords} 關鍵詞
                </span>
                {job.success_rate !== null && (
                  <span className="text-emerald-600">
                    成功率 {job.success_rate}%
                  </span>
                )}
                {job.duration_seconds !== null && (
                  <span>耗時 {formatDuration(job.duration_seconds)}</span>
                )}
              </div>

              {/* 錯誤信息 */}
              {job.errors && job.errors.length > 0 && (
                <p className="text-red-500 text-xs mt-1">
                  {job.errors.length} 個錯誤
                </p>
              )}

              {/* 時間 */}
              <p className="text-slate-400 text-xs mt-2">
                {job.completed_at
                  ? `完成於 ${formatTimeAgo(new Date(job.completed_at))}`
                  : job.started_at
                  ? `開始於 ${formatTimeAgo(new Date(job.started_at))}`
                  : `建立於 ${formatTimeAgo(new Date(job.created_at))}`}
              </p>
            </div>

            {/* 進度指示器（進行中時顯示） */}
            {(job.status === "running" || job.status === "pending") && (
              <div className="flex-shrink-0">
                <ProgressRing
                  progress={job.progress_percent}
                  size={40}
                  strokeWidth={3}
                  color="cyan"
                  showLabel
                />
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

// ==================== 輔助組件 ====================

function StatusIcon({
  status,
  progress,
}: {
  status: string;
  progress: number;
}) {
  switch (status) {
    case "completed":
      return <CheckCircle className="w-5 h-5 text-emerald-500" />;
    case "failed":
      return <XCircle className="w-5 h-5 text-red-500" />;
    case "running":
      return <Loader2 className="w-5 h-5 text-cyan-500 animate-spin" />;
    case "pending":
      return <PlayCircle className="w-5 h-5 text-amber-500" />;
    default:
      return <Clock className="w-5 h-5 text-slate-400" />;
  }
}

function StatusBadge({ status }: { status: string }) {
  const config: Record<
    string,
    { label: string; variant: "default" | "info" | "success" | "warning" | "error" }
  > = {
    completed: { label: "已完成", variant: "success" },
    failed: { label: "失敗", variant: "error" },
    running: { label: "進行中", variant: "info" },
    pending: { label: "等待中", variant: "warning" },
  };

  const { label, variant } = config[status] || {
    label: status,
    variant: "default",
  };

  return <HoloBadge variant={variant}>{label}</HoloBadge>;
}

function getJobTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    full: "完整抓取",
    google_only: "Google 抓取",
    hktvmall_only: "HKTVmall 抓取",
    selective: "選擇性抓取",
  };
  return labels[type] || type;
}

function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds}秒`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  if (minutes < 60) {
    return remainingSeconds > 0
      ? `${minutes}分${remainingSeconds}秒`
      : `${minutes}分鐘`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}小時${remainingMinutes}分`;
}
