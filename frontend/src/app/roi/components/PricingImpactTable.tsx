// =============================================
// AI 改價影響表格組件
// =============================================

'use client'

import { Loader2, TrendingUp, CheckCircle, XCircle, Clock } from 'lucide-react'
import { usePricingImpact } from '../hooks/useROIData'

export function PricingImpactTable() {
  const { data, isLoading, error } = usePricingImpact(10)

  // 格式化金額
  const formatMoney = (value: number) => {
    return `$${Number(value).toLocaleString('zh-HK', { minimumFractionDigits: 2 })}`
  }

  // 格式化日期
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('zh-HK', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64 text-red-500">
        載入失敗
      </div>
    )
  }

  const summary = data?.summary
  const proposals = data?.proposals || []

  return (
    <div className="space-y-4">
      {/* 統計摘要 */}
      <div className="grid grid-cols-4 gap-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-gray-900">{summary?.total_proposals || 0}</div>
          <div className="text-xs text-gray-500">總提案數</div>
        </div>
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{summary?.executed_count || 0}</div>
          <div className="text-xs text-gray-500">已執行</div>
        </div>
        <div className="text-center p-3 bg-yellow-50 rounded-lg">
          <div className="text-2xl font-bold text-yellow-600">{summary?.approved_count || 0}</div>
          <div className="text-xs text-gray-500">待執行</div>
        </div>
        <div className="text-center p-3 bg-purple-50 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">
            {formatMoney(summary?.total_impact || 0)}
          </div>
          <div className="text-xs text-gray-500">總影響金額</div>
        </div>
      </div>

      {/* 提案列表 */}
      {proposals.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-2 font-medium text-gray-500">產品</th>
                <th className="text-right py-3 px-2 font-medium text-gray-500">原價</th>
                <th className="text-right py-3 px-2 font-medium text-gray-500">新價</th>
                <th className="text-right py-3 px-2 font-medium text-gray-500">差異</th>
                <th className="text-right py-3 px-2 font-medium text-gray-500">影響金額</th>
                <th className="text-right py-3 px-2 font-medium text-gray-500">執行時間</th>
              </tr>
            </thead>
            <tbody>
              {proposals.map((proposal) => (
                <tr key={proposal.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-2">
                    <div className="font-medium text-gray-900 truncate max-w-[200px]">
                      {proposal.product_name}
                    </div>
                  </td>
                  <td className="text-right py-3 px-2 text-gray-500">
                    {formatMoney(proposal.old_price)}
                  </td>
                  <td className="text-right py-3 px-2 text-gray-900">
                    {formatMoney(proposal.new_price)}
                  </td>
                  <td className="text-right py-3 px-2">
                    <span className={`font-medium ${proposal.price_diff > 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {proposal.price_diff > 0 ? '+' : ''}{formatMoney(proposal.price_diff)}
                    </span>
                  </td>
                  <td className="text-right py-3 px-2">
                    <span className="font-medium text-purple-600">
                      {formatMoney(proposal.impact)}
                    </span>
                  </td>
                  <td className="text-right py-3 px-2 text-gray-400 text-xs">
                    {formatDate(proposal.executed_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          暫無已執行的改價提案
        </div>
      )}
    </div>
  )
}
