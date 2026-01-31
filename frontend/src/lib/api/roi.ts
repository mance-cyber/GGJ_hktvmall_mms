// =============================================
// ROI 分析 API 客戶端
// =============================================

import { apiClient } from './client'

// ==================== Types ====================

export interface ROISummary {
  total_value_generated: number
  ai_pricing_contribution: number
  competitor_monitoring_value: number
  risk_avoidance_value: number
  roi_percentage: number
  period_start: string
  period_end: string
}

export interface ROITrendPoint {
  date: string
  cumulative_value: number
  ai_pricing: number
  monitoring: number
  risk_avoidance: number
}

export interface ROITrendsResponse {
  trends: ROITrendPoint[]
  start_date: string
  end_date: string
  granularity: string
}

export interface PricingProposalImpact {
  id: string
  product_name: string
  old_price: number
  new_price: number
  price_diff: number
  impact: number
  executed_at: string
}

export interface PricingImpactSummary {
  total_proposals: number
  executed_count: number
  approved_count: number
  rejected_count: number
  total_impact: number
}

export interface PricingImpactResponse {
  proposals: PricingProposalImpact[]
  summary: PricingImpactSummary
}

export interface CompetitorInsights {
  price_alerts_triggered: number
  price_drops_detected: number
  price_increases_detected: number
  avg_response_time_hours: number | null
  potential_savings: number
  period: string
}

export type ROIPeriod = 'today' | 'week' | 'month' | 'quarter'

// ==================== API Functions ====================

/**
 * 獲取 ROI 總覽
 */
export async function getROISummary(period: ROIPeriod = 'month'): Promise<ROISummary> {
  const response = await apiClient.get('/roi/summary', {
    params: { period }
  })
  return response as unknown as ROISummary
}

/**
 * 獲取 ROI 趨勢數據
 */
export async function getROITrends(
  days: number = 30,
  granularity: 'day' | 'week' | 'month' = 'day'
): Promise<ROITrendsResponse> {
  const response = await apiClient.get('/roi/trends', {
    params: { days, granularity }
  })
  return response as unknown as ROITrendsResponse
}

/**
 * 獲取 AI 改價影響分析
 */
export async function getPricingImpact(limit: number = 10): Promise<PricingImpactResponse> {
  const response = await apiClient.get('/roi/pricing-impact', {
    params: { limit }
  })
  return response as unknown as PricingImpactResponse
}

/**
 * 獲取競品監測洞察
 */
export async function getCompetitorInsights(period: ROIPeriod = 'month'): Promise<CompetitorInsights> {
  const response = await apiClient.get('/roi/competitor-insights', {
    params: { period }
  })
  return response as unknown as CompetitorInsights
}
