'use client'

import { useState } from 'react'
import { MerchantOverview } from '@/lib/api'
import { ChevronDown, ChevronUp, Package, AlertCircle } from 'lucide-react'
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
    <div className="rounded-xl border border-gray-200 bg-white shadow-sm transition-all hover:border-teal-200 hover:shadow-md">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-3 sm:p-4 flex items-center justify-between text-left"
      >
        <div className="flex items-center gap-2 sm:gap-3 flex-1 min-w-0">
          <TierBadge tier={competitor.tier} />
          <span className="font-medium text-gray-700 text-sm sm:text-base truncate">
            {competitor.name}
          </span>
          {competitor.store_code && (
            <span className="hidden sm:inline text-xs text-gray-400 font-mono">
              {competitor.store_code}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 sm:gap-4 shrink-0 ml-2">
          {/* Product count — compact on mobile */}
          <div className="flex items-center gap-1 text-[10px] sm:text-xs text-gray-400">
            <Package className="w-3 h-3 sm:w-3.5 sm:h-3.5" />
            <span>{competitor.total_products}</span>
            {competitor.overlap_products > 0 && (
              <span className="hidden sm:inline text-teal-500">({competitor.overlap_products} 重疊)</span>
            )}
          </div>

          {/* Price bar — hide on very small screens */}
          {totalCompared > 0 && (
            <div className="hidden sm:flex items-center gap-1">
              <div className="flex h-2 w-16 sm:w-20 rounded-full overflow-hidden bg-gray-100">
                {price_comparison.expensive_count > 0 && (
                  <div
                    className="bg-emerald-400 h-full"
                    style={{ width: `${(price_comparison.expensive_count / totalCompared) * 100}%` }}
                  />
                )}
                {price_comparison.same_count > 0 && (
                  <div
                    className="bg-gray-300 h-full"
                    style={{ width: `${(price_comparison.same_count / totalCompared) * 100}%` }}
                  />
                )}
                {price_comparison.cheaper_count > 0 && (
                  <div
                    className="bg-red-400 h-full"
                    style={{ width: `${(price_comparison.cheaper_count / totalCompared) * 100}%` }}
                  />
                )}
              </div>
              <span className={cn(
                'text-xs font-mono',
                price_comparison.avg_price_diff_pct > 0 ? 'text-emerald-500' : 'text-red-500'
              )}>
                {price_comparison.avg_price_diff_pct > 0 ? '+' : ''}{price_comparison.avg_price_diff_pct}%
              </span>
            </div>
          )}

          {/* Mobile: just show % */}
          {totalCompared > 0 && (
            <span className={cn(
              'sm:hidden text-xs font-mono',
              price_comparison.avg_price_diff_pct > 0 ? 'text-emerald-500' : 'text-red-500'
            )}>
              {price_comparison.avg_price_diff_pct > 0 ? '+' : ''}{price_comparison.avg_price_diff_pct}%
            </span>
          )}

          {expanded ? (
            <ChevronUp className="w-4 h-4 text-gray-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-400" />
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
            <div className="px-3 sm:px-4 pb-3 sm:pb-4 border-t border-gray-100 pt-3">
              {/* Stats grid — 2x2 on mobile */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3 mb-3 sm:mb-4">
                <div className="text-center p-2 rounded-lg bg-gray-50">
                  <div className="text-base sm:text-lg font-bold text-gray-700">{competitor.total_products}</div>
                  <div className="text-[10px] sm:text-xs text-gray-400">總products</div>
                </div>
                <div className="text-center p-2 rounded-lg bg-teal-50">
                  <div className="text-base sm:text-lg font-bold text-teal-600">{competitor.fresh_products}</div>
                  <div className="text-[10px] sm:text-xs text-gray-400">生鮮品</div>
                </div>
                <div className="text-center p-2 rounded-lg bg-amber-50">
                  <div className="text-base sm:text-lg font-bold text-amber-600">{competitor.overlap_products}</div>
                  <div className="text-[10px] sm:text-xs text-gray-400">與我重疊</div>
                </div>
                <div className="text-center p-2 rounded-lg bg-purple-50">
                  <div className="text-base sm:text-lg font-bold text-purple-600">{competitor.unique_products}</div>
                  <div className="text-[10px] sm:text-xs text-gray-400">獨有products</div>
                </div>
              </div>

              {totalCompared > 0 && (
                <div className="flex flex-wrap items-center gap-3 sm:gap-4 mb-3 sm:mb-4 text-[10px] sm:text-xs">
                  <span className="flex items-center gap-1 text-emerald-500">
                    <span className="w-2 h-2 rounded-full bg-emerald-400" />
                    佢貴: {price_comparison.expensive_count}
                  </span>
                  <span className="flex items-center gap-1 text-gray-400">
                    <span className="w-2 h-2 rounded-full bg-gray-300" />
                    差不多: {price_comparison.same_count}
                  </span>
                  <span className="flex items-center gap-1 text-red-500">
                    <span className="w-2 h-2 rounded-full bg-red-400" />
                    佢平: {price_comparison.cheaper_count}
                  </span>
                </div>
              )}

              {recent_changes.length > 0 && (
                <div>
                  <h4 className="text-[10px] sm:text-xs text-gray-400 mb-2 flex items-center gap-1">
                    <AlertCircle className="w-3 h-3" />
                    最近 7 日變動
                  </h4>
                  <div className="space-y-1.5">
                    {recent_changes.map((change, i) => (
                      <div key={i} className="flex items-center gap-1.5 sm:gap-2 text-[10px] sm:text-xs">
                        <span className={cn(
                          'px-1 sm:px-1.5 py-0.5 rounded shrink-0',
                          change.change_type === 'price_drop' ? 'bg-emerald-50 text-emerald-600' :
                          change.change_type === 'price_increase' ? 'bg-red-50 text-red-600' :
                          'bg-gray-100 text-gray-500'
                        )}>
                          {change.change_type === 'price_drop' ? '↓' :
                           change.change_type === 'price_increase' ? '↑' :
                           change.change_type}
                        </span>
                        <span className="text-gray-600 truncate flex-1">{change.product_name}</span>
                        {change.old_price && change.new_price && (
                          <span className="text-gray-400 font-mono shrink-0">
                            ${change.old_price}→${change.new_price}
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {recent_changes.length === 0 && totalCompared === 0 && (
                <p className="text-xs sm:text-sm text-gray-400 text-center py-2">
                  暫無CompareData
                </p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
