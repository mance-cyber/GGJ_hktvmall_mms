"use client";

// =============================================
// Ranking Alerts List Component
// =============================================

import { AlertTriangle, AlertCircle, Info, TrendingDown, TrendingUp, Check } from "lucide-react";
import { HoloBadge } from "@/components/ui/future-tech";
import { RankingAlert } from "@/lib/api/seo-ranking";
import { useMarkAlertRead } from "../hooks/useSEORanking";

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

interface AlertsListProps {
  alerts: RankingAlert[];
}

export function AlertsList({ alerts }: AlertsListProps) {
  const markRead = useMarkAlertRead();

  if (alerts.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Check className="w-8 h-8 mx-auto mb-2 text-green-500" />
        <p>No alerts requiring attention</p>
      </div>
    );
  }

  const handleMarkRead = (alertId: string) => {
    markRead.mutate(alertId);
  };

  return (
    <div className="space-y-3">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className={`p-3 rounded-lg border transition-colors cursor-pointer ${
            alert.is_read
              ? "bg-slate-50 border-slate-200 opacity-60"
              : "bg-white border-slate-200 hover:border-cyan-400 hover:shadow-sm"
          }`}
          onClick={() => !alert.is_read && handleMarkRead(alert.id)}
        >
          <div className="flex items-start gap-3">
            {/* Icon */}
            <div className="flex-shrink-0 mt-0.5">
              <AlertIcon severity={alert.severity} />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              {/* Title Row */}
              <div className="flex items-center gap-2 mb-1">
                <span className="text-slate-800 font-medium text-sm truncate">
                  {alert.keyword}
                </span>
                <SeverityBadge severity={alert.severity} />
                <SourceBadge source={alert.source} />
              </div>

              {/* Message */}
              <p className="text-slate-600 text-sm">{alert.message}</p>

              {/* Rank Change */}
              {alert.previous_rank && alert.current_rank && (
                <div className="flex items-center gap-2 mt-2 text-xs">
                  <span className="text-slate-500">
                    #{alert.previous_rank} → #{alert.current_rank}
                  </span>
                  <RankChangeIndicator change={alert.rank_change} />
                </div>
              )}

              {/* Timestamp */}
              <p className="text-slate-400 text-xs mt-2">
                {formatTimeAgo(new Date(alert.created_at))}
              </p>
            </div>

            {/* Unread Indicator */}
            {!alert.is_read && (
              <div className="w-2 h-2 rounded-full bg-cyan-500 flex-shrink-0 animate-pulse" />
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

// ==================== Helper Components ====================

function AlertIcon({ severity }: { severity: string }) {
  switch (severity) {
    case "critical":
      return <AlertTriangle className="w-5 h-5 text-red-500" />;
    case "warning":
      return <AlertCircle className="w-5 h-5 text-amber-500" />;
    default:
      return <Info className="w-5 h-5 text-blue-500" />;
  }
}

function SeverityBadge({ severity }: { severity: string }) {
  const config: Record<string, { label: string; variant: "default" | "info" | "success" | "warning" | "error" }> = {
    critical: { label: "Critical", variant: "error" },
    warning: { label: "Warning", variant: "warning" },
    info: { label: "Info", variant: "info" },
  };

  const { label, variant } = config[severity] || { label: severity, variant: "default" };

  return <HoloBadge variant={variant}>{label}</HoloBadge>;
}

function SourceBadge({ source }: { source: string }) {
  const label = source === "google_hk" ? "Google" : "HKTVmall";
  return (
    <span className="text-xs px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
      {label}
    </span>
  );
}

function RankChangeIndicator({ change }: { change: number | null }) {
  if (change === null || change === 0) return null;

  if (change > 0) {
    return (
      <span className="text-emerald-600 flex items-center gap-0.5">
        <TrendingUp className="w-3 h-3" />
        Up {change} positions
      </span>
    );
  }

  return (
    <span className="text-red-500 flex items-center gap-0.5">
      <TrendingDown className="w-3 h-3" />
      Down {Math.abs(change)} positions
    </span>
  );
}
