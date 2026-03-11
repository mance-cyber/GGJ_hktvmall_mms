'use client'

// =============================================
// AI 文案對話式Optimize組items
// =============================================

import { useState, useRef, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  Send,
  Sparkles,
  RefreshCw,
  MessageSquare,
  AlertCircle,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
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
// 內建快捷suggestions（備用，優先從 API Fetch）
// =============================================

const FALLBACK_QUICK_SUGGESTIONS: QuickSuggestion[] = [
  { key: 'tone_casual', label: '語氣輕鬆啲', instruction: '請將文案語氣改得更輕鬆親切，加入更多香港地道口語' },
  { key: 'enhance_selling_points', label: '加強賣點', instruction: '請加強Product的核心賣點Description，突出米芝蓮/五星酒店背書' },
  { key: 'shorten', label: '縮短長度', instruction: 'Please refine the copy, keep the key points, remove redundancyContent' },
  { key: 'more_local', label: '更貼地', instruction: 'Please rewrite in more authentic Hong Kong colloquial, make copy closer to local consumers' },
  { key: 'add_urgency', label: '加入限時優惠', instruction: '請加入限時優惠的緊迫感，如「限時88折」「上週一minutes售罄」等' },
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
// 對話消息組items
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
// 主組items
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
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Fetch快捷suggestions
  const { data: suggestionsData } = useQuery({
    queryKey: ['optimize-suggestions'],
    queryFn: () => api.getOptimizeSuggestions(),
    staleTime: 1000 * 60 * 10, // 10 minutesCache
  })

  const quickSuggestions = suggestionsData?.suggestions || FALLBACK_QUICK_SUGGESTIONS

  // Optimize mutation
  const optimizeMutation = useMutation({
    mutationFn: (data: ContentOptimizeRequest) =>
      api.optimizeContent(contentId, data),
    onSuccess: (response: ContentOptimizeResponse) => {
      // 添加 AI 回覆
      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: `已CompleteOptimize！VersionUpdate至 v${response.version}。\n\n後續suggestions：\n${response.suggestions.map((s, i) => `${i + 1}. ${s}`).join('\n')}`,
      }
      setMessages((prev) => [...prev, aiMessage])

      // Notification父組itemsUpdateContent
      onContentUpdate(response.content, response.version)
    },
    onError: (error: Error) => {
      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: `抱歉，OptimizeFailed：${error.message}。請稍後再試。`,
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

  // 發送Optimize指令
  const handleSend = (instruction: string) => {
    if (!instruction.trim()) return

    // 添加用戶消息
    const userMessage: ChatMessage = {
      role: 'user',
      content: instruction,
    }
    setMessages((prev) => [...prev, userMessage])
    setInputValue('')

    // 發送OptimizeRequest
    optimizeMutation.mutate({
      instruction,
      context: messages,
      target_languages: selectedLanguages,
    })
  }

  // 快捷suggestions點擊
  const handleQuickSuggestion = (suggestion: QuickSuggestion) => {
    handleSend(suggestion.instruction)
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* 快捷suggestions區 */}
      <div>
        <p className="text-xs text-slate-500 mb-2">快捷Optimize：</p>
        <div className="flex flex-wrap gap-1.5">
          {quickSuggestions.map((suggestion) => (
            <Button
              key={suggestion.key}
              variant="outline"
              size="sm"
              className="h-7 text-xs bg-white hover:bg-purple-50 hover:text-purple-700 hover:border-purple-200"
              onClick={() => handleQuickSuggestion(suggestion)}
              disabled={optimizeMutation.isPending}
            >
              {suggestion.label}
            </Button>
          ))}
        </div>
      </div>

      {/* 對話History區 */}
      {messages.length > 0 && (
        <div className="border border-slate-200 rounded-lg bg-white/50">
          <div className="max-h-[250px] overflow-y-auto p-3">
            {messages.map((msg, index) => (
              <ChatMessageItem key={index} message={msg} />
            ))}
            {optimizeMutation.isPending && (
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <RefreshCw className="w-4 h-4 animate-spin" />
                AI currentlyOptimize中...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      )}

      {/* Input區 */}
      <div>
        <div className="flex gap-2">
          <Textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="InputOptimize指令，例如：「加強限時優惠感」「語氣更活潑」..."
            className="min-h-[80px] resize-none bg-white text-sm"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend(inputValue)
              }
            }}
          />
        </div>
        <div className="flex items-center justify-between mt-2">
          <p className="text-xs text-slate-400">
            Enter 發送 · Shift+Enter 換行
          </p>
          <Button
            onClick={() => handleSend(inputValue)}
            disabled={!inputValue.trim() || optimizeMutation.isPending}
            size="sm"
            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white"
          >
            {optimizeMutation.isPending ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <Send className="w-4 h-4 mr-1" />
                發送
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Error hint */}
      {optimizeMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          OptimizeFailed，請稍後再試
        </div>
      )}
    </div>
  )
}

export default ContentOptimizeChat
