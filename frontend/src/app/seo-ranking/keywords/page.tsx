"use client";

// =============================================
// Keyword Management Page
// =============================================

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useLocale } from "@/components/providers/locale-provider";
import {
  Search,
  Plus,
  Filter,
  Trash2,
  Edit2,
  MoreHorizontal,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-react";
import {
  PageTransition,
  HoloCard,
  HoloPanelHeader,
  HoloButton,
  HoloBadge,
  HoloSkeleton,
} from "@/components/ui/future-tech";
import {
  useKeywordConfigs,
  useDeleteKeywordConfig,
  useUpdateKeywordConfig,
} from "../hooks/useSEORanking";
import { KeywordConfig, KeywordType } from "@/lib/api/seo-ranking";
import { KeywordConfigDialog } from "../components/KeywordConfigDialog";

export default function KeywordsPage() {
  const { t } = useLocale();
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<KeywordType | "">("");
  const [activeFilter, setActiveFilter] = useState<boolean | undefined>(undefined);
  const [page, setPage] = useState(1);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingKeyword, setEditingKeyword] = useState<KeywordConfig | null>(null);

  // Fetch keyword list
  const { data, isLoading, refetch } = useKeywordConfigs({
    search: search || undefined,
    keyword_type: typeFilter || undefined,
    is_active: activeFilter,
    page,
    page_size: 20,
  });

  // Delete keyword
  const deleteKeyword = useDeleteKeywordConfig();

  // Update keyword
  const updateKeyword = useUpdateKeywordConfig();

  const handleDelete = async (id: string) => {
    if (confirm(t('keywords.confirm_delete'))) {
      await deleteKeyword.mutateAsync(id);
    }
  };

  const handleToggleActive = async (keyword: KeywordConfig) => {
    await updateKeyword.mutateAsync({
      id: keyword.id,
      data: { is_active: !keyword.is_active },
    });
  };

  const handleEdit = (keyword: KeywordConfig) => {
    setEditingKeyword(keyword);
    setIsDialogOpen(true);
  };

  const handleCreate = () => {
    setEditingKeyword(null);
    setIsDialogOpen(true);
  };

  const handleDialogClose = () => {
    setIsDialogOpen(false);
    setEditingKeyword(null);
  };

  return (
    <PageTransition>
      <div className="space-y-6 p-6">
        {/* ==================== Page title ==================== */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Search className="w-6 h-6 text-cyan-400" />
              {t('keywords.title')}
            </h1>
            <p className="text-gray-400 text-sm mt-1">
              {t('keywords.subtitle')}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <HoloButton onClick={handleCreate}>
              <Plus className="w-4 h-4 mr-2" />
              {t('keywords.add')}
            </HoloButton>
            <HoloButton variant="ghost" onClick={() => refetch()}>
              <RefreshCw className="w-4 h-4" />
            </HoloButton>
          </div>
        </div>

        {/* ==================== Filter Panel ==================== */}
        <HoloCard className="p-4">
          <div className="flex flex-wrap items-center gap-4">
            {/* Search */}
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder={t('keywords.search_placeholder')}
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
                className="w-full bg-gray-800/50 border border-cyan-500/30 rounded-lg pl-10 pr-4 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
              />
            </div>

            {/* Type Filter */}
            <select
              value={typeFilter}
              onChange={(e) => {
                setTypeFilter(e.target.value as KeywordType | "");
                setPage(1);
              }}
              className="bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="">{t('keywords.filter_all_types')}</option>
              <option value="primary">{t('keywords.type_primary')}</option>
              <option value="secondary">{t('keywords.type_secondary')}</option>
              <option value="long_tail">{t('keywords.type_long_tail')}</option>
              <option value="brand">{t('keywords.type_brand')}</option>
              <option value="competitor">{t('keywords.type_competitor')}</option>
            </select>

            {/* Status Filter */}
            <select
              value={activeFilter === undefined ? "" : activeFilter ? "active" : "inactive"}
              onChange={(e) => {
                const val = e.target.value;
                setActiveFilter(val === "" ? undefined : val === "active");
                setPage(1);
              }}
              className="bg-gray-800/50 border border-cyan-500/30 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500"
            >
              <option value="">{t('keywords.filter_all_statuses')}</option>
              <option value="active">{t('keywords.status_active')}</option>
              <option value="inactive">{t('keywords.status_inactive')}</option>
            </select>
          </div>
        </HoloCard>

        {/* ==================== Keyword List ==================== */}
        <HoloCard>
          <HoloPanelHeader
            title={t('keywords.table_title')}
            subtitle={t('keywords.table_subtitle').replace('{count}', String(data?.total || 0))}
            icon={<Filter className="w-5 h-5" />}
          />
          <div className="p-4">
            {isLoading ? (
              <div className="space-y-2">
                {[...Array(5)].map((_, i) => (
                  <HoloSkeleton key={i} className="h-16" />
                ))}
              </div>
            ) : data?.data.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <Search className="w-12 h-12 mx-auto mb-4 text-gray-600" />
                <p className="text-lg">{t('keywords.empty_title')}</p>
                <p className="text-sm mt-1">{t('keywords.empty_hint')}</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-xs text-gray-500 uppercase tracking-wider border-b border-gray-800">
                      <th className="pb-3">{t('keywords.col_keyword')}</th>
                      <th className="pb-3">{t('keywords.col_type')}</th>
                      <th className="pb-3 text-center">{t('keywords.col_google_rank')}</th>
                      <th className="pb-3 text-center">{t('keywords.col_hktvmall_rank')}</th>
                      <th className="pb-3 text-center">{t('keywords.col_status')}</th>
                      <th className="pb-3 text-right">{t('keywords.col_actions')}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/50">
                    {data?.data.map((keyword) => (
                      <tr
                        key={keyword.id}
                        className="group hover:bg-cyan-500/5 transition-colors"
                      >
                        {/* Keyword */}
                        <td className="py-4">
                          <div>
                            <p className="text-white font-medium">{keyword.keyword}</p>
                            {keyword.tags && keyword.tags.length > 0 && (
                              <div className="flex gap-1 mt-1">
                                {keyword.tags.slice(0, 3).map((tag) => (
                                  <span
                                    key={tag}
                                    className="text-xs px-1.5 py-0.5 rounded bg-gray-800 text-gray-400"
                                  >
                                    {tag}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </td>

                        {/* Type */}
                        <td className="py-4">
                          <KeywordTypeBadge type={keyword.keyword_type} />
                        </td>

                        {/* Google Ranking */}
                        <td className="py-4 text-center">
                          <RankDisplay
                            rank={keyword.latest_google_rank}
                            change={keyword.google_rank_change}
                            target={keyword.target_google_rank}
                          />
                        </td>

                        {/* HKTVmall Ranking */}
                        <td className="py-4 text-center">
                          <RankDisplay
                            rank={keyword.latest_hktvmall_rank}
                            change={keyword.hktvmall_rank_change}
                            target={keyword.target_hktvmall_rank}
                          />
                        </td>

                        {/* State */}
                        <td className="py-4 text-center">
                          <button
                            onClick={() => handleToggleActive(keyword)}
                            disabled={updateKeyword.isPending}
                          >
                            <HoloBadge
                              variant={keyword.is_active ? "success" : "default"}
                            >
                              {keyword.is_active ? t('keywords.status_active') : t('keywords.status_inactive')}
                            </HoloBadge>
                          </button>
                        </td>

                        {/* Operation */}
                        <td className="py-4 text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleEdit(keyword)}
                              className="p-2 text-gray-400 hover:text-cyan-400 transition-colors"
                              title={t('keywords.edit')}
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(keyword.id)}
                              disabled={deleteKeyword.isPending}
                              className="p-2 text-gray-400 hover:text-red-400 transition-colors"
                              title={t('keywords.delete')}
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {/* Pagination */}
            {data && data.total > 20 && (
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-800">
                <p className="text-sm text-gray-500">
                  {t('keywords.pagination').replace('{from}', String((page - 1) * 20 + 1)).replace('{to}', String(Math.min(page * 20, data.total)))} / {data.total} {t('keywords.pagination_page')}
                </p>
                <div className="flex items-center gap-2">
                  <HoloButton
                    variant="ghost"
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    {t('keywords.prev_page')}
                  </HoloButton>
                  <span className="text-gray-400 px-2">
                    {page} / {Math.ceil(data.total / 20)}
                  </span>
                  <HoloButton
                    variant="ghost"
                    onClick={() => setPage((p) => p + 1)}
                    disabled={page * 20 >= data.total}
                  >
                    {t('keywords.next_page')}
                  </HoloButton>
                </div>
              </div>
            )}
          </div>
        </HoloCard>

        {/* Add/EditDialog */}
        <KeywordConfigDialog
          isOpen={isDialogOpen}
          onClose={handleDialogClose}
          keyword={editingKeyword}
        />
      </div>
    </PageTransition>
  );
}

// ==================== Helper Components ====================

function KeywordTypeBadge({ type }: { type: string }) {
  const { t } = useLocale();
  const config: Record<
    string,
    { label: string; variant: "default" | "info" | "success" | "warning" | "error" }
  > = {
    primary: { label: t('keywords.badge_primary'), variant: "info" },
    secondary: { label: t('keywords.badge_secondary'), variant: "default" },
    long_tail: { label: t('keywords.badge_long_tail'), variant: "success" },
    brand: { label: t('keywords.badge_brand'), variant: "warning" },
    competitor: { label: t('keywords.badge_competitor'), variant: "error" },
  };

  const { label, variant } = config[type] || { label: type, variant: "default" };

  return <HoloBadge variant={variant}>{label}</HoloBadge>;
}

function RankDisplay({
  rank,
  change,
  target,
}: {
  rank: number | null;
  change: number | null;
  target: number | null;
}) {
  const { t } = useLocale();
  if (rank === null) {
    return <span className="text-gray-600">-</span>;
  }

  return (
    <div className="inline-flex flex-col items-center">
      <span className={getRankColor(rank)}>#{rank}</span>
      {change !== null && change !== 0 && (
        <span
          className={`text-xs flex items-center gap-0.5 ${
            change > 0 ? "text-green-400" : "text-red-400"
          }`}
        >
          {change > 0 ? (
            <TrendingUp className="w-3 h-3" />
          ) : (
            <TrendingDown className="w-3 h-3" />
          )}
          {change > 0 ? `+${change}` : change}
        </span>
      )}
      {target && (
        <span className="text-xs text-gray-500">{t('keywords.badge_target')}: #{target}</span>
      )}
    </div>
  );
}

function getRankColor(rank: number): string {
  if (rank <= 3) return "text-green-400 font-bold";
  if (rank <= 10) return "text-cyan-400";
  if (rank <= 30) return "text-white";
  return "text-gray-400";
}
