"use client";

// =============================================
// Scrape Jobs List Component
// =============================================

import { Clock, CheckCircle, XCircle, Loader2, PlayCircle } from "lucide-react";
import { HoloBadge, ProgressRing } from "@/components/ui/future-tech";
import { RankingScrapeJob } from "@/lib/api/seo-ranking";

// Time formatting utility
function formatTimeAgo(date: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) return "Just now";
  if (diffMin < 60) return `${diffMin} min ago`;
  if (diffHour < 24) return `${diffHour} hr ago`;
  if (diffDay < 30) return `${diffDay} days ago`;
  return date.toLocaleDateString("en-US");
}

interface ScrapeJobsListProps {
  jobs: RankingScrapeJob[];
}

export function ScrapeJobsList({ jobs }: ScrapeJobsListProps) {
  if (jobs.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Clock className="w-8 h-8 mx-auto mb-2 text-gray-600" />
        <p>No scrape jobs available</p>
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
            {/* Status Icon */}
            <div className="flex-shrink-0">
              <StatusIcon status={job.status} progress={job.progress_percent} />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              {/* Title Row */}
              <div className="flex items-center gap-2 mb-1">
                <span className="text-slate-800 font-medium text-sm">
                  {getJobTypeLabel(job.job_type)}
                </span>
                <StatusBadge status={job.status} />
              </div>

              {/* Progress Info */}
              <div className="flex items-center gap-4 text-xs text-slate-500">
                <span>
                  {job.processed_keywords} / {job.total_keywords} keywords
                </span>
                {job.success_rate !== null && (
                  <span className="text-emerald-600">
                    Success rate {job.success_rate}%
                  </span>
                )}
                {job.duration_seconds !== null && (
                  <span>Duration: {formatDuration(job.duration_seconds)}</span>
                )}
              </div>

              {/* Error Info */}
              {job.errors && job.errors.length > 0 && (
                <p className="text-red-500 text-xs mt-1">
                  {job.errors.length} error(s)
                </p>
              )}

              {/* Time */}
              <p className="text-slate-400 text-xs mt-2">
                {job.completed_at
                  ? `Completed ${formatTimeAgo(new Date(job.completed_at))}`
                  : job.started_at
                  ? `Started ${formatTimeAgo(new Date(job.started_at))}`
                  : `Created ${formatTimeAgo(new Date(job.created_at))}`}
              </p>
            </div>

            {/* Progress indicator (shown when in progress) */}
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

// ==================== Helper Components ====================

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
    completed: { label: "Completed", variant: "success" },
    failed: { label: "Failed", variant: "error" },
    running: { label: "In Progress", variant: "info" },
    pending: { label: "Waiting", variant: "warning" },
  };

  const { label, variant } = config[status] || {
    label: status,
    variant: "default",
  };

  return <HoloBadge variant={variant}>{label}</HoloBadge>;
}

function getJobTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    full: "Full Scrape",
    google_only: "Google Scrape",
    hktvmall_only: "HKTVmall Scrape",
    selective: "Selective Scrape",
  };
  return labels[type] || type;
}

function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${seconds}s`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  if (minutes < 60) {
    return remainingSeconds > 0
      ? `${minutes}m ${remainingSeconds}s`
      : `${minutes}m`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return `${hours}h ${remainingMinutes}m`;
}
