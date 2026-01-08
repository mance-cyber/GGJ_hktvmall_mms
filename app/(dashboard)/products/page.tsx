"use client";

import { useState } from "react";
import { useProducts, useProductCategories } from "@/lib/hooks/use-products";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import {
  Plus,
  Package,
  MoreVertical,
  Edit,
  Trash2,
  Search,
  Filter,
  PackageOpen,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { formatCurrency } from "@/lib/utils";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { Product } from "@/types/api";

// ==================== 商品狀態標籤 ====================

function StatusBadge({ status }: { status: Product["status"] }) {
  const statusConfig = {
    active: { label: "在售", className: "bg-success/10 text-success-700" },
    inactive: { label: "下架", className: "bg-gray-100 text-gray-600" },
    out_of_stock: { label: "缺貨", className: "bg-warning/10 text-warning-700" },
  };

  const config = statusConfig[status] || statusConfig.inactive;

  return (
    <Badge variant="secondary" className={config.className}>
      {config.label}
    </Badge>
  );
}

// ==================== 商品卡片組件 ====================

interface ProductCardProps {
  product: Product;
}

function ProductCard({ product }: ProductCardProps) {
  return (
    <Card className="stat-card hover:shadow-md transition-shadow">
      <CardContent className="p-4">
        {/* 商品圖片 */}
        <div className="aspect-square bg-gray-100 rounded-lg mb-3 flex items-center justify-center overflow-hidden">
          {product.imageUrl ? (
            <img
              src={product.imageUrl}
              alt={product.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <Package className="h-12 w-12 text-gray-300" />
          )}
        </div>

        {/* 商品資訊 */}
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-gray-900 truncate" title={product.name}>
              {product.name}
            </h3>
            <p className="text-xs text-gray-500 mt-0.5">SKU: {product.sku}</p>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8 -mr-2">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem>
                <Edit className="mr-2 h-4 w-4" />
                編輯
              </DropdownMenuItem>
              <DropdownMenuItem className="text-error-600">
                <Trash2 className="mr-2 h-4 w-4" />
                刪除
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* 分類與品牌 */}
        <div className="flex items-center gap-2 mb-3">
          {product.category && (
            <span className="text-xs px-2 py-0.5 bg-gray-100 rounded text-gray-600">
              {product.category}
            </span>
          )}
          {product.brand && (
            <span className="text-xs text-gray-500">{product.brand}</span>
          )}
        </div>

        {/* 價格與庫存 */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-lg font-bold text-gray-900 font-tabular">
              {formatCurrency(product.price)}
            </p>
            {product.cost && (
              <p className="text-xs text-gray-500">
                成本: {formatCurrency(product.cost)}
              </p>
            )}
          </div>
          <div className="text-right">
            <StatusBadge status={product.status} />
            <p className="text-xs text-gray-500 mt-1">庫存: {product.stock}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ==================== 商品表格行組件 ====================

function ProductTableRow({ product }: ProductCardProps) {
  return (
    <tr className="border-b hover:bg-gray-50">
      <td className="px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gray-100 rounded flex items-center justify-center overflow-hidden flex-shrink-0">
            {product.imageUrl ? (
              <img
                src={product.imageUrl}
                alt={product.name}
                className="w-full h-full object-cover"
              />
            ) : (
              <Package className="h-5 w-5 text-gray-300" />
            )}
          </div>
          <div className="min-w-0">
            <p className="font-medium text-gray-900 truncate">{product.name}</p>
            <p className="text-xs text-gray-500">SKU: {product.sku}</p>
          </div>
        </div>
      </td>
      <td className="px-4 py-3 text-sm text-gray-600">{product.category || "-"}</td>
      <td className="px-4 py-3 text-sm text-gray-600">{product.brand || "-"}</td>
      <td className="px-4 py-3 text-sm font-medium text-gray-900 font-tabular">
        {formatCurrency(product.price)}
      </td>
      <td className="px-4 py-3 text-sm text-gray-600 font-tabular">{product.stock}</td>
      <td className="px-4 py-3">
        <StatusBadge status={product.status} />
      </td>
      <td className="px-4 py-3">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <MoreVertical className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem>
              <Edit className="mr-2 h-4 w-4" />
              編輯
            </DropdownMenuItem>
            <DropdownMenuItem className="text-error-600">
              <Trash2 className="mr-2 h-4 w-4" />
              刪除
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </td>
    </tr>
  );
}

// ==================== 空狀態組件 ====================

function EmptyState() {
  return (
    <div className="empty-state">
      <PackageOpen className="empty-state-icon" />
      <h3 className="empty-state-title">尚無商品</h3>
      <p className="empty-state-description">開始添加商品以進行價格監控</p>
      <Button className="mt-4">
        <Plus className="mr-2 h-4 w-4" />
        新增第一個商品
      </Button>
    </div>
  );
}

// ==================== 載入骨架組件 ====================

function LoadingSkeleton({ viewMode }: { viewMode: "grid" | "table" }) {
  if (viewMode === "table") {
    return (
      <div className="bg-white rounded-lg border">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">商品</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">分類</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">品牌</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">價格</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">庫存</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500">狀態</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {[1, 2, 3, 4, 5].map((i) => (
              <tr key={i} className="border-b">
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    <Skeleton className="w-10 h-10 rounded" />
                    <div>
                      <Skeleton className="h-4 w-32 mb-1" />
                      <Skeleton className="h-3 w-20" />
                    </div>
                  </div>
                </td>
                <td className="px-4 py-3"><Skeleton className="h-4 w-16" /></td>
                <td className="px-4 py-3"><Skeleton className="h-4 w-16" /></td>
                <td className="px-4 py-3"><Skeleton className="h-4 w-16" /></td>
                <td className="px-4 py-3"><Skeleton className="h-4 w-12" /></td>
                <td className="px-4 py-3"><Skeleton className="h-5 w-12 rounded-full" /></td>
                <td className="px-4 py-3"><Skeleton className="h-8 w-8" /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
        <Card key={i} className="stat-card">
          <CardContent className="p-4">
            <Skeleton className="aspect-square rounded-lg mb-3" />
            <Skeleton className="h-5 w-3/4 mb-1" />
            <Skeleton className="h-3 w-1/2 mb-3" />
            <div className="flex justify-between">
              <Skeleton className="h-6 w-20" />
              <Skeleton className="h-5 w-12 rounded-full" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// ==================== 商品管理頁面 ====================

export default function ProductsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [categoryFilter, setCategoryFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<"active" | "inactive" | "out_of_stock" | "">("");
  const [viewMode, setViewMode] = useState<"grid" | "table">("grid");
  const [page, setPage] = useState(1);
  const limit = 20;

  // 獲取商品列表
  const { data: productsData, isLoading, error } = useProducts({
    search: searchQuery || undefined,
    category: categoryFilter || undefined,
    status: statusFilter || undefined,
    page,
    limit,
  });

  // 獲取分類列表
  const { data: categories } = useProductCategories();

  const products = productsData?.items || [];
  const total = productsData?.total || 0;
  const totalPages = Math.ceil(total / limit);

  return (
    <div className="page-container">
      {/* 頁面標題 */}
      <div className="page-header">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="page-title">商品管理</h1>
            <p className="page-description">管理您的商品目錄與價格</p>
          </div>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            新增商品
          </Button>
        </div>
      </div>

      {/* 統計卡片 */}
      {!isLoading && products.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card className="stat-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="stat-card-header">總商品數</p>
                  <p className="stat-card-value mt-1">{total}</p>
                </div>
                <Package className="h-8 w-8 text-brand-primary/30" />
              </div>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="stat-card-header">在售中</p>
                  <p className="stat-card-value mt-1 text-success">
                    {products.filter((p) => p.status === "active").length}
                  </p>
                </div>
                <div className="h-8 w-8 rounded-full bg-success/20 flex items-center justify-center">
                  <div className="h-3 w-3 rounded-full bg-success"></div>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="stat-card-header">缺貨中</p>
                  <p className="stat-card-value mt-1 text-warning">
                    {products.filter((p) => p.status === "out_of_stock").length}
                  </p>
                </div>
                <div className="h-8 w-8 rounded-full bg-warning/20 flex items-center justify-center">
                  <div className="h-3 w-3 rounded-full bg-warning"></div>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="stat-card-header">已下架</p>
                  <p className="stat-card-value mt-1 text-gray-500">
                    {products.filter((p) => p.status === "inactive").length}
                  </p>
                </div>
                <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center">
                  <div className="h-3 w-3 rounded-full bg-gray-400"></div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 搜尋與篩選 */}
      {!isLoading && (
        <div className="flex flex-col md:flex-row gap-3 mb-6">
          <div className="relative flex-1 md:max-w-[300px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="search"
              placeholder="搜尋商品名稱或 SKU..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setPage(1);
              }}
              className="flex h-10 w-full rounded-md border border-gray-300 bg-white pl-9 pr-3 py-2 text-sm focus:border-brand-primary focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
            />
          </div>

          <Select
            value={categoryFilter}
            onValueChange={(value) => {
              setCategoryFilter(value === "all" ? "" : value);
              setPage(1);
            }}
          >
            <SelectTrigger className="w-full md:w-[160px]">
              <Filter className="h-4 w-4 mr-2 text-gray-400" />
              <SelectValue placeholder="全部分類" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部分類</SelectItem>
              {categories?.map((cat) => (
                <SelectItem key={cat} value={cat}>
                  {cat}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select
            value={statusFilter}
            onValueChange={(value) => {
              setStatusFilter(value === "all" ? "" : value as "active" | "inactive" | "out_of_stock");
              setPage(1);
            }}
          >
            <SelectTrigger className="w-full md:w-[140px]">
              <SelectValue placeholder="全部狀態" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部狀態</SelectItem>
              <SelectItem value="active">在售</SelectItem>
              <SelectItem value="inactive">下架</SelectItem>
              <SelectItem value="out_of_stock">缺貨</SelectItem>
            </SelectContent>
          </Select>

          <div className="flex gap-1 ml-auto">
            <Button
              variant={viewMode === "grid" ? "secondary" : "ghost"}
              size="icon"
              onClick={() => setViewMode("grid")}
            >
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 16 16">
                <path d="M1 2.5A1.5 1.5 0 0 1 2.5 1h3A1.5 1.5 0 0 1 7 2.5v3A1.5 1.5 0 0 1 5.5 7h-3A1.5 1.5 0 0 1 1 5.5v-3zM2.5 2a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3zm6.5.5A1.5 1.5 0 0 1 10.5 1h3A1.5 1.5 0 0 1 15 2.5v3A1.5 1.5 0 0 1 13.5 7h-3A1.5 1.5 0 0 1 9 5.5v-3zm1.5-.5a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3zM1 10.5A1.5 1.5 0 0 1 2.5 9h3A1.5 1.5 0 0 1 7 10.5v3A1.5 1.5 0 0 1 5.5 15h-3A1.5 1.5 0 0 1 1 13.5v-3zm1.5-.5a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3zm6.5.5A1.5 1.5 0 0 1 10.5 9h3a1.5 1.5 0 0 1 1.5 1.5v3a1.5 1.5 0 0 1-1.5 1.5h-3A1.5 1.5 0 0 1 9 13.5v-3zm1.5-.5a.5.5 0 0 0-.5.5v3a.5.5 0 0 0 .5.5h3a.5.5 0 0 0 .5-.5v-3a.5.5 0 0 0-.5-.5h-3z"/>
              </svg>
            </Button>
            <Button
              variant={viewMode === "table" ? "secondary" : "ghost"}
              size="icon"
              onClick={() => setViewMode("table")}
            >
              <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 16 16">
                <path fillRule="evenodd" d="M0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2zm15 2h-4v3h4V4zm0 4h-4v3h4V8zm0 4h-4v3h3a1 1 0 0 0 1-1v-2zm-5 3v-3H6v3h4zm-5 0v-3H1v2a1 1 0 0 0 1 1h3zm-4-4h4V8H1v3zm0-4h4V4H1v3zm5-3v3h4V4H6zm4 4H6v3h4V8z"/>
              </svg>
            </Button>
          </div>
        </div>
      )}

      {/* 錯誤狀態 */}
      {error && (
        <div className="empty-state">
          <Package className="empty-state-icon text-error" />
          <h3 className="empty-state-title">載入失敗</h3>
          <p className="empty-state-description">無法載入商品列表</p>
        </div>
      )}

      {/* 載入中 */}
      {isLoading && <LoadingSkeleton viewMode={viewMode} />}

      {/* 空狀態 */}
      {!isLoading && !error && products.length === 0 && !searchQuery && !categoryFilter && !statusFilter && (
        <EmptyState />
      )}

      {/* 無搜尋結果 */}
      {!isLoading && !error && products.length === 0 && (searchQuery || categoryFilter || statusFilter) && (
        <div className="empty-state">
          <Search className="empty-state-icon" />
          <h3 className="empty-state-title">找不到符合的商品</h3>
          <p className="empty-state-description">請嘗試調整篩選條件</p>
        </div>
      )}

      {/* 商品列表 - 網格視圖 */}
      {!isLoading && !error && products.length > 0 && viewMode === "grid" && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {products.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      )}

      {/* 商品列表 - 表格視圖 */}
      {!isLoading && !error && products.length > 0 && viewMode === "table" && (
        <div className="bg-white rounded-lg border overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  商品
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  分類
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  品牌
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  價格
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  庫存
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  狀態
                </th>
                <th className="px-4 py-3 w-10"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {products.map((product) => (
                <ProductTableRow key={product.id} product={product} />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* 分頁 */}
      {!isLoading && !error && totalPages > 1 && (
        <div className="flex items-center justify-between mt-6">
          <p className="text-sm text-gray-500">
            共 {total} 件商品，第 {page} / {totalPages} 頁
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              <ChevronLeft className="h-4 w-4 mr-1" />
              上一頁
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              下一頁
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
