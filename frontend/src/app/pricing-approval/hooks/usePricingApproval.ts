// =============================================
// Pricing Approval React Query Hooks
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
 * Fetch pending proposal list
 */
export function usePendingProposals() {
  return useQuery({
    queryKey: [QUERY_KEY],
    queryFn: getPendingProposals,
    staleTime: 30 * 1000, // Don't re-fetch within 30 seconds
  })
}

/**
 * Approve proposal mutation
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
 * Reject proposal mutation
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
 * Trigger AI Analysis mutation
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
 * Batch approve proposals
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
 * Batch reject proposals
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
