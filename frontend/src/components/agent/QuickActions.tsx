'use client'

// =============================================
// 快捷操作組件 - 常用問題快捷入口
// =============================================

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Package,
  DollarSign,
  Bell,
  TrendingUp,
  Store,
  ChevronDown,
  ChevronUp,
  Zap,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

// =============================================
// Types
// =============================================

interface QuickAction {
  id: string
  label: string
  query: string
  icon: React.ReactNode
  color: string
}

interface QuickActionsProps {
  onAction: (query: string) => void
  disabled?: boolean
}

// =============================================
// Quick Actions Data
// =============================================

const QUICK_ACTIONS: QuickAction[] = [
  {
    id: 'orders',
    label: '今日訂單',
    query: '今日有幾多單未處理？',
    icon: <Package className="w-4 h-4" />,
    color: 'from-blue-500 to-cyan-500',
  },
  {
    id: 'revenue',
    label: '本月營收',
    query: '本月營收係幾多？',
    icon: <DollarSign className="w-4 h-4" />,
    color: 'from-green-500 to-emerald-500',
  },
  {
    id: 'alerts',
    label: '查警報',
    query: '有咩價格警報？',
    icon: <Bell className="w-4 h-4" />,
    color: 'from-amber-500 to-orange-500',
  },
  {
    id: 'trends',
    label: '價格趨勢',
    query: '分析和牛嘅價格趨勢',
    icon: <TrendingUp className="w-4 h-4" />,
    color: 'from-purple-500 to-pink-500',
  },
  {
    id: 'competitors',
    label: '競爭分析',
    query: '同百佳比較日本零食價格',
    icon: <Store className="w-4 h-4" />,
    color: 'from-red-500 to-rose-500',
  },
]

// =============================================
// Main Component
// =============================================

export function QuickActions({ onAction, disabled }: QuickActionsProps) {
  const [isExpanded, setIsExpanded] = useState(true)

  return (
    <div className="border-t bg-slate-50/80 backdrop-blur-sm">
      {/* Toggle Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-2 flex items-center justify-between text-sm text-slate-500 hover:text-slate-700 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4" />
          <span>快捷操作</span>
        </div>
        {isExpanded ? (
          <ChevronDown className="w-4 h-4" />
        ) : (
          <ChevronUp className="w-4 h-4" />
        )}
      </button>

      {/* Actions Grid */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-3 flex gap-2 overflow-x-auto scrollbar-hide sm:flex-wrap">
              {QUICK_ACTIONS.map((action) => (
                <motion.button
                  key={action.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => onAction(action.query)}
                  disabled={disabled}
                  className={cn(
                    "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium",
                    "text-white shadow-sm transition-all whitespace-nowrap flex-shrink-0",
                    "disabled:opacity-50 disabled:cursor-not-allowed",
                    `bg-gradient-to-r ${action.color}`,
                    "hover:shadow-md"
                  )}
                >
                  {action.icon}
                  {action.label}
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default QuickActions
