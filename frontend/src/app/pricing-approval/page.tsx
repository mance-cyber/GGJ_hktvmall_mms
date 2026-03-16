// =============================================
// Pricing Approval Center Page
// =============================================

'use client'

import { useState, useCallback } from 'react'
import { Sparkles, Loader2, RefreshCw } from 'lucide-react'
import { HoloCard, HoloButton } from '@/components/ui/future-tech'
import { useToast } from '@/components/ui/use-toast'
import { useLocale } from '@/components/providers/locale-provider'
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
  const { t } = useLocale()

  // Data queries
  const { data: proposals = [], isLoading, refetch } = usePendingProposals()

  // Mutations
  const approveProposal = useApproveProposal()
  const rejectProposal = useRejectProposal()
  const batchApprove = useBatchApprove()
  const batchReject = useBatchReject()
  const triggerAI = useTriggerAIAnalysis()

  // Selection state
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  // Approval dialog state
  const [dialogProposal, setDialogProposal] = useState<PriceProposal | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)

  // Selection handling
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

  // Single approve
  const handleApprove = useCallback((id: string) => {
    const proposal = proposals.find((p) => p.id === id)
    if (proposal) {
      setDialogProposal(proposal)
      setDialogOpen(true)
    }
  }, [proposals])

  // Confirm approval (from dialog)
  const handleConfirmApprove = useCallback(async (finalPrice?: number) => {
    if (!dialogProposal) return

    try {
      await approveProposal.mutateAsync(dialogProposal.id)
      toast({
        title: t('pricing.approve_success'),
        description: t('pricing.approve_desc').replace('{name}', dialogProposal.product_name ?? ''),
      })
      setDialogOpen(false)
      setSelectedIds((prev) => {
        const newSet = new Set(prev)
        newSet.delete(dialogProposal.id)
        return newSet
      })
    } catch (error) {
      toast({
        title: t('pricing.approve_failed'),
        description: error instanceof Error ? error.message : t('pricing.retry_later'),
        variant: 'destructive',
      })
    }
  }, [dialogProposal, approveProposal, toast, t])

  // Single reject
  const handleReject = useCallback(async (id: string) => {
    const proposal = proposals.find((p) => p.id === id)
    if (!proposal) return

    try {
      await rejectProposal.mutateAsync(id)
      toast({
        title: t('pricing.rejected'),
        description: t('pricing.reject_desc').replace('{name}', proposal.product_name ?? ''),
      })
      setSelectedIds((prev) => {
        const newSet = new Set(prev)
        newSet.delete(id)
        return newSet
      })
    } catch (error) {
      toast({
        title: t('pricing.reject_failed'),
        description: error instanceof Error ? error.message : t('pricing.retry_later'),
        variant: 'destructive',
      })
    }
  }, [proposals, rejectProposal, toast, t])

  // Batch approve
  const handleBatchApprove = useCallback(async () => {
    if (selectedIds.size === 0) return

    try {
      const result = await batchApprove.mutateAsync(Array.from(selectedIds))
      toast({
        title: t('pricing.batch_approve_done'),
        description: t('pricing.batch_result').replace('{success}', String(result.succeeded)).replace('{failed}', String(result.failed)),
      })
      setSelectedIds(new Set())
    } catch (error) {
      toast({
        title: t('pricing.batch_approve_failed'),
        description: error instanceof Error ? error.message : t('pricing.retry_later'),
        variant: 'destructive',
      })
    }
  }, [selectedIds, batchApprove, toast, t])

  // Batch reject
  const handleBatchReject = useCallback(async () => {
    if (selectedIds.size === 0) return

    try {
      const result = await batchReject.mutateAsync(Array.from(selectedIds))
      toast({
        title: t('pricing.batch_reject_done'),
        description: t('pricing.batch_result').replace('{success}', String(result.succeeded)).replace('{failed}', String(result.failed)),
      })
      setSelectedIds(new Set())
    } catch (error) {
      toast({
        title: t('pricing.batch_reject_failed'),
        description: error instanceof Error ? error.message : t('pricing.retry_later'),
        variant: 'destructive',
      })
    }
  }, [selectedIds, batchReject, toast, t])

  // Trigger AI Analysis
  const handleTriggerAI = useCallback(async () => {
    try {
      const result = await triggerAI.mutateAsync()
      toast({
        title: t('pricing.ai_done'),
        description: t('pricing.ai_result').replace('{count}', String(result.generated_proposals)),
      })
    } catch (error) {
      toast({
        title: t('pricing.ai_failed'),
        description: error instanceof Error ? error.message : t('pricing.retry_later'),
        variant: 'destructive',
      })
    }
  }, [triggerAI, toast, t])

  // Statistics - currently only displaying pending count
  // TODO: Fetch complete statistics from backend
  const stats = {
    pending: proposals.length,
    approved: 0,
    rejected: 0,
    failed: 0,
  }

  return (
    <div className="space-y-6">
      {/* Page title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{t('pricing.title')}</h1>
          <p className="text-gray-500 mt-1">{t('pricing.subtitle')}</p>
        </div>
        <div className="flex items-center gap-2">
          <HoloButton
            variant="secondary"
            onClick={() => refetch()}
            disabled={isLoading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            {t('pricing.refresh')}
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
            {t('pricing.trigger_ai')}
          </HoloButton>
        </div>
      </div>

      {/* Statistics Cards */}
      <ProposalStats {...stats} />

      {/* Proposal List */}
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

      {/* Approval Confirmation Dialog */}
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
