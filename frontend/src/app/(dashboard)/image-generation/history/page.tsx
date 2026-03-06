// =============================================
// 圖片生成歷史記錄頁面
// =============================================

'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useLocale } from '@/components/providers/locale-provider'
import {
  listTasks,
  deleteTask,
  deleteTasksBatch,
  type ImageGenerationTask,
  type TaskListResponse
} from '@/lib/api/image-generation'
import {
  Loader2,
  Trash2,
  Eye,
  CheckCircle2,
  XCircle,
  Clock,
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Plus,
  Image as ImageIcon
} from 'lucide-react'

// 狀態標籤組件
function StatusBadge({ status }: { status: string }) {
  const { t } = useLocale()

  const config: Record<string, { color: string; icon: React.ReactNode; key: keyof typeof t }> = {
    pending: {
      color: 'bg-gray-100 text-gray-700',
      icon: <Clock className="w-3 h-3" />,
      key: 'image_gen.status_pending'
    },
    analyzing: {
      color: 'bg-purple-100 text-purple-700',
      icon: <Loader2 className="w-3 h-3 animate-spin" />,
      key: 'image_gen.status_analyzing'
    },
    processing: {
      color: 'bg-blue-100 text-blue-700',
      icon: <Loader2 className="w-3 h-3 animate-spin" />,
      key: 'image_gen.status_processing'
    },
    completed: {
      color: 'bg-green-100 text-green-700',
      icon: <CheckCircle2 className="w-3 h-3" />,
      key: 'image_gen.status_completed'
    },
    failed: {
      color: 'bg-red-100 text-red-700',
      icon: <XCircle className="w-3 h-3" />,
      key: 'image_gen.status_failed'
    }
  }

  const { color, icon, key } = config[status] || config.pending

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${color}`}>
      {icon}
      {t[key]}
    </span>
  )
}

// 格式化日期
function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleString('zh-HK', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 計算剩餘天數
function getDaysRemaining(dateString: string): number {
  const createdDate = new Date(dateString)
  const expiryDate = new Date(createdDate.getTime() + 7 * 24 * 60 * 60 * 1000)
  const now = new Date()
  const diff = expiryDate.getTime() - now.getTime()
  return Math.max(0, Math.ceil(diff / (24 * 60 * 60 * 1000)))
}

export default function ImageGenerationHistoryPage() {
  const router = useRouter()
  const { t } = useLocale()
  const [tasks, setTasks] = useState<ImageGenerationTask[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(10)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 選中的任務（用於批量刪除）
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [isDeleting, setIsDeleting] = useState(false)

  // 加載任務列表
  const loadTasks = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response: TaskListResponse = await listTasks(page, pageSize)
      setTasks(response.tasks)
      setTotal(response.total)
    } catch (err: any) {
      console.error('Failed to load tasks:', err)
      setError(err.response?.data?.detail || t['image_gen.error_load_failed'])
    } finally {
      setIsLoading(false)
    }
  }, [page, pageSize, t])

  useEffect(() => {
    loadTasks()
  }, [loadTasks])

  // 計算總頁數
  const totalPages = Math.ceil(total / pageSize)

  // 全選/取消全選
  const handleSelectAll = () => {
    if (selectedIds.size === tasks.length) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(tasks.map(t => t.id)))
    }
  }

  // 選中/取消選中單個任務
  const handleSelectTask = (taskId: string) => {
    const newSelected = new Set(selectedIds)
    if (newSelected.has(taskId)) {
      newSelected.delete(taskId)
    } else {
      newSelected.add(taskId)
    }
    setSelectedIds(newSelected)
  }

  // 刪除單個任務
  const handleDeleteTask = async (taskId: string) => {
    if (!confirm(t['image_gen.confirm_delete'])) {
      return
    }

    setIsDeleting(true)
    try {
      await deleteTask(taskId)
      setSelectedIds(prev => {
        const next = new Set(prev)
        next.delete(taskId)
        return next
      })
      await loadTasks()
    } catch (err: any) {
      console.error('Failed to delete task:', err)
      alert(err.response?.data?.detail || t['image_gen.error_delete_failed'])
    } finally {
      setIsDeleting(false)
    }
  }

  // 批量刪除任務
  const handleBatchDelete = async () => {
    if (selectedIds.size === 0) return

    const msg = t['image_gen.confirm_batch_delete'].replace('{count}', String(selectedIds.size))
    if (!confirm(msg)) {
      return
    }

    setIsDeleting(true)
    try {
      await deleteTasksBatch(Array.from(selectedIds))
      setSelectedIds(new Set())
      await loadTasks()
    } catch (err: any) {
      console.error('Failed to batch delete tasks:', err)
      alert(err.response?.data?.detail || t['image_gen.error_batch_delete_failed'])
    } finally {
      setIsDeleting(false)
    }
  }

  // 查看任務詳情
  const handleViewTask = (taskId: string) => {
    router.push(`/image-generation/results/${taskId}`)
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* 標題 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t['image_gen.history_title']}</h1>
          <p className="text-gray-600 mt-1">
            {t['image_gen.history_subtitle']}
          </p>
        </div>
        <button
          onClick={() => router.push('/image-generation/upload')}
          className="
            px-4 py-2 bg-blue-600 text-white rounded-lg
            font-medium hover:bg-blue-700
            flex items-center gap-2
          "
        >
          <Plus className="w-5 h-5" />
          {t['image_gen.new_generation']}
        </button>
      </div>

      {/* 批量操作欄 */}
      {tasks.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={selectedIds.size === tasks.length && tasks.length > 0}
                onChange={handleSelectAll}
                className="w-4 h-4 text-blue-600 rounded"
              />
              <span className="text-sm text-gray-600">
                {selectedIds.size > 0
                  ? `${t['image_gen.selected']} ${selectedIds.size} ${t['image_gen.items']}`
                  : t['image_gen.select_all']}
              </span>
            </label>
          </div>

          {selectedIds.size > 0 && (
            <button
              onClick={handleBatchDelete}
              disabled={isDeleting}
              className="
                px-4 py-2 bg-red-600 text-white rounded-lg
                font-medium text-sm
                hover:bg-red-700 disabled:bg-gray-300
                flex items-center gap-2
              "
            >
              {isDeleting ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Trash2 className="w-4 h-4" />
              )}
              {t['image_gen.delete_selected']}
            </button>
          )}
        </div>
      )}

      {/* 任務列表 */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      ) : error ? (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <XCircle className="w-12 h-12 text-red-600 mx-auto mb-3" />
          <p className="text-red-800">{error}</p>
          <button
            onClick={loadTasks}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            {t['image_gen.retry']}
          </button>
        </div>
      ) : tasks.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <ImageIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">{t['image_gen.empty_title']}</h3>
          <p className="text-gray-600 mb-6">{t['image_gen.empty_desc']}</p>
          <button
            onClick={() => router.push('/image-generation/upload')}
            className="
              px-6 py-2 bg-blue-600 text-white rounded-lg
              font-medium hover:bg-blue-700
            "
          >
            {t['image_gen.start']}
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left w-10">
                  <span className="sr-only">{t['image_gen.select']}</span>
                </th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">{t['image_gen.col_mode']}</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">{t['image_gen.col_status']}</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">{t['image_gen.col_image_count']}</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">{t['image_gen.col_created_time']}</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">{t['image_gen.col_remaining_time']}</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-600">{t['image_gen.col_actions']}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {tasks.map((task) => {
                const daysRemaining = getDaysRemaining(task.created_at)
                return (
                  <tr key={task.id} className="hover:bg-gray-50">
                    <td className="px-4 py-4">
                      <input
                        type="checkbox"
                        checked={selectedIds.has(task.id)}
                        onChange={() => handleSelectTask(task.id)}
                        className="w-4 h-4 text-blue-600 rounded"
                      />
                    </td>
                    <td className="px-4 py-4">
                      <span className="text-sm text-gray-900">
                        {task.mode === 'white_bg_topview' ? t['image_gen.mode_white_bg'] : t['image_gen.mode_professional']}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <StatusBadge status={task.status} />
                    </td>
                    <td className="px-4 py-4">
                      <span className="text-sm text-gray-600">
                        {task.input_images.length} {t['image_gen.input']} / {task.output_images.length} {t['image_gen.output']}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <span className="text-sm text-gray-600">
                        {formatDate(task.created_at)}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      {daysRemaining > 0 ? (
                        <span className={`text-sm ${daysRemaining <= 2 ? 'text-orange-600' : 'text-gray-600'}`}>
                          {daysRemaining} {t['image_gen.days']}
                        </span>
                      ) : (
                        <span className="text-sm text-red-600 flex items-center gap-1">
                          <AlertCircle className="w-3 h-3" />
                          {t['image_gen.expiring']}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() => handleViewTask(task.id)}
                          className="
                            p-2 text-gray-600 hover:text-blue-600
                            hover:bg-blue-50 rounded-lg
                          "
                          title={t['image_gen.view_details']}
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDeleteTask(task.id)}
                          disabled={isDeleting}
                          className="
                            p-2 text-gray-600 hover:text-red-600
                            hover:bg-red-50 rounded-lg
                            disabled:opacity-50
                          "
                          title={t['image_gen.delete']}
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>

          {/* 分頁 */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between px-4 py-3 border-t border-gray-200">
              <div className="text-sm text-gray-600">
                {t['image_gen.pagination']
                  .replace('{total}', String(total))
                  .replace('{page}', String(page))
                  .replace('{pages}', String(totalPages))}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="
                    p-2 rounded-lg border border-gray-300
                    hover:bg-gray-50 disabled:opacity-50
                    disabled:cursor-not-allowed
                  "
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="
                    p-2 rounded-lg border border-gray-300
                    hover:bg-gray-50 disabled:opacity-50
                    disabled:cursor-not-allowed
                  "
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
