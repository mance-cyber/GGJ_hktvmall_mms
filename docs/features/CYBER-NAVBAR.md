# 🌌 全息賽博朋克導航欄

**Holographic Cyberpunk Navbar** - 一個獨特的未來科技風格導航組件

## ✨ 設計特色

### 核心美學
- **全息投影效果** - 動態掃描線動畫
- **霓虹光暈** - 互動式光效反饋
- **數據流背景** - 垂直流動的數據可視化
- **玻璃態材質** - 透明模糊背景
- **賽博網格** - 科技感網格背景

### 獨特之處
與常見的玻璃態導航欄不同，這個設計採用：
- ✅ **Orbitron + Rajdhani** 字體組合（非 Inter/Roboto）
- ✅ **電光藍 + 霓虹紫** 配色（非紫色漸變白底）
- ✅ **全息掃描線動畫**（非靜態玻璃效果）
- ✅ **動態數據流**（非單純背景模糊）
- ✅ **懸浮光暈交互**（非簡單 hover 效果）

---

## 📦 安裝使用

### 1. 安裝依賴

```bash
npm install framer-motion lucide-react clsx tailwind-merge
```

### 2. 複製文件

將以下文件複製到你的項目：

```
components/ui/CyberNavbar.tsx
styles/cyber-navbar.css
```

### 3. 導入樣式

在你的 `app/layout.tsx` 或主入口文件中導入樣式：

```tsx
import '@/styles/cyber-navbar.css'
```

或在需要的頁面中動態導入：

```tsx
<link rel="stylesheet" href="/styles/cyber-navbar.css" />
```

### 4. 使用組件

```tsx
import { CyberNavbar } from '@/components/ui/CyberNavbar'

export default function Page() {
  return (
    <>
      <CyberNavbar />
      {/* 你的頁面內容 */}
    </>
  )
}
```

---

## 🎨 自定義配置

### 修改導航項目

編輯 `CyberNavbar.tsx` 中的 `navItems` 數組：

```tsx
const navItems: NavItem[] = [
  { label: 'Home', href: '/', icon: Home },
  { label: 'Products', href: '/products', icon: Package },
  { label: 'About', href: '/about', icon: Info },
  // 添加更多項目...
]
```

### 自定義配色

修改 `tailwind.config.ts`：

```typescript
theme: {
  extend: {
    colors: {
      cyber: {
        primary: '#00f0ff',    // 電光藍
        accent: '#b537ff',     // 霓虹紫
        glow: '#ff2e97',       // 霓虹粉（可選）
      },
    },
  },
}
```

或直接在 CSS 中修改：

```css
/* styles/cyber-navbar.css */
:root {
  --cyber-primary: #00f0ff;
  --cyber-accent: #b537ff;
  --cyber-glow: rgba(0, 240, 255, 0.5);
}
```

### 調整動畫速度

在 `CyberNavbar.tsx` 中修改動畫參數：

```tsx
// 掃描線速度
<motion.div
  animate={{ y: ['-100%', '200%'] }}
  transition={{
    duration: 3,  // 改為 2 讓動畫更快
    repeat: Infinity,
  }}
/>

// 數據流速度
transition={{
  duration: 2 + i * 0.5,  // 調整基礎速度
  repeat: Infinity,
}
```

### 禁用特定效果

```tsx
// 禁用掃描線
{/* <motion.div className="scan-line" /> */}

// 禁用數據流
{/* <DataFlow /> */}

// 禁用網格背景
{/* <div className="cyber-grid" /> */}
```

---

## 🚀 進階功能

### 添加搜索框

```tsx
<div className="flex items-center gap-3">
  {/* 搜索框 */}
  <div className="relative">
    <input
      type="search"
      placeholder="Search..."
      className="px-4 py-2 rounded-lg bg-slate-900/50 border border-cyan-500/30 text-white placeholder:text-slate-500 focus:border-cyan-500/50 focus:outline-none"
    />
    <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
  </div>

  {/* 原有的按鈕... */}
</div>
```

### 添加子菜單

```tsx
interface NavItem {
  label: string
  href: string
  icon: React.ElementType
  children?: NavItem[]  // 添加子菜單
}

// 在 NavLink 組件中添加下拉邏輯
function NavLink({ item }: NavLinkProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div
      onMouseEnter={() => setIsOpen(true)}
      onMouseLeave={() => setIsOpen(false)}
    >
      {/* 主菜單 */}
      <a href={item.href}>{item.label}</a>

      {/* 子菜單 */}
      {item.children && isOpen && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute top-full left-0 mt-2 p-2 rounded-lg bg-slate-950/95 backdrop-blur-xl border border-cyan-500/30"
        >
          {item.children.map(child => (
            <a key={child.href} href={child.href}>
              {child.label}
            </a>
          ))}
        </motion.div>
      )}
    </div>
  )
}
```

### 滾動進度條

```tsx
import { useScroll, useTransform, motion } from 'framer-motion'

function ScrollProgress() {
  const { scrollYProgress } = useScroll()
  const scaleX = useTransform(scrollYProgress, [0, 1], [0, 1])

  return (
    <motion.div
      style={{ scaleX }}
      className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-cyan-500 to-purple-600 origin-left"
    />
  )
}

// 在 CyberNavbar 中添加
<ScrollProgress />
```

---

## ♿ 可訪問性

### 內建功能
- ✅ **鍵盤導航** - 完整支持 Tab 導航
- ✅ **ARIA 標籤** - 適當的語義化標記
- ✅ **高對比度** - 符合 WCAG AA 標準
- ✅ **減少動畫** - 尊重 `prefers-reduced-motion`

### 測試清單

```bash
# 使用 axe DevTools 測試
npm install -D @axe-core/react

# 鍵盤測試
- Tab: 導航到下一個元素
- Shift+Tab: 導航到上一個元素
- Enter/Space: 激活按鈕
- Escape: 關閉移動菜單

# 螢幕閱讀器測試
- NVDA (Windows)
- JAWS (Windows)
- VoiceOver (Mac/iOS)
```

---

## 📊 性能優化

### 已實施優化

1. **CSS 動畫優先** - 使用 CSS transform 而非 JS
2. **條件渲染** - 移動菜單僅在需要時渲染
3. **Framer Motion 優化** - 使用 `layoutId` 減少重渲染
4. **背景效果分層** - 分離靜態和動態元素

### Lighthouse 分數目標

- **Performance**: 90+
- **Accessibility**: 100
- **Best Practices**: 95+
- **SEO**: 100

### 監控建議

```tsx
// 使用 React DevTools Profiler
import { Profiler } from 'react'

<Profiler id="CyberNavbar" onRender={onRenderCallback}>
  <CyberNavbar />
</Profiler>
```

---

## 🎯 最佳實踐

### ✅ 推薦做法

```tsx
// 1. 使用語義化 HTML
<nav aria-label="主導航">
  <ul role="list">...</ul>
</nav>

// 2. 適當的 loading 狀態
<button disabled={isLoading}>
  {isLoading ? <Loader /> : 'ACTIVATE'}
</button>

// 3. 錯誤邊界
<ErrorBoundary fallback={<NavbarFallback />}>
  <CyberNavbar />
</ErrorBoundary>
```

### ❌ 避免做法

```tsx
// 1. 過度使用動畫（影響性能）
❌ animate={{ rotate: [0, 360], scale: [1, 2, 1] }}

// 2. 內聯樣式（難以維護）
❌ style={{ background: 'linear-gradient(...)' }}

// 3. 硬編碼值（缺乏彈性）
❌ const items = ['Home', 'About', 'Contact']
✅ const items = navItems.map(...)
```

---

## 🐛 疑難排解

### 字體未加載

**問題**: Orbitron/Rajdhani 字體顯示為系統字體

**解決方案**:
```tsx
// 確保 CSS 已導入
import '@/styles/cyber-navbar.css'

// 或使用 Next.js 字體優化
import { Orbitron, Rajdhani } from 'next/font/google'

const orbitron = Orbitron({ subsets: ['latin'] })
const rajdhani = Rajdhani({ weight: ['300', '400', '500', '600', '700'], subsets: ['latin'] })
```

### 動畫卡頓

**問題**: 掃描線或數據流動畫不流暢

**解決方案**:
```tsx
// 1. 減少動畫元素數量
const lines = Array.from({ length: 3 })  // 從 5 減到 3

// 2. 使用 CSS will-change
.scan-line {
  will-change: transform;
}

// 3. 啟用硬件加速
transform: translateZ(0);
```

### 移動端菜單不關閉

**問題**: 點擊鏈接後菜單仍然打開

**解決方案**:
```tsx
onClick={() => {
  setActiveIndex(index)
  setIsMobileOpen(false)  // 確保關閉菜單
}}
```

---

## 📱 響應式設計

### 斷點說明

```css
/* Mobile First 方法 */
/* xs: < 640px  - 默認 */
/* sm: 640px   - 小平板 */
/* md: 768px   - 平板 */
/* lg: 1024px  - 桌面 */
/* xl: 1280px  - 大桌面 */
```

### 移動端優化

```tsx
// 1. 觸摸優化
<button className="touch-none select-none">

// 2. 適當的點擊區域 (44x44 最小)
<button className="min-h-[44px] min-w-[44px]">

// 3. 禁用縮放（如需要）
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
```

---

## 🔗 相關資源

- [Framer Motion 文檔](https://www.framer.com/motion/)
- [Tailwind CSS 文檔](https://tailwindcss.com/docs)
- [WCAG 2.1 指南](https://www.w3.org/WAI/WCAG21/quickref/)
- [Google Fonts](https://fonts.google.com/)
- [Lucide Icons](https://lucide.dev/)

---

## 📄 授權

MIT License - 自由使用、修改和分發

---

**創建於**: 2026-01-12
**版本**: 1.0.0
**作者**: Frontend Design Agent
**風格**: Cyberpunk Holographic
