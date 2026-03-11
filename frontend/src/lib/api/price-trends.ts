// =============================================
// PriceTrend API 客戶端
// =============================================

import { apiClient } from './client'

// =============================================
// Type definitions
// =============================================

export type TimeInterval = 'hour' | 'day' | 'week'

export interface ProductListItem {
  id: string
  sku: string
  name: string
  current_price: number | null
  competitor_count: number
}

export interface ProductListResponse {
  products: ProductListItem[]
  total: number
}

export interface PriceDataPoint {
  date: string
  price: number | null
  original_price: number | null
  discount_percent: number | null
  stock_status: string | null
  promotion_text: string | null
}

export interface CompetitorInfo {
  id: string
  name: string
  platform: string
  product_name: string
  current_price: number | null
}

export interface OwnProductInfo {
  id: string
  sku: string
  name: string
  category: string | null
  current_price: number | null
}

export interface TrendSummary {
  price_gap_current: number | null
  price_gap_avg: number | null
  lowest_competitor_price: number | null
  volatility: number | null
  own_price_change: number | null
  competitor_avg_change: number | null
}

export interface PriceTrendResponse {
  own_product: OwnProductInfo
  competitors: CompetitorInfo[]
  trends: Record<string, PriceDataPoint[]>
  summary: TrendSummary
  start_date: string
  end_date: string
  interval: TimeInterval
}

export interface PriceTrendQuery {
  start_date?: string
  end_date?: string
  interval?: TimeInterval
}

// =============================================
// API Method
// =============================================

/**
 * Get products with price historyList（供下拉選單）
 */
export async function getProductsWithTrends(
  search?: string
): Promise<ProductListResponse> {
  const params = search ? { search } : {}
  const response = await apiClient.get('/price-trends/products', { params })
  return response as unknown as ProductListResponse
}

/**
 * Fetch單個Product的PriceTrend
 */
export async function getProductPriceTrend(
  productId: string,
  query?: PriceTrendQuery
): Promise<PriceTrendResponse> {
  const response = await apiClient.get(`/price-trends/product/${productId}`, {
    params: query
  })
  return response as unknown as PriceTrendResponse
}

// =============================================
// 工具Function
// =============================================

/**
 * Format化Date為 YYYY-MM-DD
 */
export function formatDateForApi(date: Date): string {
  return date.toISOString().split('T')[0]
}

/**
 * CalculateTimeRange
 */
export function getDateRange(days: number): { start_date: string; end_date: string } {
  const endDate = new Date()
  const startDate = new Date()
  startDate.setDate(startDate.getDate() - days)

  return {
    start_date: formatDateForApi(startDate),
    end_date: formatDateForApi(endDate)
  }
}

/**
 * DefaultTimeRangeOption
 */
export const TIME_RANGE_OPTIONS = [
  { label: '7 天', value: 7 },
  { label: '30 天', value: 30 },
  { label: '90 天', value: 90 },
] as const

/**
 * Chart顏色Configuration
 */
export const CHART_COLORS = {
  own: '#8b5cf6',        // 紫色 - 自家Product（實線）
  competitor1: '#06b6d4', // Cyan - Competitor 1 (dashed)
  competitor2: '#f59e0b', // Orange - Competitor 2 (dashed)
  competitor3: '#22c55e', // Green - Competitor 3 (dashed)
  competitor4: '#ef4444', // 紅色 - 競爭Competitor 4（虛線）
  outOfStock: '#dc2626',  // Out of stock標記點
  promotion: '#facc15',   // 促銷標記
} as const

/**
 * Fetch競爭Competitor顏色
 */
export function getCompetitorColor(index: number): string {
  const colors = [
    CHART_COLORS.competitor1,
    CHART_COLORS.competitor2,
    CHART_COLORS.competitor3,
    CHART_COLORS.competitor4,
  ]
  return colors[index % colors.length]
}
