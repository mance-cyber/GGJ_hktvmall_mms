'use client'

import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, PriceAlert } from '@/lib/api'
import Link from 'next/link'
import { useLocale } from '@/components/providers/locale-provider'
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
// Type definitions
// =============================================

type FilterType = 'all' | 'unread' | 'price_drop' | 'price_increase' | 'out_of_stock' | 'back_in_stock'

// =============================================
// Main page
// =============================================

export default function AlertsPage() {
  const queryClient = useQueryClient()
  const { t } = useLocale()
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState<FilterType>('all')
  const [selectedAlerts, setSelectedAlerts] = useState<Set<string>>(new Set())
  const [currentPage, setCurrentPage] = useState(1)
  const pageSize = 20

  // Fetch alert data
  const { data: alerts, isLoading, refetch } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => api.getAlerts(undefined, undefined, 100),
    refetchInterval: 30000,
  })

  // Mark as read
  const markReadMutation = useMutation({
    mutationFn: (alertId: string) => api.markAlertRead(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })

  // Mark all as read
  const [markingAllRead, setMarkingAllRead] = useState(false)

  // Filter and search
  const filteredAlerts = useMemo(() => {
    if (!alerts?.data) return []

    let result = [...alerts.data]

    // Filter by type
    if (filterType === 'unread') {
      result = result.filter(a => !a.is_read)
    } else if (filterType !== 'all') {
      result = result.filter(a => a.alert_type === filterType)
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      result = result.filter(a =>
        a.product_name.toLowerCase().includes(query) ||
        a.competitor_name.toLowerCase().includes(query)
      )
    }

    return result
  }, [alerts?.data, filterType, searchQuery])

  // Pagination
  const totalPages = Math.ceil(filteredAlerts.length / pageSize)
  const paginatedAlerts = filteredAlerts.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  )

  // Statistics
  const stats = useMemo(() => {
    if (!alerts?.data) return { total: 0, unread: 0, priceDrops: 0, priceIncreases: 0 }
    return {
      total: alerts.data.length,
      unread: alerts.data.filter(a => !a.is_read).length,
      priceDrops: alerts.data.filter(a => a.alert_type === 'price_drop').length,
      priceIncreases: alerts.data.filter(a => a.alert_type === 'price_increase').length,
    }
  }, [alerts?.data])

  // Batch operations
  const handleSelectAll = () => {
    if (selectedAlerts.size === paginatedAlerts.length) {
      setSelectedAlerts(new Set())
    } else {
      setSelectedAlerts(new Set(paginatedAlerts.map(a => a.id)))
    }
  }

  const handleMarkAllRead = async () => {
    setMarkingAllRead(true)
    try {
      await api.markAllAlertsRead()
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    } catch (err) {
      console.error('Failed to mark all alerts as read:', err)
    } finally {
      setMarkingAllRead(false)
    }
  }

  // ========== Loading Skeleton ==========
  if (isLoading) {
    return (
      <PageTransition>
        <div className="space-y-6">
          {/* Title skeleton */}
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

          {/* Stats card skeleton */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <HoloSkeleton key={i} variant="rectangular" height={100} />
            ))}
          </div>

          {/* Toolbar skeleton */}
          <div className="flex items-center justify-between gap-4">
            <HoloSkeleton variant="rectangular" width={400} height={40} />
            <HoloSkeleton variant="rectangular" width={120} height={40} />
          </div>

          {/* List skeleton */}
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
      <div className="space-y-4 sm:space-y-6">
        {/* ========== Page title ========== */}
        <div className="flex items-center justify-between gap-2">
          <div className="min-w-0">
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
              {t['alerts.title']}
              {stats.unread > 0 && (
                <HoloBadge variant="error" pulse>
                  {stats.unread}
                </HoloBadge>
              )}
            </h1>
            <p className="text-sm text-muted-foreground mt-1 hidden sm:block">
              {t['alerts.subtitle']}
            </p>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <HoloButton
              variant="secondary"
              size="sm"
              onClick={() => refetch()}
              icon={<RefreshCw className="w-3.5 h-3.5" />}
              className="px-2 sm:px-3"
            >
              <span className="hidden sm:inline">{t['alerts.refresh']}</span>
            </HoloButton>
            {stats.unread > 0 && (
              <HoloButton
                variant="primary"
                size="sm"
                onClick={handleMarkAllRead}
                disabled={markingAllRead}
                icon={markingAllRead ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <CheckCheck className="w-3.5 h-3.5" />}
              >
                <span className="hidden sm:inline">{markingAllRead ? 'Processing...' : t['alerts.mark_all_read']}</span>
                <span className="sm:hidden">{markingAllRead ? '...' : t['alerts.read']}</span>
              </HoloButton>
            )}
          </div>
        </div>

        {/* ========== Stats Cards ========== */}
        <StaggerContainer className="grid grid-cols-2 md:grid-cols-4 gap-2 sm:gap-3">
          <MetricCard
            label={t['alerts.total']}
            value={stats.total}
            icon={<Bell className="w-4 h-4" />}
            color="cyan"
            active={filterType === 'all'}
            onClick={() => setFilterType('all')}
          />
          <MetricCard
            label={t['alerts.unread']}
            value={stats.unread}
            icon={<Inbox className="w-4 h-4" />}
            color="blue"
            active={filterType === 'unread'}
            onClick={() => setFilterType('unread')}
          />
          <MetricCard
            label={t['alerts.price_drop']}
            value={stats.priceDrops}
            icon={<TrendingDown className="w-4 h-4" />}
            color="green"
            active={filterType === 'price_drop'}
            onClick={() => setFilterType('price_drop')}
          />
          <MetricCard
            label={t['alerts.price_increase']}
            value={stats.priceIncreases}
            icon={<TrendingUp className="w-4 h-4" />}
            color="orange"
            active={filterType === 'price_increase'}
            onClick={() => setFilterType('price_increase')}
          />
        </StaggerContainer>

        {/* ========== Toolbar ========== */}
        <div className="flex items-center gap-2 sm:gap-4">
          {/* Search box */}
          <div className="relative flex-1 sm:max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              type="text"
              placeholder={t['alerts.search_placeholder']}
              value={searchQuery}
              onChange={(e) => { setSearchQuery(e.target.value); setCurrentPage(1); }}
              className="pl-9 bg-white/50 h-9 text-sm"
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

          {/* Filters */}
          <div className="flex items-center space-x-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="h-10">
                  <SlidersHorizontal className="w-4 h-4 mr-2" />
                  {filterType === 'all' ? t['alerts.all_types'] :
                   filterType === 'unread' ? t['alerts.unread'] :
                   filterType === 'price_drop' ? t['alerts.price_drop'] :
                   filterType === 'price_increase' ? t['alerts.price_increase'] :
                   filterType === 'out_of_stock' ? t['alerts.out_of_stock'] : t['alerts.back_in_stock']}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem onClick={() => { setFilterType('all'); setCurrentPage(1); }}>
                  <Bell className="w-4 h-4 mr-2" />
                  {t['alerts.all_types']}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => { setFilterType('unread'); setCurrentPage(1); }}>
                  <Inbox className="w-4 h-4 mr-2" />
                  {t['alerts.unread_alerts']}
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => { setFilterType('price_drop'); setCurrentPage(1); }}>
                  <TrendingDown className="w-4 h-4 mr-2 text-green-500" />
                  {t['alerts.price_decreased']}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => { setFilterType('price_increase'); setCurrentPage(1); }}>
                  <TrendingUp className="w-4 h-4 mr-2 text-red-500" />
                  {t['alerts.price_increased']}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => { setFilterType('out_of_stock'); setCurrentPage(1); }}>
                  <AlertTriangle className="w-4 h-4 mr-2 text-orange-500" />
                  {t['alerts.out_of_stock_alert']}
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => { setFilterType('back_in_stock'); setCurrentPage(1); }}>
                  <Check className="w-4 h-4 mr-2 text-blue-500" />
                  {t['alerts.back_in_stock_alert']}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* ========== Alert list ========== */}
        <HoloCard className="overflow-hidden" glowColor="cyan">
          {/* List header */}
          <div className="px-3 sm:px-6 py-3 bg-slate-50/80 border-b border-slate-100 flex items-center justify-between">
            <div className="flex items-center space-x-3 sm:space-x-4">
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
              <span className="text-xs sm:text-sm text-slate-600">
                {filteredAlerts.length} {t['alerts.alert_count']}
                {searchQuery && ` (${t['alerts.search_prefix']}: "${searchQuery}")`}
              </span>
            </div>
            {selectedAlerts.size > 0 && (
              <div className="flex items-center space-x-2">
                <span className="text-xs sm:text-sm text-slate-500">{t['alerts.selected_count'].replace('{n}', String(selectedAlerts.size))}</span>
                <HoloButton size="sm" variant="ghost">
                  <CheckCheck className="w-4 h-4 mr-1" />
                  {t['alerts.mark_as_read']}
                </HoloButton>
              </div>
            )}
          </div>

          {/* Alert list */}
          <div className="divide-y divide-slate-300/60">
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

          {/* Empty state */}
          {paginatedAlerts.length === 0 && (
            <div className="px-4 sm:px-6 py-12 sm:py-16 text-center">
              <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Bell className="w-8 h-8 text-slate-300" />
              </div>
              <h3 className="text-lg font-medium text-slate-800">
                {searchQuery ? t['alerts.no_search_results'] : t['alerts.no_alerts']}
              </h3>
              <p className="text-slate-500 mt-1">
                {searchQuery ? t['alerts.try_other_keywords'] : t['alerts.empty_hint']}
              </p>
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="px-3 sm:px-6 py-3 sm:py-4 border-t border-slate-100 flex items-center justify-between bg-slate-50/50">
              <span className="text-sm text-slate-500">
                {t['alerts.page_info'].replace('{current}', String(currentPage)).replace('{total}', String(totalPages)).replace('{count}', String(filteredAlerts.length))}
              </span>
              <div className="flex items-center space-x-2">
                <HoloButton
                  variant="secondary"
                  size="sm"
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage <= 1}
                  icon={<ChevronLeft className="w-4 h-4" />}
                >
                  {t['alerts.prev_page']}
                </HoloButton>
                <HoloButton
                  variant="secondary"
                  size="sm"
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage >= totalPages}
                  icon={<ChevronRight className="w-4 h-4" />}
                >
                  {t['alerts.next_page']}
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
// Sub-components
// =============================================

// Clickable metric card wrapper
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
  const { t } = useLocale()
  const isRead = alert.is_read

  const typeConfig = useMemo(() => ({
    price_drop: {
      icon: TrendingDown,
      color: "text-green-600",
      bg: "bg-green-100",
      label: t['alerts.price_drop'],
      badgeVariant: "success" as const
    },
    price_increase: {
      icon: TrendingUp,
      color: "text-red-600",
      bg: "bg-red-100",
      label: t['alerts.price_increase'],
      badgeVariant: "error" as const
    },
    out_of_stock: {
      icon: AlertTriangle,
      color: "text-orange-600",
      bg: "bg-orange-100",
      label: t['alerts.out_of_stock'],
      badgeVariant: "warning" as const
    },
    back_in_stock: {
      icon: Check,
      color: "text-blue-600",
      bg: "bg-blue-100",
      label: t['alerts.back_in_stock'],
      badgeVariant: "info" as const
    },
  }), [t])

  const config = typeConfig[alert.alert_type as keyof typeof typeConfig] || {
    icon: Bell,
    color: "text-slate-600",
    bg: "bg-slate-100",
    label: t['alerts.notification'],
    badgeVariant: "default" as const
  }

  const Icon = config.icon

  return (
    <div className={cn(
      "px-3 py-3 sm:px-6 sm:py-4 transition-all hover:bg-slate-50/80 group",
      !isRead && "bg-blue-50/30",
      isSelected && "bg-blue-100/50"
    )}>
      {/* Desktop layout */}
      <div className="hidden sm:flex items-center gap-4">
        {/* Checkbox */}
        <button onClick={onSelect} className="flex-shrink-0">
          <div className={cn(
            "w-5 h-5 border-2 rounded flex items-center justify-center transition-colors",
            isSelected ? "bg-blue-500 border-blue-500" : "border-slate-300 hover:border-slate-400"
          )}>
            {isSelected && <Check className="w-3 h-3 text-white" />}
          </div>
        </button>

        {/* Icon */}
        <div className={cn("p-2.5 rounded-xl flex-shrink-0", config.bg)}>
          <Icon className={cn("w-5 h-5", config.color)} />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <HoloBadge variant={config.badgeVariant} size="sm">
              {config.label}
            </HoloBadge>
            {!isRead && (
              <span className="flex items-center text-xs text-blue-600 font-medium">
                <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-1 animate-pulse" />
                {t['alerts.unread']}
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

        {/* Price change */}
        <div className="flex-shrink-0 text-right min-w-[120px]">
          <div className="flex items-center justify-end space-x-2 font-mono">
            <span className="text-slate-400 line-through text-sm">{alert.old_value}</span>
            <span className="text-slate-800 font-bold">{alert.new_value}</span>
          </div>
          {alert.change_percent && (
            <span className={cn(
              "text-sm font-bold",
              Number(alert.change_percent) > 0 ? "text-red-600" : "text-green-600"
            )}>
              {Number(alert.change_percent) > 0 ? '+' : ''}{Number(alert.change_percent).toFixed(1)}%
            </span>
          )}
        </div>

        {/* Action buttons */}
        <div className="flex-shrink-0 flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
          {!isRead && (
            <HoloButton
              size="sm"
              variant="ghost"
              onClick={onMarkRead}
              icon={<CheckCheck className="w-4 h-4" />}
            >
              {t['alerts.read']}
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
                {t['alerts.view_details']}
              </DropdownMenuItem>
              <DropdownMenuItem>
                <ExternalLink className="w-4 h-4 mr-2" />
                {t['alerts.go_to_product']}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-slate-500">
                <Archive className="w-4 h-4 mr-2" />
                {t['alerts.archive']}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* Mobile layout */}
      <div className="flex sm:hidden gap-3">
        {/* Checkbox */}
        <button onClick={onSelect} className="flex-shrink-0 pt-0.5">
          <div className={cn(
            "w-5 h-5 border-2 rounded flex items-center justify-center transition-colors",
            isSelected ? "bg-blue-500 border-blue-500" : "border-slate-300 hover:border-slate-400"
          )}>
            {isSelected && <Check className="w-3 h-3 text-white" />}
          </div>
        </button>

        {/* Icon */}
        <div className={cn("p-2 rounded-lg flex-shrink-0", config.bg)}>
          <Icon className={cn("w-4 h-4", config.color)} />
        </div>

        {/* Content — vertical layout */}
        <div className="flex-1 min-w-0">
          {/* Row 1: Badge + unread */}
          <div className="flex items-center gap-2 mb-1">
            <HoloBadge variant={config.badgeVariant} size="sm">
              {config.label}
            </HoloBadge>
            {!isRead && (
              <span className="flex items-center text-xs text-blue-600 font-medium">
                <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-1 animate-pulse" />
                {t['alerts.unread']}
              </span>
            )}
          </div>

          {/* Row 2: Product name */}
          <h3 className="font-semibold text-slate-800 text-sm leading-snug mb-1 line-clamp-2">
            {alert.product_name}
          </h3>

          {/* Row 3: Merchant name */}
          <div className="flex items-center text-xs text-slate-500 mb-1.5">
            <Building2 className="w-3 h-3 mr-1 flex-shrink-0" />
            <span className="truncate">{alert.competitor_name}</span>
          </div>

          {/* Row 4: Price + time */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-mono text-sm">
              {(alert.old_value != null && alert.new_value != null) ? (
                <>
                  <span className="text-slate-400 line-through text-xs">{alert.old_value}</span>
                  <span className="text-slate-800 font-bold">{alert.new_value}</span>
                  {alert.change_percent && (
                    <span className={cn(
                      "text-xs font-bold",
                      Number(alert.change_percent) > 0 ? "text-red-600" : "text-green-600"
                    )}>
                      {Number(alert.change_percent) > 0 ? '+' : ''}{Number(alert.change_percent).toFixed(1)}%
                    </span>
                  )}
                </>
              ) : (
                <span className="text-slate-800 font-bold text-xs">{alert.new_value ?? '—'}</span>
              )}
            </div>
            <span className="flex items-center text-xs text-slate-400 flex-shrink-0 ml-2">
              <Clock className="w-3 h-3 mr-1" />
              {new Date(alert.created_at).toLocaleDateString('zh-HK', { month: 'numeric', day: 'numeric' })}
              {' '}
              {new Date(alert.created_at).toLocaleTimeString('zh-HK', { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        </div>

        {/* Mobile Action buttons */}
        <div className="flex-shrink-0">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button size="sm" variant="ghost" className="h-7 w-7 p-0">
                <MoreHorizontal className="w-4 h-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {!isRead && (
                <>
                  <DropdownMenuItem onClick={onMarkRead}>
                    <CheckCheck className="w-4 h-4 mr-2" />
                    {t['alerts.mark_as_read']}
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                </>
              )}
              <DropdownMenuItem>
                <Eye className="w-4 h-4 mr-2" />
                {t['alerts.view_details']}
              </DropdownMenuItem>
              <DropdownMenuItem>
                <ExternalLink className="w-4 h-4 mr-2" />
                {t['alerts.go_to_product']}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="text-slate-500">
                <Archive className="w-4 h-4 mr-2" />
                {t['alerts.archive']}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </div>
  )
}
