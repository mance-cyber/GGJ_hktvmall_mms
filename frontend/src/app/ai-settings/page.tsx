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
import { useLocale } from '@/components/providers/locale-provider'

// =============================================
// Page Component
// =============================================

export default function AISettingsPage() {
  const { t } = useLocale()
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

  // Dynamically fetched model list
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
        setTestMessage(data.message || t('ai_settings.test_success'))
      } else {
        setTestStatus('error')
        setTestMessage(data.error || t('ai_settings.test_failed'))
      }
    },
    onError: (error: any) => {
      setTestStatus('error')
      setTestMessage(error.message || t('ai_settings.test_error'))
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
        setFetchModelsError(data.error || t('ai_settings.error_fetch_models'))
      }
    },
    onError: (error: any) => {
      setFetchModelsStatus('error')
      setFetchModelsError(error.message || t('ai_settings.error_fetch_models'))
    },
  })

  // Handle test connection
  const handleTestConnection = () => {
    const key = apiKey.trim() || (config?.api_key_set ? 'existing' : '')
    const url = baseUrl.trim() || config?.base_url || ''

    if (!key || key === 'existing') {
      setTestStatus('error')
      setTestMessage(t('ai_settings.error_api_key_missing'))
      return
    }
    if (!url) {
      setTestStatus('error')
      setTestMessage(t('ai_settings.error_base_url_missing'))
      return
    }

    testMutation.mutate({ apiKey: key, baseUrl: url, model: 'gpt-3.5-turbo' })
  }

  // Handle fetch models from API
  const handleFetchModels = () => {
    const newKey = apiKey.trim()
    const newUrl = baseUrl.trim()

    // If new API Key is entered, use new config
    if (newKey) {
      if (!newUrl && !config?.base_url) {
        setFetchModelsStatus('error')
        setFetchModelsError(t('ai_settings.error_base_url_required'))
        return
      }
      fetchModelsMutation.mutate({
        apiKey: newKey,
        baseUrl: newUrl || config?.base_url,
      })
    }
    // Otherwise use saved config
    else if (config?.api_key_set) {
      fetchModelsMutation.mutate({
        useSaved: true,
        baseUrl: newUrl || undefined,  // If new URL entered, use it; otherwise let backend use saved value
      })
    }
    // Neither provided, show error
    else {
      setFetchModelsStatus('error')
      setFetchModelsError(t('ai_settings.error_set_api_key'))
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
      <div className="flex flex-col items-center justify-center min-h-[300px] gap-3">
        <Loader2 className="w-6 h-6 sm:w-8 sm:h-8 animate-spin text-primary" />
        <p className="text-xs sm:text-sm text-muted-foreground">{t('ai_settings.connecting')}</p>
      </div>
    )
  }

  if (configError) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[300px] gap-3 p-4">
        <div className="w-12 h-12 sm:w-16 sm:h-16 rounded-full bg-red-100 flex items-center justify-center">
          <AlertCircle className="w-6 h-6 sm:w-8 sm:h-8 text-red-600" />
        </div>
        <h2 className="text-lg sm:text-xl font-semibold text-gray-900">{t('ai_settings.error_backend')}</h2>
        <p className="text-xs sm:text-sm text-gray-600 text-center max-w-md">
          {t('ai_settings.error_backend_desc')}
        </p>
        <Button onClick={() => window.location.reload()} size="sm" className="mt-2">
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
          {t('ai_settings.retry')}
        </Button>
      </div>
    )
  }

  return (
    <PageTransition>
      <div className="space-y-4 sm:space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Brain className="w-5 h-5 sm:w-6 sm:h-6 text-primary" />
            <h1 className="page-title">{t('ai_settings.title')}</h1>
          </div>
          <HoloBadge variant={config?.api_key_set ? 'success' : 'warning'} className="text-[10px] sm:text-xs">
            {config?.api_key_set ? (
              <><CheckCircle2 className="w-3 h-3" /> {t('ai_settings.badge_configured')}</>
            ) : (
              <><AlertCircle className="w-3 h-3" /> {t('ai_settings.badge_not_configured')}</>
            )}
          </HoloBadge>
        </div>

        {/* Info Cards */}
        <div className="grid grid-cols-2 gap-2 sm:gap-4">
          <InfoCard
            icon={Sparkles}
            title={t('ai_settings.info_insights_title')}
            description={t('ai_settings.info_insights_desc')}
            color="purple"
          />
          <InfoCard
            icon={Target}
            title={t('ai_settings.info_strategy_title')}
            description={t('ai_settings.info_strategy_desc')}
            color="blue"
          />
        </div>

        {/* API Connection Section */}
        <HoloCard glowColor="cyan" className="p-3 sm:p-6">
          <div className="flex items-center gap-2 mb-4 sm:mb-6">
            <div className="p-1.5 sm:p-2 rounded-lg bg-amber-500/10">
              <Server className="w-4 h-4 sm:w-5 sm:h-5 text-amber-600" />
            </div>
            <div>
              <h2 className="text-base sm:text-xl font-bold text-slate-800">{t('ai_settings.section_api_connection')}</h2>
              <p className="text-xs sm:text-sm text-muted-foreground hidden sm:block">{t('ai_settings.section_api_connection_desc')}</p>
            </div>
          </div>

          {/* Current Status */}
          {config?.api_key_set && (
            <div className="mb-4 sm:mb-6 p-2.5 sm:p-4 rounded-lg sm:rounded-xl bg-green-50 border border-green-200">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 sm:w-5 sm:h-5 text-green-600" />
                  <span className="text-sm font-medium text-green-800">{t('ai_settings.status_configured')}</span>
                </div>
                <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-4 text-xs sm:text-sm">
                  <span className="text-green-700 truncate">
                    Key: <code className="px-1.5 py-0.5 bg-green-100 rounded font-mono">{config.api_key_preview}</code>
                  </span>
                  <span className="text-green-700 truncate">
                    <code className="px-1.5 py-0.5 bg-green-100 rounded font-mono text-[10px] sm:text-xs">{config.base_url}</code>
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Input Fields */}
          <div className="space-y-3 sm:space-y-4">
            {/* Base URL */}
            <div>
              <Label htmlFor="base-url" className="text-xs sm:text-sm text-slate-700 flex items-center gap-1.5">
                <Globe className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                Base URL
              </Label>
              <Input
                id="base-url"
                type="text"
                placeholder="https://api.example.com/v1"
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
                className="mt-1.5 font-mono text-sm h-9 sm:h-10"
              />
            </div>

            {/* API Key */}
            <div>
              <Label htmlFor="api-key" className="text-xs sm:text-sm text-slate-700 flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                API Key
              </Label>
              <div className="mt-1.5 flex gap-2">
                <div className="relative flex-1">
                  <Input
                    id="api-key"
                    type={showApiKey ? 'text' : 'password'}
                    placeholder={config?.api_key_set ? t('ai_settings.placeholder_new_key') : 'sk-...'}
                    value={apiKey}
                    onChange={(e) => {
                      setApiKey(e.target.value)
                      setTestStatus('idle')
                    }}
                    className="pr-9 font-mono text-sm h-9 sm:h-10"
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showApiKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>
            </div>

            {/* Test & Save Buttons */}
            <div className="flex gap-2 sm:gap-3 pt-1">
              <HoloButton
                variant="secondary"
                size="sm"
                onClick={handleTestConnection}
                disabled={testMutation.isPending}
                loading={testMutation.isPending}
                icon={!testMutation.isPending ? <Zap className="w-3.5 h-3.5" /> : undefined}
              >
                {t('ai_settings.test')}
              </HoloButton>
              <HoloButton
                variant="primary"
                size="sm"
                onClick={handleSaveAll}
                disabled={saveMutation.isPending}
                loading={saveMutation.isPending}
                icon={!saveMutation.isPending ? <Check className="w-3.5 h-3.5" /> : undefined}
              >
                {t('ai_settings.save')}
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
                <span className="text-sm font-medium">{t('ai_settings.saved')}</span>
              </motion.div>
            )}
          </div>
        </HoloCard>

        {/* Model Selection Section */}
        <HoloCard glowColor="purple" className="p-3 sm:p-6">
          <div className="flex items-center justify-between mb-4 sm:mb-6 gap-2">
            <div className="flex items-center gap-2">
              <div className="p-1.5 sm:p-2 rounded-lg bg-purple-500/10">
                <Cpu className="w-4 h-4 sm:w-5 sm:h-5 text-purple-600" />
              </div>
              <div>
                <h2 className="text-base sm:text-xl font-bold text-slate-800">{t('ai_settings.section_model_selection')}</h2>
              </div>
            </div>
            <HoloButton
              variant="secondary"
              size="sm"
              onClick={handleFetchModels}
              disabled={fetchModelsMutation.isPending}
              loading={fetchModelsMutation.isPending}
              icon={!fetchModelsMutation.isPending ? <RefreshCw className="w-3.5 h-3.5" /> : undefined}
            >
              <span className="hidden sm:inline">{t('ai_settings.fetch_models')}</span>
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
                {fetchModelsStatus === 'loading' && t('ai_settings.fetching_models')}
                {fetchModelsStatus === 'success' && t('ai_settings.models_fetched').replace('{n}', String(fetchedModels.length))}
                {fetchModelsStatus === 'error' && fetchModelsError}
              </span>
            </motion.div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
            <div className="space-y-2 sm:space-y-3">
              <div className="flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-purple-500" />
                <Label className="text-xs sm:text-sm text-slate-700 font-medium">{t('ai_settings.label_insights_model')}</Label>
              </div>
              <ModelCombobox
                value={insightsModel}
                onValueChange={setInsightsModel}
                fetchedModels={fetchedModels}
                presetModels={models || []}
                placeholder={t('ai_settings.placeholder_select')}
                searchPlaceholder={t('ai_settings.placeholder_search')}
              />
              {insightsModel === 'custom' && (
                <Input
                  placeholder={t('ai_settings.placeholder_custom_model')}
                  value={customInsightsModel}
                  onChange={(e) => setCustomInsightsModel(e.target.value)}
                  className="font-mono text-sm h-9"
                />
              )}
            </div>

            <div className="space-y-2 sm:space-y-3">
              <div className="flex items-center gap-1.5">
                <Target className="w-3.5 h-3.5 text-blue-500" />
                <Label className="text-xs sm:text-sm text-slate-700 font-medium">{t('ai_settings.label_strategy_model')}</Label>
              </div>
              <ModelCombobox
                value={strategyModel}
                onValueChange={setStrategyModel}
                fetchedModels={fetchedModels}
                presetModels={models || []}
                placeholder={t('ai_settings.placeholder_select')}
                searchPlaceholder={t('ai_settings.placeholder_search')}
              />
              {strategyModel === 'custom' && (
                <Input
                  placeholder={t('ai_settings.placeholder_custom_model')}
                  value={customStrategyModel}
                  onChange={(e) => setCustomStrategyModel(e.target.value)}
                  className="font-mono text-sm h-9"
                />
              )}
            </div>
          </div>

          <div className="flex justify-end pt-3 sm:pt-4">
            <HoloButton
              variant="primary"
              size="sm"
              onClick={handleSaveAll}
              disabled={saveMutation.isPending}
              loading={saveMutation.isPending}
              icon={!saveMutation.isPending ? <Check className="w-3.5 h-3.5" /> : undefined}
            >
              {t('ai_settings.save')}
            </HoloButton>
          </div>

          {saveMutation.isSuccess && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="p-2 sm:p-3 rounded-lg bg-green-50 text-green-700 flex items-center gap-2"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span className="text-xs sm:text-sm font-medium">{t('ai_settings.saved_short')}</span>
            </motion.div>
          )}

          <div className="mt-4 sm:mt-6 p-2.5 sm:p-4 rounded-lg sm:rounded-xl bg-blue-50/50 border border-blue-100 hidden sm:block">
            <div className="flex items-start gap-2">
              <Zap className="w-4 h-4 text-blue-500 mt-0.5" />
              <p className="text-xs text-blue-600">
                {t('ai_settings.hint_fetch_models')}
              </p>
            </div>
          </div>
        </HoloCard>

        {/* Usage Guide - hidden on mobile */}
        <HoloCard glowColor="blue" className="p-3 sm:p-6 bg-gradient-to-br from-slate-50/50 to-transparent hidden sm:block">
          <h2 className="text-base sm:text-xl font-bold text-slate-800 mb-3 sm:mb-4 flex items-center gap-2">
            <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />
            {t('ai_settings.section_guide')}
          </h2>

          <div className="space-y-3 sm:space-y-4">
            <GuideStep
              step={1}
              title={t('ai_settings.guide_step1_title')}
              description={t('ai_settings.guide_step1_desc')}
            />
            <GuideStep
              step={2}
              title={t('ai_settings.guide_step2_title')}
              description={t('ai_settings.guide_step2_desc')}
            />
            <GuideStep
              step={3}
              title={t('ai_settings.guide_step3_title')}
              description={t('ai_settings.guide_step3_desc')}
            />
            <GuideStep
              step={4}
              title={t('ai_settings.guide_step4_title')}
              description={t('ai_settings.guide_step4_desc')}
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
    <div className={cn("p-2.5 sm:p-4 rounded-lg sm:rounded-xl border", c.bg, c.border)}>
      <div className="flex items-start gap-2 sm:gap-3">
        <div className={cn("p-1.5 sm:p-2 rounded-md sm:rounded-lg", c.icon)}>
          <Icon className="w-4 h-4 sm:w-5 sm:h-5" />
        </div>
        <div>
          <h3 className="text-sm sm:text-base font-semibold text-slate-800">{title}</h3>
          <p className="text-[10px] sm:text-sm text-muted-foreground mt-0.5 sm:mt-1">{description}</p>
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
