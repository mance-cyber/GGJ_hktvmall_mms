"use client";

import { useState } from "react";
import { useContentRecords, useGenerateContent, useUpdateContentStatus } from "@/lib/hooks/use-content";
import { useProducts } from "@/lib/hooks/use-products";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import {
  Sparkles,
  FileText,
  CheckCircle2,
  XCircle,
  Clock,
  Copy,
  MoreVertical,
  Search,
  Filter,
  Wand2,
  Loader2,
} from "lucide-react";
import { formatRelativeTime, cn } from "@/lib/utils";
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
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog";
import type { ContentRecord, ContentType, ContentStyle, ContentLanguage } from "@/types/api";

// ==================== 狀態標籤 ====================

function StatusBadge({ status }: { status: ContentRecord["status"] }) {
  const statusConfig = {
    draft: { label: "草稿", className: "bg-gray-100 text-gray-600", icon: FileText },
    pending_review: { label: "待審核", className: "bg-warning/10 text-warning-700", icon: Clock },
    approved: { label: "已通過", className: "bg-success/10 text-success-700", icon: CheckCircle2 },
    rejected: { label: "已拒絕", className: "bg-error/10 text-error-700", icon: XCircle },
  };

  const config = statusConfig[status] || statusConfig.draft;
  const Icon = config.icon;

  return (
    <Badge variant="secondary" className={cn("gap-1", config.className)}>
      <Icon className="h-3 w-3" />
      {config.label}
    </Badge>
  );
}

// ==================== 內容類型標籤 ====================

function ContentTypeBadge({ type }: { type: string }) {
  const typeConfig: Record<string, { label: string; className: string }> = {
    product_description: { label: "商品描述", className: "bg-blue-100 text-blue-700" },
    seo_title: { label: "SEO 標題", className: "bg-purple-100 text-purple-700" },
    seo_description: { label: "SEO 描述", className: "bg-indigo-100 text-indigo-700" },
    marketing_copy: { label: "行銷文案", className: "bg-pink-100 text-pink-700" },
    social_post: { label: "社交貼文", className: "bg-orange-100 text-orange-700" },
  };

  const config = typeConfig[type] || { label: type, className: "bg-gray-100 text-gray-700" };

  return (
    <span className={cn("px-2 py-0.5 rounded text-xs font-medium", config.className)}>
      {config.label}
    </span>
  );
}

// ==================== 內容卡片組件 ====================

interface ContentCardProps {
  record: ContentRecord;
  onApprove: (id: number) => void;
  onReject: (id: number) => void;
}

function ContentCard({ record, onApprove, onReject }: ContentCardProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(record.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card className="stat-card">
      <CardContent className="p-4">
        {/* 標題與操作 */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex-1 min-w-0">
            <p className="font-medium text-gray-900 truncate">{record.productName}</p>
            <div className="flex items-center gap-2 mt-1">
              <ContentTypeBadge type={record.contentType} />
              <StatusBadge status={record.status} />
            </div>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8 -mr-2">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={handleCopy}>
                <Copy className="mr-2 h-4 w-4" />
                {copied ? "已複製" : "複製內容"}
              </DropdownMenuItem>
              {record.status !== "approved" && (
                <DropdownMenuItem onClick={() => onApprove(record.id)}>
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  通過審核
                </DropdownMenuItem>
              )}
              {record.status !== "rejected" && (
                <DropdownMenuItem
                  className="text-error-600"
                  onClick={() => onReject(record.id)}
                >
                  <XCircle className="mr-2 h-4 w-4" />
                  拒絕
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* 內容預覽 */}
        <div className="bg-gray-50 rounded-lg p-3 mb-3 max-h-32 overflow-y-auto">
          <p className="text-sm text-gray-700 whitespace-pre-wrap line-clamp-4">
            {record.content}
          </p>
        </div>

        {/* 底部資訊 */}
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>{formatRelativeTime(new Date(record.createdAt))}</span>
          <span className="capitalize">{record.language}</span>
        </div>
      </CardContent>
    </Card>
  );
}

// ==================== 生成對話框 ====================

function GenerateDialog() {
  const [open, setOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<string>("");
  const [contentType, setContentType] = useState<ContentType>("product_description");
  const [style, setStyle] = useState<ContentStyle>("professional");
  const [language, setLanguage] = useState<ContentLanguage>("zh-HK");

  const { data: productsData, isLoading: productsLoading } = useProducts({ limit: 100 });
  const generateMutation = useGenerateContent();

  const handleGenerate = () => {
    if (!selectedProduct) return;

    generateMutation.mutate(
      {
        productId: parseInt(selectedProduct),
        contentType,
        style,
        language,
      },
      {
        onSuccess: () => {
          setOpen(false);
          setSelectedProduct("");
        },
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Wand2 className="mr-2 h-4 w-4" />
          生成內容
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-brand-primary" />
            AI 內容生成
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* 選擇商品 */}
          <div className="space-y-2">
            <label className="text-sm font-medium">選擇商品</label>
            <Select value={selectedProduct} onValueChange={setSelectedProduct}>
              <SelectTrigger>
                <SelectValue placeholder="選擇要生成內容的商品" />
              </SelectTrigger>
              <SelectContent>
                {productsLoading ? (
                  <div className="p-2 text-center text-sm text-gray-500">載入中...</div>
                ) : (
                  productsData?.items.map((product) => (
                    <SelectItem key={product.id} value={product.id}>
                      {product.name}
                    </SelectItem>
                  ))
                )}
              </SelectContent>
            </Select>
          </div>

          {/* 內容類型 */}
          <div className="space-y-2">
            <label className="text-sm font-medium">內容類型</label>
            <Select value={contentType} onValueChange={(v) => setContentType(v as ContentType)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="product_description">商品描述</SelectItem>
                <SelectItem value="seo_title">SEO 標題</SelectItem>
                <SelectItem value="seo_description">SEO 描述</SelectItem>
                <SelectItem value="marketing_copy">行銷文案</SelectItem>
                <SelectItem value="social_post">社交貼文</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* 風格 */}
          <div className="space-y-2">
            <label className="text-sm font-medium">寫作風格</label>
            <Select value={style} onValueChange={(v) => setStyle(v as ContentStyle)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="professional">專業</SelectItem>
                <SelectItem value="casual">輕鬆</SelectItem>
                <SelectItem value="playful">活潑</SelectItem>
                <SelectItem value="luxury">高端</SelectItem>
                <SelectItem value="minimalist">簡約</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* 語言 */}
          <div className="space-y-2">
            <label className="text-sm font-medium">語言</label>
            <Select value={language} onValueChange={(v) => setLanguage(v as ContentLanguage)}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="zh-HK">繁體中文（香港）</SelectItem>
                <SelectItem value="zh-TW">繁體中文（台灣）</SelectItem>
                <SelectItem value="zh-CN">簡體中文</SelectItem>
                <SelectItem value="en">English</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">取消</Button>
          </DialogClose>
          <Button
            onClick={handleGenerate}
            disabled={!selectedProduct || generateMutation.isPending}
          >
            {generateMutation.isPending ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                生成中...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                開始生成
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// ==================== 載入骨架 ====================

function LoadingSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <Card key={i} className="stat-card">
          <CardContent className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div>
                <Skeleton className="h-5 w-32 mb-2" />
                <div className="flex gap-2">
                  <Skeleton className="h-5 w-16 rounded-full" />
                  <Skeleton className="h-5 w-14 rounded-full" />
                </div>
              </div>
              <Skeleton className="h-8 w-8" />
            </div>
            <Skeleton className="h-24 w-full rounded-lg mb-3" />
            <div className="flex justify-between">
              <Skeleton className="h-3 w-20" />
              <Skeleton className="h-3 w-12" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// ==================== 空狀態 ====================

function EmptyState() {
  return (
    <div className="empty-state">
      <Sparkles className="empty-state-icon" />
      <h3 className="empty-state-title">尚無生成內容</h3>
      <p className="empty-state-description">
        開始使用 AI 為您的商品生成專業文案
      </p>
      <GenerateDialog />
    </div>
  );
}

// ==================== AI 內容生成頁面 ====================

export default function ContentPage() {
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");

  const { data: recordsData, isLoading, error } = useContentRecords({
    status: statusFilter || undefined,
    contentType: typeFilter || undefined,
  });

  const updateStatusMutation = useUpdateContentStatus();

  const records = recordsData?.items || [];

  // 本地搜尋過濾
  const filteredRecords = records.filter((r) =>
    r.productName.toLowerCase().includes(searchQuery.toLowerCase()) ||
    r.content.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleApprove = (id: number) => {
    updateStatusMutation.mutate({ id, data: { status: "approved" } });
  };

  const handleReject = (id: number) => {
    updateStatusMutation.mutate({ id, data: { status: "rejected" } });
  };

  // 統計數據
  const stats = {
    total: records.length,
    draft: records.filter((r) => r.status === "draft").length,
    pending: records.filter((r) => r.status === "pending_review").length,
    approved: records.filter((r) => r.status === "approved").length,
    rejected: records.filter((r) => r.status === "rejected").length,
  };

  return (
    <div className="page-container">
      {/* 頁面標題 */}
      <div className="page-header">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="page-title flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-brand-primary" />
              AI 內容生成
            </h1>
            <p className="page-description">
              使用 AI 快速生成專業的商品文案與行銷內容
            </p>
          </div>
          <GenerateDialog />
        </div>
      </div>

      {/* 統計卡片 */}
      {!isLoading && records.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
          <Card className="stat-card">
            <CardContent className="p-4">
              <p className="stat-card-header">總生成數</p>
              <p className="stat-card-value mt-1">{stats.total}</p>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-4">
              <p className="stat-card-header">草稿</p>
              <p className="stat-card-value mt-1 text-gray-500">{stats.draft}</p>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-4">
              <p className="stat-card-header">待審核</p>
              <p className="stat-card-value mt-1 text-warning">{stats.pending}</p>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-4">
              <p className="stat-card-header">已通過</p>
              <p className="stat-card-value mt-1 text-success">{stats.approved}</p>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-4">
              <p className="stat-card-header">已拒絕</p>
              <p className="stat-card-value mt-1 text-error">{stats.rejected}</p>
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
              placeholder="搜尋商品或內容..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex h-10 w-full rounded-md border border-gray-300 bg-white pl-9 pr-3 py-2 text-sm focus:border-brand-primary focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
            />
          </div>

          <Select
            value={statusFilter}
            onValueChange={(v) => setStatusFilter(v === "all" ? "" : v)}
          >
            <SelectTrigger className="w-full md:w-[140px]">
              <SelectValue placeholder="全部狀態" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部狀態</SelectItem>
              <SelectItem value="draft">草稿</SelectItem>
              <SelectItem value="pending_review">待審核</SelectItem>
              <SelectItem value="approved">已通過</SelectItem>
              <SelectItem value="rejected">已拒絕</SelectItem>
            </SelectContent>
          </Select>

          <Select
            value={typeFilter}
            onValueChange={(v) => setTypeFilter(v === "all" ? "" : v)}
          >
            <SelectTrigger className="w-full md:w-[140px]">
              <Filter className="h-4 w-4 mr-2 text-gray-400" />
              <SelectValue placeholder="全部類型" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部類型</SelectItem>
              <SelectItem value="product_description">商品描述</SelectItem>
              <SelectItem value="seo_title">SEO 標題</SelectItem>
              <SelectItem value="seo_description">SEO 描述</SelectItem>
              <SelectItem value="marketing_copy">行銷文案</SelectItem>
              <SelectItem value="social_post">社交貼文</SelectItem>
            </SelectContent>
          </Select>
        </div>
      )}

      {/* 錯誤狀態 */}
      {error && (
        <div className="empty-state">
          <FileText className="empty-state-icon text-error" />
          <h3 className="empty-state-title">載入失敗</h3>
          <p className="empty-state-description">無法載入內容列表</p>
        </div>
      )}

      {/* 載入中 */}
      {isLoading && <LoadingSkeleton />}

      {/* 空狀態 */}
      {!isLoading && !error && records.length === 0 && <EmptyState />}

      {/* 內容列表 */}
      {!isLoading && !error && filteredRecords.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRecords.map((record) => (
            <ContentCard
              key={record.id}
              record={record}
              onApprove={handleApprove}
              onReject={handleReject}
            />
          ))}
        </div>
      )}

      {/* 無搜尋結果 */}
      {!isLoading && !error && records.length > 0 && filteredRecords.length === 0 && (
        <div className="empty-state">
          <Search className="empty-state-icon" />
          <h3 className="empty-state-title">找不到符合的內容</h3>
          <p className="empty-state-description">請嘗試調整篩選條件</p>
        </div>
      )}
    </div>
  );
}
