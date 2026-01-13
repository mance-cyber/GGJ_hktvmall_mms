'use client'

import { useState } from 'react'
import { api, BatchResultItem, GeneratedContent } from '@/lib/api'
import {
  Check,
  X,
  AlertCircle,
  Loader2,
  Download,
  Eye,
  ChevronRight,
  Copy,
  ExternalLink,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'
import {
  HoloCard,
  HoloBadge,
  HoloButton,
} from '@/components/ui/future-tech'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

interface BatchResultListProps {
  results: BatchResultItem[]
  isProcessing?: boolean
  progress?: {
    total: number
    completed: number
    failed: number
    percent: number
  }
  onViewDetail?: (contentId: string) => void
  className?: string
}

export function BatchResultList({
  results,
  isProcessing = false,
  progress,
  onViewDetail,
  className,
}: BatchResultListProps) {
  const [selectedResult, setSelectedResult] = useState<BatchResultItem | null>(null)
  const [copiedField, setCopiedField] = useState<string | null>(null)

  // 統計
  const successCount = results.filter((r) => r.success).length
  const failedCount = results.filter((r) => !r.success).length
  const successIds = results.filter((r) => r.success && r.content_id).map((r) => r.content_id!)

  // 導出 CSV
  const handleExport = () => {
    if (successIds.length === 0) return
    const url = api.exportContentCsv(successIds)
    window.open(url, '_blank')
  }

  // 複製文本
  const handleCopy = async (text: string, field: string) => {
    await navigator.clipboard.writeText(text)
    setCopiedField(field)
    setTimeout(() => setCopiedField(null), 2000)
  }

  // 查看詳情
  const handleViewDetail = (result: BatchResultItem) => {
    if (result.success && result.content_id && onViewDetail) {
      onViewDetail(result.content_id)
    } else {
      setSelectedResult(result)
    }
  }

  if (results.length === 0 && !isProcessing) {
    return null
  }

  return (
    <div className={cn('space-y-4', className)}>
      {/* 進度條（異步模式） */}
      {isProcessing && progress && (
        <div className="p-4 bg-slate-50 rounded-lg space-y-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-600 flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin text-cyan-500" />
              正在生成中...
            </span>
            <span className="font-medium text-slate-700">
              {progress.completed + progress.failed} / {progress.total}
            </span>
          </div>
          <Progress value={progress.percent} className="h-2" />
          <div className="flex items-center gap-4 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <Check className="w-3 h-3 text-green-500" /> 成功: {progress.completed}
            </span>
            {progress.failed > 0 && (
              <span className="flex items-center gap-1">
                <X className="w-3 h-3 text-red-500" /> 失敗: {progress.failed}
              </span>
            )}
          </div>
        </div>
      )}

      {/* 摘要和操作 */}
      {results.length > 0 && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-sm text-slate-600">生成結果</span>
            {successCount > 0 && (
              <HoloBadge variant="success">
                <Check className="w-3 h-3 mr-1" /> {successCount} 成功
              </HoloBadge>
            )}
            {failedCount > 0 && (
              <HoloBadge variant="error">
                <X className="w-3 h-3 mr-1" /> {failedCount} 失敗
              </HoloBadge>
            )}
          </div>

          {successIds.length > 0 && (
            <HoloButton
              variant="secondary"
              size="sm"
              onClick={handleExport}
              icon={<Download className="w-4 h-4" />}
            >
              導出 CSV
            </HoloButton>
          )}
        </div>
      )}

      {/* 結果列表 */}
      {results.length > 0 && (
        <div className="border border-slate-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left font-medium text-slate-600 w-12">狀態</th>
                <th className="px-4 py-3 text-left font-medium text-slate-600">商品名稱</th>
                <th className="px-4 py-3 text-left font-medium text-slate-600">生成標題</th>
                <th className="px-4 py-3 text-center font-medium text-slate-600 w-24">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {results.map((result, index) => (
                <tr
                  key={index}
                  className={cn(
                    'transition-colors',
                    result.success ? 'hover:bg-slate-50' : 'bg-red-50/50'
                  )}
                >
                  <td className="px-4 py-3">
                    {result.success ? (
                      <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center">
                        <Check className="w-4 h-4 text-green-600" />
                      </div>
                    ) : (
                      <div className="w-6 h-6 rounded-full bg-red-100 flex items-center justify-center">
                        <X className="w-4 h-4 text-red-600" />
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className="font-medium text-slate-900">{result.product_name}</span>
                    {!result.success && result.error && (
                      <p className="text-xs text-red-600 mt-1">{result.error}</p>
                    )}
                  </td>
                  <td className="px-4 py-3 text-slate-600">
                    {result.content?.title ? (
                      <span className="line-clamp-1">{result.content.title}</span>
                    ) : (
                      <span className="text-slate-400">-</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleViewDetail(result)}
                      className="text-slate-500 hover:text-cyan-600"
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 詳情彈窗 */}
      <Dialog open={!!selectedResult} onOpenChange={() => setSelectedResult(null)}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {selectedResult?.success ? (
                <Check className="w-5 h-5 text-green-500" />
              ) : (
                <AlertCircle className="w-5 h-5 text-red-500" />
              )}
              {selectedResult?.product_name}
            </DialogTitle>
          </DialogHeader>

          {selectedResult && (
            <div className="space-y-4 pt-4">
              {selectedResult.success && selectedResult.content ? (
                <>
                  {/* 標題 */}
                  {selectedResult.content.title && (
                    <ContentSection
                      label="標題"
                      content={selectedResult.content.title}
                      onCopy={(text) => handleCopy(text, 'title')}
                      isCopied={copiedField === 'title'}
                    />
                  )}

                  {/* 賣點 */}
                  {selectedResult.content.selling_points &&
                    selectedResult.content.selling_points.length > 0 && (
                      <ContentSection
                        label="賣點"
                        content={selectedResult.content.selling_points.join('\n')}
                        onCopy={(text) => handleCopy(text, 'points')}
                        isCopied={copiedField === 'points'}
                        isList
                        listItems={selectedResult.content.selling_points}
                      />
                    )}

                  {/* 描述 */}
                  {selectedResult.content.description && (
                    <ContentSection
                      label="描述"
                      content={selectedResult.content.description}
                      onCopy={(text) => handleCopy(text, 'desc')}
                      isCopied={copiedField === 'desc'}
                    />
                  )}

                  {/* 跳轉到編輯 */}
                  {selectedResult.content_id && onViewDetail && (
                    <div className="pt-4 border-t border-slate-200">
                      <Button
                        onClick={() => {
                          setSelectedResult(null)
                          onViewDetail(selectedResult.content_id!)
                        }}
                        className="w-full"
                      >
                        <ExternalLink className="w-4 h-4 mr-2" />
                        前往編輯優化
                      </Button>
                    </div>
                  )}
                </>
              ) : (
                <div className="p-4 bg-red-50 rounded-lg">
                  <p className="text-sm text-red-700">
                    <span className="font-medium">錯誤原因：</span>
                    {selectedResult.error || '未知錯誤'}
                  </p>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

// 內容區塊組件
function ContentSection({
  label,
  content,
  onCopy,
  isCopied,
  isList = false,
  listItems = [],
}: {
  label: string
  content: string
  onCopy: (text: string) => void
  isCopied: boolean
  isList?: boolean
  listItems?: string[]
}) {
  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden">
      <div className="flex items-center justify-between px-4 py-2 bg-slate-50 border-b border-slate-200">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
          {label}
        </span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onCopy(content)}
          className="h-6 px-2 text-slate-400 hover:text-cyan-600"
        >
          {isCopied ? (
            <>
              <Check className="w-3 h-3 mr-1" />
              已複製
            </>
          ) : (
            <>
              <Copy className="w-3 h-3 mr-1" />
              複製
            </>
          )}
        </Button>
      </div>
      <div className="p-4 text-sm text-slate-700">
        {isList ? (
          <ul className="space-y-2">
            {listItems.map((item, index) => (
              <li key={index} className="flex items-start">
                <ChevronRight className="w-4 h-4 mr-2 mt-0.5 text-cyan-400 flex-shrink-0" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="whitespace-pre-wrap">{content}</p>
        )}
      </div>
    </div>
  )
}
