// =============================================
// PriceDataTable組items
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

// Table行Type
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

  // ProcessingTableData
  const tableData = useMemo((): TableRow[] => {
    // 收集所有唯一Date
    const dateMap = new Map<string, Record<string, PriceDataPoint | null>>()

    // Processing自家ProductData
    if (trends.own) {
      trends.own.forEach((point) => {
        const dateKey = new Date(point.date).toISOString().split('T')[0]
        if (!dateMap.has(dateKey)) {
          dateMap.set(dateKey, { own: null })
        }
        dateMap.get(dateKey)!.own = point
      })
    }

    // Processing競爭CompetitorData
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

    // Convert為數組並Sort
    const rows: TableRow[] = Array.from(dateMap.entries()).map(([date, data]) => ({
      date,
      ...data,
    }))

    // Sort
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

  // ProcessingSort
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('desc')
    }
  }

  // Sort指示器
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

  // Format化Date
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('zh-HK', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  // Format化Price
  const formatPrice = (price: number | null) => {
    if (price === null) return '--'
    return `$${Number(price).toLocaleString()}`
  }

  // RenderingPrice單元格
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

        {/* Status label */}
        <div className="flex items-center gap-1">
          {isOutOfStock && (
            <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-xs bg-red-100 text-red-600">
              <AlertTriangle className="w-3 h-3" />
              Out of stock
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

  // 如果沒有Data
  if (tableData.length === 0) {
    return (
      <div className="py-12 text-center text-gray-500">暫無PriceData</div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            {/* Date列 */}
            <th className="text-left py-3 px-4">
              <button
                onClick={() => handleSort('date')}
                className="flex items-center gap-1 font-medium text-gray-700 hover:text-gray-900"
              >
                Date
                <SortIndicator field="date" />
              </button>
            </th>

            {/* 自家Product列 */}
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

            {/* 競爭Competitor列 */}
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
              {/* Date */}
              <td className="py-3 px-4 text-gray-600">
                {formatDate(row.date)}
              </td>

              {/* 自家ProductPrice */}
              <td className="py-3 px-4">
                <PriceCell
                  point={row.own as PriceDataPoint | null}
                  color={CHART_COLORS.own}
                />
              </td>

              {/* 競爭CompetitorPrice */}
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

      {/* Table底部統計 */}
      <div className="mt-4 pt-4 border-t border-gray-200 flex items-center justify-between text-sm text-gray-500">
        <span>共 {tableData.length} 條Record</span>
        <span>
          Display {ownProduct.name} 與 {competitors.length} 個競爭Competitor的Price對比
        </span>
      </div>
    </div>
  )
}
