// =============================================
// 改價審批中心頁面
// =============================================

'use client'

import { useState, useCallback } from 'react'
import { Sparkles, Loader2, RefreshCw } from 'lucide-react'
import { HoloCard, HoloButton } from '@/components/ui/future-tech'
import { useToast } from '@/components/ui/use-toast'
import { ProposalStats } from './components/ProposalStats'
import { ProposalList } from './components/ProposalList'
import { ApprovalDialog } from './components/ApprovalDialog'
import {
  usePendingProposals,
  useApproveProposal,
  useRejectProposal,
  useBatchApprove,
  useBatchReject,
  useTriggerAIAnalysis,
} from './hooks/usePricingApproval'
import type { PriceProposal } from '@/lib/api/pricing'

export default function PricingApprovalPage() {
  const { toast } = useToast()

  // 數據查詢
  const { data: proposals = [], isLoading, refetch } = usePendingProposals()

  // Mutations
  const approveProposal = useApproveProposal()
  const rejectProposal = useRejectProposal()
  const batchApprove = useBatchApprove()
  const batchReject = useBatchReject()
  const triggerAI = useTriggerAIAnalysis()

  // 選擇狀態
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  // 審批對話框狀態
  const [dialogProposal, setDialogProposal] = useState<PriceProposal | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)

  // 選擇處理
  const handleSelect = useCallback((id: string) => {
    setSelectedIds((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }, [])

  const handleSelectAll = useCallback(() => {
    if (selectedIds.size === proposals.length) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(proposals.map((p) => p.id)))
    }
  }, [proposals, selectedIds.size])

  // 單個批准
  const handleApprove = useCallback((id: string) => {
    const proposal = proposals.find((p) => p.id === id)
    if (proposal) {
      setDialogProposal(proposal)
      setDialogOpen(true)
    }
  }, [proposals])

  // 確認批准（從對話框）
  const handleConfirmApprove = useCallback(async (finalPrice?: number) => {
    if (!dialogProposal) return

    try {
      await approveProposal.mutateAsync(dialogProposal.id)
      toast({
        title: '批准成功',
        description: `已批准「${dialogProposal.product_name}」的改價提案`,
      })
      setDialogOpen(false)
      setSelectedIds((prev) => {
        const newSet = new Set(prev)
        newSet.delete(dialogProposal.id)
        return newSet
      })
    } catch (error) {
      toast({
        title: '批准失敗',
        description: error instanceof Error ? error.message : '請稍後重試',
        variant: 'destructive',
      })
    }
  }, [dialogProposal, approveProposal, toast])

  // 單個拒絕
  const handleReject = useCallback(async (id: string) => {
    const proposal = proposals.find((p) => p.id === id)
    if (!proposal) return

    try {
      await rejectProposal.mutateAsync(id)
      toast({
        title: '已拒絕',
        description: `已拒絕「${proposal.product_name}」的改價提案`,
      })
      setSelectedIds((prev) => {
        const newSet = new Set(prev)
        newSet.delete(id)
        return newSet
      })
    } catch (error) {
      toast({
        title: '拒絕失敗',
        description: error instanceof Error ? error.message : '請稍後重試',
        variant: 'destructive',
      })
    }
  }, [proposals, rejectProposal, toast])

  // 批量批准
  const handleBatchApprove = useCallback(async () => {
    if (selectedIds.size === 0) return

    try {
      const result = await batchApprove.mutateAsync(Array.from(selectedIds))
      toast({
        title: '批量批准完成',
        description: `成功 ${result.succeeded} 項，失敗 ${result.failed} 項`,
      })
      setSelectedIds(new Set())
    } catch (error) {
      toast({
        title: '批量批准失敗',
        description: error instanceof Error ? error.message : '請稍後重試',
        variant: 'destructive',
      })
    }
  }, [selectedIds, batchApprove, toast])

  // 批量拒絕
  const handleBatchReject = useCallback(async () => {
    if (selectedIds.size === 0) return

    try {
      const result = await batchReject.mutateAsync(Array.from(selectedIds))
      toast({
        title: '批量拒絕完成',
        description: `成功 ${result.succeeded} 項，失敗 ${result.failed} 項`,
      })
      setSelectedIds(new Set())
    } catch (error) {
      toast({
        title: '批量拒絕失敗',
        description: error instanceof Error ? error.message : '請稍後重試',
        variant: 'destructive',
      })
    }
  }, [selectedIds, batchReject, toast])

  // 觸發 AI 分析
  const handleTriggerAI = useCallback(async () => {
    try {
      const result = await triggerAI.mutateAsync()
      toast({
        title: 'AI 分析完成',
        description: `已生成 ${result.generated_proposals} 個新提案`,
      })
    } catch (error) {
      toast({
        title: 'AI 分析失敗',
        description: error instanceof Error ? error.message : '請稍後重試',
        variant: 'destructive',
      })
    }
  }, [triggerAI, toast])

  // 統計數據 - 暫時只顯示 pending 數量
  // TODO: 從後端獲取完整統計
  const stats = {
    pending: proposals.length,
    approved: 0,
    rejected: 0,
    failed: 0,
  }

  return (
    <div className="space-y-6">
      {/* 頁面標題 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">改價審批中心</h1>
          <p className="text-gray-500 mt-1">審核 AI 生成的改價提案，批准後自動更新 HKTVmall 價格</p>
        </div>
        <div className="flex items-center gap-2">
          <HoloButton
            variant="secondary"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            刷新
          </HoloButton>
          <HoloButton
            variant="primary"
            onClick={handleTriggerAI}
            disabled={triggerAI.isPending}
          >
            {triggerAI.isPending ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Sparkles className="w-4 h-4 mr-2" />
            )}
            觸發 AI 分析
          </HoloButton>
        </div>
      </div>

      {/* 統計卡片 */}
      <ProposalStats {...stats} />

      {/* 提案列表 */}
      <HoloCard className="p-6">
        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
          </div>
        ) : (
          <ProposalList
            proposals={proposals}
            selectedIds={selectedIds}
            onSelect={handleSelect}
            onSelectAll={handleSelectAll}
            onApprove={handleApprove}
            onReject={handleReject}
            onBatchApprove={handleBatchApprove}
            onBatchReject={handleBatchReject}
            isApproving={approveProposal.isPending}
            isRejecting={rejectProposal.isPending}
            isBatchApproving={batchApprove.isPending}
            isBatchRejecting={batchReject.isPending}
          />
        )}
      </HoloCard>

      {/* 批准確認對話框 */}
      <ApprovalDialog
        proposal={dialogProposal}
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        onConfirm={handleConfirmApprove}
        isLoading={approveProposal.isPending}
      />
    </div>
  )
}
