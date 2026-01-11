'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { api, analyticsApi } from '@/lib/api'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Brain,
  Sparkles,
  Target,
  FileText,
  Loader2,
  Play,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  ArrowRight,
  Copy,
  Download,
  ChevronDown,
  ChevronUp,
  Zap,
  BarChart3,
  TrendingUp,
  Clock,
  Database
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import {
  PageTransition,
  HoloCard,
  HoloPanelHeader,
  HoloButton,
  HoloBadge
} from '@/components/ui/future-tech'

// Simple markdown-like renderer (no external dependency)
const renderContent = (text: string) => {
  // Split by newlines and render
  return text.split('\n').map((line, i) => {
    // Headers
    if (line.startsWith('### ')) {
      return <h3 key={i} className="text-lg font-bold mt-4 mb-2">{line.slice(4)}</h3>
    }
    if (line.startsWith('## ')) {
      return <h2 key={i} className="text-xl font-bold mt-4 mb-2">{line.slice(3)}</h2>
    }
    if (line.startsWith('# ')) {
      return <h1 key={i} className="text-2xl font-bold mt-4 mb-2">{line.slice(2)}</h1>
    }
    // Bold
    if (line.startsWith('**') && line.endsWith('**')) {
      return <p key={i} className="font-bold">{line.slice(2, -2)}</p>
    }
    // List items
    if (line.startsWith('- ') || line.startsWith('• ')) {
      return <li key={i} className="ml-4">{line.slice(2)}</li>
    }
    if (line.match(/^\d+\. /)) {
      return <li key={i} className="ml-4 list-decimal">{line.replace(/^\d+\. /, '')}</li>
    }
    // Empty line
    if (line.trim() === '') {
      return <br key={i} />
    }
    // Regular paragraph
    return <p key={i} className="mb-2">{line}</p>
  })
}

// =============================================
// Page Component
// =============================================

// 數據摘要類型
interface DataSummary {
  total_products: number
  total_competitors: number
  total_categories: number
  monthly_revenue: number
  monthly_profit: number
  pending_alerts: number
  products_sample: { name: string; price: number; category: string }[]
  competitors_sample: { name: string; platform: string; product_count: number }[]
}

export default function AIAnalysisPage() {
  // State
  const [inputData, setInputData] = useState<string>('')
  const [dataSummary, setDataSummary] = useState<DataSummary | null>(null)
  const [insightsResult, setInsightsResult] = useState<string | null>(null)
  const [strategyResult, setStrategyResult] = useState<string | null>(null)
  const [expandedSection, setExpandedSection] = useState<'insights' | 'strategy' | 'both'>('both')
  const [totalTokens, setTotalTokens] = useState(0)
  const [isLoadingData, setIsLoadingData] = useState(false)
  const [dataLoaded, setDataLoaded] = useState(false)

  // Check AI config
  const { data: config } = useQuery({
    queryKey: ['ai-config'],
    queryFn: () => api.getAIConfig(),
  })

  // 從數據庫加載數據
  const loadDatabaseData = async () => {
    setIsLoadingData(true)
    try {
      // 並行獲取多個數據源
      const [productsRes, competitorsRes, categoriesRes, commandCenterRes] = await Promise.all([
        api.getProducts(1, 50),
        api.getCompetitors(),
        api.getCategories(1, 20),
        analyticsApi.getCommandCenter().catch(() => null)
      ])

      // 獲取競品產品（取前3個競爭對手的產品）
      const competitorProducts: any[] = []
      const activeCompetitors = competitorsRes.data?.slice(0, 3) || []
      for (const competitor of activeCompetitors) {
        try {
          const products = await api.getCompetitorProducts(competitor.id, 1, 10)
          competitorProducts.push({
            competitor_name: competitor.name,
            platform: competitor.platform,
            products: products.data?.slice(0, 5).map((p: any) => ({
              name: p.name,
              price: p.price,
              original_price: p.original_price,
              discount_percent: p.discount_percent,
              is_available: p.is_available
            })) || []
          })
        } catch (e) {
          // 忽略單個競爭對手的錯誤
        }
      }

      // 組織數據結構
      const analysisData = {
        summary: {
          total_products: productsRes.total || 0,
          total_competitors: competitorsRes.data?.length || 0,
          total_categories: categoriesRes.total || 0,
          monthly_revenue: commandCenterRes?.stats?.monthly_revenue || 0,
          monthly_profit: commandCenterRes?.stats?.monthly_profit || 0,
          pending_alerts: commandCenterRes?.stats?.unread_alerts || 0
        },
        our_products: productsRes.data?.slice(0, 20).map((p: any) => ({
          name: p.name,
          sku: p.sku,
          category: p.category,
          price: p.price,
          cost: p.cost,
          stock_quantity: p.stock_quantity,
          status: p.status,
          profit_margin: p.price && p.cost ? ((p.price - p.cost) / p.price * 100).toFixed(1) + '%' : null
        })) || [],
        competitors: activeCompetitors.map((c: any) => ({
          name: c.name,
          platform: c.platform,
          product_count: c.product_count,
          is_active: c.is_active,
          last_scraped: c.last_scraped_at
        })),
        competitor_products: competitorProducts,
        categories: categoriesRes.items?.map((c: any) => ({
          name: c.name,
          product_count: c.product_count,
          url: c.url
        })) || [],
        recent_activity: commandCenterRes?.recent_activity?.slice(0, 5) || [],
        analysis_time: new Date().toISOString()
      }

      setInputData(JSON.stringify(analysisData, null, 2))

      // 設置摘要數據供 UI 顯示
      setDataSummary({
        total_products: analysisData.summary.total_products,
        total_competitors: analysisData.summary.total_competitors,
        total_categories: analysisData.summary.total_categories,
        monthly_revenue: analysisData.summary.monthly_revenue,
        monthly_profit: analysisData.summary.monthly_profit,
        pending_alerts: analysisData.summary.pending_alerts,
        products_sample: analysisData.our_products.slice(0, 5).map((p: any) => ({
          name: p.name,
          price: p.price || 0,
          category: p.category || '未分類'
        })),
        competitors_sample: analysisData.competitors.slice(0, 3).map((c: any) => ({
          name: c.name,
          platform: c.platform,
          product_count: c.product_count || 0
        }))
      })

      setDataLoaded(true)
    } catch (error) {
      console.error('Failed to load database data:', error)
      alert('加載數據失敗，請稍後再試')
    } finally {
      setIsLoadingData(false)
    }
  }

  // Generate insights mutation
  const insightsMutation = useMutation({
    mutationFn: async (data: Record<string, any>) => {
      const result = await api.generateDataInsights(data)
      if (!result.success) {
        throw new Error(result.error || '生成摘要失敗')
      }
      return result
    },
    onSuccess: (result) => {
      setInsightsResult(result.content)
      setTotalTokens(prev => prev + result.tokens_used)
    },
  })

  // Generate strategy mutation
  const strategyMutation = useMutation({
    mutationFn: async ({ insights, context }: { insights: string; context: Record<string, any> }) => {
      const result = await api.generateMarketingStrategy(insights, context)
      if (!result.success) {
        throw new Error(result.error || '生成策略失敗')
      }
      return result
    },
    onSuccess: (result) => {
      setStrategyResult(result.content)
      setTotalTokens(prev => prev + result.tokens_used)
    },
  })

  // Full analysis mutation
  const fullAnalysisMutation = useMutation({
    mutationFn: async (data: Record<string, any>) => {
      const result = await api.runFullAnalysis(data, {})
      // 後端可能返回 200 但 success: false，需要手動處理
      if (!result.success) {
        const errorMsg = result.error || result.strategy?.error || '分析失敗，請稍後再試'
        throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg))
      }
      return result
    },
    onSuccess: (result) => {
      if (result.insights) {
        setInsightsResult(result.insights.content)
      }
      if (result.strategy?.content) {
        setStrategyResult(result.strategy.content)
      }
      setTotalTokens(result.total_tokens || 0)
    },
  })

  // Handle step 1: Generate insights
  const handleGenerateInsights = () => {
    try {
      const data = JSON.parse(inputData)
      setInsightsResult(null)
      setStrategyResult(null)
      setTotalTokens(0)
      insightsMutation.mutate(data)
    } catch (e) {
      alert('輸入數據格式錯誤，請確保是有效的 JSON')
    }
  }

  // Handle step 2: Generate strategy
  const handleGenerateStrategy = () => {
    if (insightsResult) {
      strategyMutation.mutate({ insights: insightsResult, context: {} })
    }
  }

  // Handle full analysis
  const handleFullAnalysis = () => {
    try {
      const data = JSON.parse(inputData)
      setInsightsResult(null)
      setStrategyResult(null)
      setTotalTokens(0)
      fullAnalysisMutation.mutate(data)
    } catch (e) {
      alert('輸入數據格式錯誤，請確保是有效的 JSON')
    }
  }

  // Copy to clipboard
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const isLoading = insightsMutation.isPending || strategyMutation.isPending || fullAnalysisMutation.isPending

  return (
    <PageTransition>
      <div className="space-y-4 sm:space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <Brain className="w-6 h-6 sm:w-7 sm:h-7 text-primary" />
              AI 智能分析
            </h1>
            <p className="text-sm text-muted-foreground mt-1">
              數據摘要 + Marketing 策略
            </p>
          </div>

          {/* Status Badge */}
          {config?.api_key_set ? (
            <HoloBadge variant="success">
              <CheckCircle2 className="w-3 h-3" /> AI 已就緒
            </HoloBadge>
          ) : (
            <HoloBadge variant="error">
              <AlertCircle className="w-3 h-3" /> 請先設定 API Key
            </HoloBadge>
          )}
        </div>

        {/* Pipeline Visualization */}
        <HoloCard glowColor="cyan" className="p-3 sm:p-4">
          <h2 className="text-sm sm:text-base font-bold text-slate-800 mb-3 flex items-center gap-2">
            <Zap className="w-4 h-4 sm:w-5 sm:h-5 text-amber-500" />
            分析流程
          </h2>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-3">
            <PipelineStep
              step={1}
              icon={BarChart3}
              title="輸入數據"
              description="市場數據、價格變動"
              status={inputData ? 'completed' : 'pending'}
              color="blue"
            />
            <ArrowRight className="w-4 h-4 text-slate-300 hidden sm:block" />
            <ChevronDown className="w-4 h-4 text-slate-300 sm:hidden" />
            <PipelineStep
              step={2}
              icon={FileText}
              title="AI #1: 摘要"
              description="生成洞察報告"
              status={insightsMutation.isPending ? 'processing' : insightsResult ? 'completed' : 'pending'}
              color="purple"
            />
            <ArrowRight className="w-4 h-4 text-slate-300 hidden sm:block" />
            <ChevronDown className="w-4 h-4 text-slate-300 sm:hidden" />
            <PipelineStep
              step={3}
              icon={Target}
              title="AI #2: 策略"
              description="Marketing 建議"
              status={strategyMutation.isPending || fullAnalysisMutation.isPending ? 'processing' : strategyResult ? 'completed' : 'pending'}
              color="green"
            />
          </div>
        </HoloCard>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Input Section */}
          <div className="space-y-3 sm:space-y-4">
            <HoloCard glowColor="blue" className="p-3 sm:p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm sm:text-base font-bold text-slate-800 flex items-center gap-2">
                  <Database className="w-4 h-4 sm:w-5 sm:h-5 text-blue-500" />
                  數據來源
                </h3>
                {dataLoaded && (
                  <HoloBadge variant="success" size="sm">
                    <CheckCircle2 className="w-3 h-3" /> 數據已就緒
                  </HoloBadge>
                )}
              </div>

              {/* 未加載數據時顯示加載按鈕 */}
              {!dataLoaded ? (
                <div className="text-center py-6">
                  <div className="w-12 h-12 sm:w-14 sm:h-14 mx-auto mb-3 rounded-xl bg-gradient-to-br from-blue-50 to-cyan-50 flex items-center justify-center">
                    <Database className="w-6 h-6 sm:w-7 sm:h-7 text-blue-500" />
                  </div>
                  <p className="text-sm text-slate-600 mb-3">從數據庫獲取最新數據</p>
                  <HoloButton
                    onClick={loadDatabaseData}
                    disabled={isLoadingData}
                    loading={isLoadingData}
                    icon={!isLoadingData ? <RefreshCw className="w-4 h-4" /> : undefined}
                  >
                    {isLoadingData ? '正在加載...' : '加載數據'}
                  </HoloButton>
                </div>
              ) : (
                /* 已加載數據時顯示摘要 */
                <div className="space-y-3">
                  {/* 統計數據網格 */}
                  <div className="grid grid-cols-3 gap-2">
                    <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg p-2 border border-blue-100">
                      <p className="text-[10px] text-slate-500">產品</p>
                      <p className="text-base sm:text-lg font-bold text-blue-600">{dataSummary?.total_products || 0}</p>
                    </div>
                    <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-2 border border-purple-100">
                      <p className="text-[10px] text-slate-500">競品</p>
                      <p className="text-base sm:text-lg font-bold text-purple-600">{dataSummary?.total_competitors || 0}</p>
                    </div>
                    <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-2 border border-green-100">
                      <p className="text-[10px] text-slate-500">類別</p>
                      <p className="text-base sm:text-lg font-bold text-green-600">{dataSummary?.total_categories || 0}</p>
                    </div>
                    <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-lg p-2 border border-amber-100">
                      <p className="text-[10px] text-slate-500">月營收</p>
                      <p className="text-base sm:text-lg font-bold text-amber-600">${(dataSummary?.monthly_revenue || 0).toLocaleString()}</p>
                    </div>
                    <div className="bg-gradient-to-br from-cyan-50 to-blue-50 rounded-lg p-2 border border-cyan-100">
                      <p className="text-[10px] text-slate-500">月利潤</p>
                      <p className="text-base sm:text-lg font-bold text-cyan-600">${(dataSummary?.monthly_profit || 0).toLocaleString()}</p>
                    </div>
                    <div className="bg-gradient-to-br from-red-50 to-pink-50 rounded-lg p-2 border border-red-100">
                      <p className="text-[10px] text-slate-500">警報</p>
                      <p className="text-base sm:text-lg font-bold text-red-600">{dataSummary?.pending_alerts || 0}</p>
                    </div>
                  </div>

                  {/* 產品樣本 - 手機隱藏 */}
                  {dataSummary?.products_sample && dataSummary.products_sample.length > 0 && (
                    <div className="hidden sm:block bg-slate-50 rounded-lg p-2 border border-slate-100">
                      <p className="text-[10px] text-slate-500 mb-1">產品樣本</p>
                      <div className="space-y-0.5">
                        {dataSummary.products_sample.slice(0, 3).map((p, i) => (
                          <div key={i} className="flex items-center justify-between text-xs">
                            <span className="text-slate-700 truncate flex-1">{p.name}</span>
                            <span className="text-slate-500 ml-2">${p.price}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 競品樣本 - 手機隱藏 */}
                  {dataSummary?.competitors_sample && dataSummary.competitors_sample.length > 0 && (
                    <div className="hidden sm:block bg-slate-50 rounded-lg p-2 border border-slate-100">
                      <p className="text-[10px] text-slate-500 mb-1">競爭對手</p>
                      <div className="space-y-0.5">
                        {dataSummary.competitors_sample.map((c, i) => (
                          <div key={i} className="flex items-center justify-between text-xs">
                            <span className="text-slate-700">{c.name}</span>
                            <span className="text-slate-500">{c.product_count} 個</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 重新加載按鈕 */}
                  <div className="flex justify-center pt-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={loadDatabaseData}
                      disabled={isLoadingData}
                      className="text-slate-500 text-xs h-7"
                    >
                      <RefreshCw className={cn("w-3 h-3 mr-1", isLoadingData && "animate-spin")} />
                      刷新
                    </Button>
                  </div>
                </div>
              )}
            </HoloCard>

            {/* 分析按鈕 */}
            <HoloCard glowColor="cyan" className="p-3 sm:p-4">
              <div className="flex gap-2">
                <HoloButton
                  className="flex-1"
                  onClick={handleFullAnalysis}
                  disabled={isLoading || !config?.api_key_set || !inputData}
                  loading={fullAnalysisMutation.isPending}
                  icon={!fullAnalysisMutation.isPending ? <Play className="w-4 h-4" /> : undefined}
                >
                  {fullAnalysisMutation.isPending ? '分析中...' : '一鍵分析'}
                </HoloButton>

                <HoloButton
                  variant="secondary"
                  onClick={handleGenerateInsights}
                  disabled={isLoading || !config?.api_key_set || !inputData}
                  loading={insightsMutation.isPending}
                  className="hidden sm:flex"
                >
                  {insightsMutation.isPending ? '' : '僅摘要'}
                </HoloButton>
              </div>

              {!config?.api_key_set && (
                <p className="text-xs text-red-500 mt-2 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  請先設定 API Key
                </p>
              )}

              {!inputData && config?.api_key_set && (
                <p className="text-xs text-amber-600 mt-2 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  請先加載數據
                </p>
              )}
            </HoloCard>

            {/* Token Usage */}
            {totalTokens > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-2 sm:p-3 rounded-lg bg-slate-50 border border-slate-200"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-600 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    Tokens
                  </span>
                  <span className="text-sm font-bold text-slate-800">{totalTokens.toLocaleString()}</span>
                </div>
              </motion.div>
            )}
          </div>

          {/* Results Section */}
          <div className="space-y-3 sm:space-y-4">
            {/* Insights Result */}
            <ResultPanel
              title="數據摘要"
              icon={FileText}
              content={insightsResult}
              isLoading={insightsMutation.isPending}
              error={insightsMutation.error?.message}
              color="purple"
              onCopy={() => insightsResult && copyToClipboard(insightsResult)}
              expanded={expandedSection === 'insights' || expandedSection === 'both'}
              onToggle={() => setExpandedSection(
                expandedSection === 'insights' ? 'both' :
                expandedSection === 'both' ? 'strategy' : 'insights'
              )}
            />

            {/* Generate Strategy Button */}
            {insightsResult && !strategyResult && !fullAnalysisMutation.isPending && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-center"
              >
                <HoloButton
                  onClick={handleGenerateStrategy}
                  disabled={strategyMutation.isPending}
                  loading={strategyMutation.isPending}
                  icon={!strategyMutation.isPending ? <ArrowRight className="w-4 h-4" /> : undefined}
                >
                  {strategyMutation.isPending ? '生成策略中...' : '繼續生成 Marketing 策略'}
                </HoloButton>
              </motion.div>
            )}

            {/* Strategy Result */}
            <ResultPanel
              title="Marketing 策略"
              icon={Target}
              content={strategyResult}
              isLoading={strategyMutation.isPending || (fullAnalysisMutation.isPending && !!insightsResult)}
              error={strategyMutation.error?.message || fullAnalysisMutation.error?.message}
              color="green"
              onCopy={() => strategyResult && copyToClipboard(strategyResult)}
              expanded={expandedSection === 'strategy' || expandedSection === 'both'}
              onToggle={() => setExpandedSection(
                expandedSection === 'strategy' ? 'both' :
                expandedSection === 'both' ? 'insights' : 'strategy'
              )}
            />
          </div>
        </div>
      </div>
    </PageTransition>
  )
}

// =============================================
// Sub Components
// =============================================

function PipelineStep({
  step,
  icon: Icon,
  title,
  description,
  status,
  color
}: {
  step: number
  icon: any
  title: string
  description: string
  status: 'pending' | 'processing' | 'completed'
  color: 'blue' | 'purple' | 'green'
}) {
  const colors = {
    blue: {
      bg: status === 'completed' ? 'bg-blue-100' : 'bg-blue-50',
      icon: status === 'completed' ? 'bg-blue-500 text-white' : 'bg-blue-100 text-blue-500',
      border: status === 'completed' ? 'border-blue-300' : 'border-blue-100',
    },
    purple: {
      bg: status === 'completed' ? 'bg-purple-100' : 'bg-purple-50',
      icon: status === 'completed' ? 'bg-purple-500 text-white' : 'bg-purple-100 text-purple-500',
      border: status === 'completed' ? 'border-purple-300' : 'border-purple-100',
    },
    green: {
      bg: status === 'completed' ? 'bg-green-100' : 'bg-green-50',
      icon: status === 'completed' ? 'bg-green-500 text-white' : 'bg-green-100 text-green-500',
      border: status === 'completed' ? 'border-green-300' : 'border-green-100',
    },
  }

  const c = colors[color]

  return (
    <div className={cn(
      "p-2 sm:p-3 rounded-lg border transition-all flex-1 min-w-0",
      c.bg, c.border,
      status === 'processing' && "animate-pulse"
    )}>
      <div className="flex items-center gap-2">
        <div className={cn("p-1.5 rounded-md transition-colors flex-shrink-0", c.icon)}>
          {status === 'processing' ? (
            <Loader2 className="w-3.5 h-3.5 sm:w-4 sm:h-4 animate-spin" />
          ) : status === 'completed' ? (
            <CheckCircle2 className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          ) : (
            <Icon className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
          )}
        </div>
        <div className="min-w-0">
          <p className="font-medium text-slate-800 text-xs sm:text-sm truncate">{title}</p>
          <p className="text-[10px] sm:text-xs text-slate-500 truncate">{description}</p>
        </div>
      </div>
    </div>
  )
}

function ResultPanel({
  title,
  icon: Icon,
  content,
  isLoading,
  error,
  color,
  onCopy,
  expanded,
  onToggle
}: {
  title: string
  icon: any
  content: string | null
  isLoading: boolean
  error?: string
  color: 'purple' | 'green'
  onCopy: () => void
  expanded: boolean
  onToggle: () => void
}) {
  const colors = {
    purple: {
      header: 'bg-purple-50 border-purple-100',
      icon: 'text-purple-500',
    },
    green: {
      header: 'bg-green-50 border-green-100',
      icon: 'text-green-500',
    },
  }

  const c = colors[color]

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel rounded-xl border border-white/40 overflow-hidden"
    >
      {/* Header */}
      <div
        className={cn("px-3 py-2 sm:p-3 flex items-center justify-between cursor-pointer border-b", c.header)}
        onClick={onToggle}
      >
        <div className="flex items-center gap-1.5 sm:gap-2 min-w-0">
          <Icon className={cn("w-4 h-4 flex-shrink-0", c.icon)} />
          <h3 className="text-sm font-bold text-slate-800 truncate">{title}</h3>
          {content && (
            <HoloBadge variant="success" size="sm" className="hidden sm:flex">
              <CheckCircle2 className="w-2.5 h-2.5" />
              已生成
            </HoloBadge>
          )}
        </div>
        <div className="flex items-center gap-1 flex-shrink-0">
          {content && (
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onCopy()
              }}
              className="h-7 w-7 p-0"
            >
              <Copy className="w-3.5 h-3.5" />
            </Button>
          )}
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </div>
      </div>

      {/* Content */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0 }}
            animate={{ height: 'auto' }}
            exit={{ height: 0 }}
            className="overflow-hidden"
          >
            <div className="p-3 max-h-[300px] sm:max-h-[400px] overflow-y-auto">
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin text-primary" />
                </div>
              ) : error ? (
                <div className="p-2 rounded-lg bg-red-50 text-red-700 text-xs sm:text-sm">
                  <AlertCircle className="w-4 h-4 inline mr-1" />
                  {error}
                </div>
              ) : content ? (
                <div className="prose prose-sm max-w-none prose-headings:text-slate-800 prose-p:text-slate-600 text-sm">
                  {renderContent(content)}
                </div>
              ) : (
                <div className="text-center py-8 text-slate-400">
                  <Icon className="w-8 h-8 mx-auto mb-2 opacity-30" />
                  <p className="text-xs">尚未生成</p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
