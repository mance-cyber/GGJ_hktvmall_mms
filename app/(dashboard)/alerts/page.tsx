"use client";

import { useState } from "react";
import { useAlerts, useMarkAlertsAsRead, useUnreadAlertsCount } from "@/lib/hooks/use-alerts";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Bell,
  BellOff,
  TrendingDown,
  TrendingUp,
  PackageX,
  Package,
  CheckCircle2,
  Filter,
  Search,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { formatRelativeTime, formatCurrency, cn } from "@/lib/utils";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { PriceAlert } from "@/types/api";

// ==================== 警報類型配置 ====================

const alertTypeConfig: Record<
  string,
  { label: string; icon: React.ElementType; color: string; bgColor: string }
> = {
  price_higher: {
    label: "價格上漲",
    icon: TrendingUp,
    color: "text-error-600",
    bgColor: "bg-error/10",
  },
  price_lower: {
    label: "價格下跌",
    icon: TrendingDown,
    color: "text-success-600",
    bgColor: "bg-success/10",
  },
  price_drop: {
    label: "價格下跌",
    icon: TrendingDown,
    color: "text-success-600",
    bgColor: "bg-success/10",
  },
  price_increase: {
    label: "價格上漲",
    icon: TrendingUp,
    color: "text-error-600",
    bgColor: "bg-error/10",
  },
  out_of_stock: {
    label: "缺貨警報",
    icon: PackageX,
    color: "text-warning-600",
    bgColor: "bg-warning/10",
  },
  back_in_stock: {
    label: "補貨通知",
    icon: Package,
    color: "text-info-600",
    bgColor: "bg-info/10",
  },
  price_equal: {
    label: "價格相同",
    icon: Bell,
    color: "text-gray-600",
    bgColor: "bg-gray-100",
  },
};

// ==================== 警報卡片組件 ====================

interface AlertCardProps {
  alert: PriceAlert;
  isSelected: boolean;
  onSelect: (id: number, selected: boolean) => void;
}

function AlertCard({ alert, isSelected, onSelect }: AlertCardProps) {
  const config = alertTypeConfig[alert.alertType] || alertTypeConfig.price_equal;
  const Icon = config.icon;

  return (
    <Card
      className={cn(
        "stat-card transition-all",
        !alert.isRead && "border-l-4 border-l-brand-primary",
        isSelected && "ring-2 ring-brand-primary/50"
      )}
    >
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          {/* 選擇框 */}
          <Checkbox
            checked={isSelected}
            onCheckedChange={(checked) => onSelect(alert.id, !!checked)}
            className="mt-1"
          />

          {/* 類型圖標 */}
          <div
            className={cn(
              "w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0",
              config.bgColor
            )}
          >
            <Icon className={cn("h-5 w-5", config.color)} />
          </div>

          {/* 內容 */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="font-medium text-gray-900 line-clamp-1">
                  {alert.productName}
                </p>
                <p className="text-sm text-gray-500">{alert.competitorName}</p>
              </div>
              <Badge
                variant="secondary"
                className={cn("flex-shrink-0", config.bgColor, config.color)}
              >
                {config.label}
              </Badge>
            </div>

            {/* 價格變動 */}
            <div className="mt-2 flex items-center gap-3">
              {alert.ourPrice > 0 && (
                <div className="text-sm">
                  <span className="text-gray-500">我們: </span>
                  <span className="font-medium">
                    {formatCurrency(alert.ourPrice)}
                  </span>
                </div>
              )}
              {alert.competitorPrice > 0 && (
                <div className="text-sm">
                  <span className="text-gray-500">對手: </span>
                  <span className="font-medium">
                    {formatCurrency(alert.competitorPrice)}
                  </span>
                </div>
              )}
              {alert.priceDifferencePercent !== 0 && (
                <div
                  className={cn(
                    "text-sm font-medium",
                    alert.priceDifferencePercent > 0
                      ? "text-error"
                      : "text-success"
                  )}
                >
                  {alert.priceDifferencePercent > 0 ? "+" : ""}
                  {alert.priceDifferencePercent.toFixed(1)}%
                </div>
              )}
            </div>

            {/* 時間 */}
            <p className="text-xs text-gray-400 mt-2">
              {formatRelativeTime(new Date(alert.createdAt))}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ==================== 空狀態組件 ====================

function EmptyState() {
  return (
    <div className="empty-state">
      <BellOff className="empty-state-icon" />
      <h3 className="empty-state-title">暫無警報</h3>
      <p className="empty-state-description">
        當競爭對手價格變動時，您將在這裡收到通知
      </p>
    </div>
  );
}

// ==================== 載入骨架 ====================

function LoadingSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3, 4, 5].map((i) => (
        <Card key={i} className="stat-card">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <Skeleton className="w-5 h-5 rounded" />
              <Skeleton className="w-10 h-10 rounded-lg" />
              <div className="flex-1">
                <Skeleton className="h-5 w-48 mb-1" />
                <Skeleton className="h-4 w-32 mb-2" />
                <div className="flex gap-3">
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-4 w-20" />
                </div>
              </div>
              <Skeleton className="h-5 w-16 rounded-full" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// ==================== 價格警報頁面 ====================

export default function AlertsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [readFilter, setReadFilter] = useState<string>("");
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [page, setPage] = useState(1);
  const limit = 20;

  // 獲取警報列表
  const { data: alertsData, isLoading, error } = useAlerts({
    alertType: typeFilter || undefined,
    isRead: readFilter === "read" ? true : readFilter === "unread" ? false : undefined,
    page,
    limit,
  });

  // 獲取未讀數量
  const { data: unreadData } = useUnreadAlertsCount();

  // 批量標記已讀
  const markAsReadMutation = useMarkAlertsAsRead();

  const alerts = alertsData?.items || [];
  const total = alertsData?.total || 0;
  const totalPages = Math.ceil(total / limit);
  const unreadCount = unreadData?.count || 0;

  // 本地搜尋過濾
  const filteredAlerts = alerts.filter(
    (a) =>
      a.productName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      a.competitorName?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // 選擇處理
  const handleSelect = (id: number, selected: boolean) => {
    if (selected) {
      setSelectedIds((prev) => [...prev, id]);
    } else {
      setSelectedIds((prev) => prev.filter((i) => i !== id));
    }
  };

  const handleSelectAll = () => {
    if (selectedIds.length === filteredAlerts.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(filteredAlerts.map((a) => a.id));
    }
  };

  const handleMarkAsRead = () => {
    if (selectedIds.length === 0) return;
    markAsReadMutation.mutate(selectedIds, {
      onSuccess: () => setSelectedIds([]),
    });
  };

  return (
    <div className="page-container">
      {/* 頁面標題 */}
      <div className="page-header">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="page-title flex items-center gap-2">
              <Bell className="h-6 w-6 text-brand-primary" />
              價格警報
              {unreadCount > 0 && (
                <Badge className="ml-2 bg-error text-white">
                  {unreadCount} 未讀
                </Badge>
              )}
            </h1>
            <p className="page-description">
              監控競爭對手價格變動，及時掌握市場動態
            </p>
          </div>
          {selectedIds.length > 0 && (
            <Button onClick={handleMarkAsRead} disabled={markAsReadMutation.isPending}>
              <CheckCircle2 className="mr-2 h-4 w-4" />
              標記 {selectedIds.length} 項為已讀
            </Button>
          )}
        </div>
      </div>

      {/* 統計卡片 */}
      {!isLoading && alerts.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <Card className="stat-card">
            <CardContent className="p-4">
              <p className="stat-card-header">總警報數</p>
              <p className="stat-card-value mt-1">{total}</p>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-4">
              <p className="stat-card-header">未讀</p>
              <p className="stat-card-value mt-1 text-brand-primary">
                {unreadCount}
              </p>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-4">
              <p className="stat-card-header">降價警報</p>
              <p className="stat-card-value mt-1 text-success">
                {alerts.filter((a) => a.alertType === "price_lower" || a.alertType === "price_drop").length}
              </p>
            </CardContent>
          </Card>
          <Card className="stat-card">
            <CardContent className="p-4">
              <p className="stat-card-header">漲價警報</p>
              <p className="stat-card-value mt-1 text-error">
                {alerts.filter((a) => a.alertType === "price_higher" || a.alertType === "price_increase").length}
              </p>
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
              placeholder="搜尋商品或競爭對手..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex h-10 w-full rounded-md border border-gray-300 bg-white pl-9 pr-3 py-2 text-sm focus:border-brand-primary focus:outline-none focus:ring-2 focus:ring-brand-primary/20"
            />
          </div>

          <Select
            value={typeFilter}
            onValueChange={(v) => {
              setTypeFilter(v === "all" ? "" : v);
              setPage(1);
            }}
          >
            <SelectTrigger className="w-full md:w-[140px]">
              <Filter className="h-4 w-4 mr-2 text-gray-400" />
              <SelectValue placeholder="全部類型" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部類型</SelectItem>
              <SelectItem value="price_drop">降價</SelectItem>
              <SelectItem value="price_increase">漲價</SelectItem>
              <SelectItem value="out_of_stock">缺貨</SelectItem>
              <SelectItem value="back_in_stock">補貨</SelectItem>
            </SelectContent>
          </Select>

          <Select
            value={readFilter}
            onValueChange={(v) => {
              setReadFilter(v === "all" ? "" : v);
              setPage(1);
            }}
          >
            <SelectTrigger className="w-full md:w-[120px]">
              <SelectValue placeholder="全部狀態" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">全部狀態</SelectItem>
              <SelectItem value="unread">未讀</SelectItem>
              <SelectItem value="read">已讀</SelectItem>
            </SelectContent>
          </Select>

          {filteredAlerts.length > 0 && (
            <Button variant="outline" onClick={handleSelectAll} className="ml-auto">
              {selectedIds.length === filteredAlerts.length ? "取消全選" : "全選"}
            </Button>
          )}
        </div>
      )}

      {/* 錯誤狀態 */}
      {error && (
        <div className="empty-state">
          <Bell className="empty-state-icon text-error" />
          <h3 className="empty-state-title">載入失敗</h3>
          <p className="empty-state-description">無法載入警報列表</p>
        </div>
      )}

      {/* 載入中 */}
      {isLoading && <LoadingSkeleton />}

      {/* 空狀態 */}
      {!isLoading && !error && alerts.length === 0 && <EmptyState />}

      {/* 警報列表 */}
      {!isLoading && !error && filteredAlerts.length > 0 && (
        <div className="space-y-3">
          {filteredAlerts.map((alert) => (
            <AlertCard
              key={alert.id}
              alert={alert}
              isSelected={selectedIds.includes(alert.id)}
              onSelect={handleSelect}
            />
          ))}
        </div>
      )}

      {/* 無搜尋結果 */}
      {!isLoading && !error && alerts.length > 0 && filteredAlerts.length === 0 && (
        <div className="empty-state">
          <Search className="empty-state-icon" />
          <h3 className="empty-state-title">找不到符合的警報</h3>
          <p className="empty-state-description">請嘗試調整篩選條件</p>
        </div>
      )}

      {/* 分頁 */}
      {!isLoading && !error && totalPages > 1 && (
        <div className="flex items-center justify-between mt-6">
          <p className="text-sm text-gray-500">
            共 {total} 條警報，第 {page} / {totalPages} 頁
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
