// =============================================
// 提案列表組件
// =============================================

'use client'

import { Check, X, Inbox } from 'lucide-react'
import { Checkbox } from '@/components/ui/checkbox'
import { HoloButton } from '@/components/ui/future-tech'
import { ProposalCard } from './ProposalCard'
import type { PriceProposal } from '@/lib/api/pricing'

interface ProposalListProps {
  proposals: PriceProposal[]
  selectedIds: Set<string>
  onSelect: (id: string) => void
  onSelectAll: () => void
  onApprove: (id: string) => void
  onReject: (id: string) => void
  onBatchApprove: () => void
  onBatchReject: () => void
  isApproving?: boolean
  isRejecting?: boolean
  isBatchApproving?: boolean
  isBatchRejecting?: boolean
}

export function ProposalList({
  proposals,
  selectedIds,
  onSelect,
  onSelectAll,
  onApprove,
  onReject,
  onBatchApprove,
  onBatchReject,
  isApproving,
  isRejecting,
  isBatchApproving,
  isBatchRejecting,
}: ProposalListProps) {
  const allSelected = proposals.length > 0 && selectedIds.size === proposals.length
  const someSelected = selectedIds.size > 0 && selectedIds.size < proposals.length
  const hasSelection = selectedIds.size > 0

  // 空狀態
  if (proposals.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <Inbox className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">暫無待審批提案</h3>
        <p className="text-gray-500 max-w-sm">
          目前沒有需要審批的改價提案。點擊上方「觸發 AI 分析」按鈕生成新的提案。
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* 全選控制 */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-50 rounded-lg">
        <div className="flex items-center gap-3">
          <Checkbox
            checked={allSelected}
            // @ts-ignore - indeterminate 屬性
            indeterminate={someSelected}
            onCheckedChange={onSelectAll}
          />
          <span className="text-sm text-gray-600">
            {allSelected ? '取消全選' : '全選'}
          </span>
        </div>

        {hasSelection && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500 mr-2">
              已選 {selectedIds.size} 項
            </span>
            <HoloButton
              variant="primary"
              size="sm"
              onClick={onBatchApprove}
              disabled={isBatchApproving || isBatchRejecting}
              className="bg-green-500 hover:bg-green-600 text-white"
            >
              <Check className="w-4 h-4 mr-1" />
              批量批准
            </HoloButton>
            <HoloButton
              variant="secondary"
              size="sm"
              onClick={onBatchReject}
              disabled={isBatchApproving || isBatchRejecting}
              className="hover:bg-red-50 hover:text-red-600"
            >
              <X className="w-4 h-4 mr-1" />
              批量拒絕
            </HoloButton>
          </div>
        )}
      </div>

      {/* 提案列表 */}
      <div className="space-y-3">
        {proposals.map((proposal) => (
          <ProposalCard
            key={proposal.id}
            proposal={proposal}
            isSelected={selectedIds.has(proposal.id)}
            onSelect={onSelect}
            onApprove={onApprove}
            onReject={onReject}
            isApproving={isApproving}
            isRejecting={isRejecting}
          />
        ))}
      </div>
    </div>
  )
}
