'use client'

import { useState, useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api, Product } from '@/lib/api'
import { Search, X, Check, Package, ChevronDown } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import {
  HoloCard,
  HoloBadge,
  HoloSkeleton,
} from '@/components/ui/future-tech'

interface ProductSelectorProps {
  selectedProducts: Product[]
  onSelectionChange: (products: Product[]) => void
  maxSelection?: number
  className?: string
}

export function ProductSelector({
  selectedProducts,
  onSelectionChange,
  maxSelection = 100,
  className,
}: ProductSelectorProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('')

  // 獲取商品列表
  const { data: productsData, isLoading: productsLoading } = useQuery({
    queryKey: ['own-products', 1, 200],
    queryFn: () => api.getProducts(1, 200),
  })

  // 獲取分類列表
  const { data: categoriesData } = useQuery({
    queryKey: ['categories'],
    queryFn: () => api.getCategories(),
  })

  const products = productsData?.data || []
  const categories = categoriesData?.items || []

  // 過濾商品
  const filteredProducts = useMemo(() => {
    let filtered = products

    // 按搜索詞過濾
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (p) =>
          p.name.toLowerCase().includes(query) ||
          p.brand?.toLowerCase().includes(query) ||
          p.sku?.toLowerCase().includes(query)
      )
    }

    // 按分類過濾
    if (selectedCategory) {
      filtered = filtered.filter((p) => p.category_id === selectedCategory)
    }

    return filtered
  }, [products, searchQuery, selectedCategory])

  // 檢查商品是否已選中
  const isSelected = (productId: string) =>
    selectedProducts.some((p) => p.id === productId)

  // 切換選中狀態
  const toggleSelection = (product: Product) => {
    if (isSelected(product.id)) {
      onSelectionChange(selectedProducts.filter((p) => p.id !== product.id))
    } else if (selectedProducts.length < maxSelection) {
      onSelectionChange([...selectedProducts, product])
    }
  }

  // 全選/取消全選當前過濾結果
  const toggleSelectAll = () => {
    const allFilteredSelected = filteredProducts.every((p) => isSelected(p.id))

    if (allFilteredSelected) {
      // 取消選中所有過濾結果
      const filteredIds = new Set(filteredProducts.map((p) => p.id))
      onSelectionChange(selectedProducts.filter((p) => !filteredIds.has(p.id)))
    } else {
      // 選中所有過濾結果（不超過上限）
      const currentIds = new Set(selectedProducts.map((p) => p.id))
      const toAdd = filteredProducts.filter((p) => !currentIds.has(p.id))
      const newSelection = [...selectedProducts, ...toAdd].slice(0, maxSelection)
      onSelectionChange(newSelection)
    }
  }

  // 清空選擇
  const clearSelection = () => {
    onSelectionChange([])
  }

  const allFilteredSelected =
    filteredProducts.length > 0 && filteredProducts.every((p) => isSelected(p.id))

  return (
    <div className={cn('space-y-4', className)}>
      {/* 搜索和過濾 */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="搜索商品名稱、品牌、SKU..."
            className="pl-10 bg-white/50"
          />
        </div>

        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-3 py-2 rounded-lg border border-slate-200 bg-white/50 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500"
        >
          <option value="">所有分類</option>
          {categories.map((cat) => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>
      </div>

      {/* 已選擇摘要 */}
      <div className="flex items-center justify-between px-3 py-2 bg-slate-50 rounded-lg">
        <div className="flex items-center gap-2">
          <HoloBadge variant={selectedProducts.length > 0 ? 'info' : 'default'}>
            已選 {selectedProducts.length}/{maxSelection}
          </HoloBadge>
          {selectedProducts.length > 0 && (
            <button
              onClick={clearSelection}
              className="text-xs text-slate-500 hover:text-red-500 transition-colors"
            >
              清空選擇
            </button>
          )}
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={toggleSelectAll}
          disabled={filteredProducts.length === 0}
          className="text-xs"
        >
          {allFilteredSelected ? '取消全選' : '全選當前'}
        </Button>
      </div>

      {/* 商品列表 */}
      <div className="border border-slate-200 rounded-lg overflow-hidden max-h-[400px] overflow-y-auto">
        {productsLoading ? (
          <div className="p-4 space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex items-center gap-3">
                <HoloSkeleton variant="rectangular" width={40} height={40} />
                <div className="flex-1 space-y-1">
                  <HoloSkeleton variant="text" width="60%" />
                  <HoloSkeleton variant="text" width="30%" />
                </div>
              </div>
            ))}
          </div>
        ) : filteredProducts.length === 0 ? (
          <div className="p-8 text-center text-slate-400">
            <Package className="w-10 h-10 mx-auto mb-2 text-slate-300" />
            <p className="text-sm">
              {searchQuery || selectedCategory ? '無符合條件的商品' : '暫無商品'}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {filteredProducts.map((product) => {
              const selected = isSelected(product.id)
              return (
                <div
                  key={product.id}
                  onClick={() => toggleSelection(product)}
                  className={cn(
                    'flex items-center gap-3 px-4 py-3 cursor-pointer transition-colors',
                    selected
                      ? 'bg-cyan-50 hover:bg-cyan-100'
                      : 'hover:bg-slate-50',
                    selectedProducts.length >= maxSelection &&
                      !selected &&
                      'opacity-50 cursor-not-allowed'
                  )}
                >
                  {/* Checkbox */}
                  <div
                    className={cn(
                      'w-5 h-5 rounded border-2 flex items-center justify-center transition-colors',
                      selected
                        ? 'bg-cyan-500 border-cyan-500'
                        : 'border-slate-300'
                    )}
                  >
                    {selected && <Check className="w-3 h-3 text-white" />}
                  </div>

                  {/* 商品圖片 */}
                  {product.image_url ? (
                    <img
                      src={product.image_url}
                      alt={product.name}
                      className="w-10 h-10 rounded object-cover"
                    />
                  ) : (
                    <div className="w-10 h-10 rounded bg-slate-100 flex items-center justify-center">
                      <Package className="w-5 h-5 text-slate-400" />
                    </div>
                  )}

                  {/* 商品信息 */}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900 truncate">
                      {product.name}
                    </p>
                    <p className="text-xs text-slate-500">
                      {product.brand && <span>{product.brand} · </span>}
                      {product.sku && <span>SKU: {product.sku}</span>}
                    </p>
                  </div>

                  {/* 價格 */}
                  {product.price && (
                    <div className="text-sm font-medium text-slate-700">
                      ${product.price}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* 已選商品標籤 */}
      {selectedProducts.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {selectedProducts.slice(0, 10).map((product) => (
            <Badge
              key={product.id}
              variant="secondary"
              className="flex items-center gap-1 pr-1"
            >
              <span className="truncate max-w-[150px]">{product.name}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  toggleSelection(product)
                }}
                className="p-0.5 hover:bg-slate-300 rounded"
              >
                <X className="w-3 h-3" />
              </button>
            </Badge>
          ))}
          {selectedProducts.length > 10 && (
            <Badge variant="outline">+{selectedProducts.length - 10} 更多</Badge>
          )}
        </div>
      )}
    </div>
  )
}
