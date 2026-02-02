// =============================================
// 改價審批 API 客戶端
// =============================================

import { apiClient } from './client'

// ==================== Types ====================

export type ProposalStatus = 'pending' | 'approved' | 'rejected' | 'executed' | 'failed'
export type SourceType = 'manual' | 'ai_suggestion' | 'auto_alert'

export interface PriceProposal {
  id: string
  product_id: string
  product_name: string | null
  product_sku: string | null
  current_price: number
  proposed_price: number
  final_price: number | null
  reason: string | null
  status: ProposalStatus
  ai_model_used: string | null
  created_at: string
  reviewed_at: string | null
  reviewed_by: string | null
  // Workflow 擴展欄位
  source_conversation_id: string | null
  source_type: SourceType
  assigned_to: string | null
  due_date: string | null
  reminder_sent: boolean
}

export interface AIAnalysisResult {
  status: string
  generated_proposals: number
}

// ==================== API Functions ====================

/**
 * 獲取待審批的改價提案
 */
export async function getPendingProposals(): Promise<PriceProposal[]> {
  const response = await apiClient.get('/pricing/proposals/pending')
  return response as unknown as PriceProposal[]
}

/**
 * 批准改價提案
 */
export async function approveProposal(id: string): Promise<PriceProposal> {
  const response = await apiClient.post(`/pricing/proposals/${id}/approve`)
  return response as unknown as PriceProposal
}

/**
 * 拒絕改價提案
 */
export async function rejectProposal(id: string): Promise<PriceProposal> {
  const response = await apiClient.post(`/pricing/proposals/${id}/reject`)
  return response as unknown as PriceProposal
}

/**
 * 觸發 AI 價格分析
 */
export async function triggerAIAnalysis(): Promise<AIAnalysisResult> {
  const response = await apiClient.post('/pricing/analyze')
  return response as unknown as AIAnalysisResult
}

// ==================== Utility Functions ====================

/**
 * 計算價格變化百分比
 */
export function calculatePriceChangePercent(current: number, proposed: number): number {
  if (current === 0) return 0
  return ((proposed - current) / current) * 100
}

/**
 * 格式化價格變化顯示
 */
export function formatPriceChange(current: number, proposed: number): string {
  const percent = calculatePriceChangePercent(current, proposed)
  const sign = percent >= 0 ? '+' : ''
  return `${sign}${percent.toFixed(1)}%`
}
