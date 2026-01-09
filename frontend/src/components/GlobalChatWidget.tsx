'use client'

// =============================================
// 全局浮動聊天組件
// 右下角常駐 Chatbot 按鈕 + 迷你聊天框
// =============================================

import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { usePathname } from 'next/navigation'
import {
  MessageCircle,
  X,
  Send,
  Bot,
  User,
  Loader2,
  Minimize2,
  Maximize2,
  ExternalLink
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import Link from 'next/link'

// =============================================
// Types
// =============================================

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

// =============================================
// 浮動按鈕組件
// =============================================

function FloatingButton({
  isOpen,
  onClick,
  hasUnread
}: {
  isOpen: boolean
  onClick: () => void
  hasUnread: boolean
}) {
  return (
    <motion.button
      onClick={onClick}
      className={cn(
        "w-14 h-14 rounded-full shadow-lg flex items-center justify-center",
        "transition-all duration-300 hover:scale-110",
        "bg-gradient-to-br from-purple-600 to-pink-500",
        "text-white relative"
      )}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      aria-label={isOpen ? "關閉聊天" : "開啟聊天"}
    >
      <AnimatePresence mode="wait">
        {isOpen ? (
          <motion.div
            key="close"
            initial={{ rotate: -90, opacity: 0 }}
            animate={{ rotate: 0, opacity: 1 }}
            exit={{ rotate: 90, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <X className="w-6 h-6" />
          </motion.div>
        ) : (
          <motion.div
            key="chat"
            initial={{ rotate: 90, opacity: 0 }}
            animate={{ rotate: 0, opacity: 1 }}
            exit={{ rotate: -90, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <MessageCircle className="w-6 h-6" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* 未讀指示器 */}
      {hasUnread && !isOpen && (
        <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full animate-pulse" />
      )}

      {/* 光環效果 */}
      <span className="absolute inset-0 rounded-full bg-purple-400 animate-ping opacity-20" />
    </motion.button>
  )
}

// =============================================
// 迷你聊天框組件
// =============================================

function MiniChatBox({
  messages,
  input,
  setInput,
  onSend,
  isLoading,
  onClose,
  isExpanded,
  onToggleExpand
}: {
  messages: ChatMessage[]
  input: string
  setInput: (value: string) => void
  onSend: () => void
  isLoading: boolean
  onClose: () => void
  isExpanded: boolean
  onToggleExpand: () => void
}) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className={cn(
        "bg-white shadow-2xl border overflow-hidden flex flex-col",
        // 移動端全屏，桌面端浮動
        "fixed inset-4 bottom-20 rounded-2xl",
        "sm:relative sm:inset-auto sm:bottom-auto",
        isExpanded
          ? "sm:w-[400px] sm:h-[600px] sm:rounded-2xl"
          : "sm:w-[350px] sm:h-[450px] sm:rounded-2xl"
      )}
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-500 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-white font-medium text-sm">AI 助手</h3>
            <p className="text-white/70 text-xs">隨時為你服務</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <Link href="/agent">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-white/80 hover:text-white hover:bg-white/20"
              title="完整聊天頁面"
            >
              <ExternalLink className="w-4 h-4" />
            </Button>
          </Link>
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleExpand}
            className="h-8 w-8 text-white/80 hover:text-white hover:bg-white/20"
          >
            {isExpanded ? (
              <Minimize2 className="w-4 h-4" />
            ) : (
              <Maximize2 className="w-4 h-4" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={onClose}
            className="h-8 w-8 text-white/80 hover:text-white hover:bg-white/20"
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3 bg-slate-50">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4">
            <div className="w-16 h-16 rounded-full bg-purple-100 flex items-center justify-center mb-3">
              <Bot className="w-8 h-8 text-purple-500" />
            </div>
            <h4 className="font-medium text-slate-700 mb-1">有咩可以幫到你？</h4>
            <p className="text-sm text-slate-500">
              問我任何關於產品、價格、競爭對手嘅問題
            </p>
            {/* 快捷建議 */}
            <div className="mt-4 space-y-2 w-full">
              {['今日訂單點樣？', '比較下競爭對手價格', '邊個產品賣得最好？'].map((suggestion, i) => (
                <button
                  key={i}
                  onClick={() => setInput(suggestion)}
                  className="w-full text-left text-sm px-3 py-2 rounded-lg bg-white border hover:border-purple-300 hover:bg-purple-50 transition-colors text-slate-600"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 5 }}
              animate={{ opacity: 1, y: 0 }}
              className={cn(
                "flex gap-2",
                msg.role === 'user' && "flex-row-reverse"
              )}
            >
              <div className={cn(
                "w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0",
                msg.role === 'user'
                  ? "bg-gradient-to-br from-cyan-500 to-blue-500"
                  : "bg-gradient-to-br from-purple-500 to-pink-500"
              )}>
                {msg.role === 'user' ? (
                  <User className="w-3.5 h-3.5 text-white" />
                ) : (
                  <Bot className="w-3.5 h-3.5 text-white" />
                )}
              </div>
              <div className={cn(
                "max-w-[80%] rounded-xl px-3 py-2 text-sm",
                msg.role === 'user'
                  ? "bg-gradient-to-br from-cyan-500 to-blue-500 text-white rounded-tr-sm"
                  : "bg-white border shadow-sm rounded-tl-sm"
              )}>
                {msg.role === 'assistant' ? (
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <p>{msg.content}</p>
                )}
              </div>
            </motion.div>
          ))
        )}

        {/* Loading indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-2"
          >
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <Bot className="w-3.5 h-3.5 text-white" />
            </div>
            <div className="bg-white border shadow-sm rounded-xl rounded-tl-sm px-3 py-2">
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-100" />
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t bg-white p-3">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && onSend()}
            placeholder="輸入訊息..."
            disabled={isLoading}
            className="flex-1 text-sm"
          />
          <Button
            onClick={onSend}
            disabled={!input.trim() || isLoading}
            size="icon"
            className="bg-purple-600 hover:bg-purple-700 h-9 w-9"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>
    </motion.div>
  )
}

// =============================================
// 主組件
// =============================================

export function GlobalChatWidget() {
  const pathname = usePathname()
  const [isOpen, setIsOpen] = useState(false)
  const [isExpanded, setIsExpanded] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [hasUnread, setHasUnread] = useState(false)

  // 發送訊息 (必須在所有條件返回之前調用所有 Hooks)
  const chatMutation = useMutation({
    mutationFn: (content: string) => api.agentChat({
      content,
      conversation_id: conversationId || undefined
    }),
    onSuccess: (response) => {
      if (!conversationId) {
        setConversationId(response.conversation_id)
      }

      const assistantMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: response.content,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, assistantMessage])

      // 如果聊天框關閉，設置未讀
      if (!isOpen) {
        setHasUnread(true)
      }
    }
  })

  const handleSend = () => {
    if (!input.trim() || chatMutation.isPending) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    chatMutation.mutate(input.trim())
    setInput('')
  }

  const handleOpen = () => {
    setIsOpen(true)
    setHasUnread(false)
  }

  const handleClose = () => {
    setIsOpen(false)
  }

  // 在 Agent 頁面不顯示此組件（避免重複）
  if (pathname === '/agent') {
    return null
  }

  return (
    <div className={cn(
      "fixed z-50 flex flex-col items-end gap-4",
      // 移動端避開底部導航，桌面端正常位置
      "bottom-24 right-4 sm:bottom-6 sm:right-6"
    )}>
      <AnimatePresence>
        {isOpen && (
          <MiniChatBox
            messages={messages}
            input={input}
            setInput={setInput}
            onSend={handleSend}
            isLoading={chatMutation.isPending}
            onClose={handleClose}
            isExpanded={isExpanded}
            onToggleExpand={() => setIsExpanded(!isExpanded)}
          />
        )}
      </AnimatePresence>

      <FloatingButton
        isOpen={isOpen}
        onClick={isOpen ? handleClose : handleOpen}
        hasUnread={hasUnread}
      />
    </div>
  )
}
