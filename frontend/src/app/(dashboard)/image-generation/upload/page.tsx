// =============================================
// 圖片生成上傳頁面
// =============================================

'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ImageUploadZone } from '@/components/image-generation/ImageUploadZone'
import { createTask, uploadImages, startGeneration, type GenerationMode } from '@/lib/api/image-generation'
import { Loader2, Sparkles, Image as ImageIcon } from 'lucide-react'

export default function ImageGenerationUploadPage() {
  const router = useRouter()
  const [files, setFiles] = useState<File[]>([])
  const [mode, setMode] = useState<GenerationMode>('white_bg_topview')
  const [styleDescription, setStyleDescription] = useState('')
  const [outputsPerImage, setOutputsPerImage] = useState(1)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async () => {
    if (files.length === 0) {
      setError('請至少上傳一張圖片')
      return
    }

    setIsUploading(true)
    setError(null)

    try {
      // 1. 創建任務
      const task = await createTask({
        mode,
        style_description: styleDescription || undefined,
        outputs_per_image: outputsPerImage,
      })

      // 2. 上傳圖片
      await uploadImages(task.id, files)

      // 3. 開始生成
      await startGeneration(task.id)

      // 4. 跳轉到結果頁面
      router.push(`/image-generation/results/${task.id}`)
    } catch (err: any) {
      console.error('Image generation error:', err)
      setError(err.response?.data?.detail || '圖片生成失敗，請重試')
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      {/* 標題 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI 圖片生成</h1>
        <p className="text-gray-600">
          上傳產品圖片，AI 將自動生成專業的電商圖片或白底圖
        </p>
      </div>

      {/* 生成模式選擇 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">選擇生成模式</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* 白底圖模式 */}
          <label
            className={`
              relative flex items-start p-4 border-2 rounded-lg cursor-pointer
              transition-all
              ${
                mode === 'white_bg_topview'
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }
            `}
          >
            <input
              type="radio"
              name="mode"
              value="white_bg_topview"
              checked={mode === 'white_bg_topview'}
              onChange={(e) => setMode(e.target.value as GenerationMode)}
              className="mt-1"
            />
            <div className="ml-3">
              <div className="flex items-center gap-2">
                <ImageIcon className="w-5 h-5 text-gray-700" />
                <span className="font-medium text-gray-900">白底 TopView 正面圖</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">
                生成純白背景、俯視角度的專業產品圖
              </p>
              <p className="text-xs text-gray-500 mt-1">適合電商平台展示</p>
            </div>
          </label>

          {/* 專業攝影模式 */}
          <label
            className={`
              relative flex items-start p-4 border-2 rounded-lg cursor-pointer
              transition-all
              ${
                mode === 'professional_photo'
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }
            `}
          >
            <input
              type="radio"
              name="mode"
              value="professional_photo"
              checked={mode === 'professional_photo'}
              onChange={(e) => setMode(e.target.value as GenerationMode)}
              className="mt-1"
            />
            <div className="ml-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-gray-700" />
                <span className="font-medium text-gray-900">專業美食攝影圖</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">
                生成多角度、專業打光的高質感產品圖
              </p>
              <p className="text-xs text-gray-500 mt-1">適合社交媒體、廣告宣傳</p>
            </div>
          </label>
        </div>

        {/* 風格描述（專業攝影模式才顯示） */}
        {mode === 'professional_photo' && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              風格描述（可選）
            </label>
            <textarea
              value={styleDescription}
              onChange={(e) => setStyleDescription(e.target.value)}
              placeholder="例如：溫暖陽光灑落、木質餐桌背景、清新自然風格..."
              rows={3}
              className="
                w-full px-3 py-2 border border-gray-300 rounded-lg
                focus:outline-none focus:ring-2 focus:ring-blue-500
                text-sm
              "
            />
            <p className="text-xs text-gray-500 mt-1">
              描述您期望的拍攝風格、背景、光線等，AI 將根據描述生成
            </p>
          </div>
        )}

        {/* 每張圖片輸出數量 */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            每張圖片生成數量
          </label>
          <div className="flex items-center gap-4">
            <select
              value={outputsPerImage}
              onChange={(e) => setOutputsPerImage(Number(e.target.value))}
              className="
                px-4 py-2 border border-gray-300 rounded-lg
                focus:outline-none focus:ring-2 focus:ring-blue-500
                text-sm bg-white
              "
            >
              <option value={1}>1 張</option>
              <option value={2}>2 張</option>
              <option value={3}>3 張</option>
              <option value={4}>4 張</option>
              <option value={5}>5 張</option>
            </select>
            <span className="text-sm text-gray-600">
              預計生成 <span className="font-semibold text-blue-600">{files.length * outputsPerImage}</span> 張圖片
              {files.length > 0 && (
                <span className="text-gray-500">
                  （{files.length} 張輸入 × {outputsPerImage} 張輸出）
                </span>
              )}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            每張上傳的產品圖片都會生成指定數量的結果圖片
          </p>
        </div>
      </div>

      {/* 圖片上傳區域 */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">上傳產品圖片</h2>
        <ImageUploadZone onFilesChange={setFiles} maxFiles={5} />
      </div>

      {/* 錯誤訊息 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* 提交按鈕 */}
      <div className="flex justify-end gap-4">
        <button
          type="button"
          onClick={() => router.back()}
          className="
            px-6 py-2 border border-gray-300 rounded-lg
            text-gray-700 font-medium
            hover:bg-gray-50
            transition-colors
          "
          disabled={isUploading}
        >
          取消
        </button>

        <button
          type="button"
          onClick={handleSubmit}
          disabled={files.length === 0 || isUploading}
          className="
            px-6 py-2 bg-blue-600 text-white rounded-lg
            font-medium
            hover:bg-blue-700
            disabled:bg-gray-300 disabled:cursor-not-allowed
            transition-colors
            flex items-center gap-2
          "
        >
          {isUploading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              上傳中...
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              開始生成
            </>
          )}
        </button>
      </div>
    </div>
  )
}
