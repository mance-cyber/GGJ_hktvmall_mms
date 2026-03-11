// =============================================
// AI Pricing Impact Table Component
// =============================================

'use client'

import { Loader2, TrendingUp, CheckCircle, XCircle, Clock } from 'lucide-react'
import { usePricingImpact } from '../hooks/useROIData'

export function PricingImpactTable() {
  const { data, isLoading, error } = usePricingImpact(10)

  // Format monetary amount
  const formatMoney = (value: number) => {
    return `$${Number(value).toLocaleString('zh-HK', { minimumFractionDigits: 2 })}`
  }

  // Format date
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
        Failed to load
      </div>
    )
  }

  const summary = data?.summary
  const proposals = data?.proposals || []

  return (
    <div className="space-y-4">
      {/* Summary Statistics */}
      <div className="grid grid-cols-4 gap-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-2xl font-bold text-gray-900">{summary?.total_proposals || 0}</div>
          <div className="text-xs text-gray-500">Total Proposals</div>
        </div>
        <div className="text-center p-3 bg-green-50 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{summary?.executed_count || 0}</div>
          <div className="text-xs text-gray-500">Executed</div>
        </div>
        <div className="text-center p-3 bg-yellow-50 rounded-lg">
          <div className="text-2xl font-bold text-yellow-600">{summary?.approved_count || 0}</div>
          <div className="text-xs text-gray-500">Pending Execution</div>
        </div>
        <div className="text-center p-3 bg-purple-50 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">
            {formatMoney(summary?.total_impact || 0)}
          </div>
          <div className="text-xs text-gray-500">Total Impact</div>
        </div>
      </div>

      {/* Proposal List */}
      {proposals.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-2 font-medium text-gray-500">Product</th>
                <th className="text-right py-3 px-2 font-medium text-gray-500">Original Price</th>
                <th className="text-right py-3 px-2 font-medium text-gray-500">New Price</th>
                <th className="text-right py-3 px-2 font-medium text-gray-500">Difference</th>
                <th className="text-right py-3 px-2 font-medium text-gray-500">Impact Amount</th>
                <th className="text-right py-3 px-2 font-medium text-gray-500">Executed At</th>
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
          No executed pricing proposals yet
        </div>
      )}
    </div>
  )
}
