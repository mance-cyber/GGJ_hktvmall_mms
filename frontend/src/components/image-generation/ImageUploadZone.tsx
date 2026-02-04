// =============================================
// 圖片上傳區域組件
// =============================================

'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { X, Upload, Image as ImageIcon } from 'lucide-react'

interface ImageUploadZoneProps {
  onFilesChange: (files: File[]) => void
  maxFiles?: number
  maxSize?: number
}

export function ImageUploadZone({
  onFilesChange,
  maxFiles = 5,
  maxSize = 10 * 1024 * 1024, // 10MB
}: ImageUploadZoneProps) {
  const [files, setFiles] = useState<File[]>([])
  const [previews, setPreviews] = useState<string[]>([])

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      console.log('[ImageUploadZone] onDrop called, acceptedFiles:', acceptedFiles)

      if (acceptedFiles.length === 0) {
        console.warn('[ImageUploadZone] No files accepted')
        return
      }

      // 限制總數量
      const newFiles = [...files, ...acceptedFiles].slice(0, maxFiles)
      console.log('[ImageUploadZone] Setting files:', newFiles)
      setFiles(newFiles)
      onFilesChange(newFiles)

      // 生成預覽
      const newPreviews = acceptedFiles.map((file) => URL.createObjectURL(file))
      setPreviews((prev) => [...prev, ...newPreviews].slice(0, maxFiles))
    },
    [files, maxFiles, onFilesChange]
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

  // 自定義文件驗證器（基於副檔名，不依賴 MIME type）
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
    validator: fileValidator,
    maxSize,
    maxFiles: maxFiles - files.length,
    disabled: files.length >= maxFiles,
    noClick: false,
    noKeyboard: false,
    noDrag: false,
  })

  console.log('[ImageUploadZone] Render - files:', files.length, 'disabled:', files.length >= maxFiles)

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
          {isDragActive ? (
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
                  支持 JPG、PNG、WEBP 格式，最多 {maxFiles} 張，單張最大 10MB
                </p>
              </div>
            </>
          )}

          <p className="text-xs text-gray-400">
            已上傳 {files.length} / {maxFiles} 張
          </p>
        </div>
      </div>

      {/* 預覽區域 */}
      {files.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {previews.map((preview, index) => (
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
      )}
    </div>
  )
}
