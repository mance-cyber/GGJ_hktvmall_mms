'use client'

// =============================================
// 全局浮動聊天組items
// 右下角常駐 Chatbot button + 迷你聊天框
// Feature：Sound notification、附itemsUpload、訊息反饋、page感知、可拖曳
// =============================================

import { useState, useRef, useEffect, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { motion, AnimatePresence } from 'framer-motion'
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
// page感知suggestionsConfiguration
// =============================================

const PAGE_SUGGESTIONS: Record<string, string[]> = {
  '/': [
    '今日營業額幾多？',
    '有冇Need關注嘅Alert？',
    '最近訂單情況點樣？'
  ],
  '/dashboard': [
    '今日銷售Data點樣？',
    '邊個Product賣得最好？',
    '同上星期Compare下'
  ],
  '/products': [
    '邊個ProductNeed補貨？',
    'Price有冇競爭力？',
    'Product銷量排行榜'
  ],
  '/competitors': [
    '競爭Competitor最新Price？',
    '邊個競爭Competitor最有威脅？',
    'Price差異Analysis'
  ],
  '/alerts': [
    '有幾多個未ProcessingAlert？',
    '最緊急嘅Alert係咩？',
    'AlertTrendAnalysis'
  ],
  '/orders': [
    '今日訂單Quantity？',
    '有冇異常訂單？',
    '訂單Complete率幾多？'
  ],
  '/analytics': [
    '本月營收Trend？',
    '用戶行為Analysis',
    '轉化率點樣？'
  ]
}

const DEFAULT_SUGGESTIONS = [
  '今日訂單點樣？',
  'Compare下競爭CompetitorPrice',
  '邊個Product賣得最好？'
]

// =============================================
// Sound notification Hook
// =============================================

function useNotificationSound() {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [soundEnabled, setSoundEnabled] = useState(true)

  useEffect(() => {
    // Create audio element
    audioRef.current = new Audio('/audio/notification.mp3')
    audioRef.current.volume = 0.5

    // Read from localStorageSettings
    const saved = localStorage.getItem('chatbot-sound-enabled')
    if (saved !== null) {
      setSoundEnabled(saved === 'true')
    }
  }, [])

  const playSound = useCallback(() => {
    if (soundEnabled && audioRef.current) {
      audioRef.current.currentTime = 0
      audioRef.current.play().catch(() => {
        // Ignore autoplay restriction error
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
// 浮動button組items（可拖曳）
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
  const dotLottieInstance = useRef<any>(null)

  // Animation播放Complete後停頓 3 秒再Re-播放（使用 play API Avoid閃爍）
  const dotLottieRefCallback = useCallback((dotLottie: any) => {
    if (dotLottie) {
      dotLottieInstance.current = dotLottie
      dotLottie.addEventListener('complete', () => {
        // 停頓 3 秒後Re-播放
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
      onClick={onClick}
      className={cn(
        "w-36 h-36 flex items-center justify-center",
        "relative touch-none"
      )}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      aria-label={isOpen ? "Close聊天" : "開啟聊天"}
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

      {/* Unread指示器 */}
      {hasUnread && !isOpen && (
        <span className="absolute top-2 right-2 w-4 h-4 bg-red-500 rounded-full animate-pulse" />
      )}
    </motion.button>
  )
}

// =============================================
// 訊息反饋組items
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
        title="Need改進"
      >
        <ThumbsDown className={cn("w-3 h-3", feedback === 'dislike' ? "fill-current" : "")} />
      </button>
    </div>
  )
}

// =============================================
// 附items預覽組items
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
              title="移除附items"
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
// 迷你聊天框組items
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
      data-chat-box
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      className={cn(
        "bg-white shadow-2xl border overflow-hidden flex flex-col",
        // 手機版：全屏Display，留出Security邊距
        "fixed inset-x-2 top-16 bottom-24 rounded-xl",
        // 桌面版：浮動框
        "sm:relative sm:inset-auto sm:top-auto sm:bottom-auto",
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
            <p className="text-white/70 text-xs">你嘅日本Product專家 ✨</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          {/* 聲音開關 */}
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleSound}
            className="h-8 w-8 text-white/80 hover:text-white hover:bg-white/20"
            title={soundEnabled ? "Close聲音" : "開啟聲音"}
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
              title="Full chat page"
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
            {/* page感知suggestions */}
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
            // Calculatewhether為最後一條 AI 訊息
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
                    {/* 附items預覽 */}
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
                  {/* Message feedback - shown only on AI replies */}
                  {msg.role === 'assistant' && (
                    <MessageFeedback
                      messageId={msg.id}
                      feedback={msg.feedback}
                      onFeedback={onFeedback}
                    />
                  )}
                  {/* Follow-up Suggestions - 只Display在最後一條 AI 訊息 */}
                  {isLastAssistantMessage &&
                   msg.role === 'assistant' &&
                   msg.suggestions &&
                   msg.suggestions.length > 0 &&
                   !isLoading && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {msg.suggestions.map((suggestion, i) => {
                        const isNewTopicButton = suggestion.text.includes('Ask something else')
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

      {/* 附items預覽區 */}
      {attachments.length > 0 && (
        <div className="border-t px-3 py-2">
          <AttachmentPreview attachments={attachments} onRemove={onRemoveAttachment} />
        </div>
      )}

      {/* Input */}
      <div className="border-t bg-white p-3">
        <div className="flex gap-2">
          {/* 附itemsbutton */}
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept="image/*,.pdf,.doc,.docx,.txt"
            onChange={handleFileSelect}
            className="hidden"
            title="Upload附items"
            aria-label="Upload附items"
          />
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={() => fileInputRef.current?.click()}
            className="h-9 w-9 text-slate-500 hover:text-purple-600"
            title="Upload附items"
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
// 主組items
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

  // 拖曳State — Manual pointer event, stops on release, zero inertia
  const containerRef = useRef<HTMLDivElement>(null)
  const isDragging = useRef(false)
  const [isDraggingState, setIsDraggingState] = useState(false) // for cursor re-render
  const dragStart = useRef({ x: 0, y: 0, right: 0, bottom: 0 })
  const [position, setPosition] = useState({ right: 16, bottom: 96 }) // 對應 right-4 bottom-24

  // 桌面版初始位置調整
  useEffect(() => {
    const isDesktop = window.matchMedia('(min-width: 640px)').matches
    if (isDesktop) {
      setPosition({ right: 24, bottom: 80 }) // sm:right-6 sm:bottom-20
    }
  }, [])

  const handlePointerDown = useCallback((e: React.PointerEvent) => {
    // 唔好Intercept input/button/a 嘅 click
    const tag = (e.target as HTMLElement).tagName.toLowerCase()
    if (['input', 'button', 'a', 'textarea'].includes(tag)) return
    // 也唔好Intercept chat box 入面嘅Operation
    const chatBox = (e.target as HTMLElement).closest('[data-chat-box]')
    if (chatBox) return

    isDragging.current = false
    dragStart.current = {
      x: e.clientX,
      y: e.clientY,
      right: position.right,
      bottom: position.bottom
    }
    const el = e.currentTarget as HTMLElement
    el.setPointerCapture(e.pointerId)
  }, [position])

  const handlePointerMove = useCallback((e: React.PointerEvent) => {
    if (!e.currentTarget.hasPointerCapture(e.pointerId)) return
    const dx = e.clientX - dragStart.current.x
    const dy = e.clientY - dragStart.current.y

    // Treat as drag after moving >5px (avoid accidental clicks)
    if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
      if (!isDragging.current) {
        isDragging.current = true
        setIsDraggingState(true)
      }
    }

    if (isDragging.current) {
      // right 同 bottom 係反方向
      const newRight = Math.max(0, dragStart.current.right - dx)
      const newBottom = Math.max(0, dragStart.current.bottom - dy)
      // Limit唔好拖出畫面
      const maxRight = window.innerWidth - 80
      const maxBottom = window.innerHeight - 80
      setPosition({
        right: Math.min(newRight, maxRight),
        bottom: Math.min(newBottom, maxBottom)
      })
    }
  }, [])

  const handlePointerUp = useCallback((e: React.PointerEvent) => {
    const el = e.currentTarget as HTMLElement
    if (el.hasPointerCapture(e.pointerId)) {
      el.releasePointerCapture(e.pointerId)
    }
    // Delay reset isDragging, let onClick decide
    setIsDraggingState(false)
    setTimeout(() => { isDragging.current = false }, 50)
  }, [])

  // Sound notification
  const { soundEnabled, toggleSound, playSound } = useNotificationSound()

  // page感知suggestions
  const suggestions = PAGE_SUGGESTIONS[pathname] || DEFAULT_SUGGESTIONS

  // Send message
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

      // 播放Sound notification
      playSound()

      // 如果聊天框Close，Set upUnread
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

    // If attachments present, add attachment info to message
    let messageContent = input.trim()
    if (attachments.length > 0) {
      const attachmentNames = attachments.map(a => a.name).join(', ')
      messageContent = messageContent
        ? `${messageContent}\n\n[附items: ${attachmentNames}]`
        : `[附items: ${attachmentNames}]`
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

  // 開New conversation
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
    // TODO: 發送反饋到Backend
    console.log(`Message ${messageId} feedback: ${type}`)
  }

  // 附itemsProcessing
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

  // 在 Agent page不Display此組items（Avoid重複）
  if (pathname === '/agent') {
    return null
  }

  return (
    <div
      ref={containerRef}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      style={{ right: position.right, bottom: position.bottom }}
      className={cn(
        "fixed z-50 flex flex-col items-end gap-4 touch-none",
        isDraggingState ? "cursor-grabbing" : "cursor-grab"
      )}
    >
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
        onClick={() => { if (!isDragging.current) { isOpen ? handleClose() : handleOpen() } }}
        hasUnread={hasUnread}
      />
    </div>
  )
}
