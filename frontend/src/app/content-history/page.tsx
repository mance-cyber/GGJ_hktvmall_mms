'use client'

import { useState, useEffect, useCallback } from 'react'
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
  Languages,
  Zap,
  ArrowRight,
  RefreshCw,
  FileText,
  AlertCircle,
  X,
} from 'lucide-react'
import {
  contentPipelineApi,
  PipelineHistoryItem,
  PipelineHistoryListResponse,
} from '@/lib/api'

// =============================================
// 內容生成歷史記錄頁面
// =============================================

const LANGUAGE_FLAGS: Record<string, string> = {
  'zh-HK': '🇭🇰',
  'zh-CN': '🇨🇳',
  'en': '🇬🇧',
  'ja': '🇯🇵',
}

const LANGUAGE_NAMES: Record<string, string> = {
  'zh-HK': '繁體中文',
  'zh-CN': '簡體中文',
  'en': 'English',
  'ja': '日本語',
}

export default function ContentHistoryPage() {
  const router = useRouter()

  // 數據狀態
  const [history, setHistory] = useState<PipelineHistoryListResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 篩選狀態
  const [page, setPage] = useState(1)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterLanguage, setFilterLanguage] = useState<string>('')
  const [filterBatch, setFilterBatch] = useState<string>('')
  const [showFilters, setShowFilters] = useState(false)

  // 刪除確認狀態
  const [deleteId, setDeleteId] = useState<string | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  // 獲取歷史記錄
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
      setError(err instanceof Error ? err.message : '獲取歷史記錄失敗')
    } finally {
      setIsLoading(false)
    }
  }, [page, searchQuery, filterLanguage, filterBatch])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  // 搜索時重置頁碼
  useEffect(() => {
    setPage(1)
  }, [searchQuery, filterLanguage, filterBatch])

  // 刪除歷史記錄
  const handleDelete = async (id: string) => {
    setIsDeleting(true)
    try {
      await contentPipelineApi.deleteHistory(id)
      setDeleteId(null)
      fetchHistory()
    } catch (err) {
      setError(err instanceof Error ? err.message : '刪除失敗')
    } finally {
      setIsDeleting(false)
    }
  }

  // 重新生成（跳轉到生成頁面並帶上參數）
  const handleRegenerate = (item: PipelineHistoryItem) => {
    // 將產品信息存儲到 sessionStorage，然後跳轉
    sessionStorage.setItem('regenerate_product', item.product_name)
    sessionStorage.setItem('regenerate_languages', JSON.stringify(item.languages))
    sessionStorage.setItem('regenerate_tone', item.tone)
    router.push('/content-pipeline')
  }

  // 格式化時間
  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return '剛剛'
    if (diffMins < 60) return `${diffMins} 分鐘前`
    if (diffHours < 24) return `${diffHours} 小時前`
    if (diffDays < 7) return `${diffDays} 天前`
    return date.toLocaleDateString('zh-HK', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  // SEO 分數顏色
  const getSeoScoreColor = (score: number | null) => {
    if (!score) return 'bg-zinc-600'
    if (score >= 80) return 'bg-green-500'
    if (score >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="min-h-screen bg-zinc-950 text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* 標題 */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-500/20 rounded-lg">
              <Clock className="w-6 h-6 text-purple-400" />
            </div>
            <h1 className="text-3xl font-bold">生成歷史</h1>
          </div>
          <p className="text-zinc-400">
            查看和管理內容流水線的生成記錄
          </p>
        </div>

        {/* 搜索和篩選 */}
        <div className="mb-6 space-y-4">
          <div className="flex gap-4">
            {/* 搜索框 */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="搜索產品名稱..."
                className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-10 pr-4 py-3 text-white placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
              />
            </div>

            {/* 篩選按鈕 */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center gap-2 px-4 py-3 rounded-lg border transition-colors ${
                showFilters || filterLanguage || filterBatch
                  ? 'bg-purple-500/20 border-purple-500/50 text-purple-300'
                  : 'bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-white hover:border-zinc-700'
              }`}
            >
              <Filter className="w-5 h-5" />
              篩選
            </button>

            {/* 刷新按鈕 */}
            <button
              onClick={fetchHistory}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-3 bg-zinc-900 border border-zinc-800 rounded-lg text-zinc-400 hover:text-white hover:border-zinc-700 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>

          {/* 篩選選項 */}
          <AnimatePresence>
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="flex gap-4 p-4 bg-zinc-900/50 rounded-lg border border-zinc-800">
                  {/* 語言篩選 */}
                  <div>
                    <label className="block text-sm text-zinc-400 mb-2">語言</label>
                    <select
                      value={filterLanguage}
                      onChange={(e) => setFilterLanguage(e.target.value)}
                      className="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                    >
                      <option value="">全部</option>
                      <option value="zh-HK">🇭🇰 繁體中文</option>
                      <option value="zh-CN">🇨🇳 簡體中文</option>
                      <option value="en">🇬🇧 English</option>
                      <option value="ja">🇯🇵 日本語</option>
                    </select>
                  </div>

                  {/* 批量篩選 */}
                  <div>
                    <label className="block text-sm text-zinc-400 mb-2">生成類型</label>
                    <select
                      value={filterBatch}
                      onChange={(e) => setFilterBatch(e.target.value)}
                      className="bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                    >
                      <option value="">全部</option>
                      <option value="false">單個生成</option>
                      <option value="true">批量生成</option>
                    </select>
                  </div>

                  {/* 清除篩選 */}
                  {(filterLanguage || filterBatch) && (
                    <button
                      onClick={() => {
                        setFilterLanguage('')
                        setFilterBatch('')
                      }}
                      className="self-end px-3 py-2 text-sm text-zinc-400 hover:text-white"
                    >
                      清除篩選
                    </button>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* 錯誤提示 */}
        {error && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <span className="text-red-300">{error}</span>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-400 hover:text-red-300"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}

        {/* 歷史記錄列表 */}
        <div className="bg-zinc-900/50 rounded-xl border border-zinc-800 overflow-hidden">
          {isLoading && !history ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 animate-spin text-purple-400" />
            </div>
          ) : history?.items.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-zinc-500">
              <FileText className="w-12 h-12 mb-4 opacity-50" />
              <p>暫無生成記錄</p>
              <button
                onClick={() => router.push('/content-pipeline')}
                className="mt-4 flex items-center gap-2 px-4 py-2 bg-purple-500 hover:bg-purple-600 rounded-lg text-white transition-colors"
              >
                <Zap className="w-4 h-4" />
                開始生成
              </button>
            </div>
          ) : (
            <>
              {/* 表格 */}
              <table className="w-full">
                <thead>
                  <tr className="border-b border-zinc-800 bg-zinc-900">
                    <th className="text-left py-4 px-6 text-sm font-medium text-zinc-400">產品</th>
                    <th className="text-left py-4 px-4 text-sm font-medium text-zinc-400">語言</th>
                    <th className="text-left py-4 px-4 text-sm font-medium text-zinc-400">SEO</th>
                    <th className="text-left py-4 px-4 text-sm font-medium text-zinc-400">耗時</th>
                    <th className="text-left py-4 px-4 text-sm font-medium text-zinc-400">時間</th>
                    <th className="text-right py-4 px-6 text-sm font-medium text-zinc-400">操作</th>
                  </tr>
                </thead>
                <tbody>
                  {history?.items.map((item) => (
                    <motion.tr
                      key={item.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="border-b border-zinc-800/50 hover:bg-zinc-800/30 transition-colors"
                    >
                      {/* 產品 */}
                      <td className="py-4 px-6">
                        <div className="flex items-center gap-3">
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-white truncate max-w-[300px]">
                              {item.preview_title || item.product_name}
                            </p>
                            <p className="text-sm text-zinc-500 truncate max-w-[300px]">
                              {item.product_name}
                            </p>
                          </div>
                          {item.is_batch && (
                            <span className="px-2 py-0.5 text-xs bg-blue-500/20 text-blue-300 rounded">
                              批量 #{(item.batch_index ?? 0) + 1}
                            </span>
                          )}
                        </div>
                      </td>

                      {/* 語言 */}
                      <td className="py-4 px-4">
                        <div className="flex gap-1">
                          {item.languages.map((lang) => (
                            <span
                              key={lang}
                              className="text-lg"
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
                          <div className="flex items-center gap-2">
                            <div
                              className={`w-2 h-2 rounded-full ${getSeoScoreColor(item.preview_seo_score)}`}
                            />
                            <span className="text-sm">{item.preview_seo_score}</span>
                          </div>
                        ) : (
                          <span className="text-zinc-500">-</span>
                        )}
                      </td>

                      {/* 耗時 */}
                      <td className="py-4 px-4">
                        <span className="text-sm text-zinc-400">
                          {(item.generation_time_ms / 1000).toFixed(1)}s
                        </span>
                      </td>

                      {/* 時間 */}
                      <td className="py-4 px-4">
                        <span className="text-sm text-zinc-400">
                          {formatTime(item.created_at)}
                        </span>
                      </td>

                      {/* 操作 */}
                      <td className="py-4 px-6">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleRegenerate(item)}
                            className="flex items-center gap-1 px-3 py-1.5 text-sm bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 rounded-lg transition-colors"
                            title="使用相同設定重新生成"
                          >
                            <RefreshCw className="w-4 h-4" />
                            重新生成
                          </button>
                          <button
                            onClick={() => setDeleteId(item.id)}
                            className="p-1.5 text-zinc-500 hover:text-red-400 transition-colors"
                            title="刪除"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>

              {/* 分頁 */}
              {history && history.total > 20 && (
                <div className="flex items-center justify-between px-6 py-4 border-t border-zinc-800">
                  <p className="text-sm text-zinc-400">
                    共 {history.total} 條記錄，第 {history.page} / {Math.ceil(history.total / history.page_size)} 頁
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setPage(page - 1)}
                      disabled={page <= 1}
                      className="flex items-center gap-1 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
                    >
                      <ChevronLeft className="w-4 h-4" />
                      上一頁
                    </button>
                    <button
                      onClick={() => setPage(page + 1)}
                      disabled={!history.has_more}
                      className="flex items-center gap-1 px-3 py-1.5 bg-zinc-800 hover:bg-zinc-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
                    >
                      下一頁
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* 跳轉到生成頁面 */}
        <div className="mt-6 flex justify-center">
          <button
            onClick={() => router.push('/content-pipeline')}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 rounded-lg text-white font-medium transition-all"
          >
            <Zap className="w-5 h-5" />
            前往內容生成
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>

        {/* 刪除確認對話框 */}
        <AnimatePresence>
          {deleteId && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
              onClick={() => setDeleteId(null)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="bg-zinc-900 rounded-xl border border-zinc-800 p-6 max-w-md mx-4"
                onClick={(e) => e.stopPropagation()}
              >
                <h3 className="text-lg font-semibold mb-2">確認刪除</h3>
                <p className="text-zinc-400 mb-6">
                  確定要刪除這條歷史記錄嗎？此操作無法撤銷。
                </p>
                <div className="flex gap-3 justify-end">
                  <button
                    onClick={() => setDeleteId(null)}
                    className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg transition-colors"
                  >
                    取消
                  </button>
                  <button
                    onClick={() => handleDelete(deleteId)}
                    disabled={isDeleting}
                    className="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 disabled:opacity-50 rounded-lg transition-colors"
                  >
                    {isDeleting && <Loader2 className="w-4 h-4 animate-spin" />}
                    刪除
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
