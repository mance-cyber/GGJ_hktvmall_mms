'use client'

// =============================================
// SEO 優化頁面
// =============================================

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search,
  Sparkles,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Copy,
  Check,
  History,
  RefreshCw,
  Target,
  FileText,
  Globe,
  Layers,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  Zap,
  BarChart3,
  Tags,
  Languages,
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
import { seoApi, SEOContentResponse, SEOScoreResponse, KeywordExtractionResponse, ProductInfo } from '@/lib/api'

// =============================================
// 語言選項
// =============================================

const LANGUAGES = [
  { value: 'zh-HK', label: '繁體中文', flag: '🇭🇰' },
  { value: 'zh-CN', label: '簡體中文', flag: '🇨🇳' },
  { value: 'en', label: 'English', flag: '🇬🇧' },
] as const

type LanguageCode = 'zh-HK' | 'zh-CN' | 'en'

// =============================================
// 手機版子 Tab 類型
// =============================================

type MobileSubTab = 'input' | 'result' | 'keywords'

// =============================================
// 主組件
// =============================================

export default function SEOPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'generate' | 'batch' | 'history'>('generate')
  const [mobileSubTab, setMobileSubTab] = useState<MobileSubTab>('input')
  const [formData, setFormData] = useState<{
    productInfo: ProductInfo
    targetKeywords: string[]
  }>({
    productInfo: {
      name: '',
      brand: '',
      features: [],
      target_audience: '',
      category: '',
    },
    targetKeywords: [],
  })
  const [featuresInput, setFeaturesInput] = useState('')
  const [keywordsInput, setKeywordsInput] = useState('')
  const [generatedSEO, setGeneratedSEO] = useState<SEOContentResponse | null>(null)
  const [extractedKeywords, setExtractedKeywords] = useState<KeywordExtractionResponse | null>(null)
  const [copiedField, setCopiedField] = useState<string | null>(null)
  const [selectedLanguages, setSelectedLanguages] = useState<LanguageCode[]>(['zh-HK'])
  const [showScoreDetails, setShowScoreDetails] = useState(false)

  // 生成 SEO 內容
  const generateMutation = useMutation({
    mutationFn: () => {
      const features = featuresInput
        .split('\n')
        .map((f) => f.trim())
        .filter(Boolean)
      const keywords = keywordsInput
        .split('\n')
        .map((k) => k.trim())
        .filter(Boolean)

      return seoApi.generateSEO({
        product_info: {
          ...formData.productInfo,
          features,
        },
        target_keywords: keywords.length > 0 ? keywords : undefined,
        target_languages: selectedLanguages,
        include_og: true,
      })
    },
    onSuccess: (response) => {
      setGeneratedSEO(response)
      setMobileSubTab('result')
    },
  })

  // 提取關鍵詞
  const extractKeywordsMutation = useMutation({
    mutationFn: () => {
      const features = featuresInput
        .split('\n')
        .map((f) => f.trim())
        .filter(Boolean)

      return seoApi.extractKeywords({
        product_info: {
          ...formData.productInfo,
          features,
        },
        max_keywords: 20,
        include_long_tail: true,
      })
    },
    onSuccess: (response) => {
      setExtractedKeywords(response)
      setMobileSubTab('keywords')
    },
  })

  const handleGenerate = () => {
    generateMutation.mutate()
  }

  const handleExtractKeywords = () => {
    extractKeywordsMutation.mutate()
  }

  const handleCopy = async (text: string, field: string) => {
    await navigator.clipboard.writeText(text)
    setCopiedField(field)
    setTimeout(() => setCopiedField(null), 2000)
  }

  const applyExtractedKeywords = () => {
    if (extractedKeywords) {
      const allKeywords = [
        extractedKeywords.primary_keyword,
        ...extractedKeywords.secondary_keywords,
      ].filter(Boolean)
      setKeywordsInput(allKeywords.join('\n'))
    }
  }

  // SEO 評分顏色
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-600'
    if (score >= 60) return 'text-amber-600'
    return 'text-red-600'
  }

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-emerald-100 border-emerald-200'
    if (score >= 60) return 'bg-amber-100 border-amber-200'
    return 'bg-red-100 border-red-200'
  }

  return (
    <PageTransition className="space-y-8">
      {/* 頁面標題 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
            SEO 優化
            <HoloBadge variant="info" size="sm">
              Beta
            </HoloBadge>
          </h1>
          <p className="text-muted-foreground mt-2 text-lg">
            AI 驅動的 SEO 內容生成，提升商品在搜索引擎中的曝光度
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
          <Search className="w-4 h-4 mr-2" />
          SEO 生成
        </button>
        <button
          onClick={() => setActiveTab('batch')}
          className={cn(
            "flex items-center px-4 py-2 text-sm font-medium transition-colors rounded-t-lg",
            activeTab === 'batch'
              ? "text-cyan-600 bg-white/50 border-b-2 border-cyan-600"
              : "text-muted-foreground hover:text-foreground hover:bg-white/30"
          )}
        >
          <Layers className="w-4 h-4 mr-2" />
          批量生成
        </button>
        <button
          onClick={() => setActiveTab('history')}
          className={cn(
            "flex items-center px-4 py-2 text-sm font-medium transition-colors rounded-t-lg",
            activeTab === 'history'
              ? "text-cyan-600 bg-white/50 border-b-2 border-cyan-600"
              : "text-muted-foreground hover:text-foreground hover:bg-white/30"
          )}
        >
          <History className="w-4 h-4 mr-2" />
          歷史記錄
        </button>
      </div>

      {/* SEO 生成標籤內容 */}
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
              <FileText className="w-4 h-4" />
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
              <BarChart3 className="w-4 h-4" />
              結果
              {generatedSEO && mobileSubTab !== 'result' && (
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-emerald-500 rounded-full" />
              )}
            </button>
            <button
              onClick={() => setMobileSubTab('keywords')}
              className={cn(
                "flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg text-sm font-medium transition-all",
                mobileSubTab === 'keywords'
                  ? "bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-md"
                  : "text-gray-600 hover:bg-white/50"
              )}
            >
              <Tags className="w-4 h-4" />
              關鍵詞
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
                  icon={<FileText className="w-5 h-5" />}
                />

                <div className="space-y-4">
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
                      <Label htmlFor="category">類別</Label>
                      <Input
                        id="category"
                        value={formData.productInfo.category}
                        onChange={(e) => setFormData({ ...formData, productInfo: { ...formData.productInfo, category: e.target.value } })}
                        placeholder="例如：保健食品"
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

                  <div className="grid gap-2">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="keywords">目標關鍵詞（每行一個）</Label>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleExtractKeywords}
                        disabled={!formData.productInfo.name || extractKeywordsMutation.isPending}
                        className="text-xs text-cyan-600 hover:text-cyan-700"
                      >
                        {extractKeywordsMutation.isPending ? (
                          <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
                        ) : (
                          <Zap className="w-3 h-3 mr-1" />
                        )}
                        AI 提取
                      </Button>
                    </div>
                    <Textarea
                      id="keywords"
                      value={keywordsInput}
                      onChange={(e) => setKeywordsInput(e.target.value)}
                      rows={3}
                      placeholder="維他命C&#10;保健食品&#10;增強免疫力"
                      className="bg-white/50"
                    />
                  </div>

                  {/* 語言選擇 */}
                  <div className="grid gap-2">
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
                                setSelectedLanguages(selectedLanguages.filter(l => l !== lang.value))
                              } else if (!isSelected) {
                                setSelectedLanguages([...selectedLanguages, lang.value])
                              }
                            }}
                            className={cn(
                              "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all",
                              isSelected
                                ? "bg-cyan-100 text-cyan-700 border-2 border-cyan-300"
                                : "bg-white/50 text-slate-600 border border-slate-200 hover:border-cyan-200 hover:bg-cyan-50"
                            )}
                          >
                            <span>{lang.flag}</span>
                            <span>{lang.label}</span>
                            {isSelected && <Check className="w-3 h-3 ml-1" />}
                          </button>
                        )
                      })}
                    </div>
                  </div>
                </div>

                <HoloButton
                  onClick={handleGenerate}
                  disabled={!formData.productInfo.name}
                  loading={generateMutation.isPending}
                  icon={generateMutation.isPending ? undefined : <Sparkles className="w-5 h-5" />}
                  size="lg"
                  className="w-full"
                >
                  {generateMutation.isPending ? 'AI 優化中...' : '生成 SEO 內容'}
                </HoloButton>
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
                  <h2 className="text-lg font-semibold text-gray-900">SEO 結果</h2>
                  {generatedSEO && (
                    <HoloBadge variant="success">
                      <Check className="w-3 h-3 mr-1" /> 生成成功
                    </HoloBadge>
                  )}
                </div>

                {generateMutation.isError && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 text-red-700 flex items-center">
                    <AlertCircle className="w-5 h-5 mr-2" />
                    生成失敗，請稍後再試
                  </div>
                )}

                {!generatedSEO && !generateMutation.isPending && (
                  <div className="flex flex-col items-center justify-center h-[300px] text-gray-400">
                    <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                      <Search className="w-8 h-8 text-slate-300" />
                    </div>
                    <p className="text-sm text-center">在左側填寫資訊後<br />AI 將為您生成 SEO 優化內容</p>
                  </div>
                )}

                {generateMutation.isPending && (
                  <div className="flex flex-col items-center justify-center h-[300px]">
                    <div className="relative w-20 h-20 mb-4">
                      <div className="absolute inset-0 bg-cyan-200 rounded-full animate-ping opacity-20" />
                      <div className="relative w-20 h-20 bg-gradient-to-br from-cyan-100 to-blue-100 rounded-full flex items-center justify-center">
                        <Search className="w-10 h-10 text-cyan-500 animate-pulse" />
                      </div>
                    </div>
                    <h3 className="text-base font-medium text-gray-900">AI 正在優化中...</h3>
                    <p className="text-gray-500 mt-1 text-sm">正在分析關鍵詞與搜索趨勢</p>
                  </div>
                )}

                {generatedSEO && !generateMutation.isPending && (
                  <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {/* SEO 評分 */}
                    {generatedSEO.content.seo_score !== undefined && (
                      <div
                        className={cn(
                          "p-4 rounded-xl border cursor-pointer transition-all",
                          getScoreBg(generatedSEO.content.seo_score)
                        )}
                        onClick={() => setShowScoreDetails(!showScoreDetails)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className={cn(
                              "text-3xl font-bold",
                              getScoreColor(generatedSEO.content.seo_score)
                            )}>
                              {generatedSEO.content.seo_score}
                            </div>
                            <div>
                              <p className="font-medium text-gray-900">SEO 評分</p>
                              <p className="text-xs text-gray-500">
                                {generatedSEO.content.seo_score >= 80 ? '優秀' :
                                 generatedSEO.content.seo_score >= 60 ? '良好' : '需改進'}
                              </p>
                            </div>
                          </div>
                          {showScoreDetails ? (
                            <ChevronUp className="w-5 h-5 text-gray-400" />
                          ) : (
                            <ChevronDown className="w-5 h-5 text-gray-400" />
                          )}
                        </div>

                        <AnimatePresence>
                          {showScoreDetails && generatedSEO.content.score_breakdown && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: 'auto', opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              className="mt-4 pt-4 border-t border-gray-200/50 space-y-2"
                            >
                              <ScoreItem label="標題評分" score={generatedSEO.content.score_breakdown.title_score} />
                              <ScoreItem label="描述評分" score={generatedSEO.content.score_breakdown.description_score} />
                              <ScoreItem label="關鍵詞評分" score={generatedSEO.content.score_breakdown.keyword_score} />
                              <ScoreItem label="可讀性評分" score={generatedSEO.content.score_breakdown.readability_score} />
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    )}

                    {/* Meta 標題 */}
                    {generatedSEO.content.meta_title && (
                      <SEOContentBlock
                        label="Meta 標題"
                        content={generatedSEO.content.meta_title}
                        charCount={generatedSEO.content.meta_title.length}
                        maxChars={70}
                        onCopy={() => handleCopy(generatedSEO.content.meta_title, 'meta_title')}
                        isCopied={copiedField === 'meta_title'}
                      />
                    )}

                    {/* Meta 描述 */}
                    {generatedSEO.content.meta_description && (
                      <SEOContentBlock
                        label="Meta 描述"
                        content={generatedSEO.content.meta_description}
                        charCount={generatedSEO.content.meta_description.length}
                        maxChars={160}
                        onCopy={() => handleCopy(generatedSEO.content.meta_description, 'meta_description')}
                        isCopied={copiedField === 'meta_description'}
                      />
                    )}

                    {/* 主要關鍵詞 */}
                    {generatedSEO.content.primary_keyword && (
                      <div className="border border-slate-200 rounded-lg overflow-hidden bg-white/50">
                        <div className="px-4 py-2 bg-slate-50/50 border-b border-slate-100">
                          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">主要關鍵詞</span>
                        </div>
                        <div className="p-4">
                          <HoloBadge variant="info" size="lg">
                            <Target className="w-3 h-3 mr-1" />
                            {generatedSEO.content.primary_keyword}
                          </HoloBadge>
                        </div>
                      </div>
                    )}

                    {/* 次要關鍵詞 */}
                    {generatedSEO.content.secondary_keywords && generatedSEO.content.secondary_keywords.length > 0 && (
                      <div className="border border-slate-200 rounded-lg overflow-hidden bg-white/50">
                        <div className="px-4 py-2 bg-slate-50/50 border-b border-slate-100">
                          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">次要關鍵詞</span>
                        </div>
                        <div className="p-4 flex flex-wrap gap-2">
                          {generatedSEO.content.secondary_keywords.map((keyword, index) => (
                            <HoloBadge key={index} variant="default" size="sm">
                              {keyword}
                            </HoloBadge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 改進建議 */}
                    {generatedSEO.content.improvement_suggestions && generatedSEO.content.improvement_suggestions.length > 0 && (
                      <div className="border border-amber-200 rounded-lg overflow-hidden bg-amber-50/50">
                        <div className="px-4 py-2 bg-amber-100/50 border-b border-amber-200">
                          <span className="text-xs font-bold uppercase tracking-wider text-amber-700">改進建議</span>
                        </div>
                        <div className="p-4">
                          <ul className="space-y-2">
                            {generatedSEO.content.improvement_suggestions.map((suggestion, index) => (
                              <li key={index} className="flex items-start text-sm text-amber-800">
                                <ArrowRight className="w-4 h-4 mr-2 mt-0.5 text-amber-500 flex-shrink-0" />
                                {suggestion}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </HoloCard>

            {/* 右側：關鍵詞分析 */}
            <HoloCard
              glowColor="blue"
              className={cn(
                "lg:max-h-[calc(100vh-200px)] lg:overflow-y-auto",
                mobileSubTab !== 'keywords' && "hidden lg:block"
              )}
            >
              <div className="p-6">
                <HoloPanelHeader
                  title="關鍵詞分析"
                  icon={<Tags className="w-5 h-5" />}
                />

                {!extractedKeywords && !extractKeywordsMutation.isPending && (
                  <div className="flex flex-col items-center justify-center h-[300px] text-gray-400">
                    <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                      <Tags className="w-8 h-8 text-slate-300" />
                    </div>
                    <p className="text-sm text-center">填寫商品資訊後<br />可使用 AI 提取關鍵詞</p>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleExtractKeywords}
                      disabled={!formData.productInfo.name || extractKeywordsMutation.isPending}
                      className="mt-4"
                    >
                      <Zap className="w-4 h-4 mr-2" />
                      AI 提取關鍵詞
                    </Button>
                  </div>
                )}

                {extractKeywordsMutation.isPending && (
                  <div className="flex flex-col items-center justify-center h-[300px]">
                    <div className="relative w-20 h-20 mb-4">
                      <div className="absolute inset-0 bg-blue-200 rounded-full animate-ping opacity-20" />
                      <div className="relative w-20 h-20 bg-gradient-to-br from-blue-100 to-cyan-100 rounded-full flex items-center justify-center">
                        <Tags className="w-10 h-10 text-blue-500 animate-pulse" />
                      </div>
                    </div>
                    <h3 className="text-base font-medium text-gray-900">AI 正在分析...</h3>
                    <p className="text-gray-500 mt-1 text-sm">正在提取最佳關鍵詞組合</p>
                  </div>
                )}

                {extractedKeywords && !extractKeywordsMutation.isPending && (
                  <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {/* 主要關鍵詞 */}
                    <div className="border border-blue-200 rounded-lg overflow-hidden bg-blue-50/50">
                      <div className="px-4 py-2 bg-blue-100/50 border-b border-blue-200">
                        <span className="text-xs font-bold uppercase tracking-wider text-blue-700">主要關鍵詞</span>
                      </div>
                      <div className="p-4">
                        <HoloBadge variant="info" size="lg">
                          <Target className="w-3 h-3 mr-1" />
                          {extractedKeywords.primary_keyword}
                        </HoloBadge>
                      </div>
                    </div>

                    {/* 次要關鍵詞 */}
                    {extractedKeywords.secondary_keywords.length > 0 && (
                      <div className="border border-slate-200 rounded-lg overflow-hidden bg-white/50">
                        <div className="px-4 py-2 bg-slate-50/50 border-b border-slate-100">
                          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">次要關鍵詞</span>
                        </div>
                        <div className="p-4 flex flex-wrap gap-2">
                          {extractedKeywords.secondary_keywords.map((keyword, index) => (
                            <HoloBadge key={index} variant="default" size="sm">
                              {keyword}
                            </HoloBadge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 長尾關鍵詞 */}
                    {extractedKeywords.long_tail_keywords.length > 0 && (
                      <div className="border border-purple-200 rounded-lg overflow-hidden bg-purple-50/50">
                        <div className="px-4 py-2 bg-purple-100/50 border-b border-purple-200">
                          <span className="text-xs font-bold uppercase tracking-wider text-purple-700">長尾關鍵詞</span>
                        </div>
                        <div className="p-4 flex flex-wrap gap-2">
                          {extractedKeywords.long_tail_keywords.map((keyword, index) => (
                            <HoloBadge key={index} variant="default" size="sm" className="bg-purple-100 text-purple-700 border-purple-200">
                              {keyword}
                            </HoloBadge>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* 關鍵詞意圖分析 */}
                    {extractedKeywords.all_keywords && extractedKeywords.all_keywords.length > 0 && (
                      <div className="border border-slate-200 rounded-lg overflow-hidden bg-white/50">
                        <div className="px-4 py-2 bg-slate-50/50 border-b border-slate-100">
                          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">關鍵詞意圖</span>
                        </div>
                        <div className="p-4 space-y-2">
                          {extractedKeywords.all_keywords.slice(0, 5).map((kw, index) => (
                            <div key={index} className="flex items-center justify-between text-sm">
                              <span className="text-gray-700">{kw.keyword}</span>
                              {kw.intent && (
                                <HoloBadge variant={kw.intent === 'transactional' ? 'success' : 'default'} size="sm">
                                  {kw.intent === 'transactional' ? '購買意圖' :
                                   kw.intent === 'informational' ? '資訊型' : '導航型'}
                                </HoloBadge>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <HoloButton
                      onClick={applyExtractedKeywords}
                      variant="secondary"
                      size="sm"
                      className="w-full"
                    >
                      <ArrowRight className="w-4 h-4 mr-2" />
                      應用到目標關鍵詞
                    </HoloButton>
                  </div>
                )}
              </div>
            </HoloCard>
          </div>
        </>
      )}

      {/* 批量生成標籤內容 */}
      {activeTab === 'batch' && (
        <HoloCard glowColor="cyan" className="p-8">
          <div className="flex flex-col items-center justify-center h-[400px] text-gray-400">
            <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-4">
              <Layers className="w-10 h-10 text-slate-300" />
            </div>
            <h3 className="text-lg font-medium text-gray-900">批量 SEO 生成</h3>
            <p className="text-gray-500 mt-2 text-center max-w-md">
              選擇多個商品，一次性生成 SEO 優化內容。<br />
              支持從商品庫選擇或導入 CSV 文件。
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

      {/* 歷史記錄標籤內容 */}
      {activeTab === 'history' && (
        <HoloCard glowColor="cyan" className="p-8">
          <div className="flex flex-col items-center justify-center h-[400px] text-gray-400">
            <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-4">
              <History className="w-10 h-10 text-slate-300" />
            </div>
            <h3 className="text-lg font-medium text-gray-900">尚無歷史記錄</h3>
            <p className="text-gray-500 mt-2">生成的 SEO 內容會自動保存在這裡</p>
          </div>
        </HoloCard>
      )}
    </PageTransition>
  )
}

// =============================================
// 輔助組件
// =============================================

function SEOContentBlock({
  label,
  content,
  charCount,
  maxChars,
  onCopy,
  isCopied,
}: {
  label: string
  content: string
  charCount: number
  maxChars: number
  onCopy: () => void
  isCopied: boolean
}) {
  const isOverLimit = charCount > maxChars

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden bg-white/50 hover:bg-white transition-colors group">
      <div className="flex items-center justify-between px-4 py-2 bg-slate-50/50 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{label}</span>
          <span className={cn(
            "text-xs px-2 py-0.5 rounded-full",
            isOverLimit ? "bg-red-100 text-red-600" : "bg-emerald-100 text-emerald-600"
          )}>
            {charCount}/{maxChars}
          </span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={onCopy}
          className="h-6 px-2 text-slate-400 hover:text-cyan-600"
        >
          {isCopied ? (
            <>
              <Check className="w-3 h-3 mr-1" />
              已複製
            </>
          ) : (
            <>
              <Copy className="w-3 h-3 mr-1" />
              複製
            </>
          )}
        </Button>
      </div>
      <div className="p-4 text-sm leading-relaxed text-slate-700">
        <p>{content}</p>
      </div>
    </div>
  )
}

function ScoreItem({ label, score }: { label: string; score: number }) {
  const getColor = (s: number) => {
    if (s >= 80) return 'bg-emerald-500'
    if (s >= 60) return 'bg-amber-500'
    return 'bg-red-500'
  }

  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-gray-600 w-24">{label}</span>
      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all", getColor(score))}
          style={{ width: `${score}%` }}
        />
      </div>
      <span className="text-sm font-medium text-gray-700 w-8">{score}</span>
    </div>
  )
}
