'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { 
  Activity, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Loader2,
  ChevronRight,
  Building2,
  Package
} from 'lucide-react'
import { cn } from '@/lib/utils'

// =============================================
// 類型定義
// =============================================

export type TaskStatus = 'pending' | 'running' | 'success' | 'failed'

export interface ScrapeTask {
  id: string
  name: string           // 競爭對手或類別名稱
  type: 'competitor' | 'category' | 'product'
  status: TaskStatus
  progress?: number      // 0-100
  startedAt?: string
  completedAt?: string
  error?: string
  productCount?: number  // 抓取的商品數量
}

interface ScrapeTaskQueueProps {
  tasks: ScrapeTask[]
  className?: string
  showHeader?: boolean
  maxVisible?: number
  compact?: boolean
}

// =============================================
// 主組件
// =============================================

export function ScrapeTaskQueue({ 
  tasks, 
  className,
  showHeader = true,
  maxVisible = 5,
  compact = false
}: ScrapeTaskQueueProps) {
  const runningTasks = tasks.filter(t => t.status === 'running')
  const pendingTasks = tasks.filter(t => t.status === 'pending')
  const completedTasks = tasks.filter(t => t.status === 'success' || t.status === 'failed')
  
  // 顯示的任務：正在運行 + 等待中 + 最近完成的
  const visibleTasks = [
    ...runningTasks,
    ...pendingTasks,
    ...completedTasks.slice(0, maxVisible - runningTasks.length - pendingTasks.length)
  ].slice(0, maxVisible)

  if (tasks.length === 0) {
    return null
  }

  return (
    <div className={cn("space-y-3", className)}>
      {showHeader && (
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-700 flex items-center">
            <Activity className="w-4 h-4 mr-2 text-blue-500" />
            抓取任務隊列
          </h3>
          <div className="flex items-center space-x-2 text-xs">
            {runningTasks.length > 0 && (
              <span className="flex items-center text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
                <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                {runningTasks.length} 進行中
              </span>
            )}
            {pendingTasks.length > 0 && (
              <span className="flex items-center text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                <Clock className="w-3 h-3 mr-1" />
                {pendingTasks.length} 等待中
              </span>
            )}
          </div>
        </div>
      )}

      <div className="space-y-2">
        <AnimatePresence mode="popLayout">
          {visibleTasks.map((task, index) => (
            <TaskItem 
              key={task.id} 
              task={task} 
              index={index}
              compact={compact}
            />
          ))}
        </AnimatePresence>
      </div>

      {/* 顯示更多提示 */}
      {tasks.length > maxVisible && (
        <div className="text-xs text-slate-400 text-center py-1">
          還有 {tasks.length - maxVisible} 個任務...
        </div>
      )}
    </div>
  )
}

// =============================================
// 任務項組件
// =============================================

function TaskItem({ 
  task, 
  index,
  compact 
}: { 
  task: ScrapeTask
  index: number
  compact: boolean
}) {
  const statusConfig = {
    pending: {
      icon: Clock,
      iconClass: 'text-slate-400',
      bgClass: 'bg-slate-50 border-slate-200',
      label: '等待中'
    },
    running: {
      icon: Loader2,
      iconClass: 'text-blue-500 animate-spin',
      bgClass: 'bg-blue-50/50 border-blue-200',
      label: '抓取中'
    },
    success: {
      icon: CheckCircle2,
      iconClass: 'text-green-500',
      bgClass: 'bg-green-50/50 border-green-200',
      label: '已完成'
    },
    failed: {
      icon: XCircle,
      iconClass: 'text-red-500',
      bgClass: 'bg-red-50/50 border-red-200',
      label: '失敗'
    }
  }

  const config = statusConfig[task.status]
  const Icon = config.icon
  const TypeIcon = task.type === 'competitor' ? Building2 : Package

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: -10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95, x: 20 }}
      transition={{ 
        duration: 0.2, 
        delay: index * 0.05,
        layout: { duration: 0.2 }
      }}
      className={cn(
        "relative rounded-lg border transition-all overflow-hidden",
        config.bgClass,
        compact ? "p-2" : "p-3"
      )}
    >
      {/* 進度條背景 */}
      {task.status === 'running' && task.progress !== undefined && (
        <motion.div
          className="absolute inset-0 bg-blue-500/10"
          initial={{ width: 0 }}
          animate={{ width: `${task.progress}%` }}
          transition={{ duration: 0.3 }}
        />
      )}

      <div className="relative flex items-center space-x-3">
        {/* 類型圖標 */}
        <div className={cn(
          "flex-shrink-0 rounded-lg flex items-center justify-center",
          compact ? "w-8 h-8 bg-white/80" : "w-10 h-10 bg-white shadow-sm"
        )}>
          <TypeIcon className={cn("text-slate-400", compact ? "w-4 h-4" : "w-5 h-5")} />
        </div>

        {/* 任務信息 */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2">
            <h4 className={cn(
              "font-medium text-slate-800 truncate",
              compact ? "text-xs" : "text-sm"
            )}>
              {task.name}
            </h4>
            {task.status === 'running' && task.progress !== undefined && (
              <span className="text-xs text-blue-600 font-mono bg-white/80 px-1.5 py-0.5 rounded">
                {task.progress.toFixed(0)}%
              </span>
            )}
          </div>
          
          {!compact && (
            <div className="flex items-center space-x-2 mt-0.5">
              <span className={cn("text-xs flex items-center", config.iconClass)}>
                <Icon className="w-3 h-3 mr-1" />
                {config.label}
              </span>
              {task.productCount !== undefined && task.status === 'success' && (
                <span className="text-xs text-slate-400">
                  · {task.productCount} 商品
                </span>
              )}
              {task.error && (
                <span className="text-xs text-red-500 truncate max-w-[150px]">
                  · {task.error}
                </span>
              )}
            </div>
          )}
        </div>

        {/* 狀態圖標 */}
        <div className="flex-shrink-0">
          <Icon className={cn(config.iconClass, compact ? "w-4 h-4" : "w-5 h-5")} />
        </div>
      </div>

      {/* 運行中的脈動效果 */}
      {task.status === 'running' && (
        <motion.div
          className="absolute inset-0 border-2 border-blue-400 rounded-lg"
          animate={{ opacity: [0.5, 0, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}
    </motion.div>
  )
}

// =============================================
// 輔助組件：迷你任務指示器
// =============================================

export function ScrapeTaskIndicator({ 
  tasks,
  onClick
}: { 
  tasks: ScrapeTask[]
  onClick?: () => void
}) {
  const runningCount = tasks.filter(t => t.status === 'running').length
  const pendingCount = tasks.filter(t => t.status === 'pending').length
  const hasActive = runningCount > 0 || pendingCount > 0

  if (!hasActive) return null

  return (
    <motion.button
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      onClick={onClick}
      className={cn(
        "flex items-center space-x-2 px-3 py-1.5 rounded-full text-sm font-medium",
        "bg-blue-50 text-blue-700 border border-blue-200",
        "hover:bg-blue-100 transition-colors cursor-pointer"
      )}
    >
      <Loader2 className="w-4 h-4 animate-spin" />
      <span>{runningCount + pendingCount} 個任務</span>
      <ChevronRight className="w-4 h-4" />
    </motion.button>
  )
}
