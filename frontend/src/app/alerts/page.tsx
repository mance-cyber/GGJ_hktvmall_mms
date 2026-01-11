'use client'

import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, PriceAlert } from '@/lib/api'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Bell,
  CheckCheck,
  TrendingDown,
  TrendingUp,
  AlertTriangle,
  Clock,
  Filter,
  Eye,
  Check,
  Search,
  Calendar,
  Building2,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  Inbox,
  Archive,
  Trash2,
  MoreHorizontal,
  X,
  SlidersHorizontal
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'
import { cn } from '@/lib/utils'
import {
  PageTransition,
  HoloCard,
  HoloPanelHeader,
  HoloButton,
  HoloBadge,
  DataMetric,
  HoloSkeleton,
  StaggerContainer,
} from '@/components/ui/future-tech'

// =============================================
// 類型定義
// =============================================

type FilterType = 'all' | 'unread' | 'price_drop' | 'price_increase' | 'out_of_stock' | 'back_in_stock'

// =============================================
// 主頁面
// =============================================

export default function AlertsPage() {
  const queryClient = useQueryClient()
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState<FilterType>('all')
  const [selectedAlerts, setSelectedAlerts] = useState<Set<string>>(new Set())
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 20

  // 獲取警報數據
  const { data: alerts, isLoading, refetch } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => api.getAlerts(undefined, undefined, 100),
    refetchInterval: 30000,
  })

  // 標記已讀
  const markReadMutation = useMutation({
    mutationFn: (alertId: string) => api.markAlertRead(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })

  // 過濾和搜索
  const filteredAlerts = useMemo(() => {
    if (!alerts?.data) return []

    let result = [...alerts.data]

    // 按類型過濾
    if (filterType === 'unread') {
      result = result.filter(a => !a.is_read)
    } else if (filterType !== 'all') {
      result = result.filter(a => a.alert_type === filterType)
    }

    // 搜索過濾
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      result = result.filter(a =>
        a.product_name.toLowerCase().includes(query) ||
        a.competitor_name.toLowerCase().includes(query)
      )
    }

    return result
  }, [alerts?.data, filterType, searchQuery])

  // 分頁
  const totalPages = Math.ceil(filteredAlerts.length / pageSize)
  const paginatedAlerts = filteredAlerts.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  )

  // 統計數據
  const stats = useMemo(() => {
    if (!alerts?.data) return { total: 0, unread: 0, priceDrops: 0, priceIncreases: 0 }
    return {
      total: alerts.data.length,
      unread: alerts.data.filter(a => !a.is_read).length,
      priceDrops: alerts.data.filter(a => a.alert_type === 'price_drop').length,
      priceIncreases: alerts.data.filter(a => a.alert_type === 'price_increase').length,
    }
  }, [alerts?.data])

  // 批量操作
  const handleSelectAll = () => {
    if (selectedAlerts.size === paginatedAlerts.length) {
      setSelectedAlerts(new Set())
    } else {
      setSelectedAlerts(new Set(paginatedAlerts.map(a => a.id)))
    }
  }

  const handleMarkAllRead = async () => {
    const unreadAlerts = alerts?.data.filter(a => !a.is_read) || []
    for (const alert of unreadAlerts) {
      await api.markAlertRead(alert.id)
    }
    queryClient.invalidateQueries({ queryKey: ['alerts'] })
  }

  // ========== Loading 骨架屏 ==========
  if (isLoading) {
    return (
      <PageTransition>
        <div className="space-y-6">
          {/* 標題骨架屏 */}
          <div className="flex items-start justify-between">
            <div>
              <HoloSkeleton variant="text" width={200} height={36} />
              <HoloSkeleton variant="text" width={300} height={20} className="mt-2" />
            </div>
            <div className="flex gap-3">
              <HoloSkeleton variant="rectangular" width={100} height={40} />
              <HoloSkeleton variant="rectangular" width={140} height={40} />
            </div>
          </div>

          {/* 統計卡片骨架屏 */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <HoloSkeleton key={i} variant="rectangular" height={100} />
            ))}
          </div>

          {/* 工具欄骨架屏 */}
          <div className="flex items-center justify-between gap-4">
            <HoloSkeleton variant="rectangular" width={400} height={40} />
            <HoloSkeleton variant="rectangular" width={120} height={40} />
          </div>

          {/* 列表骨架屏 */}
          <HoloCard className="overflow-hidden">
            <div className="px-6 py-3 bg-slate-50/80 border-b border-slate-100">
              <HoloSkeleton variant="text" width={150} height={20} />
            </div>
            <div className="divide-y divide-slate-100">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="px-6 py-4 flex items-center gap-4">
                  <HoloSkeleton variant="circular" width={20} height={20} />
                  <HoloSkeleton variant="circular" width={44} height={44} />
                  <div className="flex-1 space-y-2">
                    <HoloSkeleton variant="text" width={200} height={16} />
                    <HoloSkeleton variant="text" width={300} height={14} />
                  </div>
                  <HoloSkeleton variant="text" width={100} height={20} />
                </div>
              ))}
            </div>
          </HoloCard>
        </div>
      </PageTransition>
    )
  }

  return (
    <PageTransition>
      <div className="space-y-6">
        {/* ========== 頁面標題 ========== */}
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
              警報中心
              {stats.unread > 0 && (
                <HoloBadge variant="error" pulse>
                  {stats.unread} 未讀
                </HoloBadge>
              )}
            </h1>
            <p className="text-muted-foreground mt-2 text-lg">
              即時監控市場價格波動，把握每一個競爭優勢
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <HoloButton
              variant="secondary"
              onClick={() => refetch()}
              icon={<RefreshCw className="w-4 h-4" />}
            >
              刷新
            </HoloButton>
            {stats.unread > 0 && (
              <HoloButton
                variant="primary"
                onClick={handleMarkAllRead}
                icon={<CheckCheck className="w-4 h-4" />}
              >
                全部標為已讀
              </HoloButton>
            )}
          </div>
        </div>

        {/* ========== 統計卡片 ========== */}
        <StaggerContainer className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard
            label="總警報數"
            value={stats.total}
            icon={<Bell className="w-5 h-5" />}
            color="cyan"
            active={filterType === 'all'}
            onClick={() => setFilterType('all')}
          />
          <MetricCard
            label="未讀警報"
            value={stats.unread}
            icon={<Inbox className="w-5 h-5" />}
            color="blue"
            active={filterType === 'unread'}
            onClick={() => setFilterType('unread')}
          />
          <MetricCard
            label="價格下跌"
            value={stats.priceDrops}
            icon={<TrendingDown className="w-5 h-5" />}
            color="green"
            active={filterType === 'price_drop'}
            onClick={() => setFilterType('price_drop')}
          />
          <MetricCard
            label="價格上漲"
            value={stats.priceIncreases}
            icon={<TrendingUp className="w-5 h-5" />}
            color="orange"
            active={filterType === 'price_increase'}
            onClick={() => setFilterType('price_increase')}
          />
        </StaggerContainer>

        {/* ========== 工具欄 ========== */}
        <div className="flex items-center justify-between gap-4">
          {/* 搜索框 */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              type="text"
              placeholder="搜索商品名稱或競爭對手..."
              value={searchQuery}
              onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }}
              className="pl-9 bg-white/50"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* 過濾器 */}
          <div className="flex items-center space-x-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="h-10">
                  <SlidersHorizontal className="w-4 h-4 mr-2" />
                  {filterType === 'all' ? '全部類型' :
                   filterType === 'unread' ? '未讀' :
                   filterType === 'price_drop' ? '降價' :
                   filterType === 'price_increase' ? '漲價' :
                   filterType === 'out_of_stock' ? '缺貨' : '補貨'}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem onClick={() => { setFilterType('all'); setCurrentPage(1); }}>
                  <Bell className="w-4 h-4 mr-2" />
                  全部類型
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => { setFilterType('unread'); setCurrentPage(1); }}>
                  <Inbox className="w-4 h-4 mr-2" />
                  未讀警報
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => { setFilterType('price_drop'); setCurrentPage(1); }}>
                  <TrendingDown className="w-4 h-4 mr-2 text-green-500" />
                  價格下跌
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => { setFilterType('price_increase'); setCurrentPage(1); }}>
                  <TrendingUp className="w-4 h-4 mr-2 text-red-500" />
                  價格上漲
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => { setFilterType('out_of_stock'); setCurrentPage(1); }}>
                  <AlertTriangle className="w-4 h-4 mr-2 text-orange-500" />
                  缺貨警報
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => { setFilterType('back_in_stock'); setCurrentPage(1); }}>
                  <Check className="w-4 h-4 mr-2 text-blue-500" />
                  補貨通知
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* ========== 警報列表 ========== */}
        <HoloCard className="overflow-hidden" glowColor="cyan">
          {/* 列表頭部 */}
          <div className="px-6 py-3 bg-slate-50/80 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button onClick={handleSelectAll} className="p-1 hover:bg-slate-200 rounded">
                <div className={cn(
                  "w-4 h-4 border-2 rounded flex items-center justify-center",
                  selectedAlerts.size === paginatedAlerts.length && paginatedAlerts.length > 0
                    ? "bg-blue-500 border-blue-500"
                    : "border-slate-300"
                )}>
                  {selectedAlerts.size === paginatedAlerts.length && paginatedAlerts.length > 0 && (
                    <Check className="w-3 h-3 text-white" />
                  )}
                </div>
              </button>
              <span className="text-sm text-slate-600">
                {filteredAlerts.length} 條警報
                {searchQuery && ` (搜索: "${searchQuery}")`}
              </span>
            </div>
            {selectedAlerts.size > 0 && (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-slate-500">已選 {selectedAlerts.size} 項</span>
                <HoloButton size="sm" variant="ghost">
                  <CheckCheck className="w-4 h-4 mr-1" />
                  標為已讀
                </HoloButton>
              </div>
            )}
          </div>

          {/* 警報列表 */}
          <div className="divide-y divide-slate-100">
            <AnimatePresence mode="popLayout">
              {paginatedAlerts.map((alert, index) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ delay: index * 0.02 }}
                >
                  <AlertCard
                    alert={alert}
                    isSelected={selectedAlerts.has(alert.id)}
                    onSelect={() => {
                      const newSet = new Set(selectedAlerts)
                      if (newSet.has(alert.id)) {
                        newSet.delete(alert.id)
                      } else {
                        newSet.add(alert.id)
                      }
                      setSelectedAlerts(newSet)
                    }}
                    onMarkRead={() => markReadMutation.mutate(alert.id)}
                  />
                </motion.div>
              ))}
            </AnimatePresence>
          </div>

          {/* 空狀態 */}
          {paginatedAlerts.length === 0 && (
            <div className="px-6 py-16 text-center">
              <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Bell className="w-8 h-8 text-slate-300" />
              </div>
              <h3 className="text-lg font-medium text-slate-800">
                {searchQuery ? '未找到匹配的警報' : '暫無警報'}
              </h3>
              <p className="text-slate-500 mt-1">
                {searchQuery ? '請嘗試其他搜索關鍵詞' : '當競品價格變動時會顯示在這裡'}
              </p>
            </div>
          )}

          {/* 分頁 */}
          {totalPages > 1 && (
            <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-between bg-slate-50/50">
              <span className="text-sm text-slate-500">
                第 {currentPage} / {totalPages} 頁，共 {filteredAlerts.length} 條
              </span>
              <div className="flex items-center space-x-2">
                <HoloButton
                  variant="secondary"
                  size="sm"
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage <= 1}
                  icon={<ChevronLeft className="w-4 h-4" />}
                >
                  上一頁
                </HoloButton>
                <HoloButton
                  variant="secondary"
                  size="sm"
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage >= totalPages}
                  icon={<ChevronRight className="w-4 h-4" />}
                >
                  下一頁
                </HoloButton>
              </div>
            </div>
          )}
        </HoloCard>
      </div>
    </PageTransition>
  )
}

// =============================================
// 子組件
// =============================================

// 可點擊的指標卡片包裝器
function MetricCard({
  label,
  value,
  icon,
  color = 'cyan',
  active,
  onClick
}: {
  label: string
  value: number
  icon: React.ReactNode
  color?: 'blue' | 'cyan' | 'green' | 'orange' | 'purple'
  active?: boolean
  onClick?: () => void
}) {
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={cn(
        "text-left w-full transition-all rounded-xl",
        active && "ring-2 ring-offset-2",
        color === 'cyan' && active && "ring-cyan-400",
        color === 'blue' && active && "ring-blue-400",
        color === 'green' && active && "ring-emerald-400",
        color === 'orange' && active && "ring-amber-400",
        color === 'purple' && active && "ring-violet-400",
      )}
    >
      <DataMetric
        label={label}
        value={value}
        icon={icon}
        color={color}
        size="sm"
      />
    </motion.button>
  )
}

function AlertCard({
  alert,
  isSelected,
  onSelect,
  onMarkRead
}: {
  alert: PriceAlert
  isSelected: boolean
  onSelect: () => void
  onMarkRead: () => void
}) {
  const isRead = alert.is_read

  const typeConfig = {
    price_drop: {
      icon: TrendingDown,
      color: "text-green-600",
      bg: "bg-green-100",
      label: "降價",
      badgeVariant: "success" as const
    },
    price_increase: {
      icon: TrendingUp,
      color: "text-red-600",
      bg: "bg-red-100",
      label: "漲價",
      badgeVariant: "error" as const
    },
    out_of_stock: {
      icon: AlertTriangle,
      color: "text-orange-600",
      bg: "bg-orange-100",
      label: "缺貨",
      badgeVariant: "warning" as const
    },
    back_in_stock: {
      icon: Check,
      color: "text-blue-600",
      bg: "bg-blue-100",
      label: "補貨",
      badgeVariant: "info" as const
    },
  }

  const config = typeConfig[alert.alert_type as keyof typeof typeConfig] || {
    icon: Bell,
    color: "text-slate-600",
    bg: "bg-slate-100",
    label: "通知",
    badgeVariant: "default" as const
  }

  const Icon = config.icon

  return (
    <div className={cn(
      "px-6 py-4 flex items-center gap-4 transition-all hover:bg-slate-50/80 group",
      !isRead && "bg-blue-50/30",
      isSelected && "bg-blue-100/50"
    )}>
      {/* 選擇框 */}
      <button onClick={onSelect} className="flex-shrink-0">
        <div className={cn(
          "w-5 h-5 border-2 rounded flex items-center justify-center transition-colors",
          isSelected ? "bg-blue-500 border-blue-500" : "border-slate-300 hover:border-slate-400"
        )}>
          {isSelected && <Check className="w-3 h-3 text-white" />}
        </div>
      </button>

      {/* 圖標 */}
      <div className={cn("p-2.5 rounded-xl flex-shrink-0", config.bg)}>
        <Icon className={cn("w-5 h-5", config.color)} />
      </div>

      {/* 內容 */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <HoloBadge variant={config.badgeVariant} size="sm">
            {config.label}
          </HoloBadge>
          {!isRead && (
            <span className="flex items-center text-xs text-blue-600 font-medium">
              <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-1 animate-pulse" />
              未讀
            </span>
          )}
        </div>

        <h3 className="font-semibold text-slate-800 truncate mb-1">
          {alert.product_name}
        </h3>

        <div className="flex items-center text-sm text-slate-500 space-x-3">
          <span className="flex items-center">
            <Building2 className="w-3.5 h-3.5 mr-1" />
            {alert.competitor_name}
          </span>
          <span className="flex items-center">
            <Clock className="w-3.5 h-3.5 mr-1" />
            {new Date(alert.created_at).toLocaleString('zh-HK')}
          </span>
        </div>
      </div>

      {/* 價格變動 */}
      <div className="flex-shrink-0 text-right min-w-[120px]">
        <div className="flex items-center justify-end space-x-2 font-mono">
          <span className="text-slate-400 line-through text-sm">{alert.old_value}</span>
          <span className="text-slate-800 font-bold">{alert.new_value}</span>
        </div>
        {alert.change_percent && (
          <span className={cn(
            "text-sm font-bold",
            alert.change_percent > 0 ? "text-red-600" : "text-green-600"
          )}>
            {alert.change_percent > 0 ? '+' : ''}{alert.change_percent.toFixed(1)}%
          </span>
        )}
      </div>

      {/* 操作按鈕 */}
      <div className="flex-shrink-0 flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
        {!isRead && (
          <HoloButton
            size="sm"
            variant="ghost"
            onClick={onMarkRead}
            icon={<CheckCheck className="w-4 h-4" />}
          >
            已讀
          </HoloButton>
        )}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button size="sm" variant="ghost" className="h-8 px-2">
              <MoreHorizontal className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <Eye className="w-4 h-4 mr-2" />
              查看詳情
            </DropdownMenuItem>
            <DropdownMenuItem>
              <ExternalLink className="w-4 h-4 mr-2" />
              前往商品頁
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-slate-500">
              <Archive className="w-4 h-4 mr-2" />
              歸檔
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  )
}
