'use client'

import { useState, useRef, useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import {
  Loader2,
  Play,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Bot,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { useToast } from '@/components/ui/use-toast'
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

// =============================================
// 批量競品匹配 Dialog（可複用組件）
// =============================================

interface BatchResultItem {
  product_id: string
  product_name: string
  candidates: number
  matches: number
  match_details: { name: string; confidence: number; url: string }[]
  error?: string
  status: 'searching' | 'done' | 'error'
}

interface BatchSummary {
  processed: number
  total_matches: number
  total_candidates: number
}

type BatchPhase = 'idle' | 'processing' | 'done'

export function BatchMatchDialog({
  trigger,
  invalidateKeys = [],
}: {
  trigger?: React.ReactNode
  invalidateKeys?: string[][]
}) {
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const [open, setOpen] = useState(false)
  const [batchLimit, setBatchLimit] = useState('10')
  const [batchCategory, setBatchCategory] = useState('all')
  const [batchPlatform, setBatchPlatform] = useState('hktvmall')

  const [batchPhase, setBatchPhase] = useState<BatchPhase>('idle')
  const [batchCurrent, setBatchCurrent] = useState(0)
  const [batchTotal, setBatchTotal] = useState(0)
  const [batchCurrentName, setBatchCurrentName] = useState('')
  const [batchResults, setBatchResults] = useState<BatchResultItem[]>([])
  const [batchSummary, setBatchSummary] = useState<BatchSummary | null>(null)
  const abortRef = useRef<AbortController | null>(null)
  const resultsEndRef = useRef<HTMLDivElement>(null)

  const resetBatchState = useCallback(() => {
    setBatchPhase('idle')
    setBatchCurrent(0)
    setBatchTotal(0)
    setBatchCurrentName('')
    setBatchResults([])
    setBatchSummary(null)
  }, [])

  // SSE 批量匹配
  const handleBatchMatch = useCallback(async () => {
    const limit = parseInt(batchLimit)
    const categoryMain = batchCategory === 'all' ? undefined : batchCategory

    setBatchPhase('processing')
    setBatchCurrent(0)
    setBatchTotal(limit)
    setBatchCurrentName('')
    setBatchResults([])
    setBatchSummary(null)

    const controller = new AbortController()
    abortRef.current = controller

    try {
      const url = api.batchFindCompetitorsStreamUrl(limit, categoryMain, batchPlatform)
      const response = await fetch(url, {
        method: 'POST',
        signal: controller.signal,
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body?.getReader()
      if (!reader) throw new Error('無法讀取串流')

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        let currentEvent = ''
        for (const line of lines) {
          if (line.startsWith('event: ')) {
            currentEvent = line.slice(7).trim()
          } else if (line.startsWith('data: ') && currentEvent) {
            try {
              const data = JSON.parse(line.slice(6))

              if (currentEvent === 'progress') {
                setBatchCurrent(data.current)
                setBatchTotal(data.total)
                setBatchCurrentName(data.product_name)
              } else if (currentEvent === 'result') {
                setBatchResults(prev => [...prev, {
                  product_id: data.product_id,
                  product_name: data.product_name,
                  candidates: data.candidates,
                  matches: data.matches,
                  match_details: data.match_details || [],
                  error: data.error,
                  status: data.error ? 'error' : 'done',
                }])
                setTimeout(() => resultsEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 50)
              } else if (currentEvent === 'done') {
                setBatchSummary(data)
                setBatchPhase('done')
                // 刷新相關查詢
                for (const key of invalidateKeys) {
                  queryClient.invalidateQueries({ queryKey: key })
                }
                queryClient.invalidateQueries({ queryKey: ['competitors'] })
              }
            } catch {
              // 忽略 JSON 解析失敗
            }
            currentEvent = ''
          }
        }
      }
    } catch (err: any) {
      if (err.name === 'AbortError') return
      toast({
        title: '批量匹配失敗',
        description: err.message,
        variant: 'destructive',
      })
      setBatchPhase('idle')
    }
  }, [batchLimit, batchCategory, batchPlatform, queryClient, toast, invalidateKeys])

  const handleDialogClose = useCallback((nextOpen: boolean) => {
    if (!nextOpen) {
      if (batchPhase === 'processing') {
        abortRef.current?.abort()
      }
      resetBatchState()
    }
    setOpen(nextOpen)
  }, [batchPhase, resetBatchState])

  return (
    <Dialog open={open} onOpenChange={handleDialogClose}>
      <DialogTrigger asChild>
        {trigger || (
          <HoloButton variant="primary" size="sm" icon={<Bot className="w-4 h-4" />}>
            <span className="hidden sm:inline">批量匹配</span>
            <span className="sm:hidden">匹配</span>
          </HoloButton>
        )}
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>批量競品匹配</DialogTitle>
          <DialogDescription>
            自動搜索競品平台上的競爭商品，並使用 AI 智能判斷是否為同級商品
          </DialogDescription>
        </DialogHeader>

        {/* 設定區：idle 時顯示 */}
        {batchPhase === 'idle' && (
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">處理數量</label>
              <Select value={batchLimit} onValueChange={setBatchLimit}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10 個商品（測試）</SelectItem>
                  <SelectItem value="20">20 個商品</SelectItem>
                  <SelectItem value="30">30 個商品</SelectItem>
                  <SelectItem value="50">50 個商品</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">目標平台</label>
              <Select value={batchPlatform} onValueChange={setBatchPlatform}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="hktvmall">HKTVmall</SelectItem>
                  <SelectItem value="wellcome">惠康 Wellcome</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">分類篩選（可選）</label>
              <Select value={batchCategory} onValueChange={setBatchCategory}>
                <SelectTrigger>
                  <SelectValue placeholder="選擇分類" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">全部分類</SelectItem>
                  <SelectItem value="鮮魚">鮮魚</SelectItem>
                  <SelectItem value="貝類">貝類</SelectItem>
                  <SelectItem value="蟹類">蟹類</SelectItem>
                  <SelectItem value="其他海鮮">其他海鮮</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="rounded-lg bg-blue-50 p-3 text-sm text-blue-700">
              <p className="font-medium mb-1">預估成本</p>
              <p className="text-xs">
                {parseInt(batchLimit)} 個商品 ≈ ¥{(parseInt(batchLimit) * 0.04).toFixed(2)} (Claude API)
                {batchPlatform === 'hktvmall' && <><br />+ Firecrawl API 額度</>}
                {batchPlatform === 'wellcome' && <><br />惠康使用 JSON-LD 提取，零額外成本</>}
              </p>
            </div>
            <div className="rounded-lg bg-yellow-50 p-3 text-sm text-yellow-700">
              <p className="font-medium mb-1">注意事項</p>
              <p className="text-xs">
                • 只會處理尚未匹配競品的商品<br />
                • 執行時間約 {Math.ceil(parseInt(batchLimit) / 5)} 分鐘<br />
                • 建議先執行 10 個商品測試
              </p>
            </div>
          </div>
        )}

        {/* 進度區：processing / done 時顯示 */}
        {(batchPhase === 'processing' || batchPhase === 'done') && (
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">
                  {batchPhase === 'processing' ? (
                    <span className="flex items-center gap-1.5">
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      正在搜索: {batchCurrentName}
                    </span>
                  ) : (
                    <span className="flex items-center gap-1.5 text-green-600">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      匹配完成
                    </span>
                  )}
                </span>
                <span className="font-medium tabular-nums">
                  {batchPhase === 'done' ? batchSummary?.processed : batchCurrent}/{batchTotal}
                </span>
              </div>
              <Progress
                value={batchPhase === 'done' ? 100 : (batchTotal > 0 ? (batchCurrent / batchTotal) * 100 : 0)}
              />
            </div>

            <div className="max-h-[240px] overflow-y-auto rounded-lg border bg-slate-50/50 divide-y divide-slate-100">
              {batchResults.length === 0 && batchPhase === 'processing' && (
                <div className="p-4 text-center text-sm text-muted-foreground">
                  等待第一個結果...
                </div>
              )}
              {batchResults.map((item, idx) => (
                <div key={idx} className="px-3 py-2 text-sm flex items-start gap-2">
                  {item.error ? (
                    <XCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
                  ) : item.matches > 0 ? (
                    <CheckCircle2 className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                  )}
                  <div className="flex-1 min-w-0">
                    <span className="font-medium text-slate-700 truncate block">
                      {item.product_name}
                    </span>
                    {item.error ? (
                      <span className="text-xs text-red-500">錯誤: {item.error}</span>
                    ) : item.matches > 0 && item.match_details[0] ? (
                      <span className="text-xs text-green-600">
                        → {item.match_details[0].name}{' '}
                        <span className="font-medium">
                          {Math.round(item.match_details[0].confidence * 100)}%
                        </span>
                      </span>
                    ) : (
                      <span className="text-xs text-muted-foreground">
                        {item.candidates > 0 ? `找到 ${item.candidates} 個候選，但無匹配` : '未找到匹配'}
                      </span>
                    )}
                  </div>
                </div>
              ))}
              <div ref={resultsEndRef} />
            </div>

            {batchPhase === 'done' && batchSummary && (
              <div className="rounded-lg bg-green-50 border border-green-200 p-3 text-sm text-green-700">
                <p className="font-medium mb-1">匹配完成</p>
                <div className="flex gap-4 text-xs">
                  <span>處理 {batchSummary.processed} 個</span>
                  <span>候選 {batchSummary.total_candidates} 個</span>
                  <span className="font-medium">匹配 {batchSummary.total_matches} 個</span>
                </div>
              </div>
            )}
          </div>
        )}

        <DialogFooter>
          {batchPhase === 'idle' && (
            <>
              <Button variant="outline" onClick={() => handleDialogClose(false)}>
                取消
              </Button>
              <Button onClick={handleBatchMatch}>
                <Play className="mr-2 h-4 w-4" />
                開始匹配
              </Button>
            </>
          )}
          {batchPhase === 'processing' && (
            <Button variant="outline" onClick={() => {
              abortRef.current?.abort()
              setBatchPhase('done')
            }}>
              停止
            </Button>
          )}
          {batchPhase === 'done' && (
            <Button onClick={() => handleDialogClose(false)}>
              關閉
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
