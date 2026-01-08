'use client'

import { useState, useEffect } from 'react'
import { promotionApi, PromotionProposal, PromotionStats } from '@/lib/api'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Sparkles, TrendingUp, CheckCircle, XCircle, Tag, AlertCircle } from 'lucide-react'
import { toast } from 'sonner'

export default function PromotionsPage() {
  const [proposals, setProposals] = useState<PromotionProposal[]>([])
  const [stats, setStats] = useState<PromotionStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)

  const fetchData = async () => {
    setLoading(true)
    try {
      const [pData, sData] = await Promise.all([
        promotionApi.getSuggestions(),
        promotionApi.getStats()
      ])
      setProposals(pData)
      setStats(sData)
    } catch (error) {
      console.error('Failed to fetch promotions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    setGenerating(true)
    try {
      const res = await promotionApi.generateSuggestions()
      toast.success(`AI 已生成 ${res.generated_count} 個促銷建議`)
      await fetchData()
    } catch (error) {
      toast.error('生成失敗')
    } finally {
      setGenerating(false)
    }
  }

  const handleApprove = async (id: string) => {
    try {
      await promotionApi.approveProposal(id)
      toast.success('促銷活動已批准')
      setProposals(prev => prev.filter(p => p.id !== id))
      // Update stats locally
      if (stats) setStats({ ...stats, active_count: stats.active_count + 1, pending_count: stats.pending_count - 1 })
    } catch (error) {
      toast.error('操作失敗')
    }
  }

  const handleReject = async (id: string) => {
    try {
      await promotionApi.rejectProposal(id)
      toast.info('已忽略建議')
      setProposals(prev => prev.filter(p => p.id !== id))
    } catch (error) {
      toast.error('操作失敗')
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">智能推廣建議</h1>
          <p className="text-muted-foreground mt-1">AI 根據利潤率自動尋找促銷機會</p>
        </div>
        <div className="space-x-2">
          <Button onClick={handleGenerate} disabled={generating} className="bg-gradient-to-r from-purple-600 to-blue-600 text-white border-0">
            <Sparkles className={`mr-2 h-4 w-4 ${generating ? 'animate-spin' : ''}`} /> 
            {generating ? '分析中...' : 'AI 尋找機會'}
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">進行中活動</CardTitle>
            <Tag className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.active_count || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">待審批建議</CardTitle>
            <AlertCircle className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.pending_count || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">平均折扣力度</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.avg_discount || 0}%</div>
          </CardContent>
        </Card>
      </div>

      {/* Proposals Grid */}
      <h2 className="text-lg font-semibold flex items-center gap-2">
        <Sparkles className="h-5 w-5 text-purple-600" />
        AI 推薦機會 ({proposals.length})
      </h2>
      
      {proposals.length === 0 ? (
        <Card className="bg-slate-50 border-dashed">
          <CardContent className="flex flex-col items-center justify-center py-12 text-muted-foreground">
            <Sparkles className="h-12 w-12 mb-4 text-slate-300" />
            <p>暫無新建議，點擊右上角「AI 尋找機會」試試看</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {proposals.map((p) => (
            <Card key={p.id} className="border-t-4 border-t-purple-500 shadow-sm hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex justify-between items-start mb-2">
                  <Badge variant="secondary" className="bg-purple-100 text-purple-700">
                    -{p.discount_percent}% OFF
                  </Badge>
                  <span className="text-xs text-muted-foreground bg-slate-100 px-2 py-1 rounded">
                    利潤率: {p.projected_margin.toFixed(1)}%
                  </span>
                </div>
                <CardTitle className="line-clamp-1" title={p.product_name}>{p.product_name}</CardTitle>
                <CardDescription className="font-mono text-xs">{p.product_sku}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-end bg-slate-50 p-3 rounded-lg">
                  <div>
                    <div className="text-sm text-muted-foreground line-through">${p.original_price}</div>
                    <div className="text-2xl font-bold text-red-600">${p.discounted_price}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-muted-foreground">預計單單賺</div>
                    <div className="text-lg font-bold text-green-600">+${p.projected_profit}</div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <div className="text-sm">
                    <span className="font-semibold text-slate-700">推薦原因：</span>
                    <span className="text-slate-600">{p.reason}</span>
                  </div>
                  <div className="text-sm bg-yellow-50 p-2 rounded border border-yellow-100">
                    <span className="font-semibold text-yellow-800">建議文案：</span>
                    <p className="text-yellow-700 mt-1 italic">"{p.marketing_copy}"</p>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="flex gap-2 pt-2">
                <Button variant="outline" className="flex-1 hover:bg-red-50 hover:text-red-600 hover:border-red-200" onClick={() => handleReject(p.id)}>
                  <XCircle className="w-4 h-4 mr-2" /> 忽略
                </Button>
                <Button className="flex-1 bg-green-600 hover:bg-green-700" onClick={() => handleApprove(p.id)}>
                  <CheckCircle className="w-4 h-4 mr-2" /> 批准上架
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
