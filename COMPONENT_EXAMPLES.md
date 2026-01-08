# GoGoJap 組件使用範例

## 按鈕組件

### 主要按鈕
```tsx
import { Button } from "@/components/ui/button";

// 基本使用
<Button>儲存變更</Button>

// 載入狀態
<Button disabled>
  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
  處理中...
</Button>

// 帶圖標
<Button>
  <Plus className="mr-2 h-4 w-4" />
  新增商品
</Button>
```

### 按鈕變體
```tsx
// 主要動作
<Button variant="default">確認</Button>

// 次要動作
<Button variant="outline">取消</Button>

// 危險操作
<Button variant="destructive">刪除</Button>

// 無背景
<Button variant="ghost">查看詳情</Button>

// 連結樣式
<Button variant="link">了解更多</Button>
```

### 按鈕尺寸
```tsx
<Button size="sm">小型按鈕</Button>
<Button size="default">標準按鈕</Button>
<Button size="lg">大型按鈕</Button>
<Button size="icon">
  <Settings className="h-4 w-4" />
</Button>
```

---

## 卡片組件

### 標準卡片
```tsx
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";

<Card>
  <CardHeader>
    <CardTitle>商品總覽</CardTitle>
    <CardDescription>最近 30 天的商品統計</CardDescription>
  </CardHeader>
  <CardContent>
    <p>這裡是卡片內容</p>
  </CardContent>
  <CardFooter>
    <Button variant="outline">查看完整報告</Button>
  </CardFooter>
</Card>
```

### 數據卡片
```tsx
<Card className="stat-card">
  <CardHeader className="stat-card-header">
    <CardTitle className="text-sm font-medium text-gray-600">
      總銷售額
    </CardTitle>
  </CardHeader>
  <CardContent>
    <div className="stat-card-value">HK$ 1,234,567</div>
    <div className="stat-card-footer">
      <span className="trend-indicator trend-up">
        <TrendingUp className="h-4 w-4" />
        +12.5% 較上月
      </span>
    </div>
  </CardContent>
</Card>
```

---

## 表單組件

### 輸入框
```tsx
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

<div className="input-group">
  <Label htmlFor="sku" className="input-label">
    商品 SKU
  </Label>
  <Input
    id="sku"
    type="text"
    placeholder="請輸入 SKU"
    className="w-full"
  />
  <p className="input-helper">請輸入完整的 SKU 編號</p>
</div>
```

### 帶驗證的輸入框
```tsx
import { useForm } from "react-hook-form";

const { register, formState: { errors } } = useForm();

<div className="input-group">
  <Label htmlFor="price">價格</Label>
  <Input
    id="price"
    type="number"
    {...register("price", {
      required: "價格為必填欄位",
      min: { value: 0, message: "價格不可為負數" }
    })}
    className={errors.price ? "border-error-500" : ""}
  />
  {errors.price && (
    <p className="input-error">{errors.price.message}</p>
  )}
</div>
```

### 下拉選單
```tsx
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

<Select>
  <SelectTrigger className="w-[200px]">
    <SelectValue placeholder="選擇分類" />
  </SelectTrigger>
  <SelectContent>
    <SelectItem value="electronics">電子產品</SelectItem>
    <SelectItem value="fashion">時尚服飾</SelectItem>
    <SelectItem value="food">食品飲料</SelectItem>
  </SelectContent>
</Select>
```

### 日期選擇器
```tsx
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { format } from "date-fns";
import { zhTW } from "date-fns/locale";

const [date, setDate] = useState<Date>();

<Popover>
  <PopoverTrigger asChild>
    <Button variant="outline" className="w-[240px] justify-start text-left">
      <CalendarIcon className="mr-2 h-4 w-4" />
      {date ? format(date, "PPP", { locale: zhTW }) : "選擇日期"}
    </Button>
  </PopoverTrigger>
  <PopoverContent className="w-auto p-0">
    <Calendar
      mode="single"
      selected={date}
      onSelect={setDate}
      locale={zhTW}
    />
  </PopoverContent>
</Popover>
```

---

## 表格組件

### 基本表格
```tsx
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

<div className="table-container">
  <Table>
    <TableHeader>
      <TableRow>
        <TableHead>商品名稱</TableHead>
        <TableHead>SKU</TableHead>
        <TableHead className="text-right">價格</TableHead>
        <TableHead className="text-right">庫存</TableHead>
        <TableHead>狀態</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>
      <TableRow className="table-row-hover">
        <TableCell className="font-medium">
          iPhone 15 Pro Max
        </TableCell>
        <TableCell className="font-mono">SKU-001</TableCell>
        <TableCell className="text-right font-tabular">
          HK$ 9,999
        </TableCell>
        <TableCell className="text-right font-tabular">123</TableCell>
        <TableCell>
          <span className="badge badge-success">有貨</span>
        </TableCell>
      </TableRow>
    </TableBody>
  </Table>
</div>
```

### 帶排序的表格
```tsx
import { ArrowUpDown } from "lucide-react";

<TableHead>
  <Button
    variant="ghost"
    onClick={() => handleSort("price")}
    className="hover:bg-transparent"
  >
    價格
    <ArrowUpDown className="ml-2 h-4 w-4" />
  </Button>
</TableHead>
```

---

## 徽章與狀態指示器

### 狀態徽章
```tsx
// 成功狀態
<span className="badge badge-success">價格優勢</span>

// 警告狀態
<span className="badge badge-warning">接近競爭價</span>

// 錯誤狀態
<span className="badge badge-error">價格劣勢</span>

// 資訊狀態
<span className="badge badge-info">AI 建議</span>
```

### 趨勢指標
```tsx
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

// 上升趨勢
<div className="trend-indicator trend-up">
  <TrendingUp className="h-4 w-4" />
  <span>+12.5%</span>
</div>

// 下降趨勢
<div className="trend-indicator trend-down">
  <TrendingDown className="h-4 w-4" />
  <span>-3.2%</span>
</div>

// 持平
<div className="trend-indicator trend-neutral">
  <Minus className="h-4 w-4" />
  <span>0.0%</span>
</div>
```

### 數字徽章
```tsx
// 通知數量
<div className="relative">
  <Bell className="h-5 w-5" />
  <span className="badge-count absolute -top-1 -right-1">5</span>
</div>
```

---

## 對話框與彈窗

### 警示對話框
```tsx
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

<AlertDialog>
  <AlertDialogTrigger asChild>
    <Button variant="destructive">刪除商品</Button>
  </AlertDialogTrigger>
  <AlertDialogContent>
    <AlertDialogHeader>
      <AlertDialogTitle>確定要刪除嗎？</AlertDialogTitle>
      <AlertDialogDescription>
        此操作無法復原，商品資料將永久刪除。
      </AlertDialogDescription>
    </AlertDialogHeader>
    <AlertDialogFooter>
      <AlertDialogCancel>取消</AlertDialogCancel>
      <AlertDialogAction onClick={handleDelete}>
        確認刪除
      </AlertDialogAction>
    </AlertDialogFooter>
  </AlertDialogContent>
</AlertDialog>
```

### 表單對話框
```tsx
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

<Dialog>
  <DialogTrigger asChild>
    <Button>
      <Plus className="mr-2 h-4 w-4" />
      新增商品
    </Button>
  </DialogTrigger>
  <DialogContent className="sm:max-w-[600px]">
    <DialogHeader>
      <DialogTitle>新增商品</DialogTitle>
      <DialogDescription>
        填寫以下資訊以新增商品到系統
      </DialogDescription>
    </DialogHeader>
    <form onSubmit={handleSubmit}>
      {/* 表單內容 */}
      <div className="grid gap-4 py-4">
        <div className="input-group">
          <Label htmlFor="name">商品名稱</Label>
          <Input id="name" />
        </div>
      </div>
      <DialogFooter>
        <Button type="button" variant="outline">取消</Button>
        <Button type="submit">儲存</Button>
      </DialogFooter>
    </form>
  </DialogContent>
</Dialog>
```

### 工具提示
```tsx
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

<TooltipProvider>
  <Tooltip>
    <TooltipTrigger asChild>
      <Button variant="ghost" size="icon">
        <Info className="h-4 w-4" />
      </Button>
    </TooltipTrigger>
    <TooltipContent>
      <p>根據過去 30 天的銷售數據計算</p>
    </TooltipContent>
  </Tooltip>
</TooltipProvider>
```

---

## 通知與提示

### Toast 通知
```tsx
import { useToast } from "@/components/ui/use-toast";

const { toast } = useToast();

// 成功通知
toast({
  title: "儲存成功",
  description: "商品資料已更新",
});

// 錯誤通知
toast({
  variant: "destructive",
  title: "操作失敗",
  description: "無法連接到伺服器，請稍後再試",
});

// 帶動作的通知
toast({
  title: "價格警報",
  description: "偵測到 3 項商品價格需要調整",
  action: (
    <Button variant="outline" size="sm" onClick={handleView}>
      查看
    </Button>
  ),
});
```

---

## 載入狀態

### 骨架屏
```tsx
import { Skeleton } from "@/components/ui/skeleton";

<Card>
  <CardHeader>
    <Skeleton className="h-4 w-[200px]" />
    <Skeleton className="h-3 w-[150px] mt-2" />
  </CardHeader>
  <CardContent>
    <Skeleton className="h-12 w-full" />
    <div className="flex gap-2 mt-4">
      <Skeleton className="h-4 w-20" />
      <Skeleton className="h-4 w-32" />
    </div>
  </CardContent>
</Card>
```

### 載入指示器
```tsx
import { Loader2 } from "lucide-react";

<div className="flex items-center justify-center py-12">
  <Loader2 className="h-8 w-8 animate-spin text-brand-primary" />
  <span className="ml-2 text-gray-600">載入中...</span>
</div>
```

---

## 空狀態

### 通用空狀態
```tsx
import { PackageOpen } from "lucide-react";

<div className="empty-state">
  <PackageOpen className="empty-state-icon" />
  <h3 className="empty-state-title">尚無商品資料</h3>
  <p className="empty-state-description">
    開始新增商品以建立您的產品目錄
  </p>
  <Button className="mt-4">
    <Plus className="mr-2 h-4 w-4" />
    新增第一個商品
  </Button>
</div>
```

### 搜尋無結果
```tsx
import { SearchX } from "lucide-react";

<div className="empty-state">
  <SearchX className="empty-state-icon" />
  <h3 className="empty-state-title">找不到符合的結果</h3>
  <p className="empty-state-description">
    請嘗試調整搜尋條件或關鍵字
  </p>
  <Button variant="outline" className="mt-4" onClick={clearFilters}>
    清除篩選
  </Button>
</div>
```

---

## 數據圖表

### 折線圖（價格趨勢）
```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

const data = [
  { date: "1/1", ourPrice: 299, competitorPrice: 319 },
  { date: "1/2", ourPrice: 299, competitorPrice: 309 },
  // ...更多數據
];

<Card>
  <CardHeader>
    <CardTitle>價格趨勢</CardTitle>
  </CardHeader>
  <CardContent>
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
        <XAxis
          dataKey="date"
          stroke="#6B7280"
          style={{ fontSize: 12 }}
        />
        <YAxis
          stroke="#6B7280"
          style={{ fontSize: 12 }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1F2937',
            border: 'none',
            borderRadius: '6px',
            color: '#FFFFFF',
          }}
        />
        <Line
          type="monotone"
          dataKey="ourPrice"
          stroke="#1570EF"
          strokeWidth={2}
          name="我們的價格"
        />
        <Line
          type="monotone"
          dataKey="competitorPrice"
          stroke="#F97316"
          strokeWidth={2}
          name="競爭對手"
        />
      </LineChart>
    </ResponsiveContainer>
  </CardContent>
</Card>
```

### 長條圖（銷售統計）
```tsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

<ResponsiveContainer width="100%" height={300}>
  <BarChart data={salesData}>
    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
    <XAxis dataKey="category" stroke="#6B7280" />
    <YAxis stroke="#6B7280" />
    <Tooltip />
    <Bar dataKey="sales" fill="#2E90FA" radius={[4, 4, 0, 0]} />
  </BarChart>
</ResponsiveContainer>
```

---

## 頁面布局

### 標準頁面結構
```tsx
export default function ProductsPage() {
  return (
    <div className="page-container">
      {/* 頁面標題 */}
      <div className="page-header">
        <h1 className="page-title">商品管理</h1>
        <p className="page-description">
          管理您的商品目錄並監控價格變動
        </p>
      </div>

      {/* 操作列 */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex gap-2">
          <Input
            type="search"
            placeholder="搜尋商品..."
            className="w-[300px]"
          />
          <Button variant="outline">
            <Filter className="mr-2 h-4 w-4" />
            篩選
          </Button>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          新增商品
        </Button>
      </div>

      {/* 統計卡片 */}
      <div className="card-grid mb-8">
        <Card className="stat-card">
          {/* 統計內容 */}
        </Card>
      </div>

      {/* 主要內容 */}
      <Card>
        <CardContent className="p-0">
          <Table>
            {/* 表格內容 */}
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
```

### 儀表板布局
```tsx
<div className="page-container">
  <div className="page-header">
    <h1 className="page-title">營運儀表板</h1>
  </div>

  {/* KPI 指標 */}
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
    <Card className="stat-card">
      {/* KPI 卡片 */}
    </Card>
  </div>

  {/* 圖表區 */}
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
    <Card>
      <CardHeader>
        <CardTitle>銷售趨勢</CardTitle>
      </CardHeader>
      <CardContent>
        {/* 折線圖 */}
      </CardContent>
    </Card>
    <Card>
      <CardHeader>
        <CardTitle>分類銷售</CardTitle>
      </CardHeader>
      <CardContent>
        {/* 長條圖 */}
      </CardContent>
    </Card>
  </div>

  {/* 警報列表 */}
  <Card>
    <CardHeader>
      <CardTitle>價格警報</CardTitle>
    </CardHeader>
    <CardContent>
      {/* 警報表格 */}
    </CardContent>
  </Card>
</div>
```

---

## 響應式設計範例

### 響應式網格
```tsx
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {items.map((item) => (
    <Card key={item.id}>
      {/* 卡片內容 */}
    </Card>
  ))}
</div>
```

### 響應式文字大小
```tsx
<h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold">
  標題文字
</h1>
```

### 響應式顯示/隱藏
```tsx
{/* 桌面版 */}
<div className="hidden md:block">
  <DetailedView />
</div>

{/* 手機版 */}
<div className="block md:hidden">
  <CompactView />
</div>
```

---

## 最佳實踐

### 1. 一致性使用設計 Token
```tsx
// ✅ 正確：使用 Tailwind 類別
<div className="text-gray-600 bg-white rounded-md p-4">

// ❌ 錯誤：硬編碼樣式
<div style={{ color: '#6B7280', backgroundColor: 'white' }}>
```

### 2. 適當的載入狀態
```tsx
{isLoading ? (
  <Skeleton className="h-12 w-full" />
) : (
  <div>{data}</div>
)}
```

### 3. 錯誤處理
```tsx
{error && (
  <Alert variant="destructive">
    <AlertCircle className="h-4 w-4" />
    <AlertTitle>錯誤</AlertTitle>
    <AlertDescription>{error.message}</AlertDescription>
  </Alert>
)}
```

### 4. 無障礙支援
```tsx
<Button aria-label="關閉對話框" onClick={onClose}>
  <X className="h-4 w-4" />
</Button>
```

### 5. 數字格式化
```tsx
import { formatCurrency, formatNumber } from "@/lib/utils";

// 貨幣
<span className="font-tabular">
  {formatCurrency(1234.56)} {/* HK$ 1,234.56 */}
</span>

// 數量
<span className="font-tabular">
  {formatNumber(1234567)} {/* 1,234,567 */}
</span>
```

---

**維護者**: GoGoJap 開發團隊
**最後更新**: 2026-01-05
