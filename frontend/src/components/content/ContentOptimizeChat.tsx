'use client'

// =============================================
// AI 文案對話式優化組件
// =============================================

import { useState, useRef, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Send,
  Sparkles,
  RefreshCw,
  ChevronDown,
  ChevronUp,
  MessageSquare,
  Wand2,
  Copy,
  Check,
  AlertCircle,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import {
  api,
  GeneratedContent,
  ChatMessage,
  ContentOptimizeRequest,
  ContentOptimizeResponse,
  QuickSuggestion,
} from '@/lib/api'

// =============================================
// 內建快捷建議（備用，優先從 API 獲取）
// =============================================

const FALLBACK_QUICK_SUGGESTIONS: QuickSuggestion[] = [
  { key: 'tone_casual', label: '語氣輕鬆啲', instruction: '請將文案語氣改得更輕鬆親切，加入更多香港地道口語' },
  { key: 'enhance_selling_points', label: '加強賣點', instruction: '請加強產品的核心賣點描述，突出米芝蓮/五星酒店背書' },
  { key: 'shorten', label: '縮短長度', instruction: '請精簡文案，保留重點，去除冗餘內容' },
  { key: 'more_local', label: '更貼地', instruction: '請用更地道的香港口語重寫，讓文案更貼近本地消費者' },
  { key: 'add_urgency', label: '加入限時優惠', instruction: '請加入限時優惠的緊迫感，如「限時88折」「上週一分鐘售罄」等' },
]

// =============================================
// Props 介面
// =============================================

interface ContentOptimizeChatProps {
  contentId: string
  initialContent: GeneratedContent
  onContentUpdate: (content: GeneratedContent, version: number) => void
  selectedLanguages?: ('TC' | 'SC' | 'EN')[]
  className?: string
}

// =============================================
// 對話消息組件
// =============================================

function ChatMessageItem({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user'

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        'flex gap-3 mb-4',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
    >
      <div
        className={cn(
          'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
          isUser ? 'bg-purple-100' : 'bg-blue-100'
        )}
      >
        {isUser ? (
          <MessageSquare className="w-4 h-4 text-purple-600" />
        ) : (
          <Sparkles className="w-4 h-4 text-blue-600" />
        )}
      </div>
      <div
        className={cn(
          'max-w-[80%] rounded-lg px-4 py-2 text-sm',
          isUser
            ? 'bg-purple-100 text-purple-900'
            : 'bg-slate-100 text-slate-800'
        )}
      >
        {message.content}
      </div>
    </motion.div>
  )
}

// =============================================
// 主組件
// =============================================

export function ContentOptimizeChat({
  contentId,
  initialContent,
  onContentUpdate,
  selectedLanguages = ['TC'],
  className,
}: ContentOptimizeChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isExpanded, setIsExpanded] = useState(true)
  const [copiedSuggestion, setCopiedSuggestion] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 獲取快捷建議
  const { data: suggestionsData } = useQuery({
    queryKey: ['optimize-suggestions'],
    queryFn: () => api.getOptimizeSuggestions(),
    staleTime: 1000 * 60 * 10, // 10 分鐘緩存
  })

  const quickSuggestions = suggestionsData?.suggestions || FALLBACK_QUICK_SUGGESTIONS

  // 優化 mutation
  const optimizeMutation = useMutation({
    mutationFn: (data: ContentOptimizeRequest) =>
      api.optimizeContent(contentId, data),
    onSuccess: (response: ContentOptimizeResponse) => {
      // 添加 AI 回覆
      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: `已完成優化！版本更新至 v${response.version}。\n\n後續建議：\n${response.suggestions.map((s, i) => `${i + 1}. ${s}`).join('\n')}`,
      }
      setMessages((prev) => [...prev, aiMessage])

      // 通知父組件更新內容
      onContentUpdate(response.content, response.version)
    },
    onError: (error: Error) => {
      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: `抱歉，優化失敗：${error.message}。請稍後再試。`,
      }
      setMessages((prev) => [...prev, aiMessage])
    },
  })

  // 滾動到底部
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages])

  // 發送優化指令
  const handleSend = (instruction: string) => {
    if (!instruction.trim()) return

    // 添加用戶消息
    const userMessage: ChatMessage = {
      role: 'user',
      content: instruction,
    }
    setMessages((prev) => [...prev, userMessage])
    setInputValue('')

    // 發送優化請求
    optimizeMutation.mutate({
      instruction,
      context: messages,
      target_languages: selectedLanguages,
    })
  }

  // 快捷建議點擊
  const handleQuickSuggestion = (suggestion: QuickSuggestion) => {
    handleSend(suggestion.instruction)
  }

  // 複製建議
  const handleCopySuggestion = (suggestion: QuickSuggestion) => {
    setInputValue(suggestion.instruction)
    setCopiedSuggestion(suggestion.key)
    setTimeout(() => setCopiedSuggestion(null), 1500)
  }

  return (
    <div className={cn('border border-slate-200 rounded-lg bg-white/50 overflow-hidden', className)}>
      {/* 標題欄 */}
      <div
        className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-purple-50 to-blue-50 border-b border-slate-100 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <Wand2 className="w-4 h-4 text-purple-500" />
          <span className="text-sm font-medium text-slate-700">對話式優化</span>
          {messages.length > 0 && (
            <Badge variant="secondary" className="text-xs">
              {messages.length} 條消息
            </Badge>
          )}
        </div>
        <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
          {isExpanded ? (
            <ChevronUp className="w-4 h-4" />
          ) : (
            <ChevronDown className="w-4 h-4" />
          )}
        </Button>
      </div>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {/* 對話歷史區 */}
            {messages.length > 0 && (
              <div className="max-h-[200px] overflow-y-auto p-4 border-b border-slate-100">
                {messages.map((msg, index) => (
                  <ChatMessageItem key={index} message={msg} />
                ))}
                {optimizeMutation.isPending && (
                  <div className="flex items-center gap-2 text-sm text-slate-500">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    AI 正在優化中...
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}

            {/* 快捷建議區 */}
            <div className="p-4 border-b border-slate-100">
              <p className="text-xs text-slate-500 mb-2">快捷優化：</p>
              <div className="flex flex-wrap gap-2">
                {quickSuggestions.map((suggestion) => (
                  <div key={suggestion.key} className="flex items-center">
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-7 text-xs bg-white hover:bg-purple-50 hover:text-purple-700 hover:border-purple-200"
                      onClick={() => handleQuickSuggestion(suggestion)}
                      disabled={optimizeMutation.isPending}
                    >
                      {suggestion.label}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-7 w-7 p-0 ml-1"
                      onClick={() => handleCopySuggestion(suggestion)}
                      title="複製到輸入框"
                    >
                      {copiedSuggestion === suggestion.key ? (
                        <Check className="w-3 h-3 text-green-500" />
                      ) : (
                        <Copy className="w-3 h-3 text-slate-400" />
                      )}
                    </Button>
                  </div>
                ))}
              </div>
            </div>

            {/* 輸入區 */}
            <div className="p-4">
              <div className="flex gap-2">
                <Textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="輸入優化指令，例如：「加強限時優惠感」「語氣更活潑」..."
                  className="min-h-[60px] resize-none bg-white text-sm"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleSend(inputValue)
                    }
                  }}
                />
                <Button
                  onClick={() => handleSend(inputValue)}
                  disabled={!inputValue.trim() || optimizeMutation.isPending}
                  className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white self-end"
                >
                  {optimizeMutation.isPending ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </div>
              <p className="text-xs text-slate-400 mt-2">
                按 Enter 發送，Shift + Enter 換行
              </p>
            </div>

            {/* 錯誤提示 */}
            {optimizeMutation.isError && (
              <div className="px-4 pb-4">
                <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  優化失敗，請稍後再試
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default ContentOptimizeChat
