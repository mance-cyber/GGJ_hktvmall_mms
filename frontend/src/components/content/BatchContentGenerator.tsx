'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import {
  api,
  OwnProduct,
  ProductInfo,
  ContentBatchGenerateRequest,
  BatchResultItem,
  BatchGenerateResponse,
  BatchProgress,
} from '@/lib/api'
import {
  Package,
  FileSpreadsheet,
  Sparkles,
  Settings2,
  AlertCircle,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { cn } from '@/lib/utils'
import {
  HoloCard,
  HoloPanelHeader,
  HoloButton,
  HoloBadge,
} from '@/components/ui/future-tech'
import { ProductSelector } from './ProductSelector'
import { FileImporter } from './FileImporter'
import { BatchResultList } from './BatchResultList'

// ConfigurationOption
const CONTENT_TYPES = [
  { value: 'title', label: 'productsTitle' },
  { value: 'selling_points', label: '賣點List' },
  { value: 'description', label: 'productsDescription' },
  { value: 'full_copy', label: '完整文案' },
] as const

const STYLES = [
  { value: 'professional', label: '專業正式' },
  { value: 'casual', label: '輕鬆隨意' },
  { value: 'playful', label: '活潑有趣' },
  { value: 'formal', label: '正式官方' },
] as const

const LANGUAGES = [
  { value: 'TC', label: '繁體中文', flag: '🇭🇰' },
  { value: 'SC', label: '簡體中文', flag: '🇨🇳' },
  { value: 'EN', label: 'English', flag: '🇬🇧' },
] as const

type InputMode = 'products' | 'file'
type LanguageCode = 'TC' | 'SC' | 'EN'

interface BatchContentGeneratorProps {
  onNavigateToEdit?: (contentId: string) => void
  className?: string
}

export function BatchContentGenerator({
  onNavigateToEdit,
  className,
}: BatchContentGeneratorProps) {
  // Input模式
  const [inputMode, setInputMode] = useState<InputMode>('products')

  // 選中的products（productsSelect模式）
  const [selectedProducts, setSelectedProducts] = useState<OwnProduct[]>([])

  // Import的productsInformation（文itemsImport模式）
  const [importedProducts, setImportedProducts] = useState<ProductInfo[]>([])

  // GenerateConfiguration
  const [contentType, setContentType] = useState<ContentBatchGenerateRequest['content_type']>('full_copy')
  const [style, setStyle] = useState<ContentBatchGenerateRequest['style']>('professional')
  const [selectedLanguages, setSelectedLanguages] = useState<LanguageCode[]>(['TC'])

  // GenerateResult
  const [results, setResults] = useState<BatchResultItem[]>([])
  const [asyncTaskId, setAsyncTaskId] = useState<string | null>(null)
  const [asyncProgress, setAsyncProgress] = useState<BatchProgress | null>(null)

  // 輪詢定時器
  const pollingRef = useRef<NodeJS.Timeout | null>(null)

  // Clean up輪詢
  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }, [])

  // 批量Generate mutation
  const generateMutation = useMutation({
    mutationFn: (data: ContentBatchGenerateRequest) => api.batchGenerateContent(data),
    onSuccess: (response: BatchGenerateResponse) => {
      if (response.mode === 'sync') {
        // Sync模式：直接DisplayResult
        setResults(response.results)
        setAsyncTaskId(null)
        setAsyncProgress(null)
      } else {
        // Async模式：Start輪詢
        setAsyncTaskId(response.task_id)
        setAsyncProgress({
          total: response.total,
          completed: 0,
          failed: 0,
          percent: 0,
        })
        startPolling(response.task_id)
      }
    },
  })

  // Start輪詢任務State
  const startPolling = useCallback((taskId: string) => {
    stopPolling()

    const poll = async () => {
      try {
        const status = await api.getBatchTaskStatus(taskId)
        setAsyncProgress(status.progress)
        setResults(status.results)

        // 任務Complete，Stopped輪詢
        if (status.status === 'completed' || status.status === 'failed') {
          stopPolling()
          setAsyncTaskId(null)
        }
      } catch (error) {
        console.error('輪詢任務StateFailed:', error)
        stopPolling()
        setAsyncTaskId(null)
      }
    }

    // 立即執行一次
    poll()

    // Poll every 2 seconds
    pollingRef.current = setInterval(poll, 2000)
  }, [stopPolling])

  // 組items卸載時Clean up
  useEffect(() => {
    return () => {
      stopPolling()
    }
  }, [stopPolling])

  // Calculate當前選中的productsQuantity
  const itemCount = inputMode === 'products' ? selectedProducts.length : importedProducts.length

  // 構建Request並Submit
  const handleGenerate = () => {
    const items =
      inputMode === 'products'
        ? selectedProducts.map((p) => ({ product_id: p.id }))
        : importedProducts.map((p) => ({ product_info: p }))

    if (items.length === 0) return

    // ResetResult
    setResults([])
    setAsyncTaskId(null)
    setAsyncProgress(null)

    generateMutation.mutate({
      items,
      content_type: contentType,
      style,
      target_languages: selectedLanguages,
    })
  }

  // 切換Input模式時Reset
  const handleModeChange = (mode: InputMode) => {
    if (mode !== inputMode) {
      setInputMode(mode)
      setSelectedProducts([])
      setImportedProducts([])
      setResults([])
      stopPolling()
    }
  }

  const isProcessing = generateMutation.isPending || !!asyncTaskId

  return (
    <div className={cn('space-y-6', className)}>
      {/* Input模式切換 */}
      <div className="flex rounded-xl bg-white/50 p-1 border border-white/40">
        <button
          onClick={() => handleModeChange('products')}
          className={cn(
            'flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all',
            inputMode === 'products'
              ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-md'
              : 'text-gray-600 hover:bg-white/50'
          )}
        >
          <Package className="w-4 h-4" />
          從Product listSelect
        </button>
        <button
          onClick={() => handleModeChange('file')}
          className={cn(
            'flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all',
            inputMode === 'file'
              ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-md'
              : 'text-gray-600 hover:bg-white/50'
          )}
        >
          <FileSpreadsheet className="w-4 h-4" />
          CSV 文itemsImport
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左側：Input區 */}
        <div className="lg:col-span-2">
          <HoloCard glowColor="cyan" className="h-full">
            <div className="p-6">
              <HoloPanelHeader
                title={inputMode === 'products' ? 'Selectproducts' : 'Import文items'}
                icon={
                  inputMode === 'products' ? (
                    <Package className="w-5 h-5" />
                  ) : (
                    <FileSpreadsheet className="w-5 h-5" />
                  )
                }
              />

              <div className="mt-4">
                {inputMode === 'products' ? (
                  <ProductSelector
                    selectedProducts={selectedProducts}
                    onSelectionChange={setSelectedProducts}
                    maxSelection={100}
                  />
                ) : (
                  <FileImporter onProductsChange={setImportedProducts} />
                )}
              </div>
            </div>
          </HoloCard>
        </div>

        {/* 右側：Configuration區 */}
        <div>
          <HoloCard glowColor="purple" className="h-full">
            <div className="p-6 space-y-6">
              <HoloPanelHeader
                title="GenerateSettings"
                icon={<Settings2 className="w-5 h-5" />}
              />

              {/* ContentType */}
              <div className="space-y-2">
                <Label>ContentType</Label>
                <Select
                  value={contentType}
                  onValueChange={(val) =>
                    setContentType(val as ContentBatchGenerateRequest['content_type'])
                  }
                >
                  <SelectTrigger className="bg-white/50">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {CONTENT_TYPES.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* 文案風格 */}
              <div className="space-y-2">
                <Label>文案風格</Label>
                <Select
                  value={style}
                  onValueChange={(val) =>
                    setStyle(val as ContentBatchGenerateRequest['style'])
                  }
                >
                  <SelectTrigger className="bg-white/50">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {STYLES.map((s) => (
                      <SelectItem key={s.value} value={s.value}>
                        {s.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* 語言Select */}
              <div className="space-y-2">
                <Label>Output語言（可多選）</Label>
                <div className="flex flex-wrap gap-2">
                  {LANGUAGES.map((lang) => {
                    const isSelected = selectedLanguages.includes(lang.value)
                    return (
                      <button
                        key={lang.value}
                        type="button"
                        onClick={() => {
                          if (isSelected && selectedLanguages.length > 1) {
                            setSelectedLanguages(
                              selectedLanguages.filter((l) => l !== lang.value)
                            )
                          } else if (!isSelected) {
                            setSelectedLanguages([...selectedLanguages, lang.value])
                          }
                        }}
                        className={cn(
                          'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
                          isSelected
                            ? 'bg-cyan-100 text-cyan-700 border-2 border-cyan-300'
                            : 'bg-white/50 text-slate-600 border border-slate-200 hover:border-cyan-200 hover:bg-cyan-50'
                        )}
                      >
                        <span>{lang.flag}</span>
                        <span>{lang.label}</span>
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* 摘要信息 */}
              <div className="p-3 bg-slate-50 rounded-lg space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">Selectedproducts</span>
                  <HoloBadge variant={itemCount > 0 ? 'info' : 'default'}>
                    {itemCount} 個
                  </HoloBadge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">Processing模式</span>
                  <span className="text-slate-700 font-medium">
                    {itemCount <= 10 ? '即時Generate' : '後台Processing'}
                  </span>
                </div>
                {itemCount > 10 && (
                  <p className="text-xs text-amber-600 flex items-start gap-1">
                    <AlertCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                    大於 10 個products將使用後台AsyncProcessing，預計Need數minutes
                  </p>
                )}
              </div>

              {/* Generatebutton */}
              <HoloButton
                onClick={handleGenerate}
                disabled={itemCount === 0 || isProcessing}
                loading={isProcessing}
                icon={!isProcessing ? <Sparkles className="w-5 h-5" /> : undefined}
                size="lg"
                className="w-full"
              >
                {isProcessing
                  ? asyncTaskId
                    ? '後台Processing...'
                    : 'Generate中...'
                  : `批量Generate ${itemCount} 個products`}
              </HoloButton>

              {generateMutation.isError && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>
                    GenerateFailed:{' '}
                    {generateMutation.error instanceof Error
                      ? generateMutation.error.message
                      : 'UnknownError'}
                  </span>
                </div>
              )}
            </div>
          </HoloCard>
        </div>
      </div>

      {/* ResultArea */}
      <BatchResultList
        results={results}
        isProcessing={!!asyncTaskId}
        progress={asyncProgress || undefined}
        onViewDetail={onNavigateToEdit}
      />
    </div>
  )
}
