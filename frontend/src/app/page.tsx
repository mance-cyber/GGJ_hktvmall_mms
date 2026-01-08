'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, pricingApi } from '@/lib/api'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import {
  FolderOpen,
  Package,
  TrendingDown,
  TrendingUp,
  RefreshCw,
  ExternalLink,
  AlertCircle,
  Bell,
  Check,
  AlertTriangle,
  Eye,
  Building2,
  Zap,
  Clock,
  ArrowRight,
  ChevronRight,
  Activity,
  Target,
  Sparkles,
  Calendar,
  CheckCircle2,
  XCircle,
  Plus,
  BarChart3,
  DollarSign
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { PricingProposalList } from '@/components/pricing/proposal-card'

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
    refetchInterval: 30000, // 每30秒自動刷新
  })

  const { data: products } = useQuery({
    queryKey: ['own-products'],
    queryFn: () => api.getProducts(1, 100),
  })

  const { data: pendingProposals, refetch: refetchProposals } = useQuery({
    queryKey: ['pending-proposals'],
    queryFn: () => pricingApi.getPendingProposals(),
    // refetchInterval: 10000
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
  
  // 今日數據（模擬）
  const todayAlerts = alerts?.data.filter(a => {
    const alertDate = new Date(a.created_at)
    const today = new Date()
    return alertDate.toDateString() === today.toDateString()
  }) || []
  
  const priceDrops = todayAlerts.filter(a => a.alert_type === 'price_drop').length
  const priceIncreases = todayAlerts.filter(a => a.alert_type === 'price_increase').length

  if (categoriesLoading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="relative">
          <div className="absolute inset-0 bg-blue-500/20 blur-xl rounded-full animate-pulse" />
          <RefreshCw className="relative w-12 h-12 animate-spin text-primary" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in-up">
      {/* ========== 頁面標題 + 今日摘要 ========== */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            歡迎回來 👋
          </h1>
          <p className="text-muted-foreground mt-2 text-lg">
            {new Date().toLocaleDateString('zh-HK', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline" onClick={() => { refetchAlerts(); refetchProposals(); }} className="glass-card">
            <RefreshCw className="w-4 h-4 mr-2" />
            刷新數據
          </Button>
          <Link href="/competitors">
            <Button className="bg-primary hover:bg-primary/90 shadow-lg shadow-blue-500/20">
              <Zap className="w-4 h-4 mr-2" />
              開始抓取
            </Button>
          </Link>
        </div>
      </div>

      {/* ========== 今日摘要卡片 ========== */}
      <div className="glass-panel rounded-2xl p-6 border border-white/40 bg-gradient-to-r from-blue-50/50 to-purple-50/50">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-slate-800 flex items-center">
            <Calendar className="w-5 h-5 mr-2 text-blue-500" />
            今日摘要
          </h2>
          <Badge variant="outline" className="text-blue-600 border-blue-200 bg-blue-50">
            <Activity className="w-3 h-3 mr-1" />
            實時更新
          </Badge>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <TodayStat 
            icon={Bell} 
            label="新警報" 
            value={todayAlerts.length}
            color="blue"
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
            color="red"
            highlight={priceIncreases > 0}
          />
          <TodayStat 
            icon={Eye} 
            label="未讀通知" 
            value={alerts?.unread_count || 0}
            color="orange"
            highlight={(alerts?.unread_count || 0) > 0}
          />
        </div>
      </div>

      {/* ========== 待處理事項 ========== */}
      {(alerts?.unread_count || 0) > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-panel rounded-2xl overflow-hidden border-2 border-orange-200 bg-orange-50/30"
        >
          <div className="px-6 py-4 bg-orange-100/50 border-b border-orange-200 flex items-center justify-between">
            <h2 className="font-bold text-orange-800 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2" />
              待處理警報
              <Badge className="ml-2 bg-orange-500">{alerts?.unread_count}</Badge>
            </h2>
            <Link href="/alerts">
              <Button variant="ghost" size="sm" className="text-orange-700 hover:text-orange-800">
                查看全部
                <ChevronRight className="w-4 h-4 ml-1" />
              </Button>
            </Link>
          </div>
          <div className="divide-y divide-orange-100">
            {alerts?.data.filter(a => !a.is_read).slice(0, 3).map((alert) => (
              <ActionableAlertRow
                key={alert.id}
                alert={alert}
                onMarkRead={() => markReadMutation.mutate(alert.id)}
              />
            ))}
          </div>
        </motion.div>
      )}

      {/* ========== 關鍵指標 ========== */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="監測類別"
          value={categories?.total || 0}
          subtitle={`${activeCategories} 個活躍`}
          icon={FolderOpen}
          color="blue"
          href="/categories"
        />
        <MetricCard
          title="追踪商品"
          value={totalProducts}
          subtitle="HKTVmall 商品"
          icon={Package}
          color="green"
          href="/categories"
        />
        <MetricCard
          title="競爭對手"
          value={competitors?.total || 0}
          subtitle={`${competitorProducts} 個監測商品`}
          icon={Building2}
          color="purple"
          href="/competitors"
        />
        <MetricCard
          title="自家商品"
          value={products?.total || 0}
          subtitle="已錄入系統"
          icon={Sparkles}
          color="pink"
          href="/products"
        />
      </div>

      {/* ========== 主內容區域 ========== */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左側：快速操作 + 最近活動 */}
        <div className="lg:col-span-2 space-y-6">
        
          {/* AI 智能改價待辦 */}
          {pendingProposals && pendingProposals.length > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="glass-panel rounded-2xl p-6 border-2 border-primary/20 bg-primary/5"
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-slate-800 flex items-center">
                  <DollarSign className="w-5 h-5 mr-2 text-primary" />
                  AI 智能定價建議
                  <Badge className="ml-2 bg-primary">{pendingProposals.length}</Badge>
                </h2>
                <Badge variant="outline" className="bg-white border-primary/20 text-primary">
                  需要審批
                </Badge>
              </div>
              <PricingProposalList 
                proposals={pendingProposals} 
                onUpdate={refetchProposals} 
              />
            </motion.div>
          )}
        
          {/* 快速操作 */}
          <div className="glass-panel rounded-2xl p-6 border border-white/40">
            <h2 className="text-lg font-bold text-slate-800 mb-4 flex items-center">
              <Zap className="w-5 h-5 mr-2 text-yellow-500" />
              快速操作
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <QuickAction 
                icon={Plus} 
                label="新增競品" 
                href="/competitors"
                color="blue"
              />
              <QuickAction 
                icon={Zap} 
                label="全網抓取" 
                href="/competitors"
                color="green"
              />
              <QuickAction 
                icon={Sparkles} 
                label="AI 內容" 
                href="/ai-content"
                color="purple"
              />
              <QuickAction 
                icon={BarChart3} 
                label="價格趨勢" 
                href="/trends"
                color="orange"
              />
            </div>
          </div>

          {/* 競爭對手概覽 */}
          <div className="glass-panel rounded-2xl overflow-hidden border border-white/40">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-800 flex items-center">
                <Building2 className="w-5 h-5 mr-2 text-blue-500" />
                競爭對手監測
              </h2>
              <Link href="/competitors">
                <Button variant="ghost" size="sm" className="text-blue-600">
                  管理全部
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </Link>
            </div>
            <div className="divide-y divide-slate-100">
              {competitors?.data.slice(0, 4).map((comp) => (
                <CompetitorRow key={comp.id} competitor={comp} />
              ))}
              {(!competitors?.data || competitors.data.length === 0) && (
                <div className="px-6 py-12 text-center">
                  <Building2 className="w-12 h-12 mx-auto text-slate-300 mb-3" />
                  <p className="text-slate-500">尚未添加競爭對手</p>
                  <Link href="/competitors">
                    <Button size="sm" className="mt-3">
                      <Plus className="w-4 h-4 mr-2" />
                      立即添加
                    </Button>
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 右側：最近警報 */}
        <div className="space-y-6">
          <div className="glass-panel rounded-2xl overflow-hidden border border-white/40 sticky top-6">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-gradient-to-r from-red-50 to-orange-50">
              <h2 className="text-lg font-bold text-slate-800 flex items-center">
                <Bell className="w-5 h-5 mr-2 text-red-500" />
                最近警報
              </h2>
              {alerts?.unread_count ? (
                <Badge variant="destructive" className="animate-pulse">
                  {alerts.unread_count} 未讀
                </Badge>
              ) : null}
            </div>
            <div className="divide-y divide-slate-100 max-h-[500px] overflow-y-auto">
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
                <Link href="/alerts" className="flex items-center justify-center text-blue-600 hover:text-blue-700 text-sm font-medium">
                  查看全部警報
                  <ArrowRight className="w-4 h-4 ml-1" />
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// =============================================
// 子組件
// =============================================

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
  color: 'blue' | 'green' | 'red' | 'orange'
  highlight?: boolean
}) {
  const colors = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    red: 'bg-red-100 text-red-600',
    orange: 'bg-orange-100 text-orange-600'
  }

  return (
    <div className={cn(
      "flex items-center space-x-3 p-3 rounded-xl transition-all",
      highlight ? "bg-white/80 shadow-md" : "bg-white/40"
    )}>
      <div className={cn("p-2 rounded-lg", colors[color])}>
        <Icon className="w-5 h-5" />
      </div>
      <div>
        <p className="text-2xl font-bold text-slate-800">{value}</p>
        <p className="text-xs text-slate-500">{label}</p>
      </div>
    </div>
  )
}

function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  color,
  href
}: {
  title: string
  value: string | number
  subtitle: string
  icon: React.ElementType
  color: 'blue' | 'green' | 'purple' | 'pink'
  href: string
}) {
  const colors = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    purple: 'from-purple-500 to-purple-600',
    pink: 'from-pink-500 to-pink-600'
  }

  return (
    <Link href={href}>
      <motion.div 
        whileHover={{ scale: 1.02, y: -2 }}
        className="glass-panel rounded-2xl p-6 border border-white/40 cursor-pointer group"
      >
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-slate-500">{title}</p>
            <p className="text-3xl font-bold text-slate-800 mt-2">{value}</p>
            <p className="text-sm text-slate-400 mt-1">{subtitle}</p>
          </div>
          <div className={cn(
            "p-3 rounded-xl bg-gradient-to-br shadow-lg",
            colors[color]
          )}>
            <Icon className="w-6 h-6 text-white" />
          </div>
        </div>
        <div className="mt-4 flex items-center text-sm text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity">
          查看詳情
          <ChevronRight className="w-4 h-4 ml-1" />
        </div>
      </motion.div>
    </Link>
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
  color: 'blue' | 'green' | 'purple' | 'orange'
}) {
  const colors = {
    blue: 'bg-blue-50 text-blue-600 hover:bg-blue-100',
    green: 'bg-green-50 text-green-600 hover:bg-green-100',
    purple: 'bg-purple-50 text-purple-600 hover:bg-purple-100',
    orange: 'bg-orange-50 text-orange-600 hover:bg-orange-100'
  }

  return (
    <Link href={href} className="block">
      <div className={cn(
        "flex flex-col items-center justify-center p-4 rounded-xl transition-colors text-center h-full",
        colors[color]
      )}>
        <Icon className="w-6 h-6 mb-2" />
        <span className="text-sm font-medium">{label}</span>
      </div>
    </Link>
  )
}

function AlertRow({ alert, onMarkRead }: { alert: any, onMarkRead: () => void }) {
  const isDrop = alert.alert_type === 'price_drop'
  
  return (
    <div className={cn(
      "px-6 py-3 flex items-start gap-3 hover:bg-slate-50 transition-colors cursor-pointer",
      !alert.is_read && "bg-blue-50/30"
    )} onClick={onMarkRead}>
      <div className={cn(
        "p-1.5 rounded-full mt-1 flex-shrink-0",
        isDrop ? "bg-green-100 text-green-600" : "bg-red-100 text-red-600"
      )}>
        {isDrop ? <TrendingDown className="w-3 h-3" /> : <TrendingUp className="w-3 h-3" />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex justify-between items-start">
          <p className="text-sm font-medium text-slate-800 line-clamp-1">{alert.product_name}</p>
          <span className="text-xs text-slate-400 whitespace-nowrap ml-2">
            {new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="text-xs text-slate-500">{alert.competitor_name}</span>
          <span className={cn(
            "text-xs font-bold px-1.5 py-0.5 rounded",
            isDrop ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
          )}>
            {isDrop ? '-' : '+'}{Math.abs(alert.change_percent).toFixed(1)}%
          </span>
          <span className="text-xs font-mono text-slate-600">
            ${alert.old_price} → ${alert.new_price}
          </span>
        </div>
      </div>
      {!alert.is_read && (
        <div className="w-2 h-2 rounded-full bg-blue-500 mt-2 flex-shrink-0" />
      )}
    </div>
  )
}

function ActionableAlertRow({ alert, onMarkRead }: { alert: any, onMarkRead: () => void }) {
  return (
    <div className="px-6 py-3 flex items-center justify-between hover:bg-orange-50/50 transition-colors">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-orange-100 rounded-lg text-orange-600">
          <AlertCircle className="w-4 h-4" />
        </div>
        <div>
          <p className="text-sm font-medium text-slate-800">{alert.product_name}</p>
          <p className="text-xs text-slate-500">
            {alert.competitor_name}: <span className="text-red-600 font-bold">${alert.new_price}</span>
            <span className="mx-1 text-slate-300">|</span>
            跌幅 {Math.abs(alert.change_percent).toFixed(1)}%
          </p>
        </div>
      </div>
      <Button size="sm" variant="outline" className="text-xs h-8 border-orange-200 text-orange-700 hover:bg-orange-100" onClick={onMarkRead}>
        <Check className="w-3 h-3 mr-1" />
        已閱
      </Button>
    </div>
  )
}

function CompetitorRow({ competitor }: { competitor: any }) {
  return (
    <div className="px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors group">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-slate-100 flex items-center justify-center text-slate-500 font-bold text-lg">
          {competitor.name.substring(0, 1)}
        </div>
        <div>
          <h3 className="text-sm font-medium text-slate-800">{competitor.name}</h3>
          <p className="text-xs text-slate-500">{competitor.product_count} 個監測商品</p>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="text-right">
          <p className="text-xs text-slate-400">最近更新</p>
          <p className="text-xs font-medium text-slate-600">
            {competitor.last_scraped_at ? new Date(competitor.last_scraped_at).toLocaleDateString() : '從未'}
          </p>
        </div>
        <ExternalLink className="w-4 h-4 text-slate-300 group-hover:text-blue-500 transition-colors cursor-pointer" />
      </div>
    </div>
  )
}
