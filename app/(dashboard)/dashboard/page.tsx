"use client";

import { useDashboard } from "@/lib/hooks/use-dashboard";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Users,
  Package,
  AlertTriangle,
  FileText,
  TrendingUp,
  TrendingDown,
} from "lucide-react";
import { formatNumber, formatPercent } from "@/lib/utils";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import Link from "next/link";
import { Button } from "@/components/ui/button";

// ==================== 統計卡片組件 ====================

interface StatCardProps {
  title: string;
  value: number;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  icon: React.ReactNode;
  href: string;
}

function StatCard({ title, value, trend, icon, href }: StatCardProps) {
  return (
    <Card className="stat-card hover:shadow-md transition-shadow">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="stat-card-header">{title}</p>
            <p className="stat-card-value mt-2">{formatNumber(value)}</p>
            {trend && (
              <div className="stat-card-footer mt-2">
                <div
                  className={`trend-indicator ${
                    trend.isPositive ? "trend-up" : "trend-down"
                  }`}
                >
                  {trend.isPositive ? (
                    <TrendingUp className="h-4 w-4" />
                  ) : (
                    <TrendingDown className="h-4 w-4" />
                  )}
                  <span>{formatPercent(trend.value)}</span>
                  <span className="text-gray-500 ml-1">較上週</span>
                </div>
              </div>
            )}
          </div>
          <div className="h-12 w-12 rounded-lg bg-brand-primary/10 flex items-center justify-center flex-shrink-0">
            {icon}
          </div>
        </div>
        <Link href={href} className="block mt-3">
          <Button variant="link" className="p-0 h-auto text-sm">
            查看詳情 →
          </Button>
        </Link>
      </CardContent>
    </Card>
  );
}

// ==================== 預警列表組件 ====================

function AlertsList() {
  const { data, isLoading } = useDashboard();

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-[150px]" />
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const alerts = data?.recentAlerts || [];

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>近期價格預警</CardTitle>
        <Link href="/alerts">
          <Button variant="outline" size="sm">
            查看全部
          </Button>
        </Link>
      </CardHeader>
      <CardContent>
        {alerts.length === 0 ? (
          <div className="empty-state py-8">
            <AlertTriangle className="empty-state-icon" />
            <p className="empty-state-title">尚無價格預警</p>
            <p className="empty-state-description">系統持續監控中</p>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map((alert) => (
              <div
                key={alert.id}
                className="flex items-start gap-3 p-3 rounded-md bg-gray-50 hover:bg-gray-100 transition-colors"
              >
                <AlertTriangle
                  className={`h-5 w-5 flex-shrink-0 mt-0.5 ${
                    alert.severity === "critical"
                      ? "text-error"
                      : alert.severity === "warning"
                      ? "text-warning"
                      : "text-info"
                  }`}
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {alert.productName}
                  </p>
                  <p className="text-xs text-gray-600 mt-1">
                    類型：{alert.alertType === "price_higher" ? "價格較高" : alert.alertType === "price_lower" ? "價格較低" : "價格相等"}
                  </p>
                  <div className="flex items-center gap-4 mt-2">
                    <span className="text-xs text-gray-500">
                      變動：{formatPercent(alert.priceDifferencePercent / 100)}
                    </span>
                    <span className="text-xs text-gray-400">
                      {new Date(alert.createdAt).toLocaleString("zh-HK", {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// ==================== 價格趨勢圖表組件 ====================

function PriceTrendChart() {
  const { data, isLoading } = useDashboard();

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-6 w-[150px]" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-[300px] w-full" />
        </CardContent>
      </Card>
    );
  }

  const trendData = data?.priceTrend || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle>價格趨勢（最近 7 天）</CardTitle>
      </CardHeader>
      <CardContent>
        {trendData.length === 0 ? (
          <div className="h-[300px] flex items-center justify-center">
            <p className="text-sm text-gray-500">暫無數據</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis
                dataKey="date"
                stroke="#6B7280"
                style={{ fontSize: 12 }}
                tickFormatter={(value) => {
                  const date = new Date(value);
                  return `${date.getMonth() + 1}/${date.getDate()}`;
                }}
              />
              <YAxis
                stroke="#6B7280"
                style={{ fontSize: 12 }}
                tickFormatter={(value) => `$${value}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1F2937",
                  border: "none",
                  borderRadius: "6px",
                  color: "#FFFFFF",
                  fontSize: 12,
                }}
                formatter={(value: any) => [`HK$ ${formatNumber(value, 2)}`, ""]}
                labelFormatter={(label) => {
                  const date = new Date(label);
                  return date.toLocaleDateString("zh-HK");
                }}
              />
              <Legend
                wrapperStyle={{ fontSize: 12 }}
                iconType="line"
              />
              <Line
                type="monotone"
                dataKey="ourPrice"
                stroke="#1570EF"
                strokeWidth={2}
                name="我們的價格"
                dot={{ fill: "#1570EF", r: 3 }}
                activeDot={{ r: 5 }}
              />
              {trendData.some((d) => d.competitorPrice) && (
                <Line
                  type="monotone"
                  dataKey="competitorPrice"
                  stroke="#F97316"
                  strokeWidth={2}
                  name="競爭對手"
                  dot={{ fill: "#F97316", r: 3 }}
                  activeDot={{ r: 5 }}
                />
              )}
              {trendData.some((d) => d.averagePrice) && (
                <Line
                  type="monotone"
                  dataKey="averagePrice"
                  stroke="#9CA3AF"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  name="市場平均"
                  dot={false}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}

// ==================== 儀表板頁面 ====================

export default function DashboardPage() {
  const { data, isLoading, error } = useDashboard();

  if (error) {
    return (
      <div className="page-container">
        <div className="empty-state">
          <AlertTriangle className="empty-state-icon text-error" />
          <h3 className="empty-state-title">載入失敗</h3>
          <p className="empty-state-description">
            無法載入儀表板數據，請重新整理頁面
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      {/* 頁面標題 */}
      <div className="page-header">
        <h1 className="page-title">營運儀表板</h1>
        <p className="page-description">
          即時監控商品價格與 AI 內容生成狀態
        </p>
      </div>

      {/* KPI 統計卡片 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {isLoading ? (
          <>
            {[1, 2, 3, 4].map((i) => (
              <Card key={i} className="stat-card">
                <CardContent className="p-5">
                  <Skeleton className="h-4 w-24 mb-3" />
                  <Skeleton className="h-8 w-32 mb-2" />
                  <Skeleton className="h-4 w-20" />
                </CardContent>
              </Card>
            ))}
          </>
        ) : (
          <>
            <StatCard
              title="競爭對手數量"
              value={data?.stats.competitorsCount || 0}
              trend={{ value: 0.05, isPositive: true }}
              icon={<Users className="h-6 w-6 text-brand-primary" />}
              href="/competitors"
            />
            <StatCard
              title="監控商品數"
              value={data?.stats.monitoredProductsCount || 0}
              trend={{ value: 0.12, isPositive: true }}
              icon={<Package className="h-6 w-6 text-brand-primary" />}
              href="/products"
            />
            <StatCard
              title="今日預警數"
              value={data?.stats.todayAlertsCount || 0}
              trend={{ value: -0.08, isPositive: false }}
              icon={<AlertTriangle className="h-6 w-6 text-warning" />}
              href="/alerts"
            />
            <StatCard
              title="待審核內容"
              value={data?.stats.pendingContentCount || 0}
              icon={<FileText className="h-6 w-6 text-info" />}
              href="/content"
            />
          </>
        )}
      </div>

      {/* 圖表與預警 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <PriceTrendChart />
        <AlertsList />
      </div>

      {/* 快速操作 */}
      <Card>
        <CardHeader>
          <CardTitle>快速操作</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Link href="/competitors/new">
              <Button variant="outline" className="w-full">
                新增競爭對手
              </Button>
            </Link>
            <Link href="/products/new">
              <Button variant="outline" className="w-full">
                新增商品
              </Button>
            </Link>
            <Link href="/content/generator">
              <Button variant="outline" className="w-full">
                生成 AI 內容
              </Button>
            </Link>
            <Link href="/alerts">
              <Button variant="outline" className="w-full">
                查看所有預警
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
