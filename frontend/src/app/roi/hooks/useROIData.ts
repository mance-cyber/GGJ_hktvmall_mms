// =============================================
// ROI 數據 React Query Hooks
// =============================================

'use client'

import { useQuery } from '@tanstack/react-query'
import {
  getROISummary,
  getROITrends,
  getPricingImpact,
  getCompetitorInsights,
  type ROIPeriod,
  type ROISummary,
  type ROITrendsResponse,
  type PricingImpactResponse,
  type CompetitorInsights,
} from '@/lib/api/roi'

// ==================== Query Keys ====================

export const roiKeys = {
  all: ['roi'] as const,
  summary: (period: ROIPeriod) => [...roiKeys.all, 'summary', period] as const,
  trends: (days: number) => [...roiKeys.all, 'trends', days] as const,
  pricingImpact: (limit: number) => [...roiKeys.all, 'pricing-impact', limit] as const,
  competitorInsights: (period: ROIPeriod) => [...roiKeys.all, 'competitor-insights', period] as const,
}

// ==================== Hooks ====================

/**
 * 獲取 ROI 總覽
 */
export function useROISummary(period: ROIPeriod = 'month') {
  return useQuery<ROISummary>({
    queryKey: roiKeys.summary(period),
    queryFn: () => getROISummary(period),
    staleTime: 5 * 60 * 1000, // 5 分鐘緩存
  })
}

/**
 * 獲取 ROI 趨勢數據
 */
export function useROITrends(days: number = 30) {
  return useQuery<ROITrendsResponse>({
    queryKey: roiKeys.trends(days),
    queryFn: () => getROITrends(days),
    staleTime: 5 * 60 * 1000,
  })
}

/**
 * 獲取 AI 改價影響
 */
export function usePricingImpact(limit: number = 10) {
  return useQuery<PricingImpactResponse>({
    queryKey: roiKeys.pricingImpact(limit),
    queryFn: () => getPricingImpact(limit),
    staleTime: 5 * 60 * 1000,
  })
}

/**
 * 獲取競品監測洞察
 */
export function useCompetitorInsights(period: ROIPeriod = 'month') {
  return useQuery<CompetitorInsights>({
    queryKey: roiKeys.competitorInsights(period),
    queryFn: () => getCompetitorInsights(period),
    staleTime: 5 * 60 * 1000,
  })
}
