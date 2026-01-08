# GoGoJap - HKTVmall AI 營運系統品牌指南

## 品牌核心

### 品牌定位
GoGoJap 是 HKTVmall 的智能營運中樞，專為專業營運團隊打造的 AI 驅動管理平台。

### 品牌個性
- **專業 Professional**: 企業級可靠性，精準數據驅動決策
- **高效 Efficient**: 自動化工作流，減少重複勞動
- **智能 Intelligent**: AI 賦能，提供洞察與建議
- **可靠 Trustworthy**: 穩定系統，準確數據，安心使用

### 品牌價值主張
「讓數據說話，讓 AI 賦能，讓營運更簡單」

---

## 視覺識別系統

### 1. 色彩系統

#### 主色系 Primary Colors
```css
/* 品牌藍 - 專業、信賴、科技感 */
--brand-primary-50: #EBF5FF;
--brand-primary-100: #D1E9FF;
--brand-primary-200: #B3DDFF;
--brand-primary-300: #84CAFF;
--brand-primary-400: #53B1FD;
--brand-primary-500: #2E90FA;  /* 主色 */
--brand-primary-600: #1570EF;
--brand-primary-700: #175CD3;
--brand-primary-800: #1849A9;
--brand-primary-900: #194185;

/* 品牌深藍 - 專業權威 */
--brand-secondary-50: #F0F3FF;
--brand-secondary-100: #E0E7FF;
--brand-secondary-200: #C7D2FE;
--brand-secondary-300: #A5B4FC;
--brand-secondary-400: #818CF8;
--brand-secondary-500: #6366F1;
--brand-secondary-600: #4F46E5;  /* 輔助色 */
--brand-secondary-700: #4338CA;
--brand-secondary-800: #3730A3;
--brand-secondary-900: #312E81;
```

#### 功能色系 Functional Colors
```css
/* 成功 - 價格優勢、操作完成 */
--success-50: #ECFDF5;
--success-100: #D1FAE5;
--success-500: #10B981;
--success-600: #059669;
--success-700: #047857;

/* 警告 - 價格接近、需關注 */
--warning-50: #FFFBEB;
--warning-100: #FEF3C7;
--warning-500: #F59E0B;
--warning-600: #D97706;
--warning-700: #B45309;

/* 危險 - 價格劣勢、錯誤 */
--error-50: #FEF2F2;
--error-100: #FEE2E2;
--error-500: #EF4444;
--error-600: #DC2626;
--error-700: #B91C1C;

/* 資訊 - AI 建議、系統提示 */
--info-50: #EFF6FF;
--info-100: #DBEAFE;
--info-500: #3B82F6;
--info-600: #2563EB;
--info-700: #1D4ED8;
```

#### 中性色系 Neutral Colors
```css
/* 灰階 - 文字、背景、邊框 */
--gray-50: #F9FAFB;   /* 淺背景 */
--gray-100: #F3F4F6;  /* 卡片背景 */
--gray-200: #E5E7EB;  /* 分隔線 */
--gray-300: #D1D5DB;  /* 禁用狀態 */
--gray-400: #9CA3AF;  /* 輔助文字 */
--gray-500: #6B7280;  /* 次要文字 */
--gray-600: #4B5563;  /* 常規文字 */
--gray-700: #374151;  /* 標題文字 */
--gray-800: #1F2937;  /* 主標題 */
--gray-900: #111827;  /* 強調標題 */

/* 白色與黑色 */
--white: #FFFFFF;
--black: #000000;
```

#### 數據可視化配色 Data Visualization Palette
```css
/* 主要數據系列 - 和諧且易辨識 */
--chart-blue: #2E90FA;      /* 主要數據 */
--chart-purple: #7C3AED;    /* 次要數據 */
--chart-teal: #14B8A6;      /* 第三數據 */
--chart-orange: #F97316;    /* 對比數據 */
--chart-pink: #EC4899;      /* 強調數據 */
--chart-green: #10B981;     /* 正向指標 */
--chart-red: #EF4444;       /* 負向指標 */
--chart-amber: #F59E0B;     /* 中性指標 */

/* 漸變色 - 用於熱力圖、進度條 */
--gradient-cool: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
--gradient-warm: linear-gradient(135deg, #F093FB 0%, #F5576C 100%);
--gradient-success: linear-gradient(135deg, #4ADE80 0%, #22C55E 100%);
--gradient-primary: linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%);
```

### 2. 字型系統

#### 字體家族
```css
/* 系統字體堆疊 - 優先支援繁體中文 */
--font-sans:
  'Noto Sans TC',           /* 繁體中文主力 */
  'PingFang TC',            /* macOS 繁中 */
  'Microsoft JhengHei',     /* Windows 繁中 */
  -apple-system,
  BlinkMacSystemFont,
  'Segoe UI',
  'Roboto',
  'Helvetica Neue',
  Arial,
  sans-serif;

/* 等寬字體 - 代碼、數據 */
--font-mono:
  'JetBrains Mono',
  'SF Mono',
  'Consolas',
  'Liberation Mono',
  'Menlo',
  monospace;

/* 數字字體 - 表格、圖表 */
--font-numeric:
  'Roboto Mono',
  'SF Mono',
  monospace;
```

#### 字級階層 Type Scale
```css
/* Display - 僅用於營銷頁面 */
--text-display-2xl: 72px;  /* Line height: 90px */
--text-display-xl: 60px;   /* Line height: 72px */
--text-display-lg: 48px;   /* Line height: 60px */

/* Heading - 標題層級 */
--text-h1: 36px;  /* Line height: 44px, Weight: 700 */
--text-h2: 30px;  /* Line height: 38px, Weight: 600 */
--text-h3: 24px;  /* Line height: 32px, Weight: 600 */
--text-h4: 20px;  /* Line height: 28px, Weight: 600 */
--text-h5: 18px;  /* Line height: 26px, Weight: 500 */

/* Body - 內文 */
--text-xl: 20px;   /* Line height: 30px */
--text-lg: 18px;   /* Line height: 28px */
--text-base: 16px; /* Line height: 24px - 預設 */
--text-sm: 14px;   /* Line height: 20px */
--text-xs: 12px;   /* Line height: 18px */

/* Caption - 輔助文字 */
--text-caption: 11px; /* Line height: 16px */
```

#### 字重 Font Weights
```css
--font-light: 300;     /* 僅用於大標題裝飾 */
--font-regular: 400;   /* 內文 */
--font-medium: 500;    /* UI 元素、按鈕 */
--font-semibold: 600;  /* 小標題 */
--font-bold: 700;      /* 主標題 */
```

### 3. 間距系統

#### 基礎單位
```css
--spacing-unit: 4px; /* 最小單位 */
```

#### 間距階層 Spacing Scale
```css
--spacing-0: 0px;
--spacing-1: 4px;    /* 0.25rem */
--spacing-2: 8px;    /* 0.5rem */
--spacing-3: 12px;   /* 0.75rem */
--spacing-4: 16px;   /* 1rem - 基準 */
--spacing-5: 20px;   /* 1.25rem */
--spacing-6: 24px;   /* 1.5rem */
--spacing-8: 32px;   /* 2rem */
--spacing-10: 40px;  /* 2.5rem */
--spacing-12: 48px;  /* 3rem */
--spacing-16: 64px;  /* 4rem */
--spacing-20: 80px;  /* 5rem */
--spacing-24: 96px;  /* 6rem */
```

#### 使用指南
- **組件內間距**: 4px, 8px, 12px, 16px
- **組件間距**: 16px, 24px, 32px
- **區塊間距**: 32px, 48px, 64px
- **頁面邊距**: 24px (mobile), 48px (desktop)

### 4. 圓角系統

```css
--radius-none: 0px;
--radius-sm: 4px;     /* 小元素：標籤、徽章 */
--radius-base: 6px;   /* 基準：按鈕、輸入框 */
--radius-md: 8px;     /* 中等：卡片 */
--radius-lg: 12px;    /* 大型：模態框 */
--radius-xl: 16px;    /* 特大：面板 */
--radius-2xl: 24px;   /* 超大：浮動卡片 */
--radius-full: 9999px; /* 圓形：頭像、圓形按鈕 */
```

### 5. 陰影系統

```css
/* 卡片陰影 */
--shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
--shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

/* 特殊陰影 */
--shadow-inner: inset 0 2px 4px 0 rgba(0, 0, 0, 0.05);
--shadow-outline: 0 0 0 3px rgba(46, 144, 250, 0.5); /* 焦點狀態 */
--shadow-outline-error: 0 0 0 3px rgba(239, 68, 68, 0.5);
```

### 6. 動畫系統

#### 時長 Duration
```css
--duration-instant: 100ms;  /* 即時反饋 */
--duration-fast: 150ms;     /* 快速互動 */
--duration-base: 200ms;     /* 標準動畫 */
--duration-slow: 300ms;     /* 複雜轉場 */
--duration-slower: 500ms;   /* 頁面級轉場 */
```

#### 緩動函數 Easing
```css
--ease-linear: linear;
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);      /* 最常用 */
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1); /* 標準 */
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

#### 動畫原則
1. **性能優先**: 僅動畫 `transform` 和 `opacity`
2. **避免過度**: 減少不必要的動畫干擾
3. **一致性**: 相同類型互動使用相同動畫
4. **可關閉**: 尊重 `prefers-reduced-motion`

---

## 組件風格指南

### 1. 按鈕 Buttons

#### 主要按鈕 Primary
```tsx
// 視覺特徵
background: var(--brand-primary-600);
color: white;
padding: 10px 18px;
border-radius: var(--radius-base);
font-weight: var(--font-medium);
transition: all var(--duration-fast) var(--ease-out);

// Hover
background: var(--brand-primary-700);
box-shadow: var(--shadow-sm);

// Active
background: var(--brand-primary-800);
transform: translateY(1px);

// Disabled
background: var(--gray-300);
cursor: not-allowed;
```

#### 次要按鈕 Secondary
```tsx
background: transparent;
color: var(--brand-primary-600);
border: 1.5px solid var(--gray-300);

// Hover
border-color: var(--brand-primary-600);
background: var(--brand-primary-50);
```

#### 危險按鈕 Danger
```tsx
background: var(--error-600);
color: white;

// Hover
background: var(--error-700);
```

#### 按鈕尺寸
```css
/* Small */
padding: 6px 12px;
font-size: var(--text-sm);
height: 32px;

/* Medium (預設) */
padding: 10px 18px;
font-size: var(--text-base);
height: 40px;

/* Large */
padding: 12px 24px;
font-size: var(--text-lg);
height: 48px;
```

### 2. 卡片 Cards

#### 標準卡片
```css
background: var(--white);
border: 1px solid var(--gray-200);
border-radius: var(--radius-md);
padding: var(--spacing-6);
box-shadow: var(--shadow-sm);
transition: box-shadow var(--duration-base) var(--ease-out);

/* Hover */
box-shadow: var(--shadow-md);
border-color: var(--gray-300);
```

#### 資訊卡片（數據展示）
```css
background: var(--gray-50);
border: none;
padding: var(--spacing-5);

/* 內部結構 */
.card-header {
  margin-bottom: var(--spacing-3);
  font-size: var(--text-sm);
  color: var(--gray-600);
}

.card-value {
  font-size: var(--text-h2);
  font-weight: var(--font-bold);
  color: var(--gray-900);
  font-family: var(--font-numeric);
}

.card-footer {
  margin-top: var(--spacing-2);
  font-size: var(--text-xs);
  color: var(--gray-500);
}
```

### 3. 表單元素 Form Elements

#### 輸入框 Input
```css
background: var(--white);
border: 1.5px solid var(--gray-300);
border-radius: var(--radius-base);
padding: 10px 14px;
font-size: var(--text-base);
color: var(--gray-900);
transition: all var(--duration-fast) var(--ease-out);

/* Focus */
border-color: var(--brand-primary-600);
box-shadow: var(--shadow-outline);
outline: none;

/* Error */
border-color: var(--error-500);
box-shadow: var(--shadow-outline-error);

/* Disabled */
background: var(--gray-100);
color: var(--gray-500);
cursor: not-allowed;
```

#### 標籤 Label
```css
font-size: var(--text-sm);
font-weight: var(--font-medium);
color: var(--gray-700);
margin-bottom: var(--spacing-2);
display: block;
```

#### 輔助文字 Helper Text
```css
font-size: var(--text-xs);
color: var(--gray-500);
margin-top: var(--spacing-1);

/* Error */
color: var(--error-600);
```

### 4. 表格 Tables

#### 標準表格
```css
.table-container {
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.table-header {
  background: var(--gray-50);
  border-bottom: 1px solid var(--gray-200);
  padding: var(--spacing-3) var(--spacing-4);
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--gray-700);
  text-align: left;
}

.table-cell {
  padding: var(--spacing-4);
  font-size: var(--text-sm);
  color: var(--gray-900);
  border-bottom: 1px solid var(--gray-100);
}

.table-row:hover {
  background: var(--gray-50);
}
```

#### 數據表格（價格監控）
```css
/* 數字對齊右側 */
.table-cell-numeric {
  text-align: right;
  font-family: var(--font-numeric);
  font-variant-numeric: tabular-nums;
}

/* 狀態標籤 */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}

.status-success {
  background: var(--success-50);
  color: var(--success-700);
}

.status-warning {
  background: var(--warning-50);
  color: var(--warning-700);
}

.status-danger {
  background: var(--error-50);
  color: var(--error-700);
}
```

### 5. 徽章與標籤 Badges & Tags

#### 徽章 Badge
```css
.badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  line-height: 1.5;
}

.badge-primary {
  background: var(--brand-primary-100);
  color: var(--brand-primary-700);
}

.badge-count {
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: var(--radius-full);
  background: var(--error-600);
  color: white;
  font-size: 11px;
  line-height: 20px;
  text-align: center;
}
```

### 6. 圖表樣式 Chart Styles

#### 通用圖表配置
```javascript
const chartConfig = {
  // 主題色
  colors: [
    'var(--chart-blue)',
    'var(--chart-purple)',
    'var(--chart-teal)',
    'var(--chart-orange)',
    'var(--chart-pink)',
  ],

  // 網格線
  grid: {
    stroke: 'var(--gray-200)',
    strokeDasharray: '3 3',
  },

  // 軸線
  axis: {
    stroke: 'var(--gray-300)',
    fontSize: 12,
    fontFamily: 'var(--font-sans)',
    fill: 'var(--gray-600)',
  },

  // 工具提示
  tooltip: {
    backgroundColor: 'var(--gray-900)',
    color: 'var(--white)',
    borderRadius: 'var(--radius-base)',
    padding: '8px 12px',
    fontSize: 'var(--text-sm)',
    boxShadow: 'var(--shadow-lg)',
  },

  // 圖例
  legend: {
    fontSize: 'var(--text-sm)',
    fontFamily: 'var(--font-sans)',
    fill: 'var(--gray-700)',
  },
};
```

#### 價格趨勢圖
```javascript
const priceChartConfig = {
  lineColors: {
    ownPrice: 'var(--brand-primary-600)',      // 自家價格
    competitorPrice: 'var(--chart-orange)',    // 競爭對手
    averagePrice: 'var(--gray-400)',           // 市場平均
  },

  lineWidth: 2,

  areaGradient: {
    start: 'rgba(46, 144, 250, 0.2)',
    end: 'rgba(46, 144, 250, 0)',
  },
};
```

---

## 品牌語調指南

### 語言原則
1. **清晰直接**: 避免模糊表達，使用具體數據
2. **專業友好**: 保持專業但不冷漠
3. **行動導向**: 明確下一步該做什麼
4. **尊重用戶時間**: 簡潔有力，不贅述

### 常見情境用語

#### 成功訊息
- ✅ 「已成功同步 1,234 件商品」
- ✅ 「價格更新完成，偵測到 5 項需關注變動」
- ❌ 「恭喜！您的操作已經成功了！」

#### 錯誤訊息
- ✅ 「無法連接到 HKTVmall API，請檢查網路連線」
- ✅ 「此商品 SKU 不存在，請確認後重試」
- ❌ 「糟糕！發生了一個錯誤」

#### 空狀態
- ✅ 「尚無價格警報，系統持續監控中」
- ✅ 「開始添加競爭對手以追蹤價格」
- ❌ 「這裡什麼都沒有」

#### AI 建議
- ✅ 「根據市場數據，建議將價格調整至 HK$XX」
- ✅ 「AI 分析：此商品描述可優化關鍵字密度」
- ❌ 「我覺得你應該...」

### 數據展示原則
1. **使用千分位**: 1,234 而非 1234
2. **明確單位**: HK$299、+15%、3,456 件
3. **趨勢標示**: ↑ 12.5%、↓ 3.2%
4. **時間範圍**: 最近 7 天、本月、過去 30 天

---

## 無障礙指南

### 色彩對比
- **正常文字**: 最小對比度 4.5:1 (WCAG AA)
- **大型文字**: 最小對比度 3:1 (18px+)
- **UI 元素**: 最小對比度 3:1

### 鍵盤導航
- 所有互動元素必須可通過 Tab 鍵訪問
- 焦點狀態必須清晰可見（使用 `--shadow-outline`）
- 提供鍵盤快捷鍵給常用功能

### 螢幕閱讀器
- 使用語義化 HTML 標籤
- 為圖示按鈕提供 `aria-label`
- 為複雜圖表提供文字描述

### 響應式設計
```css
/* 斷點 */
--breakpoint-sm: 640px;   /* 手機 */
--breakpoint-md: 768px;   /* 平板 */
--breakpoint-lg: 1024px;  /* 筆電 */
--breakpoint-xl: 1280px;  /* 桌機 */
--breakpoint-2xl: 1536px; /* 大螢幕 */
```

---

## 品牌資產管理

### 目錄結構
```
/public
  /brand
    /logos
      logo-primary.svg        # 主要標誌
      logo-icon.svg          # 圖標版本
      logo-white.svg         # 白色版本
    /icons
      /system               # 系統圖標
      /feature              # 功能圖標
    /illustrations
      empty-state.svg       # 空狀態插圖
      error-state.svg       # 錯誤狀態
  /images
    /screenshots            # 產品截圖
    /charts                # 圖表示例
```

### 檔案命名規範
```
格式: [類型]-[名稱]-[變體].[副檔名]

範例:
- logo-primary-color.svg
- icon-alert-filled.svg
- illustration-empty-dashboard.svg
- chart-price-trend-light.png
```

### Logo 使用規範

#### 最小尺寸
- **完整標誌**: 120px 寬度
- **圖標版本**: 24px × 24px

#### 安全空間
- 四周留白至少等於標誌高度的 25%

#### 禁止行為
- ❌ 拉伸或擠壓
- ❌ 改變顏色（僅允許主色、白色、黑色）
- ❌ 添加效果（陰影、漸變、外框）
- ❌ 旋轉或傾斜

---

## 實施檢查清單

### 設計階段
- [ ] 使用正確的色彩變數
- [ ] 遵循字型階層
- [ ] 應用統一間距系統
- [ ] 設置適當圓角與陰影
- [ ] 確保色彩對比度達標
- [ ] 包含所有互動狀態（hover, active, disabled）

### 開發階段
- [ ] 使用 CSS 變數而非硬編碼值
- [ ] 實現鍵盤導航
- [ ] 添加 ARIA 標籤
- [ ] 測試響應式佈局
- [ ] 驗證動畫性能
- [ ] 檢查 `prefers-reduced-motion`

### 內容階段
- [ ] 文案符合品牌語調
- [ ] 錯誤訊息清晰可行
- [ ] 數據格式一致
- [ ] 提供適當的空狀態指引

---

## 設計資源

### 推薦字體下載
- **Noto Sans TC**: [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Sans+TC)
- **JetBrains Mono**: [官網](https://www.jetbrains.com/lp/mono/)
- **Roboto Mono**: [Google Fonts](https://fonts.google.com/specimen/Roboto+Mono)

### 設計工具設定
- **Figma**: 使用 8px 網格系統
- **Sketch**: 安裝 Tailwind CSS 插件
- **Adobe XD**: 匯入設計系統 token

### 開發工具
- **shadcn/ui**: 預設組件符合本指南
- **Tailwind CSS**: 使用自訂配置檔
- **Radix UI**: 無障礙基礎組件

---

## 版本記錄

### v1.0.0 (2026-01-05)
- 初始品牌指南發布
- 建立完整設計系統
- 定義組件風格規範

---

**維護者**: GoGoJap 設計團隊
**最後更新**: 2026-01-05
**狀態**: 生效中
