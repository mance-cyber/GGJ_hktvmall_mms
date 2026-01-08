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
  MessageSquare
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

  // 路由變化時關閉移動端菜單
  useEffect(() => {
    setIsMobileOpen(false)
  }, [pathname])

  // 移動端菜單按鈕
  const MobileMenuButton = () => (
    <button
      onClick={() => setIsMobileOpen(!isMobileOpen)}
      className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-lg border border-gray-200"
    >
      {isMobileOpen ? (
        <X className="w-6 h-6 text-gray-600" />
      ) : (
        <Menu className="w-6 h-6 text-gray-600" />
      )}
    </button>
  )

  // 側邊欄內容
  const SidebarContent = () => (
    <>
      {/* Logo */}
      <div className="flex items-center h-16 px-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/30">
            <span className="text-white font-bold text-sm">AI</span>
          </div>
          <div>
            <h1 className="text-lg font-bold text-gray-900">GoGoJap</h1>
            <p className="text-xs text-gray-500">AI 營運系統</p>
          </div>
        </div>
      </div>

      {/* Navigation - 分組顯示 */}
      <nav className="mt-4 px-3 flex-1 overflow-y-auto">
        {navigationGroups.map((group, groupIdx) => (
          <div key={group.title} className={cn(groupIdx > 0 && "mt-6")}>
            {/* 分組標題 */}
            <h3 className="px-3 mb-2 text-xs font-semibold text-gray-400 uppercase tracking-wider">
              {group.title}
            </h3>
            
            <ul className="space-y-1">
              {group.items.map((item) => {
                const isActive = pathname === item.href ||
                  (item.href !== '/' && pathname.startsWith(item.href))
                const showBadge = item.href === '/alerts' && unreadCount > 0

                return (
                  <li key={item.name}>
                    <Link
                      href={item.href}
                      className={cn(
                        "flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium",
                        "transition-all duration-200",
                        isActive
                          ? 'bg-blue-50 text-blue-700 shadow-sm'
                          : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                      )}
                    >
                      <div className="flex items-center">
                        <item.icon className={cn(
                          "w-5 h-5 mr-3 transition-colors",
                          isActive ? 'text-blue-600' : 'text-gray-400'
                        )} />
                        {item.name}
                      </div>
                      
                      {/* 未讀警報徽章 */}
                      {showBadge && (
                        <motion.span
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="flex items-center justify-center min-w-[20px] h-5 px-1.5 bg-red-500 text-white text-xs font-bold rounded-full"
                        >
                          {unreadCount > 99 ? '99+' : unreadCount}
                        </motion.span>
                      )}
                      
                      {/* Active 指示器 */}
                      {isActive && (
                        <ChevronRight className="w-4 h-4 text-blue-400" />
                      )}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">
          <p>GoGoJap 營運系統</p>
          <p className="mt-1">v1.0.0</p>
        </div>
      </div>
    </>
  )

  return (
    <>
      {/* 移動端菜單按鈕 */}
      <MobileMenuButton />

      {/* 桌面端側邊欄 */}
      <div className="hidden lg:flex lg:flex-col lg:fixed lg:inset-y-0 lg:left-0 lg:w-64 bg-white shadow-lg border-r border-gray-200 z-40">
        <SidebarContent />
      </div>

      {/* 移動端側邊欄 */}
      <AnimatePresence>
        {isMobileOpen && (
          <>
            {/* 遮罩層 */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsMobileOpen(false)}
              className="lg:hidden fixed inset-0 bg-black/50 z-40"
            />
            
            {/* 側邊欄 */}
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="lg:hidden fixed inset-y-0 left-0 w-64 bg-white shadow-xl z-50 flex flex-col"
            >
              <SidebarContent />
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  )
}

// =============================================
// 輔助組件：移動端底部導航
// =============================================

export function MobileBottomNav() {
  const pathname = usePathname()
  
  const quickNav = [
    { name: '首頁', href: '/', icon: LayoutDashboard },
    { name: '警報', href: '/alerts', icon: Bell },
    { name: '競品', href: '/competitors', icon: Eye },
    { name: '設定', href: '/settings', icon: Settings },
  ]

  return (
    <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-40 safe-area-bottom">
      <nav className="flex items-center justify-around py-2">
        {quickNav.map((item) => {
          const isActive = pathname === item.href ||
            (item.href !== '/' && pathname.startsWith(item.href))
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex flex-col items-center py-1 px-3 rounded-lg transition-colors",
                isActive ? 'text-blue-600' : 'text-gray-500'
              )}
            >
              <item.icon className="w-6 h-6" />
              <span className="text-xs mt-1 font-medium">{item.name}</span>
            </Link>
          )
        })}
      </nav>
    </div>
  )
}
