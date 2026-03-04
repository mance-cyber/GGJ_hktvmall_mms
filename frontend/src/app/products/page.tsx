'use client'

// =============================================
// 商品管理頁面 - Future Tech 設計
// =============================================

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient, keepPreviousData } from '@tanstack/react-query'
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
import { useLocale } from '@/components/providers/locale-provider'

export default function ProductsPage() {
  const queryClient = useQueryClient()
  const { t } = useLocale()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [categoryFilter, setCategoryFilter] = useState('all')

  const { data: productsData, isLoading, isFetching, error } = useQuery({
    queryKey: ['products', page, search, statusFilter, categoryFilter],
    queryFn: () => api.getProducts(
      page,
      20,
      search || undefined,
      statusFilter === 'all' ? undefined : statusFilter,
      categoryFilter === 'all' ? undefined : categoryFilter
    ),
    placeholderData: keepPreviousData,
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
      alert(data.message)
    },
    onError: (err: any) => {
      const msg = err?.message || err?.detail || String(err)
      alert(t['products.sync_failed'] + msg)
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
        <div className="space-y-3 sm:space-y-6">
          <div className="flex items-center justify-between">
            <HoloSkeleton variant="text" width={150} height={28} />
            <HoloSkeleton variant="rectangular" width={80} height={32} />
          </div>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-4">
            {[...Array(4)].map((_, i) => (
              <HoloSkeleton key={i} variant="rectangular" height={80} />
            ))}
          </div>
          <HoloSkeleton variant="rectangular" height={300} />
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
            <span className="font-medium">{t['products.load_error']}</span>
          </div>
        </HoloCard>
      </PageTransition>
    )
  }

  return (
    <PageTransition>
      <div className="space-y-3 sm:space-y-6">
        {/* ========== 頁面標題 ========== */}
        <div className="flex items-center justify-between gap-2">
          <h1 className="page-title">{t['products.title']}</h1>
          <div className="flex gap-1.5 sm:gap-2">
            <HoloButton
              variant="secondary"
              size="sm"
              onClick={() => syncMutation.mutate()}
              disabled={syncMutation.isPending}
              loading={syncMutation.isPending}
              icon={<RefreshCw className={cn("w-3.5 h-3.5 sm:w-4 sm:h-4", syncMutation.isPending && "animate-spin")} />}
            >
              <span className="hidden sm:inline">{t['products.sync']}</span>
            </HoloButton>
            <HoloButton size="sm" icon={<Plus className="w-3.5 h-3.5 sm:w-4 sm:h-4" />}>
              <span className="hidden sm:inline">{t['products.add']}</span>
            </HoloButton>
          </div>
        </div>

        {/* ========== 數據指標 ========== */}
        <StaggerContainer className="grid grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-4">
          <DataMetric
            label={t['products.total']}
            value={stats.total}
            color="blue"
            size="sm"
            icon={<Package className="w-4 h-4 sm:w-5 sm:h-5 text-blue-500" />}
          />
          <DataMetric
            label={t['products.active']}
            value={stats.active}
            color="green"
            size="sm"
            icon={<CheckCircle2 className="w-4 h-4 sm:w-5 sm:h-5 text-emerald-500" />}
          />
          <DataMetric
            label={t['products.low_stock']}
            value={stats.lowStock}
            color="orange"
            size="sm"
            icon={<AlertCircle className="w-4 h-4 sm:w-5 sm:h-5 text-orange-500" />}
          />
          <HoloCard className="p-2 sm:p-4" glowColor="cyan">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[10px] sm:text-sm text-slate-500">{t['products.sync']}</p>
                <p className="text-sm sm:text-lg font-semibold text-slate-800 mt-0.5 sm:mt-1">
                  {syncMutation.isPending ? t['products.sync_in_progress'] : t['products.sync_done']}
                </p>
              </div>
              <div className="p-2 sm:p-3 rounded-lg sm:rounded-xl bg-cyan-50">
                <RefreshCw className={cn("w-4 h-4 sm:w-5 sm:h-5 text-cyan-500", syncMutation.isPending && "animate-spin")} />
              </div>
            </div>
          </HoloCard>
        </StaggerContainer>

        {/* ========== 搜索與過濾 ========== */}
        <HoloCard className="p-2.5 sm:p-4">
          <div className="flex flex-col sm:flex-row gap-2 sm:gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 sm:left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 sm:h-4 sm:w-4 text-slate-400" />
              <Input
                placeholder={t['products.search_placeholder']}
                className="pl-8 sm:pl-9 h-9 sm:h-10 text-sm bg-white/50 border-slate-200"
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1) }}
              />
            </div>
            <div className="flex gap-1.5 sm:gap-2">
              <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(1) }}>
                <SelectTrigger className="flex-1 sm:w-[110px] h-9 sm:h-10 text-xs sm:text-sm bg-white/50 border-slate-200">
                  <SelectValue placeholder={t['products.filter_status']} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t['products.filter_all']}</SelectItem>
                  <SelectItem value="active">{t['products.filter_active']}</SelectItem>
                  <SelectItem value="draft">{t['products.filter_draft']}</SelectItem>
                  <SelectItem value="archived">{t['products.filter_archived']}</SelectItem>
                </SelectContent>
              </Select>
              <Select value={categoryFilter} onValueChange={(v) => { setCategoryFilter(v); setPage(1) }}>
                <SelectTrigger className="flex-1 sm:w-[110px] h-9 sm:h-10 text-xs sm:text-sm bg-white/50 border-slate-200">
                  <SelectValue placeholder={t['products.filter_category']} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">{t['products.filter_all']}</SelectItem>
                  <SelectItem value="health">{t['products.category_health']}</SelectItem>
                  <SelectItem value="beauty">{t['products.category_beauty']}</SelectItem>
                  <SelectItem value="food">{t['products.category_food']}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </HoloCard>

        {/* ========== 手機版卡片視圖 ========== */}
        <div className="sm:hidden space-y-2">
          <AnimatePresence mode="popLayout">
            {productsData?.data.map((product, index) => (
              <motion.div
                key={product.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ delay: index * 0.02 }}
              >
                <HoloCard className="p-2.5">
                  <div className="flex items-start gap-2.5">
                    <div className="w-12 h-12 rounded-lg bg-slate-100 flex items-center justify-center overflow-hidden border border-slate-200 flex-shrink-0">
                      {product.images?.[0] ? (
                        <img src={product.images[0]} alt={product.name} className="w-full h-full object-cover" />
                      ) : (
                        <Package className="w-6 h-6 text-slate-400" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-1">
                        <div className="text-sm font-medium text-slate-800 truncate">{product.name}</div>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" className="h-6 w-6 p-0 flex-shrink-0">
                              <MoreHorizontal className="h-3.5 w-3.5 text-slate-500" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem><Edit className="mr-2 h-4 w-4" /> {t['products.edit']}</DropdownMenuItem>
                            <DropdownMenuItem onClick={() => syncMutation.mutate()}>
                              <RefreshCw className="mr-2 h-4 w-4" /> {t['products.sync']}
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              className="text-red-600"
                              onClick={() => deleteMutation.mutate(product.id)}
                            >
                              <Trash2 className="mr-2 h-4 w-4" /> {t['products.delete']}
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <StatusBadge status={product.status} />
                        <span className="font-mono text-xs font-medium text-slate-700">
                          ${product.price ? Number(product.price).toFixed(0) : '-'}
                        </span>
                        <span className={cn("text-xs", product.stock_quantity < 10 ? "text-red-500" : "text-slate-500")}>
                          {t['products.stock_prefix']}{product.stock_quantity}
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
              title={t['products.table_title']}
              subtitle={t['products.table_subtitle'].replace('{total}', String(productsData?.total || 0))}
              icon={<Package className="w-5 h-5" />}
            />
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50/80 text-slate-600 font-medium border-b border-slate-100">
                  <tr>
                    <th className="px-6 py-4 text-left">{t['products.col_product_info']}</th>
                    <th className="px-6 py-4 text-left">{t['products.col_status']}</th>
                    <th className="px-6 py-4 text-right">{t['products.col_price']}</th>
                    <th className="px-6 py-4 text-right">{t['products.col_stock']}</th>
                    <th className="px-6 py-4 text-right">{t['products.col_actions']}</th>
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
                            <span className="ml-2 text-xs text-red-400">{t['products.badge_low_stock']}</span>
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
                              <DropdownMenuLabel>{t['products.actions_label']}</DropdownMenuLabel>
                              <DropdownMenuItem><Edit className="mr-2 h-4 w-4" /> {t['products.edit']}</DropdownMenuItem>
                              <DropdownMenuItem onClick={() => syncMutation.mutate()}>
                                <RefreshCw className="mr-2 h-4 w-4" /> {t['products.sync_update']}
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem
                                className="text-red-600"
                                onClick={() => deleteMutation.mutate(product.id)}
                              >
                                <Trash2 className="mr-2 h-4 w-4" /> {t['products.delete']}
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
                <p>{t['products.no_results']}</p>
              </div>
            )}

            {/* 分頁 */}
            <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-between">
              <div className="text-sm text-slate-500">
                {t['products.pagination']
                  .replace('{from}', String(productsData?.total ? (page - 1) * 20 + 1 : 0))
                  .replace('{to}', String(Math.min(page * 20, productsData?.total || 0)))
                  .replace('{total}', String(productsData?.total || 0))}
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="icon"
                  disabled={page <= 1 || isFetching}
                  onClick={() => setPage(p => p - 1)}
                  className="h-8 w-8"
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className={cn("text-sm tabular-nums min-w-[60px] text-center", isFetching && "text-slate-400")}>
                  {page} / {totalPages || 1}
                </span>
                <Button
                  variant="outline"
                  size="icon"
                  disabled={page >= totalPages || isFetching}
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
            {productsData?.total ? (page - 1) * 20 + 1 : 0}-{Math.min(page * 20, productsData?.total || 0)} / {productsData?.total || 0}
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="icon" disabled={page <= 1 || isFetching} onClick={() => setPage(p => p - 1)} className="h-8 w-8">
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className={cn("text-xs tabular-nums", isFetching && "text-slate-400")}>
              {page}/{totalPages || 1}
            </span>
            <Button variant="outline" size="icon" disabled={page >= totalPages || isFetching} onClick={() => setPage(p => p + 1)} className="h-8 w-8">
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
  const { t } = useLocale()

  const config: Record<string, { variant: 'success' | 'warning' | 'default'; label: string }> = {
    active: { variant: 'success', label: t['products.status_active'] },
    draft: { variant: 'default', label: t['products.status_draft'] },
    archived: { variant: 'warning', label: t['products.status_archived'] },
  }

  const { variant, label } = config[status] || config.draft

  return <HoloBadge variant={variant}>{label}</HoloBadge>
}
