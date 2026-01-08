"use client";

import { useAnalyticsOverview, usePriceTrends, useAlertTrends } from "@/lib/hooks/use-analytics";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import {
  BarChart3,
  TrendingUp,
  TrendingDown,
  Package,
  Users,
  Bell,
  FileText,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

// ==================== 簡易圖表組件 ====================

interface SimpleBarChartProps {
  data: { label: string; value: number; color?: string }[];
  height?: number;
}

function SimpleBarChart({ data, height = 200 }: SimpleBarChartProps) {
  const maxValue = Math.max(...data.map((d) => d.value), 1);

  return (
    <div className="flex items-end gap-2" style={{ height }}>
      {data.map((item, i) => (
        <div key={i} className="flex-1 flex flex-col items-center gap-1">
          <div
            className={cn(
              "w-full rounded-t transition-all",
              item.color || "bg-brand-primary"
            )}
            style={{
              height: `${(item.value / maxValue) * 100}%`,
              minHeight: item.value > 0 ? 4 : 0,
            }}
          />
          <span className="text-xs text-gray-500 truncate max-w-full">
            {item.label}
          </span>
        </div>
      ))}
    </div>
  );
}

interface SimpleTrendLineProps {
  data: { date: string; value: number }[];
  height?: number;
  color?: string;
}

function SimpleTrendLine({ data, height = 100, color = "#2E90FA" }: SimpleTrendLineProps) {
  if (data.length === 0) return null;

  const maxValue = Math.max(...data.map((d) => d.value), 1);
  const minValue = Math.min(...data.map((d) => d.value), 0);
  const range = maxValue - minValue || 1;

  const points = data.map((d, i) => {
    const x = (i / (data.length - 1)) * 100;
    const y = 100 - ((d.value - minValue) / range) * 100;
    return `${x},${y}`;
  }).join(" ");

  return (
    <div style={{ height }}>
      <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full h-full">
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="2"
          vectorEffect="non-scaling-stroke"
        />
        <linearGradient id="gradient" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
        <polygon
          points={`0,100 ${points} 100,100`}
          fill="url(#gradient)"
        />
      </svg>
    </div>
  );
}

// ==================== 統計卡片組件 ====================

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  description?: string;
}

function StatCard({ title, value, icon, trend, description }: StatCardProps) {
  return (
    <Card className="stat-card">
      <CardContent className="p-5">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <p className="stat-card-header">{title}</p>
            <div className="flex items-baseline gap-2 mt-2">
              <p className="stat-card-value">{value}</p>
              {trend && (
                <span
                  className={cn(
                    "text-sm font-medium flex items-center",
                    trend.isPositive ? "text-success" : "text-error"
                  )}
                >
                  {trend.isPositive ? (
                    <ArrowUpRight className="h-4 w-4" />
                  ) : (
                    <ArrowDownRight className="h-4 w-4" />
                  )}
                  {Math.abs(trend.value)}%
                </span>
              )}
            </div>
            {description && (
              <p className="text-xs text-gray-500 mt-1">{description}</p>
            )}
          </div>
          <div className="h-12 w-12 rounded-lg bg-brand-primary/10 flex items-center justify-center">
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// ==================== 載入骨架 ====================

function LoadingSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="stat-card">
            <CardContent className="p-5">
              <div className="flex justify-between">
                <div>
                  <Skeleton className="h-4 w-20 mb-2" />
                  <Skeleton className="h-8 w-16" />
                </div>
                <Skeleton className="h-12 w-12 rounded-lg" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <Skeleton className="h-5 w-32" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-[200px] w-full" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <Skeleton className="h-5 w-32" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-[200px] w-full" />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

// ==================== 數據分析頁面 ====================

export default function AnalyticsPage() {
  const { data: overview, isLoading: overviewLoading } = useAnalyticsOverview();
  const { data: priceTrends, isLoading: priceTrendsLoading } = usePriceTrends(7);
  const { data: alertTrends, isLoading: alertTrendsLoading } = useAlertTrends(7);

  const isLoading = overviewLoading || priceTrendsLoading || alertTrendsLoading;

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1 className="page-title">數據分析</h1>
          <p className="page-description">查看業務數據與趨勢分析</p>
        </div>
        <LoadingSkeleton />
      </div>
    );
  }

  // 準備圖表數據
  const alertsByTypeData = [
    { label: "降價", value: overview?.alertsByType.priceDrops || 0, color: "bg-success" },
    { label: "漲價", value: overview?.alertsByType.priceIncreases || 0, color: "bg-error" },
    { label: "缺貨", value: overview?.alertsByType.outOfStock || 0, color: "bg-warning" },
  ];

  const weekDays = ["週日", "週一", "週二", "週三", "週四", "週五", "週六"];
  const alertTrendData = alertTrends?.map((t) => ({
    label: weekDays[new Date(t.date).getDay()],
    value: t.value,
    color: "bg-brand-primary",
  })) || [];

  return (
    <div className="page-container">
      {/* 頁面標題 */}
      <div className="page-header">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="page-title flex items-center gap-2">
              <BarChart3 className="h-6 w-6 text-brand-primary" />
              數據分析
            </h1>
            <p className="page-description">
              查看業務數據與趨勢分析
            </p>
          </div>
        </div>
      </div>

      {/* 核心指標 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          title="監控商品總數"
          value={overview?.totalProducts || 0}
          icon={<Package className="h-6 w-6 text-brand-primary" />}
          description="正在監控的競品數量"
        />
        <StatCard
          title="競爭對手數"
          value={overview?.totalCompetitors || 0}
          icon={<Users className="h-6 w-6 text-brand-primary" />}
          description="追蹤中的競爭對手"
        />
        <StatCard
          title="今日警報數"
          value={overview?.priceAlertsToday || 0}
          icon={<Bell className="h-6 w-6 text-brand-primary" />}
          trend={
            overview?.priceAlertsToday
              ? { value: 12, isPositive: false }
              : undefined
          }
        />
        <StatCard
          title="今日生成內容"
          value={overview?.contentGenerated || 0}
          icon={<FileText className="h-6 w-6 text-brand-primary" />}
          description="AI 生成的文案數量"
        />
      </div>

      {/* 圖表區域 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* 警報類型分佈 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-medium flex items-center gap-2">
              <Bell className="h-4 w-4 text-gray-500" />
              警報類型分佈（近7天）
            </CardTitle>
          </CardHeader>
          <CardContent>
            <SimpleBarChart data={alertsByTypeData} height={180} />
            <div className="flex justify-center gap-6 mt-4">
              {alertsByTypeData.map((item, i) => (
                <div key={i} className="flex items-center gap-2">
                  <div className={cn("w-3 h-3 rounded", item.color)} />
                  <span className="text-sm text-gray-600">
                    {item.label}: {item.value}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 每日警報趨勢 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-gray-500" />
              每日警報趨勢
            </CardTitle>
          </CardHeader>
          <CardContent>
            <SimpleBarChart data={alertTrendData} height={180} />
          </CardContent>
        </Card>
      </div>

      {/* 價格趨勢 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base font-medium flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-gray-500" />
            價格變動趨勢（近7天）
          </CardTitle>
        </CardHeader>
        <CardContent>
          {priceTrends && priceTrends.length > 0 ? (
            <>
              <SimpleTrendLine data={priceTrends} height={150} />
              <div className="flex justify-between text-xs text-gray-500 mt-2">
                {priceTrends.map((t, i) => (
                  <span key={i}>{t.date.slice(5)}</span>
                ))}
              </div>
            </>
          ) : (
            <div className="h-[150px] flex items-center justify-center text-gray-400">
              暫無數據
            </div>
          )}
        </CardContent>
      </Card>

      {/* 快速洞察 */}
      <div className="mt-6">
        <h2 className="text-lg font-semibold mb-4">快速洞察</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="stat-card border-l-4 border-l-success">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <TrendingDown className="h-5 w-5 text-success mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">降價機會</p>
                  <p className="text-sm text-gray-600 mt-1">
                    {overview?.alertsByType.priceDrops || 0} 個競品降價，
                    可考慮調整定價策略
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="stat-card border-l-4 border-l-warning">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <Bell className="h-5 w-5 text-warning mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">待處理警報</p>
                  <p className="text-sm text-gray-600 mt-1">
                    今日有 {overview?.priceAlertsToday || 0} 個新警報需要關注
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="stat-card border-l-4 border-l-brand-primary">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <FileText className="h-5 w-5 text-brand-primary mt-0.5" />
                <div>
                  <p className="font-medium text-gray-900">內容生成</p>
                  <p className="text-sm text-gray-600 mt-1">
                    今日已生成 {overview?.contentGenerated || 0} 篇 AI 文案
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
