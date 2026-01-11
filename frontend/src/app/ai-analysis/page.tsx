'use client'

import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { api } from '@/lib/api'
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
  Clock
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
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

export default function AIAnalysisPage() {
  // State
  const [inputData, setInputData] = useState<string>(JSON.stringify({
    products: [
      { name: "北海道毛蟹", category: "鮮魚", our_price: 580, competitor_price: 620, stock: "有貨" },
      { name: "日本和牛 A5", category: "肉類", our_price: 1280, competitor_price: 1350, stock: "有貨" },
      { name: "秋刀魚", category: "鮮魚", our_price: 45, competitor_price: null, stock: "季節限定" },
    ],
    price_changes: [
      { product: "藍鰭吞拿魚", change: "+8%", reason: "供應緊張" },
      { product: "日本米", change: "-5%", reason: "對手促銷" },
    ],
    market_trends: {
      overall: "鮮魚類價格上漲趨勢",
      season: "冬季",
      hot_items: ["蟹類", "和牛", "海膽"]
    }
  }, null, 2))

  const [insightsResult, setInsightsResult] = useState<string | null>(null)
  const [strategyResult, setStrategyResult] = useState<string | null>(null)
  const [expandedSection, setExpandedSection] = useState<'insights' | 'strategy' | 'both'>('both')
  const [totalTokens, setTotalTokens] = useState(0)

  // Check AI config
  const { data: config } = useQuery({
    queryKey: ['ai-config'],
    queryFn: () => api.getAIConfig(),
  })

  // Generate insights mutation
  const insightsMutation = useMutation({
    mutationFn: (data: Record<string, any>) => api.generateDataInsights(data),
    onSuccess: (result) => {
      if (result.success) {
        setInsightsResult(result.content)
        setTotalTokens(prev => prev + result.tokens_used)
      }
    },
  })

  // Generate strategy mutation
  const strategyMutation = useMutation({
    mutationFn: ({ insights, context }: { insights: string; context: Record<string, any> }) =>
      api.generateMarketingStrategy(insights, context),
    onSuccess: (result) => {
      if (result.success) {
        setStrategyResult(result.content)
        setTotalTokens(prev => prev + result.tokens_used)
      }
    },
  })

  // Full analysis mutation
  const fullAnalysisMutation = useMutation({
    mutationFn: (data: Record<string, any>) => api.runFullAnalysis(data, {}),
    onSuccess: (result) => {
      if (result.insights) {
        setInsightsResult(result.insights.content)
      }
      if (result.strategy?.content) {
        setStrategyResult(result.strategy.content)
      }
      setTotalTokens(result.total_tokens)
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
      <div className="space-y-8 p-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <Brain className="w-8 h-8 text-primary" />
              AI 智能分析
            </h1>
            <p className="text-muted-foreground mt-2">
              兩個 AI 協同工作：數據摘要 + Marketing 策略
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
        <HoloCard glowColor="cyan" className="p-6">
          <h2 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-500" />
            分析流程
          </h2>

          <div className="flex flex-col md:flex-row items-center justify-center gap-4">
            <PipelineStep
              step={1}
              icon={BarChart3}
              title="輸入數據"
              description="市場數據、價格變動"
              status={inputData ? 'completed' : 'pending'}
              color="blue"
            />
            <ArrowRight className="w-6 h-6 text-slate-300 hidden md:block" />
            <ChevronDown className="w-6 h-6 text-slate-300 md:hidden" />
            <PipelineStep
              step={2}
              icon={FileText}
              title="AI #1: 數據摘要"
              description="分析並生成洞察報告"
              status={insightsMutation.isPending ? 'processing' : insightsResult ? 'completed' : 'pending'}
              color="purple"
            />
            <ArrowRight className="w-6 h-6 text-slate-300 hidden md:block" />
            <ChevronDown className="w-6 h-6 text-slate-300 md:hidden" />
            <PipelineStep
              step={3}
              icon={Target}
              title="AI #2: 策略建議"
              description="生成 Marketing 策略"
              status={strategyMutation.isPending || fullAnalysisMutation.isPending ? 'processing' : strategyResult ? 'completed' : 'pending'}
              color="green"
            />
          </div>
        </HoloCard>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Input Section */}
          <div className="space-y-4">
            <HoloCard glowColor="blue" className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-slate-800 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-blue-500" />
                  輸入數據
                </h3>
                <HoloBadge variant="info" size="sm">JSON 格式</HoloBadge>
              </div>

              <Textarea
                className="font-mono text-sm min-h-[300px]"
                value={inputData}
                onChange={(e) => setInputData(e.target.value)}
                placeholder="輸入 JSON 格式的數據..."
              />

              <div className="flex gap-3 mt-4">
                <HoloButton
                  className="flex-1"
                  onClick={handleFullAnalysis}
                  disabled={isLoading || !config?.api_key_set}
                  loading={fullAnalysisMutation.isPending}
                  icon={!fullAnalysisMutation.isPending ? <Play className="w-4 h-4" /> : undefined}
                >
                  {fullAnalysisMutation.isPending ? '分析中...' : '一鍵分析'}
                </HoloButton>

                <HoloButton
                  variant="secondary"
                  onClick={handleGenerateInsights}
                  disabled={isLoading || !config?.api_key_set}
                  loading={insightsMutation.isPending}
                >
                  {insightsMutation.isPending ? '' : '僅生成摘要'}
                </HoloButton>
              </div>

              {!config?.api_key_set && (
                <p className="text-sm text-red-500 mt-3 flex items-center gap-1">
                  <AlertCircle className="w-4 h-4" />
                  請先到 AI 設定頁面設定 API Key
                </p>
              )}
            </HoloCard>

            {/* Token Usage */}
            {totalTokens > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 rounded-xl bg-slate-50 border border-slate-200"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600 flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    本次分析使用 Tokens
                  </span>
                  <span className="font-bold text-slate-800">{totalTokens.toLocaleString()}</span>
                </div>
              </motion.div>
            )}
          </div>

          {/* Results Section */}
          <div className="space-y-4">
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
      "p-4 rounded-xl border transition-all",
      c.bg, c.border,
      status === 'processing' && "animate-pulse"
    )}>
      <div className="flex items-center gap-3">
        <div className={cn("p-2 rounded-lg transition-colors", c.icon)}>
          {status === 'processing' ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : status === 'completed' ? (
            <CheckCircle2 className="w-5 h-5" />
          ) : (
            <Icon className="w-5 h-5" />
          )}
        </div>
        <div>
          <p className="font-medium text-slate-800 text-sm">{title}</p>
          <p className="text-xs text-slate-500">{description}</p>
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
      className="glass-panel rounded-2xl border border-white/40 overflow-hidden"
    >
      {/* Header */}
      <div
        className={cn("p-4 flex items-center justify-between cursor-pointer border-b", c.header)}
        onClick={onToggle}
      >
        <div className="flex items-center gap-2">
          <Icon className={cn("w-5 h-5", c.icon)} />
          <h3 className="font-bold text-slate-800">{title}</h3>
          {content && (
            <HoloBadge variant="success" size="sm">
              <CheckCircle2 className="w-3 h-3" />
              已生成
            </HoloBadge>
          )}
        </div>
        <div className="flex items-center gap-2">
          {content && (
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onCopy()
              }}
            >
              <Copy className="w-4 h-4" />
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
            <div className="p-4 max-h-[400px] overflow-y-auto">
              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-primary" />
                </div>
              ) : error ? (
                <div className="p-4 rounded-lg bg-red-50 text-red-700">
                  <AlertCircle className="w-5 h-5 inline mr-2" />
                  {error}
                </div>
              ) : content ? (
                <div className="prose prose-sm max-w-none prose-headings:text-slate-800 prose-p:text-slate-600">
                  {renderContent(content)}
                </div>
              ) : (
                <div className="text-center py-12 text-slate-400">
                  <Icon className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p>尚未生成</p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
