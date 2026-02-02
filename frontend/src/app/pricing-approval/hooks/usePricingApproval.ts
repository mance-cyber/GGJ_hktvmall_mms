// =============================================
// 改價審批 React Query Hooks
// =============================================

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  getPendingProposals,
  approveProposal,
  rejectProposal,
  triggerAIAnalysis,
  PriceProposal,
} from '@/lib/api/pricing'

const QUERY_KEY = 'pending-proposals'

/**
 * 獲取待審批提案列表
 */
export function usePendingProposals() {
  return useQuery({
    queryKey: [QUERY_KEY],
    queryFn: getPendingProposals,
    staleTime: 30 * 1000, // 30 秒內不重新請求
  })
}

/**
 * 批准提案 mutation
 */
export function useApproveProposal() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => approveProposal(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] })
    },
  })
}

/**
 * 拒絕提案 mutation
 */
export function useRejectProposal() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: string) => rejectProposal(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] })
    },
  })
}

/**
 * 觸發 AI 分析 mutation
 */
export function useTriggerAIAnalysis() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: triggerAIAnalysis,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] })
    },
  })
}

/**
 * 批量批准提案
 */
export function useBatchApprove() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (ids: string[]) => {
      const results = await Promise.allSettled(
        ids.map(id => approveProposal(id))
      )

      const succeeded = results.filter(r => r.status === 'fulfilled').length
      const failed = results.filter(r => r.status === 'rejected').length

      return { succeeded, failed, total: ids.length }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] })
    },
  })
}

/**
 * 批量拒絕提案
 */
export function useBatchReject() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (ids: string[]) => {
      const results = await Promise.allSettled(
        ids.map(id => rejectProposal(id))
      )

      const succeeded = results.filter(r => r.status === 'fulfilled').length
      const failed = results.filter(r => r.status === 'rejected').length

      return { succeeded, failed, total: ids.length }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEY] })
    },
  })
}
