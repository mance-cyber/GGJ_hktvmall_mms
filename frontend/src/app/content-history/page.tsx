'use client'

import { useState, useEffect, useCallback, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Clock,
  Search,
  Filter,
  Trash2,
  ChevronLeft,
  ChevronRight,
  Loader2,
  Zap,
  ArrowRight,
  RefreshCw,
  FileText,
  AlertCircle,
  X,
  Languages,
  SlidersHorizontal,
  CheckCheck,
} from 'lucide-react'
import {
  contentPipelineApi,
  PipelineHistoryItem,
  PipelineHistoryListResponse,
} from '@/lib/api'
import { cn } from '@/lib/utils'
import {
  PageTransition,
  HoloCard,
  HoloPanelHeader,
  HoloButton,
  HoloBadge,
  DataMetric,
  HoloSkeleton,
  StaggerContainer,
} from '@/components/ui/future-tech'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { useLocale } from '@/components/providers/locale-provider'

// =============================================
// Content Generation History Page
// =============================================

const LANGUAGE_FLAGS: Record<string, string> = {
  'zh-HK': '🇭🇰',
  'zh-CN': '🇨🇳',
  'en': '🇬🇧',
  'ja': '🇯🇵',
}

export default function ContentHistoryPage() {
  const router = useRouter()
  const { t } = useLocale()

  // Language name mapping (from i18n dictionary)
  const LANGUAGE_NAMES: Record<string, string> = useMemo(() => ({
    'zh-HK': t['content_history.lang_zh_HK'],
    'zh-CN': t['content_history.lang_zh_CN'],
    'en': 'English',
    'ja': '日本語',
  }), [t])

  // Data state
  const [history, setHistory] = useState<PipelineHistoryListResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filter state
  const [page, setPage] = useState(1)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterLanguage, setFilterLanguage] = useState<string>('')
  const [filterBatch, setFilterBatch] = useState<string>('')
  const [showFilters, setShowFilters] = useState(false)

  // Delete confirm state
  const [deleteId, setDeleteId] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  // Fetch history records
  const fetchHistory = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await contentPipelineApi.getHistory({
        page,
        page_size: 20,
        language: filterLanguage || undefined,
        is_batch: filterBatch === '' ? undefined : filterBatch === 'true',
        search: searchQuery || undefined,
      })
      setHistory(response)
    } catch (err) {
      setError(err instanceof Error ? err.message : t['content_history.fetch_failed'])
    } finally {
      setIsLoading(false)
    }
  }, [page, searchQuery, filterLanguage, filterBatch, t])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  // Reset page number on search
  useEffect(() => {
    setPage(1)
  }, [searchQuery, filterLanguage, filterBatch])

  // Delete history record
  const handleDelete = async (id: string) => {
    setIsDeleting(true)
    try {
      await contentPipelineApi.deleteHistory(id)
      setDeleteId(null)
      fetchHistory()
    } catch (err) {
      setError(err instanceof Error ? err.message : t['content_history.delete_failed'])
    } finally {
      setIsDeleting(false)
    }
  }

  // Re-Generate
  const handleRegenerate = (item: PipelineHistoryItem) => {
    sessionStorage.setItem('regenerate_product', item.product_name)
    sessionStorage.setItem('regenerate_languages', JSON.stringify(item.languages))
    sessionStorage.setItem('regenerate_tone', item.tone)
    router.push('/content-pipeline')
  }

  // Format time
  const formatTime = useCallback((dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return t['content_history.time_just_now']
    if (diffMins < 60) return t['content_history.time_minutes_ago'].replace('{n}', String(diffMins))
    if (diffHours < 24) return t['content_history.time_hours_ago'].replace('{n}', String(diffHours))
    if (diffDays < 7) return t['content_history.time_days_ago'].replace('{n}', String(diffDays))
    return date.toLocaleDateString('zh-HK', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }, [t])

  // SEO score color
  const getSeoScoreStyle = (score: number | null) => {
    if (!score) return { bg: 'bg-slate-200', text: 'text-slate-600' }
    if (score >= 80) return { bg: 'bg-emerald-100', text: 'text-emerald-700' }
    if (score >= 60) return { bg: 'bg-amber-100', text: 'text-amber-700' }
    return { bg: 'bg-red-100', text: 'text-red-700' }
  }

  // Statistics
  const stats = useMemo(() => {
    if (!history) return { total: 0, single: 0, batch: 0 }
    return {
      total: history.total,
      single: history.items.filter(i => !i.is_batch).length,
      batch: history.items.filter(i => i.is_batch).length,
    }
  }, [history])

  // ========== Loading Skeleton ==========
  if (isLoading && !history) {
    return (
      <PageTransition>
        <div className="space-y-6">
          {/* TitleSkeleton */}
          <div className="flex items-start justify-between">
            <div>
              <HoloSkeleton variant="text" width={200} height={36} />
              <HoloSkeleton variant="text" width={300} height={20} className="mt-2" />
            </div>
            <div className="flex gap-3">
              <HoloSkeleton variant="rectangular" width={140} height={40} />
            </div>
          </div>

          {/* Stats card skeleton */}
          <div className="grid grid-cols-3 gap-4">
            {[...Array(3)].map((_, i) => (
              <HoloSkeleton key={i} variant="rectangular" height={100} />
            ))}
          </div>

          {/* ToolbarSkeleton */}
          <div className="flex items-center gap-4">
            <HoloSkeleton variant="rectangular" className="flex-1" height={40} />
            <HoloSkeleton variant="rectangular" width={100} height={40} />
          </div>

          {/* ListSkeleton */}
          <HoloCard className="overflow-hidden">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="px-6 py-4 border-b border-slate-100">
                <HoloSkeleton variant="text" width="60%" height={24} />
                <HoloSkeleton variant="text" width="40%" height={16} className="mt-2" />
              </div>
            ))}
          </HoloCard>
        </div>
      </PageTransition>
    )
  }

  return (
    <PageTransition>
      <div className="space-y-6">
        {/* ========== Title section ========== */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
              <div className="p-2 bg-gradient-to-br from-purple-500 to-violet-600 rounded-xl shadow-lg shadow-purple-500/20">
                <Clock className="w-6 h-6 text-white" />
              </div>
              {t['content_history.title']}
            </h1>
            <p className="text-slate-500 mt-2">
              {t['content_history.subtitle']}
            </p>
          </div>

          <HoloButton
            variant="primary"
            icon={<Zap className="w-4 h-4" />}
            onClick={() => router.push('/content-pipeline')}
          >
            {t['content_history.go_generate']}
          </HoloButton>
        </div>

        {/* ========== Stats Cards ========== */}
        <StaggerContainer className="grid grid-cols-3 gap-4">
          <HoloCard className="p-4">
            <DataMetric
              label={t['content_history.metric_total']}
              value={stats.total}
              icon={<FileText className="w-5 h-5" />}
              color="purple"
            />
          </HoloCard>
          <HoloCard className="p-4">
            <DataMetric
              label={t['content_history.metric_single']}
              value={stats.single}
              icon={<Zap className="w-5 h-5" />}
              color="blue"
            />
          </HoloCard>
          <HoloCard className="p-4">
            <DataMetric
              label={t['content_history.metric_batch']}
              value={stats.batch}
              icon={<CheckCheck className="w-5 h-5" />}
              color="green"
            />
          </HoloCard>
        </StaggerContainer>

        {/* ========== Search and Filter ========== */}
        <div className="space-y-4">
          <div className="flex gap-4">
            {/* Search box */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <Input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={t['content_history.search_placeholder']}
                className="pl-10"
              />
            </div>

            {/* Filterbutton */}
            <Button
              variant="outline"
              onClick={() => setShowFilters(!showFilters)}
              className={cn(
                "gap-2",
                (showFilters || filterLanguage || filterBatch) && "border-purple-300 bg-purple-50 text-purple-700"
              )}
            >
              <SlidersHorizontal className="w-4 h-4" />
              {t['content_history.filter']}
              {(filterLanguage || filterBatch) && (
                <span className="w-2 h-2 bg-purple-500 rounded-full" />
              )}
            </Button>

            {/* Refreshbutton */}
            <Button
              variant="outline"
              size="icon"
              onClick={fetchHistory}
              disabled={isLoading}
            >
              <RefreshCw className={cn("w-4 h-4", isLoading && "animate-spin")} />
            </Button>
          </div>

          {/* FilterOption */}
          <AnimatePresence>
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <HoloCard className="p-4">
                  <div className="flex items-end gap-6">
                    {/* Language filter */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-slate-600">{t['content_history.filter_language']}</label>
                      <select
                        value={filterLanguage}
                        onChange={(e) => setFilterLanguage(e.target.value)}
                        className="h-10 px-3 rounded-lg border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-400"
                      >
                        <option value="">{t['content_history.filter_all_languages']}</option>
                        <option value="zh-HK">🇭🇰 {t['content_history.lang_zh_HK']}</option>
                        <option value="zh-CN">🇨🇳 {t['content_history.lang_zh_CN']}</option>
                        <option value="en">🇬🇧 English</option>
                        <option value="ja">🇯🇵 日本語</option>
                      </select>
                    </div>

                    {/* TypeFilter */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-slate-600">{t['content_history.filter_gen_type']}</label>
                      <select
                        value={filterBatch}
                        onChange={(e) => setFilterBatch(e.target.value)}
                        className="h-10 px-3 rounded-lg border border-slate-200 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/20 focus:border-purple-400"
                      >
                        <option value="">{t['content_history.filter_all_types']}</option>
                        <option value="false">{t['content_history.filter_single']}</option>
                        <option value="true">{t['content_history.filter_batch']}</option>
                      </select>
                    </div>

                    {/* Clear filter */}
                    {(filterLanguage || filterBatch) && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setFilterLanguage('')
                          setFilterBatch('')
                        }}
                        className="text-slate-500 hover:text-slate-700"
                      >
                        <X className="w-4 h-4 mr-1" />
                        {t['content_history.clear_filter']}
                      </Button>
                    )}
                  </div>
                </HoloCard>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* ========== Error hint ========== */}
        {error && (
          <HoloCard className="p-4 border-red-200 bg-red-50">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-red-500" />
              <span className="text-red-700 flex-1">{error}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setError(null)}
                className="text-red-500 hover:text-red-700"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </HoloCard>
        )}

        {/* ========== History Record List ========== */}
        <HoloCard className="overflow-hidden">
          <HoloPanelHeader
            title={`${t['content_history.table_title']}${history ? ` (${t['content_history.table_count'].replace('{total}', String(history.total))})` : ''}`}
            icon={<Clock className="w-4 h-4" />}
          />

          {history?.items.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-slate-400">
              <FileText className="w-12 h-12 mb-4 opacity-50" />
              <p className="text-lg font-medium">{t['content_history.empty_title']}</p>
              <p className="text-sm mt-1">{t['content_history.empty_desc']}</p>
              <HoloButton
                variant="primary"
                icon={<Zap className="w-4 h-4" />}
                className="mt-6"
                onClick={() => router.push('/content-pipeline')}
              >
                {t['content_history.start_generate']}
              </HoloButton>
            </div>
          ) : (
            <>
              {/* Table */}
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-100 bg-slate-50/80">
                      <th className="text-left py-3 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">{t['content_history.col_product']}</th>
                      <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{t['content_history.col_language']}</th>
                      <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{t['content_history.col_seo']}</th>
                      <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{t['content_history.col_duration']}</th>
                      <th className="text-left py-3 px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{t['content_history.col_time']}</th>
                      <th className="text-right py-3 px-6 text-xs font-semibold text-slate-500 uppercase tracking-wider">{t['content_history.col_actions']}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {history?.items.map((item, index) => {
                      const scoreStyle = getSeoScoreStyle(item.preview_seo_score)

                      return (
                        <motion.tr
                          key={item.id}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.03 }}
                          className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors"
                        >
                          {/* Product */}
                          <td className="py-4 px-6">
                            <div className="flex items-center gap-3">
                              <div className="flex-1 min-w-0">
                                <p className="font-medium text-slate-900 truncate max-w-[280px]">
                                  {item.preview_title || item.product_name}
                                </p>
                                <p className="text-sm text-slate-500 truncate max-w-[280px]">
                                  {item.product_name}
                                </p>
                              </div>
                              {item.is_batch && (
                                <HoloBadge variant="info" size="sm">
                                  {t['content_history.batch_label'].replace('{n}', String((item.batch_index ?? 0) + 1))}
                                </HoloBadge>
                              )}
                            </div>
                          </td>

                          {/* 語言 */}
                          <td className="py-4 px-4">
                            <div className="flex gap-1">
                              {item.languages.map((lang) => (
                                <span
                                  key={lang}
                                  className="text-lg cursor-default"
                                  title={LANGUAGE_NAMES[lang] || lang}
                                >
                                  {LANGUAGE_FLAGS[lang] || lang}
                                </span>
                              ))}
                            </div>
                          </td>

                          {/* SEO 分數 */}
                          <td className="py-4 px-4">
                            {item.preview_seo_score !== null ? (
                              <span className={cn(
                                "inline-flex items-center px-2.5 py-1 rounded-full text-sm font-medium",
                                scoreStyle.bg, scoreStyle.text
                              )}>
                                {item.preview_seo_score}
                              </span>
                            ) : (
                              <span className="text-slate-400">-</span>
                            )}
                          </td>

                          {/* 耗時 */}
                          <td className="py-4 px-4">
                            <span className="text-sm text-slate-600">
                              {(item.generation_time_ms / 1000).toFixed(1)}s
                            </span>
                          </td>

                          {/* Time */}
                          <td className="py-4 px-4">
                            <span className="text-sm text-slate-500">
                              {formatTime(item.created_at)}
                            </span>
                          </td>

                          {/* Operation */}
                          <td className="py-4 px-6">
                            <div className="flex items-center justify-end gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleRegenerate(item)}
                                className="gap-1.5 text-purple-600 border-purple-200 hover:bg-purple-50"
                              >
                                <RefreshCw className="w-3.5 h-3.5" />
                                {t['content_history.regenerate']}
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => setDeleteId(item.id)}
                                className="text-slate-400 hover:text-red-500 hover:bg-red-50"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </td>
                        </motion.tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              {history && history.total > 20 && (
                <div className="flex items-center justify-between px-6 py-4 border-t border-slate-100 bg-slate-50/50">
                  <p className="text-sm text-slate-500">
                    {t['content_history.pagination']
                      .replace('{total}', String(history.total))
                      .replace('{page}', String(history.page))
                      .replace('{pages}', String(Math.ceil(history.total / history.page_size)))}
                  </p>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(page - 1)}
                      disabled={page <= 1}
                      className="gap-1"
                    >
                      <ChevronLeft className="w-4 h-4" />
                      {t['content_history.prev_page']}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage(page + 1)}
                      disabled={!history.has_more}
                      className="gap-1"
                    >
                      {t['content_history.next_page']}
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </HoloCard>

        {/* ========== DeleteConfirmDialog ========== */}
        <AnimatePresence>
          {deleteId && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center z-50"
              onClick={() => setDeleteId(null)}
            >
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.95, opacity: 0 }}
                className="bg-white rounded-2xl shadow-2xl p-6 max-w-md mx-4 border border-slate-200"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <Trash2 className="w-5 h-5 text-red-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900">{t['content_history.dialog_delete_title']}</h3>
                </div>
                <p className="text-slate-600 mb-6">
                  {t['content_history.dialog_delete_message']}
                </p>
                <div className="flex gap-3 justify-end">
                  <Button
                    variant="outline"
                    onClick={() => setDeleteId(null)}
                  >
                    {t['common.cancel']}
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={() => handleDelete(deleteId)}
                    disabled={isDeleting}
                    className="gap-2"
                  >
                    {isDeleting && <Loader2 className="w-4 h-4 animate-spin" />}
                    {t['content_history.delete']}
                  </Button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </PageTransition>
  )
}
