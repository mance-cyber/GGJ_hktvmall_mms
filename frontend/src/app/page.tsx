'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { analyticsApi, CommandCenterResponse } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  DollarSign, 
  Truck, 
  MessageSquare, 
  Bell, 
  TrendingUp, 
  ArrowRight, 
  CheckCircle,
  AlertTriangle,
  Sparkles,
  ShoppingBag
} from 'lucide-react'

export default function DashboardPage() {
  const [data, setData] = useState<CommandCenterResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await analyticsApi.getCommandCenter()
        setData(res)
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const stats = data?.stats
  
  // Format currency
  const fmtMoney = (val: number) => `$${val?.toLocaleString()}`

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">營運總覽 (Command Center)</h1>
          <p className="text-slate-500 mt-1">歡迎回來，這是您今天的業務概況。</p>
        </div>
        <div className="text-sm text-slate-500 font-medium">
          {new Date().toLocaleDateString('zh-HK', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })}
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Revenue */}
        <Card className="border-l-4 border-l-emerald-500 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">本月營收</CardTitle>
            <DollarSign className="h-4 w-4 text-emerald-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">{stats ? fmtMoney(stats.monthly_revenue) : '...'}</div>
            <p className="text-xs text-muted-foreground mt-1">
              淨利: <span className="text-emerald-600 font-medium">{stats ? fmtMoney(stats.monthly_profit) : '...'}</span>
            </p>
          </CardContent>
        </Card>

        {/* Orders */}
        <Card className="border-l-4 border-l-blue-500 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">待出貨訂單</CardTitle>
            <Truck className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">{stats?.orders_to_ship || 0}</div>
            <Link href="/orders" className="text-xs text-blue-600 hover:underline flex items-center mt-1">
              前往處理 <ArrowRight className="h-3 w-3 ml-1" />
            </Link>
          </CardContent>
        </Card>

        {/* Inbox */}
        <Card className="border-l-4 border-l-purple-500 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">未讀訊息</CardTitle>
            <MessageSquare className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">{stats?.unread_messages || 0}</div>
            <Link href="/inbox" className="text-xs text-purple-600 hover:underline flex items-center mt-1">
              查看收件箱 <ArrowRight className="h-3 w-3 ml-1" />
            </Link>
          </CardContent>
        </Card>

        {/* Alerts */}
        <Card className="border-l-4 border-l-amber-500 shadow-sm">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-600">新警報</CardTitle>
            <Bell className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">{stats?.unread_alerts || 0}</div>
            <Link href="/alerts" className="text-xs text-amber-600 hover:underline flex items-center mt-1">
              查看警報 <ArrowRight className="h-3 w-3 ml-1" />
            </Link>
          </CardContent>
        </Card>
      </div>

      {/* Action Center & Activity Feed */}
      <div className="grid gap-6 md:grid-cols-7">
        
        {/* Left Column: Action Items (Span 4) */}
        <div className="md:col-span-4 space-y-6">
          <h2 className="text-lg font-semibold text-slate-800">待辦事項 (Action Items)</h2>
          
          <div className="grid gap-4">
            {/* Pricing Review Action */}
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:border-blue-300 transition-colors flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="bg-blue-100 p-3 rounded-full text-blue-600">
                  <TrendingUp className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-medium text-slate-900">AI 價格建議審批</h3>
                  <p className="text-sm text-slate-500">
                    {stats?.pending_price_reviews || 0} 個建議等待您的確認
                  </p>
                </div>
              </div>
              <Link href="/products?tab=pricing">
                <Button variant="outline" size="sm">前往審批</Button>
              </Link>
            </div>

            {/* Promotion Review Action */}
            <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:border-purple-300 transition-colors flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="bg-purple-100 p-3 rounded-full text-purple-600">
                  <Sparkles className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-medium text-slate-900">智能推廣機會</h3>
                  <p className="text-sm text-slate-500">
                    {stats?.pending_promotion_reviews || 0} 個高利潤促銷機會
                  </p>
                </div>
              </div>
              <Link href="/promotions">
                <Button variant="outline" size="sm">查看建議</Button>
              </Link>
            </div>

            {/* Orders Action */}
            {stats && stats.orders_to_ship > 0 && (
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:border-amber-300 transition-colors flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="bg-amber-100 p-3 rounded-full text-amber-600">
                    <Truck className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900">急需出貨</h3>
                    <p className="text-sm text-slate-500">
                      {stats.orders_to_ship} 張訂單等待處理
                    </p>
                  </div>
                </div>
                <Link href="/orders">
                  <Button variant="default" size="sm" className="bg-amber-600 hover:bg-amber-700">立即出貨</Button>
                </Link>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Recent Activity (Span 3) */}
        <div className="md:col-span-3 space-y-4">
          <h2 className="text-lg font-semibold text-slate-800">最近動態</h2>
          <Card>
            <CardContent className="p-0">
              <div className="divide-y divide-slate-100">
                {data?.recent_activity.length === 0 ? (
                  <div className="p-8 text-center text-slate-400 text-sm">暫無最近活動</div>
                ) : (
                  data?.recent_activity.map((item, i) => (
                    <div
