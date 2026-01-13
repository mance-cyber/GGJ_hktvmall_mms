// =============================================
// 圖片生成結果頁面
// =============================================

'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { getTaskStatus, getPresignedUrl, type ImageGenerationTask, type InputImage } from '@/lib/api/image-generation'
import { ResultGallery } from '@/components/image-generation/ResultGallery'
import {
  Loader2,
  CheckCircle2,
  XCircle,
  ArrowLeft,
  Image as ImageIcon,
  ChevronDown,
  ChevronUp,
  Brain,
  Sparkles,
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
  const [inputImageUrls, setInputImageUrls] = useState<Record<string, string>>({})
  const [showAnalysis, setShowAnalysis] = useState<Record<string, boolean>>({})

  // 獲取輸入圖片的預簽名 URL
  const fetchInputImageUrls = useCallback(async (images: InputImage[]) => {
    const urls: Record<string, string> = {}
    for (const image of images) {
      if (!inputImageUrls[image.id] && image.file_path) {
        try {
          const response = await getPresignedUrl(image.file_path)
          urls[image.id] = response.presigned_url
        } catch (err) {
          console.error('Failed to get presigned URL for input image:', err)
          urls[image.id] = image.file_path
        }
      }
    }
    if (Object.keys(urls).length > 0) {
      setInputImageUrls(prev => ({ ...prev, ...urls }))
    }
  }, [inputImageUrls])

  // 獲取任務狀態
  const fetchTaskStatus = async () => {
    try {
      const data = await getTaskStatus(params.taskId)
      setTask(data)
      setError(null)

      // 如果任務還在處理中，繼續輪詢
      if (data.status === 'processing' || data.status === 'pending' || data.status === 'analyzing') {
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

  // 當任務數據加載後，獲取輸入圖片的預簽名 URL
  useEffect(() => {
    if (task?.input_images && task.input_images.length > 0) {
      fetchInputImageUrls(task.input_images)
    }
  }, [task?.input_images, fetchInputImageUrls])

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
    } else if (status === 'analyzing') {
      statusColor = 'bg-purple-500'
      statusText = 'AI 分析中'
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

          {status === 'analyzing' && (
            <div className="flex items-center gap-2 text-sm text-purple-600">
              <Brain className="w-4 h-4 animate-pulse" />
              AI 正在分析圖片...
            </div>
          )}
          {status === 'processing' && (
            <div className="flex items-center gap-2 text-sm text-blue-600">
              <Sparkles className="w-4 h-4 animate-spin" />
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

      {/* 輸入圖片和 AI 分析結果 */}
      {task.input_images.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            輸入圖片 ({task.input_images.length})
          </h2>
          <div className="space-y-6">
            {task.input_images.map((image) => (
              <div key={image.id} className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="flex flex-col md:flex-row">
                  {/* 圖片預覽 */}
                  <div className="relative w-full md:w-48 h-48 flex-shrink-0 bg-gray-100">
                    {inputImageUrls[image.id] ? (
                      <Image
                        src={inputImageUrls[image.id]}
                        alt={image.file_name}
                        fill
                        className="object-cover"
                        unoptimized
                      />
                    ) : (
                      <div className="absolute inset-0 flex items-center justify-center">
                        <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
                      </div>
                    )}
                  </div>

                  {/* 圖片信息和分析結果 */}
                  <div className="flex-1 p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-gray-900 truncate">{image.file_name}</h3>
                      {image.analysis_result && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full">
                          <Brain className="w-3 h-3" />
                          AI 已分析
                        </span>
                      )}
                    </div>

                    {/* AI 分析結果摘要 */}
                    {image.analysis_result && (
                      <div className="mt-3">
                        {/* 產品類型 */}
                        {image.analysis_result.product_type && (
                          <p className="text-sm text-gray-600 mb-2">
                            <span className="font-medium">產品類型：</span>
                            {image.analysis_result.product_type}
                          </p>
                        )}

                        {/* 視覺描述 */}
                        {image.analysis_result.visual_description && (
                          <p className="text-sm text-gray-600 mb-2">
                            <span className="font-medium">AI 描述：</span>
                            {image.analysis_result.visual_description}
                          </p>
                        )}

                        {/* 展開/收起 Prompt */}
                        {image.analysis_result.generated_prompt && (
                          <div className="mt-3">
                            <button
                              onClick={() => setShowAnalysis(prev => ({
                                ...prev,
                                [image.id]: !prev[image.id]
                              }))}
                              className="flex items-center gap-1 text-sm text-purple-600 hover:text-purple-800"
                            >
                              {showAnalysis[image.id] ? (
                                <>
                                  <ChevronUp className="w-4 h-4" />
                                  隱藏生成 Prompt
                                </>
                              ) : (
                                <>
                                  <ChevronDown className="w-4 h-4" />
                                  查看生成 Prompt
                                </>
                              )}
                            </button>

                            {showAnalysis[image.id] && (
                              <div className="mt-2 p-3 bg-gray-50 rounded-lg text-xs text-gray-700 font-mono overflow-auto max-h-40">
                                {image.analysis_result.generated_prompt}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}

                    {/* 分析中狀態 */}
                    {task.status === 'analyzing' && !image.analysis_result && (
                      <div className="mt-3 flex items-center gap-2 text-sm text-purple-600">
                        <Loader2 className="w-4 h-4 animate-spin" />
                        AI 正在分析這張圖片...
                      </div>
                    )}
                  </div>
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
      {task.status === 'analyzing' && (
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-6 text-center">
          <Brain className="w-12 h-12 text-purple-600 mx-auto mb-3 animate-pulse" />
          <p className="text-purple-800 font-medium">AI 正在分析您的圖片...</p>
          <p className="text-purple-600 text-sm mt-1">AI 會根據圖片內容生成最佳的生成策略</p>
        </div>
      )}
      {(task.status === 'processing' || task.status === 'pending') && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <Sparkles className="w-12 h-12 text-blue-600 mx-auto mb-3 animate-spin" />
          <p className="text-blue-800 font-medium">AI 正在根據分析結果生成圖片...</p>
          <p className="text-blue-600 text-sm mt-1">請稍候，頁面將自動更新</p>
        </div>
      )}
    </div>
  )
}
