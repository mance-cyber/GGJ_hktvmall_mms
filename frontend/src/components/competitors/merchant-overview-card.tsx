'use client'

import { useState } from 'react'
import { MerchantOverview } from '@/lib/api'
import { ChevronDown, ChevronUp, Package, ArrowUpDown, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { TierBadge } from './tier-badge'
import { motion, AnimatePresence } from 'framer-motion'

interface MerchantOverviewCardProps {
  data: MerchantOverview
}

export function MerchantOverviewCard({ data }: MerchantOverviewCardProps) {
  const [expanded, setExpanded] = useState(false)
  const { competitor, price_comparison, recent_changes } = data

  const totalCompared = price_comparison.cheaper_count + price_comparison.same_count + price_comparison.expensive_count

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/50 transition-all hover:border-slate-700">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <TierBadge tier={competitor.tier} />
          <span className="font-medium text-slate-200 truncate">
            {competitor.name}
          </span>
          {competitor.store_code && (
            <span className="text-xs text-slate-600 font-mono">
              {competitor.store_code}
            </span>
          )}
        </div>

        <div className="flex items-center gap-4 shrink-0 ml-3">
          {/* Product counts */}
          <div className="flex items-center gap-1.5 text-xs text-slate-500">
            <Package className="w-3.5 h-3.5" />
            <span>{competitor.total_products}</span>
            {competitor.overlap_products > 0 && (
              <span className="text-cyan-500">({competitor.overlap_products} 重疊)</span>
            )}
          </div>

          {/* Price comparison mini bar */}
          {totalCompared > 0 && (
            <div className="flex items-center gap-1">
              <div className="flex h-2 w-20 rounded-full overflow-hidden bg-slate-800">
                {price_comparison.expensive_count > 0 && (
                  <div
                    className="bg-emerald-500 h-full"
                    style={{ width: `${(price_comparison.expensive_count / totalCompared) * 100}%` }}
                    title={`佢貴: ${price_comparison.expensive_count}`}
                  />
                )}
                {price_comparison.same_count > 0 && (
                  <div
                    className="bg-slate-500 h-full"
                    style={{ width: `${(price_comparison.same_count / totalCompared) * 100}%` }}
                    title={`差不多: ${price_comparison.same_count}`}
                  />
                )}
                {price_comparison.cheaper_count > 0 && (
                  <div
                    className="bg-red-500 h-full"
                    style={{ width: `${(price_comparison.cheaper_count / totalCompared) * 100}%` }}
                    title={`佢平: ${price_comparison.cheaper_count}`}
                  />
                )}
              </div>
              <span className={cn(
                'text-xs font-mono',
                price_comparison.avg_price_diff_pct > 0 ? 'text-emerald-400' : 'text-red-400'
              )}>
                {price_comparison.avg_price_diff_pct > 0 ? '+' : ''}{price_comparison.avg_price_diff_pct}%
              </span>
            </div>
          )}

          {expanded ? (
            <ChevronUp className="w-4 h-4 text-slate-500" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-500" />
          )}
        </div>
      </button>

      {/* Expanded details */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 border-t border-slate-800 pt-3">
              {/* Stats grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                <div className="text-center p-2 rounded-lg bg-slate-800/50">
                  <div className="text-lg font-bold text-slate-200">{competitor.total_products}</div>
                  <div className="text-xs text-slate-500">總商品</div>
                </div>
                <div className="text-center p-2 rounded-lg bg-slate-800/50">
                  <div className="text-lg font-bold text-cyan-400">{competitor.fresh_products}</div>
                  <div className="text-xs text-slate-500">生鮮品</div>
                </div>
                <div className="text-center p-2 rounded-lg bg-slate-800/50">
                  <div className="text-lg font-bold text-amber-400">{competitor.overlap_products}</div>
                  <div className="text-xs text-slate-500">與我重疊</div>
                </div>
                <div className="text-center p-2 rounded-lg bg-slate-800/50">
                  <div className="text-lg font-bold text-purple-400">{competitor.unique_products}</div>
                  <div className="text-xs text-slate-500">獨有商品</div>
                </div>
              </div>

              {/* Price comparison summary */}
              {totalCompared > 0 && (
                <div className="flex items-center gap-4 mb-4 text-xs">
                  <span className="flex items-center gap-1 text-emerald-400">
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    佢貴過我: {price_comparison.expensive_count}
                  </span>
                  <span className="flex items-center gap-1 text-slate-400">
                    <span className="w-2 h-2 rounded-full bg-slate-500" />
                    差不多: {price_comparison.same_count}
                  </span>
                  <span className="flex items-center gap-1 text-red-400">
                    <span className="w-2 h-2 rounded-full bg-red-500" />
                    佢平過我: {price_comparison.cheaper_count}
                  </span>
                </div>
              )}

              {/* Recent changes */}
              {recent_changes.length > 0 && (
                <div>
                  <h4 className="text-xs text-slate-500 mb-2 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" />
                    最近 7 日變動
                  </h4>
                  <div className="space-y-1.5">
                    {recent_changes.map((change, i) => (
                      <div key={i} className="flex items-center gap-2 text-xs">
                        <span className={cn(
                          'px-1.5 py-0.5 rounded',
                          change.change_type === 'price_drop' ? 'bg-emerald-500/10 text-emerald-400' :
                          change.change_type === 'price_increase' ? 'bg-red-500/10 text-red-400' :
                          'bg-slate-800 text-slate-400'
                        )}>
                          {change.change_type === 'price_drop' ? '↓ 降價' :
                           change.change_type === 'price_increase' ? '↑ 加價' :
                           change.change_type}
                        </span>
                        <span className="text-slate-300 truncate flex-1">{change.product_name}</span>
                        {change.old_price && change.new_price && (
                          <span className="text-slate-500 font-mono">
                            ${change.old_price} → ${change.new_price}
                          </span>
                        )}
                        <span className="text-slate-600">{change.date}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {recent_changes.length === 0 && totalCompared === 0 && (
                <p className="text-sm text-slate-600 text-center py-2">
                  暫無比較數據（需先跑建庫）
                </p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
