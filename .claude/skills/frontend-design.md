---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, or applications. Generates creative, polished code that avoids generic AI aesthetics.
category: Design & Development
tags:
  - frontend
  - ui-ux
  - react
  - tailwindcss
  - design-system
  - accessibility
pairs-with:
  - skill: testing-patterns
    reason: Ensure components are testable
  - skill: systematic-debugging
    reason: Debug UI rendering issues
---

# Frontend Design Expert

**Role**: 資深前端設計工程師 (10+ 年經驗)
**Specialty**: 科技感未來風格的 React + Tailwind CSS 實現
**Mission**: 將設計概念轉化為高質量、可訪問、可維護的前端代碼

## 設計哲學

### 核心原則

1. **未來科技感美學**
   - 使用漸變、玻璃態、霓虹光效
   - 流暢的動畫和過渡效果
   - 深色優先的配色方案
   - 幾何形狀和抽象視覺元素

2. **功能優先於裝飾**
   - 每個設計元素都有明確目的
   - 視覺層級清晰
   - 減少認知負擔

3. **可訪問性第一**
   - WCAG 2.1 AA 標準
   - 鍵盤導航支持
   - 螢幕閱讀器友好
   - 適當的對比度和字體大小

4. **性能與體驗並重**
   - 優先使用 CSS 動畫而非 JS
   - 懶加載圖片和組件
   - 優化重渲染
   - 流暢的 60fps 體驗

## 核心能力

### 1. UI/UX 組件設計

**設計流程**:
```
需求理解 → 視覺設計 → 組件拆解 → 狀態管理 → 動畫設計 → 可訪問性 → 代碼實現
```

**科技感配色方案**:
```javascript
// Futuristic Tech Palette
const colors = {
  // Primary - Electric Blue
  primary: {
    50: '#e6f7ff',
    100: '#bae7ff',
    500: '#1890ff',
    600: '#096dd9',
    700: '#0050b3',
  },
  // Accent - Neon Purple
  accent: {
    50: '#f9f0ff',
    500: '#722ed1',
    600: '#531dab',
  },
  // Cyber - Neon Green
  cyber: {
    400: '#52c41a',
    500: '#73d13d',
  },
  // Glass - Translucent surfaces
  glass: 'rgba(255, 255, 255, 0.1)',
  glassBorder: 'rgba(255, 255, 255, 0.2)',
}
```

### 2. React + Tailwind 實現模式

#### 玻璃態效果 (Glassmorphism)
```tsx
// components/ui/GlassCard.tsx
import { cn } from '@/lib/utils'

interface GlassCardProps {
  children: React.ReactNode
  className?: string
  intensity?: 'light' | 'medium' | 'strong'
}

export function GlassCard({
  children,
  className,
  intensity = 'medium'
}: GlassCardProps) {
  const intensityClasses = {
    light: 'bg-white/5 backdrop-blur-sm',
    medium: 'bg-white/10 backdrop-blur-md',
    strong: 'bg-white/20 backdrop-blur-lg',
  }

  return (
    <div className={cn(
      // Glass effect
      intensityClasses[intensity],
      // Border with gradient
      'border border-white/20',
      'rounded-2xl',
      // Shadow
      'shadow-xl shadow-black/10',
      // Hover effect
      'transition-all duration-300',
      'hover:bg-white/15 hover:border-white/30',
      className
    )}>
      {children}
    </div>
  )
}
```

#### 霓虹按鈕效果
```tsx
// components/ui/NeonButton.tsx
import { ButtonHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

interface NeonButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'accent' | 'cyber'
  glow?: boolean
}

export function NeonButton({
  children,
  className,
  variant = 'primary',
  glow = true,
  ...props
}: NeonButtonProps) {
  const variants = {
    primary: 'bg-blue-500 hover:bg-blue-600 text-white',
    accent: 'bg-purple-500 hover:bg-purple-600 text-white',
    cyber: 'bg-green-500 hover:bg-green-600 text-black',
  }

  const glowClasses = glow ? {
    primary: 'shadow-[0_0_20px_rgba(59,130,246,0.5)] hover:shadow-[0_0_30px_rgba(59,130,246,0.7)]',
    accent: 'shadow-[0_0_20px_rgba(168,85,247,0.5)] hover:shadow-[0_0_30px_rgba(168,85,247,0.7)]',
    cyber: 'shadow-[0_0_20px_rgba(34,197,94,0.5)] hover:shadow-[0_0_30px_rgba(34,197,94,0.7)]',
  } : {}

  return (
    <button
      className={cn(
        'px-6 py-3 rounded-lg font-medium',
        'transition-all duration-300',
        'transform hover:scale-105 active:scale-95',
        variants[variant],
        glow && glowClasses[variant],
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}
```

#### 漸變文字效果
```tsx
// components/ui/GradientText.tsx
import { cn } from '@/lib/utils'

interface GradientTextProps {
  children: React.ReactNode
  className?: string
  from?: string
  to?: string
}

export function GradientText({
  children,
  className,
  from = 'from-blue-400',
  to = 'to-purple-600'
}: GradientTextProps) {
  return (
    <span className={cn(
      'bg-gradient-to-r bg-clip-text text-transparent',
      from,
      to,
      className
    )}>
      {children}
    </span>
  )
}

// Usage
<h1 className="text-5xl font-bold">
  <GradientText from="from-cyan-400" to="to-blue-600">
    Future Tech Platform
  </GradientText>
</h1>
```

#### 動畫卡片 (Framer Motion)
```tsx
// components/ui/AnimatedCard.tsx
'use client'

import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface AnimatedCardProps {
  children: React.ReactNode
  className?: string
  delay?: number
}

export function AnimatedCard({
  children,
  className,
  delay = 0
}: AnimatedCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.5,
        delay,
        ease: [0.25, 0.1, 0.25, 1] // Smooth easing
      }}
      whileHover={{
        scale: 1.02,
        transition: { duration: 0.2 }
      }}
      className={cn(
        'bg-gradient-to-br from-slate-900 to-slate-800',
        'border border-white/10',
        'rounded-xl p-6',
        'shadow-2xl',
        className
      )}
    >
      {children}
    </motion.div>
  )
}
```

### 3. 設計系統建議

#### Tailwind 配置 (tailwind.config.ts)
```typescript
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Futuristic palette
        neon: {
          blue: '#00d4ff',
          purple: '#b537ff',
          pink: '#ff2e97',
          green: '#00ff88',
        },
        cyber: {
          dark: '#0a0e1a',
          darker: '#050812',
        },
      },
      backgroundImage: {
        'cyber-grid': 'linear-gradient(rgba(0, 212, 255, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 212, 255, 0.1) 1px, transparent 1px)',
        'glow-radial': 'radial-gradient(circle, rgba(0, 212, 255, 0.15) 0%, transparent 70%)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'float': 'float 6s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 20px rgba(0, 212, 255, 0.5)' },
          '100%': { boxShadow: '0 0 30px rgba(0, 212, 255, 0.8)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}

export default config
```

#### 全局樣式 (globals.css)
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  /* Futuristic scrollbar */
  ::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }

  ::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.5);
  }

  ::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #00d4ff 0%, #b537ff 100%);
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #00e5ff 0%, #c847ff 100%);
  }

  /* Smooth transitions */
  * {
    @apply transition-colors duration-200;
  }

  /* Dark mode defaults */
  body {
    @apply bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950;
    @apply text-slate-100;
  }
}

@layer components {
  /* Glass panel effect */
  .glass-panel {
    @apply bg-white/5 backdrop-blur-md;
    @apply border border-white/10;
    @apply rounded-2xl;
    @apply shadow-xl shadow-black/20;
  }

  /* Cyber grid background */
  .cyber-grid {
    background-image:
      linear-gradient(rgba(0, 212, 255, 0.05) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 212, 255, 0.05) 1px, transparent 1px);
    background-size: 50px 50px;
  }

  /* Neon text */
  .neon-text {
    @apply text-transparent bg-clip-text;
    @apply bg-gradient-to-r from-cyan-400 via-blue-500 to-purple-600;
    text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
  }
}
```

### 4. 可訪問性檢查清單

#### ARIA 屬性
```tsx
// ✅ Good - Accessible button
<button
  aria-label="關閉對話框"
  aria-pressed={isOpen}
  onClick={handleClose}
>
  <X className="w-5 h-5" />
</button>

// ✅ Good - Accessible navigation
<nav aria-label="主導航">
  <ul role="list">
    <li><a href="/" aria-current="page">首頁</a></li>
    <li><a href="/about">關於</a></li>
  </ul>
</nav>

// ✅ Good - Form accessibility
<label htmlFor="email" className="sr-only">
  電子郵件
</label>
<input
  id="email"
  type="email"
  aria-required="true"
  aria-invalid={hasError}
  aria-describedby={hasError ? "email-error" : undefined}
/>
{hasError && (
  <p id="email-error" role="alert" className="text-red-500 text-sm">
    請輸入有效的電子郵件地址
  </p>
)}
```

#### 鍵盤導航
```tsx
// ✅ Good - Keyboard accessible modal
function Modal({ isOpen, onClose, children }: ModalProps) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      // Trap focus
      const focusableElements = modalRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      )
      const firstElement = focusableElements?.[0] as HTMLElement
      firstElement?.focus()
    }

    return () => document.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      ref={modalRef}
    >
      {children}
    </div>
  )
}
```

#### 顏色對比度
```tsx
// ✅ Good - High contrast for readability
<div className="bg-slate-900">
  <p className="text-slate-100"> {/* 17:1 contrast ratio */}
    主要內容文字
  </p>
  <p className="text-slate-400"> {/* 7:1 contrast ratio */}
    次要內容文字
  </p>
</div>

// ❌ Bad - Low contrast
<div className="bg-slate-800">
  <p className="text-slate-700"> {/* < 3:1 - fails WCAG */}
    難以閱讀的文字
  </p>
</div>
```

### 5. 代碼審查標準

#### Component Checklist
- [ ] **響應式設計**: 支持移動端、平板、桌面
- [ ] **可訪問性**: ARIA 標籤、鍵盤導航、對比度
- [ ] **性能**: 避免不必要的重渲染、優化圖片
- [ ] **可維護性**: 清晰的命名、適當的拆分
- [ ] **TypeScript**: 完整的類型定義
- [ ] **動畫**: 流暢的過渡效果（考慮 prefers-reduced-motion）
- [ ] **錯誤處理**: 優雅的降級和錯誤狀態

#### Performance Optimization
```tsx
// ✅ Good - Optimized component
import { memo } from 'react'
import dynamic from 'next/dynamic'

// Lazy load heavy components
const HeavyChart = dynamic(() => import('./HeavyChart'), {
  loading: () => <ChartSkeleton />,
  ssr: false, // Disable SSR for client-only components
})

// Memoize expensive components
const ExpensiveCard = memo(({ data }: Props) => {
  return <div>{/* render */}</div>
}, (prevProps, nextProps) => {
  // Custom comparison
  return prevProps.data.id === nextProps.data.id
})

// Use CSS transforms for animations (GPU accelerated)
<motion.div
  animate={{ x: 100 }}
  transition={{ type: 'spring' }}
  // ✅ Uses transform, not left/right
/>
```

## 質量標準

### Design Excellence
1. **視覺一致性**: 統一的間距、圓角、陰影系統
2. **動畫流暢**: 60fps，自然的緩動函數
3. **層級清晰**: 明確的視覺權重和信息架構
4. **細節打磨**: 微交互、hover 狀態、loading 狀態

### Code Quality
1. **類型安全**: 完整的 TypeScript 類型
2. **可複用性**: DRY 原則，適當的抽象
3. **可測試性**: 單元測試覆蓋關鍵邏輯
4. **文檔完整**: JSDoc 註釋、README、Storybook

### Accessibility
1. **WCAG 2.1 AA**: 最低標準
2. **鍵盤友好**: 所有功能可用鍵盤操作
3. **螢幕閱讀器**: 語義化 HTML、ARIA
4. **運動敏感**: 尊重 prefers-reduced-motion

## 使用示例

### 創建未來科技風格的儀表板

```tsx
// app/dashboard/page.tsx
'use client'

import { motion } from 'framer-motion'
import { GlassCard } from '@/components/ui/GlassCard'
import { NeonButton } from '@/components/ui/NeonButton'
import { GradientText } from '@/components/ui/GradientText'
import { BarChart3, TrendingUp, Users, Zap } from 'lucide-react'

export default function Dashboard() {
  const stats = [
    { label: '總用戶', value: '12.5K', icon: Users, change: '+12%' },
    { label: '總收入', value: '$45.2K', icon: TrendingUp, change: '+8%' },
    { label: '活躍率', value: '68%', icon: Zap, change: '+5%' },
    { label: '轉化率', value: '3.2%', icon: BarChart3, change: '+2%' },
  ]

  return (
    <div className="min-h-screen p-8 cyber-grid">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <h1 className="text-5xl font-bold mb-2">
          <GradientText from="from-cyan-400" to="to-blue-600">
            營運儀表板
          </GradientText>
        </h1>
        <p className="text-slate-400">實時數據分析與洞察</p>
      </div>

      {/* Stats Grid */}
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <GlassCard className="p-6 hover:scale-105 transition-transform">
              <div className="flex items-center justify-between mb-4">
                <stat.icon className="w-8 h-8 text-cyan-400" />
                <span className="text-green-400 text-sm font-medium">
                  {stat.change}
                </span>
              </div>
              <p className="text-3xl font-bold mb-1">{stat.value}</p>
              <p className="text-slate-400 text-sm">{stat.label}</p>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="max-w-7xl mx-auto flex gap-4">
        <NeonButton variant="primary" glow>
          查看報告
        </NeonButton>
        <NeonButton variant="accent">
          匯出數據
        </NeonButton>
      </div>
    </div>
  )
}
```

## 反模式警示

### ❌ 過度裝飾
```tsx
// Bad - 太多視覺效果影響可讀性
<div className="bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500
                animate-pulse shadow-2xl border-4 border-yellow-400
                transform rotate-3 skew-x-12">
  <p className="text-6xl font-black animate-bounce">文字內容</p>
</div>
```

### ❌ 忽略可訪問性
```tsx
// Bad - 無法用鍵盤操作
<div onClick={handleClick} className="cursor-pointer">
  點擊我
</div>

// Good - 使用語義化元素
<button onClick={handleClick} className="...">
  點擊我
</button>
```

### ❌ 性能問題
```tsx
// Bad - 每次渲染都創建新對象
{items.map(item => (
  <Component
    style={{ color: 'red' }} // ❌ 每次新對象
    data={item}
  />
))}

// Good - 使用 CSS 類或 memo
const itemStyle = { color: 'red' } // ✅ 單一引用
{items.map(item => <Component style={itemStyle} data={item} />)}
```

## 工具推薦

- **UI 組件庫**: shadcn/ui (可自定義的 Tailwind 組件)
- **動畫**: Framer Motion (聲明式動畫)
- **圖標**: Lucide React (現代化圖標庫)
- **配色工具**: [Coolors](https://coolors.co/) (生成配色方案)
- **對比度檢查**: [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- **可訪問性測試**: axe DevTools (瀏覽器擴展)

---

**核心洞察**: 優秀的前端設計不只是好看，而是**美學、功能、可訪問性的完美平衡**。科技感來自於**精心設計的細節和流暢的體驗**，而非堆砌視覺效果。
