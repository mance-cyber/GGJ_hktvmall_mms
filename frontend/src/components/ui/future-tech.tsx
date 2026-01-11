'use client'

// =============================================
// Future Tech Design System
// 未來科技感組件庫 - 淺色專業版
// =============================================

import React, { useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence, useMotionValue, useTransform, useSpring } from 'framer-motion'
import { cn } from '@/lib/utils'

// =============================================
// 1. 全息卡片 (HoloCard)
// 帶有動態光效和掃描線的玻璃卡片
// =============================================

interface HoloCardProps {
  children: React.ReactNode
  className?: string
  glowColor?: 'blue' | 'cyan' | 'purple' | 'green'
  interactive?: boolean
  scanLine?: boolean
}

export function HoloCard({
  children,
  className,
  glowColor = 'cyan',
  interactive = true,
  scanLine = false,
}: HoloCardProps) {
  const cardRef = useRef<HTMLDivElement>(null)
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)

  const glowColors = {
    blue: 'rgba(59, 130, 246, 0.15)',
    cyan: 'rgba(6, 182, 212, 0.15)',
    purple: 'rgba(139, 92, 246, 0.15)',
    green: 'rgba(34, 197, 94, 0.15)',
  }

  const borderColors = {
    blue: 'rgba(59, 130, 246, 0.3)',
    cyan: 'rgba(6, 182, 212, 0.3)',
    purple: 'rgba(139, 92, 246, 0.3)',
    green: 'rgba(34, 197, 94, 0.3)',
  }

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!interactive || !cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    mouseX.set(e.clientX - rect.left)
    mouseY.set(e.clientY - rect.top)
  }

  const background = useTransform(
    [mouseX, mouseY],
    ([x, y]) =>
      `radial-gradient(600px circle at ${x}px ${y}px, ${glowColors[glowColor]}, transparent 40%)`
  )

  return (
    <motion.div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className={cn(
        'relative rounded-2xl overflow-hidden',
        'bg-white/70 backdrop-blur-xl',
        'border border-white/60',
        'shadow-[0_8px_32px_rgba(0,0,0,0.08)]',
        'transition-all duration-300',
        interactive && 'hover:shadow-[0_16px_48px_rgba(0,0,0,0.12)] hover:border-opacity-80',
        className
      )}
      style={{
        borderColor: borderColors[glowColor],
      }}
    >
      {/* 動態光效 */}
      {interactive && (
        <motion.div
          className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
          style={{ background }}
        />
      )}

      {/* 掃描線 */}
      {scanLine && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div
            className="absolute inset-x-0 h-px bg-gradient-to-r from-transparent via-cyan-400/50 to-transparent"
            style={{
              animation: 'scan-vertical 3s ease-in-out infinite',
            }}
          />
        </div>
      )}

      {/* 角落裝飾 */}
      <div className="absolute top-0 left-0 w-6 h-6 border-l-2 border-t-2 border-cyan-400/30 rounded-tl-xl" />
      <div className="absolute top-0 right-0 w-6 h-6 border-r-2 border-t-2 border-cyan-400/30 rounded-tr-xl" />
      <div className="absolute bottom-0 left-0 w-6 h-6 border-l-2 border-b-2 border-cyan-400/30 rounded-bl-xl" />
      <div className="absolute bottom-0 right-0 w-6 h-6 border-r-2 border-b-2 border-cyan-400/30 rounded-br-xl" />

      {/* 內容 */}
      <div className="relative z-10">{children}</div>
    </motion.div>
  )
}

// =============================================
// 2. 數據指標卡 (DataMetric)
// 帶有動畫計數器和狀態指示的指標展示
// =============================================

interface DataMetricProps {
  label: string
  value: number
  suffix?: string
  prefix?: string
  trend?: number
  icon?: React.ReactNode
  color?: 'blue' | 'cyan' | 'green' | 'orange' | 'purple'
  size?: 'sm' | 'md' | 'lg'
  animate?: boolean
}

export function DataMetric({
  label,
  value,
  suffix = '',
  prefix = '',
  trend,
  icon,
  color = 'cyan',
  size = 'md',
  animate = true,
}: DataMetricProps) {
  const [displayValue, setDisplayValue] = useState(0)

  useEffect(() => {
    if (!animate) {
      setDisplayValue(value)
      return
    }

    const duration = 1500
    const steps = 60
    const increment = value / steps
    let current = 0
    let step = 0

    const timer = setInterval(() => {
      step++
      // 緩動函數
      const progress = step / steps
      const eased = 1 - Math.pow(1 - progress, 3)
      current = Math.round(value * eased)
      setDisplayValue(current)

      if (step >= steps) {
        clearInterval(timer)
        setDisplayValue(value)
      }
    }, duration / steps)

    return () => clearInterval(timer)
  }, [value, animate])

  const colors = {
    blue: {
      bg: 'bg-blue-50',
      text: 'text-blue-600',
      glow: 'shadow-blue-200/50',
      border: 'border-blue-200/50',
    },
    cyan: {
      bg: 'bg-cyan-50',
      text: 'text-cyan-600',
      glow: 'shadow-cyan-200/50',
      border: 'border-cyan-200/50',
    },
    green: {
      bg: 'bg-emerald-50',
      text: 'text-emerald-600',
      glow: 'shadow-emerald-200/50',
      border: 'border-emerald-200/50',
    },
    orange: {
      bg: 'bg-amber-50',
      text: 'text-amber-600',
      glow: 'shadow-amber-200/50',
      border: 'border-amber-200/50',
    },
    purple: {
      bg: 'bg-violet-50',
      text: 'text-violet-600',
      glow: 'shadow-violet-200/50',
      border: 'border-violet-200/50',
    },
  }

  const sizes = {
    sm: { value: 'text-2xl', label: 'text-xs', icon: 'w-8 h-8', padding: 'p-3' },
    md: { value: 'text-3xl', label: 'text-sm', icon: 'w-10 h-10', padding: 'p-4' },
    lg: { value: 'text-4xl', label: 'text-base', icon: 'w-12 h-12', padding: 'p-5' },
  }

  const colorStyle = colors[color]
  const sizeStyle = sizes[size]

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className={cn(
        'relative rounded-xl bg-white/80 backdrop-blur-sm',
        'border',
        colorStyle.border,
        sizeStyle.padding,
        'hover:shadow-lg transition-all duration-300',
        colorStyle.glow
      )}
    >
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className={cn('font-medium text-slate-500', sizeStyle.label)}>{label}</p>
          <div className="flex items-baseline gap-1">
            {prefix && <span className={cn('font-light', colorStyle.text)}>{prefix}</span>}
            <span className={cn('font-bold tracking-tight text-slate-800', sizeStyle.value)}>
              {displayValue.toLocaleString()}
            </span>
            {suffix && <span className={cn('font-light', colorStyle.text)}>{suffix}</span>}
          </div>
          {trend !== undefined && (
            <div className="flex items-center gap-1 mt-1">
              <span
                className={cn(
                  'text-xs font-medium',
                  trend > 0 ? 'text-emerald-600' : trend < 0 ? 'text-red-500' : 'text-slate-400'
                )}
              >
                {trend > 0 ? '↑' : trend < 0 ? '↓' : '→'} {Math.abs(trend)}%
              </span>
              <span className="text-xs text-slate-400">vs 上期</span>
            </div>
          )}
        </div>
        {icon && (
          <div
            className={cn(
              'rounded-xl flex items-center justify-center',
              colorStyle.bg,
              sizeStyle.icon
            )}
          >
            {icon}
          </div>
        )}
      </div>

      {/* 底部進度條效果 */}
      <div className="absolute bottom-0 left-0 right-0 h-0.5 overflow-hidden rounded-b-xl">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: '100%' }}
          transition={{ duration: 1.5, ease: [0.22, 1, 0.36, 1] }}
          className={cn('h-full', colorStyle.bg)}
          style={{ opacity: 0.5 }}
        />
      </div>
    </motion.div>
  )
}

// =============================================
// 3. 脈衝狀態指示器 (PulseStatus)
// 帶有脈衝動畫的狀態點
// =============================================

interface PulseStatusProps {
  status: 'online' | 'offline' | 'warning' | 'processing'
  label?: string
  size?: 'sm' | 'md' | 'lg'
}

export function PulseStatus({ status, label, size = 'md' }: PulseStatusProps) {
  const statusConfig = {
    online: {
      color: 'bg-emerald-500',
      pulse: 'bg-emerald-400',
      text: 'text-emerald-600',
      label: label || '在線',
    },
    offline: {
      color: 'bg-slate-400',
      pulse: 'bg-slate-300',
      text: 'text-slate-500',
      label: label || '離線',
    },
    warning: {
      color: 'bg-amber-500',
      pulse: 'bg-amber-400',
      text: 'text-amber-600',
      label: label || '警告',
    },
    processing: {
      color: 'bg-cyan-500',
      pulse: 'bg-cyan-400',
      text: 'text-cyan-600',
      label: label || '處理中',
    },
  }

  const sizes = {
    sm: { dot: 'w-2 h-2', pulse: 'w-4 h-4', text: 'text-xs' },
    md: { dot: 'w-2.5 h-2.5', pulse: 'w-5 h-5', text: 'text-sm' },
    lg: { dot: 'w-3 h-3', pulse: 'w-6 h-6', text: 'text-base' },
  }

  const config = statusConfig[status]
  const sizeConfig = sizes[size]

  return (
    <div className="flex items-center gap-2">
      <div className="relative flex items-center justify-center">
        {/* 脈衝環 */}
        {status !== 'offline' && (
          <span
            className={cn(
              'absolute rounded-full opacity-75 animate-ping',
              config.pulse,
              sizeConfig.pulse
            )}
            style={{ animationDuration: '2s' }}
          />
        )}
        {/* 核心點 */}
        <span className={cn('relative rounded-full', config.color, sizeConfig.dot)} />
      </div>
      <span className={cn('font-medium', config.text, sizeConfig.text)}>{config.label}</span>
    </div>
  )
}

// =============================================
// 4. 數據流背景 (DataStreamBg)
// 科技感數據流動畫背景
// =============================================

interface DataStreamBgProps {
  className?: string
  density?: 'low' | 'medium' | 'high'
  color?: 'cyan' | 'blue' | 'purple'
}

export function DataStreamBg({ className, density = 'medium', color = 'cyan' }: DataStreamBgProps) {
  const densityConfig = {
    low: 8,
    medium: 15,
    high: 25,
  }

  const colorConfig = {
    cyan: 'from-cyan-400/20 to-transparent',
    blue: 'from-blue-400/20 to-transparent',
    purple: 'from-violet-400/20 to-transparent',
  }

  const streamCount = densityConfig[density]

  return (
    <div className={cn('absolute inset-0 overflow-hidden pointer-events-none', className)}>
      {Array.from({ length: streamCount }).map((_, i) => (
        <motion.div
          key={i}
          className={cn('absolute w-px bg-gradient-to-b', colorConfig[color])}
          style={{
            left: `${(i / streamCount) * 100}%`,
            height: `${Math.random() * 30 + 20}%`,
          }}
          initial={{ y: '-100%', opacity: 0 }}
          animate={{
            y: '200%',
            opacity: [0, 1, 1, 0],
          }}
          transition={{
            duration: Math.random() * 3 + 2,
            repeat: Infinity,
            delay: Math.random() * 5,
            ease: 'linear',
          }}
        />
      ))}
    </div>
  )
}

// =============================================
// 5. 全息按鈕 (HoloButton)
// 帶有光效的科技感按鈕
// =============================================

interface HoloButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  icon?: React.ReactNode
}

export function HoloButton({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  icon,
  className,
  disabled,
  ...props
}: HoloButtonProps) {
  const variants = {
    primary: cn(
      'bg-gradient-to-r from-cyan-500 to-blue-500 text-white',
      'hover:from-cyan-400 hover:to-blue-400',
      'shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40',
      'border border-cyan-400/30'
    ),
    secondary: cn(
      'bg-white/80 backdrop-blur-sm text-slate-700',
      'hover:bg-white',
      'border border-slate-200 hover:border-cyan-300',
      'shadow-sm hover:shadow-md'
    ),
    ghost: cn(
      'bg-transparent text-slate-600',
      'hover:bg-slate-100/80',
      'border border-transparent hover:border-slate-200'
    ),
  }

  const sizes = {
    sm: 'px-3 py-1.5 text-sm rounded-lg gap-1.5',
    md: 'px-4 py-2 text-sm rounded-xl gap-2',
    lg: 'px-6 py-3 text-base rounded-xl gap-2.5',
  }

  return (
    <motion.button
      whileHover={{ scale: disabled ? 1 : 1.02 }}
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      className={cn(
        'relative inline-flex items-center justify-center font-medium',
        'transition-all duration-200',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        variants[variant],
        sizes[size],
        className
      )}
      disabled={disabled || loading}
      {...props}
    >
      {/* 光效 */}
      {variant === 'primary' && !disabled && (
        <span className="absolute inset-0 overflow-hidden rounded-xl">
          <span
            className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full hover:translate-x-full transition-transform duration-700"
          />
        </span>
      )}

      {/* Loading 狀態 */}
      {loading && (
        <svg
          className="animate-spin h-4 w-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
          />
        </svg>
      )}

      {/* 圖標 */}
      {!loading && icon && <span className="flex-shrink-0">{icon}</span>}

      {/* 文字 */}
      <span className="relative z-10">{children}</span>
    </motion.button>
  )
}

// =============================================
// 6. 全息標籤 (HoloBadge)
// 帶有微光效果的標籤
// =============================================

interface HoloBadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info'
  size?: 'sm' | 'md'
  pulse?: boolean
}

export function HoloBadge({
  children,
  variant = 'default',
  size = 'md',
  pulse = false,
}: HoloBadgeProps) {
  const variants = {
    default: 'bg-slate-100 text-slate-600 border-slate-200',
    success: 'bg-emerald-50 text-emerald-600 border-emerald-200',
    warning: 'bg-amber-50 text-amber-600 border-amber-200',
    error: 'bg-red-50 text-red-600 border-red-200',
    info: 'bg-cyan-50 text-cyan-600 border-cyan-200',
  }

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
  }

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full font-medium border',
        variants[variant],
        sizes[size],
        pulse && 'animate-pulse'
      )}
    >
      {children}
    </span>
  )
}

// =============================================
// 7. 科技感分隔線 (TechDivider)
// =============================================

interface TechDividerProps {
  className?: string
  label?: string
}

export function TechDivider({ className, label }: TechDividerProps) {
  return (
    <div className={cn('relative flex items-center', className)}>
      <div className="flex-grow h-px bg-gradient-to-r from-transparent via-cyan-300/50 to-transparent" />
      {label && (
        <>
          <span className="mx-4 text-xs font-medium text-slate-400 uppercase tracking-wider">
            {label}
          </span>
          <div className="flex-grow h-px bg-gradient-to-r from-transparent via-cyan-300/50 to-transparent" />
        </>
      )}
      {/* 裝飾點 */}
      <div className="absolute left-1/2 -translate-x-1/2 w-1 h-1 bg-cyan-400 rounded-full" />
    </div>
  )
}

// =============================================
// 8. 頁面入場動畫容器 (PageTransition)
// =============================================

interface PageTransitionProps {
  children: React.ReactNode
  className?: string
}

export function PageTransition({ children, className }: PageTransitionProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{
        duration: 0.5,
        ease: [0.22, 1, 0.36, 1],
      }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

// =============================================
// 9. 交錯動畫容器 (StaggerContainer)
// 子元素依次入場
// =============================================

interface StaggerContainerProps {
  children: React.ReactNode
  className?: string
  staggerDelay?: number
}

export function StaggerContainer({
  children,
  className,
  staggerDelay = 0.1,
}: StaggerContainerProps) {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        visible: {
          transition: {
            staggerChildren: staggerDelay,
          },
        },
      }}
      className={className}
    >
      {React.Children.map(children, (child) => (
        <motion.div
          variants={{
            hidden: { opacity: 0, y: 20 },
            visible: { opacity: 1, y: 0 },
          }}
          transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
        >
          {child}
        </motion.div>
      ))}
    </motion.div>
  )
}

// =============================================
// 10. 全息面板標題 (HoloPanelHeader)
// =============================================

interface HoloPanelHeaderProps {
  title: string
  subtitle?: string
  icon?: React.ReactNode
  action?: React.ReactNode
}

export function HoloPanelHeader({ title, subtitle, icon, action }: HoloPanelHeaderProps) {
  return (
    <div className="flex items-center justify-between p-4 border-b border-slate-100/80">
      <div className="flex items-center gap-3">
        {icon && (
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-50 to-blue-50 flex items-center justify-center text-cyan-600">
            {icon}
          </div>
        )}
        <div>
          <h3 className="font-semibold text-slate-800">{title}</h3>
          {subtitle && <p className="text-sm text-slate-500">{subtitle}</p>}
        </div>
      </div>
      {action}
    </div>
  )
}

// =============================================
// 11. 懸浮工具提示 (HoloTooltip)
// =============================================

interface HoloTooltipProps {
  children: React.ReactNode
  content: string
  position?: 'top' | 'bottom' | 'left' | 'right'
}

export function HoloTooltip({ children, content, position = 'top' }: HoloTooltipProps) {
  const [isVisible, setIsVisible] = useState(false)

  const positions = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2',
  }

  return (
    <div
      className="relative inline-block"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      <AnimatePresence>
        {isVisible && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className={cn(
              'absolute z-50 px-3 py-1.5 text-xs font-medium',
              'bg-slate-800 text-white rounded-lg shadow-lg',
              'whitespace-nowrap',
              positions[position]
            )}
          >
            {content}
            {/* 箭頭 */}
            <div
              className={cn(
                'absolute w-2 h-2 bg-slate-800 rotate-45',
                position === 'top' && 'top-full left-1/2 -translate-x-1/2 -mt-1',
                position === 'bottom' && 'bottom-full left-1/2 -translate-x-1/2 -mb-1',
                position === 'left' && 'left-full top-1/2 -translate-y-1/2 -ml-1',
                position === 'right' && 'right-full top-1/2 -translate-y-1/2 -mr-1'
              )}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// =============================================
// 12. 進度環 (ProgressRing)
// =============================================

interface ProgressRingProps {
  progress: number
  size?: number
  strokeWidth?: number
  color?: 'cyan' | 'blue' | 'green' | 'purple'
  showLabel?: boolean
}

export function ProgressRing({
  progress,
  size = 60,
  strokeWidth = 4,
  color = 'cyan',
  showLabel = true,
}: ProgressRingProps) {
  const radius = (size - strokeWidth) / 2
  const circumference = radius * 2 * Math.PI
  const offset = circumference - (progress / 100) * circumference

  const colors = {
    cyan: 'stroke-cyan-500',
    blue: 'stroke-blue-500',
    green: 'stroke-emerald-500',
    purple: 'stroke-violet-500',
  }

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        {/* 背景環 */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          fill="none"
          className="stroke-slate-100"
        />
        {/* 進度環 */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          fill="none"
          strokeLinecap="round"
          className={colors[color]}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
          style={{
            strokeDasharray: circumference,
          }}
        />
      </svg>
      {showLabel && (
        <span className="absolute text-sm font-bold text-slate-700">{Math.round(progress)}%</span>
      )}
    </div>
  )
}

// =============================================
// 13. 骨架屏 (HoloSkeleton)
// =============================================

interface HoloSkeletonProps {
  className?: string
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
}

export function HoloSkeleton({
  className,
  variant = 'rectangular',
  width,
  height,
}: HoloSkeletonProps) {
  const variants = {
    text: 'rounded h-4',
    circular: 'rounded-full',
    rectangular: 'rounded-xl',
  }

  return (
    <div
      className={cn(
        'bg-gradient-to-r from-slate-100 via-slate-50 to-slate-100 animate-shimmer',
        'bg-[length:200%_100%]',
        variants[variant],
        className
      )}
      style={{ width, height }}
    />
  )
}
