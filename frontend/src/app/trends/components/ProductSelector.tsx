// =============================================
// 產品選擇器組件
// =============================================

'use client'

import { useState, useMemo } from 'react'
import { Search, ChevronDown, Package } from 'lucide-react'
import type { ProductListItem } from '@/lib/api/price-trends'

interface ProductSelectorProps {
  products: ProductListItem[]
  selectedId: string | null
  onSelect: (id: string | null) => void
}

export function ProductSelector({
  products,
  selectedId,
  onSelect,
}: ProductSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [search, setSearch] = useState('')

  // 過濾產品
  const filteredProducts = useMemo(() => {
    if (!search.trim()) return products
    const lowerSearch = search.toLowerCase()
    return products.filter(
      (p) =>
        p.name.toLowerCase().includes(lowerSearch) ||
        p.sku.toLowerCase().includes(lowerSearch)
    )
  }, [products, search])

  // 當前選中的產品
  const selectedProduct = useMemo(
    () => products.find((p) => p.id === selectedId),
    [products, selectedId]
  )

  // 格式化價格
  const formatPrice = (price: number | null) => {
    if (price === null) return '--'
    return `$${price.toLocaleString()}`
  }

  return (
    <div className="relative">
      {/* 選擇器按鈕 */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between gap-2 px-4 py-3 bg-white border border-gray-200 rounded-xl hover:border-emerald-300 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all"
      >
        <div className="flex items-center gap-3 min-w-0">
          <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600 flex-shrink-0">
            <Package className="w-4 h-4" />
          </div>
          {selectedProduct ? (
            <div className="text-left min-w-0">
              <div className="font-medium text-gray-900 truncate">
                {selectedProduct.name}
              </div>
              <div className="text-sm text-gray-500 flex items-center gap-2">
                <span>{selectedProduct.sku}</span>
                <span className="text-gray-300">•</span>
                <span>{formatPrice(selectedProduct.current_price)}</span>
                <span className="text-gray-300">•</span>
                <span>{selectedProduct.competitor_count} 個競爭對手</span>
              </div>
            </div>
          ) : (
            <span className="text-gray-500">選擇產品...</span>
          )}
        </div>
        <ChevronDown
          className={`w-5 h-5 text-gray-400 flex-shrink-0 transition-transform ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>

      {/* 下拉選單 */}
      {isOpen && (
        <>
          {/* 背景遮罩 */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />

          {/* 選單內容 */}
          <div className="absolute z-20 w-full mt-2 bg-white border border-gray-200 rounded-xl shadow-lg overflow-hidden">
            {/* 搜尋框 */}
            <div className="p-3 border-b border-gray-100">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="搜尋產品名稱或 SKU..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500"
                  autoFocus
                />
              </div>
            </div>

            {/* 產品列表 */}
            <div className="max-h-64 overflow-y-auto">
              {filteredProducts.length === 0 ? (
                <div className="px-4 py-8 text-center text-gray-500 text-sm">
                  找不到符合的產品
                </div>
              ) : (
                filteredProducts.map((product) => (
                  <button
                    key={product.id}
                    type="button"
                    onClick={() => {
                      onSelect(product.id)
                      setIsOpen(false)
                      setSearch('')
                    }}
                    className={`w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors flex items-center gap-3 ${
                      product.id === selectedId ? 'bg-emerald-50' : ''
                    }`}
                  >
                    <div
                      className={`p-2 rounded-lg flex-shrink-0 ${
                        product.id === selectedId
                          ? 'bg-emerald-100 text-emerald-600'
                          : 'bg-gray-100 text-gray-500'
                      }`}
                    >
                      <Package className="w-4 h-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div
                        className={`font-medium truncate ${
                          product.id === selectedId
                            ? 'text-emerald-700'
                            : 'text-gray-900'
                        }`}
                      >
                        {product.name}
                      </div>
                      <div className="text-sm text-gray-500 flex items-center gap-2">
                        <span>{product.sku}</span>
                        <span className="text-gray-300">•</span>
                        <span>{formatPrice(product.current_price)}</span>
                      </div>
                    </div>
                    <div className="flex-shrink-0 text-xs text-gray-400">
                      {product.competitor_count} 競爭對手
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
