"use client";

// =============================================
// Leaderboard Table Component
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
        <p>No ranking data available</p>
        <p className="text-sm mt-1">Start tracking keywords to see rankings</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="text-left text-xs text-slate-500 uppercase tracking-wider border-b border-slate-200">
            <th className="pb-3 pl-2">#</th>
            <th className="pb-3">Keyword</th>
            <th className="pb-3 text-center">Type</th>
            <th className="pb-3 text-right">Current Rank</th>
            <th className="pb-3 text-right">Change</th>
            <th className="pb-3 text-right">Target</th>
            <th className="pb-3 text-right">Gap</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {entries.map((entry) => (
            <tr
              key={entry.keyword_config_id}
              className="group hover:bg-cyan-50/50 transition-colors"
            >
              {/* Rank Position */}
              <td className="py-3 pl-2">
                <span className="text-slate-400 text-sm">{entry.rank}</span>
              </td>

              {/* Keyword */}
              <td className="py-3">
                <Link
                  href={`/seo-ranking/keywords/${entry.keyword_config_id}`}
                  className="text-slate-800 font-medium hover:text-cyan-600 transition-colors flex items-center gap-1"
                >
                  {entry.keyword}
                  <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-50" />
                </Link>
              </td>

              {/* Type */}
              <td className="py-3 text-center">
                <KeywordTypeBadge type={entry.keyword_type} />
              </td>

              {/* Current Rank */}
              <td className="py-3 text-right">
                {entry.current_rank ? (
                  <span className={getRankColor(entry.current_rank)}>
                    #{entry.current_rank}
                  </span>
                ) : (
                  <span className="text-slate-400">-</span>
                )}
              </td>

              {/* Rank Change */}
              <td className="py-3 text-right">
                <RankChange change={entry.rank_change} />
              </td>

              {/* Target Rank */}
              <td className="py-3 text-right">
                {entry.target_rank ? (
                  <span className="text-purple-600 font-medium">#{entry.target_rank}</span>
                ) : (
                  <span className="text-slate-400">-</span>
                )}
              </td>

              {/* Target Gap */}
              <td className="py-3 text-right">
                {entry.target_gap !== null ? (
                  <span
                    className={
                      entry.target_gap <= 0 ? "text-emerald-600 font-medium" : "text-amber-600"
                    }
                  >
                    {entry.target_gap <= 0 ? "Achieved" : `${entry.target_gap} to go`}
                  </span>
                ) : (
                  <span className="text-slate-400">-</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ==================== Helper Components ====================

function KeywordTypeBadge({ type }: { type: string }) {
  const config: Record<string, { label: string; variant: "default" | "info" | "success" | "warning" | "error" }> = {
    primary: { label: "Primary", variant: "info" },
    secondary: { label: "Secondary", variant: "default" },
    long_tail: { label: "Long-tail", variant: "success" },
    brand: { label: "Brand", variant: "warning" },
    competitor: { label: "Competitor", variant: "error" },
  };

  const { label, variant } = config[type] || { label: type, variant: "default" };

  return <HoloBadge variant={variant}>{label}</HoloBadge>;
}

function RankChange({ change }: { change: number | null }) {
  if (change === null || change === 0) {
    return (
      <span className="text-slate-400 flex items-center justify-end gap-1">
        <Minus className="w-3 h-3" />
        <span>-</span>
      </span>
    );
  }

  if (change > 0) {
    return (
      <span className="text-emerald-600 flex items-center justify-end gap-1">
        <TrendingUp className="w-3 h-3" />
        <span>+{change}</span>
      </span>
    );
  }

  return (
    <span className="text-red-500 flex items-center justify-end gap-1">
      <TrendingDown className="w-3 h-3" />
      <span>{change}</span>
    </span>
  );
}

function getRankColor(rank: number): string {
  if (rank <= 3) return "text-emerald-600 font-bold";
  if (rank <= 10) return "text-cyan-600 font-medium";
  if (rank <= 30) return "text-slate-700";
  return "text-slate-500";
}
