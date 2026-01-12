// =============================================
// 圖片生成結果展示組件
// =============================================

'use client'

import { useState } from 'react'
import Image from 'next/image'
import { Download, ZoomIn } from 'lucide-react'
import type { OutputImage } from '@/lib/api/image-generation'

interface ResultGalleryProps {
  images: OutputImage[]
}

export function ResultGallery({ images }: ResultGalleryProps) {
  const [selectedImage, setSelectedImage] = useState<OutputImage | null>(null)

  const handleDownload = async (image: OutputImage) => {
    try {
      const response = await fetch(image.file_path)
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = image.file_name
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download failed:', error)
    }
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
            <Image
              src={image.file_path}
              alt={image.file_name}
              fill
              className="object-cover"
            />

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
              src={selectedImage.file_path}
              alt={selectedImage.file_name}
              fill
              className="object-contain"
              onClick={(e) => e.stopPropagation()}
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
