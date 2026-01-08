# GoGoJap 快速入門指南

## 環境要求

- Node.js 18.17 或以上
- npm 9.0 或以上
- 後端 API 服務運行於 http://localhost:8000

---

## 安裝步驟

### 1. 安裝依賴

```bash
npm install
```

### 2. 環境變數設定

建立 `.env.local` 檔案：

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_NAME=GoGoJap
NEXT_PUBLIC_SITE_DESCRIPTION=HKTVmall AI 營運系統
```

### 3. 啟動開發伺服器

```bash
npm run dev
```

瀏覽器訪問：http://localhost:3000

---

## 主要依賴套件

### 核心框架
```json
{
  "next": "14.0.0",
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "typescript": "^5.0.0"
}
```

### UI 組件
```json
{
  "@radix-ui/react-*": "最新版本",
  "lucide-react": "^0.294.0",
  "tailwindcss": "^3.3.0"
}
```

### 狀態管理 & 數據獲取
```json
{
  "@tanstack/react-query": "^5.0.0",
  "axios": "^1.6.0"
}
```

### 表單處理
```json
{
  "react-hook-form": "^7.48.0",
  "zod": "^3.22.0"
}
```

### 圖表
```json
{
  "recharts": "^2.10.0"
}
```

### 日期處理
```json
{
  "date-fns": "^2.30.0"
}
```

### 工具類
```json
{
  "clsx": "^2.0.0",
  "tailwind-merge": "^2.0.0"
}
```

---

## 安裝命令（完整）

如果 `package.json` 尚未建立，請依序執行：

```bash
# 初始化專案（如果需要）
npm init -y

# 安裝 Next.js 與 React
npm install next@14.0.0 react@^18.2.0 react-dom@^18.2.0

# 安裝 TypeScript
npm install -D typescript @types/react @types/node

# 安裝 Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 安裝 shadcn/ui 依賴（核心）
npm install @radix-ui/react-dialog
npm install @radix-ui/react-dropdown-menu
npm install @radix-ui/react-label
npm install @radix-ui/react-select
npm install @radix-ui/react-slot
npm install @radix-ui/react-tooltip
npm install @radix-ui/react-popover
npm install @radix-ui/react-separator
npm install @radix-ui/react-alert-dialog

# 安裝圖標庫
npm install lucide-react

# 安裝工具庫
npm install clsx tailwind-merge
npm install class-variance-authority

# 安裝 React Query
npm install @tanstack/react-query

# 安裝 Axios
npm install axios

# 安裝表單處理
npm install react-hook-form
npm install zod
npm install @hookform/resolvers

# 安裝圖表庫
npm install recharts

# 安裝日期處理
npm install date-fns

# 安裝動畫庫
npm install tailwindcss-animate
```

---

## 必要的 shadcn/ui 組件初始化

如果使用 shadcn/ui CLI（推薦）：

```bash
# 初始化 shadcn/ui
npx shadcn-ui@latest init

# 選擇以下配置：
# - Style: Default
# - Base color: Slate
# - CSS variables: Yes
# - Import alias: @/*

# 安裝需要的組件
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add label
npx shadcn-ui@latest add select
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add tooltip
npx shadcn-ui@latest add skeleton
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add alert-dialog
npx shadcn-ui@latest add sheet
npx shadcn-ui@latest add toast
npx shadcn-ui@latest add popover
npx shadcn-ui@latest add separator
npx shadcn-ui@latest add table
```

---

## 專案結構

```
GoGoJap/
├── app/                          # Next.js App Router
│   ├── (dashboard)/              # 主應用路由組
│   │   ├── dashboard/            # 儀表板頁面 ✅
│   │   ├── competitors/          # 競爭對手頁面 ✅
│   │   ├── alerts/               # 價格預警（待完成）
│   │   ├── products/             # 商品管理（待完成）
│   │   ├── content/              # AI 內容（待完成）
│   │   └── layout.tsx            # Dashboard 佈局 ✅
│   ├── globals.css               # 全局樣式 ✅
│   └── layout.tsx                # 根佈局
├── components/                   # React 組件
│   ├── ui/                       # shadcn/ui 基礎組件
│   ├── layout/                   # 佈局組件 ✅
│   │   ├── sidebar.tsx
│   │   └── header.tsx
│   ├── dashboard/                # 儀表板組件（待完成）
│   ├── competitors/              # 競爭對手組件（待完成）
│   └── shared/                   # 共用組件（待完成）
├── lib/                          # 工具與邏輯
│   ├── api/                      # API 客戶端 ✅
│   │   ├── client.ts
│   │   ├── dashboard.ts
│   │   ├── competitors.ts
│   │   ├── alerts.ts
│   │   ├── products.ts
│   │   └── content.ts
│   ├── hooks/                    # React Hooks ✅
│   │   ├── use-dashboard.ts
│   │   ├── use-competitors.ts
│   │   └── use-products.ts
│   └── utils.ts                  # 工具函數 ✅
├── types/                        # TypeScript 類型 ✅
│   └── api.ts
├── public/                       # 靜態資源
├── tailwind.config.ts            # Tailwind 配置 ✅
├── tsconfig.json                 # TypeScript 配置
├── next.config.js                # Next.js 配置
└── package.json                  # 專案依賴
```

---

## 開發命令

```bash
# 啟動開發伺服器（支援熱重載）
npm run dev

# TypeScript 類型檢查
npm run type-check

# ESLint 代碼檢查
npm run lint

# Prettier 代碼格式化
npm run format

# 建置生產版本
npm run build

# 啟動生產伺服器
npm start
```

---

## 常見問題

### Q1: 後端 API 無法連接
**A**: 確保後端服務運行於 http://localhost:8000，並檢查 `.env.local` 中的 `NEXT_PUBLIC_API_URL` 設定。

### Q2: Tailwind 樣式未生效
**A**: 確認 `tailwind.config.ts` 的 `content` 配置包含所有組件路徑：
```ts
content: [
  "./app/**/*.{js,ts,jsx,tsx}",
  "./components/**/*.{js,ts,jsx,tsx}",
]
```

### Q3: shadcn/ui 組件找不到
**A**: 使用 `npx shadcn-ui@latest add <component-name>` 安裝缺少的組件。

### Q4: React Query DevTools 不顯示
**A**: 在開發環境中，DevTools 應自動啟用。確保在根佈局中包含：
```tsx
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

<ReactQueryDevtools initialIsOpen={false} />
```

---

## 瀏覽器支援

- Chrome/Edge（最新版本）
- Firefox（最新版本）
- Safari 14+

---

## 開發流程建議

### 1. 新增頁面
```bash
# 1. 建立頁面檔案
touch app/(dashboard)/new-page/page.tsx

# 2. 建立 API 函數
touch lib/api/new-page.ts

# 3. 建立 React Hook
touch lib/hooks/use-new-page.ts

# 4. 建立組件
mkdir components/new-page
touch components/new-page/component.tsx
```

### 2. 新增 shadcn/ui 組件
```bash
npx shadcn-ui@latest add <component-name>
```

### 3. Git 提交規範
```bash
feat: 新增競爭對手詳情頁面
fix: 修復價格趨勢圖表顯示錯誤
style: 更新按鈕樣式
refactor: 重構數據表格組件
docs: 更新 README
test: 新增商品表單測試
```

---

## 效能優化建議

### 1. 圖片優化
使用 Next.js Image 組件：
```tsx
import Image from 'next/image';

<Image
  src="/image.jpg"
  alt="Description"
  width={500}
  height={300}
  loading="lazy"
/>
```

### 2. 代碼分割
使用動態導入：
```tsx
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <Skeleton />,
  ssr: false,
});
```

### 3. React Query 快取
調整快取策略：
```tsx
useQuery({
  queryKey: ['data'],
  queryFn: fetchData,
  staleTime: 60000,      // 1 分鐘內視為新鮮
  cacheTime: 300000,     // 5 分鐘快取
  refetchOnWindowFocus: false,  // 不在視窗聚焦時刷新
});
```

---

## 部署

### Vercel（推薦）
```bash
# 安裝 Vercel CLI
npm install -g vercel

# 部署
vercel

# 生產部署
vercel --prod
```

### 自訂伺服器
```bash
# 建置
npm run build

# 啟動
npm start
```

---

## 額外資源

- [專案架構文檔](./FRONTEND_ARCHITECTURE.md)
- [實施總結](./FRONTEND_IMPLEMENTATION_SUMMARY.md)
- [品牌指南](./BRAND_GUIDELINES.md)
- [設計 Token](./DESIGN_TOKENS.md)
- [組件範例](./COMPONENT_EXAMPLES.md)

---

**需要幫助？** 請查閱文檔或聯絡開發團隊。

**最後更新**: 2026-01-05
