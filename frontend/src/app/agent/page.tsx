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
  
  // Extract config with fallbacks
  const config = chart.config || {}
  const xKey = config.xKey || chart.xKey || 'name'
  
  // Handle yKeys (support both simple string array or object array)
  let series = []
  if (config.yKeys) {
    series = config.yKeys
  } else if (chart.lines) {
    series = chart.lines.map((key: string) => ({ key, name: key }))
  } else if (chart.bars) {
    series = chart.bars.map((key: string) => ({ key, name: key }))
  } else {
    // Default fallback
    series = [{ key: 'value', name: '數值' }]
  }

  if (chart.type === 'line') {
    return (
      <div className="bg-white rounded-lg p-4 border">
        <h4 className="font-medium text-slate-700 mb-3">{chart.title}</h4>
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={chart.data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey={xKey} tick={{ fontSize: 12 }} stroke="#94a3b8" />
            <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
            <Tooltip />
            <Legend />
            {series.map((s: any, i: number) => (
              <Line 
                key={s.key} 
                type="monotone" 
                dataKey={s.key} 
                name={s.name || s.key}
                stroke={s.color || colors[i % colors.length]} 
                strokeWidth={2}
                dot={{ fill: s.color || colors[i % colors.length] }}
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
            <XAxis dataKey={xKey} tick={{ fontSize: 12 }} stroke="#94a3b8" />
            <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
            <Tooltip />
            <Legend />
            {series.map((s: any, i: number) => (
              <Bar 
                key={s.key} 
                dataKey={s.key} 
                name={s.name || s.key}
                fill={s.color || colors[i % colors.length]} 
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
                  onClick={()
