'use client'

import { Search, SlidersHorizontal, ArrowUpDown } from 'lucide-react'
import { cn } from '@/lib/utils'

export type SortKey = 'threat' | 'price_diff' | 'competitors' | 'name' | 'rank'
export type SortDir = 'asc' | 'desc'

interface FilterBarProps {
  search: string
  onSearchChange: (v: string) => void
  categoryFilter: string
  onCategoryChange: (v: string) => void
  categories: string[]
  sortKey: SortKey
  sortDir: SortDir
  onSortChange: (key: SortKey, dir: SortDir) => void
  resultCount: number
  totalCount: number
  mode: 'products' | 'merchants'
}

const SORT_OPTIONS_PRODUCTS: { key: SortKey; label: string }[] = [
  { key: 'threat', label: '威脅程度' },
  { key: 'price_diff', label: '價差 %' },
  { key: 'rank', label: '排名' },
  { key: 'competitors', label: '競品數' },
  { key: 'name', label: '名稱' },
]

const SORT_OPTIONS_MERCHANTS: { key: SortKey; label: string }[] = [
  { key: 'threat', label: '威脅程度' },
  { key: 'competitors', label: '商品數' },
  { key: 'name', label: '名稱' },
]

export function FilterBar({
  search, onSearchChange,
  categoryFilter, onCategoryChange,
  categories,
  sortKey, sortDir, onSortChange,
  resultCount, totalCount,
  mode,
}: FilterBarProps) {
  const sortOptions = mode === 'products' ? SORT_OPTIONS_PRODUCTS : SORT_OPTIONS_MERCHANTS

  const handleSortSelect = (key: SortKey) => {
    if (sortKey === key) {
      onSortChange(key, sortDir === 'asc' ? 'desc' : 'asc')
    } else {
      onSortChange(key, key === 'name' ? 'asc' : 'desc')
    }
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-3 sm:p-4 space-y-3">
      {/* Row 1: Search + Category */}
      <div className="flex gap-2">
        {/* Search */}
        <div className="relative flex-1 min-w-0">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={e => onSearchChange(e.target.value)}
            placeholder={mode === 'products' ? '搜索商品...' : '搜索商戶...'}
            className="w-full pl-8 pr-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-300 focus:border-teal-400"
          />
        </div>

        {/* Category filter (products only) */}
        {mode === 'products' && categories.length > 0 && (
          <select
            value={categoryFilter}
            onChange={e => onCategoryChange(e.target.value)}
            className="shrink-0 px-2 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-300 text-gray-600 bg-white"
          >
            <option value="">全部分類</option>
            {categories.map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        )}
      </div>

      {/* Row 2: Sort chips + result count */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-1 flex-wrap">
          <span className="text-[10px] sm:text-xs text-gray-400 flex items-center gap-1 mr-1">
            <ArrowUpDown className="w-3 h-3" /> 排序:
          </span>
          {sortOptions.map(opt => (
            <button
              key={opt.key}
              onClick={() => handleSortSelect(opt.key)}
              className={cn(
                'text-[10px] sm:text-xs px-2 py-1 rounded-full border transition-all',
                sortKey === opt.key
                  ? 'bg-teal-500 text-white border-teal-500'
                  : 'text-gray-500 border-gray-200 hover:border-teal-300 hover:text-teal-600'
              )}
            >
              {opt.label}
              {sortKey === opt.key && (
                <span className="ml-0.5">{sortDir === 'asc' ? '↑' : '↓'}</span>
              )}
            </button>
          ))}
        </div>

        <span className="shrink-0 text-[10px] sm:text-xs text-gray-400">
          {resultCount === totalCount ? `共 ${totalCount}` : `${resultCount}/${totalCount}`}
        </span>
      </div>
    </div>
  )
}
