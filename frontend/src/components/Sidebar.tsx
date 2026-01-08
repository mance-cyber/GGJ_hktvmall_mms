'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard,
  FolderOpen,
  Bell,
  Settings,
  TrendingUp,
  Download,
  Package,
  Sparkles,
  Eye,
  Menu,
  X,
  ChevronRight,
  Globe,
  Brain,
  MessageSquare,
  Truck,
  DollarSign
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

// =============================================
// 導航配置 - 按功能分組
// =============================================

const navigationGroups = [
  {
    title: '總覽',
    items: [
      { name: '儀表板', href: '/', icon: LayoutDashboard },
    ]
  },
  {
    title: '營運中心',
    items: [
      { name: '訂單管理', href: '/orders', icon: Truck, description: '訂單同步與出貨' },
      { name: '客服收件箱', href: '/inbox', icon: MessageSquare, description: '客戶查詢' },
    ]
  },
  {
    title: '市場情報',
    items: [
      { name: 'AI 助手', href: '/agent', icon: MessageSquare, description: '對話式數據分析', highlight: true },
      { name: '市場應對中心', href: '/market-response', icon: Globe, description: 'SKU 分析與競品配對' },
      { name: '競品監測', href: '/competitors', icon: Eye, description: '追蹤對手價格變動' },
      { name: '價格趨勢', href: '/trends', icon: TrendingUp, description: '歷史價格走勢圖' },
    ]
  },
  {
    title: '商品管理',
    items: [
      { name: '商品庫', href: '/products', icon: Package, description: '管理自家商品' },
      { name: '類別管理', href: '/categories', icon: FolderOpen, description: 'HKTVmall 類別數據' },
      { name: 'AI 文案', href: '/ai-content', icon: Sparkles, description: '智能生成商品描述' },
      { name: 'AI 分析', href: '/ai-analysis', icon: Brain, description: '數據摘要 + 策略' },
    ]
  },
  {
    title: '通知',
    items: [
      { name: '警報中心', href: '/alerts', icon: Bell, highlight: true, description: '價格變動提醒' },
    ]
  },
  {
    title: '系統',
    items: [
      { name: 'AI 設定', href: '/ai-settings', icon: Brain, description: 'API Key 與模型選擇' },
      { name: '數據導出', href: '/export', icon: Download, description: '匯出報表' },
      { name: '設定', href: '/settings', icon: Settings, description: '系統配置' },
    ]
  },
]

// 扁平化導航（用於移動端底部導航）
const navigation = navigationGroups.flatMap(g => g.items)

// =============================================
// 主組件
// =============================================

export function Sidebar() {
  const pathname = usePathname()
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  // 獲取未讀警報數
  const { data: alerts } = useQuery({
    queryKey: ['alerts-count'],
    queryFn: () => api.getAlerts(false, undefined, 1),
    refetchInterval: 30000,
  })
  const unreadCount = alerts?.unread_count || 0

  // 檢測屏幕尺寸
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024)
    }
    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  return (
    <>
      {/* Mobile Trigger */}
      {isMobile && (
        <div className="fixed top-4 left-4 z-50">
          <button
            onClick={() => setIsMobileOpen(!isMobileOpen)}
            className="p-2 bg-white rounded-lg shadow-lg border border-slate-100 text-slate-600"
          >
            {isMobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      )}

      {/* Sidebar Container */}
      <AnimatePresence>
        {(!isMobile || isMobileOpen) && (
          <motion.aside
            initial={isMobile ? { x: -300 } : false}
            animate={{ x: 0 }}
            exit={isMobile ? { x: -300 } : false}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className={cn(
              "fixed top-0 left-0 h-screen bg-white/80 backdrop-blur-xl border-r border-white/20 shadow-xl z-40 overflow-y-auto w-64",
              "flex flex-col"
            )}
          >
            {/* Logo */}
            <div className="p-6 border-b border-slate-100/50">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-blue-500/20">
                  G
                </div>
                <div>
                  <h1 className="font-bold text-xl text-slate-800 tracking-tight">GoGoJap</h1>
                  <p className="text-xs text-slate-500 font-medium">AI 營運系統</p>
                </div>
              </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-4 space-y-6">
              {navigationGroups.map((group) => (
                <div key={group.title}>
                  <h3 className="px-4 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
                    {group.title}
                  </h3>
                  <div className="space-y-1">
                    {group.items.map((item) => {
                      const isActive = pathname === item.href
                      const Icon = item.icon
                      
                      return (
                        <Link
                          key={item.name}
                          href={item.href}
                          onClick={() => isMobile && setIsMobileOpen(false)}
                        >
                          <div className={cn(
                            "group flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200",
                            isActive 
                              ? "bg-blue-50 text-blue-600 shadow-sm" 
                              : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                          )}>
                            <Icon className={cn(
                              "mr-3 h-5 w-5 transition-colors",
                              isActive ? "text-blue-600" : "text-slate-400 group-hover:text-slate-600",
                              item.highlight && !isActive && "text-amber-500"
                            )} />
                            <div className="flex-1">
                              <span>{item.name}</span>
                              {item.description && (
                                <p className="text-[10px] text-slate-400 font-normal line-clamp-1 opacity-0 group-hover:opacity-100 transition-opacity h-0 group-hover:h-auto">
                                  {item.description}
                                </p>
                              )}
                            </div>
                            {item.name === '警報中心' && unreadCount > 0 && (
                              <span className="bg-red-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full ml-auto animate-pulse">
                                {unreadCount}
                              </span>
                            )}
                            {isActive && <ChevronRight className="w-4 h-4 text-blue-400 ml-auto" />}
                          </div>
                        </Link>
                      )
                    })}
                  </div>
                </div>
              ))}
            </nav>

            {/* User Profile */}
            <div className="p-4 border-t border-slate-100/50 bg-slate-50/50">
              <div className="flex items-center gap-3 px-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-slate-200 to-slate-300 border-2 border-white shadow-sm" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-700 truncate">Administrator</p>
                  <p className="text-xs text-slate-500 truncate">admin@gogojap.com</p>
                </div>
                <Link href="/settings">
                  <Settings className="w-4 h-4 text-slate-400 hover:text-slate-600 cursor-pointer" />
                </Link>
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePres
ence>
    </>
  )
}

// =============================================
// 移動端底部導航
// =============================================

export function MobileBottomNav() {
  const pathname = usePathname()
  
  // 只顯示核心功能
  const mainNavItems = [
    { name: '首頁', href: '/', icon: LayoutDashboard },
    { name: '訂單', href: '/orders', icon: Truck },
    { name: '警報', href: '/alerts', icon: Bell },
    { name: '商品', href: '/products', icon: Package },
  ]

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-lg border-t border-slate-200 px-6 py-2 lg:hidden z-50 safe-area-pb">
      <div className="flex justify-between items-center">
        {mainNavItems.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon
          
          return (
            <Link key={item.name} href={item.href}>
              <div className="flex flex-col items-center p-2">
                <div className={cn(
                  "p-1.5 rounded-lg transition-colors",
                  isActive ? "bg-blue-50 text-blue-600" : "text-slate-400"
                )}>
                  <Icon size={24} />
                </div>
                <span className={cn(
                  "text-[10px] font-medium mt-1",
                  isActive ? "text-blue-600" : "text-slate-400"
                )}>
                  {item.name}
                </span>
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
