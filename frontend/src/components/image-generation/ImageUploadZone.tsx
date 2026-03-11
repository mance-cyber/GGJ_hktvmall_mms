// =============================================
// ImageUploadArea組items（含AutoCompressFeature）
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

// CompressImage的Target大小（8MB，留一些餘量給Backend）
const TARGET_SIZE = 8 * 1024 * 1024

// Compress images using Canvas
async function compressImage(file: File, maxSizeBytes: number): Promise<File> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      // CalculateNeed的Compress比例
      let quality = 0.9
      let scale = 1

      // If image is large, reduce dimensions first
      const maxDimension = 4096 // 最大邊長
      if (img.width > maxDimension || img.height > maxDimension) {
        scale = maxDimension / Math.max(img.width, img.height)
      }

      const canvas = document.createElement('canvas')
      canvas.width = img.width * scale
      canvas.height = img.height * scale

      const ctx = canvas.getContext('2d')
      if (!ctx) {
        reject(new Error('無法Create Canvas context'))
        return
      }

      ctx.drawImage(img, 0, 0, canvas.width, canvas.height)

      // Gradually reduce quality until target size is reached
      const tryCompress = (q: number) => {
        canvas.toBlob(
          (blob) => {
            if (!blob) {
              reject(new Error('CompressFailed'))
              return
            }

            console.log(`[Compress] quality=${q.toFixed(2)}, size=${(blob.size / 1024 / 1024).toFixed(2)}MB`)

            if (blob.size <= maxSizeBytes || q <= 0.1) {
              // 達到Target或已到最低質量
              const compressedFile = new File([blob], file.name, {
                type: 'image/jpeg',
                lastModified: Date.now(),
              })
              resolve(compressedFile)
            } else {
              // Continue降低質量
              tryCompress(q - 0.1)
            }
          },
          'image/jpeg',
          q
        )
      }

      tryCompress(quality)
    }

    img.onerror = () => reject(new Error('無法LoadImage'))
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
        // NeedCompress
        setCompressStatus(`currentlyCompress ${file.name}...`)
        console.log(`[ImageUploadZone] Compressing ${file.name} (${(file.size / 1024 / 1024).toFixed(2)}MB)`)

        try {
          const compressed = await compressImage(file, TARGET_SIZE)
          console.log(`[ImageUploadZone] Compressed to ${(compressed.size / 1024 / 1024).toFixed(2)}MB`)
          processedFiles.push(compressed)
        } catch (err) {
          console.error(`[ImageUploadZone] Compression failed for ${file.name}:`, err)
          // CompressFailed，Skip這個文items
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
      setCompressStatus('Processing...')

      try {
        // Processing文items（包括Compress大文items）
        const processedFiles = await processFiles(acceptedFiles)

        if (processedFiles.length === 0) {
          console.warn('[ImageUploadZone] No files after processing')
          return
        }

        // Limit總Quantity
        const newFiles = [...files, ...processedFiles].slice(0, maxFiles)
        console.log('[ImageUploadZone] Setting files:', newFiles.length)
        setFiles(newFiles)
        onFilesChange(newFiles)

        // Generate預覽（最多保留 10 個預覽 URL，Avoid大量Image時記憶體浪費）
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

  // Processing被Reject的文items
  const onDropRejected = useCallback((rejectedFiles: any[]) => {
    console.error('[ImageUploadZone] Files rejected:', rejectedFiles)
    rejectedFiles.forEach((rejection) => {
      console.error(`  - ${rejection.file.name}:`, rejection.errors)
      console.error(`    File type: ${rejection.file.type}`)
      console.error(`    File size: ${rejection.file.size}`)
    })
  }, [])

  // Custom file validator (check extension only, not size, auto-compression)
  const fileValidator = useCallback((file: File) => {
    const allowedExtensions = ['.jpg', '.jpeg', '.png', '.webp']
    const ext = file.name.toLowerCase().slice(file.name.lastIndexOf('.'))

    if (!allowedExtensions.includes(ext)) {
      return {
        code: 'file-invalid-type',
        message: `不Support的檔案Format: ${ext}`
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
    // 使用CustomValidate器，不依賴 MIME type（相機檔案 MIME type 常不準確）
    // 不設 maxSize，因為會AutoCompress大Image
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
      {/* 拖放Area */}
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
              <p className="text-sm text-gray-500">大ImagecurrentlyAutoCompress中...</p>
            </>
          ) : isDragActive ? (
            <>
              <Upload className="w-12 h-12 text-blue-500" />
              <p className="text-lg font-medium text-blue-600">放開以UploadImage</p>
            </>
          ) : files.length >= maxFiles ? (
            <>
              <ImageIcon className="w-12 h-12 text-gray-400" />
              <p className="text-lg font-medium text-gray-500">
                Maximum upload count reached ({maxFiles} 張)
              </p>
            </>
          ) : (
            <>
              <Upload className="w-12 h-12 text-gray-400" />
              <div>
                <p className="text-lg font-medium text-gray-700">
                  拖放Image至此，或點擊Select
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Support JPG、PNG、WEBP Format{maxFiles < 100 ? `，最多 ${maxFiles} 張` : ''}
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  大Image會AutoCompress
                </p>
              </div>
            </>
          )}

          <p className="text-xs text-gray-400">
            已Upload {files.length}{maxFiles < 100 ? ` / ${maxFiles}` : ''} 張
          </p>
        </div>
      </div>

      {/* 預覽Area */}
      {files.length > 0 && (
        <>
          {/* 超過 10 張時Display計數摘要，只Rendering前 10 張預覽Avoid DOM 爆炸 */}
          {files.length > 10 && (
            <div className="flex items-center justify-between bg-blue-50 border border-blue-200 rounded-lg px-4 py-3">
              <div className="flex items-center gap-2">
                <ImageIcon className="w-5 h-5 text-blue-600" />
                <span className="text-sm font-medium text-blue-800">
                  Selected擇 {files.length} 張Image
                </span>
                <span className="text-xs text-blue-600">
                  （僅Display前 10 張預覽）
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
                ClearAll
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

                {/* Deletebutton */}
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
                  aria-label="DeleteImage"
                >
                  <X className="w-4 h-4" />
                </button>

                {/* 文items信息 */}
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
