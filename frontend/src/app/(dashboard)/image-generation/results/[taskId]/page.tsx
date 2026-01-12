// =============================================
// 圖片生成結果頁面
// =============================================

'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { getTaskStatus, type ImageGenerationTask } from '@/lib/api/image-generation'
import { ResultGallery } from '@/components/image-generation/ResultGallery'
import {
  Loader2,
  CheckCircle2,
  XCircle,
  ArrowLeft,
  Image as ImageIcon,
} from 'lucide-react'

export default function ImageGenerationResultPage({
  params,
}: {
  params: { taskId: string }
}) {
  const router = useRouter()
  const [task, setTask] = useState<ImageGenerationTask | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // 獲取任務狀態
  const fetchTaskStatus = async () => {
    try {
      const data = await getTaskStatus(params.taskId)
      setTask(data)
      setError(null)

      // 如果任務還在處理中，繼續輪詢
      if (data.status === 'processing' || data.status === 'pending') {
        setTimeout(fetchTaskStatus, 2000) // 每 2 秒輪詢一次
      }
    } catch (err: any) {
      console.error('Failed to fetch task status:', err)
      setError(err.response?.data?.detail || '無法獲取任務狀態')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchTaskStatus()
  }, [params.taskId])

  // 渲染進度條
  const renderProgressBar = () => {
    if (!task) return null

    const { status, progress } = task

    let statusColor = 'bg-blue-500'
    let statusText = '處理中'

    if (status === 'completed') {
      statusColor = 'bg-green-500'
      statusText = '已完成'
    } else if (status === 'failed') {
      statusColor = 'bg-red-500'
      statusText = '失敗'
    } else if (status === 'pending') {
      statusColor = 'bg-gray-400'
      statusText = '等待中'
    }

    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-900">生成進度</h2>
          <span className={`text-sm font-medium ${status === 'completed' ? 'text-green-600' : status === 'failed' ? 'text-red-600' : 'text-blue-600'}`}>
            {statusText}
          </span>
        </div>

        {/* 進度條 */}
        <div className="relative w-full h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full ${statusColor} transition-all duration-500`}
            style={{ width: `${progress}%` }}
          />
        </div>

        <div className="flex justify-between items-center mt-2">
          <p className="text-sm text-gray-600">{progress}%</p>

          {status === 'processing' && (
            <div className="flex items-center gap-2 text-sm text-blue-600">
              <Loader2 className="w-4 h-4 animate-spin" />
              正在生成圖片...
            </div>
          )}
        </div>
      </div>
    )
  }

  // 渲染狀態指示器
  const renderStatusIndicator = () => {
    if (!task) return null

    const { status, error_message } = task

    if (status === 'completed') {
      return (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6 flex items-start gap-3">
          <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-green-900">生成完成！</h3>
            <p className="text-sm text-green-700 mt-1">
              成功生成 {task.output_images.length} 張圖片
            </p>
          </div>
        </div>
      )
    }

    if (status === 'failed') {
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-start gap-3">
          <XCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-medium text-red-900">生成失敗</h3>
            <p className="text-sm text-red-700 mt-1">
              {error_message || '發生未知錯誤，請重試'}
            </p>
          </div>
        </div>
      )
    }

    return null
  }

  if (isLoading && !task) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <XCircle className="w-12 h-12 text-red-600 mx-auto mb-3" />
          <p className="text-red-800">{error}</p>
          <button
            onClick={() => router.push('/image-generation/upload')}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            返回上傳頁面
          </button>
        </div>
      </div>
    )
  }

  if (!task) return null

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      {/* 標題 */}
      <div className="mb-6 flex items-center gap-4">
        <button
          onClick={() => router.push('/image-generation/upload')}
          className="text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-6 h-6" />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">生成結果</h1>
          <p className="text-gray-600 mt-1">
            模式：{task.mode === 'white_bg_topview' ? '白底 TopView 正面圖' : '專業美食攝影圖'}
          </p>
        </div>
      </div>

      {/* 進度條 */}
      {renderProgressBar()}

      {/* 狀態指示器 */}
      {renderStatusIndicator()}

      {/* 輸入圖片 */}
      {task.input_images.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            輸入圖片 ({task.input_images.length})
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {task.input_images.map((image) => (
              <div
                key={image.id}
                className="relative aspect-square rounded-lg overflow-hidden bg-gray-100"
              >
                <ImageIcon className="absolute inset-0 m-auto w-8 h-8 text-gray-400" />
                <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white p-2 text-xs">
                  <p className="truncate">{image.file_name}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 輸出圖片 */}
      {task.status === 'completed' && task.output_images.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            生成結果 ({task.output_images.length})
          </h2>
          <ResultGallery images={task.output_images} />
        </div>
      )}

      {/* 處理中提示 */}
      {(task.status === 'processing' || task.status === 'pending') && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <Loader2 className="w-12 h-12 text-blue-600 mx-auto mb-3 animate-spin" />
          <p className="text-blue-800 font-medium">AI 正在努力生成圖片...</p>
          <p className="text-blue-600 text-sm mt-1">請稍候，頁面將自動更新</p>
        </div>
      )}
    </div>
  )
}
