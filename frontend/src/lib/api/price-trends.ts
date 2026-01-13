// =============================================
// 價格趨勢 API 客戶端
// =============================================

import { apiClient } from './client'

// =============================================
// 類型定義
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
// API 方法
// =============================================

/**
 * 獲取有價格歷史的產品列表（供下拉選單）
 */
export async function getProductsWithTrends(
  search?: string
): Promise<ProductListResponse> {
  const params = search ? { search } : {}
  const response = await apiClient.get('/price-trends/products', { params })
  return response as unknown as ProductListResponse
}

/**
 * 獲取單個產品的價格趨勢
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
// 工具函數
// =============================================

/**
 * 格式化日期為 YYYY-MM-DD
 */
export function formatDateForApi(date: Date): string {
  return date.toISOString().split('T')[0]
}

/**
 * 計算時間範圍
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
 * 預設時間範圍選項
 */
export const TIME_RANGE_OPTIONS = [
  { label: '7 天', value: 7 },
  { label: '30 天', value: 30 },
  { label: '90 天', value: 90 },
] as const

/**
 * 圖表顏色配置
 */
export const CHART_COLORS = {
  own: '#8b5cf6',        // 紫色 - 自家產品（實線）
  competitor1: '#06b6d4', // 青色 - 競爭對手 1（虛線）
  competitor2: '#f59e0b', // 橙色 - 競爭對手 2（虛線）
  competitor3: '#22c55e', // 綠色 - 競爭對手 3（虛線）
  competitor4: '#ef4444', // 紅色 - 競爭對手 4（虛線）
  outOfStock: '#dc2626',  // 缺貨標記點
  promotion: '#facc15',   // 促銷標記
} as const

/**
 * 獲取競爭對手顏色
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
