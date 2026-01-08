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

export default function AIContentPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<'generate' | 'history'>('generate')
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
      queryClient.invalidateQueries({ queryKey: ['content-history'] })
    },
  })

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
    })
  }

  const handleCopy = async (text: string, field: string) => {
    await navigator.clipboard.writeText(text)
    setCopiedField(field)
    setTimeout(() => setCopiedField(null), 2000)
  }

  return (
    <div className="space-y-8 animate-fade-in-up">
      {/* 頁面標題 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
            AI 內容生成
            <Badge variant="outline" className="text-purple-500 border-purple-500/30 bg-purple-500/10">
              Beta
            </Badge>
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
              ? "text-purple-600 bg-white/50 border-b-2 border-purple-600"
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
              ? "text-purple-600 bg-white/50 border-b-2 border-purple-600"
              : "text-muted-foreground hover:text-foreground hover:bg-white/30"
          )}
        >
          <History className="w-4 h-4 mr-2" />
          歷史記錄
        </button>
      </div>

      {/* 生成文案標籤內容 */}
      {activeTab === 'generate' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 左側：輸入表單 */}
          <div className="glass-panel p-6 rounded-xl border border-white/40 space-y-6">
            <div className="flex items-center gap-2 mb-2">
              <Bot className="w-5 h-5 text-purple-500" />
              <h2 className="text-lg font-semibold text-gray-900">輸入商品資訊</h2>
            </div>

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
            </div>

            <Button
              onClick={handleGenerate}
              disabled={!formData.productInfo.name || generateMutation.isPending}
              className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg shadow-purple-500/20"
              size="lg"
            >
              {generateMutation.isPending ? (
                <>
                  <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                  AI 思考中...
                </>
              ) : (
                <>
                  <Sparkles className="w-5 h-5 mr-2" />
                  立即生成
                </>
              )}
            </Button>
          </div>

          {/* 右側：生成結果 */}
          <div className="glass-panel p-6 rounded-xl border border-white/40 min-h-[500px]">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">生成結果</h2>
              {generatedContent && (
                <Badge variant="outline" className="text-green-600 bg-green-50 border-green-200">
                  <Check className="w-3 h-3 mr-1" /> 生成成功
                </Badge>
              )}
            </div>

            {generateMutation.isError && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4 text-red-700 flex items-center">
                <AlertCircle className="w-5 h-5 mr-2" />
                生成失敗，請稍後再試
              </div>
            )}

            {!generatedContent && !generateMutation.isPending && (
              <div className="flex flex-col items-center justify-center h-[400px] text-gray-400">
                <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                  <Sparkles className="w-10 h-10 text-slate-300" />
                </div>
                <p>在左側填寫資訊後，AI 將為您生成文案</p>
              </div>
            )}

            {generateMutation.isPending && (
              <div className="flex flex-col items-center justify-center h-[400px]">
                <div className="relative w-24 h-24 mb-6">
                  <div className="absolute inset-0 bg-purple-200 rounded-full animate-ping opacity-20" />
                  <div className="relative w-24 h-24 bg-gradient-to-br from-purple-100 to-blue-100 rounded-full flex items-center justify-center">
                    <Sparkles className="w-12 h-12 text-purple-500 animate-pulse" />
                  </div>
                </div>
                <h3 className="text-lg font-medium text-gray-900">AI 正在創作中...</h3>
                <p className="text-gray-500 mt-2">正在分析商品特點與市場趨勢</p>
              </div>
            )}

            {generatedContent && !generateMutation.isPending && (
              <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
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
              </div>
            )}
          </div>
        </div>
      )}

      {/* 歷史記錄標籤內容 */}
      {activeTab === 'history' && (
        <div className="glass-panel rounded-xl border border-white/40 overflow-hidden">
          {historyLoading ? (
            <div className="flex items-center justify-center py-20">
              <RefreshCw className="w-8 h-8 animate-spin text-purple-500" />
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
        </div>
      )}
    </div>
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
          className="h-6 px-2 text-slate-400 hover:text-purple-600"
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
                <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-purple-400 flex-shrink-0" />
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
    <div className="px-6 py-4 hover:bg-purple-50/30 transition-colors group">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-4">
          <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:bg-purple-200 transition-colors">
            <Icon className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-gray-900">
              {item.product_name || '未關聯商品'}
            </h3>
            <div className="flex items-center gap-2 mt-1">
              <Badge variant="secondary" className="text-xs font-normal">
                {contentType?.label || item.content_type}
              </Badge>
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
            <Badge className="bg-green-100 text-green-700 hover:bg-green-100 border-green-200">
              已審批
            </Badge>
          ) : item.status === 'rejected' ? (
            <Badge variant="destructive" className="bg-red-100 text-red-700 hover:bg-red-100 border-red-200">
              已拒絕
            </Badge>
          ) : (
            <Button
              size="sm"
              onClick={onApprove}
              disabled={isApproving}
              className="bg-white border-green-200 text-green-700 hover:bg-green-50 hover:text-green-800 hover:border-green-300"
              variant="outline"
            >
              {isApproving ? (
                <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
              ) : (
                <Check className="w-3 h-3 mr-1" />
              )}
              批准
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
