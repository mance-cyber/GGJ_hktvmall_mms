'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, ContentGenerateRequest, ContentItem, GeneratedContent, ProductInfo } from '@/lib/api'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Sparkles,
  RefreshCw,
  AlertCircle,
  Copy,
  Check,
  History,
  Wand2,
  FileText,
  List,
  BookOpen,
  ChevronRight,
  Bot
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
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'
import { ContentOptimizeChat } from '@/components/content/ContentOptimizeChat'
import {
  PageTransition,
  HoloCard,
  HoloPanelHeader,
  HoloButton,
  HoloBadge,
  HoloSkeleton,
} from '@/components/ui/future-tech'

// 內容類型選項
const CONTENT_TYPES = [
  { value: 'title', label: '商品標題', icon: FileText },
  { value: 'selling_points', label: '賣點列表', icon: List },
  { value: 'description', label: '商品描述', icon: BookOpen },
  { value: 'full_copy', label: '完整文案', icon: Wand2 },
] as const

// 風格選項
const STYLES = [
  { value: 'professional', label: '專業正式' },
  { value: 'casual', label: '輕鬆隨意' },
  { value: 'playful', label: '活潑有趣' },
  { value: 'formal', label: '正式官方' },
] as const

// 語言選項
const LANGUAGES = [
  { value: 'TC', label: '繁體中文', flag: '🇭🇰' },
  { value: 'SC', label: '簡體中文', flag: '🇨🇳' },
  { value: 'EN', label: 'English', flag: '🇬🇧' },
] as const

type LanguageCode = 'TC' | 'SC' | 'EN'

// 手機版子 Tab 類型
type MobileSubTab = 'input' | 'result' | 'optimize'

export default function AIContentPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'generate' | 'history'>('generate')
  const [mobileSubTab, setMobileSubTab] = useState<MobileSubTab>('input')
  const [formData, setFormData] = useState<{
    productInfo: ProductInfo
    contentType: ContentGenerateRequest['content_type']
    style: ContentGenerateRequest['style']
  }>({
    productInfo: {
      name: '',
      brand: '',
      features: [],
      target_audience: '',
    },
    contentType: 'full_copy',
    style: 'professional',
  })
  const [featuresInput, setFeaturesInput] = useState('')
  const [generatedContent, setGeneratedContent] = useState<GeneratedContent | null>(null)
  const [copiedField, setCopiedField] = useState<string | null>(null)
  const [currentContentId, setCurrentContentId] = useState<string | null>(null)
  const [currentVersion, setCurrentVersion] = useState<number>(1)
  const [selectedLanguages, setSelectedLanguages] = useState<LanguageCode[]>(['TC'])

  // 獲取歷史記錄
  const { data: history, isLoading: historyLoading } = useQuery({
    queryKey: ['content-history'],
    queryFn: () => api.getContentHistory(undefined, undefined, undefined, 50),
    enabled: activeTab === 'history',
  })

  // 生成內容
  const generateMutation = useMutation({
    mutationFn: (data: ContentGenerateRequest) => api.generateContent(data),
    onSuccess: (response) => {
      setGeneratedContent(response.content)
      setCurrentContentId(response.id)
      setCurrentVersion(1)
      setMobileSubTab('result') // 手機版自動切換到結果 tab
      queryClient.invalidateQueries({ queryKey: ['content-history'] })
    },
  })

  // 處理對話優化後的內容更新
  const handleContentUpdate = (content: GeneratedContent, version: number) => {
    setGeneratedContent(content)
    setCurrentVersion(version)
    queryClient.invalidateQueries({ queryKey: ['content-history'] })
  }

  // 審批內容
  const approveMutation = useMutation({
    mutationFn: (contentId: string) => api.approveContent(contentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content-history'] })
    },
  })

  const handleGenerate = () => {
    const features = featuresInput
      .split('\n')
      .map((f) => f.trim())
      .filter(Boolean)

    generateMutation.mutate({
      product_info: {
        ...formData.productInfo,
        features,
      },
      content_type: formData.contentType,
      style: formData.style,
      target_languages: selectedLanguages,
    })
  }

  const handleCopy = async (text: string, field: string) => {
    await navigator.clipboard.writeText(text)
    setCopiedField(field)
    setTimeout(() => setCopiedField(null), 2000)
  }

  return (
    <PageTransition className="space-y-8">
      {/* 頁面標題 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
            AI 內容生成
            <HoloBadge variant="info" size="sm">
              Beta
            </HoloBadge>
          </h1>
          <p className="text-muted-foreground mt-2 text-lg">
            利用 Claude AI 的強大能力，一鍵生成高品質商品文案
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
          <Wand2 className="w-4 h-4 mr-2" />
          生成文案
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

      {/* 生成文案標籤內容 */}
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
              <Bot className="w-4 h-4" />
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
              <Sparkles className="w-4 h-4" />
              結果
              {generatedContent && mobileSubTab !== 'result' && (
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-emerald-500 rounded-full" />
              )}
            </button>
            <button
              onClick={() => setMobileSubTab('optimize')}
              className={cn(
                "flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg text-sm font-medium transition-all",
                mobileSubTab === 'optimize'
                  ? "bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-md"
                  : "text-gray-600 hover:bg-white/50",
                !generatedContent && "opacity-50 pointer-events-none"
              )}
              disabled={!generatedContent}
            >
              <Wand2 className="w-4 h-4" />
              優化
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 左側：輸入表單 - 手機版按 tab 顯示 */}
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
                  icon={<Bot className="w-5 h-5" />}
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
                    <Label htmlFor="features">商品特點（每行一個）</Label>
                    <Textarea
                      id="features"
                      value={featuresInput}
                      onChange={(e) => setFeaturesInput(e.target.value)}
                      rows={4}
                      placeholder="1000mg 高劑量&#10;美國進口&#10;60粒裝"
                      className="bg-white/50 min-h-[100px]"
                    />
                  </div>

                  <div className="grid gap-2">
                    <Label htmlFor="audience">目標受眾</Label>
                    <Input
                      id="audience"
                      value={formData.productInfo.target_audience}
                      onChange={(e) => setFormData({ ...formData, productInfo: { ...formData.productInfo, target_audience: e.target.value } })}
                      placeholder="例如：注重健康的成年人"
                      className="bg-white/50"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label>內容類型</Label>
                      <Select
                        value={formData.contentType}
                        onValueChange={(val) => setFormData({ ...formData, contentType: val as ContentGenerateRequest['content_type'] })}
                      >
                        <SelectTrigger className="bg-white/50">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {CONTENT_TYPES.map((type) => (
                            <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="grid gap-2">
                      <Label>文案風格</Label>
                      <Select
                        value={formData.style}
                        onValueChange={(val) => setFormData({ ...formData, style: val as ContentGenerateRequest['style'] })}
                      >
                        <SelectTrigger className="bg-white/50">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {STYLES.map((style) => (
                            <SelectItem key={style.value} value={style.value}>{style.label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
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
                    <p className="text-xs text-slate-500">至少選擇一種語言</p>
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
                  {generateMutation.isPending ? 'AI 思考中...' : '立即生成'}
                </HoloButton>
              </div>
            </HoloCard>

            {/* 中間：生成結果 - 手機版按 tab 顯示 */}
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
                  {generatedContent && (
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

                {!generatedContent && !generateMutation.isPending && (
                  <div className="flex flex-col items-center justify-center h-[300px] text-gray-400">
                    <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                      <Sparkles className="w-8 h-8 text-slate-300" />
                    </div>
                    <p className="text-sm text-center">在左側填寫資訊後<br />AI 將為您生成文案</p>
                  </div>
                )}

                {generateMutation.isPending && (
                  <div className="flex flex-col items-center justify-center h-[300px]">
                    <div className="relative w-20 h-20 mb-4">
                      <div className="absolute inset-0 bg-cyan-200 rounded-full animate-ping opacity-20" />
                      <div className="relative w-20 h-20 bg-gradient-to-br from-cyan-100 to-blue-100 rounded-full flex items-center justify-center">
                        <Sparkles className="w-10 h-10 text-cyan-500 animate-pulse" />
                      </div>
                    </div>
                    <h3 className="text-base font-medium text-gray-900">AI 正在創作中...</h3>
                    <p className="text-gray-500 mt-1 text-sm">正在分析商品特點與市場趨勢</p>
                  </div>
                )}

                {generatedContent && !generateMutation.isPending && (
                  <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
                    {/* 版本指示器 */}
                    {currentVersion > 1 && (
                      <div className="flex items-center gap-2 text-xs text-slate-500">
                        <HoloBadge variant="default" size="sm">
                          v{currentVersion}
                        </HoloBadge>
                        <span>已優化 {currentVersion - 1} 次</span>
                      </div>
                    )}

                    {/* 多語言內容顯示 */}
                    {generatedContent.multilang ? (
                      <div className="space-y-4">
                        {Object.entries(generatedContent.multilang).map(([langCode, langContent]) => {
                          const langInfo = LANGUAGES.find(l => l.value === langCode)
                          const langLabel = langInfo ? `${langInfo.flag} ${langInfo.label}` : langCode
                          return (
                            <div key={langCode} className="border border-slate-200 rounded-lg overflow-hidden">
                              <div className="bg-slate-50 px-3 py-1.5 border-b border-slate-200">
                                <span className="font-medium text-slate-700 text-sm">{langLabel}</span>
                              </div>
                              <div className="p-3 space-y-3">
                                {langContent.title && (
                                  <ContentBlock
                                    label="標題"
                                    content={langContent.title}
                                    onCopy={() => handleCopy(langContent.title!, `title-${langCode}`)}
                                    isCopied={copiedField === `title-${langCode}`}
                                  />
                                )}
                                {langContent.selling_points && langContent.selling_points.length > 0 && (
                                  <ContentBlock
                                    label="賣點"
                                    content={langContent.selling_points.join('\n')}
                                    onCopy={() => handleCopy(langContent.selling_points!.join('\n'), `points-${langCode}`)}
                                    isCopied={copiedField === `points-${langCode}`}
                                    isList
                                    listItems={langContent.selling_points}
                                  />
                                )}
                                {langContent.description && (
                                  <ContentBlock
                                    label="描述"
                                    content={langContent.description}
                                    onCopy={() => handleCopy(langContent.description!, `desc-${langCode}`)}
                                    isCopied={copiedField === `desc-${langCode}`}
                                  />
                                )}
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    ) : (
                      <>
                        {generatedContent.title && (
                          <ContentBlock
                            label="商品標題"
                            content={generatedContent.title}
                            onCopy={() => handleCopy(generatedContent.title!, 'title')}
                            isCopied={copiedField === 'title'}
                          />
                        )}

                        {generatedContent.selling_points && generatedContent.selling_points.length > 0 && (
                          <ContentBlock
                            label="賣點列表"
                            content={generatedContent.selling_points.join('\n')}
                            onCopy={() => handleCopy(generatedContent.selling_points!.join('\n'), 'selling_points')}
                            isCopied={copiedField === 'selling_points'}
                            isList
                            listItems={generatedContent.selling_points}
                          />
                        )}

                        {generatedContent.description && (
                          <ContentBlock
                            label="商品描述"
                            content={generatedContent.description}
                            onCopy={() => handleCopy(generatedContent.description!, 'description')}
                            isCopied={copiedField === 'description'}
                          />
                        )}
                      </>
                    )}
                  </div>
                )}
              </div>
            </HoloCard>

            {/* 右側：對話優化區 - 手機版按 tab 顯示 */}
            <HoloCard
              glowColor="blue"
              className={cn(
                "lg:max-h-[calc(100vh-200px)] lg:overflow-y-auto",
                mobileSubTab !== 'optimize' && "hidden lg:block"
              )}
            >
              <div className="p-6">
                <HoloPanelHeader
                  title="對話優化"
                  icon={<Wand2 className="w-5 h-5" />}
                />

                {!generatedContent && !generateMutation.isPending && (
                  <div className="flex flex-col items-center justify-center h-[300px] text-gray-400">
                    <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                      <Wand2 className="w-8 h-8 text-slate-300" />
                    </div>
                    <p className="text-sm text-center">生成文案後<br />可在此進行對話優化</p>
                  </div>
                )}

                {generateMutation.isPending && (
                  <div className="flex flex-col items-center justify-center h-[300px] text-gray-400">
                    <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                      <RefreshCw className="w-8 h-8 text-slate-300 animate-spin" />
                    </div>
                    <p className="text-sm text-center">等待文案生成中...</p>
                  </div>
                )}

                {generatedContent && !generateMutation.isPending && currentContentId && (
                  <ContentOptimizeChat
                    contentId={currentContentId}
                    initialContent={generatedContent}
                    onContentUpdate={handleContentUpdate}
                    selectedLanguages={selectedLanguages}
                    className=""
                  />
                )}
              </div>
            </HoloCard>
          </div>
        </>
      )}

      {/* 歷史記錄標籤內容 */}
      {activeTab === 'history' && (
        <HoloCard glowColor="cyan" className="overflow-hidden">
          {historyLoading ? (
            <div className="p-6 space-y-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="flex items-start gap-4">
                  <HoloSkeleton variant="rectangular" width={40} height={40} className="rounded-lg" />
                  <div className="flex-1 space-y-2">
                    <HoloSkeleton variant="text" width="60%" />
                    <HoloSkeleton variant="text" width="40%" />
                    <HoloSkeleton variant="rectangular" height={60} />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              {history?.data.map((item) => (
                <HistoryItem
                  key={item.id}
                  item={item}
                  onApprove={() => approveMutation.mutate(item.id)}
                  isApproving={approveMutation.isPending}
                />
              ))}

              {(!history?.data || history.data.length === 0) && (
                <div className="px-6 py-20 text-center text-slate-500">
                  <History className="w-12 h-12 mx-auto text-slate-300 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900">尚無歷史記錄</h3>
                  <p className="mt-1">生成的內容會自動保存在這裡</p>
                </div>
              )}
            </div>
          )}
        </HoloCard>
      )}
    </PageTransition>
  )
}

// 內容區塊組件
function ContentBlock({
  label,
  content,
  onCopy,
  isCopied,
  isList = false,
  listItems = [],
}: {
  label: string
  content: string
  onCopy: () => void
  isCopied: boolean
  isList?: boolean
  listItems?: string[]
}) {
  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden bg-white/50 hover:bg-white transition-colors group">
      <div className="flex items-center justify-between px-4 py-2 bg-slate-50/50 border-b border-slate-100">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{label}</span>
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
        {isList ? (
          <ul className="space-y-2">
            {listItems.map((item, index) => (
              <li key={index} className="flex items-start">
                <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-cyan-400 flex-shrink-0" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="whitespace-pre-wrap">{content}</p>
        )}
      </div>
    </div>
  )
}

// 歷史記錄項組件
function HistoryItem({
  item,
  onApprove,
  isApproving,
}: {
  item: ContentItem
  onApprove: () => void
  isApproving: boolean
}) {
  const contentType = CONTENT_TYPES.find((t) => t.value === item.content_type)
  const Icon = contentType?.icon || FileText

  return (
    <div className="px-6 py-4 hover:bg-cyan-50/30 transition-colors group">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4">
          <div className="w-10 h-10 bg-cyan-100 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:bg-cyan-200 transition-colors">
            <Icon className="w-5 h-5 text-cyan-600" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-gray-900">
              {item.product_name || '未關聯商品'}
            </h3>
            <div className="flex items-center gap-2 mt-1">
              <HoloBadge variant="default" size="sm">
                {contentType?.label || item.content_type}
              </HoloBadge>
              <span className="text-xs text-slate-400">
                {new Date(item.generated_at).toLocaleString('zh-HK')}
              </span>
            </div>
            {item.content && (
              <p className="text-sm text-slate-600 mt-2 line-clamp-2 bg-slate-50 p-2 rounded border border-slate-100">
                {item.content}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {item.status === 'approved' ? (
            <HoloBadge variant="success">
              已審批
            </HoloBadge>
          ) : item.status === 'rejected' ? (
            <HoloBadge variant="error">
              已拒絕
            </HoloBadge>
          ) : (
            <HoloButton
              size="sm"
              variant="secondary"
              onClick={onApprove}
              disabled={isApproving}
              loading={isApproving}
              icon={!isApproving ? <Check className="w-3 h-3" /> : undefined}
            >
              批准
            </HoloButton>
          )}
        </div>
      </div>
    </div>
  )
}
