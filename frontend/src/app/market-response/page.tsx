'use client'

import { useState, useRef, useCallback } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  Search,
  BarChart3,
  Globe,
  ShoppingCart,
  Zap,
  Filter,
  ArrowUpRight,
  Package,
  ThermometerSun,
  Layers,
  Search as SearchIcon,
  Loader2,
  Eye,
  TrendingUp,
  Sparkles,
  Bell,
  FileBarChart,
  Target,
  Download,
  Bot,
  Play,
  CheckCircle2,
  XCircle,
  AlertCircle
} from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'
import { useToast } from '@/components/ui/use-toast'
import {
  PageTransition,
  HoloCard,
  HoloPanelHeader,
  HoloButton,
  DataMetric,
  StaggerContainer
} from '@/components/ui/future-tech'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

// =============================================
// Interfaces
// =============================================

interface CategoryData {
  name: string
  count: number
  percentage: number
}

// =============================================
// Page Component
// =============================================

export default function MarketResponsePage() {
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [batchDialogOpen, setBatchDialogOpen] = useState(false)
  const [batchLimit, setBatchLimit] = useState('10')
  const [batchCategory, setBatchCategory] = useState('all')
  const [batchPlatform, setBatchPlatform] = useState('hktvmall')

  // =============================================
  // SSE 批量匹配狀態
  // =============================================
  type BatchPhase = 'idle' | 'processing' | 'done'

  interface BatchResultItem {
    product_id: string
    product_name: string
    candidates: number
    matches: number
    match_details: { name: string; confidence: number; url: string }[]
    error?: string
    status: 'searching' | 'done' | 'error'
  }

  interface BatchSummary {
    processed: number
    total_matches: number
    total_candidates: number
  }

  const [batchPhase, setBatchPhase] = useState<BatchPhase>('idle')
  const [batchCurrent, setBatchCurrent] = useState(0)
  const [batchTotal, setBatchTotal] = useState(0)
  const [batchCurrentName, setBatchCurrentName] = useState('')
  const [batchResults, setBatchResults] = useState<BatchResultItem[]>([])
  const [batchSummary, setBatchSummary] = useState<BatchSummary | null>(null)
  const abortRef = useRef<AbortController | null>(null)
  const resultsEndRef = useRef<HTMLDivElement>(null)

  // Handle search debounce
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
    const timeoutId = setTimeout(() => {
      setDebouncedQuery(e.target.value)
    }, 500)
    return () => clearTimeout(timeoutId)
  }

  // 匯出報告功能
  const handleExportReport = () => {
    toast({
      title: '功能開發中',
      description: '報告匯出功能即將推出，敬請期待！',
    })
  }

  // 重置批量匹配狀態
  const resetBatchState = useCallback(() => {
    setBatchPhase('idle')
    setBatchCurrent(0)
    setBatchTotal(0)
    setBatchCurrentName('')
    setBatchResults([])
    setBatchSummary(null)
  }, [])

  // SSE 批量匹配
  const handleBatchMatch = useCallback(async () => {
    const limit = parseInt(batchLimit)
    const categoryMain = batchCategory === 'all' ? undefined : batchCategory

    // 重置狀態
    setBatchPhase('processing')
    setBatchCurrent(0)
    setBatchTotal(limit)
    setBatchCurrentName('')
    setBatchResults([])
    setBatchSummary(null)

    const controller = new AbortController()
    abortRef.current = controller

    try {
      const url = api.batchFindCompetitorsStreamUrl(limit, categoryMain, batchPlatform)
      const response = await fetch(url, {
        method: 'POST',
        signal: controller.signal,
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('無法讀取串流')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        // 保留最後一行（可能不完整）
        buffer = lines.pop() || ''

        let currentEvent = ''
        for (const line of lines) {
          if (line.startsWith('event: ')) {
            currentEvent = line.slice(7).trim()
          } else if (line.startsWith('data: ') && currentEvent) {
            try {
              const data = JSON.parse(line.slice(6))

              if (currentEvent === 'progress') {
                setBatchCurrent(data.current)
                setBatchTotal(data.total)
                setBatchCurrentName(data.product_name)
              } else if (currentEvent === 'result') {
                setBatchResults(prev => [...prev, {
                  product_id: data.product_id,
                  product_name: data.product_name,
                  candidates: data.candidates,
                  matches: data.matches,
                  match_details: data.match_details || [],
                  error: data.error,
                  status: data.error ? 'error' : 'done',
                }])
                // 自動捲動到最新結果
                setTimeout(() => resultsEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 50)
              } else if (currentEvent === 'done') {
                setBatchSummary(data)
                setBatchPhase('done')
                // 刷新相關數據
                queryClient.invalidateQueries({ queryKey: ['competitors-for-mrc'] })
                queryClient.invalidateQueries({ queryKey: ['products-for-mrc'] })
              }
            } catch {
              // 忽略 JSON 解析失敗
            }
            currentEvent = ''
          }
        }
      }
    } catch (err: any) {
      if (err.name === 'AbortError') return
      toast({
        title: '批量匹配失敗',
        description: err.message,
        variant: 'destructive',
      })
      setBatchPhase('idle')
    }
  }, [batchLimit, batchCategory, batchPlatform, queryClient, toast])

  // Dialog 關閉時清理
  const handleBatchDialogClose = useCallback((open: boolean) => {
    if (!open) {
      // 如果正在處理中，中斷連接
      if (batchPhase === 'processing') {
        abortRef.current?.abort()
      }
      resetBatchState()
    }
    setBatchDialogOpen(open)
  }, [batchPhase, resetBatchState])

  // 使用現有 API 獲取數據
  const { data: products } = useQuery({
    queryKey: ['products-for-mrc'],
    queryFn: () => api.getProducts(1, 100),
  })

  const { data: competitors } = useQuery({
    queryKey: ['competitors-for-mrc'],
    queryFn: () => api.getCompetitors(),
  })

  const { data: alerts } = useQuery({
    queryKey: ['alerts-for-mrc'],
    queryFn: () => api.getAlerts(false, undefined, 10),
  })

  const { data: categories, isLoading: categoriesLoading } = useQuery({
    queryKey: ['categories-for-mrc'],
    queryFn: () => api.getCategories(1, 20),
  })

  // 計算統計數據
  const stats = {
    total_skus: products?.total || 0,
    products_with_competitors: competitors?.data?.reduce((sum, c) => sum + c.product_count, 0) || 0,
    seasonal_products: products?.data?.filter((p) => p.status === 'active').length || 0,
    unread_alerts: alerts?.unread_count || 0,
  }

  // 搜索結果使用現有商品數據過濾
  const searchResults = debouncedQuery.length > 0
    ? products?.data?.filter((p) =>
        p.name?.toLowerCase().includes(debouncedQuery.toLowerCase()) ||
        p.sku?.toLowerCase().includes(debouncedQuery.toLowerCase())
      ) || []
    : []
  const searchLoading = false

  // 季節性商品（使用現有商品數據）
  const seasonalProducts = products?.data?.slice(0, 5) || []
  const seasonalLoading = !products

  // 分類數據轉換
  const categoryData = categories?.items?.map((cat, idx) => ({
    name: cat.name,
    count: cat.total_products,
    percentage: Math.min(100, (cat.total_products / (products?.total || 1)) * 100 * 5),
  })) || []

  return (
    <PageTransition>
      <div className="space-y-4 sm:space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Globe className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />
            <h1 className="page-title">市場應對</h1>
          </div>
          <div className="flex items-center gap-1.5 sm:gap-3">
            <Badge variant="outline" className="px-2 py-0.5 sm:px-3 sm:py-1 bg-blue-50 text-blue-700 border-blue-200 text-[10px] sm:text-xs">
              <Zap className="w-2.5 h-2.5 sm:w-3 sm:h-3 mr-0.5 sm:mr-1 fill-blue-700" /> 即時
            </Badge>
            <Dialog open={batchDialogOpen} onOpenChange={handleBatchDialogClose}>
              <DialogTrigger asChild>
                <HoloButton variant="primary" size="sm" icon={<Bot className="w-3.5 h-3.5" />}>
                  <span className="hidden sm:inline">批量匹配</span>
                  <span className="sm:hidden">匹配</span>
                </HoloButton>
              </DialogTrigger>
              <DialogContent className="sm:max-w-lg">
                <DialogHeader>
                  <DialogTitle>批量競品匹配</DialogTitle>
                  <DialogDescription>
                    自動搜索競品平台上的競爭商品，並使用 AI 智能判斷是否為同級商品
                  </DialogDescription>
                </DialogHeader>

                {/* 設定區：idle 時顯示 */}
                {batchPhase === 'idle' && (
                  <div className="space-y-4 py-4">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">處理數量</label>
                      <Select value={batchLimit} onValueChange={setBatchLimit}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="10">10 個商品（測試）</SelectItem>
                          <SelectItem value="20">20 個商品</SelectItem>
                          <SelectItem value="30">30 個商品</SelectItem>
                          <SelectItem value="50">50 個商品</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">目標平台</label>
                      <Select value={batchPlatform} onValueChange={setBatchPlatform}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="hktvmall">HKTVmall</SelectItem>
                          <SelectItem value="wellcome">惠康 Wellcome</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">分類篩選（可選）</label>
                      <Select value={batchCategory} onValueChange={setBatchCategory}>
                        <SelectTrigger>
                          <SelectValue placeholder="選擇分類" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">全部分類</SelectItem>
                          <SelectItem value="鮮魚">鮮魚</SelectItem>
                          <SelectItem value="貝類">貝類</SelectItem>
                          <SelectItem value="蟹類">蟹類</SelectItem>
                          <SelectItem value="其他海鮮">其他海鮮</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="rounded-lg bg-blue-50 p-3 text-sm text-blue-700">
                      <p className="font-medium mb-1">預估成本</p>
                      <p className="text-xs">
                        {parseInt(batchLimit)} 個商品 ≈ ¥{(parseInt(batchLimit) * 0.04).toFixed(2)} (Claude API)
                        {batchPlatform === 'hktvmall' && <><br />+ Firecrawl API 額度</>}
                        {batchPlatform === 'wellcome' && <><br />惠康使用 JSON-LD 提取，零額外成本</>}
                      </p>
                    </div>
                    <div className="rounded-lg bg-yellow-50 p-3 text-sm text-yellow-700">
                      <p className="font-medium mb-1">注意事項</p>
                      <p className="text-xs">
                        • 只會處理尚未匹配競品的商品<br />
                        • 執行時間約 {Math.ceil(parseInt(batchLimit) / 5)} 分鐘<br />
                        • 建議先執行 10 個商品測試
                      </p>
                    </div>
                  </div>
                )}

                {/* 進度區：processing / done 時顯示 */}
                {(batchPhase === 'processing' || batchPhase === 'done') && (
                  <div className="space-y-4 py-4">
                    {/* 進度條 */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">
                          {batchPhase === 'processing' ? (
                            <span className="flex items-center gap-1.5">
                              <Loader2 className="w-3.5 h-3.5 animate-spin" />
                              正在搜索: {batchCurrentName}
                            </span>
                          ) : (
                            <span className="flex items-center gap-1.5 text-green-600">
                              <CheckCircle2 className="w-3.5 h-3.5" />
                              匹配完成
                            </span>
                          )}
                        </span>
                        <span className="font-medium tabular-nums">
                          {batchPhase === 'done' ? batchSummary?.processed : batchCurrent}/{batchTotal}
                        </span>
                      </div>
                      <Progress
                        value={batchPhase === 'done' ? 100 : (batchTotal > 0 ? (batchCurrent / batchTotal) * 100 : 0)}
                      />
                    </div>

                    {/* 結果列表 */}
                    <div className="max-h-[240px] overflow-y-auto rounded-lg border bg-slate-50/50 divide-y divide-slate-100">
                      {batchResults.length === 0 && batchPhase === 'processing' && (
                        <div className="p-4 text-center text-sm text-muted-foreground">
                          等待第一個結果...
                        </div>
                      )}
                      {batchResults.map((item, idx) => (
                        <div key={idx} className="px-3 py-2 text-sm flex items-start gap-2">
                          {/* 狀態 icon */}
                          {item.error ? (
                            <XCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                          ) : item.matches > 0 ? (
                            <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                          ) : (
                            <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                          )}
                          {/* 內容 */}
                          <div className="flex-1 min-w-0">
                            <span className="font-medium text-slate-700 truncate block">
                              {item.product_name}
                            </span>
                            {item.error ? (
                              <span className="text-xs text-red-500">錯誤: {item.error}</span>
                            ) : item.matches > 0 && item.match_details[0] ? (
                              <span className="text-xs text-green-600">
                                → {item.match_details[0].name}{' '}
                                <span className="font-medium">
                                  {Math.round(item.match_details[0].confidence * 100)}%
                                </span>
                              </span>
                            ) : (
                              <span className="text-xs text-muted-foreground">
                                {item.candidates > 0 ? `找到 ${item.candidates} 個候選，但無匹配` : '未找到匹配'}
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                      <div ref={resultsEndRef} />
                    </div>

                    {/* 完成摘要 */}
                    {batchPhase === 'done' && batchSummary && (
                      <div className="rounded-lg bg-green-50 border border-green-200 p-3 text-sm text-green-700">
                        <p className="font-medium mb-1">匹配完成</p>
                        <div className="flex gap-4 text-xs">
                          <span>處理 {batchSummary.processed} 個</span>
                          <span>候選 {batchSummary.total_candidates} 個</span>
                          <span className="font-medium">匹配 {batchSummary.total_matches} 個</span>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <DialogFooter>
                  {batchPhase === 'idle' && (
                    <>
                      <Button variant="outline" onClick={() => handleBatchDialogClose(false)}>
                        取消
                      </Button>
                      <Button onClick={handleBatchMatch}>
                        <Play className="mr-2 h-4 w-4" />
                        開始匹配
                      </Button>
                    </>
                  )}
                  {batchPhase === 'processing' && (
                    <Button variant="outline" onClick={() => {
                      abortRef.current?.abort()
                      setBatchPhase('done')
                    }}>
                      停止
                    </Button>
                  )}
                  {batchPhase === 'done' && (
                    <Button onClick={() => handleBatchDialogClose(false)}>
                      關閉
                    </Button>
                  )}
                </DialogFooter>
              </DialogContent>
            </Dialog>
            <HoloButton variant="secondary" size="sm" icon={<Download className="w-3.5 h-3.5" />} onClick={handleExportReport}>
              <span className="hidden sm:inline">匯出</span>
            </HoloButton>
          </div>
        </div>

        {/* Feature Introduction Cards */}
        <StaggerContainer className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-3 gap-2 sm:gap-4">
          <Link href="/competitors">
            <FeatureCard icon={Eye} title="競品監測" description="追蹤價格變動" color="blue" />
          </Link>
          <Link href="/products">
            <FeatureCard icon={Target} title="SKU 配對" description="AI 智能配對" color="purple" />
          </Link>
          <Link href="/ai-analysis">
            <FeatureCard icon={TrendingUp} title="趨勢分析" description="價格走勢" color="green" />
          </Link>
          <Link href="/alerts">
            <FeatureCard icon={Bell} title="智能警報" description="即時推送" color="orange" />
          </Link>
          <Link href="/agent">
            <FeatureCard icon={Sparkles} title="AI 文案" description="自動生成" color="pink" />
          </Link>
          <FeatureCard icon={FileBarChart} title="報表匯出" description="Excel/PDF" color="cyan" onClick={handleExportReport} />
        </StaggerContainer>

        {/* Search Section */}
        <HoloCard className="p-1.5 sm:p-2" glowColor="blue">
          <div className="flex items-center">
            <SearchIcon className="w-4 h-4 sm:w-5 sm:h-5 ml-2 sm:ml-3 text-muted-foreground" />
            <Input
              className="border-none shadow-none focus-visible:ring-0 bg-transparent text-sm sm:text-lg placeholder:text-muted-foreground/50 h-9 sm:h-12"
              placeholder="搜尋商品..."
              value={searchQuery}
              onChange={handleSearch}
            />
            {searchLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin text-primary" />}
          </div>
        </HoloCard>

        {/* Search Results Dropdown */}
        {debouncedQuery && searchResults && (
          <div className="relative -mt-6">
            <div className="absolute top-0 left-0 right-0 bg-white/90 backdrop-blur-xl rounded-xl border border-slate-200 shadow-xl z-50 overflow-hidden max-h-[400px] overflow-y-auto">
              {searchResults.length > 0 ? (
                <div className="divide-y divide-slate-100">
                  {searchResults.map((product) => (
                    <Link key={product.id} href={`/products`}>
                      <div className="p-4 hover:bg-blue-50/50 transition-colors flex items-center justify-between cursor-pointer group">
                        <div>
                          <h4 className="font-medium text-slate-800 group-hover:text-primary transition-colors">{product.name}</h4>
                          <p className="text-xs text-slate-500 flex items-center gap-2 mt-1">
                            <Badge variant="secondary" className="text-[10px] h-5">{product.sku}</Badge>
                            <span>{product.category || '未分類'}</span>
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-slate-800">${Number(product.price || 0).toFixed(2)}</p>
                          <p className={cn(
                            "text-xs",
                            product.status === 'active' ? "text-green-600" : "text-red-500"
                          )}>{product.status === 'active' ? '有貨' : '缺貨'}</p>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center text-muted-foreground">
                  找不到符合「{debouncedQuery}」的商品
                </div>
              )}
            </div>
          </div>
        )}

        {/* Stats Overview */}
        <StaggerContainer className="grid grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-4">
          <Link href="/products">
            <DataMetric
              label="SKU"
              value={stats?.total_skus || 0}
              icon={<Package className="w-4 h-4 sm:w-5 sm:h-5 text-blue-600" />}
              color="blue"
              size="sm"
            />
          </Link>
          <Link href="/competitors">
            <DataMetric
              label="監測競品"
              value={stats?.products_with_competitors || 0}
              icon={<Layers className="w-4 h-4 sm:w-5 sm:h-5 text-purple-600" />}
              color="purple"
              size="sm"
            />
          </Link>
          <Link href="/products">
            <DataMetric
              label="當季商品"
              value={stats?.seasonal_products || 0}
              icon={<ThermometerSun className="w-4 h-4 sm:w-5 sm:h-5 text-orange-600" />}
              color="orange"
              size="sm"
            />
          </Link>
          <Link href="/alerts">
            <DataMetric
              label="待處理"
              value={stats?.unread_alerts || 0}
              icon={<Zap className="w-4 h-4 sm:w-5 sm:h-5 text-cyan-600" />}
              color="cyan"
              size="sm"
            />
          </Link>
        </StaggerContainer>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 sm:gap-6">
          {/* Category Breakdown */}
          <HoloCard className="lg:col-span-2" glowColor="blue">
            <HoloPanelHeader
              title="分類分佈"
              icon={<BarChart3 className="w-4 h-4 sm:w-5 sm:h-5" />}
              action={
                <Link href="/categories">
                  <HoloButton variant="ghost" size="sm">全部</HoloButton>
                </Link>
              }
            />
            <div className="p-3 sm:p-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-4">
                {categoriesLoading ? (
                  <div className="col-span-2 py-8 flex justify-center"><Loader2 className="animate-spin w-5 h-5" /></div>
                ) : categoryData.slice(0, 4).map((cat, idx) => (
                  <Link key={idx} href="/categories">
                    <CategoryCard category={cat} index={idx} />
                  </Link>
                ))}
              </div>
            </div>
          </HoloCard>

          {/* Seasonal Products */}
          <HoloCard glowColor="green" className="bg-gradient-to-b from-orange-50/30 to-transparent">
            <HoloPanelHeader
              title="熱門商品"
              icon={<ThermometerSun className="w-4 h-4 sm:w-5 sm:h-5 text-orange-500" />}
              action={
                <Badge className="bg-orange-100 text-orange-700 hover:bg-orange-200 border-none text-[10px] sm:text-xs">精選</Badge>
              }
            />
            <div className="p-3 sm:p-6">
              <div className="space-y-2 sm:space-y-4">
                {seasonalLoading ? (
                  <div className="py-8 flex justify-center"><Loader2 className="animate-spin w-5 h-5" /></div>
                ) : seasonalProducts.slice(0, 3).map((product) => (
                  <Link key={product.id} href="/products">
                    <div className="flex items-center gap-2 sm:gap-3 p-2 sm:p-3 rounded-lg sm:rounded-xl bg-white/50 hover:bg-white/80 transition-all cursor-pointer group border border-transparent hover:border-orange-100">
                      <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg bg-gray-100 overflow-hidden flex-shrink-0 relative">
                        <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                          <Package className="w-5 h-5 sm:w-6 sm:h-6" />
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-slate-800 truncate group-hover:text-orange-600 transition-colors">
                          {product.name}
                        </h4>
                        <div className="flex items-center justify-between mt-0.5 sm:mt-1">
                          <span className="text-[10px] sm:text-xs text-muted-foreground">{product.status === 'active' ? '有貨' : '缺貨'}</span>
                          <span className="font-bold text-xs sm:text-sm">${Number(product.price || 0).toFixed(0)}</span>
                        </div>
                      </div>
                      <ArrowUpRight className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-slate-300 group-hover:text-orange-500 transition-colors" />
                    </div>
                  </Link>
                ))}
              </div>

              <Link href="/products">
                <HoloButton className="w-full mt-3 sm:mt-4" variant="secondary" size="sm">
                  查看全部
                </HoloButton>
              </Link>
            </div>
          </HoloCard>
        </div>
      </div>
    </PageTransition>
  )
}

// =============================================
// Sub Components
// =============================================

function CategoryCard({ category, index }: { category: CategoryData, index: number }) {
  return (
    <div className="flex items-center p-2.5 sm:p-4 rounded-lg sm:rounded-xl bg-slate-50/50 border border-slate-100 hover:border-blue-200 hover:bg-blue-50/50 transition-all cursor-pointer">
      <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-white flex items-center justify-center shadow-sm text-sm sm:text-lg font-bold text-slate-300 mr-2.5 sm:mr-4">
        {index + 1}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex justify-between mb-1 gap-2">
          <span className="text-sm sm:text-base font-medium text-slate-700 truncate">{category.name}</span>
          <span className="text-sm sm:text-base font-bold text-slate-900 flex-shrink-0">{category.count}</span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-1.5 sm:h-2 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${category.percentage}%` }}
            transition={{ duration: 1, delay: index * 0.1 }}
            className="bg-primary h-full rounded-full"
          />
        </div>
      </div>
    </div>
  )
}

// =============================================
// 功能介紹卡片組件
// =============================================

function FeatureCard({
  icon: Icon,
  title,
  description,
  color,
  onClick
}: {
  icon: any
  title: string
  description: string
  color: 'blue' | 'purple' | 'green' | 'orange' | 'pink' | 'cyan'
  onClick?: () => void
}) {
  const colorMap = {
    blue: {
      bg: 'bg-blue-50 hover:bg-blue-100/80',
      icon: 'bg-blue-500/10 text-blue-600',
      border: 'border-blue-100 hover:border-blue-200',
    },
    purple: {
      bg: 'bg-purple-50 hover:bg-purple-100/80',
      icon: 'bg-purple-500/10 text-purple-600',
      border: 'border-purple-100 hover:border-purple-200',
    },
    green: {
      bg: 'bg-green-50 hover:bg-green-100/80',
      icon: 'bg-green-500/10 text-green-600',
      border: 'border-green-100 hover:border-green-200',
    },
    orange: {
      bg: 'bg-orange-50 hover:bg-orange-100/80',
      icon: 'bg-orange-500/10 text-orange-600',
      border: 'border-orange-100 hover:border-orange-200',
    },
    pink: {
      bg: 'bg-pink-50 hover:bg-pink-100/80',
      icon: 'bg-pink-500/10 text-pink-600',
      border: 'border-pink-100 hover:border-pink-200',
    },
    cyan: {
      bg: 'bg-cyan-50 hover:bg-cyan-100/80',
      icon: 'bg-cyan-500/10 text-cyan-600',
      border: 'border-cyan-100 hover:border-cyan-200',
    },
  }

  const colors = colorMap[color]

  return (
    <motion.div
      whileHover={{ y: -2, scale: 1.01 }}
      transition={{ duration: 0.2 }}
      onClick={onClick}
      className={cn(
        "p-2.5 sm:p-4 rounded-lg sm:rounded-xl border transition-all cursor-pointer",
        colors.bg,
        colors.border
      )}
    >
      <div className="flex items-start gap-2 sm:gap-3">
        <div className={cn("p-1.5 sm:p-2 rounded-md sm:rounded-lg flex-shrink-0", colors.icon)}>
          <Icon className="w-4 h-4 sm:w-5 sm:h-5" />
        </div>
        <div className="min-w-0">
          <h3 className="text-sm sm:text-base font-semibold text-slate-800 mb-0.5 sm:mb-1">{title}</h3>
          <p className="text-[10px] sm:text-sm text-slate-500 leading-relaxed">{description}</p>
        </div>
      </div>
    </motion.div>
  )
}
