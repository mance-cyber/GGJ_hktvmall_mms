'use client'

import { useState, useEffect } from 'react'
import { financeApi, Settlement, ProfitSummary } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { RefreshCw, DollarSign, TrendingUp, TrendingDown, FileText, ChevronDown, ChevronUp } from 'lucide-react'

export default function FinancePage() {
  const [summary, setSummary] = useState<ProfitSummary | null>(null)
  const [settlements, setSettlements] = useState<Settlement[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedSettlement, setExpandedSettlement] = useState<string | null>(null)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [sumData, settData] = await Promise.all([
        financeApi.getProfitSummary(),
        financeApi.getSettlements(10)
      ])
      setSummary(sumData)
      setSettlements(settData)
    } catch (error) {
      console.error('Failed to fetch finance data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSyncMock = async () => {
    setLoading(true)
    await financeApi.syncMockData()
    await fetchData()
  }

  useEffect(() => {
    fetchData()
  }, [])

  const toggleExpand = (id: string) => {
    if (expandedSettlement === id) {
      setExpandedSettlement(null)
    } else {
      setExpandedSettlement(id)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">財務與利潤中心</h1>
        <div className="space-x-2">
          <Button variant="outline" onClick={handleSyncMock}>
            <RefreshCw className="mr-2 h-4 w-4" /> 生成測試數據
          </Button>
          <Button onClick={fetchData} disabled={loading}>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} /> 刷新
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">總營收 (Revenue)</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${summary?.total_revenue?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">過去 30 天</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">平台佣金 (Commission)</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              -${summary?.total_commission?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">平均佔比 {(summary?.total_revenue ? (summary.total_commission / summary.total_revenue * 100).toFixed(1) : 0)}%</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">淨利潤 (Net Profit)</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              ${summary?.total_profit?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground">已扣除佣金與運費</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">利潤率 (Margin)</CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">
              {summary?.profit_margin?.toFixed(1) || '0'}%
            </div>
            <p className="text-xs text-muted-foreground">健康指標 > 25%</p>
          </CardContent>
        </Card>
      </div>

      {/* Settlement List */}
      <Card>
        <CardHeader>
          <CardTitle>最近結算單 (Settlements)</CardTitle>
          <CardDescription>來自 HKTVmall 的官方結算報告</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {settlements.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">暫無結算數據</div>
            ) : (
              settlements.map((s) => (
                <div key={s.id} className="border rounded-lg p-4">
                  <div 
                    className="flex items-center justify-between cursor-pointer"
                    onClick={() => toggleExpand(s.id)}
                  >
                    <div className="flex items-center gap-4">
                      <div className="bg-blue-100 p-2 rounded-full">
                        <FileText className="h-5 w-5 text-blue-600" />
                      </div>
                      <div>
                        <div className="font-medium">{s.statement_no}</div>
                        <div className="text-sm text-muted-foreground">
                          {new Date(s.cycle_start).toLocaleDateString()} - {new Date(s.cycle_end).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-6">
                      <div className="text-right">
                        <div className="font-bold text-green-600">+${s.net_settlement_amount.toLocaleString()}</div>
                        <div className="text-xs text-muted-foreground">結算日: {new Date(s.settlement_date).toLocaleDateString()}</div>
                      </div>
                      {expandedSettlement === s.id ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
                    </div>
                  </div>

                  {/* Expanded Details */}
                  {expandedSettlement === s.id && (
                    <div className="mt-4 pt-4 border-t bg-slate-50 p-4 rounded-md">
                      <div className="grid grid-cols-3 gap-4 mb-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">銷售總額:</span>
                          <span className="font-medium ml-2">${s.total_sales_amount.toLocaleString()}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">佣金總額:</span>
                          <span className="font-medium ml-2 text-red-600">-${s.total_commission.toLocaleString()}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">運費扣除:</span>
                          <span className="font-medium ml-2 text-red-600">-${s.total_shipping_fee.toLocaleString()}</span>
                        </div>
                      </div>
                      
                      <h4 className="font-medium mb-2 text-sm">訂單明細 ({s.items?.length || 0})</h4>
                      <div className="space-y-2">
                        {s.items?.map((item) => (
                          <div key={item.id} className="flex justify-between text-sm border-b pb-1 last:border-0">
                            <span>{item.order_number} ({item.product_name}) x{item.quantity}</span>
                            <div className="flex gap-4">
                              <span>${(item.item_price * item.quantity).toLocaleString()}</span>
                              <span className="text-red-500">-${item.commission_amount.toLocaleString()} ({(item.commission_rate)}%)</span>
           
