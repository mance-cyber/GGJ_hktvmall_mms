"use client";

// =============================================
// 排行榜表格組件
// =============================================

import { TrendingUp, TrendingDown, Minus, ExternalLink } from "lucide-react";
import { HoloBadge, HoloSkeleton } from "@/components/ui/future-tech";
import { LeaderboardEntry, RankingSource } from "@/lib/api/seo-ranking";
import Link from "next/link";

interface LeaderboardTableProps {
  entries: LeaderboardEntry[];
  isLoading?: boolean;
  source: RankingSource;
}

export function LeaderboardTable({ entries, isLoading, source }: LeaderboardTableProps) {
  if (isLoading) {
    return (
      <div className="space-y-2">
        {[...Array(5)].map((_, i) => (
          <HoloSkeleton key={i} className="h-12" />
        ))}
      </div>
    );
  }

  if (entries.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>暫無排名數據</p>
        <p className="text-sm mt-1">開始追蹤關鍵詞以查看排名</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="text-left text-xs text-gray-500 uppercase tracking-wider border-b border-gray-800">
            <th className="pb-3 pl-2">#</th>
            <th className="pb-3">關鍵詞</th>
            <th className="pb-3 text-center">類型</th>
            <th className="pb-3 text-right">當前排名</th>
            <th className="pb-3 text-right">變化</th>
            <th className="pb-3 text-right">目標</th>
            <th className="pb-3 text-right">差距</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800/50">
          {entries.map((entry) => (
            <tr
              key={entry.keyword_config_id}
              className="group hover:bg-cyan-500/5 transition-colors"
            >
              {/* 排名位置 */}
              <td className="py-3 pl-2">
                <span className="text-gray-500 text-sm">{entry.rank}</span>
              </td>

              {/* 關鍵詞 */}
              <td className="py-3">
                <Link
                  href={`/seo-ranking/keywords/${entry.keyword_config_id}`}
                  className="text-white hover:text-cyan-400 transition-colors flex items-center gap-1"
                >
                  {entry.keyword}
                  <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-50" />
                </Link>
              </td>

              {/* 類型 */}
              <td className="py-3 text-center">
                <KeywordTypeBadge type={entry.keyword_type} />
              </td>

              {/* 當前排名 */}
              <td className="py-3 text-right">
                {entry.current_rank ? (
                  <span className={getRankColor(entry.current_rank)}>
                    #{entry.current_rank}
                  </span>
                ) : (
                  <span className="text-gray-600">-</span>
                )}
              </td>

              {/* 排名變化 */}
              <td className="py-3 text-right">
                <RankChange change={entry.rank_change} />
              </td>

              {/* 目標排名 */}
              <td className="py-3 text-right">
                {entry.target_rank ? (
                  <span className="text-purple-400">#{entry.target_rank}</span>
                ) : (
                  <span className="text-gray-600">-</span>
                )}
              </td>

              {/* 目標差距 */}
              <td className="py-3 text-right">
                {entry.target_gap !== null ? (
                  <span
                    className={
                      entry.target_gap <= 0 ? "text-green-400" : "text-amber-400"
                    }
                  >
                    {entry.target_gap <= 0 ? "已達成" : `還差 ${entry.target_gap}`}
                  </span>
                ) : (
                  <span className="text-gray-600">-</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ==================== 輔助組件 ====================

function KeywordTypeBadge({ type }: { type: string }) {
  const config: Record<string, { label: string; variant: "default" | "info" | "success" | "warning" | "error" }> = {
    primary: { label: "主要", variant: "info" },
    secondary: { label: "次要", variant: "default" },
    long_tail: { label: "長尾", variant: "success" },
    brand: { label: "品牌", variant: "warning" },
    competitor: { label: "競品", variant: "error" },
  };

  const { label, variant } = config[type] || { label: type, variant: "default" };

  return <HoloBadge variant={variant}>{label}</HoloBadge>;
}

function RankChange({ change }: { change: number | null }) {
  if (change === null || change === 0) {
    return (
      <span className="text-gray-500 flex items-center justify-end gap-1">
        <Minus className="w-3 h-3" />
        <span>-</span>
      </span>
    );
  }

  if (change > 0) {
    return (
      <span className="text-green-400 flex items-center justify-end gap-1">
        <TrendingUp className="w-3 h-3" />
        <span>+{change}</span>
      </span>
    );
  }

  return (
    <span className="text-red-400 flex items-center justify-end gap-1">
      <TrendingDown className="w-3 h-3" />
      <span>{change}</span>
    </span>
  );
}

function getRankColor(rank: number): string {
  if (rank <= 3) return "text-green-400 font-bold";
  if (rank <= 10) return "text-cyan-400";
  if (rank <= 30) return "text-white";
  return "text-gray-400";
}
