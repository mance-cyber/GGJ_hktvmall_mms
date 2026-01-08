# GoGoJap 前端架構文檔

## 架構概覽

### 技術堆疊
- **框架**: Next.js 14 (App Router)
- **UI 組件**: shadcn/ui + Radix UI
- **樣式**: Tailwind CSS
- **狀態管理**: React Query (TanStack Query)
- **圖表**: Recharts
- **表單**: React Hook Form + Zod
- **日期**: date-fns
- **圖標**: Lucide React

### 設計原則
1. **移動優先**: 所有界面從移動端開始設計
2. **組件復用**: 最大化組件復用，減少重複代碼
3. **性能優先**: 使用 React Server Components，優化加載速度
4. **類型安全**: 完整的 TypeScript 類型定義
5. **無障礙**: 遵循 WCAG 2.1 AA 標準

---

## 目錄結構

```
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # 認證相關頁面
│   │   ├── login/
│   │   └── layout.tsx
│   ├── (dashboard)/              # 主要應用頁面
│   │   ├── dashboard/            # 儀表板
│   │   ├── competitors/          # 競爭對手監控
│   │   │   ├── [id]/             # 競爭對手詳情
│   │   │   └── page.tsx
│   │   ├── alerts/               # 價格預警
│   │   ├── products/             # 商品管理
│   │   ├── content/              # AI 內容生成
│   │   └── layout.tsx            # 主佈局
│   ├── layout.tsx                # 根佈局
│   ├── globals.css               # 全局樣式
│   └── error.tsx                 # 全局錯誤頁面
├── components/                   # 組件庫
│   ├── ui/                       # shadcn/ui 基礎組件
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── input.tsx
│   │   ├── table.tsx
│   │   └── ...
│   ├── layout/                   # 佈局組件
│   │   ├── sidebar.tsx
│   │   ├── header.tsx
│   │   ├── footer.tsx
│   │   └── mobile-nav.tsx
│   ├── dashboard/                # 儀表板特定組件
│   │   ├── stat-card.tsx
│   │   ├── price-trend-chart.tsx
│   │   └── alert-list.tsx
│   ├── competitors/              # 競爭對手相關組件
│   │   ├── competitor-card.tsx
│   │   ├── product-list.tsx
│   │   └── add-competitor-dialog.tsx
│   ├── products/                 # 商品相關組件
│   │   ├── product-table.tsx
│   │   ├── product-form.tsx
│   │   └── product-filters.tsx
│   ├── content/                  # AI 內容相關組件
│   │   ├── content-generator.tsx
│   │   ├── batch-generator.tsx
│   │   └── content-preview.tsx
│   └── shared/                   # 共用組件
│       ├── data-table.tsx
│       ├── loading-skeleton.tsx
│       ├── empty-state.tsx
│       ├── error-alert.tsx
│       └── search-bar.tsx
├── lib/                          # 工具函數與配置
│   ├── api/                      # API 客戶端
│   │   ├── client.ts             # Axios 配置
│   │   ├── dashboard.ts          # 儀表板 API
│   │   ├── competitors.ts        # 競爭對手 API
│   │   ├── alerts.ts             # 預警 API
│   │   ├── products.ts           # 商品 API
│   │   └── content.ts            # AI 內容 API
│   ├── hooks/                    # 自訂 React Hooks
│   │   ├── use-dashboard.ts
│   │   ├── use-competitors.ts
│   │   ├── use-alerts.ts
│   │   └── use-products.ts
│   ├── utils.ts                  # 工具函數
│   ├── constants.ts              # 常量定義
│   └── validations.ts            # Zod 驗證 Schema
├── types/                        # TypeScript 類型定義
│   ├── api.ts                    # API 響應類型
│   ├── dashboard.ts
│   ├── competitor.ts
│   ├── alert.ts
│   ├── product.ts
│   └── content.ts
├── public/                       # 靜態資源
│   ├── brand/
│   │   ├── logo.svg
│   │   └── icon.svg
│   └── images/
└── config/                       # 配置文件
    ├── site.ts                   # 網站配置
    └── navigation.ts             # 導航配置
```

---

## 核心組件架構

### 1. 佈局系統

#### 主佈局 (DashboardLayout)
```tsx
// app/(dashboard)/layout.tsx
- 左側邊欄（桌面）或底部導航（移動）
- 頂部欄（用戶資訊、通知、搜尋）
- 主內容區（動態路由）
- 響應式切換
```

#### 側邊欄 (Sidebar)
```tsx
// components/layout/sidebar.tsx
- Logo 與品牌名稱
- 導航菜單（Dashboard、競爭對手、預警、商品、AI 內容）
- 當前頁面高亮
- 收合/展開功能
- 移動端自動隱藏
```

#### 頂部欄 (Header)
```tsx
// components/layout/header.tsx
- 頁面標題與麵包屑
- 全局搜尋
- 通知圖標（含未讀數量）
- 用戶下拉菜單（設定、登出）
```

### 2. 數據展示組件

#### 統計卡片 (StatCard)
```tsx
// components/dashboard/stat-card.tsx
Props:
- title: string
- value: number | string
- trend?: { value: number, isPositive: boolean }
- icon?: ReactNode
- loading?: boolean
```

#### 數據表格 (DataTable)
```tsx
// components/shared/data-table.tsx
Features:
- 排序
- 分頁
- 篩選
- 搜尋
- 批量操作
- 響應式（移動端卡片視圖）
```

#### 圖表組件
```tsx
// components/dashboard/price-trend-chart.tsx
- 折線圖（價格趨勢）
- 多條數據線（自家 vs 競爭對手）
- 響應式尺寸
- 工具提示
- 圖例
```

### 3. 表單組件

#### 產品表單 (ProductForm)
```tsx
// components/products/product-form.tsx
- React Hook Form 整合
- Zod 驗證
- 實時錯誤提示
- 自動保存草稿
- 圖片上傳
```

#### 搜尋與篩選 (SearchBar + Filters)
```tsx
// components/shared/search-bar.tsx
- 防抖搜尋
- 清除按鈕
- 快捷鍵支援 (/)

// components/products/product-filters.tsx
- 多選篩選器
- 日期範圍選擇器
- 價格範圍滑桿
- 重置按鈕
```

---

## 狀態管理策略

### React Query 使用模式

#### 查詢 (Queries)
```tsx
// lib/hooks/use-dashboard.ts
export function useDashboardData() {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboardData,
    refetchInterval: 60000, // 每分鐘刷新
    staleTime: 30000,
  });
}
```

#### 變更 (Mutations)
```tsx
// lib/hooks/use-competitors.ts
export function useAddCompetitor() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: addCompetitor,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitors'] });
      toast({ title: '新增成功' });
    },
    onError: (error) => {
      toast({
        variant: 'destructive',
        title: '新增失敗',
        description: error.message
      });
    },
  });
}
```

#### 快取策略
```tsx
// lib/api/client.ts
默認配置:
- staleTime: 5 分鐘（數據視為新鮮的時間）
- cacheTime: 10 分鐘（快取保留時間）
- refetchOnWindowFocus: true（窗口聚焦時刷新）
- retry: 3（失敗重試次數）
```

---

## 路由結構

### 頁面路由表

```
/ (重定向到 /dashboard)
├── /dashboard                    # 儀表板首頁
├── /competitors                  # 競爭對手列表
│   └── /competitors/[id]         # 競爭對手詳情
├── /alerts                       # 價格預警列表
├── /products                     # 商品管理
│   ├── /products/new             # 新增商品
│   └── /products/[id]            # 編輯商品
├── /content                      # AI 內容生成
│   ├── /content/generator        # 單個生成
│   └── /content/batch            # 批量生成
└── /settings                     # 系統設定
```

### 導航配置
```tsx
// config/navigation.ts
export const navigationItems = [
  {
    title: '儀表板',
    href: '/dashboard',
    icon: Home,
  },
  {
    title: '競爭對手',
    href: '/competitors',
    icon: Users,
    badge: competitorCount,
  },
  {
    title: '價格預警',
    href: '/alerts',
    icon: AlertTriangle,
    badge: unreadAlerts,
  },
  {
    title: '商品管理',
    href: '/products',
    icon: Package,
  },
  {
    title: 'AI 內容',
    href: '/content',
    icon: Sparkles,
  },
];
```

---

## API 整合層

### API 客戶端配置
```tsx
// lib/api/client.ts
import axios from 'axios';

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 請求攔截器
apiClient.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 響應攔截器
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // 處理未授權
      redirectToLogin();
    }
    return Promise.reject(error);
  }
);
```

### API 模塊劃分

#### Dashboard API
```tsx
// lib/api/dashboard.ts
export async function getDashboardData() {
  return apiClient.get('/api/v1/dashboard');
}
```

#### Competitors API
```tsx
// lib/api/competitors.ts
export async function getCompetitors() {
  return apiClient.get('/api/v1/competitors');
}

export async function addCompetitor(data: CreateCompetitorDto) {
  return apiClient.post('/api/v1/competitors', data);
}

export async function getCompetitorProducts(id: number) {
  return apiClient.get(`/api/v1/competitors/${id}/products`);
}
```

#### Alerts API
```tsx
// lib/api/alerts.ts
export async function getAlerts(params?: AlertFilterParams) {
  return apiClient.get('/api/v1/alerts', { params });
}
```

---

## 響應式設計策略

### 斷點使用規範

```tsx
移動端 (< 640px):
- 卡片式佈局
- 底部導航
- 單列網格
- 簡化表格（僅顯示關鍵欄位）

平板 (640px - 1024px):
- 側邊欄收合
- 雙列網格
- 完整表格

桌面 (> 1024px):
- 側邊欄展開
- 三/四列網格
- 完整功能
```

### 響應式組件範例

```tsx
// 統計卡片網格
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  {stats.map((stat) => (
    <StatCard key={stat.id} {...stat} />
  ))}
</div>

// 響應式表格
<div className="hidden md:block">
  <DataTable data={products} columns={columns} />
</div>
<div className="block md:hidden">
  <ProductCardList data={products} />
</div>
```

---

## 性能優化策略

### 1. 代碼分割
```tsx
// 動態導入大型組件
const ChartComponent = dynamic(() => import('@/components/charts/price-trend'), {
  loading: () => <Skeleton className="h-[300px]" />,
  ssr: false,
});
```

### 2. 圖片優化
```tsx
// 使用 Next.js Image 組件
import Image from 'next/image';

<Image
  src="/images/product.jpg"
  alt="Product"
  width={300}
  height={300}
  loading="lazy"
  placeholder="blur"
/>
```

### 3. 虛擬滾動
```tsx
// 使用 react-virtual 處理大型列表
import { useVirtualizer } from '@tanstack/react-virtual';
```

### 4. React Server Components
```tsx
// app/(dashboard)/dashboard/page.tsx
// 在伺服器端獲取數據，減少客戶端負擔
export default async function DashboardPage() {
  const data = await getDashboardData();
  return <DashboardView data={data} />;
}
```

---

## 錯誤處理

### 全局錯誤邊界
```tsx
// app/error.tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="error-container">
      <h2>發生錯誤</h2>
      <p>{error.message}</p>
      <Button onClick={reset}>重試</Button>
    </div>
  );
}
```

### API 錯誤處理
```tsx
// lib/hooks/use-competitors.ts
const { data, error, isLoading } = useCompetitors();

if (error) {
  return <ErrorAlert error={error} />;
}

if (isLoading) {
  return <LoadingSkeleton />;
}
```

---

## 無障礙指南

### 1. 語義化 HTML
```tsx
<nav aria-label="主導航">
  <ul>
    <li><a href="/dashboard">儀表板</a></li>
  </ul>
</nav>
```

### 2. 鍵盤導航
```tsx
// 所有互動元素支援 Tab 導航
<Button
  onClick={handleClick}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
>
  確認
</Button>
```

### 3. ARIA 標籤
```tsx
<Button aria-label="關閉對話框" onClick={onClose}>
  <X className="h-4 w-4" />
</Button>
```

### 4. 焦點管理
```tsx
// 對話框打開時聚焦第一個輸入框
useEffect(() => {
  if (isOpen) {
    inputRef.current?.focus();
  }
}, [isOpen]);
```

---

## 測試策略

### 單元測試
```tsx
// 使用 Vitest + React Testing Library
import { render, screen } from '@testing-library/react';
import StatCard from '@/components/dashboard/stat-card';

test('renders stat card correctly', () => {
  render(<StatCard title="總銷售額" value={1234567} />);
  expect(screen.getByText('總銷售額')).toBeInTheDocument();
});
```

### E2E 測試
```tsx
// 使用 Playwright
test('user can add competitor', async ({ page }) => {
  await page.goto('/competitors');
  await page.click('[data-testid="add-competitor-button"]');
  await page.fill('[name="name"]', 'Competitor A');
  await page.click('[type="submit"]');
  await expect(page.locator('text=Competitor A')).toBeVisible();
});
```

---

## 部署配置

### 環境變數
```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SITE_NAME=GoGoJap
NEXT_PUBLIC_SITE_DESCRIPTION=HKTVmall AI 營運系統
```

### 建置優化
```js
// next.config.js
module.exports = {
  images: {
    domains: ['hktvmall.com'],
    formats: ['image/avif', 'image/webp'],
  },
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ['lucide-react', 'recharts'],
  },
};
```

---

## 開發工作流

### 1. 新增頁面
```bash
1. 建立路由檔案: app/(dashboard)/new-page/page.tsx
2. 建立頁面組件: components/new-page/
3. 建立 API 函數: lib/api/new-page.ts
4. 建立 React Hook: lib/hooks/use-new-page.ts
5. 更新導航配置: config/navigation.ts
```

### 2. 新增組件
```bash
1. 建立組件檔案: components/shared/new-component.tsx
2. 撰寫 TypeScript 類型
3. 實現組件邏輯
4. 撰寫 Storybook 故事（選填）
5. 撰寫單元測試
```

### 3. Git 提交規範
```bash
feat: 新增競爭對手詳情頁面
fix: 修復價格趨勢圖表顯示錯誤
style: 更新按鈕樣式符合品牌指南
refactor: 重構數據表格組件
docs: 更新前端架構文檔
test: 新增商品表單單元測試
```

---

## 維護指南

### 依賴更新
```bash
# 每月檢查依賴更新
npm outdated

# 更新補丁版本（安全）
npm update

# 更新主要版本（需測試）
npm install package@latest
```

### 性能監控
```tsx
// 使用 Vercel Analytics 或 Google Analytics
import { Analytics } from '@vercel/analytics/react';

<Analytics />
```

### 程式碼品質
```bash
# ESLint 檢查
npm run lint

# TypeScript 類型檢查
npm run type-check

# Prettier 格式化
npm run format
```

---

**維護者**: GoGoJap 開發團隊
**最後更新**: 2026-01-05
**版本**: 1.0.0
