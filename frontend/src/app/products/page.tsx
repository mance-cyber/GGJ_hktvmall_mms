'use client'

// =============================================
// 商品管理頁面 - Future Tech 設計
// =============================================

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, OwnProduct } from '@/lib/api'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search,
  Plus,
  MoreHorizontal,
  Edit,
  Trash2,
  Package,
  AlertCircle,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  Archive,
  CheckCircle2,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'
import {
  PageTransition,
  HoloCard,
  HoloPanelHeader,
  HoloButton,
  HoloBadge,
  DataMetric,
  PulseStatus,
  HoloSkeleton,
  TechDivider,
  StaggerContainer,
} from '@/components/ui/future-tech'

export default function ProductsPage() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [categoryFilter, setCategoryFilter] = useState('all')

  const { data: productsData, isLoading, error } = useQuery({
    queryKey: ['products', page, search, statusFilter, categoryFilter],
    queryFn: () => api.getProducts(
      page,
      20,
      search || undefined,
      statusFilter === 'all' ? undefined : statusFilter,
      categoryFilter === 'all' ? undefined : categoryFilter
    ),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.deleteOwnProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
  })

  const syncMutation = useMutation({
    mutationFn: () => api.hktvSyncProducts(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      alert('同步已開始！模式: ' + data.mode + '\n' + data.message)
    },
    onError: (err) => {
      alert('同步失敗: ' + err)
    }
  })

  const totalPages = productsData ? Math.ceil(productsData.total / productsData.limit) : 0

  // 計算統計數據
  const stats = {
    total: productsData?.total || 0,
    active: productsData?.data.filter(p => p.status === 'active').length || 0,
    lowStock: productsData?.data.filter(p => p.stock_quantity < 10).length || 0,
  }

  if (isLoading) {
    return (
      <PageTransition>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <HoloSkeleton variant="text" width={200} height={32} />
            <HoloSkeleton variant="rectangular" width={120} height={36} />
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <HoloSkeleton key={i} variant="rectangular" height={100} />
            ))}
          </div>
          <HoloSkeleton variant="rectangular" height={400} />
        </div>
      </PageTransition>
    )
  }

  if (error) {
    return (
      <PageTransition>
        <HoloCard className="p-6 border-red-200 bg-red-50/50">
          <div className="flex items-center text-red-600">
            <AlertCircle className="w-5 h-5 mr-3" />
            <span className="font-medium">無法載入商品數據，請稍後再試。</span>
          </div>
        </HoloCard>
      </PageTransition>
    )
  }

  return (
    <PageTransition>
      <div className="space-y-6">
        {/* ========== 頁面標題 ========== */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-800">
              商品管理
            </h1>
            <p className="text-slate-500 mt-1 hidden sm:block">
              管理您的商品庫存與價格策略
            </p>
          </div>
          <div className="flex gap-2">
            <HoloButton
              variant="secondary"
              size="sm"
              onClick={() => syncMutation.mutate()}
              disabled={syncMutation.isPending}
              loading={syncMutation.isPending}
              icon={<RefreshCw className={cn("w-4 h-4", syncMutation.isPending && "animate-spin")} />}
            >
              <span className="hidden sm:inline">同步 HKTVmall</span>
              <span className="sm:hidden">同步</span>
            </HoloButton>
            <HoloButton size="sm" icon={<Plus className="w-4 h-4" />}>
              <span className="hidden sm:inline">新增商品</span>
            </HoloButton>
          </div>
        </div>

        {/* ========== 數據指標 ========== */}
        <StaggerContainer className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <DataMetric
            label="總商品數"
            value={stats.total}
            color="blue"
            icon={<Package className="w-5 h-5 text-blue-500" />}
          />
          <DataMetric
            label="上架中"
            value={stats.active}
            color="green"
            icon={<CheckCircle2 className="w-5 h-5 text-emerald-500" />}
          />
          <DataMetric
            label="低庫存警告"
            value={stats.lowStock}
            color="orange"
            icon={<AlertCircle className="w-5 h-5 text-orange-500" />}
          />
          <HoloCard className="p-4" glowColor="cyan">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-500">同步狀態</p>
                <p className="text-lg font-semibold text-slate-800 mt-1">
                  {syncMutation.isPending ? '同步中...' : '已同步'}
                </p>
              </div>
              <div className="p-3 rounded-xl bg-cyan-50">
                <RefreshCw className={cn("w-5 h-5 text-cyan-500", syncMutation.isPending && "animate-spin")} />
              </div>
            </div>
          </HoloCard>
        </StaggerContainer>

        {/* ========== 搜索與過濾 ========== */}
        <HoloCard className="p-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="搜索商品名稱、SKU..."
                className="pl-9 bg-white/50 border-slate-200"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[130px] bg-white/50 border-slate-200">
                  <SelectValue placeholder="狀態" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">所有狀態</SelectItem>
                  <SelectItem value="active">上架中</SelectItem>
                  <SelectItem value="draft">草稿</SelectItem>
                  <SelectItem value="archived">已歸檔</SelectItem>
                </SelectContent>
              </Select>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger className="w-[130px] bg-white/50 border-slate-200">
                  <SelectValue placeholder="分類" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">所有分類</SelectItem>
                  <SelectItem value="health">保健品</SelectItem>
                  <SelectItem value="beauty">美容護膚</SelectItem>
                  <SelectItem value="food">食品飲料</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </HoloCard>

        {/* ========== 手機版卡片視圖 ========== */}
        <div className="sm:hidden space-y-3">
          <AnimatePresence mode="popLayout">
            {productsData?.data.map((product, index) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ delay: index * 0.03 }}
              >
                <HoloCard className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="w-16 h-16 rounded-xl bg-slate-100 flex items-center justify-center overflow-hidden border border-slate-200 flex-shrink-0">
                      {product.images?.[0] ? (
                        <img src={product.images[0]} alt={product.name} className="w-full h-full object-cover" />
                      ) : (
                        <Package className="w-8 h-8 text-slate-400" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div className="font-medium text-slate-800 truncate">{product.name}</div>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-7 w-7 p-0 flex-shrink-0">
                              <MoreHorizontal className="h-4 w-4 text-slate-500" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem><Edit className="mr-2 h-4 w-4" /> 編輯</DropdownMenuItem>
                            <DropdownMenuItem onClick={() => syncMutation.mutate()}>
                              <RefreshCw className="mr-2 h-4 w-4" /> 同步
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              className="text-red-600"
                              onClick={() => deleteMutation.mutate(product.id)}
                            >
                              <Trash2 className="mr-2 h-4 w-4" /> 刪除
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                      <div className="text-xs text-slate-500 mt-0.5">SKU: {product.sku}</div>
                      <div className="flex items-center gap-3 mt-2">
                        <StatusBadge status={product.status} />
                        <span className="font-mono font-medium text-slate-700">
                          ${product.price ? Number(product.price).toFixed(2) : '-'}
                        </span>
                        <span className={cn("text-sm", product.stock_quantity < 10 ? "text-red-500" : "text-slate-500")}>
                          庫存: {product.stock_quantity}
                        </span>
                      </div>
                    </div>
                  </div>
                </HoloCard>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* ========== 桌面版表格視圖 ========== */}
        <div className="hidden sm:block">
          <HoloCard className="overflow-hidden">
            <HoloPanelHeader
              title="商品列表"
              subtitle={`共 ${productsData?.total || 0} 件商品`}
              icon={<Package className="w-5 h-5" />}
            />
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50/80 text-slate-600 font-medium border-b border-slate-100">
                  <tr>
                    <th className="px-6 py-4 text-left">商品資訊</th>
                    <th className="px-6 py-4 text-left">狀態</th>
                    <th className="px-6 py-4 text-right">售價</th>
                    <th className="px-6 py-4 text-right">庫存</th>
                    <th className="px-6 py-4 text-right">操作</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100/50">
                  <AnimatePresence mode="popLayout">
                    {productsData?.data.map((product, index) => (
                      <motion.tr
                        key={product.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ delay: index * 0.02 }}
                        className="hover:bg-cyan-50/30 transition-colors group"
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center overflow-hidden border border-slate-200">
                              {product.images?.[0] ? (
                                <img src={product.images[0]} alt={product.name} className="w-full h-full object-cover" />
                              ) : (
                                <Package className="w-6 h-6 text-slate-400" />
                              )}
                            </div>
                            <div>
                              <div className="font-medium text-slate-800 group-hover:text-cyan-600 transition-colors">
                                {product.name}
                              </div>
                              <div className="text-xs text-slate-500 mt-0.5">SKU: {product.sku}</div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <StatusBadge status={product.status} />
                        </td>
                        <td className="px-6 py-4 text-right font-mono font-medium text-slate-700">
                          ${product.price ? Number(product.price).toFixed(2) : '-'}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <span className={cn(
                            "font-medium",
                            product.stock_quantity < 10 ? "text-red-500" : "text-slate-600"
                          )}>
                            {product.stock_quantity}
                          </span>
                          {product.stock_quantity < 10 && (
                            <span className="ml-2 text-xs text-red-400">低庫存</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" className="h-8 w-8 p-0">
                                <MoreHorizontal className="h-4 w-4 text-slate-500" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuLabel>操作</DropdownMenuLabel>
                              <DropdownMenuItem><Edit className="mr-2 h-4 w-4" /> 編輯</DropdownMenuItem>
                              <DropdownMenuItem onClick={() => syncMutation.mutate()}>
                                <RefreshCw className="mr-2 h-4 w-4" /> 更新同步
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem
                                className="text-red-600"
                                onClick={() => deleteMutation.mutate(product.id)}
                              >
                                <Trash2 className="mr-2 h-4 w-4" /> 刪除
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </td>
                      </motion.tr>
                    ))}
                  </AnimatePresence>
                </tbody>
              </table>
            </div>

            {productsData?.data.length === 0 && (
              <div className="py-16 text-center text-slate-500">
                <Package className="w-12 h-12 mx-auto mb-4 text-slate-300" />
                <p>沒有找到符合條件的商品</p>
              </div>
            )}

            {/* 分頁 */}
            <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-between">
              <div className="text-sm text-slate-500">
                顯示 {(page - 1) * 20 + 1} 至 {Math.min(page * 20, productsData?.total || 0)} 筆，共 {productsData?.total || 0} 筆
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="icon"
                  disabled={page <= 1}
                  onClick={() => setPage(p => p - 1)}
                  className="h-8 w-8"
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  disabled={page >= totalPages}
                  onClick={() => setPage(p => p + 1)}
                  className="h-8 w-8"
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </HoloCard>
        </div>

        {/* 手機版分頁 */}
        <div className="sm:hidden flex items-center justify-between">
          <div className="text-xs text-slate-500">
            {(page - 1) * 20 + 1}-{Math.min(page * 20, productsData?.total || 0)} / {productsData?.total || 0}
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="icon" disabled={page <= 1} onClick={() => setPage(p => p - 1)} className="h-8 w-8">
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" disabled={page >= totalPages} onClick={() => setPage(p => p + 1)} className="h-8 w-8">
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </PageTransition>
  )
}

// =============================================
// 狀態標籤組件
// =============================================

function StatusBadge({ status }: { status: string }) {
  const config: Record<string, { variant: 'success' | 'warning' | 'default'; label: string }> = {
    active: { variant: 'success', label: '上架中' },
    draft: { variant: 'default', label: '草稿' },
    archived: { variant: 'warning', label: '已歸檔' },
  }

  const { variant, label } = config[status] || config.draft

  return <HoloBadge variant={variant}>{label}</HoloBadge>
}
