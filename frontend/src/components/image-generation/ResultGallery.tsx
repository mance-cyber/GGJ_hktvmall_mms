// =============================================
// 圖片生成結果展示組件
// =============================================

'use client'

import { useState, useEffect, useCallback } from 'react'
import Image from 'next/image'
import { Download, ZoomIn, Loader2 } from 'lucide-react'
import type { OutputImage } from '@/lib/api/image-generation'
import { getPresignedUrl } from '@/lib/api/image-generation'

interface ResultGalleryProps {
  images: OutputImage[]
}

export function ResultGallery({ images }: ResultGalleryProps) {
  const [selectedImage, setSelectedImage] = useState<OutputImage | null>(null)
  const [presignedUrls, setPresignedUrls] = useState<Record<string, string>>({})
  const [loadingUrls, setLoadingUrls] = useState<Set<string>>(new Set())

  // 獲取單個圖片的預簽名 URL
  const fetchPresignedUrl = useCallback(async (image: OutputImage) => {
    if (presignedUrls[image.id] || loadingUrls.has(image.id)) {
      return
    }

    setLoadingUrls(prev => new Set(prev).add(image.id))

    try {
      const response = await getPresignedUrl(image.file_path)
      setPresignedUrls(prev => ({
        ...prev,
        [image.id]: response.presigned_url
      }))
    } catch (error) {
      console.error('Failed to get presigned URL:', error)
      // 降級使用原始 URL
      setPresignedUrls(prev => ({
        ...prev,
        [image.id]: image.file_path
      }))
    } finally {
      setLoadingUrls(prev => {
        const next = new Set(prev)
        next.delete(image.id)
        return next
      })
    }
  }, [presignedUrls, loadingUrls])

  // 當圖片列表變化時，預加載所有預簽名 URL
  useEffect(() => {
    images.forEach(image => {
      if (!presignedUrls[image.id] && !loadingUrls.has(image.id)) {
        fetchPresignedUrl(image)
      }
    })
  }, [images, presignedUrls, loadingUrls, fetchPresignedUrl])

  const handleDownload = async (image: OutputImage) => {
    try {
      // 使用預簽名 URL 下載
      const url = presignedUrls[image.id] || image.file_path
      const response = await fetch(url)
      const blob = await response.blob()
      const blobUrl = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = blobUrl
      a.download = image.file_name
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(blobUrl)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  // 獲取圖片顯示 URL
  const getImageUrl = (image: OutputImage): string => {
    return presignedUrls[image.id] || image.file_path
  }

  // 檢查圖片 URL 是否正在加載
  const isLoading = (imageId: string): boolean => {
    return loadingUrls.has(imageId) && !presignedUrls[imageId]
  }

  if (images.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>尚無生成圖片</p>
      </div>
    )
  }

  return (
    <>
      {/* 圖片網格 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {images.map((image) => (
          <div
            key={image.id}
            className="relative aspect-square rounded-lg overflow-hidden bg-gray-100 group"
          >
            {isLoading(image.id) ? (
              <div className="absolute inset-0 flex items-center justify-center">
                <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
              </div>
            ) : (
              <Image
                src={getImageUrl(image)}
                alt={image.file_name}
                fill
                className="object-cover"
                unoptimized
              />
            )}

            {/* 操作按鈕 */}
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all">
              <div className="absolute bottom-4 left-4 right-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => setSelectedImage(image)}
                  className="
                    flex-1 bg-white text-gray-900 px-4 py-2 rounded-lg
                    font-medium text-sm
                    hover:bg-gray-100
                    transition-colors
                    flex items-center justify-center gap-2
                  "
                >
                  <ZoomIn className="w-4 h-4" />
                  查看
                </button>

                <button
                  onClick={() => handleDownload(image)}
                  className="
                    flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg
                    font-medium text-sm
                    hover:bg-blue-700
                    transition-colors
                    flex items-center justify-center gap-2
                  "
                >
                  <Download className="w-4 h-4" />
                  下載
                </button>
              </div>
            </div>

            {/* 文件信息 */}
            <div className="absolute top-2 left-2 right-2">
              <div className="bg-black bg-opacity-50 text-white px-3 py-1 rounded text-xs">
                {image.file_name}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 燈箱預覽 */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="relative max-w-5xl max-h-[90vh] w-full h-full">
            <Image
              src={getImageUrl(selectedImage)}
              alt={selectedImage.file_name}
              fill
              className="object-contain"
              onClick={(e) => e.stopPropagation()}
              unoptimized
            />

            {/* 關閉按鈕 */}
            <button
              onClick={() => setSelectedImage(null)}
              className="
                absolute top-4 right-4
                bg-white text-gray-900 px-4 py-2 rounded-lg
                font-medium
                hover:bg-gray-100
              "
            >
              關閉
            </button>

            {/* 下載按鈕 */}
            <button
              onClick={() => handleDownload(selectedImage)}
              className="
                absolute bottom-4 right-4
                bg-blue-600 text-white px-4 py-2 rounded-lg
                font-medium
                hover:bg-blue-700
                flex items-center gap-2
              "
            >
              <Download className="w-5 h-5" />
              下載圖片
            </button>
          </div>
        </div>
      )}
    </>
  )
}
