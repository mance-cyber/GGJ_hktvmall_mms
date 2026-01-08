"use client";

import { useState, useEffect } from "react";
import {
  useScrapeLogs,
  useScrapeStats,
  useRunningScrapeTasks,
  useTriggerScrape,
  usePreviewScrape,
  useDiscoverUrls,
  useScheduleConfig,
  useUpdateScheduleConfig,
  useFailedProducts,
  useRetryFailedProducts,
  useScrapeConfigs,
  useCreateScrapeConfig,
  useUpdateScrapeConfig,
  useDeleteScrapeConfig,
  useTestScrapeConfig,
} from "@/lib/hooks/use-scrape";
import type { ScrapeConfig } from "@/lib/api/scrape";
import { useCompetitors } from "@/lib/hooks/use-competitors";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Database,
  Play,
  RefreshCw,
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Loader2,
  ChevronLeft,
  ChevronRight,
  Timer,
  Package,
  TrendingUp,
  Activity,
  Search,
  Link,
  Settings,
  RotateCcw,
  ExternalLink,
  Calendar,
  Zap,
  Globe,
  Image,
  Star,
  Tag,
  Plus,
  Edit2,
  Trash2,
  Server,
  Shield,
  Network,
} from "lucide-react";
import { formatRelativeTime, cn } from "@/lib/utils";
import type { ScrapeLog, ScrapePreviewResult, FailedProduct } from "@/lib/api/scrape";

// ==================== 狀態配置 ====================

const statusConfig: Record<
  string,
  { label: string; icon: React.ElementType; color: string; bgColor: string }
> = {
  pending: {
    label: "等待中",
    icon: Clock,
    color: "text-gray-600",
    bgColor: "bg-gray-100",
  },
  running: {
    label: "運行中",
    icon: Loader2,
    color: "text-blue-600",
    bgColor: "bg-blue-100",
  },
  success: {
    label: "成功",
    icon: CheckCircle2,
    color: "text-success-600",
    bgColor: "bg-success/10",
  },
  partial: {
    label: "部分成功",
    icon: AlertTriangle,
    color: "text-warning-600",
    bgColor: "bg-warning/10",
  },
  failed: {
    label: "失敗",
    icon: XCircle,
    color: "text-error-600",
    bgColor: "bg-error/10",
  },
};

// ==================== 統計卡片組件 ====================

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ElementType;
  trend?: string;
  trendUp?: boolean;
}

function StatCard({ title, value, icon: Icon, trend, trendUp }: StatCardProps) {
  return (
    <Card className="stat-card">
      <CardContent className="p-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="stat-card-header">{title}</p>
            <p className="stat-card-value mt-2">{value}</p>
            {trend && (
              <p
                className={cn(
                  "text-xs mt-1",
                  trendUp ? "text-success" : "text-error"
                )}
              >
                {trend}
              </p>
            )}
          </div>
          <Icon className="h-10 w-10 text-brand-primary/30" />
        </div>
      </CardContent>
    </Card>
  );
}

// ==================== 運行中任務卡片 ====================

interface RunningTaskCardProps {
  task: ScrapeLog;
}

function RunningTaskCard({ task }: RunningTaskCardProps) {
  const progress =
    task.productsTotal > 0
      ? Math.round((task.productsScraped / task.productsTotal) * 100)
      : 0;

  return (
    <Card className="stat-card border-l-4 border-l-blue-500">
      <CardContent className="p-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
            <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />
          </div>
          <div className="flex-1">
            <p className="font-medium text-gray-900">
              {task.competitorName || "全部競爭對手"}
            </p>
            <div className="flex items-center gap-2 text-sm text-gray-500 mt-1">
              <span>
                {task.productsScraped} / {task.productsTotal} 商品
              </span>
              <span className="text-blue-600 font-medium">{progress}%</span>
            </div>
            {/* 進度條 */}
            <div className="w-full bg-gray-200 rounded-full h-1.5 mt-2">
              <div
                className="bg-blue-500 h-1.5 rounded-full transition-all"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ==================== 日誌記錄卡片 ====================

interface LogCardProps {
  log: ScrapeLog;
}

function LogCard({ log }: LogCardProps) {
  const config = statusConfig[log.status] || statusConfig.pending;
  const Icon = config.icon;

  return (
    <Card className="stat-card">
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          {/* 狀態圖標 */}
          <div
            className={cn(
              "w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0",
              config.bgColor
            )}
          >
            <Icon
              className={cn(
                "h-5 w-5",
                config.color,
                log.status === "running" && "animate-spin"
              )}
            />
          </div>

          {/* 內容 */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="font-medium text-gray-900">
                  {log.competitorName || "全部競爭對手"}
                </p>
                <p className="text-sm text-gray-500 capitalize">
                  {log.taskType?.replace(/_/g, " ") || "未知任務"}
                </p>
              </div>
              <Badge className={cn("flex-shrink-0", config.bgColor, config.color)}>
                {config.label}
              </Badge>
            </div>

            {/* 統計 */}
            <div className="mt-2 flex items-center gap-4 text-sm">
              <div className="flex items-center gap-1">
                <Package className="h-4 w-4 text-gray-400" />
                <span>
                  {log.productsScraped}/{log.productsTotal}
                </span>
              </div>
              {log.productsFailed > 0 && (
                <div className="flex items-center gap-1 text-error">
                  <XCircle className="h-4 w-4" />
                  <span>{log.productsFailed} 失敗</span>
                </div>
              )}
              {log.durationSeconds && (
                <div className="flex items-center gap-1 text-gray-500">
                  <Timer className="h-4 w-4" />
                  <span>{log.durationSeconds}s</span>
                </div>
              )}
            </div>

            {/* 時間 */}
            <p className="text-xs text-gray-400 mt-2">
              {log.startedAt
                ? formatRelativeTime(new Date(log.startedAt))
                : formatRelativeTime(new Date(log.createdAt))}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
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
              <Skeleton className="w-10 h-10 rounded-lg" />
              <div className="flex-1">
                <Skeleton className="h-5 w-48 mb-1" />
                <Skeleton className="h-4 w-32 mb-2" />
                <div className="flex gap-3">
                  <Skeleton className="h-4 w-16" />
                  <Skeleton className="h-4 w-16" />
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

// ==================== 抓取預覽組件 ====================

function ScrapePreviewSection() {
  const [url, setUrl] = useState("");
  const [useActions, setUseActions] = useState(false);
  const previewMutation = usePreviewScrape();

  const handlePreview = () => {
    if (!url.trim()) return;
    previewMutation.mutate({ url: url.trim(), useActions });
  };

  const result = previewMutation.data;

  return (
    <div className="space-y-6">
      {/* 輸入區域 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Search className="h-5 w-5" />
            抓取預覽測試
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="preview-url">商品頁面 URL</Label>
            <div className="flex gap-2">
              <Input
                id="preview-url"
                placeholder="https://www.hktvmall.com/product/..."
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1"
              />
              <Button
                onClick={handlePreview}
                disabled={!url.trim() || previewMutation.isPending}
              >
                {previewMutation.isPending ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <Zap className="h-4 w-4 mr-2" />
                )}
                測試抓取
              </Button>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Switch
              id="use-actions"
              checked={useActions}
              onCheckedChange={setUseActions}
            />
            <Label htmlFor="use-actions" className="text-sm text-gray-600">
              使用 Actions（用於動態頁面，需要滾動載入內容）
            </Label>
          </div>
        </CardContent>
      </Card>

      {/* 結果展示 */}
      {result && (
        <Card className={result.success ? "border-success/50" : "border-error/50"}>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              {result.success ? (
                <CheckCircle2 className="h-5 w-5 text-success" />
              ) : (
                <XCircle className="h-5 w-5 text-error" />
              )}
              抓取結果
              {result.durationMs && (
                <Badge variant="outline" className="ml-auto">
                  耗時 {result.durationMs}ms
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {result.success ? (
              <PreviewResultDisplay result={result} />
            ) : (
              <div className="text-error">
                <p className="font-medium">抓取失敗</p>
                <p className="text-sm mt-1">{result.error}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// ==================== 預覽結果展示 ====================

function PreviewResultDisplay({ result }: { result: ScrapePreviewResult }) {
  return (
    <div className="grid md:grid-cols-3 gap-6">
      {/* 左側：圖片 */}
      <div className="md:col-span-1">
        {result.imageUrl ? (
          <div className="aspect-square rounded-lg overflow-hidden bg-gray-100">
            <img
              src={result.imageUrl}
              alt={result.name || "商品圖片"}
              className="w-full h-full object-cover"
            />
          </div>
        ) : (
          <div className="aspect-square rounded-lg bg-gray-100 flex items-center justify-center">
            <Image className="h-12 w-12 text-gray-300" />
          </div>
        )}
      </div>

      {/* 右側：商品資訊 */}
      <div className="md:col-span-2 space-y-4">
        {/* 商品名稱 */}
        <div>
          <h3 className="text-xl font-semibold text-gray-900">
            {result.name || "未知商品"}
          </h3>
          {result.brand && (
            <p className="text-sm text-gray-500 mt-1">品牌：{result.brand}</p>
          )}
        </div>

        {/* 價格信息 */}
        <div className="flex items-baseline gap-3">
          {result.price !== null && (
            <span className="text-2xl font-bold text-brand-primary">
              HK${result.price.toFixed(2)}
            </span>
          )}
          {result.originalPrice !== null && result.originalPrice !== result.price && (
            <span className="text-lg text-gray-400 line-through">
              HK${result.originalPrice.toFixed(2)}
            </span>
          )}
          {result.discountPercent !== null && result.discountPercent > 0 && (
            <Badge className="bg-error text-white">
              -{result.discountPercent.toFixed(0)}%
            </Badge>
          )}
        </div>

        {/* 其他信息 */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          {result.sku && (
            <div className="flex items-center gap-2">
              <Tag className="h-4 w-4 text-gray-400" />
              <span>SKU: {result.sku}</span>
            </div>
          )}
          {result.stockStatus && (
            <div className="flex items-center gap-2">
              <Package className="h-4 w-4 text-gray-400" />
              <span>
                {result.stockStatus === "in_stock"
                  ? "有貨"
                  : result.stockStatus === "out_of_stock"
                  ? "缺貨"
                  : result.stockStatus === "low_stock"
                  ? "庫存緊張"
                  : result.stockStatus}
              </span>
            </div>
          )}
          {result.rating !== null && (
            <div className="flex items-center gap-2">
              <Star className="h-4 w-4 text-yellow-400" />
              <span>
                {result.rating.toFixed(1)}{" "}
                {result.reviewCount !== null && `(${result.reviewCount} 評價)`}
              </span>
            </div>
          )}
        </div>

        {/* 促銷信息 */}
        {result.promotionText && (
          <div className="bg-warning/10 text-warning-700 px-3 py-2 rounded-lg text-sm">
            {result.promotionText}
          </div>
        )}

        {/* 描述 */}
        {result.description && (
          <div className="text-sm text-gray-600 line-clamp-3">
            {result.description}
          </div>
        )}

        {/* URL */}
        <a
          href={result.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-brand-primary hover:underline inline-flex items-center gap-1"
        >
          <ExternalLink className="h-3 w-3" />
          查看原始頁面
        </a>
      </div>
    </div>
  );
}

// ==================== URL 發現組件 ====================

function UrlDiscoverySection() {
  const [baseUrl, setBaseUrl] = useState("");
  const [keywords, setKeywords] = useState("");
  const discoverMutation = useDiscoverUrls();

  const handleDiscover = () => {
    if (!baseUrl.trim()) return;
    const keywordList = keywords
      .split(",")
      .map((k) => k.trim())
      .filter(Boolean);
    discoverMutation.mutate({
      baseUrl: baseUrl.trim(),
      keywords: keywordList.length > 0 ? keywordList : undefined,
    });
  };

  const result = discoverMutation.data;

  return (
    <div className="space-y-6">
      {/* 輸入區域 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Globe className="h-5 w-5" />
            URL 發現工具
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="base-url">網站根 URL</Label>
            <Input
              id="base-url"
              placeholder="https://www.hktvmall.com"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="keywords">
              過濾關鍵詞（可選，逗號分隔）
            </Label>
            <Input
              id="keywords"
              placeholder="product, item, pd/, 商品"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
            />
            <p className="text-xs text-gray-500">
              留空將使用預設關鍵詞：product, item, goods, 商品, p/, pd/
            </p>
          </div>

          <Button
            onClick={handleDiscover}
            disabled={!baseUrl.trim() || discoverMutation.isPending}
          >
            {discoverMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <Search className="h-4 w-4 mr-2" />
            )}
            發現 URL
          </Button>
        </CardContent>
      </Card>

      {/* 結果展示 */}
      {result && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Link className="h-5 w-5" />
              發現結果
              <Badge variant="outline" className="ml-2">
                共 {result.total} 個 URL
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent>
            {result.urls.length > 0 ? (
              <div className="max-h-96 overflow-y-auto space-y-2">
                {result.urls.map((url, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 bg-gray-50 rounded-lg hover:bg-gray-100"
                  >
                    <span className="text-sm text-gray-700 truncate flex-1 mr-2">
                      {url}
                    </span>
                    <a
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-brand-primary hover:text-brand-primary/80"
                      title="在新分頁中打開"
                      aria-label="在新分頁中打開此 URL"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">
                未找到符合條件的 URL
              </p>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// ==================== 定時任務配置組件 ====================

function ScheduleConfigSection() {
  const { data: config, isLoading } = useScheduleConfig();
  const updateMutation = useUpdateScheduleConfig();

  const [enabled, setEnabled] = useState(config?.enabled ?? false);
  const [cronExpression, setCronExpression] = useState(config?.cronExpression ?? "");

  // 當遠程配置載入完成時同步到本地狀態
  useEffect(() => {
    if (config) {
      setEnabled(config.enabled);
      setCronExpression(config.cronExpression);
    }
  }, [config]);

  const handleSave = () => {
    updateMutation.mutate({ enabled, cronExpression });
  };

  // 預設 Cron 表達式
  const presetCrons = [
    { label: "每天凌晨 2 點", value: "0 2 * * *" },
    { label: "每 6 小時", value: "0 */6 * * *" },
    { label: "每週一凌晨 3 點", value: "0 3 * * 1" },
    { label: "每 12 小時", value: "0 */12 * * *" },
  ];

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-32" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Calendar className="h-5 w-5" />
          定時任務配置
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 啟用開關 */}
        <div className="flex items-center justify-between">
          <div>
            <Label htmlFor="schedule-enabled" className="text-base">
              啟用定時抓取
            </Label>
            <p className="text-sm text-gray-500">
              開啟後將按照設定的時間自動執行抓取任務
            </p>
          </div>
          <Switch
            id="schedule-enabled"
            checked={enabled}
            onCheckedChange={setEnabled}
          />
        </div>

        {/* Cron 表達式 */}
        <div className="space-y-2">
          <Label htmlFor="cron-expression">Cron 表達式</Label>
          <Input
            id="cron-expression"
            placeholder="0 2 * * *"
            value={cronExpression}
            onChange={(e) => setCronExpression(e.target.value)}
          />
          <div className="flex flex-wrap gap-2 mt-2">
            {presetCrons.map((preset) => (
              <Button
                key={preset.value}
                variant="outline"
                size="sm"
                onClick={() => setCronExpression(preset.value)}
                className={cn(
                  cronExpression === preset.value && "border-brand-primary text-brand-primary"
                )}
              >
                {preset.label}
              </Button>
            ))}
          </div>
        </div>

        {/* 上次/下次執行時間 */}
        {config && (
          <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
            <div>
              <p className="text-sm text-gray-500">上次執行</p>
              <p className="font-medium">
                {config.lastRunAt
                  ? formatRelativeTime(new Date(config.lastRunAt))
                  : "從未執行"}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-500">下次執行</p>
              <p className="font-medium">
                {config.nextRunAt
                  ? new Date(config.nextRunAt).toLocaleString("zh-HK")
                  : "未排程"}
              </p>
            </div>
          </div>
        )}

        {/* 保存按鈕 */}
        <Button
          onClick={handleSave}
          disabled={updateMutation.isPending}
        >
          {updateMutation.isPending ? (
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
          ) : (
            <Settings className="h-4 w-4 mr-2" />
          )}
          保存配置
        </Button>
      </CardContent>
    </Card>
  );
}

// ==================== 失敗商品重試組件 ====================

function FailedProductsSection() {
  const { data: failedProducts, isLoading } = useFailedProducts(50);
  const retryMutation = useRetryFailedProducts();
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const handleSelectAll = () => {
    if (selectedIds.length === failedProducts?.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(failedProducts?.map((p) => p.id) || []);
    }
  };

  const handleSelect = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleRetrySelected = () => {
    if (selectedIds.length === 0) return;
    retryMutation.mutate({ productIds: selectedIds });
    setSelectedIds([]);
  };

  const handleRetryAll = () => {
    retryMutation.mutate({ retryAll: true });
  };

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  if (!failedProducts || failedProducts.length === 0) {
    return (
      <div className="empty-state">
        <CheckCircle2 className="empty-state-icon text-success" />
        <h3 className="empty-state-title">沒有失敗的商品</h3>
        <p className="empty-state-description">
          所有商品抓取都正常運作中
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* 操作欄 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="select-all-failed"
            checked={selectedIds.length === failedProducts.length}
            onChange={handleSelectAll}
            className="rounded border-gray-300"
            aria-label="全選失敗商品"
          />
          <label htmlFor="select-all-failed" className="text-sm text-gray-500">
            已選擇 {selectedIds.length} / {failedProducts.length}
          </label>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRetrySelected}
            disabled={selectedIds.length === 0 || retryMutation.isPending}
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            重試選中
          </Button>
          <Button
            size="sm"
            onClick={handleRetryAll}
            disabled={retryMutation.isPending}
          >
            {retryMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-2" />
            )}
            重試全部
          </Button>
        </div>
      </div>

      {/* 失敗商品列表 */}
      <div className="space-y-2">
        {failedProducts.map((product) => (
          <FailedProductCard
            key={product.id}
            product={product}
            selected={selectedIds.includes(product.id)}
            onSelect={() => handleSelect(product.id)}
          />
        ))}
      </div>
    </div>
  );
}

// ==================== 失敗商品卡片 ====================

interface FailedProductCardProps {
  product: FailedProduct;
  selected: boolean;
  onSelect: () => void;
}

function FailedProductCard({ product, selected, onSelect }: FailedProductCardProps) {
  return (
    <Card className={cn("stat-card", selected && "border-brand-primary")}>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <input
            type="checkbox"
            id={`failed-product-${product.id}`}
            checked={selected}
            onChange={onSelect}
            className="mt-1 rounded border-gray-300"
            aria-label={`選擇 ${product.name}`}
          />
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="font-medium text-gray-900 truncate">
                  {product.name}
                </p>
                <p className="text-sm text-gray-500">{product.competitorName}</p>
              </div>
              <Badge className="bg-error/10 text-error flex-shrink-0">
                失敗
              </Badge>
            </div>

            {product.error && (
              <p className="text-sm text-error mt-2 line-clamp-2">
                {product.error}
              </p>
            )}

            <div className="flex items-center justify-between mt-2">
              <a
                href={product.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-brand-primary hover:underline inline-flex items-center gap-1"
              >
                <ExternalLink className="h-3 w-3" />
                查看商品頁面
              </a>
              {product.lastScrapedAt && (
                <span className="text-xs text-gray-400">
                  上次嘗試: {formatRelativeTime(new Date(product.lastScrapedAt))}
                </span>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ==================== 平台配置組件 ====================

function PlatformConfigSection() {
  const { data: configsData, isLoading } = useScrapeConfigs();
  const createMutation = useCreateScrapeConfig();
  const updateMutation = useUpdateScrapeConfig();
  const deleteMutation = useDeleteScrapeConfig();
  const testMutation = useTestScrapeConfig();

  const [editingConfig, setEditingConfig] = useState<ScrapeConfig | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [testUrl, setTestUrl] = useState("");
  const [testingPlatform, setTestingPlatform] = useState<string | null>(null);

  // 新建/編輯表單狀態
  const [formData, setFormData] = useState({
    platform: "",
    rateLimitRequests: 10,
    rateLimitWindowSeconds: 60,
    concurrentLimit: 3,
    maxRetries: 3,
    retryDelaySeconds: 5,
    timeoutSeconds: 30,
    useActions: false,
    proxyEnabled: false,
    isActive: true,
  });

  const handleCreate = () => {
    setIsCreating(true);
    setEditingConfig(null);
    setFormData({
      platform: "",
      rateLimitRequests: 10,
      rateLimitWindowSeconds: 60,
      concurrentLimit: 3,
      maxRetries: 3,
      retryDelaySeconds: 5,
      timeoutSeconds: 30,
      useActions: false,
      proxyEnabled: false,
      isActive: true,
    });
  };

  const handleEdit = (config: ScrapeConfig) => {
    setEditingConfig(config);
    setIsCreating(false);
    setFormData({
      platform: config.platform,
      rateLimitRequests: config.rateLimitRequests,
      rateLimitWindowSeconds: config.rateLimitWindowSeconds,
      concurrentLimit: config.concurrentLimit,
      maxRetries: config.maxRetries,
      retryDelaySeconds: config.retryDelaySeconds,
      timeoutSeconds: config.timeoutSeconds,
      useActions: config.useActions,
      proxyEnabled: config.proxyEnabled,
      isActive: config.isActive,
    });
  };

  const handleSave = () => {
    if (isCreating) {
      createMutation.mutate({
        platform: formData.platform,
        rateLimitRequests: formData.rateLimitRequests,
        rateLimitWindowSeconds: formData.rateLimitWindowSeconds,
        concurrentLimit: formData.concurrentLimit,
        maxRetries: formData.maxRetries,
        retryDelaySeconds: formData.retryDelaySeconds,
        timeoutSeconds: formData.timeoutSeconds,
        useActions: formData.useActions,
        proxyEnabled: formData.proxyEnabled,
      }, {
        onSuccess: () => {
          setIsCreating(false);
          setFormData({
            platform: "",
            rateLimitRequests: 10,
            rateLimitWindowSeconds: 60,
            concurrentLimit: 3,
            maxRetries: 3,
            retryDelaySeconds: 5,
            timeoutSeconds: 30,
            useActions: false,
            proxyEnabled: false,
            isActive: true,
          });
        },
      });
    } else if (editingConfig) {
      updateMutation.mutate({
        platform: editingConfig.platform,
        data: {
          rateLimitRequests: formData.rateLimitRequests,
          rateLimitWindowSeconds: formData.rateLimitWindowSeconds,
          concurrentLimit: formData.concurrentLimit,
          maxRetries: formData.maxRetries,
          retryDelaySeconds: formData.retryDelaySeconds,
          timeoutSeconds: formData.timeoutSeconds,
          useActions: formData.useActions,
          proxyEnabled: formData.proxyEnabled,
          isActive: formData.isActive,
        },
      }, {
        onSuccess: () => {
          setEditingConfig(null);
        },
      });
    }
  };

  const handleDelete = (platform: string) => {
    if (confirm(`確定要刪除平台 "${platform}" 的配置嗎？`)) {
      deleteMutation.mutate(platform);
    }
  };

  const handleTest = (platform: string) => {
    if (!testUrl.trim()) return;
    setTestingPlatform(platform);
    testMutation.mutate({ platform, testUrl: testUrl.trim() }, {
      onSettled: () => {
        setTestingPlatform(null);
      },
    });
  };

  const handleCancel = () => {
    setIsCreating(false);
    setEditingConfig(null);
  };

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  const configs = configsData?.items || [];
  const isEditing = isCreating || editingConfig !== null;

  return (
    <div className="space-y-6">
      {/* 標題與新增按鈕 */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">平台爬取配置</h2>
          <p className="text-sm text-gray-500">
            管理各電商平台的爬取策略，包括速率限制、並發控制、重試策略等
          </p>
        </div>
        {!isEditing && (
          <Button onClick={handleCreate}>
            <Plus className="h-4 w-4 mr-2" />
            新增配置
          </Button>
        )}
      </div>

      {/* 編輯/新建表單 */}
      {isEditing && (
        <Card className="border-brand-primary/50">
          <CardHeader>
            <CardTitle className="text-lg">
              {isCreating ? "新增平台配置" : `編輯配置：${editingConfig?.platform}`}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* 基本信息 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {isCreating && (
                <div className="space-y-2">
                  <Label htmlFor="platform">平台名稱</Label>
                  <Input
                    id="platform"
                    placeholder="例如：hktvmall, watsons"
                    value={formData.platform}
                    onChange={(e) => setFormData({ ...formData, platform: e.target.value })}
                  />
                </div>
              )}
              <div className="space-y-2">
                <Label htmlFor="timeout">請求超時（秒）</Label>
                <Input
                  id="timeout"
                  type="number"
                  min={5}
                  max={300}
                  value={formData.timeoutSeconds}
                  onChange={(e) => setFormData({ ...formData, timeoutSeconds: Number(e.target.value) })}
                />
              </div>
            </div>

            {/* 速率限制 */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-gray-700 flex items-center gap-2">
                <Shield className="h-4 w-4" />
                速率限制
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="rateLimit">請求數量</Label>
                  <Input
                    id="rateLimit"
                    type="number"
                    min={1}
                    max={1000}
                    value={formData.rateLimitRequests}
                    onChange={(e) => setFormData({ ...formData, rateLimitRequests: Number(e.target.value) })}
                  />
                  <p className="text-xs text-gray-500">每個時間窗口內的最大請求數</p>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="rateWindow">時間窗口（秒）</Label>
                  <Input
                    id="rateWindow"
                    type="number"
                    min={1}
                    max={3600}
                    value={formData.rateLimitWindowSeconds}
                    onChange={(e) => setFormData({ ...formData, rateLimitWindowSeconds: Number(e.target.value) })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="concurrent">並發數量</Label>
                  <Input
                    id="concurrent"
                    type="number"
                    min={1}
                    max={50}
                    value={formData.concurrentLimit}
                    onChange={(e) => setFormData({ ...formData, concurrentLimit: Number(e.target.value) })}
                  />
                </div>
              </div>
            </div>

            {/* 重試策略 */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-gray-700 flex items-center gap-2">
                <RotateCcw className="h-4 w-4" />
                重試策略
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="maxRetries">最大重試次數</Label>
                  <Input
                    id="maxRetries"
                    type="number"
                    min={0}
                    max={10}
                    value={formData.maxRetries}
                    onChange={(e) => setFormData({ ...formData, maxRetries: Number(e.target.value) })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="retryDelay">重試延遲（秒）</Label>
                  <Input
                    id="retryDelay"
                    type="number"
                    min={1}
                    max={300}
                    value={formData.retryDelaySeconds}
                    onChange={(e) => setFormData({ ...formData, retryDelaySeconds: Number(e.target.value) })}
                  />
                </div>
              </div>
            </div>

            {/* 功能開關 */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-gray-700 flex items-center gap-2">
                <Settings className="h-4 w-4" />
                功能設置
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <Label htmlFor="useActions">動態頁面支持</Label>
                    <p className="text-xs text-gray-500">啟用 Actions 處理 JS 渲染</p>
                  </div>
                  <Switch
                    id="useActions"
                    checked={formData.useActions}
                    onCheckedChange={(checked) => setFormData({ ...formData, useActions: checked })}
                  />
                </div>
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <Label htmlFor="proxyEnabled">代理模式</Label>
                    <p className="text-xs text-gray-500">使用代理池分散請求</p>
                  </div>
                  <Switch
                    id="proxyEnabled"
                    checked={formData.proxyEnabled}
                    onCheckedChange={(checked) => setFormData({ ...formData, proxyEnabled: checked })}
                  />
                </div>
                {!isCreating && (
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <Label htmlFor="isActive">啟用配置</Label>
                      <p className="text-xs text-gray-500">禁用後將暫停抓取</p>
                    </div>
                    <Switch
                      id="isActive"
                      checked={formData.isActive}
                      onCheckedChange={(checked) => setFormData({ ...formData, isActive: checked })}
                    />
                  </div>
                )}
              </div>
            </div>

            {/* 操作按鈕 */}
            <div className="flex justify-end gap-2 pt-4 border-t">
              <Button variant="outline" onClick={handleCancel}>
                取消
              </Button>
              <Button
                onClick={handleSave}
                disabled={
                  (isCreating && !formData.platform.trim()) ||
                  createMutation.isPending ||
                  updateMutation.isPending
                }
              >
                {(createMutation.isPending || updateMutation.isPending) ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : null}
                {isCreating ? "創建" : "保存"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 配置列表 */}
      {!isEditing && configs.length === 0 && (
        <div className="empty-state">
          <Server className="empty-state-icon" />
          <h3 className="empty-state-title">暫無平台配置</h3>
          <p className="empty-state-description">
            點擊「新增配置」開始添加電商平台的爬取配置
          </p>
        </div>
      )}

      {!isEditing && configs.length > 0 && (
        <div className="space-y-4">
          {configs.map((config) => (
            <PlatformConfigCard
              key={config.id}
              config={config}
              onEdit={() => handleEdit(config)}
              onDelete={() => handleDelete(config.platform)}
              onTest={(url) => {
                setTestUrl(url);
                handleTest(config.platform);
              }}
              isTesting={testingPlatform === config.platform}
              testUrl={testUrl}
              setTestUrl={setTestUrl}
            />
          ))}
        </div>
      )}
    </div>
  );
}

// ==================== 平台配置卡片 ====================

interface PlatformConfigCardProps {
  config: ScrapeConfig;
  onEdit: () => void;
  onDelete: () => void;
  onTest: (url: string) => void;
  isTesting: boolean;
  testUrl: string;
  setTestUrl: (url: string) => void;
}

function PlatformConfigCard({
  config,
  onEdit,
  onDelete,
  onTest,
  isTesting,
  testUrl,
  setTestUrl,
}: PlatformConfigCardProps) {
  const [showTest, setShowTest] = useState(false);

  return (
    <Card className={cn("stat-card", !config.isActive && "opacity-60")}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between">
          {/* 左側：平台信息 */}
          <div className="flex items-start gap-4">
            <div className={cn(
              "w-12 h-12 rounded-lg flex items-center justify-center",
              config.isActive ? "bg-brand-primary/10" : "bg-gray-100"
            )}>
              <Server className={cn(
                "h-6 w-6",
                config.isActive ? "text-brand-primary" : "text-gray-400"
              )} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold text-gray-900">{config.platform}</h3>
                <Badge className={config.isActive ? "bg-success/10 text-success" : "bg-gray-100 text-gray-500"}>
                  {config.isActive ? "啟用" : "禁用"}
                </Badge>
                {config.useActions && (
                  <Badge variant="outline" className="text-xs">
                    動態頁面
                  </Badge>
                )}
                {config.proxyEnabled && (
                  <Badge variant="outline" className="text-xs">
                    <Network className="h-3 w-3 mr-1" />
                    代理
                  </Badge>
                )}
              </div>
              <div className="flex flex-wrap gap-4 mt-2 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <Shield className="h-4 w-4" />
                  {config.rateLimitRequests}次/{config.rateLimitWindowSeconds}秒
                </span>
                <span className="flex items-center gap-1">
                  <Activity className="h-4 w-4" />
                  並發 {config.concurrentLimit}
                </span>
                <span className="flex items-center gap-1">
                  <RotateCcw className="h-4 w-4" />
                  重試 {config.maxRetries}次
                </span>
                <span className="flex items-center gap-1">
                  <Timer className="h-4 w-4" />
                  超時 {config.timeoutSeconds}s
                </span>
              </div>
            </div>
          </div>

          {/* 右側：操作按鈕 */}
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => setShowTest(!showTest)}>
              <Zap className="h-4 w-4 mr-1" />
              測試
            </Button>
            <Button variant="outline" size="sm" onClick={onEdit}>
              <Edit2 className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" className="text-error hover:text-error" onClick={onDelete}>
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* 測試區域 */}
        {showTest && (
          <div className="mt-4 pt-4 border-t space-y-3">
            <div className="flex gap-2">
              <Input
                placeholder="輸入測試 URL..."
                value={testUrl}
                onChange={(e) => setTestUrl(e.target.value)}
                className="flex-1"
              />
              <Button
                onClick={() => onTest(testUrl)}
                disabled={!testUrl.trim() || isTesting}
              >
                {isTesting ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Zap className="h-4 w-4" />
                )}
              </Button>
            </div>
            <p className="text-xs text-gray-500">
              輸入該平台的商品頁面 URL 進行測試抓取
            </p>
          </div>
        )}

        {/* 更新時間 */}
        <div className="mt-3 pt-3 border-t text-xs text-gray-400">
          更新於 {formatRelativeTime(new Date(config.updatedAt))}
        </div>
      </CardContent>
    </Card>
  );
}

// ==================== 數據抓取頁面 ====================

export default function ScrapePage() {
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [competitorFilter, setCompetitorFilter] = useState<string>("");
  const [page, setPage] = useState(1);
  const pageSize = 20;

  // 獲取數據
  const { data: statsData, isLoading: statsLoading } = useScrapeStats(7);
  const { data: runningTasks } = useRunningScrapeTasks();
  const { data: logsData, isLoading: logsLoading } = useScrapeLogs({
    page,
    pageSize,
    status: statusFilter || undefined,
    competitorId: competitorFilter || undefined,
  });
  const { data: competitors } = useCompetitors();

  const triggerMutation = useTriggerScrape();

  const logs = logsData?.items || [];
  const totalPages = logsData?.totalPages || 1;

  // 觸發抓取
  const handleTriggerAll = () => {
    triggerMutation.mutate({ scrapeAll: true });
  };

  const handleTriggerCompetitor = (competitorId: string) => {
    triggerMutation.mutate({ competitorId });
  };

  return (
    <div className="page-container">
      {/* 頁面標題 */}
      <div className="page-header">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="page-title flex items-center gap-2">
              <Database className="h-6 w-6 text-brand-primary" />
              數據抓取管理
            </h1>
            <p className="page-description">
              管理競品數據抓取任務，監控抓取狀態與歷史
            </p>
          </div>
          <div className="flex gap-2">
            <Select
              value=""
              onValueChange={(v) => {
                if (v === "all") {
                  handleTriggerAll();
                } else if (v) {
                  handleTriggerCompetitor(v);
                }
              }}
            >
              <SelectTrigger className="w-[180px]">
                <Play className="h-4 w-4 mr-2" />
                <SelectValue placeholder="立即抓取..." />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">抓取全部競爭對手</SelectItem>
                {competitors?.map((c) => (
                  <SelectItem key={c.id} value={String(c.id)}>
                    {c.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      {/* 統計卡片 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {statsLoading ? (
          <>
            {[1, 2, 3, 4].map((i) => (
              <Card key={i} className="stat-card">
                <CardContent className="p-5">
                  <Skeleton className="h-4 w-24 mb-2" />
                  <Skeleton className="h-8 w-16" />
                </CardContent>
              </Card>
            ))}
          </>
        ) : (
          <>
            <StatCard
              title="今日抓取商品"
              value={statsData?.productsScrapedToday || 0}
              icon={Package}
            />
            <StatCard
              title="7 天抓取次數"
              value={statsData?.totalScrapes || 0}
              icon={Activity}
            />
            <StatCard
              title="成功率"
              value={`${statsData?.successRate || 0}%`}
              icon={TrendingUp}
            />
            <StatCard
              title="平均耗時"
              value={
                statsData?.avgDurationSeconds
                  ? `${Math.round(statsData.avgDurationSeconds)}s`
                  : "-"
              }
              icon={Timer}
            />
          </>
        )}
      </div>

      {/* 運行中任務 */}
      {runningTasks && runningTasks.length > 0 && (
        <div className="mb-6">
          <h2 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            正在運行的任務 ({runningTasks.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {runningTasks.map((task) => (
              <RunningTaskCard key={task.id} task={task} />
            ))}
          </div>
        </div>
      )}

      {/* 功能標籤頁 */}
      <Tabs defaultValue="logs" className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="logs">抓取記錄</TabsTrigger>
          <TabsTrigger value="preview">抓取測試</TabsTrigger>
          <TabsTrigger value="discover">URL 發現</TabsTrigger>
          <TabsTrigger value="schedule">定時任務</TabsTrigger>
          <TabsTrigger value="failed">失敗重試</TabsTrigger>
          <TabsTrigger value="configs">平台配置</TabsTrigger>
        </TabsList>

        {/* 抓取記錄 */}
        <TabsContent value="logs" className="space-y-4">
          {/* 篩選區域 */}
          <div className="flex flex-col md:flex-row gap-3">
            <Select
              value={statusFilter}
              onValueChange={(v) => {
                setStatusFilter(v === "all" ? "" : v);
                setPage(1);
              }}
            >
              <SelectTrigger className="w-full md:w-[140px]">
                <SelectValue placeholder="全部狀態" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部狀態</SelectItem>
                <SelectItem value="success">成功</SelectItem>
                <SelectItem value="partial">部分成功</SelectItem>
                <SelectItem value="failed">失敗</SelectItem>
                <SelectItem value="running">運行中</SelectItem>
              </SelectContent>
            </Select>

            <Select
              value={competitorFilter}
              onValueChange={(v) => {
                setCompetitorFilter(v === "all" ? "" : v);
                setPage(1);
              }}
            >
              <SelectTrigger className="w-full md:w-[180px]">
                <SelectValue placeholder="全部競爭對手" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部競爭對手</SelectItem>
                {competitors?.map((c) => (
                  <SelectItem key={c.id} value={String(c.id)}>
                    {c.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Button
              variant="outline"
              size="icon"
              onClick={() => {
                setStatusFilter("");
                setCompetitorFilter("");
                setPage(1);
              }}
              className="ml-auto"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>

          {/* 日誌列表 */}
          {logsLoading && <LoadingSkeleton />}

          {!logsLoading && logs.length === 0 && (
            <div className="empty-state">
              <Database className="empty-state-icon" />
              <h3 className="empty-state-title">暫無抓取記錄</h3>
              <p className="empty-state-description">
                點擊「立即抓取」開始抓取競品數據
              </p>
            </div>
          )}

          {!logsLoading && logs.length > 0 && (
            <div className="space-y-3">
              {logs.map((log) => (
                <LogCard key={log.id} log={log} />
              ))}
            </div>
          )}

          {/* 分頁 */}
          {!logsLoading && totalPages > 1 && (
            <div className="flex items-center justify-between mt-6">
              <p className="text-sm text-gray-500">
                共 {logsData?.total || 0} 條記錄，第 {page} / {totalPages} 頁
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
        </TabsContent>

        {/* 抓取測試 */}
        <TabsContent value="preview">
          <ScrapePreviewSection />
        </TabsContent>

        {/* URL 發現 */}
        <TabsContent value="discover">
          <UrlDiscoverySection />
        </TabsContent>

        {/* 定時任務 */}
        <TabsContent value="schedule">
          <ScheduleConfigSection />
        </TabsContent>

        {/* 失敗重試 */}
        <TabsContent value="failed">
          <FailedProductsSection />
        </TabsContent>

        {/* 平台配置 */}
        <TabsContent value="configs">
          <PlatformConfigSection />
        </TabsContent>
      </Tabs>
    </div>
  );
}
