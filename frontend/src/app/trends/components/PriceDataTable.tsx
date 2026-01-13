// =============================================
// 價格數據表格組件
// =============================================

'use client'

import { useMemo, useState } from 'react'
import {
  ChevronDown,
  ChevronUp,
  Package,
  Store,
  AlertTriangle,
  Tag,
} from 'lucide-react'
import {
  getCompetitorColor,
  CHART_COLORS,
  type PriceDataPoint,
  type CompetitorInfo,
  type OwnProductInfo,
} from '@/lib/api/price-trends'

interface PriceDataTableProps {
  trends: Record<string, PriceDataPoint[]>
  ownProduct: OwnProductInfo
  competitors: CompetitorInfo[]
}

type SortField = 'date' | 'own' | string
type SortDirection = 'asc' | 'desc'

// 表格行類型
interface TableRow {
  date: string
  own?: PriceDataPoint | null
  [key: string]: PriceDataPoint | null | string | undefined
}

export function PriceDataTable({
  trends,
  ownProduct,
  competitors,
}: PriceDataTableProps) {
  const [sortField, setSortField] = useState<SortField>('date')
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc')

  // 處理表格數據
  const tableData = useMemo((): TableRow[] => {
    // 收集所有唯一日期
    const dateMap = new Map<string, Record<string, PriceDataPoint | null>>()

    // 處理自家產品數據
    if (trends.own) {
      trends.own.forEach((point) => {
        const dateKey = new Date(point.date).toISOString().split('T')[0]
        if (!dateMap.has(dateKey)) {
          dateMap.set(dateKey, { own: null })
        }
        dateMap.get(dateKey)!.own = point
      })
    }

    // 處理競爭對手數據
    competitors.forEach((comp) => {
      const compTrends = trends[comp.id]
      if (compTrends) {
        compTrends.forEach((point) => {
          const dateKey = new Date(point.date).toISOString().split('T')[0]
          if (!dateMap.has(dateKey)) {
            dateMap.set(dateKey, { own: null })
          }
          dateMap.get(dateKey)![comp.id] = point
        })
      }
    })

    // 轉換為數組並排序
    const rows: TableRow[] = Array.from(dateMap.entries()).map(([date, data]) => ({
      date,
      ...data,
    }))

    // 排序
    rows.sort((a, b) => {
      let comparison = 0

      if (sortField === 'date') {
        comparison = new Date(a.date).getTime() - new Date(b.date).getTime()
      } else {
        const aPoint = a[sortField] as PriceDataPoint | null | undefined
        const bPoint = b[sortField] as PriceDataPoint | null | undefined
        const aPrice = (aPoint as PriceDataPoint | null)?.price ?? -Infinity
        const bPrice = (bPoint as PriceDataPoint | null)?.price ?? -Infinity
        comparison = Number(aPrice) - Number(bPrice)
      }

      return sortDirection === 'asc' ? comparison : -comparison
    })

    return rows
  }, [trends, competitors, sortField, sortDirection])

  // 處理排序
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  // 排序指示器
  const SortIndicator = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return <ChevronDown className="w-4 h-4 text-gray-300" />
    }
    return sortDirection === 'asc' ? (
      <ChevronUp className="w-4 h-4 text-emerald-600" />
    ) : (
      <ChevronDown className="w-4 h-4 text-emerald-600" />
    )
  }

  // 格式化日期
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('zh-HK', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  // 格式化價格
  const formatPrice = (price: number | null) => {
    if (price === null) return '--'
    return `$${Number(price).toLocaleString()}`
  }

  // 渲染價格單元格
  const PriceCell = ({
    point,
    color,
  }: {
    point: PriceDataPoint | null
    color: string
  }) => {
    if (!point || point.price === null) {
      return <span className="text-gray-400">--</span>
    }

    const isOutOfStock = point.stock_status === 'out_of_stock'
    const hasPromotion = !!point.promotion_text
    const hasDiscount =
      point.discount_percent && Number(point.discount_percent) > 0

    return (
      <div className="flex items-center gap-2">
        <span className="font-medium" style={{ color }}>
          {formatPrice(point.price)}
        </span>

        {/* 狀態標籤 */}
        <div className="flex items-center gap-1">
          {isOutOfStock && (
            <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-xs bg-red-100 text-red-600">
              <AlertTriangle className="w-3 h-3" />
              缺貨
            </span>
          )}
          {hasPromotion && (
            <span
              className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-xs bg-yellow-100 text-yellow-700"
              title={point.promotion_text || ''}
            >
              <Tag className="w-3 h-3" />
              促銷
            </span>
          )}
          {hasDiscount && (
            <span className="text-xs text-orange-600">
              -{point.discount_percent}%
            </span>
          )}
        </div>
      </div>
    )
  }

  // 如果沒有數據
  if (tableData.length === 0) {
    return (
      <div className="py-12 text-center text-gray-500">暫無價格數據</div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            {/* 日期列 */}
            <th className="text-left py-3 px-4">
              <button
                onClick={() => handleSort('date')}
                className="flex items-center gap-1 font-medium text-gray-700 hover:text-gray-900"
              >
                日期
                <SortIndicator field="date" />
              </button>
            </th>

            {/* 自家產品列 */}
            <th className="text-left py-3 px-4">
              <button
                onClick={() => handleSort('own')}
                className="flex items-center gap-2 font-medium text-gray-700 hover:text-gray-900"
              >
                <div
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: CHART_COLORS.own }}
                />
                <Package className="w-4 h-4 text-purple-500" />
                <span className="truncate max-w-[150px]">{ownProduct.name}</span>
                <SortIndicator field="own" />
              </button>
            </th>

            {/* 競爭對手列 */}
            {competitors.map((comp, index) => (
              <th key={comp.id} className="text-left py-3 px-4">
                <button
                  onClick={() => handleSort(comp.id)}
                  className="flex items-center gap-2 font-medium text-gray-700 hover:text-gray-900"
                >
                  <div
                    className="w-3 h-3 rounded-full flex-shrink-0"
                    style={{ backgroundColor: getCompetitorColor(index) }}
                  />
                  <Store className="w-4 h-4 text-gray-400" />
                  <span className="truncate max-w-[120px]">{comp.name}</span>
                  <SortIndicator field={comp.id} />
                </button>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {tableData.map((row, rowIndex) => (
            <tr
              key={row.date}
              className={`border-b border-gray-100 ${
                rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'
              }`}
            >
              {/* 日期 */}
              <td className="py-3 px-4 text-gray-600">
                {formatDate(row.date)}
              </td>

              {/* 自家產品價格 */}
              <td className="py-3 px-4">
                <PriceCell
                  point={row.own as PriceDataPoint | null}
                  color={CHART_COLORS.own}
                />
              </td>

              {/* 競爭對手價格 */}
              {competitors.map((comp, index) => (
                <td key={comp.id} className="py-3 px-4">
                  <PriceCell
                    point={row[comp.id] as PriceDataPoint | null}
                    color={getCompetitorColor(index)}
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>

      {/* 表格底部統計 */}
      <div className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between text-sm text-gray-500">
        <span>共 {tableData.length} 條記錄</span>
        <span>
          顯示 {ownProduct.name} 與 {competitors.length} 個競爭對手的價格對比
        </span>
      </div>
    </div>
  )
}
