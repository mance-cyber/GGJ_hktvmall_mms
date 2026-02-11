'use client'

// =============================================
// Sidebar - Future Tech 風格側邊欄
// =============================================

import { useState, useEffect, useMemo } from 'react'
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
  Globe,
  Brain,
  MessageSquare,
  LogOut,
  Image,
  Search,
  Zap,
  Clock,
  DollarSign,
  ClipboardCheck,
  Bot,
  LucideIcon
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { useAuth } from '@/components/providers/auth-provider'
import { usePermissions, PERMISSIONS } from '@/hooks/usePermissions'

// =============================================
// 導航項目類型定義
// =============================================

interface NavItem {
  name: string
  href: string
  icon: LucideIcon
  description?: string
  permissions?: string[]
  roles?: ('admin' | 'operator' | 'viewer')[]
}

interface NavGroup {
  title: string
  items: NavItem[]
  color: {
    gradient: string
    border: string
    accent: string
    activeBg: string
    activeBorder: string
    activeGlow: string
    indicator: string
  }
  permissions?: string[]
  roles?: ('admin' | 'operator' | 'viewer')[]
}

// =============================================
// 分類顏色主題
// =============================================

const categoryColors = {
  blue: {
    gradient: 'from-blue-500/10 via-blue-400/5 to-transparent',
    border: 'border-blue-300/30',
    accent: 'text-blue-600',
    activeBg: 'bg-blue-50',
    activeBorder: 'border-blue-400/50',
    activeGlow: 'shadow-[0_0_15px_rgba(59,130,246,0.15)]',
    indicator: 'from-blue-500 to-cyan-500',
  },
  emerald: {
    gradient: 'from-emerald-500/10 via-emerald-400/5 to-transparent',
    border: 'border-emerald-300/30',
    accent: 'text-emerald-600',
    activeBg: 'bg-emerald-50',
    activeBorder: 'border-emerald-400/50',
    activeGlow: 'shadow-[0_0_15px_rgba(16,185,129,0.15)]',
    indicator: 'from-emerald-500 to-teal-500',
  },
  purple: {
    gradient: 'from-purple-500/10 via-purple-400/5 to-transparent',
    border: 'border-purple-300/30',
    accent: 'text-purple-600',
    activeBg: 'bg-purple-50',
    activeBorder: 'border-purple-400/50',
    activeGlow: 'shadow-[0_0_15px_rgba(168,85,247,0.15)]',
    indicator: 'from-purple-500 to-violet-500',
  },
  orange: {
    gradient: 'from-orange-500/10 via-orange-400/5 to-transparent',
    border: 'border-orange-300/30',
    accent: 'text-orange-600',
    activeBg: 'bg-orange-50',
    activeBorder: 'border-orange-400/50',
    activeGlow: 'shadow-[0_0_15px_rgba(249,115,22,0.15)]',
    indicator: 'from-orange-500 to-amber-500',
  },
  pink: {
    gradient: 'from-pink-500/10 via-pink-400/5 to-transparent',
    border: 'border-pink-300/30',
    accent: 'text-pink-600',
    activeBg: 'bg-pink-50',
    activeBorder: 'border-pink-400/50',
    activeGlow: 'shadow-[0_0_15px_rgba(236,72,153,0.15)]',
    indicator: 'from-pink-500 to-rose-500',
  },
  cyan: {
    gradient: 'from-cyan-500/10 via-cyan-400/5 to-transparent',
    border: 'border-cyan-300/30',
    accent: 'text-cyan-600',
    activeBg: 'bg-cyan-50',
    activeBorder: 'border-cyan-400/50',
    activeGlow: 'shadow-[0_0_15px_rgba(6,182,212,0.15)]',
    indicator: 'from-cyan-500 to-blue-500',
  },
}

// =============================================
// 導航配置 - 按功能分組（含權限和顏色）
// =============================================

const navigationGroups: NavGroup[] = [
  {
    title: '總覽',
    color: categoryColors.blue,
    items: [
      { name: '儀表板', href: '/', icon: LayoutDashboard },
      { name: '投資回報', href: '/roi', icon: DollarSign, description: 'GoGoJap 幫你賺了多少錢' },
    ]
  },
  {
    title: '市場情報',
    color: categoryColors.emerald,
    items: [
      {
        name: 'AI 助手',
        href: '/agent',
        icon: MessageSquare,
        permissions: [PERMISSIONS.AGENT_READ]
      },
      {
        name: '市場應對中心',
        href: '/market-response',
        icon: Globe,
        permissions: [PERMISSIONS.COMPETITORS_READ]
      },
      {
        name: '競品監測',
        href: '/competitors',
        icon: Eye,
        permissions: [PERMISSIONS.COMPETITORS_READ]
      },
      {
        name: '價格趨勢',
        href: '/trends',
        icon: TrendingUp,
        permissions: [PERMISSIONS.PRICES_READ]
      },
      {
        name: 'SEO 排名',
        href: '/seo-ranking',
        icon: Search,
        permissions: [PERMISSIONS.COMPETITORS_READ]
      },
    ]
  },
  {
    title: '商品管理',
    color: categoryColors.purple,
    items: [
      {
        name: '改價審批',
        href: '/pricing-approval',
        icon: ClipboardCheck,
        description: 'Human-in-the-Loop 審批 AI 改價提案',
        permissions: [PERMISSIONS.PRICES_READ]
      },
      {
        name: '商品庫',
        href: '/products',
        icon: Package,
        permissions: [PERMISSIONS.COMPETITORS_READ]
      },
      {
        name: '類別管理',
        href: '/categories',
        icon: FolderOpen,
        permissions: [PERMISSIONS.COMPETITORS_READ]
      },
      {
        name: 'AI 圖片生成',
        href: '/image-generation/upload',
        icon: Image,
        permissions: [PERMISSIONS.AGENT_READ]
      },
      {
        name: '內容流水線',
        href: '/content-pipeline',
        icon: Zap,
        permissions: [PERMISSIONS.AGENT_READ]
      },
      {
        name: '生成歷史',
        href: '/content-history',
        icon: Clock,
        permissions: [PERMISSIONS.AGENT_READ]
      },
      {
        name: 'AI 分析',
        href: '/ai-analysis',
        icon: Brain,
        permissions: [PERMISSIONS.AGENT_READ]
      },
    ]
  },
  {
    title: '通知',
    color: categoryColors.orange,
    items: [
      {
        name: '警報中心',
        href: '/alerts',
        icon: Bell,
        permissions: [PERMISSIONS.NOTIFICATIONS_READ]
      },
    ]
  },
  {
    title: '系統',
    color: categoryColors.pink,
    roles: ['admin'],
    items: [
      {
        name: 'Agent Team',
        href: '/agent-team',
        icon: Bot,
        description: 'Agent 團隊狀態與控制',
        permissions: [PERMISSIONS.SYSTEM_SETTINGS_READ]
      },
      {
        name: 'AI 設定',
        href: '/ai-settings',
        icon: Brain,
        permissions: [PERMISSIONS.SYSTEM_SETTINGS_READ]
      },
      {
        name: '數據導出',
        href: '/export',
        icon: Download,
        permissions: [PERMISSIONS.REPORTS_EXPORT]
      },
      {
        name: '設定',
        href: '/settings',
        icon: Settings,
        permissions: [PERMISSIONS.SYSTEM_SETTINGS_READ]
      },
    ]
  },
]

// =============================================
// 主組件
// =============================================

export function Sidebar() {
  const pathname = usePathname()
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const { user, logout } = useAuth()
  const { role, hasAnyPermission } = usePermissions()

  // 獲取未讀警報數
  const { data: alerts } = useQuery({
    queryKey: ['alerts-count'],
    queryFn: () => api.getAlerts(false, undefined, 1),
    refetchInterval: 30000,
  })
  const unreadCount = alerts?.unread_count || 0

  // 過濾有權限的導航組和項目
  const filteredNavGroups = useMemo(() => {
    return navigationGroups
      .filter((group) => {
        if (group.roles && role && !group.roles.includes(role)) return false
        if (group.permissions && !hasAnyPermission(...group.permissions)) return false
        return true
      })
      .map((group) => ({
        ...group,
        items: group.items.filter((item) => {
          if (item.roles && role && !item.roles.includes(role)) return false
          if (item.permissions && !hasAnyPermission(...item.permissions)) return false
          return true
        }),
      }))
      .filter((group) => group.items.length > 0)
  }, [role, hasAnyPermission])

  // 路由變化時關閉移動端菜單
  useEffect(() => {
    setIsMobileOpen(false)
  }, [pathname])

  // 移動端菜單按鈕
  const MobileMenuButton = () => (
    <button
      type="button"
      onClick={() => setIsMobileOpen(!isMobileOpen)}
      className="lg:hidden fixed top-4 left-4 z-50 p-2.5 rounded-xl glass-panel hover:bg-white/90 transition-all"
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
    <div className="h-full rounded-2xl glass-sidebar p-6 relative overflow-hidden flex flex-col">
      {/* 全息邊緣效果 */}
      <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-100/20 via-transparent to-purple-100/20 pointer-events-none" />

      {/* Logo */}
      <div className="mb-6 relative">
        <div className="flex items-center gap-3">
          <img
            src="/images/GGJ_small_logo_001.ico"
            alt="GoGoJap Logo"
            className="w-20 h-20 object-contain"
          />
          <div>
            <div className="text-gray-900 font-semibold text-lg">GoGoJap</div>
            <div className="text-gray-500 text-xs flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
              AI 營運系統
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto scrollbar-subtle space-y-4 pr-1">
        {filteredNavGroups.map((group) => {
          const colors = group.color

          return (
            <div
              key={group.title}
              className={cn(
                "relative p-3 rounded-xl backdrop-blur-sm",
                `bg-gradient-to-br ${colors.gradient}`,
                `border ${colors.border}`
              )}
            >
              {/* 分類標題 */}
              <div className={cn("text-[10px] uppercase tracking-widest mb-2.5 px-2 font-bold flex items-center gap-2", colors.accent)}>
                <div className={cn("h-px flex-1 bg-gradient-to-r opacity-30", colors.indicator)} />
                <span>{group.title}</span>
                <div className={cn("h-px flex-1 bg-gradient-to-l opacity-30", colors.indicator)} />
              </div>

              <div className="space-y-1">
                {group.items.map((item) => {
                  const Icon = item.icon
                  const isActive = pathname === item.href ||
                    (item.href !== '/' && pathname.startsWith(item.href))
                  const showBadge = item.href === '/alerts' && unreadCount > 0

                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={cn(
                        "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative overflow-hidden",
                        isActive
                          ? cn(colors.activeBg, "border", colors.activeBorder, colors.activeGlow)
                          : "hover:bg-white/50 border border-transparent"
                      )}
                    >
                      <Icon className={cn(
                        "w-4 h-4 relative z-10 transition-all duration-200 flex-shrink-0",
                        isActive ? colors.accent : "text-gray-500 group-hover:text-gray-700"
                      )} />

                      <span className={cn(
                        "relative z-10 transition-all duration-200 text-[13px] whitespace-nowrap flex-1",
                        isActive ? "text-gray-900 font-bold" : "text-gray-700 font-medium group-hover:text-gray-900"
                      )}>
                        {item.name}
                      </span>

                      {/* 未讀警報徽章 */}
                      {showBadge && (
                        <span className="flex items-center justify-center min-w-[20px] h-5 px-1.5 bg-red-500 text-white text-xs font-bold rounded-full animate-pulse-glow">
                          {unreadCount > 99 ? '99+' : unreadCount}
                        </span>
                      )}

                      {/* Active 指示器 */}
                      {isActive && (
                        <div className={cn("absolute right-0 top-1/2 -translate-y-1/2 w-0.5 h-6 rounded-l-full bg-gradient-to-b", colors.indicator)} />
                      )}
                    </Link>
                  )
                })}
              </div>
            </div>
          )
        })}
      </nav>

      {/* User Info & Logout */}
      <div className="mt-4 pt-4 border-t border-purple-200/30">
        {user && (
          <div className="p-3 rounded-xl bg-gradient-to-br from-purple-50 to-cyan-50 border border-purple-200/50 backdrop-blur-sm">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-cyan-500 rounded-xl flex items-center justify-center text-white font-bold text-sm shadow-lg">
                {user.full_name?.[0] || user.email[0].toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user.full_name || user.email}
                </p>
                <p className="text-xs text-gray-500 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                  {role === 'admin' ? '管理員' : role === 'operator' ? '操作員' : '檢視者'}
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={logout}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-red-600 hover:bg-red-50/50 rounded-lg transition-all border border-transparent hover:border-red-200"
            >
              <LogOut className="w-4 h-4" />
              登出
            </button>
          </div>
        )}
      </div>
    </div>
  )

  return (
    <>
      {/* 移動端菜單按鈕 */}
      <MobileMenuButton />

      {/* 桌面端側邊欄 */}
      <div className="hidden lg:block lg:fixed lg:inset-y-0 lg:left-0 lg:w-72 lg:p-6 z-20">
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
              className="lg:hidden fixed inset-0 bg-black/30 backdrop-blur-sm z-40"
            />

            {/* 側邊欄 */}
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 300 }}
              className="lg:hidden fixed inset-y-0 left-0 w-72 p-4 z-50"
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
  const [showMore, setShowMore] = useState(false)
  const { data: alerts } = useQuery({
    queryKey: ['alerts-count-mobile'],
    queryFn: () => api.getAlerts(false, undefined, 1),
    refetchInterval: 30000,
  })
  const unreadCount = alerts?.unread_count || 0

  // 主導航項目（顯示在底部欄）
  const quickNav = [
    { name: '首頁', href: '/', icon: LayoutDashboard },
    { name: '警報', href: '/alerts', icon: Bell, badge: unreadCount },
    { name: 'AI', href: '/agent', icon: MessageSquare },
  ]

  // 更多菜單項目
  const moreItems = [
    { name: '競品監測', href: '/competitors', icon: Eye },
    { name: '商品庫', href: '/products', icon: Package },
    { name: 'AI 文案', href: '/ai-content', icon: Sparkles },
    { name: '價格趨勢', href: '/trends', icon: TrendingUp },
    { name: '設定', href: '/settings', icon: Settings },
  ]

  // 檢查更多菜單中是否有當前頁面
  const isMoreActive = moreItems.some(
    item => pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href))
  )

  return (
    <>
      {/* 更多菜單彈出層 */}
      <AnimatePresence>
        {showMore && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowMore(false)}
              className="lg:hidden fixed inset-0 bg-black/20 backdrop-blur-sm z-40"
            />
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="lg:hidden fixed bottom-20 left-3 right-3 z-50 glass-panel rounded-2xl p-3 border border-purple-200/40 shadow-xl"
            >
              <div className="grid grid-cols-4 gap-2">
                {moreItems.map((item) => {
                  const isActive = pathname === item.href ||
                    (item.href !== '/' && pathname.startsWith(item.href))

                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      onClick={() => setShowMore(false)}
                      className={cn(
                        "flex flex-col items-center py-3 px-2 rounded-xl transition-all",
                        isActive
                          ? "text-purple-600 bg-purple-50/80"
                          : "text-gray-600 active:bg-gray-100"
                      )}
                    >
                      <item.icon className="w-5 h-5" />
                      <span className="text-[10px] mt-1.5 font-medium text-center leading-tight">{item.name}</span>
                    </Link>
                  )
                })}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* 底部導航欄 */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 z-40 px-3 pb-3 safe-area-bottom bg-gradient-to-t from-white/80 to-transparent pt-6">
        <nav className="flex items-center justify-around py-1 px-2 rounded-2xl glass-panel border border-purple-200/30">
          {quickNav.map((item) => {
            const isActive = pathname === item.href ||
              (item.href !== '/' && pathname.startsWith(item.href))

            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "relative flex flex-col items-center py-3 px-5 rounded-xl transition-all touch-target",
                  isActive
                    ? "text-purple-600 bg-purple-50/80"
                    : "text-gray-500 active:bg-gray-100"
                )}
              >
                <item.icon className={cn("w-5 h-5", isActive && "scale-110")} />
                <span className="text-[10px] mt-1 font-medium">{item.name}</span>
                {/* 未讀徽章 */}
                {item.badge && item.badge > 0 && (
                  <span className="absolute -top-0.5 right-2 min-w-[18px] h-[18px] flex items-center justify-center px-1 bg-red-500 text-white text-[10px] font-bold rounded-full">
                    {item.badge > 99 ? '99+' : item.badge}
                  </span>
                )}
              </Link>
            )
          })}

          {/* 更多按鈕 */}
          <button
            type="button"
            onClick={() => setShowMore(!showMore)}
            className={cn(
              "relative flex flex-col items-center py-3 px-5 rounded-xl transition-all touch-target",
              showMore || isMoreActive
                ? "text-purple-600 bg-purple-50/80"
                : "text-gray-500 active:bg-gray-100"
            )}
          >
            <Menu className={cn("w-5 h-5", (showMore || isMoreActive) && "scale-110")} />
            <span className="text-[10px] mt-1 font-medium">更多</span>
          </button>
        </nav>
      </div>
    </>
  )
}
