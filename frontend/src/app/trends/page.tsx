'use client'

// =============================================
// 價格趨勢頁面
// =============================================

import { TrendingUp } from 'lucide-react'

export default function TrendsPage() {
  return (
    <div className="space-y-6">
      {/* 頁面標題 */}
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 text-white">
          <TrendingUp className="w-6 h-6" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">價格趨勢</h1>
          <p className="text-gray-500 text-sm">監測市場價格變化</p>
        </div>
      </div>

      {/* 佔位內容 */}
      <div className="glass-panel rounded-2xl p-12 text-center">
        <TrendingUp className="w-16 h-16 text-emerald-500 mx-auto mb-4 opacity-50" />
        <h2 className="text-xl font-semibold text-gray-700 mb-2">即將推出</h2>
        <p className="text-gray-500">
          價格趨勢分析功能正在開發中，敬請期待！
        </p>
      </div>
    </div>
  )
}
