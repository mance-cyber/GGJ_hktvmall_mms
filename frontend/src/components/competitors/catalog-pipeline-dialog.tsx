'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import {
  Loader2,
  CheckCircle2,
  XCircle,
  Database,
  Play,
  RotateCcw,
  Clock,
  ChevronDown,
  ChevronUp,
  Terminal,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { HoloButton } from '@/components/ui/future-tech'
import { useLocale } from '@/components/providers/locale-provider'

// =============================================
// Competitor建庫流程 Dialog（SSE 串流版）
// =============================================

type PipelinePhase = 'idle' | 'running' | 'done' | 'error'

interface StepResult {
  status: 'pending' | 'running' | 'done' | 'error'
  data?: any
  error?: string
  duration?: number
}

interface LogEntry {
  time: string
  message: string
  type: 'info' | 'success' | 'error' | 'step'
}

const STEPS = ['build', 'tag', 'match'] as const
type StepKey = typeof STEPS[number]

// =============================================
// 每步驟的活動訊息（輪播Display）
// =============================================

const STEP_ACTIVITY_MESSAGES: Record<StepKey, string[]> = {
  build: [
    'ConnectionCompetitor平台 API...',
    '抓取Product list頁...',
    'ParseproductsData...',
    '比對現有Data庫Record...',
    '寫入新products / Update已有products...',
    'ProcessingproductsImage與規格...',
    'Clean up重複Data...',
  ],
  tag: [
    'Load未打標products...',
    '執行關鍵詞規則引擎...',
    '分類：鮮魚 / 貝類 / 蟹類...',
    '無法Match規則的products送 AI 分類...',
    'Claude Haiku AnalysisproductsName中...',
    '寫入分類標籤...',
  ],
  match: [
    'Load自家Product list...',
    'Load已打標Competitor...',
    'Calculate Level 1 direct match...',
    'Calculate Level 2 similar match...',
    'Calculate Level 3 same-category match...',
    '寫入Match關係...',
  ],
}

// =============================================
// Hooks
// =============================================

function useActivityMessages(step: StepKey | null): string {
  const [index, setIndex] = useState(0)

  useEffect(() => {
    if (!step) {
      setIndex(0)
      return
    }
    setIndex(0)
    const messages = STEP_ACTIVITY_MESSAGES[step]
    const id = setInterval(() => {
      setIndex(prev => (prev + 1) % messages.length)
    }, 3000)
    return () => clearInterval(id)
  }, [step])

  if (!step) return ''
  return STEP_ACTIVITY_MESSAGES[step][index]
}

function formatDuration(ms: number): string {
  const s = Math.floor(ms / 1000)
  if (s < 60) return `${s}s`
  return `${Math.floor(s / 60)}m ${s % 60}s`
}

function timeStamp(): string {
  return new Date().toLocaleTimeString('en-GB', { hour12: false })
}

// =============================================
// 主組items
// =============================================

export function CatalogPipelineDialog() {
  const { t } = useLocale()
  const queryClient = useQueryClient()

  const [open, setOpen] = useState(false)
  const [platform, setPlatform] = useState('all')
  const [phase, setPhase] = useState<PipelinePhase>('idle')
  const [failedStep, setFailedStep] = useState<StepKey | null>(null)
  const [expandedStep, setExpandedStep] = useState<StepKey | null>(null)
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [steps, setSteps] = useState<Record<StepKey, StepResult>>({
    build: { status: 'pending' },
    tag: { status: 'pending' },
    match: { status: 'pending' },
  })
  // 從輪詢取得的即時耗時（秒）
  const [heartbeatElapsed, setHeartbeatElapsed] = useState(0)
  // 當前步驟即時進度（Match步驟的逐products進度）
  const [progress, setProgress] = useState<{
    current: number; total: number; failed?: number; message?: string
  } | null>(null)

  const logsEndRef = useRef<HTMLDivElement>(null)
  const abortRef = useRef<AbortController | null>(null)
  const runningStep = STEPS.find(s => steps[s].status === 'running') ?? null
  const activityMessage = useActivityMessages(runningStep)

  const isRunning = phase === 'running'

  // 寫Log（不可變）
  const addLog = useCallback((message: string, type: LogEntry['type'] = 'info') => {
    setLogs(prev => [...prev, { time: timeStamp(), message, type }])
    setTimeout(() => logsEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 50)
  }, [])

  const resetState = useCallback(() => {
    setPhase('idle')
    setFailedStep(null)
    setExpandedStep(null)
    setLogs([])
    setHeartbeatElapsed(0)
    setProgress(null)
    setSteps({
      build: { status: 'pending' },
      tag: { status: 'pending' },
      match: { status: 'pending' },
    })
  }, [])

  const updateStep = useCallback((key: StepKey, patch: Partial<StepResult>) => {
    setSteps(prev => ({ ...prev, [key]: { ...prev[key], ...patch } }))
  }, [])

  const stepNames: Record<StepKey, string> = {
    build: '建庫',
    tag: '打標',
    match: 'Match',
  }

  // =============================================
  // 後台任務 + 輪詢（取代 SSE 長連線）
  // =============================================

  const runPipeline = useCallback(async () => {
    setPhase('running')
    setFailedStep(null)
    setExpandedStep(null)
    setLogs([])
    setHeartbeatElapsed(0)
    setSteps({
      build: { status: 'pending' },
      tag: { status: 'pending' },
      match: { status: 'pending' },
    })

    const controller = new AbortController()
    abortRef.current = controller

    addLog('═══ StartCompetitor建庫流程 ═══', 'step')
    addLog(`Target平台: ${platform === 'all' ? 'All' : platform}`, 'info')

    // Track previously output logs to avoid duplicates
    const loggedStarts = new Set<StepKey>()
    const loggedDones = new Set<StepKey>()

    try {
      // 啟動後台任務
      const { task_id: taskId } = await api.startPipeline(platform)

      // 輪詢進度（每 2 秒一次短Request，完全不受反代TimeoutLimit）
      // 連續ErrorUpper limit：Prevent無限輪詢
      const MAX_CONSECUTIVE_ERRORS = 20
      let consecutiveErrors = 0

      while (true) {
        if (controller.signal.aborted) return
        await new Promise(r => setTimeout(r, 2000))
        if (controller.signal.aborted) return

        let p
        try {
          p = await api.getPipelineProgress(taskId)
          consecutiveErrors = 0  // Success時Reset計數
        } catch (pollErr: any) {
          consecutiveErrors++
          const msg = pollErr.message ?? ''

          // 404 = 任務不存在（DB 已持久化，僅Expired或誤刪才會 404）
          if (msg.includes('404') || msg.includes('不存在') || msg.includes('Expired')) {
            addLog('✗ 任務不存在或已Expired，請Retry。', 'error')
            setPhase('error')
            break
          }

          // 連續Error太多 → 放棄
          if (consecutiveErrors >= MAX_CONSECUTIVE_ERRORS) {
            addLog(`✗ 連續 ${consecutiveErrors} 次輪詢Failed，Stopped。最後Error: ${msg}`, 'error')
            setPhase('error')
            break
          }

          // 502/503 或其他瞬時Error → 下次Retry
          if (consecutiveErrors % 5 === 0) {
            addLog(`⚠ 輪詢暫時Failed (${consecutiveErrors}/${MAX_CONSECUTIVE_ERRORS})，Retry中...`, 'info')
          }
          continue
        }

        // 先Update已Complete步驟（保證「Complete」Log在「Start下一步」之前）
        for (const step of STEPS) {
          if (p.step_results[step] && !loggedDones.has(step)) {
            const dur = (p.step_durations[step] ?? 0) * 1000
            updateStep(step, { status: 'done', data: { result: p.step_results[step] }, duration: dur })
            addLog(`✓ ${stepNames[step]}Complete (${formatDuration(dur)})`, 'success')
            logStepResult(step, p.step_results[step], addLog)
            setExpandedStep(step)
            loggedDones.add(step)
          }
        }

        // 再Update當前步驟 → running
        if (p.current_step) {
          const step = p.current_step as StepKey
          if (!loggedStarts.has(step)) {
            updateStep(step, { status: 'running', error: undefined, data: undefined, duration: undefined })
            addLog(`▶ Start步驟 ${p.current_step_number}/${p.total_steps}: ${stepNames[step]}`, 'step')
            loggedStarts.add(step)
          }
          setHeartbeatElapsed(p.elapsed * 1000)
          // 即時進度（Match步驟的逐products進度）
          setProgress(p.progress ?? null)
        }

        // AllComplete
        if (p.status === 'done') {
          addLog('═══ 流程AllComplete ═══', 'success')
          setPhase('done')
          queryClient.invalidateQueries({ queryKey: ['competitors'] })
          break
        }

        // 出錯
        if (p.status === 'error') {
          const errStep = Object.keys(p.step_errors)[0] as StepKey
          if (!loggedDones.has(errStep)) {
            const dur = (p.step_durations[errStep] ?? 0) * 1000
            updateStep(errStep, { status: 'error', error: p.step_errors[errStep], duration: dur })
            addLog(`✗ ${stepNames[errStep]}Failed: ${p.step_errors[errStep]}`, 'error')
            setExpandedStep(errStep)
          }
          setPhase('error')
          setFailedStep(errStep)
          break
        }
      }
    } catch (err: any) {
      if (err.name === 'AbortError') return
      addLog(`✗ 啟動Failed: ${humanizeError(err)}`, 'error')
      setPhase('error')
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [platform, updateStep, queryClient, addLog])

  // Handle dialog close: disabled during executionClose
  const handleDialogClose = useCallback((nextOpen: boolean) => {
    if (!nextOpen && isRunning) return
    if (!nextOpen) {
      abortRef.current?.abort()
      resetState()
    }
    setOpen(nextOpen)
  }, [resetState, isRunning])

  const stepLabels: Record<StepKey, string> = {
    build: t['competitors.catalog_step_build'],
    tag: t['competitors.catalog_step_tag'],
    match: t['competitors.catalog_step_match'],
  }

  return (
    <Dialog open={open} onOpenChange={handleDialogClose}>
      <DialogTrigger asChild>
        <HoloButton variant="primary" size="sm" icon={<Database className="w-4 h-4" />}>
          <span className="hidden sm:inline">{t['competitors.catalog_build']}</span>
        </HoloButton>
      </DialogTrigger>
      <DialogContent
        className="sm:max-w-lg"
        onInteractOutside={(e) => { if (isRunning) e.preventDefault() }}
        onEscapeKeyDown={(e) => { if (isRunning) e.preventDefault() }}
        {...(isRunning ? { 'data-lock': true } : {})}
      >
        <DialogHeader>
          <DialogTitle>{t['competitors.catalog_title']}</DialogTitle>
          <DialogDescription>{t['competitors.catalog_desc']}</DialogDescription>
        </DialogHeader>

        {/* ========== idle：平台Select ========== */}
        {phase === 'idle' && (
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">{t['competitors.catalog_platform']}</label>
              <Select value={platform} onValueChange={setPlatform}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t['competitors.catalog_all_platforms']}</SelectItem>
                  <SelectItem value="hktvmall">HKTVmall</SelectItem>
                  <SelectItem value="wellcome">Wellcome</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="rounded-lg bg-blue-50 p-3 text-sm text-blue-700 space-y-1.5">
              <p className="font-medium">流程步驟</p>
              <ol className="text-xs space-y-1 list-decimal list-inside">
                <li><b>建庫</b> — 抓取Competitor平台productsData入庫</li>
                <li><b>打標</b> — 規則 + AI Auto分類標籤</li>
                <li><b>Match</b> — AI Pair自家products與Competitor</li>
              </ol>
            </div>
          </div>
        )}

        {/* ========== 執行中 / Complete / Error ========== */}
        {phase !== 'idle' && (
          <div className="space-y-3 py-3">
            {/* 步驟指示器 */}
            <div className="space-y-2">
              {STEPS.map((step, idx) => {
                const s = steps[step]
                const isExpanded = expandedStep === step
                const canExpand = s.status === 'done' || s.status === 'error'

                return (
                  <div
                    key={step}
                    data-step={step}
                    data-status={s.status}
                    className="rounded-lg border overflow-hidden transition-all"
                    style={{
                      borderColor: s.status === 'running' ? 'rgb(59 130 246 / 0.5)' :
                                   s.status === 'error' ? 'rgb(239 68 68 / 0.5)' :
                                   s.status === 'done' ? 'rgb(34 197 94 / 0.5)' :
                                   'rgb(226 232 240)',
                    }}
                  >
                    {/* 步驟主行 */}
                    <div
                      className={`flex items-center gap-3 px-3 py-2 ${canExpand ? 'cursor-pointer' : ''} select-none`}
                      onClick={() => canExpand && setExpandedStep(isExpanded ? null : step)}
                      style={{
                        backgroundColor: s.status === 'running' ? 'rgb(239 246 255)' :
                                         s.status === 'error' ? 'rgb(254 242 242)' :
                                         s.status === 'done' ? 'rgb(240 253 244)' :
                                         'transparent',
                      }}
                    >
                      {s.status === 'running' && (
                        <Loader2 className="w-4 h-4 text-blue-500 animate-spin flex-shrink-0" />
                      )}
                      {s.status === 'done' && (
                        <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0" />
                      )}
                      {s.status === 'error' && (
                        <XCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
                      )}
                      {s.status === 'pending' && (
                        <div className="w-4 h-4 rounded-full border-2 border-slate-300 flex-shrink-0 flex items-center justify-center text-[9px] text-slate-400 font-bold">
                          {idx + 1}
                        </div>
                      )}

                      <span className="text-sm font-medium flex-1">{stepLabels[step]}</span>

                      {/* Duration: use heartbeat real-time value when running */}
                      {s.status === 'running' && (
                        <span className="text-xs text-blue-500 tabular-nums flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDuration(heartbeatElapsed)}
                        </span>
                      )}
                      {(s.status === 'done' || s.status === 'error') && s.duration != null && (
                        <span className="text-xs text-muted-foreground tabular-nums flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDuration(s.duration)}
                        </span>
                      )}

                      {canExpand && (
                        isExpanded
                          ? <ChevronUp className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0" />
                          : <ChevronDown className="w-3.5 h-3.5 text-muted-foreground flex-shrink-0" />
                      )}
                    </div>

                    {/* 即時進度條（Match步驟的逐products進度） */}
                    {s.status === 'running' && progress && progress.total > 0 && (
                      <div className="px-3 pb-2 space-y-1">
                        <div className="flex items-center justify-between text-[11px]">
                          <span className="text-blue-600 truncate max-w-[240px]">
                            {progress.message}
                          </span>
                          <span className="text-blue-500 tabular-nums flex-shrink-0 ml-2">
                            {progress.current}/{progress.total}
                            {(progress.failed ?? 0) > 0 && (
                              <span className="text-red-400 ml-1">({progress.failed} Failed)</span>
                            )}
                          </span>
                        </div>
                        <div className="w-full h-1.5 bg-blue-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-500 rounded-full transition-all duration-500"
                            style={{ width: `${Math.round((progress.current / progress.total) * 100)}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {/* 展開Details */}
                    {isExpanded && s.status === 'done' && s.data && (
                      <div className="px-3 pb-2.5 pt-0">
                        <StepDetail step={step} data={s.data} platform={platform} />
                      </div>
                    )}
                    {isExpanded && s.status === 'error' && (
                      <div className="px-3 pb-2.5 pt-0">
                        <div className="rounded bg-red-50 p-2 text-xs text-red-600 break-all">
                          {s.error}
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>

            {/* ========== 活動Log面板 ========== */}
            <div className="rounded-lg border border-slate-700 bg-slate-900 overflow-hidden">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 border-b border-slate-700">
                <Terminal className="w-3.5 h-3.5 text-slate-400" />
                <span className="text-xs text-slate-400 font-mono">Pipeline Log</span>
                {isRunning && (
                  <span className="ml-auto text-xs text-blue-400 font-mono animate-pulse truncate max-w-[200px]">
                    {progress?.message || activityMessage}
                  </span>
                )}
              </div>
              <div className="max-h-[160px] overflow-y-auto p-2 font-mono text-[11px] leading-relaxed">
                {logs.map((entry, i) => (
                  <div key={i} className="flex gap-2">
                    <span className="text-slate-500 flex-shrink-0">{entry.time}</span>
                    <span className={
                      entry.type === 'success' ? 'text-green-400' :
                      entry.type === 'error' ? 'text-red-400' :
                      entry.type === 'step' ? 'text-cyan-400 font-semibold' :
                      'text-slate-300'
                    }>
                      {entry.message}
                    </span>
                  </div>
                ))}
                {isRunning && (
                  <div className="flex gap-2 animate-pulse">
                    <span className="text-slate-500 flex-shrink-0">{timeStamp()}</span>
                    <span className="text-blue-400">{activityMessage}</span>
                  </div>
                )}
                <div ref={logsEndRef} />
              </div>
            </div>

            {/* Complete摘要 */}
            {phase === 'done' && (
              <div className="rounded-lg bg-green-50 border border-green-200 p-3 text-sm text-green-700">
                <p className="font-medium">{t['competitors.catalog_done']}</p>
                <p className="text-xs mt-1">
                  總耗時 {formatDuration(
                    STEPS.reduce((sum, s) => sum + (steps[s].duration ?? 0), 0)
                  )}
                </p>
              </div>
            )}
          </div>
        )}

        <DialogFooter>
          {phase === 'idle' && (
            <>
              <Button variant="outline" onClick={() => handleDialogClose(false)}>
                {t['common.cancel']}
              </Button>
              <Button onClick={() => runPipeline()}>
                <Play className="mr-2 h-4 w-4" />
                {t['competitors.catalog_start']}
              </Button>
            </>
          )}
          {isRunning && (
            <p className="text-xs text-muted-foreground text-center w-full">
              Processing, please do not close this window...
            </p>
          )}
          {phase === 'error' && (
            <>
              <Button variant="outline" onClick={() => handleDialogClose(false)}>
                {t['common.cancel']}
              </Button>
              <Button onClick={() => runPipeline()}>
                <RotateCcw className="mr-2 h-4 w-4" />
                {t['competitors.catalog_retry']}
              </Button>
            </>
          )}
          {phase === 'done' && (
            <Button onClick={() => handleDialogClose(false)}>
              {t['common.confirm']}
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// =============================================
// Log：步驟Result摘要
// =============================================

function logStepResult(
  step: StepKey,
  result: any,
  addLog: (msg: string, type: LogEntry['type']) => void,
) {
  if (!result) return

  if (step === 'build') {
    const entries = typeof result === 'object' && ('hktvmall' in result || 'wellcome' in result)
      ? Object.entries(result)
      : [['platform', result]]
    for (const [name, stats] of entries) {
      const s = stats as any
      if (s?.skipped) {
        addLog(`  ${name}: 已Skip (${s.reason})`, 'info')
      } else if (s) {
        addLog(`  ${name}: Add ${s.new ?? 0} / Update ${s.updated ?? 0} / 未變 ${s.unchanged ?? 0}`, 'info')
      }
    }
  } else if (step === 'tag') {
    addLog(`  規則打標 ${result.rule_tagged ?? 0} / AI 打標 ${result.ai_tagged ?? 0} / Skip ${result.skipped ?? 0}`, 'info')
  } else if (step === 'match') {
    if ('products_matched' in result) {
      addLog(`  Matchproducts ${result.products_matched ?? 0} / L1 ${result.total_level_1 ?? 0} / L2 ${result.total_level_2 ?? 0} / L3 ${result.total_level_3 ?? 0}`, 'info')
    } else {
      addLog(`  Match ${result.matched ?? 0} / L1 ${result.level_1 ?? 0} / L2 ${result.level_2 ?? 0} / L3 ${result.level_3 ?? 0}`, 'info')
    }
  }
}

// =============================================
// 步驟Details面板
// =============================================

function StepDetail({ step, data, platform }: { step: StepKey; data: any; platform: string }) {
  const result = data?.result
  if (!result) return null

  if (step === 'build') return <BuildDetail result={result} platform={platform} />
  if (step === 'tag') return <TagDetail result={result} />
  if (step === 'match') return <MatchDetail result={result} />
  return null
}

function BuildDetail({ result, platform }: { result: any; platform: string }) {
  const platforms = (platform === 'all' && typeof result === 'object' && ('hktvmall' in result || 'wellcome' in result))
    ? Object.entries(result) as [string, any][]
    : [[platform, result] as [string, any]]

  return (
    <div className="space-y-2">
      {platforms.map(([name, stats]) => {
        if (!stats || typeof stats !== 'object') return null
        if (stats.skipped) {
          return (
            <div key={name} className="rounded bg-slate-50 p-2 text-xs">
              <span className="font-medium capitalize">{name}</span>
              <span className="text-muted-foreground ml-2">已Skip: {stats.reason}</span>
            </div>
          )
        }
        return (
          <div key={name} className="rounded bg-slate-50 p-2">
            <p className="text-xs font-medium capitalize mb-1">{name}</p>
            <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-xs">
              <StatRow label="Add" value={stats.new ?? stats.added ?? 0} color="text-green-600" />
              <StatRow label="Update" value={stats.updated ?? 0} color="text-blue-600" />
              <StatRow label="未變" value={stats.unchanged ?? 0} color="text-slate-500" />
              <StatRow label="總抓取" value={stats.total_fetched ?? 0} color="text-slate-700" />
              {(stats.skipped_store_limit ?? 0) > 0 && (
                <StatRow label="達Upper limitSkip" value={stats.skipped_store_limit} color="text-yellow-600" />
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function TagDetail({ result }: { result: any }) {
  return (
    <div className="rounded bg-slate-50 p-2">
      <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-xs">
        <StatRow label="規則打標" value={result.rule_tagged ?? 0} color="text-green-600" />
        <StatRow label="AI 打標" value={result.ai_tagged ?? 0} color="text-blue-600" />
        <StatRow label="Skip" value={result.skipped ?? 0} color="text-slate-500" />
        {(result.failed ?? 0) > 0 && (
          <StatRow label="Failed" value={result.failed} color="text-red-600" />
        )}
      </div>
    </div>
  )
}

function MatchDetail({ result }: { result: any }) {
  const isAll = 'products_matched' in result
  return (
    <div className="rounded bg-slate-50 p-2">
      <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-xs">
        {isAll ? (
          <>
            <StatRow label="Matchproducts數" value={result.products_matched ?? 0} color="text-green-600" />
            <StatRow label="ProcessingCompetitor數" value={result.competitors_processed ?? 0} color="text-blue-600" />
            <StatRow label="Level 1 (直接)" value={result.total_level_1 ?? 0} color="text-green-700" />
            <StatRow label="Level 2 (相似)" value={result.total_level_2 ?? 0} color="text-blue-700" />
            <StatRow label="Level 3 (同類)" value={result.total_level_3 ?? 0} color="text-slate-600" />
          </>
        ) : (
          <>
            <StatRow label="Match數" value={result.matched ?? 0} color="text-green-600" />
            <StatRow label="Skip" value={result.skipped ?? 0} color="text-slate-500" />
            <StatRow label="Level 1 (直接)" value={result.level_1 ?? 0} color="text-green-700" />
            <StatRow label="Level 2 (相似)" value={result.level_2 ?? 0} color="text-blue-700" />
            <StatRow label="Level 3 (同類)" value={result.level_3 ?? 0} color="text-slate-600" />
          </>
        )}
      </div>
    </div>
  )
}

function StatRow({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-muted-foreground">{label}</span>
      <span className={`font-medium tabular-nums ${color}`}>{value}</span>
    </div>
  )
}

// 網絡Error友好化
function humanizeError(err: unknown): string {
  if (err instanceof DOMException && err.name === 'TimeoutError') {
    return 'Request timed out, server processing took too long. Please try again later.'
  }
  if (err instanceof TypeError && (err.message === 'Failed to fetch' || err.message === 'Load failed')) {
    return 'Cannot connect to server, possibly network down or server timeout. Please check your network and retry.'
  }
  if (err instanceof Error) {
    if (err.message.includes('ERR_CONNECTION_CLOSED') || err.message.includes('connection closed')) {
      return 'Server connection interrupted, operation may be taking too long. Please try again later.'
    }
    return err.message
  }
  return String(err)
}
