'use client'

// =============================================
// GEO 結構化數據頁面
// =============================================

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Code,
  Sparkles,
  CheckCircle,
  AlertCircle,
  Copy,
  Check,
  History,
  RefreshCw,
  FileJson,
  HelpCircle,
  Globe,
  Layers,
  BookOpen,
  Zap,
  ChevronDown,
  ChevronUp,
  ArrowRight,
  AlertTriangle,
  Lightbulb,
  Bot,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'
import {
  PageTransition,
  HoloCard,
  HoloPanelHeader,
  HoloButton,
  HoloBadge,
  HoloSkeleton,
} from '@/components/ui/future-tech'
import {
  geoApi,
  StructuredDataResponse,
  AISummaryResponse,
  SchemaValidationResponse,
  ProductInfo,
} from '@/lib/api'

// =============================================
// Schema 類型選項
// =============================================

const SCHEMA_TYPES = [
  { value: 'Product', label: 'Product Schema', icon: Layers, description: '商品結構化數據' },
  { value: 'FAQPage', label: 'FAQ Schema', icon: HelpCircle, description: '常見問題結構化數據' },
  { value: 'BreadcrumbList', label: 'Breadcrumb Schema', icon: ArrowRight, description: '麵包屑導航數據' },
] as const

// =============================================
// 手機版子 Tab 類型
// =============================================

type MobileSubTab = 'input' | 'result' | 'validate'

// =============================================
// 主組件
// =============================================

export default function GEOPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'generate' | 'validate' | 'knowledge'>('generate')
  const [mobileSubTab, setMobileSubTab] = useState<MobileSubTab>('input')
  const [selectedSchemaType, setSelectedSchemaType] = useState<string>('Product')
  const [formData, setFormData] = useState<{
    productInfo: ProductInfo
    includeReviews: boolean
    includeOffers: boolean
  }>({
    productInfo: {
      name: '',
      brand: '',
      features: [],
      target_audience: '',
      category: '',
      price: '',
    },
    includeReviews: true,
    includeOffers: true,
  })
  const [featuresInput, setFeaturesInput] = useState('')
  const [faqsInput, setFaqsInput] = useState('')
  const [generatedSchema, setGeneratedSchema] = useState<StructuredDataResponse | null>(null)
  const [aiSummary, setAiSummary] = useState<AISummaryResponse | null>(null)
  const [validationResult, setValidationResult] = useState<SchemaValidationResponse | null>(null)
  const [customJsonLd, setCustomJsonLd] = useState('')
  const [copiedField, setCopiedField] = useState<string | null>(null)
  const [showJsonPreview, setShowJsonPreview] = useState(true)

  // 生成 Schema
  const generateSchemaMutation = useMutation({
    mutationFn: async () => {
      const features = featuresInput
        .split('\n')
        .map((f) => f.trim())
        .filter(Boolean)

      const productInfo = {
        ...formData.productInfo,
        features,
      }

      if (selectedSchemaType === 'Product') {
        return geoApi.generateProductSchema({
          product_info: productInfo,
          include_reviews: formData.includeReviews,
          include_offers: formData.includeOffers,
        })
      } else if (selectedSchemaType === 'FAQPage') {
        const faqs = faqsInput
          .split('\n\n')
          .map((block) => {
            const lines = block.split('\n')
            if (lines.length >= 2) {
              return {
                question: lines[0].replace(/^Q[:：]\s*/, ''),
                answer: lines.slice(1).join('\n').replace(/^A[:：]\s*/, ''),
              }
            }
            return null
          })
          .filter((faq): faq is { question: string; answer: string } => faq !== null)

        return geoApi.generateFAQSchema({
          product_info: productInfo,
          faqs: faqs.length > 0 ? faqs : undefined,
        })
      } else {
        return geoApi.generateBreadcrumbSchema({
          product_info: productInfo,
        })
      }
    },
    onSuccess: (response) => {
      setGeneratedSchema(response)
      setMobileSubTab('result')
    },
  })

  // 生成 AI 摘要
  const generateAISummaryMutation = useMutation({
    mutationFn: () => {
      const features = featuresInput
        .split('\n')
        .map((f) => f.trim())
        .filter(Boolean)

      return geoApi.generateAISummary({
        product_info: {
          ...formData.productInfo,
          features,
        },
        max_facts: 5,
      })
    },
    onSuccess: (response) => {
      setAiSummary(response)
    },
  })

  // 驗證 Schema
  const validateSchemaMutation = useMutation({
    mutationFn: () => {
      const jsonLd = customJsonLd ? JSON.parse(customJsonLd) : generatedSchema?.json_ld
      return geoApi.validateSchema(jsonLd)
    },
    onSuccess: (response) => {
      setValidationResult(response)
      setMobileSubTab('validate')
    },
  })

  const handleGenerate = () => {
    generateSchemaMutation.mutate()
  }

  const handleGenerateAISummary = () => {
    generateAISummaryMutation.mutate()
  }

  const handleValidate = () => {
    validateSchemaMutation.mutate()
  }

  const handleCopy = async (text: string, field: string) => {
    await navigator.clipboard.writeText(text)
    setCopiedField(field)
    setTimeout(() => setCopiedField(null), 2000)
  }

  const copySchemaAsScript = () => {
    if (generatedSchema) {
      const script = `<script type="application/ld+json">\n${JSON.stringify(generatedSchema.json_ld, null, 2)}\n</script>`
      handleCopy(script, 'script')
    }
  }

  return (
    <PageTransition className="space-y-8">
      {/* 頁面標題 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
            GEO 結構化數據
            <HoloBadge variant="info" size="sm">
              Beta
            </HoloBadge>
          </h1>
          <p className="text-muted-foreground mt-2 text-lg">
            生成 Schema.org 結構化數據，提升 AI 搜索引擎的理解與引用
          </p>
        </div>
      </div>

      {/* 標籤切換 */}
      <div className="flex space-x-4 border-b border-white/20 pb-1">
        <button
          onClick={() => setActiveTab('generate')}
          className={cn(
            "flex items-center px-4 py-2 text-sm font-medium transition-colors rounded-t-lg",
            activeTab === 'generate'
              ? "text-cyan-600 bg-white/50 border-b-2 border-cyan-600"
              : "text-muted-foreground hover:text-foreground hover:bg-white/30"
          )}
        >
          <Code className="w-4 h-4 mr-2" />
          Schema 生成
        </button>
        <button
          onClick={() => setActiveTab('validate')}
          className={cn(
            "flex items-center px-4 py-2 text-sm font-medium transition-colors rounded-t-lg",
            activeTab === 'validate'
              ? "text-cyan-600 bg-white/50 border-b-2 border-cyan-600"
              : "text-muted-foreground hover:text-foreground hover:bg-white/30"
          )}
        >
          <CheckCircle className="w-4 h-4 mr-2" />
          驗證工具
        </button>
        <button
          onClick={() => setActiveTab('knowledge')}
          className={cn(
            "flex items-center px-4 py-2 text-sm font-medium transition-colors rounded-t-lg",
            activeTab === 'knowledge'
              ? "text-cyan-600 bg-white/50 border-b-2 border-cyan-600"
              : "text-muted-foreground hover:text-foreground hover:bg-white/30"
          )}
        >
          <BookOpen className="w-4 h-4 mr-2" />
          品牌知識
        </button>
      </div>

      {/* Schema 生成標籤內容 */}
      {activeTab === 'generate' && (
        <>
          {/* 手機版子 Tab 切換 */}
          <div className="lg:hidden flex rounded-xl bg-white/50 p-1 border border-white/40 mb-4">
            <button
              onClick={() => setMobileSubTab('input')}
              className={cn(
                "flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg text-sm font-medium transition-all",
                mobileSubTab === 'input'
                  ? "bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-md"
                  : "text-gray-600 hover:bg-white/50"
              )}
            >
              <FileJson className="w-4 h-4" />
              輸入
            </button>
            <button
              onClick={() => setMobileSubTab('result')}
              className={cn(
                "flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg text-sm font-medium transition-all relative",
                mobileSubTab === 'result'
                  ? "bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-md"
                  : "text-gray-600 hover:bg-white/50"
              )}
            >
              <Code className="w-4 h-4" />
              結果
              {generatedSchema && mobileSubTab !== 'result' && (
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-emerald-500 rounded-full" />
              )}
            </button>
            <button
              onClick={() => setMobileSubTab('validate')}
              className={cn(
                "flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg text-sm font-medium transition-all",
                mobileSubTab === 'validate'
                  ? "bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-md"
                  : "text-gray-600 hover:bg-white/50"
              )}
            >
              <CheckCircle className="w-4 h-4" />
              驗證
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 左側：輸入表單 */}
            <HoloCard
              glowColor="cyan"
              className={cn(
                "lg:max-h-[calc(100vh-200px)] lg:overflow-y-auto",
                mobileSubTab !== 'input' && "hidden lg:block"
              )}
            >
              <div className="p-6 space-y-6">
                <HoloPanelHeader
                  title="輸入商品資訊"
                  icon={<FileJson className="w-5 h-5" />}
                />

                <div className="space-y-4">
                  {/* Schema 類型選擇 */}
                  <div className="grid gap-2">
                    <Label>Schema 類型</Label>
                    <div className="grid grid-cols-1 gap-2">
                      {SCHEMA_TYPES.map((type) => {
                        const Icon = type.icon
                        const isSelected = selectedSchemaType === type.value
                        return (
                          <button
                            key={type.value}
                            type="button"
                            onClick={() => setSelectedSchemaType(type.value)}
                            className={cn(
                              "flex items-center gap-3 p-3 rounded-lg border transition-all text-left",
                              isSelected
                                ? "bg-cyan-50 border-cyan-300 text-cyan-700"
                                : "bg-white/50 border-slate-200 hover:border-cyan-200 hover:bg-cyan-50/50"
                            )}
                          >
                            <Icon className={cn("w-5 h-5", isSelected ? "text-cyan-600" : "text-slate-400")} />
                            <div>
                              <p className="font-medium text-sm">{type.label}</p>
                              <p className="text-xs text-slate-500">{type.description}</p>
                            </div>
                            {isSelected && <Check className="w-4 h-4 ml-auto text-cyan-600" />}
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  <div className="grid gap-2">
                    <Label htmlFor="name">商品名稱 <span className="text-red-500">*</span></Label>
                    <Input
                      id="name"
                      value={formData.productInfo.name}
                      onChange={(e) => setFormData({ ...formData, productInfo: { ...formData.productInfo, name: e.target.value } })}
                      placeholder="例如：天然維他命C 1000mg"
                      className="bg-white/50"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label htmlFor="brand">品牌</Label>
                      <Input
                        id="brand"
                        value={formData.productInfo.brand}
                        onChange={(e) => setFormData({ ...formData, productInfo: { ...formData.productInfo, brand: e.target.value } })}
                        placeholder="例如：YourBrand"
                        className="bg-white/50"
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="price">價格</Label>
                      <Input
                        id="price"
                        value={formData.productInfo.price}
                        onChange={(e) => setFormData({ ...formData, productInfo: { ...formData.productInfo, price: e.target.value } })}
                        placeholder="例如：HKD 199"
                        className="bg-white/50"
                      />
                    </div>
                  </div>

                  <div className="grid gap-2">
                    <Label htmlFor="features">商品特點（每行一個）</Label>
                    <Textarea
                      id="features"
                      value={featuresInput}
                      onChange={(e) => setFeaturesInput(e.target.value)}
                      rows={3}
                      placeholder="1000mg 高劑量&#10;美國進口&#10;60粒裝"
                      className="bg-white/50"
                    />
                  </div>

                  {/* FAQ 輸入（僅 FAQ Schema） */}
                  {selectedSchemaType === 'FAQPage' && (
                    <div className="grid gap-2">
                      <Label htmlFor="faqs">FAQ 列表（留空使用 AI 自動生成）</Label>
                      <Textarea
                        id="faqs"
                        value={faqsInput}
                        onChange={(e) => setFaqsInput(e.target.value)}
                        rows={5}
                        placeholder="Q: 這個產品適合什麼人群？&#10;A: 適合注重健康的成年人。&#10;&#10;Q: 每天需要服用多少？&#10;A: 建議每天服用一粒。"
                        className="bg-white/50 font-mono text-sm"
                      />
                      <p className="text-xs text-slate-500">格式：每個 Q&A 用空行分隔</p>
                    </div>
                  )}

                  {/* Product Schema 選項 */}
                  {selectedSchemaType === 'Product' && (
                    <div className="flex flex-wrap gap-3">
                      <label className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={formData.includeReviews}
                          onChange={(e) => setFormData({ ...formData, includeReviews: e.target.checked })}
                          className="rounded border-slate-300"
                        />
                        包含評論數據
                      </label>
                      <label className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={formData.includeOffers}
                          onChange={(e) => setFormData({ ...formData, includeOffers: e.target.checked })}
                          className="rounded border-slate-300"
                        />
                        包含價格優惠
                      </label>
                    </div>
                  )}
                </div>

                <div className="space-y-2">
                  <HoloButton
                    onClick={handleGenerate}
                    disabled={!formData.productInfo.name}
                    loading={generateSchemaMutation.isPending}
                    icon={generateSchemaMutation.isPending ? undefined : <Code className="w-5 h-5" />}
                    size="lg"
                    className="w-full"
                  >
                    {generateSchemaMutation.isPending ? 'AI 生成中...' : '生成 Schema'}
                  </HoloButton>

                  <HoloButton
                    onClick={handleGenerateAISummary}
                    disabled={!formData.productInfo.name}
                    loading={generateAISummaryMutation.isPending}
                    variant="secondary"
                    size="sm"
                    className="w-full"
                  >
                    <Bot className="w-4 h-4 mr-2" />
                    生成 AI 搜索摘要
                  </HoloButton>
                </div>
              </div>
            </HoloCard>

            {/* 中間：生成結果 */}
            <HoloCard
              glowColor="purple"
              className={cn(
                "lg:max-h-[calc(100vh-200px)] lg:overflow-y-auto",
                mobileSubTab !== 'result' && "hidden lg:block"
              )}
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">生成結果</h2>
                  {generatedSchema && (
                    <div className="flex items-center gap-2">
                      {generatedSchema.is_valid ? (
                        <HoloBadge variant="success">
                          <Check className="w-3 h-3 mr-1" /> 有效
                        </HoloBadge>
                      ) : (
                        <HoloBadge variant="warning">
                          <AlertTriangle className="w-3 h-3 mr-1" /> 有問題
                        </HoloBadge>
                      )}
                    </div>
                  )}
                </div>

                {generateSchemaMutation.isError && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 text-red-700 flex items-center">
                    <AlertCircle className="w-5 h-5 mr-2" />
                    生成失敗，請稍後再試
                  </div>
                )}

                {!generatedSchema && !generateSchemaMutation.isPending && (
                  <div className="flex flex-col items-center justify-center h-[300px] text-gray-400">
                    <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                      <Code className="w-8 h-8 text-slate-300" />
                    </div>
                    <p className="text-sm text-center">在左側填寫資訊後<br />AI 將生成 Schema.org JSON-LD</p>
                  </div>
                )}

                {generateSchemaMutation.isPending && (
                  <div className="flex flex-col items-center justify-center h-[300px]">
                    <div className="relative w-20 h-20 mb-4">
                      <div className="absolute inset-0 bg-purple-200 rounded-full animate-ping opacity-20" />
                      <div className="relative w-20 h-20 bg-gradient-to-br from-purple-100 to-blue-100 rounded-full flex items-center justify-center">
                        <Code className="w-10 h-10 text-purple-500 animate-pulse" />
                      </div>
                    </div>
                    <h3 className="text-base font-medium text-gray-900">AI 正在生成...</h3>
                    <p className="text-gray-500 mt-1 text-sm">正在構建結構化數據</p>
                  </div>
                )}

                {generatedSchema && !generateSchemaMutation.isPending && (
                  <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {/* Schema 類型 */}
                    <div className="flex items-center gap-2">
                      <HoloBadge variant="info">
                        <FileJson className="w-3 h-3 mr-1" />
                        {generatedSchema.schema_type}
                      </HoloBadge>
                    </div>

                    {/* AI 摘要（如果有） */}
                    {generatedSchema.ai_summary && (
                      <div className="border border-blue-200 rounded-lg overflow-hidden bg-blue-50/50">
                        <div className="px-4 py-2 bg-blue-100/50 border-b border-blue-200">
                          <span className="text-xs font-bold uppercase tracking-wider text-blue-700">AI 搜索引擎摘要</span>
                        </div>
                        <div className="p-4 text-sm text-blue-800">
                          {generatedSchema.ai_summary}
                        </div>
                      </div>
                    )}

                    {/* AI 事實（如果有） */}
                    {generatedSchema.ai_facts && generatedSchema.ai_facts.length > 0 && (
                      <div className="border border-emerald-200 rounded-lg overflow-hidden bg-emerald-50/50">
                        <div className="px-4 py-2 bg-emerald-100/50 border-b border-emerald-200">
                          <span className="text-xs font-bold uppercase tracking-wider text-emerald-700">關鍵事實</span>
                        </div>
                        <div className="p-4">
                          <ul className="space-y-2">
                            {generatedSchema.ai_facts.map((fact, index) => (
                              <li key={index} className="flex items-start text-sm text-emerald-800">
                                <Lightbulb className="w-4 h-4 mr-2 mt-0.5 text-emerald-500 flex-shrink-0" />
                                {fact}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )}

                    {/* JSON-LD 預覽 */}
                    <div className="border border-slate-200 rounded-lg overflow-hidden bg-white/50">
                      <div className="flex items-center justify-between px-4 py-2 bg-slate-50/50 border-b border-slate-100">
                        <button
                          onClick={() => setShowJsonPreview(!showJsonPreview)}
                          className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-500 hover:text-slate-700"
                        >
                          JSON-LD
                          {showJsonPreview ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleCopy(JSON.stringify(generatedSchema.json_ld, null, 2), 'json')}
                            className="h-6 px-2 text-slate-400 hover:text-cyan-600"
                          >
                            {copiedField === 'json' ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={copySchemaAsScript}
                            className="h-6 px-2 text-slate-400 hover:text-cyan-600"
                          >
                            {copiedField === 'script' ? (
                              <><Check className="w-3 h-3 mr-1" /> 已複製</>
                            ) : (
                              <><Code className="w-3 h-3 mr-1" /> 複製 Script</>
                            )}
                          </Button>
                        </div>
                      </div>
                      <AnimatePresence>
                        {showJsonPreview && (
                          <motion.div
                            initial={{ height: 0, opacity: 0 }}
                            animate={{ height: 'auto', opacity: 1 }}
                            exit={{ height: 0, opacity: 0 }}
                            className="overflow-hidden"
                          >
                            <pre className="p-4 text-xs font-mono text-slate-700 overflow-x-auto max-h-[300px] overflow-y-auto">
                              {JSON.stringify(generatedSchema.json_ld, null, 2)}
                            </pre>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>

                    {/* 驗證按鈕 */}
                    <HoloButton
                      onClick={handleValidate}
                      variant="secondary"
                      size="sm"
                      className="w-full"
                      loading={validateSchemaMutation.isPending}
                    >
                      <CheckCircle className="w-4 h-4 mr-2" />
                      驗證 Schema
                    </HoloButton>
                  </div>
                )}
              </div>
            </HoloCard>

            {/* 右側：AI 摘要與驗證 */}
            <HoloCard
              glowColor="blue"
              className={cn(
                "lg:max-h-[calc(100vh-200px)] lg:overflow-y-auto",
                mobileSubTab !== 'validate' && "hidden lg:block"
              )}
            >
              <div className="p-6 space-y-6">
                {/* AI 摘要區塊 */}
                <div>
                  <HoloPanelHeader
                    title="AI 搜索引擎優化"
                    icon={<Bot className="w-5 h-5" />}
                  />

                  {!aiSummary && !generateAISummaryMutation.isPending && (
                    <div className="flex flex-col items-center justify-center h-[150px] text-gray-400">
                      <p className="text-sm text-center">生成適合 AI 搜索引擎<br />（ChatGPT、Perplexity）引用的摘要</p>
                    </div>
                  )}

                  {generateAISummaryMutation.isPending && (
                    <div className="flex flex-col items-center justify-center h-[150px]">
                      <RefreshCw className="w-8 h-8 text-blue-400 animate-spin mb-2" />
                      <p className="text-sm text-gray-500">正在生成摘要...</p>
                    </div>
                  )}

                  {aiSummary && (
                    <div className="space-y-3 mt-4">
                      <div className="border border-blue-200 rounded-lg p-4 bg-blue-50/50">
                        <p className="text-sm text-blue-800">{aiSummary.summary}</p>
                      </div>
                      {aiSummary.facts.length > 0 && (
                        <div className="space-y-2">
                          <p className="text-xs font-medium text-slate-500">關鍵事實：</p>
                          {aiSummary.facts.map((fact, index) => (
                            <div key={index} className="flex items-start text-sm text-slate-700">
                              <Lightbulb className="w-4 h-4 mr-2 mt-0.5 text-amber-500 flex-shrink-0" />
                              {fact}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* 驗證結果 */}
                <div>
                  <HoloPanelHeader
                    title="驗證結果"
                    icon={<CheckCircle className="w-5 h-5" />}
                  />

                  {!validationResult && !validateSchemaMutation.isPending && (
                    <div className="flex flex-col items-center justify-center h-[150px] text-gray-400">
                      <p className="text-sm text-center">生成 Schema 後<br />可在此驗證數據有效性</p>
                    </div>
                  )}

                  {validateSchemaMutation.isPending && (
                    <div className="flex flex-col items-center justify-center h-[150px]">
                      <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin mb-2" />
                      <p className="text-sm text-gray-500">正在驗證...</p>
                    </div>
                  )}

                  {validationResult && (
                    <div className="space-y-3 mt-4">
                      {/* 驗證狀態 */}
                      <div className={cn(
                        "p-4 rounded-lg border",
                        validationResult.is_valid
                          ? "bg-emerald-50 border-emerald-200"
                          : "bg-red-50 border-red-200"
                      )}>
                        <div className="flex items-center gap-2">
                          {validationResult.is_valid ? (
                            <>
                              <CheckCircle className="w-5 h-5 text-emerald-600" />
                              <span className="font-medium text-emerald-700">Schema 驗證通過</span>
                            </>
                          ) : (
                            <>
                              <AlertCircle className="w-5 h-5 text-red-600" />
                              <span className="font-medium text-red-700">Schema 有問題</span>
                            </>
                          )}
                        </div>
                      </div>

                      {/* 錯誤列表 */}
                      {validationResult.errors.length > 0 && (
                        <div className="border border-red-200 rounded-lg overflow-hidden bg-red-50/50">
                          <div className="px-4 py-2 bg-red-100/50 border-b border-red-200">
                            <span className="text-xs font-bold uppercase tracking-wider text-red-700">錯誤</span>
                          </div>
                          <div className="p-3 space-y-2">
                            {validationResult.errors.map((error, index) => (
                              <div key={index} className="flex items-start text-sm text-red-700">
                                <AlertCircle className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                                {error}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* 警告列表 */}
                      {validationResult.warnings.length > 0 && (
                        <div className="border border-amber-200 rounded-lg overflow-hidden bg-amber-50/50">
                          <div className="px-4 py-2 bg-amber-100/50 border-b border-amber-200">
                            <span className="text-xs font-bold uppercase tracking-wider text-amber-700">警告</span>
                          </div>
                          <div className="p-3 space-y-2">
                            {validationResult.warnings.map((warning, index) => (
                              <div key={index} className="flex items-start text-sm text-amber-700">
                                <AlertTriangle className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                                {warning}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* 建議列表 */}
                      {validationResult.suggestions.length > 0 && (
                        <div className="border border-blue-200 rounded-lg overflow-hidden bg-blue-50/50">
                          <div className="px-4 py-2 bg-blue-100/50 border-b border-blue-200">
                            <span className="text-xs font-bold uppercase tracking-wider text-blue-700">建議</span>
                          </div>
                          <div className="p-3 space-y-2">
                            {validationResult.suggestions.map((suggestion, index) => (
                              <div key={index} className="flex items-start text-sm text-blue-700">
                                <Lightbulb className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                                {suggestion}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </HoloCard>
          </div>
        </>
      )}

      {/* 驗證工具標籤內容 */}
      {activeTab === 'validate' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <HoloCard glowColor="cyan">
            <div className="p-6">
              <HoloPanelHeader
                title="輸入 JSON-LD"
                icon={<FileJson className="w-5 h-5" />}
              />
              <Textarea
                value={customJsonLd}
                onChange={(e) => setCustomJsonLd(e.target.value)}
                rows={15}
                placeholder='{\n  "@context": "https://schema.org",\n  "@type": "Product",\n  "name": "...",\n  ...\n}'
                className="mt-4 bg-white/50 font-mono text-sm"
              />
              <HoloButton
                onClick={handleValidate}
                disabled={!customJsonLd}
                loading={validateSchemaMutation.isPending}
                className="w-full mt-4"
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                驗證 Schema
              </HoloButton>
            </div>
          </HoloCard>

          <HoloCard glowColor="purple">
            <div className="p-6">
              <HoloPanelHeader
                title="驗證結果"
                icon={<CheckCircle className="w-5 h-5" />}
              />

              {!validationResult && (
                <div className="flex flex-col items-center justify-center h-[300px] text-gray-400">
                  <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                    <CheckCircle className="w-8 h-8 text-slate-300" />
                  </div>
                  <p className="text-sm text-center">輸入 JSON-LD 後點擊驗證</p>
                </div>
              )}

              {validationResult && (
                <div className="space-y-4 mt-4">
                  <div className={cn(
                    "p-4 rounded-lg border",
                    validationResult.is_valid
                      ? "bg-emerald-50 border-emerald-200"
                      : "bg-red-50 border-red-200"
                  )}>
                    <div className="flex items-center gap-2">
                      {validationResult.is_valid ? (
                        <>
                          <CheckCircle className="w-5 h-5 text-emerald-600" />
                          <span className="font-medium text-emerald-700">Schema 驗證通過</span>
                        </>
                      ) : (
                        <>
                          <AlertCircle className="w-5 h-5 text-red-600" />
                          <span className="font-medium text-red-700">Schema 有問題</span>
                        </>
                      )}
                    </div>
                  </div>

                  {validationResult.errors.map((error, index) => (
                    <div key={index} className="flex items-start text-sm text-red-700 bg-red-50 p-3 rounded-lg">
                      <AlertCircle className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                      {error}
                    </div>
                  ))}

                  {validationResult.warnings.map((warning, index) => (
                    <div key={index} className="flex items-start text-sm text-amber-700 bg-amber-50 p-3 rounded-lg">
                      <AlertTriangle className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                      {warning}
                    </div>
                  ))}

                  {validationResult.suggestions.map((suggestion, index) => (
                    <div key={index} className="flex items-start text-sm text-blue-700 bg-blue-50 p-3 rounded-lg">
                      <Lightbulb className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0" />
                      {suggestion}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </HoloCard>
        </div>
      )}

      {/* 品牌知識標籤內容 */}
      {activeTab === 'knowledge' && (
        <HoloCard glowColor="cyan" className="p-8">
          <div className="flex flex-col items-center justify-center h-[400px] text-gray-400">
            <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-4">
              <BookOpen className="w-10 h-10 text-slate-300" />
            </div>
            <h3 className="text-lg font-medium text-gray-900">品牌知識圖譜</h3>
            <p className="text-gray-500 mt-2 text-center max-w-md">
              創建和管理品牌知識庫，提升 AI 搜索引擎對品牌的理解。<br />
              支持專家內容生成、知識關聯和自動引用。
            </p>
            <HoloButton
              variant="secondary"
              className="mt-6"
              disabled
            >
              即將推出
            </HoloButton>
          </div>
        </HoloCard>
      )}
    </PageTransition>
  )
}
