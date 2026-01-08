# GoGoJap 設計 Token 快速參考

> 快速查閱設計系統中的所有設計 Token，方便開發時直接複製使用

## 色彩 Token

### 主色系
```
品牌主色：bg-brand-primary-600 (#1570EF)
品牌輔助色：bg-brand-secondary-600 (#4F46E5)
```

### 功能色
```
成功：bg-success-600 (#059669) | text-success-700
警告：bg-warning-600 (#D97706) | text-warning-700
錯誤：bg-error-600 (#DC2626) | text-error-700
資訊：bg-info-600 (#2563EB) | text-info-700
```

### 文字顏色
```
主要文字：text-gray-900
次要文字：text-gray-600
輔助文字：text-gray-500
禁用文字：text-gray-400
```

### 背景顏色
```
頁面背景：bg-gray-50
卡片背景：bg-white
次要背景：bg-gray-100
禁用背景：bg-gray-200
```

### 邊框顏色
```
預設邊框：border-gray-200
強調邊框：border-gray-300
主色邊框：border-brand-primary-600
錯誤邊框：border-error-500
```

### 圖表配色（按順序使用）
```css
1. text-[#2E90FA] /* 藍色 - 主要數據 */
2. text-[#7C3AED] /* 紫色 - 次要數據 */
3. text-[#14B8A6] /* 青色 - 第三數據 */
4. text-[#F97316] /* 橙色 - 對比數據 */
5. text-[#EC4899] /* 粉色 - 強調數據 */
```

---

## 字型 Token

### 字體家族
```
無襯線：font-sans
等寬字體：font-mono
數字字體：font-numeric
```

### 字級大小
```
Display 層級（營銷用）
text-display-2xl (72px) - 極少使用
text-display-xl (60px)
text-display-lg (48px)

標題層級
text-h1 (36px) - 頁面標題
text-h2 (30px) - 主要區塊標題
text-h3 (24px) - 次要區塊標題
text-h4 (20px) - 卡片標題
text-h5 (18px) - 小標題

內文層級
text-xl (20px) - 強調內文
text-lg (18px) - 大號內文
text-base (16px) - 標準內文（預設）
text-sm (14px) - 小號內文、UI 元素
text-xs (12px) - 輔助文字、標籤
text-caption (11px) - 極小文字
```

### 字重
```
font-light (300) - 裝飾性大標題
font-regular (400) - 內文
font-medium (500) - UI 元素、按鈕
font-semibold (600) - 小標題
font-bold (700) - 主標題
```

---

## 間距 Token

### Padding / Margin
```
p-0 / m-0 (0px)
p-1 / m-1 (4px) - 最小間距
p-2 / m-2 (8px) - 緊湊間距
p-3 / m-3 (12px)
p-4 / m-4 (16px) - 標準間距
p-5 / m-5 (20px)
p-6 / m-6 (24px) - 卡片內距
p-8 / m-8 (32px) - 區塊間距
p-10 / m-10 (40px)
p-12 / m-12 (48px) - 大區塊間距
p-16 / m-16 (64px)
p-20 / m-20 (80px)
p-24 / m-24 (96px)
```

### Gap（Flexbox / Grid）
```
gap-1 (4px)
gap-2 (8px)
gap-3 (12px)
gap-4 (16px) - 常用
gap-6 (24px) - 卡片間距
gap-8 (32px)
```

### 使用建議
```
組件內小元素：p-1, p-2, gap-1, gap-2
組件內容：p-4, p-5, p-6
組件間距：gap-4, gap-6
區塊間距：mb-8, mb-12
頁面邊距：px-6 py-8 (手機) | px-12 py-12 (桌面)
```

---

## 圓角 Token

```
rounded-none (0px) - 直角
rounded-sm (4px) - 徽章、標籤
rounded (6px) - 按鈕、輸入框（預設）
rounded-md (8px) - 卡片
rounded-lg (12px) - 大卡片、面板
rounded-xl (16px) - 模態框
rounded-2xl (24px) - 浮動卡片
rounded-full (9999px) - 圓形按鈕、頭像
```

---

## 陰影 Token

```
shadow-xs - 極淺陰影，微互動
shadow-sm - 標準卡片
shadow-md - 懸浮卡片
shadow-lg - 下拉選單、彈窗
shadow-xl - 模態框
shadow-2xl - 全屏覆蓋層
shadow-inner - 內陰影（凹陷效果）
shadow-outline - 焦點狀態（藍色）
shadow-outline-error - 錯誤焦點（紅色）
```

---

## 動畫 Token

### 時長
```
duration-instant (100ms) - 即時反饋
duration-fast (150ms) - 快速互動
duration-base (200ms) - 標準動畫（預設）
duration-slow (300ms) - 複雜轉場
duration-slower (500ms) - 頁面級轉場
```

### 緩動函數
```
ease-linear - 線性（進度條）
ease-in - 加速進入
ease-out - 減速退出（最常用）
ease-in-out - 先加速後減速（標準）
ease-bounce - 彈跳效果
```

### 預設動畫類別
```
animate-fade-in - 淡入
animate-fade-out - 淡出
animate-slide-in-up - 從下滑入
animate-slide-in-down - 從上滑入
animate-scale-in - 縮放進入
animate-pulse - 脈衝（載入中）
animate-spin - 旋轉（載入指示器）
```

---

## 斷點 Token

```
預設（0px）- 手機直式
sm (640px) - 手機橫式、小平板
md (768px) - 平板
lg (1024px) - 筆電
xl (1280px) - 桌機
2xl (1536px) - 大螢幕
```

### 使用範例
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  {/* 手機 1 列，平板 2 列，桌機 3 列 */}
</div>

<p className="text-sm md:text-base lg:text-lg">
  {/* 響應式文字大小 */}
</p>
```

---

## 常用組合類別

### 按鈕樣式
```tsx
// 主要按鈕
className="bg-brand-primary-600 text-white px-4 py-2 rounded-md
           hover:bg-brand-primary-700 transition-colors duration-fast
           focus:outline-none focus:ring-2 focus:ring-brand-primary-500"

// 次要按鈕
className="border-2 border-gray-300 text-gray-700 px-4 py-2 rounded-md
           hover:border-brand-primary-600 hover:bg-brand-primary-50
           transition-colors duration-fast"

// 危險按鈕
className="bg-error-600 text-white px-4 py-2 rounded-md
           hover:bg-error-700 transition-colors duration-fast"
```

### 卡片樣式
```tsx
// 標準卡片
className="bg-white border border-gray-200 rounded-md p-6
           shadow-sm hover:shadow-md transition-shadow duration-base"

// 數據卡片
className="bg-gray-50 rounded-md p-5"
```

### 輸入框樣式
```tsx
// 標準輸入框
className="w-full px-4 py-2 border border-gray-300 rounded-md
           focus:border-brand-primary-600 focus:ring-2
           focus:ring-brand-primary-500 focus:outline-none
           transition-all duration-fast"

// 錯誤狀態
className="...上面的類別... border-error-500 focus:ring-error-500"
```

### 表格樣式
```tsx
// 表頭
className="bg-gray-50 px-4 py-3 text-left text-sm font-semibold
           text-gray-700 border-b border-gray-200"

// 表格儲存格
className="px-4 py-3 text-sm text-gray-900 border-b border-gray-100"

// 數字儲存格
className="px-4 py-3 text-sm text-gray-900 text-right font-tabular"
```

### 徽章樣式
```tsx
// 成功徽章
className="inline-flex items-center px-2.5 py-0.5 rounded-sm
           text-xs font-medium bg-success-50 text-success-700"

// 警告徽章
className="inline-flex items-center px-2.5 py-0.5 rounded-sm
           text-xs font-medium bg-warning-50 text-warning-700"
```

---

## 佈局工具類別

### 容器
```tsx
// 頁面容器
className="max-w-7xl mx-auto px-6 py-8"

// 內容區塊
className="mb-8"

// 操作列
className="flex justify-between items-center mb-6"
```

### Flexbox
```tsx
// 水平置中
className="flex items-center justify-center"

// 左右分佈
className="flex justify-between items-center"

// 垂直排列
className="flex flex-col gap-4"

// 水平間距
className="flex gap-2"
```

### Grid
```tsx
// 響應式網格
className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"

// 自動填充
className="grid grid-cols-auto-fill gap-4"
```

---

## 狀態類別

### Hover
```
hover:bg-gray-100 - 背景變色
hover:text-brand-primary-600 - 文字變色
hover:shadow-md - 陰影增強
hover:scale-105 - 輕微放大
```

### Focus
```
focus:outline-none - 移除預設外框
focus:ring-2 - 焦點環
focus:ring-brand-primary-500 - 焦點環顏色
focus:border-brand-primary-600 - 邊框變色
```

### Active
```
active:bg-brand-primary-800 - 按下時的背景
active:scale-95 - 按下時縮小
```

### Disabled
```
disabled:opacity-50 - 半透明
disabled:cursor-not-allowed - 禁用游標
disabled:bg-gray-300 - 禁用背景
```

---

## 工具類別

### 文字處理
```
truncate - 單行截斷
line-clamp-2 - 兩行截斷
break-words - 自動換行
whitespace-nowrap - 不換行
```

### 可見性
```
hidden - 完全隱藏
invisible - 不可見但佔空間
sr-only - 僅螢幕閱讀器可見
```

### 響應式顯示
```
hidden md:block - 桌面顯示
block md:hidden - 手機顯示
```

### 定位
```
relative - 相對定位
absolute - 絕對定位
fixed - 固定定位
sticky - 黏性定位
z-10 - 層級
```

---

## 快速複製範本

### 頁面標題區
```tsx
<div className="mb-8">
  <h1 className="text-h1 font-bold text-gray-900 mb-2">頁面標題</h1>
  <p className="text-lg text-gray-600">頁面描述文字</p>
</div>
```

### 統計卡片
```tsx
<div className="bg-white border border-gray-200 rounded-md p-5 shadow-sm">
  <p className="text-sm font-medium text-gray-600 mb-2">指標名稱</p>
  <p className="text-h2 font-bold text-gray-900 font-tabular">1,234</p>
  <div className="mt-2 flex items-center gap-1 text-sm">
    <TrendingUp className="h-4 w-4 text-success-600" />
    <span className="text-success-600 font-medium">+12.5%</span>
    <span className="text-gray-500">較上月</span>
  </div>
</div>
```

### 搜尋列
```tsx
<div className="flex gap-2">
  <Input
    type="search"
    placeholder="搜尋..."
    className="w-[300px]"
  />
  <Button variant="outline">
    <Filter className="mr-2 h-4 w-4" />
    篩選
  </Button>
</div>
```

### 表格包裝器
```tsx
<div className="bg-white border border-gray-200 rounded-md overflow-hidden shadow-sm">
  <Table>
    {/* 表格內容 */}
  </Table>
</div>
```

### 空狀態
```tsx
<div className="flex flex-col items-center justify-center py-12 px-4 text-center">
  <IconComponent className="w-12 h-12 mb-4 text-gray-400" />
  <h3 className="text-lg font-semibold text-gray-900 mb-2">空狀態標題</h3>
  <p className="text-sm text-gray-500 max-w-md mb-4">描述文字</p>
  <Button>行動按鈕</Button>
</div>
```

---

## 數字格式化參考

### 貨幣格式
```tsx
// 使用工具函數
import { formatCurrency } from "@/lib/utils";

formatCurrency(1234.56)  // "HK$ 1,234.56"
formatCurrency(1234.56, 'USD')  // "US$ 1,234.56"
```

### 數量格式
```tsx
import { formatNumber } from "@/lib/utils";

formatNumber(1234567)  // "1,234,567"
```

### 百分比格式
```tsx
import { formatPercent } from "@/lib/utils";

formatPercent(0.1234)  // "+12.34%"
formatPercent(-0.056)  // "-5.60%"
```

### 日期格式
```tsx
import { format } from "date-fns";
import { zhTW } from "date-fns/locale";

format(new Date(), 'PPP', { locale: zhTW })  // "2026年1月5日"
format(new Date(), 'yyyy-MM-dd')  // "2026-01-05"
```

---

## 圖標使用指南

### 推薦圖標庫
```bash
npm install lucide-react
```

### 常用圖標
```tsx
import {
  // 導航
  Home, Settings, User, LogOut,

  // 操作
  Plus, Edit, Trash2, Save, X, Check,

  // 狀態
  AlertCircle, CheckCircle, Info, AlertTriangle,

  // 趨勢
  TrendingUp, TrendingDown, Minus,

  // 通用
  Search, Filter, ChevronDown, ChevronRight,
  Download, Upload, Calendar, Clock,
} from "lucide-react";
```

### 圖標尺寸
```tsx
<Icon className="h-3 w-3" />  // 小型（內聯文字）
<Icon className="h-4 w-4" />  // 標準（按鈕、標籤）
<Icon className="h-5 w-5" />  // 中型（導航）
<Icon className="h-6 w-6" />  // 大型（頁面元素）
<Icon className="h-12 w-12" /> // 特大（空狀態）
```

---

**提示**:
- 優先使用 Tailwind 類別而非內聯樣式
- 保持設計 Token 的一致性
- 遇到特殊需求時參考完整的 `BRAND_GUIDELINES.md`
- 使用 `font-tabular` 類別確保數字對齊

**維護者**: GoGoJap 開發團隊
**最後更新**: 2026-01-05
