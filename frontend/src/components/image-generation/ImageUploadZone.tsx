// =============================================
// 圖片上傳區域組件（含自動壓縮功能）
// =============================================

'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { X, Upload, Image as ImageIcon, Loader2 } from 'lucide-react'

interface ImageUploadZoneProps {
  onFilesChange: (files: File[]) => void
  maxFiles?: number
  maxSize?: number
}

// 壓縮圖片的目標大小（8MB，留一些餘量給後端）
const TARGET_SIZE = 8 * 1024 * 1024

// 使用 Canvas 壓縮圖片
async function compressImage(file: File, maxSizeBytes: number): Promise<File> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      // 計算需要的壓縮比例
      let quality = 0.9
      let scale = 1

      // 如果圖片很大，先縮小尺寸
      const maxDimension = 4096 // 最大邊長
      if (img.width > maxDimension || img.height > maxDimension) {
        scale = maxDimension / Math.max(img.width, img.height)
      }

      const canvas = document.createElement('canvas')
      canvas.width = img.width * scale
      canvas.height = img.height * scale

      const ctx = canvas.getContext('2d')
      if (!ctx) {
        reject(new Error('無法創建 Canvas context'))
        return
      }

      ctx.drawImage(img, 0, 0, canvas.width, canvas.height)

      // 逐步降低質量直到達到目標大小
      const tryCompress = (q: number) => {
        canvas.toBlob(
          (blob) => {
            if (!blob) {
              reject(new Error('壓縮失敗'))
              return
            }

            console.log(`[Compress] quality=${q.toFixed(2)}, size=${(blob.size / 1024 / 1024).toFixed(2)}MB`)

            if (blob.size <= maxSizeBytes || q <= 0.1) {
              // 達到目標或已到最低質量
              const compressedFile = new File([blob], file.name, {
                type: 'image/jpeg',
                lastModified: Date.now(),
              })
              resolve(compressedFile)
            } else {
              // 繼續降低質量
              tryCompress(q - 0.1)
            }
          },
          'image/jpeg',
          q
        )
      }

      tryCompress(quality)
    }

    img.onerror = () => reject(new Error('無法載入圖片'))
    img.src = URL.createObjectURL(file)
  })
}

export function ImageUploadZone({
  onFilesChange,
  maxFiles = 5,
  maxSize = 10 * 1024 * 1024, // 10MB
}: ImageUploadZoneProps) {
  const [files, setFiles] = useState<File[]>([])
  const [previews, setPreviews] = useState<string[]>([])
  const [isCompressing, setIsCompressing] = useState(false)
  const [compressStatus, setCompressStatus] = useState<string>('')

  const processFiles = useCallback(async (inputFiles: File[]) => {
    const processedFiles: File[] = []

    for (const file of inputFiles) {
      if (file.size > maxSize) {
        // 需要壓縮
        setCompressStatus(`正在壓縮 ${file.name}...`)
        console.log(`[ImageUploadZone] Compressing ${file.name} (${(file.size / 1024 / 1024).toFixed(2)}MB)`)

        try {
          const compressed = await compressImage(file, TARGET_SIZE)
          console.log(`[ImageUploadZone] Compressed to ${(compressed.size / 1024 / 1024).toFixed(2)}MB`)
          processedFiles.push(compressed)
        } catch (err) {
          console.error(`[ImageUploadZone] Compression failed for ${file.name}:`, err)
          // 壓縮失敗，跳過這個文件
        }
      } else {
        processedFiles.push(file)
      }
    }

    return processedFiles
  }, [maxSize])

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      console.log('[ImageUploadZone] onDrop called, files:', acceptedFiles.map(f => ({
        name: f.name,
        size: `${(f.size / 1024 / 1024).toFixed(2)}MB`,
        type: f.type
      })))

      if (acceptedFiles.length === 0) {
        console.warn('[ImageUploadZone] No files accepted')
        return
      }

      setIsCompressing(true)
      setCompressStatus('處理中...')

      try {
        // 處理文件（包括壓縮大文件）
        const processedFiles = await processFiles(acceptedFiles)

        if (processedFiles.length === 0) {
          console.warn('[ImageUploadZone] No files after processing')
          return
        }

        // 限制總數量
        const newFiles = [...files, ...processedFiles].slice(0, maxFiles)
        console.log('[ImageUploadZone] Setting files:', newFiles.length)
        setFiles(newFiles)
        onFilesChange(newFiles)

        // 生成預覽（最多保留 10 個預覽 URL，避免大量圖片時記憶體浪費）
        const PREVIEW_LIMIT = 10
        setPreviews((prev) => {
          const currentCount = prev.length
          if (currentCount >= PREVIEW_LIMIT) return prev
          const slotsLeft = PREVIEW_LIMIT - currentCount
          const newPreviews = processedFiles.slice(0, slotsLeft).map((file) => URL.createObjectURL(file))
          return [...prev, ...newPreviews]
        })
      } finally {
        setIsCompressing(false)
        setCompressStatus('')
      }
    },
    [files, maxFiles, onFilesChange, processFiles]
  )

  // 處理被拒絕的文件
  const onDropRejected = useCallback((rejectedFiles: any[]) => {
    console.error('[ImageUploadZone] Files rejected:', rejectedFiles)
    rejectedFiles.forEach((rejection) => {
      console.error(`  - ${rejection.file.name}:`, rejection.errors)
      console.error(`    File type: ${rejection.file.type}`)
      console.error(`    File size: ${rejection.file.size}`)
    })
  }, [])

  // 自定義文件驗證器（只檢查副檔名，不檢查大小，因為會自動壓縮）
  const fileValidator = useCallback((file: File) => {
    const allowedExtensions = ['.jpg', '.jpeg', '.png', '.webp']
    const ext = file.name.toLowerCase().slice(file.name.lastIndexOf('.'))

    if (!allowedExtensions.includes(ext)) {
      return {
        code: 'file-invalid-type',
        message: `不支持的檔案格式: ${ext}`
      }
    }
    return null
  }, [])

  const removeFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index)
    const newPreviews = previews.filter((_, i) => i !== index)

    setFiles(newFiles)
    setPreviews(newPreviews)
    onFilesChange(newFiles)

    // 釋放 URL
    URL.revokeObjectURL(previews[index])
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    onDropRejected,
    // 使用自定義驗證器，不依賴 MIME type（相機檔案 MIME type 常不準確）
    // 不設 maxSize，因為會自動壓縮大圖片
    validator: fileValidator,
    maxFiles: maxFiles - files.length,
    disabled: files.length >= maxFiles || isCompressing,
    noClick: false,
    noKeyboard: false,
    noDrag: false,
  })

  console.log('[ImageUploadZone] Render - files:', files.length, 'isCompressing:', isCompressing)

  return (
    <div className="space-y-4">
      {/* 拖放區域 */}
      <div
        {...getRootProps()}
        className={`
          relative border-2 border-dashed rounded-lg p-8
          transition-colors cursor-pointer
          ${
            isDragActive
              ? 'border-blue-500 bg-blue-50'
              : files.length >= maxFiles
              ? 'border-gray-300 bg-gray-50 cursor-not-allowed'
              : 'border-gray-300 hover:border-gray-400 bg-white'
          }
        `}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center justify-center text-center space-y-3">
          {isCompressing ? (
            <>
              <Loader2 className="w-12 h-12 text-blue-500 animate-spin" />
              <p className="text-lg font-medium text-blue-600">{compressStatus}</p>
              <p className="text-sm text-gray-500">大圖片正在自動壓縮中...</p>
            </>
          ) : isDragActive ? (
            <>
              <Upload className="w-12 h-12 text-blue-500" />
              <p className="text-lg font-medium text-blue-600">放開以上傳圖片</p>
            </>
          ) : files.length >= maxFiles ? (
            <>
              <ImageIcon className="w-12 h-12 text-gray-400" />
              <p className="text-lg font-medium text-gray-500">
                已達最大上傳數量 ({maxFiles} 張)
              </p>
            </>
          ) : (
            <>
              <Upload className="w-12 h-12 text-gray-400" />
              <div>
                <p className="text-lg font-medium text-gray-700">
                  拖放圖片至此，或點擊選擇
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  支持 JPG、PNG、WEBP 格式{maxFiles < 100 ? `，最多 ${maxFiles} 張` : ''}
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  大圖片會自動壓縮
                </p>
              </div>
            </>
          )}

          <p className="text-xs text-gray-400">
            已上傳 {files.length}{maxFiles < 100 ? ` / ${maxFiles}` : ''} 張
          </p>
        </div>
      </div>

      {/* 預覽區域 */}
      {files.length > 0 && (
        <>
          {/* 超過 10 張時顯示計數摘要，只渲染前 10 張預覽避免 DOM 爆炸 */}
          {files.length > 10 && (
            <div className="flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg px-4 py-3">
              <div className="flex items-center gap-2">
                <ImageIcon className="w-5 h-5 text-blue-600" />
                <span className="text-sm font-medium text-blue-800">
                  已選擇 {files.length} 張圖片
                </span>
                <span className="text-xs text-blue-600">
                  （僅顯示前 10 張預覽）
                </span>
              </div>
              <button
                type="button"
                onClick={() => {
                  previews.forEach((p) => URL.revokeObjectURL(p))
                  setFiles([])
                  setPreviews([])
                  onFilesChange([])
                }}
                className="text-sm text-red-600 hover:text-red-800 font-medium"
              >
                清除全部
              </button>
            </div>
          )}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {previews.slice(0, 10).map((preview, index) => (
              <div
                key={index}
                className="relative aspect-square rounded-lg overflow-hidden bg-gray-100 group"
              >
                {/* 使用原生 img 標籤，因為 blob URL 不支援 next/image */}
                <img
                  src={preview}
                  alt={`預覽 ${index + 1}`}
                  className="absolute inset-0 w-full h-full object-cover"
                />

                {/* 刪除按鈕 */}
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className="
                    absolute top-2 right-2
                    bg-red-500 text-white rounded-full p-1
                    opacity-0 group-hover:opacity-100
                    transition-opacity
                    hover:bg-red-600
                  "
                  aria-label="刪除圖片"
                >
                  <X className="w-4 h-4" />
                </button>

                {/* 文件信息 */}
                <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white p-2 text-xs">
                  <p className="truncate">{files[index].name}</p>
                  <p className="text-gray-300">
                    {(files[index].size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
