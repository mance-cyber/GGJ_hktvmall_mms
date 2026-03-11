'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Wand2,
  Code,
  ArrowRight,
  Check,
  Loader2,
  Copy,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Target,
  FileText,
  Globe,
  Zap,
  Clock,
  List,
  AlertCircle,
  CheckCircle,
  Languages,
} from 'lucide-react'
import {
  contentPipelineApi,
  ContentPipelineRequest,
  ContentPipelineResponse,
  BatchPipelineRequest,
  BatchPipelineResponse,
  ContentPipelineInput,
  LocalizedContentResponse,
} from '@/lib/api'
import { useLocale } from '@/components/providers/locale-provider'

// =============================================
// Unified content generation pipeline page (supports multilingual)
// =============================================

export default function ContentPipelinePage() {
  const { t } = useLocale()

  // Available languages list (name read from i18n dictionary)
  const AVAILABLE_LANGUAGES = [
    { code: 'zh-HK', name: t['content_pipeline.lang_zh_HK'], flag: '🇭🇰' },
    { code: 'zh-CN', name: t['content_pipeline.lang_zh_CN'], flag: '🇨🇳' },
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'ja', name: '日本語', flag: '🇯🇵' },
  ]

  // Tab State
  const [activeTab, setActiveTab] = useState<'single' | 'batch'>('single')

  // Single product input state
  const [productName, setProductName] = useState('')
  const [brand, setBrand] = useState('GoGoJap')
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')
  const [features, setFeatures] = useState('')
  const [price, setPrice] = useState('')
  const [origin, setOrigin] = useState('')

  // Batch input state
  const [batchInput, setBatchInput] = useState('')

  // OptionState
  const [selectedLanguages, setSelectedLanguages] = useState<string[]>(['zh-HK'])
  const [tone, setTone] = useState('professional')
  const [includeFaq, setIncludeFaq] = useState(false)

  // ResultState
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<ContentPipelineResponse | null>(null)
  const [batchResult, setBatchResult] = useState<BatchPipelineResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Currently displayed language
  const [activeResultLang, setActiveResultLang] = useState<string>('zh-HK')

  // Expanded sections state
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['content', 'seo', 'geo'])
  )

  const toggleLanguage = (langCode: string) => {
    if (selectedLanguages.includes(langCode)) {
      if (selectedLanguages.length > 1) {
        setSelectedLanguages(selectedLanguages.filter(l => l !== langCode))
      }
    } else {
      if (selectedLanguages.length < 4) {
        setSelectedLanguages([...selectedLanguages, langCode])
      }
    }
  }

  const toggleSection = (section: string) => {
    const newSections = new Set(expandedSections)
    if (newSections.has(section)) {
      newSections.delete(section)
    } else {
      newSections.add(section)
    }
    setExpandedSections(newSections)
  }

  const handleGenerate = async () => {
    if (!productName.trim()) {
      setError(t['content_pipeline.error_no_name'])
      return
    }

    if (selectedLanguages.length === 0) {
      setError(t['content_pipeline.error_no_lang'])
      return
    }

    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const request: ContentPipelineRequest = {
        product_info: {
          name: productName,
          brand: brand || 'GoGoJap',
          category: category || undefined,
          description: description || undefined,
          features: features ? features.split('\n').filter(f => f.trim()) : undefined,
          price: price ? parseFloat(price) : undefined,
          origin: origin || undefined,
        },
        languages: selectedLanguages,
        tone,
        include_faq: includeFaq,
        save_to_db: true,
      }

      const response = await contentPipelineApi.generate(request)
      setResult(response)
      // Set the first language as the active language
      if (response.languages && response.languages.length > 0) {
        setActiveResultLang(response.languages[0])
      }
    } catch (err: any) {
      setError(err.message || t['content_pipeline.error_failed'])
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  // Parse batch input
  const parseBatchInput = (input: string): ContentPipelineInput[] => {
    const trimmed = input.trim()
    if (!trimmed) return []

    if (trimmed.startsWith('[')) {
      try {
        const parsed = JSON.parse(trimmed)
        if (Array.isArray(parsed)) {
          return parsed.map(item => ({
            name: item.name || item,
            brand: item.brand || 'GoGoJap',
            category: item.category,
            description: item.description,
            features: item.features,
            price: item.price,
            origin: item.origin,
          }))
        }
      } catch {
        // Continue trying other formats
      }
    }

    const lines = trimmed.split('\n').filter(line => line.trim())
    return lines.map(line => ({
      name: line.trim(),
      brand: 'GoGoJap',
    }))
  }

  const handleBatchGenerate = async () => {
    const products = parseBatchInput(batchInput)

    if (products.length === 0) {
      setError(t['content_pipeline.error_no_info'])
      return
    }

    if (products.length > 20) {
      setError(t['content_pipeline.error_max_products'])
      return
    }

    if (selectedLanguages.length === 0) {
      setError(t['content_pipeline.error_no_lang'])
      return
    }

    setIsLoading(true)
    setError(null)
    setBatchResult(null)

    try {
      const request: BatchPipelineRequest = {
        products,
        languages: selectedLanguages,
        tone,
        include_faq: includeFaq,
        save_to_db: true,
      }

      const response = await contentPipelineApi.batchGenerate(request)
      setBatchResult(response)
    } catch (err: any) {
      setError(err.message || t['content_pipeline.error_batch_failed'])
    } finally {
      setIsLoading(false)
    }
  }

  // Fetch current language content
  const currentLangContent: LocalizedContentResponse | null = result?.localized?.[activeResultLang] || null

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50/30 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Title */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/25">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-800">{t['content_pipeline.title']}</h1>
              <p className="text-slate-500 text-sm">
                {t['content_pipeline.subtitle']}
              </p>
            </div>
          </div>
        </div>

        {/* Tab switch */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab('single')}
            className={`px-4 py-2 rounded-xl font-medium transition-all ${
              activeTab === 'single'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25'
                : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200'
            }`}
          >
            <span className="flex items-center gap-2">
              <Wand2 className="w-4 h-4" />
              {t['content_pipeline.tab_single']}
            </span>
          </button>
          <button
            onClick={() => setActiveTab('batch')}
            className={`px-4 py-2 rounded-xl font-medium transition-all ${
              activeTab === 'batch'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/25'
                : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200'
            }`}
          >
            <span className="flex items-center gap-2">
              <List className="w-4 h-4" />
              {t['content_pipeline.tab_batch']}
            </span>
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Input section */}
          <div className="space-y-6">
            {activeTab === 'single' ? (
              <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-amber-500" />
                  {t['content_pipeline.section_product_info']}
                </h2>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      {t['content_pipeline.field_product_name']} <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={productName}
                      onChange={(e) => setProductName(e.target.value)}
                      placeholder={t['content_pipeline.placeholder_product_name']}
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">{t['content_pipeline.field_brand']}</label>
                      <input
                        type="text"
                        value={brand}
                        onChange={(e) => setBrand(e.target.value)}
                        placeholder="GoGoJap"
                        className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">{t['content_pipeline.field_category']}</label>
                      <input
                        type="text"
                        value={category}
                        onChange={(e) => setCategory(e.target.value)}
                        placeholder={t['content_pipeline.placeholder_category']}
                        className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">{t['content_pipeline.field_price']}</label>
                      <input
                        type="number"
                        value={price}
                        onChange={(e) => setPrice(e.target.value)}
                        placeholder={t['content_pipeline.placeholder_price']}
                        className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">{t['content_pipeline.field_origin']}</label>
                      <input
                        type="text"
                        value={origin}
                        onChange={(e) => setOrigin(e.target.value)}
                        placeholder={t['content_pipeline.placeholder_origin']}
                        className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">{t['content_pipeline.field_features']}</label>
                    <textarea
                      value={features}
                      onChange={(e) => setFeatures(e.target.value)}
                      placeholder={t['content_pipeline.placeholder_features']}
                      rows={3}
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all resize-none"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">{t['content_pipeline.field_description']}</label>
                    <textarea
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      placeholder={t['content_pipeline.placeholder_description']}
                      rows={2}
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all resize-none"
                    />
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                  <List className="w-5 h-5 text-amber-500" />
                  {t['content_pipeline.section_batch_input']}
                </h2>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      {t['content_pipeline.field_product_list']} <span className="text-red-500">*</span>
                      <span className="font-normal text-slate-500 ml-2">{t['content_pipeline.product_list_limit']}</span>
                    </label>
                    <textarea
                      value={batchInput}
                      onChange={(e) => setBatchInput(e.target.value)}
                      placeholder={t['content_pipeline.placeholder_batch']}
                      rows={8}
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all resize-none font-mono text-sm"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Generate options */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
              <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                <Languages className="w-5 h-5 text-emerald-500" />
                {t['content_pipeline.section_language']}
                <span className="text-xs font-normal text-slate-500">
                  {t['content_pipeline.language_limit']}
                </span>
              </h2>

              {/* Language selection */}
              <div className="flex flex-wrap gap-2 mb-6">
                {AVAILABLE_LANGUAGES.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => toggleLanguage(lang.code)}
                    className={`
                      flex items-center gap-2 px-3 py-2 rounded-xl border-2 transition-all
                      ${selectedLanguages.includes(lang.code)
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-slate-200 hover:border-slate-300 text-slate-600'
                      }
                    `}
                  >
                    <span>{lang.flag}</span>
                    <span className="font-medium text-sm">{lang.name}</span>
                    {selectedLanguages.includes(lang.code) && (
                      <Check className="w-4 h-4" />
                    )}
                  </button>
                ))}
              </div>

              {/* Other options */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">{t['content_pipeline.field_tone']}</label>
                  <select
                    value={tone}
                    onChange={(e) => setTone(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                  >
                    <option value="professional">{t['content_pipeline.tone_professional']}</option>
                    <option value="casual">{t['content_pipeline.tone_casual']}</option>
                    <option value="luxury">{t['content_pipeline.tone_luxury']}</option>
                  </select>
                </div>
                <div className="flex items-end">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={includeFaq}
                      onChange={(e) => setIncludeFaq(e.target.checked)}
                      className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-slate-700">{t['content_pipeline.option_faq']}</span>
                  </label>
                </div>
              </div>

              {/* Generate button */}
              <button
                onClick={activeTab === 'single' ? handleGenerate : handleBatchGenerate}
                disabled={isLoading || (activeTab === 'single' ? !productName.trim() : !batchInput.trim())}
                className={`
                  w-full mt-6 py-3 rounded-xl font-semibold text-white
                  flex items-center justify-center gap-2 transition-all
                  ${isLoading || (activeTab === 'single' ? !productName.trim() : !batchInput.trim())
                    ? 'bg-slate-300 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:shadow-lg hover:shadow-blue-500/25'
                  }
                `}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    {t['content_pipeline.generating']}
                  </>
                ) : (
                  <>
                    <Wand2 className="w-5 h-5" />
                    {t['content_pipeline.generate_n_langs'].replace('{n}', String(selectedLanguages.length))}
                  </>
                )}
              </button>

              {error && (
                <p className="mt-3 text-sm text-red-600 text-center">{error}</p>
              )}
            </div>
          </div>

          {/* Right: Result section */}
          <div className="space-y-4">
            {activeTab === 'batch' && batchResult ? (
              <>
                {/* Batch result summary */}
                <div className={`rounded-2xl p-4 text-white ${
                  batchResult.failed_count === 0
                    ? 'bg-gradient-to-r from-emerald-500 to-teal-500'
                    : 'bg-gradient-to-r from-amber-500 to-orange-500'
                }`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {batchResult.failed_count === 0 ? <CheckCircle className="w-6 h-6" /> : <AlertCircle className="w-6 h-6" />}
                      <span className="font-semibold">{t['content_pipeline.batch_complete']}</span>
                    </div>
                    <div className="flex items-center gap-4 text-white/80 text-sm">
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {batchResult.total_time_ms}ms
                      </span>
                      <span>{t['content_pipeline.batch_success'].replace('{successful}', String(batchResult.successful_count)).replace('{total}', String(batchResult.total_products))}</span>
                      <span>{t['content_pipeline.result_lang_count'].replace('{n}', String(batchResult.languages.length))}</span>
                    </div>
                  </div>
                </div>

                {/* Batch result list */}
                {batchResult.results.map((res, index) => (
                  <div key={index} className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                    <div className="px-4 py-3 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 text-xs font-bold flex items-center justify-center">
                          {index + 1}
                        </span>
                        <span className="font-medium text-slate-800">
                          {res.product_info?.name || t['content_pipeline.batch_product_fallback'].replace('{n}', String(index + 1))}
                        </span>
                      </div>
                      <span className="text-xs text-slate-500">{res.generation_time_ms}ms</span>
                    </div>
                    <div className="p-4">
                      <div className="flex flex-wrap gap-2">
                        {res.languages.map(lang => {
                          const content = res.localized[lang]
                          return (
                            <div key={lang} className="flex-1 min-w-[200px] p-3 bg-slate-50 rounded-xl">
                              <div className="flex items-center gap-2 mb-2">
                                <span className="text-lg">{AVAILABLE_LANGUAGES.find(l => l.code === lang)?.flag}</span>
                                <span className="text-xs font-medium text-slate-600">{lang}</span>
                                <span className="px-1.5 py-0.5 bg-emerald-100 text-emerald-700 rounded text-xs font-bold ml-auto">
                                  SEO {content?.seo_score || 0}
                                </span>
                              </div>
                              <p className="text-sm font-medium text-slate-800 line-clamp-1">{content?.title}</p>
                              <p className="text-xs text-slate-500 mt-1 line-clamp-2">{content?.description}</p>
                            </div>
                          )
                        })}
                      </div>
                    </div>
                  </div>
                ))}
              </>
            ) : result && currentLangContent ? (
              <>
                {/* Single result summary */}
                <div className="bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl p-4 text-white">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Check className="w-6 h-6" />
                      <span className="font-semibold">{t['content_pipeline.result_complete']}</span>
                    </div>
                    <div className="flex items-center gap-4 text-emerald-100 text-sm">
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {result.generation_time_ms}ms
                      </span>
                      <span>{t['content_pipeline.result_lang_count'].replace('{n}', String(result.languages.length))}</span>
                    </div>
                  </div>
                </div>

                {/* Language switch tab */}
                <div className="flex gap-2 bg-white rounded-2xl p-2 shadow-sm border border-slate-100">
                  {result.languages.map(lang => {
                    const langInfo = AVAILABLE_LANGUAGES.find(l => l.code === lang)
                    const content = result.localized[lang]
                    return (
                      <button
                        key={lang}
                        onClick={() => setActiveResultLang(lang)}
                        className={`
                          flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl transition-all
                          ${activeResultLang === lang
                            ? 'bg-blue-600 text-white shadow-md'
                            : 'hover:bg-slate-50 text-slate-600'
                          }
                        `}
                      >
                        <span>{langInfo?.flag}</span>
                        <span className="font-medium text-sm">{langInfo?.name}</span>
                        <span className={`px-1.5 py-0.5 rounded text-xs font-bold ${
                          activeResultLang === lang
                            ? 'bg-white/20 text-white'
                            : 'bg-emerald-100 text-emerald-700'
                        }`}>
                          {content?.seo_score || 0}
                        </span>
                      </button>
                    )
                  })}
                </div>

                {/* Content result */}
                <ResultSection
                  title={t['content_pipeline.result_section_content']}
                  icon={<FileText className="w-5 h-5" />}
                  color="blue"
                  expanded={expandedSections.has('content')}
                  onToggle={() => toggleSection('content')}
                >
                  <div className="space-y-4">
                    <ResultItem
                      label={t['content_pipeline.result_field_title']}
                      value={currentLangContent.title}
                      onCopy={() => copyToClipboard(currentLangContent.title)}
                    />
                    <ResultItem
                      label={t['content_pipeline.result_field_selling_points']}
                      value={currentLangContent.selling_points.map((p, i) => `${i + 1}. ${p}`).join('\n')}
                      onCopy={() => copyToClipboard(currentLangContent.selling_points.join('\n'))}
                      multiline
                    />
                    <ResultItem
                      label={t['content_pipeline.result_field_description']}
                      value={currentLangContent.description}
                      onCopy={() => copyToClipboard(currentLangContent.description)}
                      multiline
                    />
                  </div>
                </ResultSection>

                {/* SEO Result */}
                <ResultSection
                  title={t['content_pipeline.result_section_seo']}
                  icon={<Target className="w-5 h-5" />}
                  color="emerald"
                  expanded={expandedSections.has('seo')}
                  onToggle={() => toggleSection('seo')}
                  badge={
                    <span className="px-2 py-0.5 text-xs font-bold bg-emerald-100 text-emerald-700 rounded-full">
                      {t['content_pipeline.result_seo_score'].replace('{score}', String(currentLangContent.seo_score))}
                    </span>
                  }
                >
                  <div className="space-y-4">
                    <ResultItem
                      label={`Meta Title (${currentLangContent.meta_title.length}/70)`}
                      value={currentLangContent.meta_title}
                      onCopy={() => copyToClipboard(currentLangContent.meta_title)}
                    />
                    <ResultItem
                      label={`Meta Description (${currentLangContent.meta_description.length}/160)`}
                      value={currentLangContent.meta_description}
                      onCopy={() => copyToClipboard(currentLangContent.meta_description)}
                      multiline
                    />
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-xs font-medium text-slate-500 uppercase">{t['content_pipeline.result_field_primary_keyword']}</span>
                        <p className="mt-1 font-medium text-emerald-700">{currentLangContent.primary_keyword}</p>
                        <div className="mt-2">
                          <span className="text-xs text-slate-400">{t['content_pipeline.result_field_secondary_keywords']}</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {currentLangContent.secondary_keywords.map((kw, i) => (
                              <span key={i} className="px-2 py-0.5 text-xs bg-slate-100 text-slate-600 rounded">{kw}</span>
                            ))}
                          </div>
                        </div>
                      </div>
                      <div>
                        <span className="text-xs font-medium text-slate-500 uppercase">{t['content_pipeline.result_field_score_breakdown']}</span>
                        <div className="mt-1 space-y-1">
                          {Object.entries(currentLangContent.score_breakdown).map(([key, value]) => (
                            <div key={key} className="flex justify-between text-sm">
                              <span className="text-slate-600">{key}</span>
                              <span className="font-medium">{String(value)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </ResultSection>

                {/* GEO Result */}
                <ResultSection
                  title={t['content_pipeline.result_section_geo']}
                  icon={<Code className="w-5 h-5" />}
                  color="purple"
                  expanded={expandedSections.has('geo')}
                  onToggle={() => toggleSection('geo')}
                >
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-medium text-slate-500 uppercase">Product Schema JSON-LD</span>
                        <button
                          onClick={() => copyToClipboard(JSON.stringify(result.product_schema, null, 2))}
                          className="text-purple-600 hover:text-purple-700"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                      </div>
                      <pre className="p-3 bg-slate-900 text-slate-100 rounded-xl text-xs overflow-x-auto max-h-48">
                        {JSON.stringify(result.product_schema, null, 2)}
                      </pre>
                    </div>

                    {currentLangContent.ai_summary && (
                      <ResultItem
                        label={t['content_pipeline.result_field_ai_summary']}
                        value={currentLangContent.ai_summary}
                        onCopy={() => copyToClipboard(currentLangContent.ai_summary)}
                        multiline
                      />
                    )}

                    {currentLangContent.ai_facts.length > 0 && (
                      <div>
                        <span className="text-xs font-medium text-slate-500 uppercase">{t['content_pipeline.result_field_ai_facts']}</span>
                        <ul className="mt-1 space-y-1">
                          {currentLangContent.ai_facts.map((fact, i) => (
                            <li key={i} className="text-sm text-slate-700 flex items-start gap-2">
                              <Globe className="w-4 h-4 text-purple-500 mt-0.5 flex-shrink-0" />
                              {fact}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </ResultSection>
              </>
            ) : (
              /* Empty state */
              <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-12 text-center">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center mx-auto mb-4">
                  <Languages className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-slate-800 mb-2">{t['content_pipeline.empty_title']}</h3>
                <p className="text-slate-500 text-sm max-w-sm mx-auto">
                  {t['content_pipeline.empty_description']}
                </p>

                <div className="mt-8 flex items-center justify-center gap-2">
                  {AVAILABLE_LANGUAGES.slice(0, 3).map((lang, i) => (
                    <div key={lang.code} className="flex items-center gap-2">
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-400 to-purple-400 flex items-center justify-center text-white text-lg">
                        {lang.flag}
                      </div>
                      {i < 2 && <ArrowRight className="w-4 h-4 text-slate-300" />}
                    </div>
                  ))}
                </div>

                <div className="mt-4 text-xs text-slate-400">
                  {t['content_pipeline.empty_supported']}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}


// =============================================
// Result section component
// =============================================

function ResultSection({
  title,
  icon,
  color,
  expanded,
  onToggle,
  badge,
  children,
}: {
  title: string
  icon: React.ReactNode
  color: 'blue' | 'emerald' | 'purple'
  expanded: boolean
  onToggle: () => void
  badge?: React.ReactNode
  children: React.ReactNode
}) {
  const colorClasses = {
    blue: 'from-blue-500 to-cyan-500',
    emerald: 'from-emerald-500 to-teal-500',
    purple: 'from-purple-500 to-pink-500',
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 flex items-center justify-between hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${colorClasses[color]} flex items-center justify-center text-white`}>
            {icon}
          </div>
          <span className="font-semibold text-slate-800">{title}</span>
          {badge}
        </div>
        {expanded ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="px-4 pb-4 border-t border-slate-100 pt-4">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}


// =============================================
// Result item component
// =============================================

function ResultItem({
  label,
  value,
  onCopy,
  multiline = false,
}: {
  label: string
  value: string
  onCopy: () => void
  multiline?: boolean
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-medium text-slate-500 uppercase">{label}</span>
        <button onClick={onCopy} className="text-slate-400 hover:text-slate-600 transition-colors">
          <Copy className="w-4 h-4" />
        </button>
      </div>
      {multiline ? (
        <p className="text-sm text-slate-700 whitespace-pre-wrap bg-slate-50 p-3 rounded-lg">{value}</p>
      ) : (
        <p className="text-sm text-slate-700 font-medium">{value}</p>
      )}
    </div>
  )
}
