"use client";

import { useState } from "react";
import { useCompetitors } from "@/lib/hooks/use-competitors";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import {
  Plus,
  Users,
  ExternalLink,
  MoreVertical,
  Edit,
  Trash2,
  Play,
  PackageOpen,
} from "lucide-react";
import { formatRelativeTime } from "@/lib/utils";
import Link from "next/link";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

// ==================== 競爭對手卡片組件 ====================

interface CompetitorCardProps {
  competitor: {
    id: number;
    name: string;
    platform: string;
    baseUrl: string;
    monitoredProductsCount: number;
    lastScrapedAt: string | null;
    isActive: boolean;
  };
}

function CompetitorCard({ competitor }: CompetitorCardProps) {
  const platformColors: Record<string, string> = {
    hktvmall: "bg-purple-100 text-purple-700",
    taobao: "bg-orange-100 text-orange-700",
    jd: "bg-red-100 text-red-700",
    amazon: "bg-yellow-100 text-yellow-700",
    other: "bg-gray-100 text-gray-700",
  };

  const platformColor = platformColors[competitor.platform] || platformColors.other;

  return (
    <Card className="stat-card">
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <h3 className="text-lg font-semibold text-gray-900">
                {competitor.name}
              </h3>
              <Badge
                variant={competitor.isActive ? "default" : "secondary"}
                className={competitor.isActive ? "" : "bg-gray-200 text-gray-600"}
              >
                {competitor.isActive ? "啟用" : "停用"}
              </Badge>
            </div>
            <div className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${platformColor}`}>
              {competitor.platform.toUpperCase()}
            </div>
          </div>

          {/* 操作菜單 */}
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
              <DropdownMenuItem>
                <Play className="mr-2 h-4 w-4" />
                立即爬取
              </DropdownMenuItem>
              <DropdownMenuItem className="text-error-600">
                <Trash2 className="mr-2 h-4 w-4" />
                刪除
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* 統計資訊 */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <p className="text-xs text-gray-500">監控商品</p>
            <p className="text-xl font-bold text-gray-900 font-tabular">
              {competitor.monitoredProductsCount}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">最後爬取</p>
            <p className="text-sm text-gray-700">
              {competitor.lastScrapedAt
                ? formatRelativeTime(new Date(competitor.lastScrapedAt))
                : "尚未爬取"}
            </p>
          </div>
        </div>

        {/* 網址 */}
        <div className="mb-4">
          <p className="text-xs text-gray-500 mb-1">網址</p>
          <a
            href={competitor.baseUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-brand-primary hover:underline flex items-center gap-1 truncate"
          >
            <span className="truncate">{competitor.baseUrl}</span>
            <ExternalLink className="h-3 w-3 flex-shrink-0" />
          </a>
        </div>

        {/* 查看詳情按鈕 */}
        <Link href={`/competitors/${competitor.id}`}>
          <Button variant="outline" className="w-full">
            查看商品列表
          </Button>
        </Link>
      </CardContent>
    </Card>
  );
}

// ==================== 空狀態組件 ====================

function EmptyState() {
  return (
    <div className="empty-state">
      <PackageOpen className="empty-state-icon" />
      <h3 className="empty-state-title">尚無競爭對手</h3>
      <p className="empty-state-description">
        開始添加競爭對手以追蹤價格與市場動態
      </p>
      <Button className="mt-4">
        <Plus className="mr-2 h-4 w-4" />
        新增第一個競爭對手
      </Button>
    </div>
  );
}

// ==================== 載入骨架組件 ====================

function LoadingSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <Card key={i} className="stat-card">
          <CardContent className="p-5">
            <Skeleton className="h-6 w-32 mb-4" />
            <Skeleton className="h-4 w-20 mb-4" />
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <Skeleton className="h-3 w-16 mb-2" />
                <Skeleton className="h-6 w-12" />
              </div>
              <div>
                <Skeleton className="h-3 w-16 mb-2" />
                <Skeleton className="h-4 w-20" />
              </div>
            </div>
            <Skeleton className="h-10 w-full" />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// ==================== 競爭對手列表頁面 ====================

export default function CompetitorsPage() {
  const { data: competitors, isLoading, error } = useCompetitors();
  const [searchQuery, setSearchQuery] = useState("");

  // 篩選競爭對手
  const filteredCompetitors = competitors?.filter((c) =>
    c.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="page-container">
      {/* 頁面標題 */}
      <div className="page-header">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="page-title">競爭對手監控</h1>
            <p className="page-description">
              管理競爭對手並監控商品價格變動
            </p>
          </div>
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            新增競爭對手
          </Button>
        </div>
      </div>

      {/* 統計卡片 */}
      {!isLoading && competitors && competitors.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="stat-card">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="stat-card-header">總競爭對手數</p>
                  <p className="stat-card-value mt-2">{competitors.length}</p>
                </div>
                <Users className="h-10 w-10 text-brand-primary/30" />
              </div>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="stat-card-header">啟用中</p>
                  <p className="stat-card-value mt-2">
                    {competitors.filter((c) => c.isActive).length}
                  </p>
                </div>
                <div className="h-10 w-10 rounded-full bg-success/20 flex items-center justify-center">
                  <div className="h-4 w-4 rounded-full bg-success"></div>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="stat-card-header">總監控商品</p>
                  <p className="stat-card-value mt-2">
                    {competitors.reduce(
                      (sum, c) => sum + c.monitoredProductsCount,
                      0
                    )}
                  </p>
                </div>
                <PackageOpen className="h-10 w-10 text-brand-primary/30" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* 搜尋與篩選 */}
      {!isLoading && competitors && competitors.length > 0 && (
        <div className="flex gap-2 mb-6">
          <input
            type="search"
            placeholder="搜尋競爭對手..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex h-10 w-full md:w-[300px] rounded-md border border-gray-300 bg-white px-3 py-2 text-sm focus:border-brand-primary focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
          />
        </div>
      )}

      {/* 競爭對手列表 */}
      {error && (
        <div className="empty-state">
          <Users className="empty-state-icon text-error" />
          <h3 className="empty-state-title">載入失敗</h3>
          <p className="empty-state-description">無法載入競爭對手列表</p>
        </div>
      )}

      {isLoading && <LoadingSkeleton />}

      {!isLoading && competitors && competitors.length === 0 && <EmptyState />}

      {!isLoading &&
        filteredCompetitors &&
        filteredCompetitors.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCompetitors.map((competitor) => (
              <CompetitorCard key={competitor.id} competitor={competitor} />
            ))}
          </div>
        )}

      {!isLoading &&
        filteredCompetitors &&
        filteredCompetitors.length === 0 &&
        searchQuery && (
          <div className="empty-state">
            <Users className="empty-state-icon" />
            <h3 className="empty-state-title">找不到符合的結果</h3>
            <p className="empty-state-description">
              請嘗試調整搜尋關鍵字
            </p>
          </div>
        )}
    </div>
  );
}
