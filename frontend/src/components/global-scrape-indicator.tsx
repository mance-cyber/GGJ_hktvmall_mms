'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Activity, 
  ChevronUp, 
  ChevronDown,
  CheckCircle2,
  XCircle,
  Loader2,
  X,
  Building2,
  FolderOpen
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { useScrapeContext, ScrapeJob } from '@/contexts/scrape-context'

// =============================================
// 全局抓取狀態指示器
// =============================================

export function GlobalScrapeIndicator() {
  const { jobs, activeJobsCount, isAnyScraping, clearCompleted } = useScrapeContext()
  const [isExpanded, setIsExpanded] = useState(false)

  // 沒有任務時不顯示
  if (jobs.length === 0) return null

  const completedJobs = jobs.filter(j => j.status === 'success' || j.status === 'failed')
  const activeJobs = jobs.filter(j => j.status === 'running' || j.status === 'pending')

  return (
    <motion.div
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 50 }}
      className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50"
    >
      <div className={cn(
        "bg-slate-900/95 backdrop-blur-xl rounded-2xl shadow-2xl shadow-black/30",
        "border border-slate-700/50 overflow-hidden",
        "min-w-[320px] max-w-[400px]"
      )}>
        {/* 標題欄 */}
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full px-4 py-3 flex items-center justify-between hover:bg-slate-800/50 transition-colors"
        >
          <div className="flex items-center space-x-3">
            {isAnyScraping ? (
              <div className="relative">
                <Activity className="w-5 h-5 text-green-400" />
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-green-400 rounded-full animate-ping" />
              </div>
            ) : (
              <CheckCircle2 className="w-5 h-5 text-slate-400" />
            )}
            <span className="text-sm font-medium text-slate-200">
              {isAnyScraping 
                ? `${activeJobsCount} 個任務進行中`
                : `${completedJobs.length} 個任務已完成`
              }
            </span>
          </div>
          <div className="flex items-center space-x-2">
            {completedJobs.length > 0 && !isAnyScraping && (
              <Button
                size="sm"
                variant="ghost"
                onClick={(e) => { e.stopPropagation(); clearCompleted(); }}
                className="h-6 px-2 text-xs text-slate-400 hover:text-slate-200"
              >
                清除
              </Button>
            )}
            {isExpanded ? (
              <ChevronDown className="w-4 h-4 text-slate-400" />
            ) : (
              <ChevronUp className="w-4 h-4 text-slate-400" />
            )}
          </div>
        </button>

        {/* 展開的任務列表 */}
        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="border-t border-slate-700/50"
            >
              <div className="max-h-[300px] overflow-y-auto">
                {/* 進行中的任務 */}
                {activeJobs.map(job => (
                  <JobItem key={job.id} job={job} />
                ))}
                
                {/* 已完成的任務 */}
                {completedJobs.length > 0 && activeJobs.length > 0 && (
                  <div className="px-4 py-2 text-xs text-slate-500 bg-slate-800/30">
                    已完成
                  </div>
                )}
                {completedJobs.slice(0, 5).map(job => (
                  <JobItem key={job.id} job={job} />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* 進度條（收起時顯示） */}
        {!isExpanded && isAnyScraping && (
          <div className="h-1 bg-slate-800">
            <motion.div
              className="h-full bg-gradient-to-r from-green-500 to-emerald-400"
              initial={{ width: 0 }}
              animate={{ 
                width: `${Math.max(...activeJobs.map(j => j.progress || 0))}%` 
              }}
              transition={{ duration: 0.3 }}
            />
          </div>
        )}
      </div>
    </motion.div>
  )
}

// =============================================
// 任務項組件
// =============================================

function JobItem({ job }: { job: ScrapeJob }) {
  const statusConfig = {
    pending: { 
      icon: Loader2, 
      iconClass: 'text-slate-400',
      label: '等待中'
    },
    running: { 
      icon: Loader2, 
      iconClass: 'text-green-400 animate-spin',
      label: '抓取中'
    },
    success: { 
      icon: CheckCircle2, 
      iconClass: 'text-green-400',
      label: '完成'
    },
    failed: { 
      icon: XCircle, 
      iconClass: 'text-red-400',
      label: '失敗'
    },
  }

  const config = statusConfig[job.status]
  const Icon = config.icon
  const TypeIcon = job.type === 'competitor' ? Building2 : FolderOpen

  return (
    <div className="px-4 py-3 flex items-center space-x-3 hover:bg-slate-800/30 transition-colors">
      {/* 類型圖標 */}
      <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center flex-shrink-0">
        <TypeIcon className="w-4 h-4 text-slate-400" />
      </div>

      {/* 任務信息 */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-slate-200 truncate">
          {job.targetName}
        </p>
        <div className="flex items-center space-x-2 mt-0.5">
          <span className={cn("text-xs flex items-center", config.iconClass)}>
            <Icon className="w-3 h-3 mr-1" />
            {config.label}
          </span>
          {job.status === 'running' && job.progress > 0 && (
            <span className="text-xs text-slate-500">
              {job.progress.toFixed(0)}%
            </span>
          )}
          {job.productCount !== undefined && job.status === 'success' && (
            <span className="text-xs text-slate-500">
              · {job.productCount} 商品
            </span>
          )}
        </div>
      </div>

      {/* 進度條 */}
      {job.status === 'running' && (
        <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden flex-shrink-0">
          <motion.div
            className="h-full bg-green-500"
            initial={{ width: 0 }}
            animate={{ width: `${job.progress}%` }}
          />
        </div>
      )}
    </div>
  )
}
