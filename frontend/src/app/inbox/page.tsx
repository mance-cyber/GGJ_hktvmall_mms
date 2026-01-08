'use client'

import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { inboxApi, Conversation, Message } from '@/lib/api'
import { cn } from '@/lib/utils'
import { format } from 'date-fns'
import { RefreshCw, Send, User, Bot, MessageSquare } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useToast } from '@/components/ui/use-toast'

export default function InboxPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [inputText, setInputText] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Fetch Conversations
  const { data: conversations, isLoading: loadingConvs } = useQuery({
    queryKey: ['conversations'],
    queryFn: () => inboxApi.getConversations(),
  })

  // Fetch Messages for selected
  const { data: messages, isLoading: loadingMsgs } = useQuery({
    queryKey: ['messages', selectedId],
    queryFn: () => selectedId ? inboxApi.getMessages(selectedId) : Promise.resolve([]),
    enabled: !!selectedId,
    refetchInterval: 5000, // Poll for new messages
  })

  // Scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Sync Mutation
  const syncMutation = useMutation({
    mutationFn: () => inboxApi.sync(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['conversations'] })
      toast({ title: `同步完成`, description: `更新了 ${data.synced_count} 個對話` })
    }
  })

  // Send Mutation
  const sendMutation = useMutation({
    mutationFn: (content: string) => inboxApi.sendMessage(selectedId!, content),
    onSuccess: () => {
      setInputText('')
      queryClient.invalidateQueries({ queryKey: ['messages', selectedId] })
    }
  })

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputText.trim() || !selectedId) return
    sendMutation.mutate(inputText)
  }

  const selectedConv = conversations?.find(c => c.id === selectedId)

  return (
    <div className="h-[calc(100vh-120px)] flex flex-col animate-fade-in-up">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <MessageSquare className="w-6 h-6 text-primary" />
          客服收件箱 (Beta)
        </h1>
        <Button variant="outline" size="sm" onClick={() => syncMutation.mutate()} disabled={syncMutation.isPending}>
          <RefreshCw className={cn("w-4 h-4 mr-2", syncMutation.isPending && "animate-spin")} />
          同步訊息
        </Button>
      </div>

      <div className="flex-1 glass-panel rounded-xl border border-white/40 overflow-hidden flex shadow-lg">
        {/* Sidebar: Conversation List */}
        <div className="w-80 border-r border-slate-100 bg-white/50 flex flex-col">
          <div className="p-4 border-b border-slate-100">
            <Input placeholder="搜尋對話..." className="bg-white" />
          </div>
          <div className="flex-1 overflow-y-auto">
            {loadingConvs ? (
              <div className="p-4 text-center text-slate-400">載入中...</div>
            ) : conversations?.length === 0 ? (
              <div className="p-8 text-center text-slate-400">暫無對話</div>
            ) : (
              conversations?.map(conv => (
                <div
                  key={conv.id}
                  onClick={() => setSelectedId(conv.id)}
                  className={cn(
                    "p-4 border-b border-slate-50 cursor-pointer hover:bg-slate-50 transition-colors",
                    selectedId === conv.id && "bg-blue-50/50 border-l-4 border-l-blue-500"
                  )}
                >
                  <div className="flex justify-between items-start mb-1">
                    <span className="font-semibold text-slate-800 line-clamp-1">{conv.customer_name}</span>
                    <span className="text-[10px] text-slate-400">
                      {format(new Date(conv.last_message_at), 'MM-dd HH:mm')}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 line-clamp-1 mb-1">{conv.subject}</p>
                  <span className={cn(
                    "inline-block px-1.5 py-0.5 rounded text-[10px]",
                    conv.status === 'open' ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-600"
                  )}>
                    {conv.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Main: Chat Area */}
        <div className="flex-1 flex flex-col bg-white/30">
          {selectedId ? (
            <>
              {/* Header */}
              <div className="p-4 border-b border-slate-100 bg-white/60 backdrop-blur-sm flex justify-between items-center">
                <div>
                  <h2 className="font-bold text-slate-800">{selectedConv?.customer_name}</h2>
                  <p className="text-xs text-slate-500">{selectedConv?.subject}</p>
                </div>
                {/* AI Toggle could go here */}
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages?.map((msg) => {
                  const isMe = msg.sender_type === 'merchant'
                  return (
                    <div key={msg.id} className={cn("flex", isMe ? "justify-end" : "justify-start")}>
                      <div className={cn(
                        "max-w-[70%] rounded-2xl p-3 shadow-sm",
                        isMe ? "bg-blue-600 text-white rounded-tr-none" : "bg-white border border-slate-100 rounded-tl-none"
                      )}>
                        <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                        <div className={cn("text-[10px] mt-1 text-right", isMe ? "text-blue-200" : "text-slate-400")}>
                          {format(new Date(msg.sent_at), 'HH:mm')}
                        </div>
                      </div>
                    </div>
                  )
                })}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="p-4 bg-white border-t border-slate-100">
                <form onSubmit={handleSend} className="flex gap-2">
                  <Input 
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="輸入回覆..."
                    className="flex-1"
                    autoFocus
                  />
                  <Button type="submit" disabled={sendMutation.isPending || !inputText.trim()}>
                    <Send className="w-4 h-4" />
                  </Button>
                </form>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-400">
              <MessageSquare className="w-16 h-16 mb-4 opacity-20" />
              <p>選擇一個對話開始</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
