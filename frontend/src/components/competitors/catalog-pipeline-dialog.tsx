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
// 競品建庫流程 Dialog（建庫 → 打標 → 匹配）
// =============================================

type PipelinePhase = 'idle' | 'building' | 'tagging' | 'matching' | 'done' | 'error'

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
// 每步驟的活動訊息（輪播顯示）
// =============================================

const STEP_ACTIVITY_MESSAGES: Record<StepKey, string[]> = {
  build: [
    '連接競品平台 API...',
    '抓取商品列表頁...',
    '解析商品數據...',
    '比對現有數據庫記錄...',
    '寫入新商品 / 更新已有商品...',
    '處理商品圖片與規格...',
    '清理重複數據...',
  ],
  tag: [
    '載入未打標商品...',
    '執行關鍵詞規則引擎...',
    '分類：鮮魚 / 貝類 / 蟹類...',
    '無法匹配規則的商品送 AI 分類...',
    'Claude Haiku 分析商品名稱中...',
    '寫入分類標籤...',
  ],
  match: [
    '載入自家商品列表...',
    '載入已打標競品...',
    '計算 Level 1 直接匹配...',
    '計算 Level 2 相似匹配...',
    '計算 Level 3 同類匹配...',
    '寫入匹配關係...',
  ],
}

// =============================================
// Hooks
// =============================================

function useElapsed(active: boolean): number {
  const [elapsed, setElapsed] = useState(0)
  const startRef = useRef(Date.now())

  useEffect(() => {
    if (!active) {
      setElapsed(0)
      return
    }
    startRef.current = Date.now()
    const id = setInterval(() => setElapsed(Date.now() - startRef.current), 200)
    return () => clearInterval(id)
  }, [active])

  return elapsed
}

// 活動訊息輪播 Hook
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
// 主組件
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

  const logsEndRef = useRef<HTMLDivElement>(null)
  const runningStep = STEPS.find(s => steps[s].status === 'running') ?? null
  const elapsed = useElapsed(runningStep !== null)
  const activityMessage = useActivityMessages(runningStep)

  const isRunning = phase === 'building' || phase === 'tagging' || phase === 'matching'

  // 寫日誌（不可變）
  const addLog = useCallback((message: string, type: LogEntry['type'] = 'info') => {
    setLogs(prev => [...prev, { time: timeStamp(), message, type }])
    setTimeout(() => logsEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 50)
  }, [])

  const resetState = useCallback(() => {
    setPhase('idle')
    setFailedStep(null)
    setExpandedStep(null)
    setLogs([])
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
    match: '匹配',
  }

  const runPipeline = useCallback(async (startFrom: StepKey = 'build') => {
    const startIndex = STEPS.indexOf(startFrom)
    setFailedStep(null)
    setExpandedStep(null)

    if (startIndex === 0) {
      setLogs([])
    }

    for (let i = startIndex; i < STEPS.length; i++) {
      updateStep(STEPS[i], { status: 'pending', error: undefined, data: undefined, duration: undefined })
    }

    addLog('═══ 開始競品建庫流程 ═══', 'step')
    addLog(`目標平台: ${platform === 'all' ? '全部' : platform}`, 'info')

    const phaseMap: Record<StepKey, PipelinePhase> = {
      build: 'building',
      tag: 'tagging',
      match: 'matching',
    }

    const apiCalls: Record<StepKey, () => Promise<any>> = {
      build: () => api.buildCatalog(platform),
      tag: () => api.tagCatalog(),
      match: () => api.matchCatalog(),
    }

    for (let i = startIndex; i < STEPS.length; i++) {
      const step = STEPS[i]
      const stepStart = Date.now()
      setPhase(phaseMap[step])
      updateStep(step, { status: 'running' })
      addLog(`▶ 開始步驟 ${i + 1}/3: ${stepNames[step]}`, 'step')

      try {
        const result = await apiCalls[step]()
        const duration = Date.now() - stepStart
        updateStep(step, { status: 'done', data: result, duration })
        addLog(`✓ ${stepNames[step]}完成 (${formatDuration(duration)})`, 'success')

        // 記錄結果摘要到日誌
        logStepResult(step, result?.result, addLog)
        setExpandedStep(step)
      } catch (err) {
        const duration = Date.now() - stepStart
        const errorMsg = humanizeError(err)
        updateStep(step, { status: 'error', error: errorMsg, duration })
        addLog(`✗ ${stepNames[step]}失敗: ${errorMsg}`, 'error')
        setPhase('error')
        setFailedStep(step)
        setExpandedStep(step)
        return
      }
    }

    addLog('═══ 流程全部完成 ═══', 'success')
    setPhase('done')
    queryClient.invalidateQueries({ queryKey: ['competitors'] })
  }, [platform, updateStep, queryClient, addLog, stepNames])

  // 處理 Dialog 關閉：執行中禁止關閉
  const handleDialogClose = useCallback((nextOpen: boolean) => {
    if (!nextOpen && isRunning) return // 執行中不允許關閉
    if (!nextOpen) resetState()
    setOpen(nextOpen)
  }, [resetState, isRunning])

  const stepLabels: Record<StepKey, string> = {
    build: t['competitors.catalog_step_build'],
    tag: t['competitors.catalog_step_tag'],
    match: t['competitors.catalog_step_match'],
  }

  const phaseLabels: Record<string, string> = {
    building: t['competitors.catalog_building'],
    tagging: t['competitors.catalog_tagging'],
    matching: t['competitors.catalog_matching'],
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
        // 處理中禁止點擊外部關閉
        onInteractOutside={(e) => { if (isRunning) e.preventDefault() }}
        onEscapeKeyDown={(e) => { if (isRunning) e.preventDefault() }}
        // 處理中隱藏 X 按鈕
        {...(isRunning ? { 'data-lock': true } : {})}
      >
        <DialogHeader>
          <DialogTitle>{t['competitors.catalog_title']}</DialogTitle>
          <DialogDescription>{t['competitors.catalog_desc']}</DialogDescription>
        </DialogHeader>

        {/* ========== idle：平台選擇 ========== */}
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
                <li><b>建庫</b> — 抓取競品平台商品數據入庫</li>
                <li><b>打標</b> — 規則 + AI 自動分類標籤</li>
                <li><b>匹配</b> — AI 配對自家商品與競品</li>
              </ol>
            </div>
          </div>
        )}

        {/* ========== 執行中 / 完成 / 錯誤 ========== */}
        {phase !== 'idle' && (
          <div className="space-y-3 py-3">
            {/* 步驟指示器 */}
            <div className="space-y-2">
              {STEPS.map((step, idx) => {
                const s = steps[step]
                const isExpanded = expandedStep === step
                const canExpand = s.status === 'done' || s.status === 'error'

                return (
                  <div key={step} className="rounded-lg border overflow-hidden transition-all"
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

                      {/* 耗時 */}
                      {s.status === 'running' && (
                        <span className="text-xs text-blue-500 tabular-nums flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDuration(elapsed)}
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

                    {/* 展開詳情 */}
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

            {/* ========== 活動日誌面板 ========== */}
            <div className="rounded-lg border border-slate-700 bg-slate-900 overflow-hidden">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 border-b border-slate-700">
                <Terminal className="w-3.5 h-3.5 text-slate-400" />
                <span className="text-xs text-slate-400 font-mono">Pipeline Log</span>
                {isRunning && (
                  <span className="ml-auto text-xs text-blue-400 font-mono animate-pulse">
                    {activityMessage}
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

            {/* 完成摘要 */}
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
              <Button onClick={() => runPipeline('build')}>
                <Play className="mr-2 h-4 w-4" />
                {t['competitors.catalog_start']}
              </Button>
            </>
          )}
          {isRunning && (
            <p className="text-xs text-muted-foreground text-center w-full">
              處理中，請勿關閉此視窗...
            </p>
          )}
          {phase === 'error' && failedStep && (
            <>
              <Button variant="outline" onClick={() => handleDialogClose(false)}>
                {t['common.cancel']}
              </Button>
              <Button onClick={() => runPipeline(failedStep)}>
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
// 日誌：步驟結果摘要
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
        addLog(`  ${name}: 已跳過 (${s.reason})`, 'info')
      } else if (s) {
        addLog(`  ${name}: 新增 ${s.new ?? 0} / 更新 ${s.updated ?? 0} / 未變 ${s.unchanged ?? 0}`, 'info')
      }
    }
  } else if (step === 'tag') {
    addLog(`  規則打標 ${result.rule_tagged ?? 0} / AI 打標 ${result.ai_tagged ?? 0} / 跳過 ${result.skipped ?? 0}`, 'info')
  } else if (step === 'match') {
    if ('products_matched' in result) {
      addLog(`  匹配商品 ${result.products_matched ?? 0} / L1 ${result.total_level_1 ?? 0} / L2 ${result.total_level_2 ?? 0} / L3 ${result.total_level_3 ?? 0}`, 'info')
    } else {
      addLog(`  匹配 ${result.matched ?? 0} / L1 ${result.level_1 ?? 0} / L2 ${result.level_2 ?? 0} / L3 ${result.level_3 ?? 0}`, 'info')
    }
  }
}

// =============================================
// 步驟詳情面板
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
              <span className="text-muted-foreground ml-2">已跳過: {stats.reason}</span>
            </div>
          )
        }
        return (
          <div key={name} className="rounded bg-slate-50 p-2">
            <p className="text-xs font-medium capitalize mb-1">{name}</p>
            <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 text-xs">
              <StatRow label="新增" value={stats.new ?? stats.added ?? 0} color="text-green-600" />
              <StatRow label="更新" value={stats.updated ?? 0} color="text-blue-600" />
              <StatRow label="未變" value={stats.unchanged ?? 0} color="text-slate-500" />
              <StatRow label="總抓取" value={stats.total_fetched ?? 0} color="text-slate-700" />
              {(stats.skipped_store_limit ?? 0) > 0 && (
                <StatRow label="達上限跳過" value={stats.skipped_store_limit} color="text-yellow-600" />
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
        <StatRow label="跳過" value={result.skipped ?? 0} color="text-slate-500" />
        {(result.failed ?? 0) > 0 && (
          <StatRow label="失敗" value={result.failed} color="text-red-600" />
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
            <StatRow label="匹配商品數" value={result.products_matched ?? 0} color="text-green-600" />
            <StatRow label="處理競品數" value={result.competitors_processed ?? 0} color="text-blue-600" />
            <StatRow label="Level 1 (直接)" value={result.total_level_1 ?? 0} color="text-green-700" />
            <StatRow label="Level 2 (相似)" value={result.total_level_2 ?? 0} color="text-blue-700" />
            <StatRow label="Level 3 (同類)" value={result.total_level_3 ?? 0} color="text-slate-600" />
          </>
        ) : (
          <>
            <StatRow label="匹配數" value={result.matched ?? 0} color="text-green-600" />
            <StatRow label="跳過" value={result.skipped ?? 0} color="text-slate-500" />
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

// 網絡錯誤友好化
function humanizeError(err: unknown): string {
  if (err instanceof DOMException && err.name === 'TimeoutError') {
    return '請求超時，伺服器處理時間過長。請稍後重試。'
  }
  if (err instanceof TypeError && (err.message === 'Failed to fetch' || err.message === 'Load failed')) {
    return '無法連接伺服器，可能是網絡中斷或伺服器超時。請檢查網絡後重試。'
  }
  if (err instanceof Error) {
    if (err.message.includes('ERR_CONNECTION_CLOSED') || err.message.includes('connection closed')) {
      return '伺服器連接中斷，操作可能耗時過長。請稍後重試。'
    }
    return err.message
  }
  return String(err)
}
