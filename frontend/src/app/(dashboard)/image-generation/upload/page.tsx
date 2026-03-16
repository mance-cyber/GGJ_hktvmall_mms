// =============================================
// Image Generation Upload Page
// =============================================

'use client'

import { useState, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { useLocale } from '@/components/providers/locale-provider'
import { ImageUploadZone } from '@/components/image-generation/ImageUploadZone'
import { createTask, uploadImages, startGeneration, type GenerationMode } from '@/lib/api/image-generation'
import { usePermissions } from '@/hooks/usePermissions'
import { Loader2, Sparkles, Image as ImageIcon, History } from 'lucide-react'

export default function ImageGenerationUploadPage() {
  const router = useRouter()
  const { t } = useLocale()
  const { isAdmin } = usePermissions()
  const [files, setFiles] = useState<File[]>([])
  const [mode, setMode] = useState<GenerationMode>('white_bg_topview')
  const [styleDescription, setStyleDescription] = useState('')
  const [outputsPerImage, setOutputsPerImage] = useState(1)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Calculate limits based on role
  const maxFiles = isAdmin ? 999 : 5
  const maxOutputsPerImage = isAdmin ? 10 : 5
  const outputOptions = useMemo(
    () => Array.from({ length: maxOutputsPerImage }, (_, i) => i + 1),
    [maxOutputsPerImage]
  )

  const handleSubmit = async () => {
    if (files.length === 0) {
      setError(t('image_gen.error_no_images'))
      return
    }

    setIsUploading(true)
    setError(null)

    try {
      // 1. Create task
      const task = await createTask({
        mode,
        style_description: styleDescription || undefined,
        outputs_per_image: outputsPerImage,
      })

      // 2. Upload images
      await uploadImages(task.id, files)

      // 3. Start generation
      await startGeneration(task.id)

      // 4. Redirect to results page
      router.push(`/image-generation/results/${task.id}`)
    } catch (err: any) {
      console.error('Image generation error:', err)
      setError(err.response?.data?.detail || t('image_gen.error_generation_failed'))
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      {/* Title */}
      <div className="mb-8 flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{t('image_gen.upload_title')}</h1>
          <p className="text-gray-600">
            {t('image_gen.upload_subtitle')}
          </p>
        </div>
        <button
          onClick={() => router.push('/image-generation/history')}
          className="
            px-4 py-2 border border-gray-300 rounded-lg
            text-gray-700 font-medium text-sm
            hover:bg-gray-50
            flex items-center gap-2
          "
        >
          <History className="w-4 h-4" />
          {t('image_gen.view_history')}
        </button>
      </div>

      {/* Generate模式Select */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('image_gen.select_mode')}</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* White background mode */}
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
                <span className="font-medium text-gray-900">{t('image_gen.mode_white_bg_topview')}</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">
                {t('image_gen.mode_white_bg_desc')}
              </p>
              <p className="text-xs text-gray-500 mt-1">{t('image_gen.mode_white_bg_hint')}</p>
            </div>
          </label>

          {/* Professional photo mode */}
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
                <span className="font-medium text-gray-900">{t('image_gen.mode_professional_photo')}</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">
                {t('image_gen.mode_professional_desc')}
              </p>
              <p className="text-xs text-gray-500 mt-1">{t('image_gen.mode_professional_hint')}</p>
            </div>
          </label>
        </div>

        {/* Style description (shown only for professional photo mode) */}
        {mode === 'professional_photo' && (
          <div className="mt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('image_gen.style_description')}
            </label>
            <textarea
              value={styleDescription}
              onChange={(e) => setStyleDescription(e.target.value)}
              placeholder={t('image_gen.style_hint')}
              rows={3}
              className="
                w-full px-3 py-2 border border-gray-300 rounded-lg
                focus:outline-none focus:ring-2 focus:ring-blue-500
                text-sm
              "
            />
            <p className="text-xs text-gray-500 mt-1">
              {t('image_gen.style_help')}
            </p>
          </div>
        )}

        {/* Outputs per image */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            {t('image_gen.outputs_per_image')}
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
              {outputOptions.map((n) => (
                <option key={n} value={n}>{n} {t('image_gen.pieces')}</option>
              ))}
            </select>
            <span className="text-sm text-gray-600">
              {t('image_gen.estimated_output').replace('{count}', String(files.length * outputsPerImage))}
              {files.length > 0 && (
                <span className="text-gray-500">
                  {`（${t('image_gen.inputs_label').replace('{n}', String(files.length))} × ${t('image_gen.outputs_label').replace('{n}', String(outputsPerImage))}）`}
                </span>
              )}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            {t('image_gen.outputs_help')}
          </p>
        </div>
      </div>

      {/* Image upload area */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('image_gen.upload_section')}</h2>
        <ImageUploadZone onFilesChange={setFiles} maxFiles={maxFiles} />
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Submit button */}
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
          {t('image_gen.cancel')}
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
              {t('image_gen.uploading')}
            </>
          ) : (
            <>
              <Sparkles className="w-5 h-5" />
              {t('image_gen.start_generation')}
            </>
          )}
        </button>
      </div>
    </div>
  )
}
