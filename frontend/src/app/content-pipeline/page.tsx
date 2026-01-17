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
} from 'lucide-react'
import {
  contentPipelineApi,
  ContentPipelineRequest,
  ContentPipelineResponse,
  BatchPipelineRequest,
  BatchPipelineResponse,
  ContentPipelineInput,
} from '@/lib/api'

// =============================================
// 統一內容生成流水線頁面
// =============================================

export default function ContentPipelinePage() {
  // Tab 狀態
  const [activeTab, setActiveTab] = useState<'single' | 'batch'>('single')

  // 單個產品輸入狀態
  const [productName, setProductName] = useState('')
  const [brand, setBrand] = useState('GoGoJap')
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')
  const [features, setFeatures] = useState('')
  const [price, setPrice] = useState('')
  const [origin, setOrigin] = useState('')

  // 批量輸入狀態
  const [batchInput, setBatchInput] = useState('')
  const [batchProducts, setBatchProducts] = useState<ContentPipelineInput[]>([])

  // 選項狀態
  const [language, setLanguage] = useState('zh-HK')
  const [tone, setTone] = useState('professional')
  const [includeFaq, setIncludeFaq] = useState(false)

  // 結果狀態
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<ContentPipelineResponse | null>(null)
  const [batchResult, setBatchResult] = useState<BatchPipelineResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  // 展開狀態
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['content', 'seo', 'geo'])
  )

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
      setError('請輸入產品名稱')
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
        language,
        tone,
        include_faq: includeFaq,
        save_to_db: true,
      }

      const response = await contentPipelineApi.generate(request)
      setResult(response)
    } catch (err: any) {
      setError(err.message || '生成失敗')
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  // 解析批量輸入（支持 JSON 數組或每行一個產品名）
  const parseBatchInput = (input: string): ContentPipelineInput[] => {
    const trimmed = input.trim()
    if (!trimmed) return []

    // 嘗試解析為 JSON
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
        // 不是有效 JSON，繼續嘗試其他格式
      }
    }

    // 按行分割，每行作為一個產品名
    const lines = trimmed.split('\n').filter(line => line.trim())
    return lines.map(line => ({
      name: line.trim(),
      brand: 'GoGoJap',
    }))
  }

  const handleBatchGenerate = async () => {
    const products = parseBatchInput(batchInput)

    if (products.length === 0) {
      setError('請輸入產品信息')
      return
    }

    if (products.length > 20) {
      setError('最多支持 20 個產品')
      return
    }

    setIsLoading(true)
    setError(null)
    setBatchResult(null)
    setBatchProducts(products)

    try {
      const request: BatchPipelineRequest = {
        products,
        language,
        tone,
        include_faq: includeFaq,
        save_to_db: true,
      }

      const response = await contentPipelineApi.batchGenerate(request)
      setBatchResult(response)
    } catch (err: any) {
      setError(err.message || '批量生成失敗')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50/30 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 標題 */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-blue-500/25">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-800">內容生成流水線</h1>
              <p className="text-slate-500 text-sm">
                一次 AI 調用，自動生成文案、SEO、結構化數據
              </p>
            </div>
          </div>
        </div>

        {/* Tab 切換 */}
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
              單個生成
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
              批量生成
            </span>
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* 左側：輸入區 */}
          <div className="space-y-6">
            {activeTab === 'single' ? (
              /* 單個產品輸入 */
              <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-amber-500" />
                  產品信息
                </h2>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      產品名稱 <span className="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      value={productName}
                      onChange={(e) => setProductName(e.target.value)}
                      placeholder="例：A5 和牛"
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                    />
                  </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      品牌
                    </label>
                    <input
                      type="text"
                      value={brand}
                      onChange={(e) => setBrand(e.target.value)}
                      placeholder="GoGoJap"
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      分類
                    </label>
                    <input
                      type="text"
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                      placeholder="例：和牛"
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      價格 (HKD)
                    </label>
                    <input
                      type="number"
                      value={price}
                      onChange={(e) => setPrice(e.target.value)}
                      placeholder="例：888"
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      產地
                    </label>
                    <input
                      type="text"
                      value={origin}
                      onChange={(e) => setOrigin(e.target.value)}
                      placeholder="例：日本福崗"
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    產品特點（每行一個）
                  </label>
                  <textarea
                    value={features}
                    onChange={(e) => setFeatures(e.target.value)}
                    placeholder="福崗直送&#10;雪花紋理細膩&#10;入口即化"
                    rows={3}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all resize-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    現有描述（可選）
                  </label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="如有現有描述可填入，AI 會參考優化"
                    rows={2}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all resize-none"
                  />
                </div>
              </div>
            </div>
            ) : (
              /* 批量產品輸入 */
              <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
                <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                  <List className="w-5 h-5 text-amber-500" />
                  批量產品輸入
                </h2>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                      產品列表 <span className="text-red-500">*</span>
                      <span className="font-normal text-slate-500 ml-2">（最多 20 個）</span>
                    </label>
                    <textarea
                      value={batchInput}
                      onChange={(e) => setBatchInput(e.target.value)}
                      placeholder={`輸入方式一：每行一個產品名
A5 和牛
北海道帆立貝
博多明太子

輸入方式二：JSON 格式（可附加詳細信息）
[
  {"name": "A5 和牛", "brand": "GoGoJap", "category": "和牛"},
  {"name": "北海道帆立貝", "origin": "日本北海道"}
]`}
                      rows={10}
                      className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all resize-none font-mono text-sm"
                    />
                  </div>

                  <div className="flex items-center gap-2 text-sm text-slate-500">
                    <AlertCircle className="w-4 h-4" />
                    <span>批量生成將並發處理，每次最多同時處理 3 個產品</span>
                  </div>
                </div>
              </div>
            )}

            {/* 流水線選項 */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6">
              <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
                <Target className="w-5 h-5 text-emerald-500" />
                生成選項
              </h2>

              {/* 其他選項 */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    語言
                  </label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                  >
                    <option value="zh-HK">繁體中文</option>
                    <option value="zh-CN">簡體中文</option>
                    <option value="en">English</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">
                    語氣風格
                  </label>
                  <select
                    value={tone}
                    onChange={(e) => setTone(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition-all"
                  >
                    <option value="professional">專業</option>
                    <option value="casual">輕鬆</option>
                    <option value="luxury">高端奢華</option>
                  </select>
                </div>
              </div>

              <div className="mt-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeFaq}
                    onChange={(e) => setIncludeFaq(e.target.checked)}
                    className="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-slate-700">生成 FAQ Schema（額外 AI 調用）</span>
                </label>
              </div>

              {/* 生成按鈕 */}
              {activeTab === 'single' ? (
                <button
                  onClick={handleGenerate}
                  disabled={isLoading || !productName.trim()}
                  className={`
                    w-full mt-6 py-3 rounded-xl font-semibold text-white
                    flex items-center justify-center gap-2 transition-all
                    ${isLoading || !productName.trim()
                      ? 'bg-slate-300 cursor-not-allowed'
                      : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:shadow-lg hover:shadow-blue-500/25'
                    }
                  `}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      生成中...
                    </>
                  ) : (
                    <>
                      <Wand2 className="w-5 h-5" />
                      一鍵生成
                    </>
                  )}
                </button>
              ) : (
                <button
                  onClick={handleBatchGenerate}
                  disabled={isLoading || !batchInput.trim()}
                  className={`
                    w-full mt-6 py-3 rounded-xl font-semibold text-white
                    flex items-center justify-center gap-2 transition-all
                    ${isLoading || !batchInput.trim()
                      ? 'bg-slate-300 cursor-not-allowed'
                      : 'bg-gradient-to-r from-amber-500 to-orange-500 hover:shadow-lg hover:shadow-amber-500/25'
                    }
                  `}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      批量生成中...
                    </>
                  ) : (
                    <>
                      <List className="w-5 h-5" />
                      批量生成
                    </>
                  )}
                </button>
              )}

              {error && (
                <p className="mt-3 text-sm text-red-600 text-center">{error}</p>
              )}
            </div>
          </div>

          {/* 右側：結果區 */}
          <div className="space-y-4">
            {/* 批量結果顯示 */}
            {activeTab === 'batch' && batchResult ? (
              <>
                {/* 批量執行摘要 */}
                <div className={`rounded-2xl p-4 text-white ${
                  batchResult.failed_count === 0
                    ? 'bg-gradient-to-r from-emerald-500 to-teal-500'
                    : batchResult.successful_count === 0
                    ? 'bg-gradient-to-r from-red-500 to-rose-500'
                    : 'bg-gradient-to-r from-amber-500 to-orange-500'
                }`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {batchResult.failed_count === 0 ? (
                        <CheckCircle className="w-6 h-6" />
                      ) : (
                        <AlertCircle className="w-6 h-6" />
                      )}
                      <span className="font-semibold">
                        批量生成完成
                      </span>
                    </div>
                    <div className="flex items-center gap-4 text-white/80 text-sm">
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {batchResult.total_time_ms}ms
                      </span>
                      <span>
                        成功 {batchResult.successful_count}/{batchResult.total_products}
                      </span>
                    </div>
                  </div>
                </div>

                {/* 錯誤列表 */}
                {batchResult.errors.length > 0 && (
                  <div className="bg-red-50 border border-red-200 rounded-2xl p-4">
                    <h3 className="text-sm font-semibold text-red-700 mb-2 flex items-center gap-2">
                      <AlertCircle className="w-4 h-4" />
                      失敗項目 ({batchResult.errors.length})
                    </h3>
                    <ul className="space-y-1">
                      {batchResult.errors.map((err, i) => (
                        <li key={i} className="text-sm text-red-600">
                          #{err.index + 1} {err.product_name}: {err.error}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* 成功結果列表 */}
                {batchResult.results.map((res, index) => (
                  <div key={index} className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
                    <div className="px-4 py-3 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 text-xs font-bold flex items-center justify-center">
                          {index + 1}
                        </span>
                        <span className="font-medium text-slate-800">
                          {res.product_info?.name || `產品 ${index + 1}`}
                        </span>
                      </div>
                      <span className="text-xs text-slate-500">
                        {res.generation_time_ms}ms
                      </span>
                    </div>
                    <div className="p-4 space-y-3">
                      {res.title && (
                        <div>
                          <span className="text-xs font-medium text-blue-600 uppercase flex items-center gap-1">
                            內容
                            <span className="px-1.5 py-0.5 bg-emerald-100 text-emerald-700 rounded text-xs font-bold">
                              SEO {res.seo_score}分
                            </span>
                          </span>
                          <p className="text-sm font-medium text-slate-800 mt-1">{res.title}</p>
                          <p className="text-xs text-slate-500 mt-1 line-clamp-2">{res.description}</p>
                        </div>
                      )}
                      {res.ai_summary && (
                        <div>
                          <span className="text-xs font-medium text-purple-600 uppercase">GEO 摘要</span>
                          <p className="text-xs text-slate-500 mt-1 line-clamp-2">{res.ai_summary}</p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </>
            ) : result ? (
              <>
                {/* 單個執行摘要 */}
                <div className="bg-gradient-to-r from-emerald-500 to-teal-500 rounded-2xl p-4 text-white">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Check className="w-6 h-6" />
                      <span className="font-semibold">生成完成</span>
                    </div>
                    <div className="flex items-center gap-4 text-emerald-100 text-sm">
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {result.generation_time_ms}ms
                      </span>
                      <span className="px-2 py-0.5 bg-white/20 rounded-full text-xs font-medium">
                        SEO {result.seo_score} 分
                      </span>
                    </div>
                  </div>
                </div>

                {/* 文案結果 */}
                {result.title && (
                  <ResultSection
                    title="文案生成"
                    icon={<FileText className="w-5 h-5" />}
                    color="blue"
                    expanded={expandedSections.has('content')}
                    onToggle={() => toggleSection('content')}
                  >
                    <div className="space-y-4">
                      <ResultItem
                        label="標題"
                        value={result.title}
                        onCopy={() => copyToClipboard(result.title)}
                      />
                      <ResultItem
                        label="賣點"
                        value={result.selling_points.map((p, i) => `${i + 1}. ${p}`).join('\n')}
                        onCopy={() => copyToClipboard(result.selling_points.join('\n'))}
                        multiline
                      />
                      <ResultItem
                        label="描述"
                        value={result.description}
                        onCopy={() => copyToClipboard(result.description)}
                        multiline
                      />
                    </div>
                  </ResultSection>
                )}

                {/* SEO 結果 */}
                {result.meta_title && (
                  <ResultSection
                    title="SEO 優化"
                    icon={<Target className="w-5 h-5" />}
                    color="emerald"
                    expanded={expandedSections.has('seo')}
                    onToggle={() => toggleSection('seo')}
                    badge={
                      <span className="px-2 py-0.5 text-xs font-bold bg-emerald-100 text-emerald-700 rounded-full">
                        {result.seo_score} 分
                      </span>
                    }
                  >
                    <div className="space-y-4">
                      <ResultItem
                        label={`Meta Title (${result.meta_title.length}/70)`}
                        value={result.meta_title}
                        onCopy={() => copyToClipboard(result.meta_title)}
                      />
                      <ResultItem
                        label={`Meta Description (${result.meta_description.length}/160)`}
                        value={result.meta_description}
                        onCopy={() => copyToClipboard(result.meta_description)}
                        multiline
                      />
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <span className="text-xs font-medium text-slate-500 uppercase">主關鍵詞</span>
                          <p className="mt-1 font-medium text-emerald-700">{result.primary_keyword}</p>
                          <div className="mt-2">
                            <span className="text-xs text-slate-400">次要關鍵詞</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {result.secondary_keywords.map((kw, i) => (
                                <span key={i} className="px-2 py-0.5 text-xs bg-slate-100 text-slate-600 rounded">
                                  {kw}
                                </span>
                              ))}
                            </div>
                          </div>
                          <div className="mt-2">
                            <span className="text-xs text-slate-400">長尾關鍵詞</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                              {result.long_tail_keywords.map((kw, i) => (
                                <span key={i} className="px-2 py-0.5 text-xs bg-blue-50 text-blue-600 rounded">
                                  {kw}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                        <div>
                          <span className="text-xs font-medium text-slate-500 uppercase">評分明細</span>
                          <div className="mt-1 space-y-1">
                            {Object.entries(result.score_breakdown).map(([key, value]) => (
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
                )}

                {/* GEO 結果 */}
                {result.product_schema && (
                  <ResultSection
                    title="GEO 結構化數據"
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

                      {result.ai_summary && (
                        <ResultItem
                          label="AI 摘要"
                          value={result.ai_summary}
                          onCopy={() => copyToClipboard(result.ai_summary)}
                          multiline
                        />
                      )}

                      {result.ai_facts && result.ai_facts.length > 0 && (
                        <div>
                          <span className="text-xs font-medium text-slate-500 uppercase">AI 事實</span>
                          <ul className="mt-1 space-y-1">
                            {result.ai_facts.map((fact, i) => (
                              <li key={i} className="text-sm text-slate-700 flex items-start gap-2">
                                <Globe className="w-4 h-4 text-purple-500 mt-0.5 flex-shrink-0" />
                                {fact}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {result.faq_schema && (
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-medium text-slate-500 uppercase">FAQ Schema</span>
                            <button
                              onClick={() => copyToClipboard(JSON.stringify(result.faq_schema, null, 2))}
                              className="text-purple-600 hover:text-purple-700"
                            >
                              <Copy className="w-4 h-4" />
                            </button>
                          </div>
                          <pre className="p-3 bg-slate-900 text-slate-100 rounded-xl text-xs overflow-x-auto max-h-32">
                            {JSON.stringify(result.faq_schema, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  </ResultSection>
                )}
              </>
            ) : (
              /* 空狀態 */
              <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-12 text-center">
                <div className={`w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 ${
                  activeTab === 'single'
                    ? 'bg-gradient-to-br from-blue-100 to-purple-100'
                    : 'bg-gradient-to-br from-amber-100 to-orange-100'
                }`}>
                  {activeTab === 'single' ? (
                    <Wand2 className="w-8 h-8 text-blue-600" />
                  ) : (
                    <List className="w-8 h-8 text-amber-600" />
                  )}
                </div>
                <h3 className="text-lg font-semibold text-slate-800 mb-2">
                  {activeTab === 'single' ? '一站式內容生成' : '批量內容生成'}
                </h3>
                <p className="text-slate-500 text-sm max-w-sm mx-auto">
                  {activeTab === 'single'
                    ? '輸入產品信息，一次 AI 調用生成文案、SEO 優化內容和結構化數據'
                    : '輸入多個產品（每行一個或 JSON 格式），批量生成內容，提高效率'}
                </p>

                {/* 流程圖 */}
                <div className="mt-8 flex items-center justify-center gap-2 flex-wrap">
                  {activeTab === 'batch' && (
                    <>
                      <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 to-orange-400 flex items-center justify-center text-white">
                        <List className="w-5 h-5" />
                      </div>
                      <ArrowRight className="w-4 h-4 text-slate-300" />
                    </>
                  )}
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-white">
                    <FileText className="w-5 h-5" />
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-300" />
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white">
                    <Target className="w-5 h-5" />
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-300" />
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white">
                    <Code className="w-5 h-5" />
                  </div>
                </div>

                <div className="mt-4 text-xs text-slate-400">
                  文案 → SEO → GEO（一次 AI 調用）
                </div>

                {activeTab === 'batch' && (
                  <div className="mt-2 text-xs text-slate-400">
                    最多支持 20 個產品，並發處理提高效率
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}


// =============================================
// 結果區塊組件
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
        {expanded ? (
          <ChevronUp className="w-5 h-5 text-slate-400" />
        ) : (
          <ChevronDown className="w-5 h-5 text-slate-400" />
        )}
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
// 結果項目組件
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
        <button
          onClick={onCopy}
          className="text-slate-400 hover:text-slate-600 transition-colors"
        >
          <Copy className="w-4 h-4" />
        </button>
      </div>
      {multiline ? (
        <p className="text-sm text-slate-700 whitespace-pre-wrap bg-slate-50 p-3 rounded-lg">
          {value}
        </p>
      ) : (
        <p className="text-sm text-slate-700 font-medium">{value}</p>
      )}
    </div>
  )
}
