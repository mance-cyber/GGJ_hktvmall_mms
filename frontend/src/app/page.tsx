'use client'

// =============================================
// 首頁 - Future Tech Design
// =============================================

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, PriceAlert } from '@/lib/api'
import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  FolderOpen,
  Package,
  TrendingDown,
  TrendingUp,
  RefreshCw,
  Bell,
  AlertTriangle,
  Eye,
  Building2,
  Zap,
  ArrowRight,
  ChevronRight,
  Activity,
  Sparkles,
  Calendar,
  CheckCircle2,
  XCircle,
  Plus,
  BarChart3,
  Cpu,
  Database,
  Wifi,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import {
  HoloCard,
  DataMetric,
  PulseStatus,
  DataStreamBg,
  HoloButton,
  HoloBadge,
  TechDivider,
  PageTransition,
  StaggerContainer,
  HoloPanelHeader,
  ProgressRing,
  HoloSkeleton,
} from '@/components/ui/future-tech'

// =============================================
// 主頁面
// =============================================

export default function DashboardPage() {
  const queryClient = useQueryClient()

  const { data: categories, isLoading: categoriesLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: () => api.getCategories(1, 100),
  })

  const { data: competitors } = useQuery({
    queryKey: ['competitors'],
    queryFn: () => api.getCompetitors(),
  })

  const { data: alerts, refetch: refetchAlerts } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => api.getAlerts(undefined, undefined, 20),
    refetchInterval: 30000,
  })

  const { data: products } = useQuery({
    queryKey: ['own-products'],
    queryFn: () => api.getProducts(1, 100),
  })

  const markReadMutation = useMutation({
    mutationFn: (alertId: string) => api.markAlertRead(alertId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })

  // 計算統計數據
  const totalProducts = categories?.items.reduce((sum, cat) => sum + cat.total_products, 0) || 0
  const activeCategories = categories?.items.filter(cat => cat.is_active).length || 0
  const activeCompetitors = competitors?.data.filter(c => c.is_active).length || 0
  const competitorProducts = competitors?.data.reduce((sum, c) => sum + c.product_count, 0) || 0

  // 今日數據
  const todayAlerts = alerts?.data.filter(a => {
    const alertDate = new Date(a.created_at)
    const today = new Date()
    return alertDate.toDateString() === today.toDateString()
  }) || []

  const priceDrops = todayAlerts.filter(a => a.alert_type === 'price_drop').length
  const priceIncreases = todayAlerts.filter(a => a.alert_type === 'price_increase').length

  // Loading 狀態
  if (categoriesLoading) {
    return (
      <div className="relative min-h-[60vh]">
        <DataStreamBg density="low" color="cyan" className="opacity-20" />
        <div className="relative z-10 flex flex-col items-center justify-center h-[60vh] gap-4">
          <div className="relative">
            <div className="absolute inset-0 bg-cyan-500/20 blur-2xl rounded-full animate-pulse" />
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            >
              <Cpu className="relative w-12 h-12 text-cyan-500" />
            </motion.div>
          </div>
          <p className="text-sm text-slate-500">正在載入數據...</p>
        </div>
      </div>
    )
  }

  return (
    <PageTransition>
      <div className="relative min-h-screen">
        {/* 背景數據流 */}
        <DataStreamBg density="low" color="cyan" className="opacity-20" />

        <div className="relative z-10 space-y-6 sm:space-y-8">
          {/* ========== 頁面標題 ========== */}
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
            <div>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center gap-3 mb-3"
              >
                <h1 className="text-2xl sm:text-4xl font-bold text-slate-800">
                  控制台
                </h1>
                <PulseStatus status="online" size="md" />
              </motion.div>
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="text-sm sm:text-base text-slate-500 flex items-center gap-2"
              >
                <Calendar className="w-4 h-4 text-cyan-500" />
                {new Date().toLocaleDateString('zh-HK', { weekday: 'long', month: 'long', day: 'numeric' })}
              </motion.p>
            </div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-2 sm:gap-3"
            >
              <HoloButton
                variant="secondary"
                size="md"
                onClick={() => refetchAlerts()}
                icon={<RefreshCw className="w-4 h-4" />}
              >
                <span className="hidden sm:inline">刷新</span>
              </HoloButton>
              <Link href="/competitors">
                <HoloButton variant="primary" icon={<Zap className="w-4 h-4" />}>
                  <span className="hidden sm:inline">開始抓取</span>
                  <span className="sm:hidden">抓取</span>
                </HoloButton>
              </Link>
            </motion.div>
          </div>

          {/* ========== 系統狀態 ========== */}
          <HoloCard glowColor="cyan" className="p-4 sm:p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-50 to-blue-50 flex items-center justify-center">
                  <Activity className="w-5 h-5 text-cyan-600" />
                </div>
                <div>
                  <h2 className="font-semibold text-slate-800">系統狀態</h2>
                  <p className="text-sm text-slate-500">實時監控各服務運行狀況</p>
                </div>
              </div>
              <HoloBadge variant="info">
                <RefreshCw className="w-3 h-3" />
                實時更新
              </HoloBadge>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <SystemStatus icon={Wifi} label="API 服務" status="online" />
              <SystemStatus icon={Database} label="數據庫" status="online" />
              <SystemStatus icon={Cpu} label="AI 引擎" status="processing" />
              <SystemStatus icon={Bell} label="通知服務" status="online" />
            </div>
          </HoloCard>

          {/* ========== 今日摘要 ========== */}
          <HoloCard glowColor="blue" className="p-4 sm:p-6">
            <HoloPanelHeader
              title="今日摘要"
              subtitle={`${new Date().toLocaleDateString('zh-HK')}`}
              icon={<Sparkles className="w-5 h-5" />}
            />
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
              <TodayStat
                icon={Bell}
                label="新警報"
                value={todayAlerts.length}
                color="cyan"
                highlight={todayAlerts.length > 0}
              />
              <TodayStat
                icon={TrendingDown}
                label="價格下跌"
                value={priceDrops}
                color="green"
                highlight={priceDrops > 0}
              />
              <TodayStat
                icon={TrendingUp}
                label="價格上漲"
                value={priceIncreases}
                color="orange"
                highlight={priceIncreases > 0}
              />
              <TodayStat
                icon={Eye}
                label="未讀通知"
                value={alerts?.unread_count || 0}
                color="purple"
                highlight={(alerts?.unread_count || 0) > 0}
              />
            </div>
          </HoloCard>

          {/* ========== 待處理事項 ========== */}
          {(alerts?.unread_count || 0) > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <HoloCard glowColor="purple" className="overflow-hidden border-amber-200/50">
                <div className="px-4 sm:px-6 py-3 sm:py-4 bg-gradient-to-r from-amber-50 to-orange-50 border-b border-amber-100 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-amber-500" />
                    <h2 className="font-semibold text-slate-800">待處理事項</h2>
                    <HoloBadge variant="warning">{alerts?.unread_count}</HoloBadge>
                  </div>
                  <Link href="/alerts">
                    <HoloButton variant="ghost" size="sm">
                      查看全部
                      <ChevronRight className="w-4 h-4 ml-1" />
                    </HoloButton>
                  </Link>
                </div>
                <div className="divide-y divide-slate-100">
                  {alerts?.data.filter(a => !a.is_read).slice(0, 3).map((alert) => (
                    <ActionableAlertRow
                      key={alert.id}
                      alert={alert}
                      onMarkRead={() => markReadMutation.mutate(alert.id)}
                    />
                  ))}
                </div>
              </HoloCard>
            </motion.div>
          )}

          <TechDivider label="核心指標" />

          {/* ========== 關鍵指標 ========== */}
          <StaggerContainer className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            <DataMetric
              label="監測類別"
              value={categories?.total || 0}
              color="cyan"
              icon={<FolderOpen className="w-5 h-5 text-cyan-500" />}
            />
            <DataMetric
              label="追踪商品"
              value={totalProducts}
              color="blue"
              icon={<Package className="w-5 h-5 text-blue-500" />}
            />
            <DataMetric
              label="競爭對手"
              value={competitors?.total || 0}
              color="purple"
              icon={<Building2 className="w-5 h-5 text-violet-500" />}
            />
            <DataMetric
              label="自家商品"
              value={products?.total || 0}
              color="green"
              icon={<Sparkles className="w-5 h-5 text-emerald-500" />}
            />
          </StaggerContainer>

          {/* ========== 主內容區域 ========== */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* 左側：快速操作 + 競爭對手 */}
            <div className="lg:col-span-2 space-y-6">
              {/* 快速操作 */}
              <HoloCard glowColor="cyan" className="p-4 sm:p-6">
                <HoloPanelHeader
                  title="快速操作"
                  subtitle="常用功能入口"
                  icon={<Zap className="w-5 h-5" />}
                />
                <div className="grid grid-cols-4 gap-2 sm:gap-3 mt-4">
                  <QuickAction
                    icon={Plus}
                    label="新增競品"
                    href="/competitors"
                    color="cyan"
                  />
                  <QuickAction
                    icon={Zap}
                    label="全網抓取"
                    href="/competitors"
                    color="blue"
                  />
                  <QuickAction
                    icon={Sparkles}
                    label="AI 內容"
                    href="/ai-content"
                    color="purple"
                  />
                  <QuickAction
                    icon={BarChart3}
                    label="數據分析"
                    href="/ai-analysis"
                    color="green"
                  />
                </div>
              </HoloCard>

              {/* 競爭對手概覽 */}
              <HoloCard glowColor="blue" scanLine className="overflow-hidden">
                <HoloPanelHeader
                  title="競爭對手監測"
                  subtitle={`${activeCompetitors} 個活躍監測`}
                  icon={<Building2 className="w-5 h-5" />}
                  action={
                    <Link href="/competitors">
                      <HoloButton variant="ghost" size="sm">
                        管理
                        <ChevronRight className="w-4 h-4 ml-1" />
                      </HoloButton>
                    </Link>
                  }
                />
                <div className="divide-y divide-slate-100">
                  {competitors?.data.slice(0, 4).map((comp) => (
                    <CompetitorRow key={comp.id} competitor={comp} />
                  ))}
                  {(!competitors?.data || competitors.data.length === 0) && (
                    <div className="px-6 py-12 text-center">
                      <Building2 className="w-12 h-12 mx-auto text-slate-300 mb-3" />
                      <p className="text-slate-500 mb-3">尚未添加競爭對手</p>
                      <Link href="/competitors">
                        <HoloButton variant="primary" size="sm" icon={<Plus className="w-4 h-4" />}>
                          立即添加
                        </HoloButton>
                      </Link>
                    </div>
                  )}
                </div>
              </HoloCard>
            </div>

            {/* 右側：最近警報 */}
            <div className="space-y-6">
              <HoloCard glowColor="purple" className="overflow-hidden lg:sticky lg:top-6">
                <HoloPanelHeader
                  title="最近警報"
                  subtitle="價格變動通知"
                  icon={<Bell className="w-5 h-5" />}
                  action={
                    alerts?.unread_count ? (
                      <HoloBadge variant="error" pulse>
                        {alerts.unread_count} 未讀
                      </HoloBadge>
                    ) : null
                  }
                />
                <div className="divide-y divide-slate-100 max-h-[500px] overflow-y-auto scrollbar-subtle">
                  {alerts?.data.slice(0, 8).map((alert) => (
                    <AlertRow
                      key={alert.id}
                      alert={alert}
                      onMarkRead={() => markReadMutation.mutate(alert.id)}
                    />
                  ))}
                  {(!alerts?.data || alerts.data.length === 0) && (
                    <div className="px-6 py-12 text-center">
                      <Bell className="w-12 h-12 mx-auto text-slate-300 mb-3" />
                      <p className="text-slate-500">暫無價格警報</p>
                      <p className="text-xs text-slate-400 mt-1">當競品價格變動時會顯示在這裡</p>
                    </div>
                  )}
                </div>
                {alerts?.data && alerts.data.length > 0 && (
                  <div className="px-6 py-3 border-t border-slate-100 bg-slate-50/50">
                    <Link href="/alerts" className="flex items-center justify-center text-cyan-600 hover:text-cyan-700 text-sm font-medium transition-colors">
                      查看全部警報
                      <ArrowRight className="w-4 h-4 ml-1" />
                    </Link>
                  </div>
                )}
              </HoloCard>
            </div>
          </div>
        </div>
      </div>
    </PageTransition>
  )
}

// =============================================
// 子組件
// =============================================

function SystemStatus({
  icon: Icon,
  label,
  status,
}: {
  icon: React.ElementType
  label: string
  status: 'online' | 'offline' | 'warning' | 'processing'
}) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="flex items-center gap-3 p-3 rounded-xl bg-white/60 border border-slate-100 hover:border-cyan-200 transition-all"
    >
      <div className="w-9 h-9 rounded-lg bg-slate-50 flex items-center justify-center">
        <Icon className="w-4 h-4 text-slate-500" />
      </div>
      <div>
        <p className="text-sm font-medium text-slate-700">{label}</p>
        <PulseStatus status={status} size="sm" />
      </div>
    </motion.div>
  )
}

function TodayStat({
  icon: Icon,
  label,
  value,
  color,
  highlight
}: {
  icon: React.ElementType
  label: string
  value: number
  color: 'cyan' | 'green' | 'orange' | 'purple'
  highlight?: boolean
}) {
  const colors = {
    cyan: { bg: 'bg-cyan-50', text: 'text-cyan-600', border: 'border-cyan-200' },
    green: { bg: 'bg-emerald-50', text: 'text-emerald-600', border: 'border-emerald-200' },
    orange: { bg: 'bg-amber-50', text: 'text-amber-600', border: 'border-amber-200' },
    purple: { bg: 'bg-violet-50', text: 'text-violet-600', border: 'border-violet-200' },
  }

  const style = colors[color]

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className={cn(
        "flex items-center gap-3 p-3 rounded-xl transition-all border",
        highlight ? `${style.bg} ${style.border} shadow-sm` : "bg-white/60 border-slate-100"
      )}
    >
      <div className={cn("p-2 rounded-lg", style.bg)}>
        <Icon className={cn("w-5 h-5", style.text)} />
      </div>
      <div>
        <motion.p
          key={value}
          initial={{ scale: 1.2, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="text-2xl font-bold text-slate-800"
        >
          {value}
        </motion.p>
        <p className="text-xs text-slate-500">{label}</p>
      </div>
    </motion.div>
  )
}

function QuickAction({
  icon: Icon,
  label,
  href,
  color
}: {
  icon: React.ElementType
  label: string
  href: string
  color: 'cyan' | 'blue' | 'purple' | 'green'
}) {
  const colors = {
    cyan: 'bg-cyan-50 text-cyan-600 hover:bg-cyan-100 border-cyan-100 hover:border-cyan-200',
    blue: 'bg-blue-50 text-blue-600 hover:bg-blue-100 border-blue-100 hover:border-blue-200',
    purple: 'bg-violet-50 text-violet-600 hover:bg-violet-100 border-violet-100 hover:border-violet-200',
    green: 'bg-emerald-50 text-emerald-600 hover:bg-emerald-100 border-emerald-100 hover:border-emerald-200',
  }

  return (
    <Link href={href}>
      <motion.div
        whileHover={{ scale: 1.05, y: -2 }}
        whileTap={{ scale: 0.95 }}
        className={cn(
          "flex flex-col items-center justify-center p-3 sm:p-4 rounded-xl transition-all cursor-pointer border",
          colors[color]
        )}
      >
        <Icon className="w-5 h-5 sm:w-6 sm:h-6 mb-1.5 sm:mb-2" />
        <span className="text-[10px] sm:text-xs font-medium text-center leading-tight">{label}</span>
      </motion.div>
    </Link>
  )
}

function CompetitorRow({ competitor }: { competitor: any }) {
  return (
    <Link href={`/competitors/${competitor.id}`}>
      <motion.div
        whileHover={{ backgroundColor: 'rgba(6, 182, 212, 0.05)' }}
        className="flex items-center justify-between px-4 sm:px-6 py-3 sm:py-4 transition-colors group"
      >
        <div className="flex items-center gap-3 sm:gap-4 min-w-0 flex-1">
          <div className="w-10 h-10 bg-gradient-to-br from-slate-50 to-slate-100 rounded-xl flex items-center justify-center border border-slate-200">
            <Building2 className="w-5 h-5 text-slate-500" />
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="font-medium text-slate-800 group-hover:text-cyan-600 transition-colors truncate">
              {competitor.name}
            </h3>
            <p className="text-sm text-slate-500">{competitor.platform}</p>
          </div>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-bold text-slate-700">{competitor.product_count}</p>
            <p className="text-xs text-slate-400">商品</p>
          </div>
          <HoloBadge variant={competitor.is_active ? "success" : "default"}>
            {competitor.is_active ? '活躍' : '停用'}
          </HoloBadge>
          <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-cyan-500 transition-colors hidden sm:block" />
        </div>
      </motion.div>
    </Link>
  )
}

function AlertRow({
  alert,
  onMarkRead,
}: {
  alert: PriceAlert
  onMarkRead: () => void
}) {
  const alertTypeConfig: Record<string, { icon: React.ElementType; color: string; bg: string }> = {
    price_drop: { icon: TrendingDown, color: 'text-emerald-600', bg: 'bg-emerald-50' },
    price_increase: { icon: TrendingUp, color: 'text-red-500', bg: 'bg-red-50' },
    out_of_stock: { icon: AlertTriangle, color: 'text-amber-600', bg: 'bg-amber-50' },
    back_in_stock: { icon: CheckCircle2, color: 'text-blue-600', bg: 'bg-blue-50' },
  }

  const config = alertTypeConfig[alert.alert_type] || {
    icon: Bell,
    color: 'text-slate-600',
    bg: 'bg-slate-50'
  }
  const Icon = config.icon

  return (
    <motion.div
      whileHover={{ backgroundColor: 'rgba(6, 182, 212, 0.03)' }}
      className={cn(
        "px-4 sm:px-6 py-3 transition-colors",
        !alert.is_read && "bg-cyan-50/30"
      )}
    >
      <div className="flex items-start gap-3">
        <div className={cn("p-1.5 rounded-lg mt-0.5", config.bg)}>
          <Icon className={cn("w-4 h-4", config.color)} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-slate-800 truncate">{alert.product_name}</p>
          <p className="text-xs text-slate-500 truncate">{alert.competitor_name}</p>
          <div className="flex items-center mt-1 text-xs">
            {alert.change_percent && (
              <span className={cn(
                "font-bold",
                alert.change_percent > 0 ? 'text-red-500' : 'text-emerald-600'
              )}>
                {alert.change_percent > 0 ? '+' : ''}{alert.change_percent.toFixed(1)}%
              </span>
            )}
            <span className="mx-2 text-slate-300">·</span>
            <span className="text-slate-400">
              {new Date(alert.created_at).toLocaleTimeString('zh-HK', { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        </div>
        {!alert.is_read && (
          <button
            onClick={(e) => { e.preventDefault(); onMarkRead(); }}
            className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors"
            title="標記已讀"
          >
            <Eye className="w-4 h-4 text-slate-400 hover:text-cyan-500" />
          </button>
        )}
      </div>
    </motion.div>
  )
}

function ActionableAlertRow({
  alert,
  onMarkRead,
}: {
  alert: PriceAlert
  onMarkRead: () => void
}) {
  const alertTypeConfig: Record<string, { icon: React.ElementType; color: string; action: string }> = {
    price_drop: { icon: TrendingDown, color: 'text-emerald-600', action: '查看降價詳情' },
    price_increase: { icon: TrendingUp, color: 'text-red-500', action: '分析漲價原因' },
    out_of_stock: { icon: XCircle, color: 'text-amber-600', action: '查看缺貨商品' },
    back_in_stock: { icon: CheckCircle2, color: 'text-blue-600', action: '查看補貨商品' },
  }

  const config = alertTypeConfig[alert.alert_type] || {
    icon: Bell,
    color: 'text-slate-600',
    action: '查看詳情'
  }
  const Icon = config.icon

  return (
    <motion.div
      whileHover={{ backgroundColor: 'rgba(251, 191, 36, 0.1)' }}
      className="px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between transition-colors"
    >
      <div className="flex items-center gap-3 sm:gap-4 min-w-0 flex-1">
        <div className={cn("p-2 rounded-lg bg-white shadow-sm border border-slate-100", config.color)}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="font-medium text-slate-800 truncate">{alert.product_name}</p>
          <p className="text-sm text-slate-500 truncate">{alert.competitor_name}</p>
        </div>
      </div>
      <HoloButton
        variant="secondary"
        size="sm"
        onClick={onMarkRead}
      >
        <span className="hidden sm:inline">{config.action}</span>
        <span className="sm:hidden">查看</span>
        <ArrowRight className="w-4 h-4 ml-1" />
      </HoloButton>
    </motion.div>
  )
}
