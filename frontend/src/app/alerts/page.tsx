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

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="relative">
          <div className="absolute inset-0 bg-red-500/20 blur-xl rounded-full animate-pulse" />
          <Bell className="relative w-12 h-12 animate-bounce text-red-500" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in-up">
      {/* ========== 頁面標題 ========== */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
            警報中心
            {stats.unread > 0 && (
              <Badge variant="destructive" className="animate-pulse text-base px-3">
                {stats.unread} 未讀
              </Badge>
            )}
          </h1>
          <p className="text-muted-foreground mt-2 text-lg">
            即時監控市場價格波動，把握每一個競爭優勢
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Button variant="outline" onClick={() => refetch()} className="glass-card">
            <RefreshCw className="w-4 h-4 mr-2" />
            刷新
          </Button>
          {stats.unread > 0 && (
            <Button 
              onClick={handleMarkAllRead}
              className="bg-slate-900 text-white hover:bg-slate-800"
            >
              <CheckCheck className="w-4 h-4 mr-2" />
              全部標為已讀
            </Button>
          )}
        </div>
      </div>

      {/* ========== 統計卡片 ========== */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard 
          label="總警報數" 
          value={stats.total} 
          icon={Bell}
          active={filterType === 'all'}
          onClick={() => setFilterType('all')}
        />
        <StatCard 
          label="未讀警報" 
          value={stats.unread} 
          icon={Inbox}
          color="blue"
          active={filterType === 'unread'}
          onClick={() => setFilterType('unread')}
        />
        <StatCard 
          label="價格下跌" 
          value={stats.priceDrops} 
          icon={TrendingDown}
          color="green"
          active={filterType === 'price_drop'}
          onClick={() => setFilterType('price_drop')}
        />
        <StatCard 
          label="價格上漲" 
          value={stats.priceIncreases} 
          icon={TrendingUp}
          color="red"
          active={filterType === 'price_increase'}
          onClick={() => setFilterType('price_increase')}
        />
      </div>

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
      <div className="glass-panel rounded-2xl overflow-hidden border border-white/40">
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
              <Button size="sm" variant="ghost" className="h-8">
                <CheckCheck className="w-4 h-4 mr-1" />
                標為已讀
              </Button>
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
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage <= 1}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage >= totalPages}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

// =============================================
// 子組件
// =============================================

function StatCard({ 
  label, 
  value, 
  icon: Icon, 
  color = 'slate',
  active,
  onClick
}: { 
  label: string
  value: number
  icon: React.ElementType
  color?: 'slate' | 'blue' | 'green' | 'red'
  active?: boolean
  onClick?: () => void
}) {
  const colors = {
    slate: { bg: 'bg-slate-100', text: 'text-slate-600', activeBg: 'bg-slate-200' },
    blue: { bg: 'bg-blue-100', text: 'text-blue-600', activeBg: 'bg-blue-200' },
    green: { bg: 'bg-green-100', text: 'text-green-600', activeBg: 'bg-green-200' },
    red: { bg: 'bg-red-100', text: 'text-red-600', activeBg: 'bg-red-200' },
  }
  const c = colors[color]

  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={cn(
        "glass-panel rounded-xl p-4 text-left transition-all border-2",
        active ? `${c.activeBg} border-${color}-400` : "border-transparent hover:border-slate-200"
      )}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-2xl font-bold text-slate-800">{value}</p>
          <p className="text-sm text-slate-500">{label}</p>
        </div>
        <div className={cn("p-2 rounded-lg", c.bg)}>
          <Icon className={cn("w-5 h-5", c.text)} />
        </div>
      </div>
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
      labelBg: "bg-green-50 text-green-700 border-green-200"
    },
    price_increase: { 
      icon: TrendingUp, 
      color: "text-red-600", 
      bg: "bg-red-100", 
      label: "漲價",
      labelBg: "bg-red-50 text-red-700 border-red-200"
    },
    out_of_stock: { 
      icon: AlertTriangle, 
      color: "text-orange-600", 
      bg: "bg-orange-100", 
      label: "缺貨",
      labelBg: "bg-orange-50 text-orange-700 border-orange-200"
    },
    back_in_stock: { 
      icon: Check, 
      color: "text-blue-600", 
      bg: "bg-blue-100", 
      label: "補貨",
      labelBg: "bg-blue-50 text-blue-700 border-blue-200"
    },
  }

  const config = typeConfig[alert.alert_type as keyof typeof typeConfig] || { 
    icon: Bell, 
    color: "text-slate-600", 
    bg: "bg-slate-100", 
    label: "通知",
    labelBg: "bg-slate-50 text-slate-700 border-slate-200"
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
          <Badge variant="outline" className={cn("text-xs font-medium", config.labelBg)}>
            {config.label}
          </Badge>
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
          <Button
            size="sm"
            variant="ghost"
            onClick={onMarkRead}
            className="h-8 px-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
            title="標記已讀"
          >
            <CheckCheck className="w-4 h-4" />
          </Button>
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
