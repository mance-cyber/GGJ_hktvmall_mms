"use client";

// =============================================
// 排名警報列表組件
// =============================================

import { AlertTriangle, AlertCircle, Info, TrendingDown, TrendingUp, Check } from "lucide-react";
import { HoloBadge } from "@/components/ui/future-tech";
import { RankingAlert } from "@/lib/api/seo-ranking";
import { useMarkAlertRead } from "../hooks/useSEORanking";
import { formatDistanceToNow } from "date-fns";
import { zhTW } from "date-fns/locale";

interface AlertsListProps {
  alerts: RankingAlert[];
}

export function AlertsList({ alerts }: AlertsListProps) {
  const markRead = useMarkAlertRead();

  if (alerts.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <Check className="w-8 h-8 mx-auto mb-2 text-green-500" />
        <p>沒有需要關注的警報</p>
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
              ? "bg-gray-900/30 border-gray-800 opacity-60"
              : "bg-gray-900/50 border-gray-700 hover:border-cyan-500/30"
          }`}
          onClick={() => !alert.is_read && handleMarkRead(alert.id)}
        >
          <div className="flex items-start gap-3">
            {/* 圖標 */}
            <div className="flex-shrink-0 mt-0.5">
              <AlertIcon severity={alert.severity} />
            </div>

            {/* 內容 */}
            <div className="flex-1 min-w-0">
              {/* 標題行 */}
              <div className="flex items-center gap-2 mb-1">
                <span className="text-white font-medium text-sm truncate">
                  {alert.keyword}
                </span>
                <SeverityBadge severity={alert.severity} />
                <SourceBadge source={alert.source} />
              </div>

              {/* 消息 */}
              <p className="text-gray-400 text-sm">{alert.message}</p>

              {/* 排名變化 */}
              {alert.previous_rank && alert.current_rank && (
                <div className="flex items-center gap-2 mt-2 text-xs">
                  <span className="text-gray-500">
                    #{alert.previous_rank} → #{alert.current_rank}
                  </span>
                  <RankChangeIndicator change={alert.rank_change} />
                </div>
              )}

              {/* 時間 */}
              <p className="text-gray-600 text-xs mt-2">
                {formatDistanceToNow(new Date(alert.created_at), {
                  addSuffix: true,
                  locale: zhTW,
                })}
              </p>
            </div>

            {/* 未讀指示 */}
            {!alert.is_read && (
              <div className="w-2 h-2 rounded-full bg-cyan-400 flex-shrink-0 animate-pulse" />
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

// ==================== 輔助組件 ====================

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
    critical: { label: "嚴重", variant: "error" },
    warning: { label: "警告", variant: "warning" },
    info: { label: "資訊", variant: "info" },
  };

  const { label, variant } = config[severity] || { label: severity, variant: "default" };

  return <HoloBadge variant={variant}>{label}</HoloBadge>;
}

function SourceBadge({ source }: { source: string }) {
  const label = source === "google_hk" ? "Google" : "HKTVmall";
  return (
    <span className="text-xs px-1.5 py-0.5 rounded bg-gray-800 text-gray-400">
      {label}
    </span>
  );
}

function RankChangeIndicator({ change }: { change: number | null }) {
  if (change === null || change === 0) return null;

  if (change > 0) {
    return (
      <span className="text-green-400 flex items-center gap-0.5">
        <TrendingUp className="w-3 h-3" />
        上升 {change} 名
      </span>
    );
  }

  return (
    <span className="text-red-400 flex items-center gap-0.5">
      <TrendingDown className="w-3 h-3" />
      下降 {Math.abs(change)} 名
    </span>
  );
}
