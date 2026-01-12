'use client'

import { useState, useEffect } from 'react'
import { motion, useScroll, useTransform } from 'framer-motion'
import Link from 'next/link'
import { cn } from '@/lib/utils'
import {
  Zap,
  Cpu,
  Database,
  TrendingUp,
  Bell,
  User,
  Menu,
  X
} from 'lucide-react'

// =============================================
// 全息賽博朋克導航欄
// Holographic Cyberpunk Navbar
// =============================================

interface NavItem {
  label: string
  href: string
  icon: React.ElementType
}

const navItems: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: Cpu },
  { label: 'Analytics', href: '/analytics', icon: TrendingUp },
  { label: 'Database', href: '/database', icon: Database },
  { label: 'Alerts', href: '/alerts', icon: Bell },
]

export function CyberNavbar() {
  const [activeIndex, setActiveIndex] = useState(0)
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const { scrollY } = useScroll()

  // 滾動時改變背景透明度
  const navOpacity = useTransform(scrollY, [0, 100], [0.7, 0.95])

  return (
    <>
      {/* 導航欄容器 */}
      <motion.nav
        style={{ opacity: navOpacity }}
        className={cn(
          "fixed top-0 left-0 right-0 z-50",
          "border-b border-cyan-500/30"
        )}
      >
        {/* 全息掃描線動畫背景 */}
        <div className="absolute inset-0 overflow-hidden">
          {/* 玻璃態背景 */}
          <div className="absolute inset-0 bg-slate-950/90 backdrop-blur-xl" />

          {/* 動態網格 */}
          <div className="absolute inset-0 cyber-grid opacity-20" />

          {/* 掃描線動畫 */}
          <motion.div
            className="absolute inset-0 bg-gradient-to-b from-cyan-500/10 via-transparent to-transparent"
            animate={{
              y: ['-100%', '200%'],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: 'linear',
            }}
          />

          {/* 數據流效果 */}
          <DataFlow />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3 group cursor-pointer"
            >
              {/* 全息 Logo 圖標 */}
              <div className="relative">
                <motion.div
                  className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-purple-600 p-[2px]"
                  whileHover={{ scale: 1.05 }}
                  transition={{ type: 'spring', stiffness: 400 }}
                >
                  <div className="w-full h-full bg-slate-950 rounded-lg flex items-center justify-center">
                    <Zap className="w-5 h-5 text-cyan-400" />
                  </div>
                </motion.div>

                {/* 光暈效果 */}
                <motion.div
                  className="absolute inset-0 bg-cyan-500/20 rounded-lg blur-xl"
                  animate={{
                    opacity: [0.3, 0.6, 0.3],
                    scale: [0.95, 1.05, 0.95],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: 'easeInOut',
                  }}
                />
              </div>

              {/* Logo 文字 */}
              <div className="flex flex-col">
                <span className="text-lg font-bold neon-text tracking-wider font-orbitron">
                  NEXUS
                </span>
                <span className="text-[10px] text-cyan-400/60 tracking-widest font-rajdhani">
                  SYSTEM v2.0
                </span>
              </div>
            </motion.div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-1">
              {navItems.map((item, index) => (
                <NavLink
                  key={item.href}
                  item={item}
                  index={index}
                  isActive={activeIndex === index}
                  onClick={() => setActiveIndex(index)}
                />
              ))}
            </div>

            {/* Right Section */}
            <div className="hidden md:flex items-center gap-3">
              {/* 通知按鈕 */}
              <HolographicButton>
                <Bell className="w-4 h-4" />
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              </HolographicButton>

              {/* 用戶按鈕 */}
              <HolographicButton>
                <User className="w-4 h-4" />
              </HolographicButton>

              {/* CTA 按鈕 */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={cn(
                  "px-4 py-2 rounded-lg font-medium text-sm",
                  "bg-gradient-to-r from-cyan-500 to-purple-600",
                  "text-white shadow-lg shadow-cyan-500/30",
                  "hover:shadow-cyan-500/50 transition-shadow",
                  "font-rajdhani tracking-wide"
                )}
              >
                ACTIVATE
              </motion.button>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMobileOpen(!isMobileOpen)}
              className="md:hidden p-2 rounded-lg border border-cyan-500/30 hover:bg-cyan-500/10 transition-colors"
            >
              {isMobileOpen ? (
                <X className="w-5 h-5 text-cyan-400" />
              ) : (
                <Menu className="w-5 h-5 text-cyan-400" />
              )}
            </button>
          </div>
        </div>

        {/* Active Indicator Line */}
        <motion.div
          className="absolute bottom-0 h-[2px] bg-gradient-to-r from-transparent via-cyan-400 to-transparent"
          initial={false}
          animate={{
            x: `${activeIndex * 25}%`,
            width: '25%',
          }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        />
      </motion.nav>

      {/* Mobile Menu */}
      <motion.div
        initial={false}
        animate={{
          height: isMobileOpen ? 'auto' : 0,
          opacity: isMobileOpen ? 1 : 0,
        }}
        className="fixed top-16 left-0 right-0 z-40 md:hidden overflow-hidden"
      >
        <div className="bg-slate-950/95 backdrop-blur-xl border-b border-cyan-500/30 p-4">
          <div className="space-y-2">
            {navItems.map((item, index) => (
              <motion.a
                key={item.href}
                href={item.href}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                onClick={() => {
                  setActiveIndex(index)
                  setIsMobileOpen(false)
                }}
                className={cn(
                  "flex items-center gap-3 p-3 rounded-lg",
                  "transition-all duration-200",
                  activeIndex === index
                    ? "bg-cyan-500/10 border border-cyan-500/30"
                    : "hover:bg-cyan-500/5 border border-transparent"
                )}
              >
                <item.icon className="w-5 h-5 text-cyan-400" />
                <span className="text-slate-200 font-rajdhani">{item.label}</span>
              </motion.a>
            ))}
          </div>
        </div>
      </motion.div>
    </>
  )
}

// =============================================
// 導航連結組件
// =============================================

interface NavLinkProps {
  item: NavItem
  index: number
  isActive: boolean
  onClick: () => void
}

function NavLink({ item, index, isActive, onClick }: NavLinkProps) {
  return (
    <motion.a
      href={item.href}
      onClick={onClick}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="relative group px-4 py-2"
    >
      <div className="flex items-center gap-2">
        <item.icon className={cn(
          "w-4 h-4 transition-colors",
          isActive ? "text-cyan-400" : "text-slate-400 group-hover:text-cyan-400"
        )} />
        <span className={cn(
          "text-sm font-medium font-rajdhani tracking-wide transition-colors",
          isActive ? "text-cyan-400" : "text-slate-400 group-hover:text-cyan-400"
        )}>
          {item.label}
        </span>
      </div>

      {/* 懸停光暈效果 */}
      <motion.div
        className="absolute inset-0 rounded-lg bg-cyan-500/0 group-hover:bg-cyan-500/10 transition-colors"
        whileHover={{
          boxShadow: '0 0 20px rgba(0, 240, 255, 0.2)',
        }}
      />

      {/* Active 指示器 */}
      {isActive && (
        <motion.div
          layoutId="activeNav"
          className="absolute inset-0 rounded-lg border border-cyan-500/30 bg-cyan-500/5"
          initial={false}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        />
      )}
    </motion.a>
  )
}

// =============================================
// 全息按鈕組件
// =============================================

function HolographicButton({ children }: { children: React.ReactNode }) {
  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className={cn(
        "relative p-2 rounded-lg",
        "border border-cyan-500/30",
        "bg-slate-900/50 backdrop-blur-sm",
        "hover:bg-cyan-500/10 hover:border-cyan-500/50",
        "transition-all duration-200",
        "text-cyan-400"
      )}
    >
      {children}

      {/* 懸停光暈 */}
      <motion.div
        className="absolute inset-0 rounded-lg bg-cyan-500/0 blur-md -z-10"
        whileHover={{
          backgroundColor: 'rgba(0, 240, 255, 0.2)',
        }}
      />
    </motion.button>
  )
}

// =============================================
// 數據流動畫效果
// =============================================

function DataFlow() {
  const lines = Array.from({ length: 5 })

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {lines.map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-px h-20 bg-gradient-to-b from-transparent via-cyan-500/30 to-transparent"
          style={{
            left: `${20 + i * 20}%`,
          }}
          animate={{
            y: ['-100%', '200%'],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: 2 + i * 0.5,
            repeat: Infinity,
            ease: 'linear',
            delay: i * 0.3,
          }}
        />
      ))}
    </div>
  )
}
