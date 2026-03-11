// =============================================
// PriceTrend React Query Hooks
// =============================================

import { useQuery } from '@tanstack/react-query'
import {
  getProductsWithTrends,
  getProductPriceTrend,
  getDateRange,
  type ProductListResponse,
  type PriceTrendResponse,
  type PriceTrendQuery,
} from '@/lib/api/price-trends'

// =============================================
// Query Keys
// =============================================

export const priceTrendsKeys = {
  all: ['price-trends'] as const,
  products: () => [...priceTrendsKeys.all, 'products'] as const,
  productSearch: (search: string) => [...priceTrendsKeys.products(), search] as const,
  trend: (productId: string) => [...priceTrendsKeys.all, 'trend', productId] as const,
  trendWithQuery: (productId: string, query: PriceTrendQuery) =>
    [...priceTrendsKeys.trend(productId), query] as const,
}

// =============================================
// Hooks
// =============================================

/**
 * Get products with price historyList
 */
export function useProductsWithTrends(search?: string) {
  return useQuery<ProductListResponse>({
    queryKey: search
      ? priceTrendsKeys.productSearch(search)
      : priceTrendsKeys.products(),
    queryFn: () => getProductsWithTrends(search),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

/**
 * Fetch單個Product的PriceTrend
 */
export function useProductPriceTrend(
  productId: string | null,
  query?: PriceTrendQuery
) {
  return useQuery<PriceTrendResponse>({
    queryKey: productId
      ? priceTrendsKeys.trendWithQuery(productId, query || {})
      : ['disabled'],
    queryFn: () => getProductPriceTrend(productId!, query),
    enabled: !!productId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

/**
 * 使用DefaultTimeRange的PriceTrend Hook
 */
export function useProductPriceTrendWithDays(
  productId: string | null,
  days: number = 30
) {
  const dateRange = getDateRange(days)

  return useProductPriceTrend(productId, {
    start_date: dateRange.start_date,
    end_date: dateRange.end_date,
  })
}
