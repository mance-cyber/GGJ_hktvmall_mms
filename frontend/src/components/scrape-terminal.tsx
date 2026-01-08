'use client'

import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  X, 
  Terminal, 
  Minimize2, 
  Maximize2,
  CheckCircle2, 
  AlertTriangle,
  XCircle,
  SkipForward,
  StopCircle,
  ChevronDown,
  ChevronUp,
  Activity,
  Clock,
  Zap
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

// =============================================
// 類型定義
// =============================================

export interface LogEntry {
  id: string
  timestamp: string
  message: string
  type: 'info' | 'success' | 'error' | 'warning'
}

export interface ScrapeStats {
  total: number
  success: number
  failed: number
  skipped: number
  current?: string  // 當前正在處理的項目名稱
}

interface ScrapeTerminalProps {
  isOpen: boolean
  onClose: () => void
  logs: LogEntry[]
  isScraping: boolean
  progress?: number
  stats?: ScrapeStats
  onCancel?: () => void
  title?: string
}

// =============================================
// 主組件
// =============================================

export function ScrapeTerminal({ 
  isOpen, 
  onClose, 
  logs, 
  isScraping, 
  progress,
  stats,
  onCancel,
  title = 'CRAWLER'
}: ScrapeTerminalProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const [isMinimized, setIsMinimized] = useState(false)
  const [showSummary, setShowSummary] = useState(false)

  // 自動滾動到底部
  useEffect(() => {
    if (scrollRef.current && !isMinimized) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs, isMinimized])

  // 當抓取完成時顯示摘要
  useEffect(() => {
    if (!isScraping && stats && stats.total > 0) {
      setShowSummary(true)
    }
  }, [isScraping, stats])

  // 計算耗時（模擬）
  const getElapsedTime = () => {
    if (logs.length < 2) return '0s'
    const firstLog = logs[0]
    const lastLog = logs[logs.length - 1]
    // 簡單計算 - 實際應該使用真實時間戳
    return `${logs.length * 0.8}s`
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, y: 100, scale: 0.95 }}
          animate={{ 
            opacity: 1, 
            y: 0, 
            scale: 1,
            height: isMinimized ? 'auto' : 'auto'
          }}
          exit={{ opacity: 0, y: 100, scale: 0.95 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          className={cn(
            "fixed bottom-6 right-6 w-[520px] max-w-[calc(100vw-3rem)] z-50",
            "rounded-xl overflow-hidden shadow-2xl shadow-black/50",
            "border border-slate-700/50 bg-slate-950/95 backdrop-blur-xl"
          )}
        >
          {/* ========== 終端標題欄 ========== */}
          <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-slate-900 to-slate-900/80 border-b border-slate-800/80">
            <div className="flex items-center space-x-3">
              {/* 狀態指示燈 */}
              <div className="flex items-center space-x-1.5">
                <div className={cn(
                  "w-3 h-3 rounded-full transition-colors",
                  isScraping ? "bg-green-500 animate-pulse shadow-lg shadow-green-500/50" : 
                  stats && stats.failed > 0 ? "bg-yellow-500" : "bg-slate-600"
                )} />
                <div className="w-3 h-3 rounded-full bg-slate-700" />
                <div className="w-3 h-3 rounded-full bg-slate-700" />
              </div>
              
              <div className="flex items-center space-x-2">
                <Terminal className="w-4 h-4 text-green-500" />
                <span className="text-sm font-mono font-bold text-slate-200 tracking-wide">
                  SYSTEM_TERMINAL // {title}
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-1">
              {/* 運行狀態標籤 */}
              {isScraping && (
                <motion.div 
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="flex items-center px-2.5 py-1 bg-green-500/10 border border-green-500/30 rounded-md text-xs text-green-400 font-mono mr-2"
                >
                  <Activity className="w-3 h-3 mr-1.5 animate-pulse" />
                  RUNNING
                </motion.div>
              )}
              
              {/* 最小化按鈕 */}
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsMinimized(!isMinimized)}
                className="h-7 w-7 text-slate-400 hover:text-white hover:bg-slate-800"
              >
                {isMinimized ? <Maximize2 className="w-3.5 h-3.5" /> : <Minimize2 className="w-3.5 h-3.5" />}
              </Button>
              
              {/* 關閉按鈕 */}
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="h-7 w-7 text-slate-400 hover:text-red-400 hover:bg-red-500/10"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* ========== 進度條 ========== */}
          {isScraping && progress !== undefined && (
            <div className="h-1 bg-slate-800 w-full relative overflow-hidden">
              <motion.div 
                className="h-full bg-gradient-to-r from-green-500 to-emerald-400"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.3, ease: "easeOut" }}
              />
              {/* 光暈效果 */}
              <motion.div
                className="absolute top-0 h-full w-20 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                animate={{ left: ['-20%', '120%'] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
              />
            </div>
          )}

          <AnimatePresence>
            {!isMinimized && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                {/* ========== 統計面板 ========== */}
                {stats && (
                  <div className="px-4 py-3 bg-slate-900/50 border-b border-slate-800/50">
                    <div className="grid grid-cols-4 gap-3">
                      <StatBadge 
                        icon={Zap} 
                        label="總計" 
                        value={stats.total} 
                        color="slate" 
                      />
                      <StatBadge 
                        icon={CheckCircle2} 
                        label="成功" 
                        value={stats.success} 
                        color="green" 
                      />
                      <StatBadge 
                        icon={XCircle} 
                        label="失敗" 
                        value={stats.failed} 
                        color="red" 
                      />
                      <StatBadge 
                        icon={SkipForward} 
                        label="跳過" 
                        value={stats.skipped} 
                        color="yellow" 
                      />
                    </div>
                    
                    {/* 當前處理項目 */}
                    {isScraping && stats.current && (
                      <motion.div 
                        initial={{ opacity: 0, y: -5 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mt-3 flex items-center text-xs text-slate-400 font-mono bg-slate-800/50 rounded px-2 py-1.5"
                      >
                        <Activity className="w-3 h-3 mr-2 text-green-400 animate-pulse" />
                        <span className="text-slate-500">Processing:</span>
                        <span className="ml-1 text-slate-300 truncate">{stats.current}</span>
                      </motion.div>
                    )}
                  </div>
                )}

                {/* ========== 日誌區域 ========== */}
                <div 
                  ref={scrollRef}
                  className="p-4 h-[280px] overflow-y-auto font-mono text-xs space-y-1.5 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-transparent"
                >
                  {logs.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-slate-500">
                      <Terminal className="w-8 h-8 mb-2 opacity-30" />
                      <span className="italic">Waiting for command input...</span>
                    </div>
                  )}
                  
                  {logs.map((log, index) => (
                    <LogLine key={log.id} log={log} index={index} />
                  ))}
                  
                  {/* 閃爍光標 */}
                  {isScraping && (
                    <div className="flex items-center text-green-500/60 mt-2 pl-1">
                      <span className="mr-2 text-green-600">$</span>
                      <motion.span 
                        className="w-2 h-4 bg-green-500/60"
                        animate={{ opacity: [1, 0] }}
                        transition={{ duration: 0.8, repeat: Infinity }}
                      />
                    </div>
                  )}
                </div>

                {/* ========== 完成摘要 ========== */}
                <AnimatePresence>
                  {showSummary && !isScraping && stats && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="border-t border-slate-800"
                    >
                      <div 
                        className="px-4 py-3 bg-slate-900/80 cursor-pointer hover:bg-slate-900 transition-colors"
                        onClick={() => setShowSummary(!showSummary)}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <CheckCircle2 className="w-4 h-4 text-green-500" />
                            <span className="text-sm font-medium text-slate-200">
                              抓取完成
                            </span>
                          </div>
                          <div className="flex items-center space-x-3 text-xs text-slate-400">
                            <span className="flex items-center">
                              <Clock className="w-3 h-3 mr-1" />
                              耗時 {getElapsedTime()}
                            </span>
                            <span className="text-green-400">{stats.success} 成功</span>
                            {stats.failed > 0 && (
                              <span className="text-red-400">{stats.failed} 失敗</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* ========== 底部操作欄 ========== */}
                <div className="px-4 py-3 bg-slate-900/30 border-t border-slate-800/50 flex items-center justify-between">
                  <div className="text-xs text-slate-500 font-mono">
                    {logs.length} entries {progress !== undefined && `• ${progress.toFixed(0)}%`}
                  </div>
                  
                  {/* 取消按鈕 */}
                  {isScraping && onCancel && (
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={onCancel}
                      className="h-7 px-3 text-xs text-red-400 hover:text-red-300 hover:bg-red-500/10 font-mono"
                    >
                      <StopCircle className="w-3.5 h-3.5 mr-1.5" />
                      ABORT
                    </Button>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* ========== 最小化狀態顯示 ========== */}
          {isMinimized && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="px-4 py-2 flex items-center justify-between"
            >
              <div className="flex items-center space-x-3 text-xs text-slate-400">
                {isScraping ? (
                  <>
                    <Activity className="w-3.5 h-3.5 text-green-400 animate-pulse" />
                    <span>Processing... {progress?.toFixed(0)}%</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />
                    <span>Completed</span>
                  </>
                )}
              </div>
              {stats && (
                <div className="flex items-center space-x-2 text-xs">
                  <span className="text-green-400">{stats.success}✓</span>
                  {stats.failed > 0 && <span className="text-red-400">{stats.failed}✕</span>}
                </div>
              )}
            </motion.div>
          )}
        </motion.div>
      )}
    </AnimatePresence>
  )
}

// =============================================
// 子組件
// =============================================

function StatBadge({ 
  icon: Icon, 
  label, 
  value, 
  color 
}: { 
  icon: React.ElementType
  label: string
  value: number
  color: 'slate' | 'green' | 'red' | 'yellow'
}) {
  const colorClasses = {
    slate: 'text-slate-400 bg-slate-800/50',
    green: 'text-green-400 bg-green-500/10',
    red: 'text-red-400 bg-red-500/10',
    yellow: 'text-yellow-400 bg-yellow-500/10'
  }

  return (
    <div className={cn(
      "flex items-center justify-between px-2.5 py-1.5 rounded-md",
      colorClasses[color]
    )}>
      <div className="flex items-center space-x-1.5">
        <Icon className="w-3.5 h-3.5" />
        <span className="text-xs font-medium">{label}</span>
      </div>
      <span className="text-sm font-bold font-mono">{value}</span>
    </div>
  )
}

function LogLine({ log, index }: { log: LogEntry; index: number }) {
  const typeStyles = {
    info: {
      textClass: 'text-slate-300',
      prefix: '',
      icon: null
    },
    success: {
      textClass: 'text-green-400',
      prefix: '✓',
      icon: CheckCircle2
    },
    error: {
      textClass: 'text-red-400',
      prefix: '✕',
      icon: XCircle
    },
    warning: {
      textClass: 'text-yellow-400',
      prefix: '⚠',
      icon: AlertTriangle
    }
  }

  const style = typeStyles[log.type]

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.02, duration: 0.15 }}
      className="flex items-start space-x-2 py-0.5 hover:bg-slate-800/30 rounded px-1 -mx-1"
    >
      <span className="text-slate-600 shrink-0 select-none">[{log.timestamp}]</span>
      <span className={cn("break-all leading-relaxed", style.textClass)}>
        {style.prefix && <span className="mr-1">{style.prefix}</span>}
        {log.message}
      </span>
    </motion.div>
  )
}

// =============================================
// 輔助函數
// =============================================

export function createLogEntry(
  message: string, 
  type: LogEntry['type'] = 'info'
): LogEntry {
  return {
    id: Math.random().toString(36).substring(7),
    timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }),
    message,
    type
  }
}
