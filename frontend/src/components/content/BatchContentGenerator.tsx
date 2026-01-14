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

// 配置選項
const CONTENT_TYPES = [
  { value: 'title', label: '商品標題' },
  { value: 'selling_points', label: '賣點列表' },
  { value: 'description', label: '商品描述' },
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
  // 輸入模式
  const [inputMode, setInputMode] = useState<InputMode>('products')

  // 選中的商品（商品選擇模式）
  const [selectedProducts, setSelectedProducts] = useState<OwnProduct[]>([])

  // 導入的商品資訊（文件導入模式）
  const [importedProducts, setImportedProducts] = useState<ProductInfo[]>([])

  // 生成配置
  const [contentType, setContentType] = useState<ContentBatchGenerateRequest['content_type']>('full_copy')
  const [style, setStyle] = useState<ContentBatchGenerateRequest['style']>('professional')
  const [selectedLanguages, setSelectedLanguages] = useState<LanguageCode[]>(['TC'])

  // 生成結果
  const [results, setResults] = useState<BatchResultItem[]>([])
  const [asyncTaskId, setAsyncTaskId] = useState<string | null>(null)
  const [asyncProgress, setAsyncProgress] = useState<BatchProgress | null>(null)

  // 輪詢定時器
  const pollingRef = useRef<NodeJS.Timeout | null>(null)

  // 清理輪詢
  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }, [])

  // 批量生成 mutation
  const generateMutation = useMutation({
    mutationFn: (data: ContentBatchGenerateRequest) => api.batchGenerateContent(data),
    onSuccess: (response: BatchGenerateResponse) => {
      if (response.mode === 'sync') {
        // 同步模式：直接顯示結果
        setResults(response.results)
        setAsyncTaskId(null)
        setAsyncProgress(null)
      } else {
        // 異步模式：開始輪詢
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

  // 開始輪詢任務狀態
  const startPolling = useCallback((taskId: string) => {
    stopPolling()

    const poll = async () => {
      try {
        const status = await api.getBatchTaskStatus(taskId)
        setAsyncProgress(status.progress)
        setResults(status.results)

        // 任務完成，停止輪詢
        if (status.status === 'completed' || status.status === 'failed') {
          stopPolling()
          setAsyncTaskId(null)
        }
      } catch (error) {
        console.error('輪詢任務狀態失敗:', error)
        stopPolling()
        setAsyncTaskId(null)
      }
    }

    // 立即執行一次
    poll()

    // 每 2 秒輪詢一次
    pollingRef.current = setInterval(poll, 2000)
  }, [stopPolling])

  // 組件卸載時清理
  useEffect(() => {
    return () => {
      stopPolling()
    }
  }, [stopPolling])

  // 計算當前選中的商品數量
  const itemCount = inputMode === 'products' ? selectedProducts.length : importedProducts.length

  // 構建請求並提交
  const handleGenerate = () => {
    const items =
      inputMode === 'products'
        ? selectedProducts.map((p) => ({ product_id: p.id }))
        : importedProducts.map((p) => ({ product_info: p }))

    if (items.length === 0) return

    // 重置結果
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

  // 切換輸入模式時重置
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
      {/* 輸入模式切換 */}
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
          從商品列表選擇
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
          CSV 文件導入
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左側：輸入區 */}
        <div className="lg:col-span-2">
          <HoloCard glowColor="cyan" className="h-full">
            <div className="p-6">
              <HoloPanelHeader
                title={inputMode === 'products' ? '選擇商品' : '導入文件'}
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

        {/* 右側：配置區 */}
        <div>
          <HoloCard glowColor="purple" className="h-full">
            <div className="p-6 space-y-6">
              <HoloPanelHeader
                title="生成設定"
                icon={<Settings2 className="w-5 h-5" />}
              />

              {/* 內容類型 */}
              <div className="space-y-2">
                <Label>內容類型</Label>
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

              {/* 語言選擇 */}
              <div className="space-y-2">
                <Label>輸出語言（可多選）</Label>
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
                  <span className="text-slate-600">已選商品</span>
                  <HoloBadge variant={itemCount > 0 ? 'info' : 'default'}>
                    {itemCount} 個
                  </HoloBadge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">處理模式</span>
                  <span className="text-slate-700 font-medium">
                    {itemCount <= 10 ? '即時生成' : '後台處理'}
                  </span>
                </div>
                {itemCount > 10 && (
                  <p className="text-xs text-amber-600 flex items-start gap-1">
                    <AlertCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
                    大於 10 個商品將使用後台異步處理，預計需要數分鐘
                  </p>
                )}
              </div>

              {/* 生成按鈕 */}
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
                    ? '後台處理中...'
                    : '生成中...'
                  : `批量生成 ${itemCount} 個商品`}
              </HoloButton>

              {generateMutation.isError && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>
                    生成失敗:{' '}
                    {generateMutation.error instanceof Error
                      ? generateMutation.error.message
                      : '未知錯誤'}
                  </span>
                </div>
              )}
            </div>
          </HoloCard>
        </div>
      </div>

      {/* 結果區域 */}
      <BatchResultList
        results={results}
        isProcessing={!!asyncTaskId}
        progress={asyncProgress || undefined}
        onViewDetail={onNavigateToEdit}
      />
    </div>
  )
}
