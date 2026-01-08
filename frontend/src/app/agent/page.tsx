'use client'

import { useState, useRef, useEffect } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { api, AgentChatResponse, AgentSlotOption } from '@/lib/api'
import { motion, AnimatePresence } from 'framer-motion'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  Send,
  Bot,
  User,
  Loader2,
  Sparkles,
  BarChart3,
  TrendingUp,
  Users,
  FileText,
  ChevronRight,
  Check,
  Copy,
  Download,
  RefreshCw,
  MessageSquare,
  Zap,
  Plus,
  Menu,
  Clock
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import {
  Sheet,
  SheetContent,
  SheetTrigger,
} from "@/components/ui/sheet"
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'

// =============================================
// Types
// =============================================

interface Message {
  id: string
  role: 'user' | 'assistant'
  type: 'message' | 'clarification' | 'report' | 'thinking'
  content: string
  options?: AgentSlotOption[]
  charts?: any[]
  timestamp: Date
}

interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
}

// =============================================
// Sidebar Component
// =============================================

function ConversationList({
  conversations,
  currentId,
  onSelect,
  onNew,
  formatDate
}: {
  conversations: Conversation[]
  currentId: string | null
  onSelect: (id: string) => void
  onNew: () => void
  formatDate: (date: string) => string
}) {
  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b">
        <Button onClick={onNew} className="w-full gap-2 bg-purple-600 hover:bg-purple-700 text-white shadow-sm">
          <Plus className="w-4 h-4" />
          新對話
        </Button>
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {conversations.length === 0 ? (
          <div className="text-center text-slate-400 py-8 text-sm">
            暫無歷史對話
          </div>
        ) : (
          conversations.map((conv) => (
            <button
              key={conv.id}
              onClick={() => onSelect(conv.id)}
              className={cn(
                "w-full text-left px-3 py-2.5 rounded-lg transition-all text-sm",
                "hover:bg-slate-100",
                currentId === conv.id 
                  ? "bg-purple-50 border border-purple-200 text-purple-700" 
                  : "text-slate-600"
              )}
            >
              <div className="flex items-start gap-2">
                <MessageSquare className="w-4 h-4 mt-0.5 flex-shrink-0 opacity-60" />
                <div className="flex-1 min-w-0">
                  <div className="font-medium truncate">{conv.title || '新對話'}</div>
                  <div className="flex items-center gap-1 text-xs text-slate-400 mt-0.5">
                    <Clock className="w-3 h-3" />
                    {formatDate(conv.created_at)}
                  </div>
                </div>
              </div>
            </button>
          ))
        )}
      </div>
    </div>
  )
}

// =============================================
// Chart Components
// =============================================

function ChartRenderer({ chart }: { chart: any }) {
  if (!chart || !chart.data) return null

  const colors = ['#8b5cf6', '#06b6d4', '#f59e0b', '#ef4444', '#22c55e']

  if (chart.type === 'line') {
    return (
      <div className="bg-white rounded-lg p-4 border">
        <h4 className="font-medium text-slate-700 mb-3">{chart.title}</h4>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chart.data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey={chart.xKey || 'name'} tick={{ fontSize: 12 }} stroke="#94a3b8" />
            <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
            <Tooltip />
            <Legend />
            {(chart.lines || ['value']).map((line: string, i: number) => (
              <Line 
                key={line} 
                type="monotone" 
                dataKey={line} 
                stroke={colors[i % colors.length]} 
                strokeWidth={2}
                dot={{ fill: colors[i % colors.length] }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    )
  }

  if (chart.type === 'bar') {
    return (
      <div className="bg-white rounded-lg p-4 border">
        <h4 className="font-medium text-slate-700 mb-3">{chart.title}</h4>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={chart.data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey={chart.xKey || 'name'} tick={{ fontSize: 12 }} stroke="#94a3b8" />
            <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
            <Tooltip />
            <Legend />
            {(chart.bars || ['value']).map((bar: string, i: number) => (
              <Bar 
                key={bar} 
                dataKey={bar} 
                fill={colors[i % colors.length]} 
                radius={[4, 4, 0, 0]}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  }

  return null
}

// =============================================
// Message Components
// =============================================

function ThinkingMessage() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex gap-3"
    >
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
        <Bot className="w-4 h-4 text-white" />
      </div>
      <div className="bg-white rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm border flex items-center gap-2">
        <Loader2 className="w-4 h-4 animate-spin text-purple-500" />
        <span className="text-slate-500">分析緊你嘅問題...</span>
      </div>
    </motion.div>
  )
}

function ClarificationCard({
  options,
  selections,
  onSelect,
  onSubmit,
  isLoading
}: {
  options: AgentSlotOption[]
  selections: Record<string, string | string[]>
  onSelect: (slot: string, value: string, type: 'single' | 'multi') => void
  onSubmit: () => void
  isLoading: boolean
}) {
  const allRequired = options.every(opt => {
    const sel = selections[opt.slot_name]
    if (opt.type === 'multi') {
      return Array.isArray(sel) && sel.length > 0
    }
    return !!sel
  })

  return (
    <div className="bg-white rounded-xl border shadow-sm p-4 space-y-4">
      {options.map((opt) => (
        <div key={opt.slot_name} className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="font-medium text-slate-700">{opt.label}</span>
            {opt.type === 'multi' && (
              <span className="text-xs text-slate-400">(可多選)</span>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {opt.options.map((option) => {
              const isSelected = opt.type === 'multi'
                ? (selections[opt.slot_name] as string[] || []).includes(option.value)
                : selections[opt.slot_name] === option.value

              return (
                <button
                  key={option.value}
                  onClick={() => onSelect(opt.slot_name, option.value, opt.type as 'single' | 'multi')}
                  className={cn(
                    "px-3 py-1.5 rounded-full text-sm font-medium transition-all",
                    "border",
                    isSelected
                      ? "bg-purple-100 border-purple-300 text-purple-700"
                      : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                  )}
                >
                  {isSelected && <Check className="w-3 h-3 inline mr-1" />}
                  {option.label}
                </button>
              )
            })}
          </div>
        </div>
      ))}
      <Button
        onClick={onSubmit}
        disabled={!allRequired || isLoading}
        className="w-full bg-purple-600 hover:bg-purple-700"
      >
        {isLoading ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            處理中...
          </>
        ) : (
          <>
            <Check className="w-4 h-4 mr-2" />
            確認選擇
          </>
        )}
      </Button>
    </div>
  )
}

function MessageBubble({ message }: { message: Message }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (message.type === 'thinking') {
    return <ThinkingMessage />
  }

  const isUser = message.role === 'user'

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("flex gap-3", isUser && "flex-row-reverse")}
    >
      <div className={cn(
        "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
        isUser 
          ? "bg-gradient-to-br from-cyan-500 to-blue-500" 
          : "bg-gradient-to-br from-purple-500 to-pink-500"
      )}>
        {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
      </div>
      <div className={cn(
        "max-w-[80%] rounded-2xl px-4 py-3 shadow-sm",
        isUser 
          ? "bg-gradient-to-br from-cyan-500 to-blue-500 text-white rounded-tr-sm" 
          : "bg-white border rounded-tl-sm"
      )}>
        <div className={cn(
          "prose prose-sm max-w-none",
          isUser && "prose-invert"
        )}>
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>
        </div>
        {!isUser && message.content && (
          <button
            onClick={handleCopy}
            className="mt-2 text-xs text-slate-400 hover:text-slate-600 flex items-center gap-1"
          >
            {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
            {copied ? '已複製' : '複製'}
          </button>
        )}
      </div>
    </motion.div>
  )
}

// =============================================
// Main Page Component
// =============================================

export default function AgentPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [pendingClarification, setPendingClarification] = useState<Message | null>(null)
  const [selections, setSelections] = useState<Record<string, string | string[]>>({})
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 獲取建議
  const { data: suggestionsData } = useQuery({
    queryKey: ['agent-suggestions'],
    queryFn: () => api.getAgentSuggestions(),
  })

  // 獲取歷史對話
  const { data: historyData, refetch: refetchHistory } = useQuery({
    queryKey: ['agent-history'],
    queryFn: () => api.getAgentConversations(),
  })

  // 加載歷史對話
  const loadConversation = async (id: string) => {
    if (id === conversationId) return
    
    setConversationId(id)
    setIsSidebarOpen(false)
    setMessages([])
    setPendingClarification(null)
    
    try {
      const state = await api.getAgentConversation(id)
      const mappedMessages: Message[] = state.messages.map((m: any, index: number) => ({
        id: `hist-${index}`,
        role: m.role as 'user' | 'assistant',
        type: (m.metadata?.type || 'message') as any,
        content: m.content,
        options: m.metadata?.options,
        charts: m.metadata?.charts,
        timestamp: new Date(m.timestamp)
      }))
      setMessages(mappedMessages)
      
      const lastMsg = mappedMessages[mappedMessages.length - 1]
      if (lastMsg && lastMsg.type === 'clarification') {
        setPendingClarification(lastMsg)
        setSelections({})
      }
    } catch (e) {
      console.error("Failed to load conversation", e)
    }
  }

  // 發送訊息
  const chatMutation = useMutation({
    mutationFn: (content: string) => api.agentChat({
      content,
      conversation_id: conversationId || undefined
    }),
    onSuccess: (response) => {
      setMessages(prev => prev.filter(m => m.type !== 'thinking'))
      
      if (!conversationId) {
        setConversationId(response.conversation_id)
        refetchHistory()
      }
      
      const newMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        type: response.type as any,
        content: response.content,
        options: response.options,
        charts: response.charts,
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, newMessage])
      
      if (response.type === 'clarification') {
        setPendingClarification(newMessage)
        setSelections({})
      } else {
        setPendingClarification(null)
      }
    }
  })

  // 發送澄清回應
  const clarifyMutation = useMutation({
    mutationFn: () => api.agentClarify({
      conversation_id: conversationId!,
      selections
    }),
    onSuccess: (response) => {
      setMessages(prev => prev.filter(m => m.type !== 'thinking'))
      
      const newMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        type: response.type as any,
        content: response.content,
        options: response.options,
        charts: response.charts,
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, newMessage])
      
      if (response.type === 'clarification') {
        setPendingClarification(newMessage)
        setSelections({})
      } else {
        setPendingClarification(null)
      }
    }
  })

  const handleSend = () => {
    if (!input.trim() || chatMutation.isPending) return
    
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      type: 'message',
      content: input.trim(),
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, userMessage])
    
    const thinkingMessage: Message = {
      id: 'thinking',
      role: 'assistant',
      type: 'thinking',
      content: '分析緊你嘅問題...',
      timestamp: new Date()
    }
    setMessages(prev => [...prev, thinkingMessage])
    
    chatMutation.mutate(input.trim())
    setInput('')
  }

  const handleSuggestionClick = (text: string) => {
    setInput(text)
  }

  const handleSelect = (slotName: string, value: string, type: 'single' | 'multi') => {
    if (type === 'single') {
      setSelections(prev => ({ ...prev, [slotName]: value }))
    } else {
      setSelections(prev => {
        const current = (prev[slotName] as string[]) || []
        if (current.includes(value)) {
          return { ...prev, [slotName]: current.filter(v => v !== value) }
        }
        return { ...prev, [slotName]: [...current, value] }
      })
    }
  }

  const handleClarifySubmit = () => {
    if (clarifyMutation.isPending) return
    
    const selectionText = Object.entries(selections)
      .map(([key, value]) => {
        const arr = Array.isArray(value) ? value : [value]
        return arr.join(', ')
      })
      .join('; ')
    
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      type: 'message',
      content: selectionText || '確認',
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    
    const thinkingMessage: Message = {
      id: 'thinking',
      role: 'assistant',
      type: 'thinking',
      content: '查詢緊數據...',
      timestamp: new Date()
    }
    setMessages(prev => [...prev, thinkingMessage])
    
    clarifyMutation.mutate()
  }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleNewConversation = () => {
    setMessages([])
    setConversationId(null)
    setPendingClarification(null)
    setSelections({})
    setIsSidebarOpen(false)
  }

  const isLoading = chatMutation.isPending || clarifyMutation.isPending

  const formatDate = (dateStr: string) => {
    try {
      const date = new Date(dateStr)
      return date.toLocaleString('zh-HK', { 
        year: 'numeric',
        month: '2-digit', 
        day: '2-digit', 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    } catch {
      return dateStr
    }
  }

  const conversations: Conversation[] = historyData?.conversations || []

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-slate-50 overflow-hidden">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex w-72 flex-col border-r bg-white shadow-sm z-10">
        <ConversationList
          conversations={conversations}
          currentId={conversationId}
          onSelect={loadConversation}
          onNew={handleNewConversation}
          formatDate={formatDate}
        />
      </div>

      {/* Mobile Sidebar (Sheet) */}
      <Sheet open={isSidebarOpen} onOpenChange={setIsSidebarOpen}>
        <SheetContent side="left" className="w-72 p-0">
          <ConversationList
            conversations={conversations}
            currentId={conversationId}
            onSelect={loadConversation}
            onNew={handleNewConversation}
            formatDate={formatDate}
          />
        </SheetContent>
      </Sheet>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile Header */}
        <div className="md:hidden flex items-center gap-2 p-3 border-b bg-white">
          <Button 
            variant="ghost" 
            size="icon"
            onClick={() => setIsSidebarOpen(true)}
          >
            <Menu className="w-5 h-5" />
          </Button>
          <span className="font-medium text-slate-700">AI 助手</span>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center px-4">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-4 shadow-lg">
                <Sparkles className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-xl font-semibold text-slate-700 mb-2">
                我係你嘅 AI 助手
              </h2>
              <p className="text-slate-500 mb-6 max-w-md">
                我可以幫你分析產品數據、比較競爭對手價格、生成市場報告
              </p>
              
              {/* Suggestions */}
              {suggestionsData?.suggestions && suggestionsData.suggestions.length > 0 && (
                <div className="w-full max-w-lg space-y-2">
                  <p className="text-sm text-slate-400 mb-3">試下呢啲問題：</p>
                  <div className="grid gap-2">
                    {suggestionsData.suggestions.slice(0, 4).map((suggestion, i) => (
                      <button
                        key={i}
                        onClick={() => handleSuggestionClick(suggestion.text)}
                        className="flex items-center gap-3 p-3 bg-white rounded-xl border hover:border-purple-300 hover:shadow-sm transition-all text-left group"
                      >
                        <div className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center group-hover:bg-purple-200 transition-colors">
                          {suggestion.category === 'price' && <BarChart3 className="w-4 h-4 text-purple-600" />}
                          {suggestion.category === 'trend' && <TrendingUp className="w-4 h-4 text-purple-600" />}
                          {suggestion.category === 'competitor' && <Users className="w-4 h-4 text-purple-600" />}
                          {suggestion.category === 'report' && <FileText className="w-4 h-4 text-purple-600" />}
                          {!['price', 'trend', 'competitor', 'report'].includes(suggestion.category) && <Zap className="w-4 h-4 text-purple-600" />}
                        </div>
                        <span className="flex-1 text-sm text-slate-600">{suggestion.text}</span>
                        <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-purple-400 transition-colors" />
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <AnimatePresence>
              {messages.map((message) => (
                <div key={message.id}>
                  <MessageBubble message={message} />
                  
                  {/* Charts */}
                  {message.charts && message.charts.length > 0 && (
                    <div className="ml-11 mt-3 space-y-3">
                      {message.charts.map((chart, i) => (
                        <ChartRenderer key={i} chart={chart} />
                      ))}
                    </div>
                  )}
                  
                  {/* Clarification Card */}
                  {message.type === 'clarification' && 
                   message.options && 
                   pendingClarification?.id === message.id && (
                    <div className="ml-11 mt-3">
                      <ClarificationCard
                        options={message.options}
                        selections={selections}
                        onSelect={handleSelect}
                        onSubmit={handleClarifySubmit}
                        isLoading={isLoading}
                      />
                    </div>
                  )}
                </div>
              ))}
            </AnimatePresence>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="border-t bg-white p-4">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
                placeholder="輸入你嘅問題..."
                disabled={isLoading || !!pendingClarification}
                className="flex-1"
              />
              <Button
                onClick={handleSend}
                disabled={!input.trim() || isLoading || !!pendingClarification}
                className="bg-purple-600 hover:bg-purple-700"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </div>
            {pendingClarification && (
              <p className="text-xs text-amber-600 mt-2 text-center">
                請先完成上面嘅選擇
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
