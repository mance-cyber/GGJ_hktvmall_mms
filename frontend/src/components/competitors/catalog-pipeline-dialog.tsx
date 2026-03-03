'use client'

import { useState, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import {
  Loader2,
  CheckCircle2,
  XCircle,
  Database,
  Play,
  RotateCcw,
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
}

const STEPS = ['build', 'tag', 'match'] as const
type StepKey = typeof STEPS[number]

export function CatalogPipelineDialog() {
  const { t } = useLocale()
  const queryClient = useQueryClient()

  const [open, setOpen] = useState(false)
  const [platform, setPlatform] = useState('all')
  const [phase, setPhase] = useState<PipelinePhase>('idle')
  const [failedStep, setFailedStep] = useState<StepKey | null>(null)
  const [steps, setSteps] = useState<Record<StepKey, StepResult>>({
    build: { status: 'pending' },
    tag: { status: 'pending' },
    match: { status: 'pending' },
  })

  const resetState = useCallback(() => {
    setPhase('idle')
    setFailedStep(null)
    setSteps({
      build: { status: 'pending' },
      tag: { status: 'pending' },
      match: { status: 'pending' },
    })
  }, [])

  // 更新單步狀態（不可變）
  const updateStep = useCallback((key: StepKey, patch: Partial<StepResult>) => {
    setSteps(prev => ({ ...prev, [key]: { ...prev[key], ...patch } }))
  }, [])

  // 執行三步流程，支持從指定步驟開始（重試場景）
  const runPipeline = useCallback(async (startFrom: StepKey = 'build') => {
    const startIndex = STEPS.indexOf(startFrom)
    setFailedStep(null)

    // 重置從 startFrom 開始的步驟狀態
    for (let i = startIndex; i < STEPS.length; i++) {
      updateStep(STEPS[i], { status: 'pending', error: undefined, data: undefined })
    }

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
      setPhase(phaseMap[step])
      updateStep(step, { status: 'running' })

      try {
        const result = await apiCalls[step]()
        updateStep(step, { status: 'done', data: result })
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : String(err)
        updateStep(step, { status: 'error', error: errorMsg })
        setPhase('error')
        setFailedStep(step)
        return
      }
    }

    setPhase('done')
    queryClient.invalidateQueries({ queryKey: ['competitors'] })
  }, [platform, updateStep, queryClient])

  const handleDialogClose = useCallback((nextOpen: boolean) => {
    if (!nextOpen) {
      resetState()
    }
    setOpen(nextOpen)
  }, [resetState])

  // 步驟指示器標籤
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

  const isRunning = phase === 'building' || phase === 'tagging' || phase === 'matching'

  return (
    <Dialog open={open} onOpenChange={handleDialogClose}>
      <DialogTrigger asChild>
        <HoloButton variant="primary" size="sm" icon={<Database className="w-4 h-4" />}>
          <span className="hidden sm:inline">{t['competitors.catalog_build']}</span>
        </HoloButton>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{t['competitors.catalog_title']}</DialogTitle>
          <DialogDescription>{t['competitors.catalog_desc']}</DialogDescription>
        </DialogHeader>

        {/* idle：平台選擇 */}
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
          </div>
        )}

        {/* 執行中 / 完成 / 錯誤：三步驟指示器 */}
        {phase !== 'idle' && (
          <div className="space-y-4 py-4">
            {/* 步驟指示器 */}
            <div className="space-y-3">
              {STEPS.map((step) => {
                const s = steps[step]
                return (
                  <div
                    key={step}
                    className="flex items-center gap-3 rounded-lg border px-3 py-2.5 transition-colors"
                    style={{
                      borderColor: s.status === 'running' ? 'rgb(59 130 246 / 0.5)' :
                                   s.status === 'error' ? 'rgb(239 68 68 / 0.5)' :
                                   s.status === 'done' ? 'rgb(34 197 94 / 0.5)' :
                                   'rgb(226 232 240)',
                      backgroundColor: s.status === 'running' ? 'rgb(239 246 255)' :
                                       s.status === 'error' ? 'rgb(254 242 242)' :
                                       s.status === 'done' ? 'rgb(240 253 244)' :
                                       'transparent',
                    }}
                  >
                    {/* 狀態圖標 */}
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
                      <div className="w-4 h-4 rounded-full border-2 border-slate-300 flex-shrink-0" />
                    )}

                    {/* 步驟名稱 */}
                    <span className="text-sm font-medium flex-1">
                      {stepLabels[step]}
                    </span>

                    {/* 結果摘要（完成時顯示統計） */}
                    {s.status === 'done' && s.data?.result && (
                      <span className="text-xs text-muted-foreground">
                        {formatStepResult(step, s.data.result, t)}
                      </span>
                    )}
                    {s.status === 'error' && (
                      <span className="text-xs text-red-500 truncate max-w-[160px]">
                        {s.error}
                      </span>
                    )}
                  </div>
                )
              })}
            </div>

            {/* 當前階段文字 */}
            {isRunning && (
              <p className="text-sm text-muted-foreground text-center">
                {phaseLabels[phase]}
              </p>
            )}

            {/* 完成摘要 */}
            {phase === 'done' && (
              <div className="rounded-lg bg-green-50 border border-green-200 p-3 text-sm text-green-700">
                <p className="font-medium">{t['competitors.catalog_done']}</p>
              </div>
            )}

            {/* 錯誤提示 */}
            {phase === 'error' && (
              <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                <p className="font-medium">{t['competitors.catalog_error']}</p>
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
            <Button variant="outline" disabled>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              {phaseLabels[phase]}
            </Button>
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
// 格式化步驟結果摘要
// =============================================

function formatStepResult(
  step: StepKey,
  result: any,
  t: Record<string, string>,
): string {
  if (!result) return ''

  switch (step) {
    case 'build': {
      const added = result.added ?? result.new ?? 0
      const updated = result.updated ?? 0
      return `${t['competitors.catalog_new']} ${added} / ${t['competitors.catalog_updated']} ${updated}`
    }
    case 'tag': {
      const tagged = result.tagged ?? result.count ?? 0
      return `${tagged} ${t['competitors.catalog_step_tag']}`
    }
    case 'match': {
      const matched = result.matched ?? result.count ?? 0
      return `${matched} ${t['competitors.catalog_matched']}`
    }
    default:
      return ''
  }
}
