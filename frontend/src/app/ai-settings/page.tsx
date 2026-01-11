'use client'

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, AIModel, AIConfigResponse, FetchedModel } from '@/lib/api'
import { motion } from 'framer-motion'
import {
  Settings,
  Key,
  Brain,
  Sparkles,
  Check,
  X,
  Loader2,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle2,
  Cpu,
  Zap,
  FileText,
  Target,
  ChevronRight,
  RefreshCw,
  Globe,
  Server
} from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { ModelCombobox } from '@/components/ui/model-combobox'
import { cn } from '@/lib/utils'
import { PageTransition, HoloCard, HoloButton, HoloBadge } from '@/components/ui/future-tech'

// =============================================
// Page Component
// =============================================

export default function AISettingsPage() {
  const queryClient = useQueryClient()

  // State
  const [apiKey, setApiKey] = useState('')
  const [baseUrl, setBaseUrl] = useState('')
  const [showApiKey, setShowApiKey] = useState(false)
  const [insightsModel, setInsightsModel] = useState('')
  const [strategyModel, setStrategyModel] = useState('')
  const [customInsightsModel, setCustomInsightsModel] = useState('')
  const [customStrategyModel, setCustomStrategyModel] = useState('')
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle')
  const [testMessage, setTestMessage] = useState('')

  // 動態獲取的模型列表
  const [fetchedModels, setFetchedModels] = useState<FetchedModel[]>([])
  const [fetchModelsStatus, setFetchModelsStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [fetchModelsError, setFetchModelsError] = useState('')

  // Fetch current config
  const { data: config, isLoading: configLoading, isError: configError } = useQuery({
    queryKey: ['ai-config'],
    queryFn: () => api.getAIConfig(),
    retry: 1,
    retryDelay: 1000,
  })

  // Fetch available models
  const { data: models, isLoading: modelsLoading } = useQuery({
    queryKey: ['ai-models'],
    queryFn: () => api.getAIModels(),
  })

  // Set initial values from config
  useEffect(() => {
    if (config) {
      setBaseUrl(config.base_url)
      setInsightsModel(config.insights_model)
      setStrategyModel(config.strategy_model)
    }
  }, [config])

  // Test connection mutation
  const testMutation = useMutation({
    mutationFn: ({ apiKey, baseUrl, model }: { apiKey: string; baseUrl: string; model: string }) =>
      api.testAIConnection(apiKey, baseUrl, model),
    onMutate: () => {
      setTestStatus('testing')
    },
    onSuccess: (data) => {
      if (data.valid) {
        setTestStatus('success')
        setTestMessage(data.message || '連接成功！')
      } else {
        setTestStatus('error')
        setTestMessage(data.error || '連接失敗')
      }
    },
    onError: (error: any) => {
      setTestStatus('error')
      setTestMessage(error.message || '測試失敗')
    },
  })

  // Save config mutation
  const saveMutation = useMutation({
    mutationFn: (data: { api_key?: string; base_url?: string; insights_model?: string; strategy_model?: string }) =>
      api.updateAIConfig(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-config'] })
    },
  })

  // Fetch models mutation
  const fetchModelsMutation = useMutation({
    mutationFn: (options: { apiKey?: string; baseUrl?: string; useSaved?: boolean }) =>
      api.fetchModelsFromAPI(options),
    onMutate: () => {
      setFetchModelsStatus('loading')
      setFetchModelsError('')
    },
    onSuccess: (data) => {
      if (data.success) {
        setFetchedModels(data.models)
        setFetchModelsStatus('success')
      } else {
        setFetchModelsStatus('error')
        setFetchModelsError(data.error || '獲取模型列表失敗')
      }
    },
    onError: (error: any) => {
      setFetchModelsStatus('error')
      setFetchModelsError(error.message || '獲取模型列表失敗')
    },
  })

  // Handle test connection
  const handleTestConnection = () => {
    const key = apiKey.trim() || (config?.api_key_set ? 'existing' : '')
    const url = baseUrl.trim() || config?.base_url || ''

    if (!key || key === 'existing') {
      setTestStatus('error')
      setTestMessage('請先輸入 API Key')
      return
    }
    if (!url) {
      setTestStatus('error')
      setTestMessage('請先輸入 Base URL')
      return
    }

    testMutation.mutate({ apiKey: key, baseUrl: url, model: 'gpt-3.5-turbo' })
  }

  // Handle fetch models from API
  const handleFetchModels = () => {
    const newKey = apiKey.trim()
    const newUrl = baseUrl.trim()

    // 如果有輸入新的 API Key，使用新的配置
    if (newKey) {
      if (!newUrl && !config?.base_url) {
        setFetchModelsStatus('error')
        setFetchModelsError('請輸入 Base URL')
        return
      }
      fetchModelsMutation.mutate({
        apiKey: newKey,
        baseUrl: newUrl || config?.base_url,
      })
    }
    // 否則使用已保存的配置
    else if (config?.api_key_set) {
      fetchModelsMutation.mutate({
        useSaved: true,
        baseUrl: newUrl || undefined,  // 如果有輸入新 URL 則使用，否則讓後端用保存的
      })
    }
    // 都沒有，顯示錯誤
    else {
      setFetchModelsStatus('error')
      setFetchModelsError('請先設定 API Key')
    }
  }

  // Handle save all settings
  const handleSaveAll = () => {
    const updates: any = {}

    if (apiKey.trim()) {
      updates.api_key = apiKey.trim()
    }
    if (baseUrl.trim()) {
      updates.base_url = baseUrl.trim()
    }

    // Handle custom model names
    const finalInsightsModel = insightsModel === 'custom' ? customInsightsModel : insightsModel
    const finalStrategyModel = strategyModel === 'custom' ? customStrategyModel : strategyModel

    if (finalInsightsModel) {
      updates.insights_model = finalInsightsModel
    }
    if (finalStrategyModel) {
      updates.strategy_model = finalStrategyModel
    }

    saveMutation.mutate(updates)
    setApiKey('')
    setTestStatus('idle')
  }

  if (configLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <p className="text-sm text-muted-foreground">正在連接後端...</p>
      </div>
    )
  }

  if (configError) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] gap-4 p-6">
        <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center">
          <AlertCircle className="w-8 h-8 text-red-600" />
        </div>
        <h2 className="text-xl font-semibold text-gray-900">無法連接後端</h2>
        <p className="text-gray-600 text-center max-w-md">
          請確保後端服務正在運行。在 backend 目錄執行：
        </p>
        <code className="px-4 py-2 bg-slate-100 rounded-lg text-sm font-mono">
          python -m uvicorn app.main:app --reload
        </code>
        <Button onClick={() => window.location.reload()} className="mt-4">
          <RefreshCw className="w-4 h-4 mr-2" />
          重試
        </Button>
      </div>
    )
  }

  return (
    <PageTransition>
      <div className="space-y-8 animate-fade-in-up p-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <Brain className="w-8 h-8 text-primary" />
              AI 設定
            </h1>
            <p className="text-muted-foreground mt-2">
              配置中轉站 API 連接和模型選擇
            </p>
          </div>
          <HoloBadge variant={config?.api_key_set ? 'success' : 'warning'}>
            {config?.api_key_set ? (
              <>
                <CheckCircle2 className="w-3 h-3" /> API 已設定
              </>
            ) : (
              <>
                <AlertCircle className="w-3 h-3" /> API 未設定
              </>
            )}
          </HoloBadge>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <InfoCard
            icon={Sparkles}
            title="數據摘要 AI"
            description="分析市場數據，自動生成結構化的數據洞察報告"
            color="purple"
          />
          <InfoCard
            icon={Target}
            title="策略顧問 AI"
            description="基於數據分析，生成可執行的 Marketing 策略建議"
            color="blue"
          />
        </div>

        {/* API Connection Section */}
        <HoloCard glowColor="cyan" className="p-6">
          <div className="flex items-center gap-2 mb-6">
            <div className="p-2 rounded-lg bg-amber-500/10">
              <Server className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-800">API 連接設定</h2>
              <p className="text-sm text-muted-foreground">設定中轉站地址和 API Key</p>
            </div>
          </div>

          {/* Current Status */}
          {config?.api_key_set && (
            <div className="mb-6 p-4 rounded-xl bg-green-50 border border-green-200">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  <span className="font-medium text-green-800">目前已設定</span>
                </div>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-green-700">
                    Key: <code className="px-2 py-0.5 bg-green-100 rounded font-mono">{config.api_key_preview}</code>
                  </span>
                  <span className="text-green-700">
                    URL: <code className="px-2 py-0.5 bg-green-100 rounded font-mono text-xs">{config.base_url}</code>
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Input Fields */}
          <div className="space-y-4">
            {/* Base URL */}
            <div>
              <Label htmlFor="base-url" className="text-slate-700 flex items-center gap-2">
                <Globe className="w-4 h-4" />
                Base URL（中轉站地址）
              </Label>
              <Input
                id="base-url"
                type="text"
                placeholder="https://api.example.com/v1"
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
                className="mt-2 font-mono"
              />
              <p className="text-xs text-muted-foreground mt-1">
                OpenAI 兼容的 API 端點，例如：https://api.openai.com/v1
              </p>
            </div>

            {/* API Key */}
            <div>
              <Label htmlFor="api-key" className="text-slate-700 flex items-center gap-2">
                <Key className="w-4 h-4" />
                API Key
              </Label>
              <div className="mt-2 flex gap-2">
                <div className="relative flex-1">
                  <Input
                    id="api-key"
                    type={showApiKey ? 'text' : 'password'}
                    placeholder={config?.api_key_set ? '輸入新 Key 以更換...' : 'sk-...'}
                    value={apiKey}
                    onChange={(e) => {
                      setApiKey(e.target.value)
                      setTestStatus('idle')
                    }}
                    className="pr-10 font-mono"
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </div>

            {/* Test & Save Buttons */}
            <div className="flex gap-3 pt-2">
              <HoloButton
                variant="secondary"
                onClick={handleTestConnection}
                disabled={testMutation.isPending}
                loading={testMutation.isPending}
                icon={!testMutation.isPending ? <Zap className="w-4 h-4" /> : undefined}
              >
                測試連接
              </HoloButton>
              <HoloButton
                variant="primary"
                onClick={handleSaveAll}
                disabled={saveMutation.isPending}
                loading={saveMutation.isPending}
                icon={!saveMutation.isPending ? <Check className="w-4 h-4" /> : undefined}
              >
                保存設定
              </HoloButton>
            </div>

            {/* Test Status */}
            {testStatus !== 'idle' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className={cn(
                  "p-3 rounded-lg flex items-center gap-2",
                  testStatus === 'testing' && "bg-blue-50 text-blue-700",
                  testStatus === 'success' && "bg-green-50 text-green-700",
                  testStatus === 'error' && "bg-red-50 text-red-700"
                )}
              >
                {testStatus === 'testing' && <Loader2 className="w-4 h-4 animate-spin" />}
                {testStatus === 'success' && <CheckCircle2 className="w-4 h-4" />}
                {testStatus === 'error' && <AlertCircle className="w-4 h-4" />}
                <span className="text-sm font-medium">{testMessage}</span>
              </motion.div>
            )}

            {/* Save Success */}
            {saveMutation.isSuccess && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-3 rounded-lg bg-green-50 text-green-700 flex items-center gap-2"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span className="text-sm font-medium">設定已保存</span>
              </motion.div>
            )}
          </div>
        </HoloCard>

        {/* Model Selection Section */}
        <HoloCard glowColor="purple" className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-purple-500/10">
                <Cpu className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-800">模型選擇</h2>
                <p className="text-sm text-muted-foreground">為不同任務選擇 AI 模型</p>
              </div>
            </div>
            <HoloButton
              variant="secondary"
              onClick={handleFetchModels}
              disabled={fetchModelsMutation.isPending}
              loading={fetchModelsMutation.isPending}
              icon={!fetchModelsMutation.isPending ? <RefreshCw className="w-4 h-4" /> : undefined}
            >
              從 API 獲取模型
            </HoloButton>
          </div>

          {/* Fetch Models Status */}
          {fetchModelsStatus !== 'idle' && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              className={cn(
                "mb-4 p-3 rounded-lg flex items-center gap-2",
                fetchModelsStatus === 'loading' && "bg-blue-50 text-blue-700",
                fetchModelsStatus === 'success' && "bg-green-50 text-green-700",
                fetchModelsStatus === 'error' && "bg-red-50 text-red-700"
              )}
            >
              {fetchModelsStatus === 'loading' && <Loader2 className="w-4 h-4 animate-spin" />}
              {fetchModelsStatus === 'success' && <CheckCircle2 className="w-4 h-4" />}
              {fetchModelsStatus === 'error' && <AlertCircle className="w-4 h-4" />}
              <span className="text-sm font-medium">
                {fetchModelsStatus === 'loading' && '正在獲取模型列表...'}
                {fetchModelsStatus === 'success' && `成功獲取 ${fetchedModels.length} 個模型`}
                {fetchModelsStatus === 'error' && fetchModelsError}
              </span>
            </motion.div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-purple-500" />
                <Label className="text-slate-700 font-medium">數據摘要模型</Label>
              </div>
              <ModelCombobox
                value={insightsModel}
                onValueChange={setInsightsModel}
                fetchedModels={fetchedModels}
                presetModels={models || []}
                placeholder="選擇模型..."
                searchPlaceholder="搜尋模型..."
              />
              {insightsModel === 'custom' && (
                <Input
                  placeholder="輸入自定義模型名稱..."
                  value={customInsightsModel}
                  onChange={(e) => setCustomInsightsModel(e.target.value)}
                  className="font-mono"
                />
              )}
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-blue-500" />
                <Label className="text-slate-700 font-medium">策略生成模型</Label>
              </div>
              <ModelCombobox
                value={strategyModel}
                onValueChange={setStrategyModel}
                fetchedModels={fetchedModels}
                presetModels={models || []}
                placeholder="選擇模型..."
                searchPlaceholder="搜尋模型..."
              />
              {strategyModel === 'custom' && (
                <Input
                  placeholder="輸入自定義模型名稱..."
                  value={customStrategyModel}
                  onChange={(e) => setCustomStrategyModel(e.target.value)}
                  className="font-mono"
                />
              )}
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <HoloButton
              variant="primary"
              onClick={handleSaveAll}
              disabled={saveMutation.isPending}
              loading={saveMutation.isPending}
              icon={!saveMutation.isPending ? <Check className="w-4 h-4" /> : undefined}
            >
              保存模型設定
            </HoloButton>
          </div>

          {saveMutation.isSuccess && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="p-3 rounded-lg bg-green-50 text-green-700 flex items-center gap-2"
            >
              <CheckCircle2 className="w-4 h-4" />
              <span className="text-sm font-medium">模型設定已保存</span>
            </motion.div>
          )}

          <div className="mt-6 p-4 rounded-xl bg-blue-50/50 border border-blue-100">
            <div className="flex items-start gap-3">
              <Zap className="w-5 h-5 text-blue-500 mt-0.5" />
              <div>
                <h4 className="font-medium text-blue-800">提示</h4>
                <p className="text-sm text-blue-600 mt-1">
                  點擊「從 API 獲取模型」可查看你的中轉站實際支持的模型。如果 API 不支持，可從預設列表選擇或使用「自定義模型」。
                </p>
              </div>
            </div>
          </div>
        </HoloCard>

        {/* Usage Guide */}
        <HoloCard glowColor="blue" className="p-6 bg-gradient-to-br from-slate-50/50 to-transparent">
          <h2 className="text-xl font-bold text-slate-800 mb-4 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary" />
            使用指南
          </h2>

          <div className="space-y-4">
            <GuideStep
              step={1}
              title="設定中轉站"
              description="輸入你的 API Base URL 和 API Key"
            />
            <GuideStep
              step={2}
              title="測試連接"
              description="點擊「測試連接」確認配置正確"
            />
            <GuideStep
              step={3}
              title="選擇模型"
              description="為數據摘要和策略生成選擇合適的模型"
            />
            <GuideStep
              step={4}
              title="開始分析"
              description="前往 AI 分析頁面開始使用"
            />
          </div>
        </HoloCard>
      </div>
    </PageTransition>
  )
}

// =============================================
// Sub Components
// =============================================

function InfoCard({
  icon: Icon,
  title,
  description,
  color
}: {
  icon: any
  title: string
  description: string
  color: 'purple' | 'blue'
}) {
  const colors = {
    purple: {
      bg: 'bg-purple-50',
      icon: 'bg-purple-500/10 text-purple-600',
      border: 'border-purple-100',
    },
    blue: {
      bg: 'bg-blue-50',
      icon: 'bg-blue-500/10 text-blue-600',
      border: 'border-blue-100',
    },
  }

  const c = colors[color]

  return (
    <div className={cn("p-4 rounded-xl border", c.bg, c.border)}>
      <div className="flex items-start gap-3">
        <div className={cn("p-2 rounded-lg", c.icon)}>
          <Icon className="w-5 h-5" />
        </div>
        <div>
          <h3 className="font-semibold text-slate-800">{title}</h3>
          <p className="text-sm text-muted-foreground mt-1">{description}</p>
        </div>
      </div>
    </div>
  )
}

function GuideStep({
  step,
  title,
  description
}: {
  step: number
  title: string
  description: string
}) {
  return (
    <div className="flex items-start gap-4">
      <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
        <span className="text-sm font-bold text-primary">{step}</span>
      </div>
      <div className="flex-1">
        <h4 className="font-medium text-slate-800">{title}</h4>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      {step < 4 && <ChevronRight className="w-4 h-4 text-slate-300 mt-2" />}
    </div>
  )
}
