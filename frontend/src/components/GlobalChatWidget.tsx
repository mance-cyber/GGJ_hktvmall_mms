'use client'

// =============================================
// 全局浮動聊天組件
// 右下角常駐 Chatbot 按鈕 + 迷你聊天框
// 功能：聲音提醒、附件上傳、訊息反饋、頁面感知、可拖曳
// =============================================

import { useState, useRef, useEffect, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { motion, AnimatePresence, useMotionValue } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { DotLottieReact } from '@lottiefiles/dotlottie-react'
import { usePathname } from 'next/navigation'
import {
  X,
  Send,
  User,
  Loader2,
  Minimize2,
  Maximize2,
  ExternalLink,
  Paperclip,
  Image as ImageIcon,
  ThumbsUp,
  ThumbsDown,
  Volume2,
  VolumeX
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import Link from 'next/link'

// =============================================
// Types
// =============================================

interface FollowUpSuggestion {
  text: string
  icon: string
}

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  feedback?: 'like' | 'dislike' | null
  attachments?: FileAttachment[]
  suggestions?: FollowUpSuggestion[]
}

interface FileAttachment {
  id: string
  name: string
  type: string
  url: string
  size: number
}

// =============================================
// 頁面感知建議配置
// =============================================

const PAGE_SUGGESTIONS: Record<string, string[]> = {
  '/': [
    '今日營業額幾多？',
    '有冇需要關注嘅警報？',
    '最近訂單情況點樣？'
  ],
  '/dashboard': [
    '今日銷售數據點樣？',
    '邊個產品賣得最好？',
    '同上星期比較下'
  ],
  '/products': [
    '邊個產品需要補貨？',
    '價格有冇競爭力？',
    '產品銷量排行榜'
  ],
  '/competitors': [
    '競爭對手最新價格？',
    '邊個競爭對手最有威脅？',
    '價格差異分析'
  ],
  '/alerts': [
    '有幾多個未處理警報？',
    '最緊急嘅警報係咩？',
    '警報趨勢分析'
  ],
  '/orders': [
    '今日訂單數量？',
    '有冇異常訂單？',
    '訂單完成率幾多？'
  ],
  '/analytics': [
    '本月營收趨勢？',
    '用戶行為分析',
    '轉化率點樣？'
  ]
}

const DEFAULT_SUGGESTIONS = [
  '今日訂單點樣？',
  '比較下競爭對手價格',
  '邊個產品賣得最好？'
]

// =============================================
// 聲音提醒 Hook
// =============================================

function useNotificationSound() {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [soundEnabled, setSoundEnabled] = useState(true)

  useEffect(() => {
    // 創建音頻元素
    audioRef.current = new Audio('/audio/notification.mp3')
    audioRef.current.volume = 0.5

    // 從 localStorage 讀取設定
    const saved = localStorage.getItem('chatbot-sound-enabled')
    if (saved !== null) {
      setSoundEnabled(saved === 'true')
    }
  }, [])

  const playSound = useCallback(() => {
    if (soundEnabled && audioRef.current) {
      audioRef.current.currentTime = 0
      audioRef.current.play().catch(() => {
        // 忽略自動播放限制錯誤
      })
    }
  }, [soundEnabled])

  const toggleSound = useCallback(() => {
    setSoundEnabled(prev => {
      const newValue = !prev
      localStorage.setItem('chatbot-sound-enabled', String(newValue))
      return newValue
    })
  }, [])

  return { soundEnabled, toggleSound, playSound }
}

// =============================================
// 浮動按鈕組件（可拖曳）
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
  // 使用 useMotionValue 實現流暢拖動（避免 state 更新造成的延遲）
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const dotLottieInstance = useRef<any>(null)

  // 動畫播放完成後停頓 3 秒再重新播放（使用 play API 避免閃爍）
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const dotLottieRefCallback = useCallback((dotLottie: any) => {
    if (dotLottie) {
      dotLottieInstance.current = dotLottie
      dotLottie.addEventListener('complete', () => {
        // 停頓 3 秒後重新播放
        setTimeout(() => {
          if (dotLottieInstance.current) {
            dotLottieInstance.current.setFrame(0)
            dotLottieInstance.current.play()
          }
        }, 3000)
      })
    }
  }, [])

  return (
    <motion.button
      drag
      dragElastic={0.15}
      dragTransition={{ bounceStiffness: 300, bounceDamping: 20 }}
      onClick={onClick}
      style={{ x, y }}
      className={cn(
        "w-36 h-36 flex items-center justify-center",
        "relative cursor-grab active:cursor-grabbing touch-none"
      )}
      whileHover={{ scale: 1.05 }}
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
            className="w-14 h-14 rounded-full bg-gradient-to-br from-purple-600 to-pink-500 flex items-center justify-center shadow-lg"
          >
            <X className="w-6 h-6 text-white" />
          </motion.div>
        ) : (
          <motion.div
            key="chat"
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="w-full h-full flex items-center justify-center"
          >
            <DotLottieReact
              src="/animations/live-chatbot.lottie"
              loop={false}
              autoplay
              speed={0.7}
              dotLottieRefCallback={dotLottieRefCallback}
              style={{ width: 144, height: 144 }}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* 未讀指示器 */}
      {hasUnread && !isOpen && (
        <span className="absolute top-2 right-2 w-4 h-4 bg-red-500 rounded-full animate-pulse" />
      )}
    </motion.button>
  )
}

// =============================================
// 訊息反饋組件
// =============================================

function MessageFeedback({
  messageId,
  feedback,
  onFeedback
}: {
  messageId: string
  feedback: 'like' | 'dislike' | null | undefined
  onFeedback: (messageId: string, type: 'like' | 'dislike') => void
}) {
  return (
    <div className="flex items-center gap-1 mt-1">
      <button
        type="button"
        onClick={() => onFeedback(messageId, 'like')}
        className={cn(
          "p-1 rounded hover:bg-green-100 transition-colors",
          feedback === 'like' && "bg-green-100 text-green-600"
        )}
        title="有幫助"
      >
        <ThumbsUp className={cn("w-3 h-3", feedback === 'like' ? "fill-current" : "")} />
      </button>
      <button
        type="button"
        onClick={() => onFeedback(messageId, 'dislike')}
        className={cn(
          "p-1 rounded hover:bg-red-100 transition-colors",
          feedback === 'dislike' && "bg-red-100 text-red-600"
        )}
        title="需要改進"
      >
        <ThumbsDown className={cn("w-3 h-3", feedback === 'dislike' ? "fill-current" : "")} />
      </button>
    </div>
  )
}

// =============================================
// 附件預覽組件
// =============================================

function AttachmentPreview({
  attachments,
  onRemove
}: {
  attachments: FileAttachment[]
  onRemove?: (id: string) => void
}) {
  if (attachments.length === 0) return null

  return (
    <div className="flex flex-wrap gap-2 p-2 bg-slate-50 rounded-lg">
      {attachments.map((file) => (
        <div
          key={file.id}
          className="relative group flex items-center gap-2 bg-white rounded-lg px-2 py-1 border text-xs"
        >
          {file.type.startsWith('image/') ? (
            <ImageIcon className="w-3 h-3 text-purple-500" />
          ) : (
            <Paperclip className="w-3 h-3 text-slate-500" />
          )}
          <span className="max-w-[100px] truncate">{file.name}</span>
          {onRemove && (
            <button
              type="button"
              onClick={() => onRemove(file.id)}
              className="opacity-0 group-hover:opacity-100 transition-opacity"
              title="移除附件"
            >
              <X className="w-3 h-3 text-slate-400 hover:text-red-500" />
            </button>
          )}
        </div>
      ))}
    </div>
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
  onToggleExpand,
  suggestions,
  soundEnabled,
  onToggleSound,
  onFeedback,
  attachments,
  onAttach,
  onRemoveAttachment,
  onNewConversation
}: {
  messages: ChatMessage[]
  input: string
  setInput: (value: string) => void
  onSend: () => void
  isLoading: boolean
  onClose: () => void
  isExpanded: boolean
  onToggleExpand: () => void
  suggestions: string[]
  soundEnabled: boolean
  onToggleSound: () => void
  onFeedback: (messageId: string, type: 'like' | 'dislike') => void
  attachments: FileAttachment[]
  onAttach: (files: FileList) => void
  onRemoveAttachment: (id: string) => void
  onNewConversation: () => void
}) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      onAttach(e.target.files)
      e.target.value = '' // Reset input
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className={cn(
        "bg-white shadow-2xl border overflow-hidden flex flex-col",
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
          <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center overflow-hidden">
            <DotLottieReact
              src="/animations/jap.lottie"
              loop
              autoplay
              style={{ width: 28, height: 28 }}
            />
          </div>
          <div>
            <h3 className="text-white font-medium text-sm">Jap仔</h3>
            <p className="text-white/70 text-xs">你嘅日本產品專家 ✨</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          {/* 聲音開關 */}
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleSound}
            className="h-8 w-8 text-white/80 hover:text-white hover:bg-white/20"
            title={soundEnabled ? "關閉聲音" : "開啟聲音"}
          >
            {soundEnabled ? (
              <Volume2 className="w-4 h-4" />
            ) : (
              <VolumeX className="w-4 h-4" />
            )}
          </Button>
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
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-100 to-pink-100 flex items-center justify-center mb-3 overflow-hidden">
              <DotLottieReact
                src="/animations/jap.lottie"
                loop
                autoplay
                style={{ width: 56, height: 56 }}
              />
            </div>
            <h4 className="font-medium text-slate-700 mb-1">Hey！我係 Jap仔 🙋‍♂️</h4>
            <p className="text-sm text-slate-500">
              有咩可以幫到你？問我啦！
            </p>
            {/* 頁面感知建議 */}
            <div className="mt-4 space-y-2 w-full">
              {suggestions.map((suggestion, i) => (
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
          messages.map((msg, index) => {
            // 計算是否為最後一條 AI 訊息
            const lastAssistantIndex = messages.findLastIndex(m => m.role === 'assistant')
            const isLastAssistantMessage = index === lastAssistantIndex

            return (
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
                  "w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 overflow-hidden",
                  msg.role === 'user'
                    ? "bg-gradient-to-br from-cyan-500 to-blue-500"
                    : "bg-gradient-to-br from-purple-500 to-pink-500"
                )}>
                  {msg.role === 'user' ? (
                    <User className="w-3.5 h-3.5 text-white" />
                  ) : (
                    <DotLottieReact
                      src="/animations/jap.lottie"
                      loop
                      autoplay
                      style={{ width: 22, height: 22 }}
                    />
                  )}
                </div>
                <div className="max-w-[80%]">
                  <div className={cn(
                    "rounded-xl px-3 py-2 text-sm",
                    msg.role === 'user'
                      ? "bg-gradient-to-br from-cyan-500 to-blue-500 text-white rounded-tr-sm"
                      : "bg-white border shadow-sm rounded-tl-sm"
                  )}>
                    {/* 附件預覽 */}
                    {msg.attachments && msg.attachments.length > 0 && (
                      <AttachmentPreview attachments={msg.attachments} />
                    )}
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
                  {/* 訊息反饋 - 只顯示在 AI 回覆 */}
                  {msg.role === 'assistant' && (
                    <MessageFeedback
                      messageId={msg.id}
                      feedback={msg.feedback}
                      onFeedback={onFeedback}
                    />
                  )}
                  {/* Follow-up Suggestions - 只顯示在最後一條 AI 訊息 */}
                  {isLastAssistantMessage &&
                   msg.role === 'assistant' &&
                   msg.suggestions &&
                   msg.suggestions.length > 0 &&
                   !isLoading && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {msg.suggestions.map((suggestion, i) => {
                        const isNewTopicButton = suggestion.text.includes('問其他嘢')
                        return (
                          <button
                            key={i}
                            type="button"
                            onClick={() => {
                              if (isNewTopicButton) {
                                onNewConversation()
                              } else {
                                setInput(suggestion.text)
                              }
                            }}
                            className={cn(
                              "flex items-center gap-1 px-2 py-1 rounded-full text-xs transition-colors",
                              isNewTopicButton
                                ? "bg-slate-100 border border-slate-300 text-slate-600 hover:bg-slate-200"
                                : "bg-purple-50 border border-purple-200 text-purple-700 hover:bg-purple-100 hover:border-purple-300"
                            )}
                          >
                            <span>{suggestion.icon}</span>
                            <span>{suggestion.text}</span>
                          </button>
                        )
                      })}
                    </div>
                  )}
                </div>
              </motion.div>
            )
          })
        )}

        {/* Loading indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-2"
          >
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center overflow-hidden">
              <DotLottieReact
                src="/animations/jap.lottie"
                loop
                autoplay
                style={{ width: 22, height: 22 }}
              />
            </div>
            <div className="bg-white border shadow-sm rounded-xl rounded-tl-sm px-3 py-2">
              <div className="flex items-center gap-1">
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce [animation-delay:0.1s]" />
                <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce [animation-delay:0.2s]" />
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 附件預覽區 */}
      {attachments.length > 0 && (
        <div className="border-t px-3 py-2">
          <AttachmentPreview attachments={attachments} onRemove={onRemoveAttachment} />
        </div>
      )}

      {/* Input */}
      <div className="border-t bg-white p-3">
        <div className="flex gap-2">
          {/* 附件按鈕 */}
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*,.pdf,.doc,.docx,.txt"
            onChange={handleFileSelect}
            className="hidden"
            title="上傳附件"
            aria-label="上傳附件"
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={() => fileInputRef.current?.click()}
            className="h-9 w-9 text-slate-500 hover:text-purple-600"
            title="上傳附件"
          >
            <Paperclip className="w-4 h-4" />
          </Button>
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && onSend()}
            placeholder="同 Jap仔 傾下計～"
            disabled={isLoading}
            className="flex-1 text-sm"
          />
          <Button
            onClick={onSend}
            disabled={(!input.trim() && attachments.length === 0) || isLoading}
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
  const [attachments, setAttachments] = useState<FileAttachment[]>([])

  // 聲音提醒
  const { soundEnabled, toggleSound, playSound } = useNotificationSound()

  // 頁面感知建議
  const suggestions = PAGE_SUGGESTIONS[pathname] || DEFAULT_SUGGESTIONS

  // 發送訊息
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
        timestamp: new Date(),
        feedback: null,
        suggestions: response.suggestions
      }

      setMessages(prev => [...prev, assistantMessage])

      // 播放聲音提醒
      playSound()

      // 如果聊天框關閉，設置未讀
      if (!isOpen) {
        setHasUnread(true)
      }
    }
  })

  const handleSend = () => {
    if ((!input.trim() && attachments.length === 0) || chatMutation.isPending) return

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
      attachments: attachments.length > 0 ? [...attachments] : undefined
    }

    setMessages(prev => [...prev, userMessage])

    // 如果有附件，將附件信息加入訊息
    let messageContent = input.trim()
    if (attachments.length > 0) {
      const attachmentNames = attachments.map(a => a.name).join(', ')
      messageContent = messageContent
        ? `${messageContent}\n\n[附件: ${attachmentNames}]`
        : `[附件: ${attachmentNames}]`
    }

    chatMutation.mutate(messageContent)
    setInput('')
    setAttachments([])
  }

  const handleOpen = () => {
    setIsOpen(true)
    setHasUnread(false)
  }

  const handleClose = () => {
    setIsOpen(false)
  }

  // 開新對話
  const handleNewConversation = () => {
    setMessages([])
    setConversationId(null)
    setInput('')
  }

  // 訊息反饋
  const handleFeedback = (messageId: string, type: 'like' | 'dislike') => {
    setMessages(prev => prev.map(msg => {
      if (msg.id === messageId) {
        return {
          ...msg,
          feedback: msg.feedback === type ? null : type
        }
      }
      return msg
    }))
    // TODO: 發送反饋到後端
    console.log(`Message ${messageId} feedback: ${type}`)
  }

  // 附件處理
  const handleAttach = (files: FileList) => {
    const newAttachments: FileAttachment[] = Array.from(files).map(file => ({
      id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
      name: file.name,
      type: file.type,
      url: URL.createObjectURL(file),
      size: file.size
    }))
    setAttachments(prev => [...prev, ...newAttachments])
  }

  const handleRemoveAttachment = (id: string) => {
    setAttachments(prev => {
      const attachment = prev.find(a => a.id === id)
      if (attachment) {
        URL.revokeObjectURL(attachment.url)
      }
      return prev.filter(a => a.id !== id)
    })
  }

  // 在 Agent 頁面不顯示此組件（避免重複）
  if (pathname === '/agent') {
    return null
  }

  return (
    <div className={cn(
      "fixed z-50 flex flex-col items-end gap-4",
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
            suggestions={suggestions}
            soundEnabled={soundEnabled}
            onToggleSound={toggleSound}
            onFeedback={handleFeedback}
            attachments={attachments}
            onAttach={handleAttach}
            onRemoveAttachment={handleRemoveAttachment}
            onNewConversation={handleNewConversation}
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
