import os

p1 = r'''
'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, Competitor, CompetitorCreate } from '@/lib/api'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Eye,
  Plus,
  RefreshCw,
  AlertCircle,
  Edit,
  Trash2,
  X,
  Check,
  Play,
  ExternalLink,
  Globe,
  Building2,
  Activity,
  Clock,
  Zap
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

// 平台選項
const PLATFORMS = [
  { value: 'hktvmall', label: 'HKTVmall' },
  { value: 'watsons', label: 'Watsons' },
  { value: 'mannings', label: 'Mannings' },
  { value: 'parknshop', label: "PARKnSHOP" },
  { value: 'ztore', label: 'Ztore' },
  { value: 'other', label: '其他' },
]

export default function CompetitorsPage() {
  const queryClient = useQueryClient()
  const [showAddForm, setShowAddForm] = useState(false)
  const [editingCompetitor, setEditingCompetitor] = useState<Competitor | null>(null)
  const [scrapingId, setScrapingId] = useState<string | null>(null)

  // 獲取競爭對手列表
  const { data: competitors, isLoading, error, refetch } = useQuery({
    queryKey: ['competitors'],
    queryFn: () => api.getCompetitors(),
  })

  // 創建競爭對手
  const createMutation = useMutation({
    mutationFn: (data: CompetitorCreate) => api.createCompetitor(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitors'] })
      setShowAddForm(false)
    },
  })

  // 更新競爭對手
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CompetitorCreate> }) =>
      api.updateCompetitor(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitors'] })
      setEditingCompetitor(null)
    },
  })

  // 刪除競爭對手
  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.deleteCompetitor(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitors'] })
    },
  })

  // 觸發爬取
  const scrapeMutation = useMutation({
    mutationFn: (id: string) => api.triggerCompetitorScrape(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitors'] })
      setScrapingId(null)
    },
    onError: () => {
      setScrapingId(null)
    },
  })

  const handleScrape = (id: string) => {
    setScrapingId(id)
    scrapeMutation.mutate(id)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="relative">
          <div className="absolute inset-0 bg-blue-500/20 blur-xl rounded-full animate-pulse" />
          <RefreshCw className="relative w-12 h-12 animate-spin text-primary" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="glass-panel border-destructive/20 bg-destructive/5 p-6 rounded-xl flex items-center text-destructive">
        <AlertCircle className="w-5 h-5 mr-3" />
        <span className="font-medium">無法載入競爭對手列表，請稍後再試。</span>
      </div>
    )
  }
'''

p2 = r'''
  return (
    <div className="space-y-8 animate-fade-in-up">
      {/* 頁面標題 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
            競品監測
            <Badge variant="outline" className="text-primary border-primary/30 bg-primary/5">
              Live
            </Badge>
          </h1>
          <p className="text-muted-foreground mt-2 text-lg">
            即時追蹤競爭對手動態，AI 智能分析價格趨勢
          </p>
        </div>
        <div className="flex space-x-3">
          <Button
            variant="outline"
            onClick={() => refetch()}
            className="glass-card hover:bg-white/60"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            刷新數據
          </Button>
          <Button
            onClick={() => setShowAddForm(true)}
            className="bg-primary hover:bg-primary/90 shadow-lg shadow-blue-500/20 transition-all hover:scale-105"
          >
            <Plus className="w-4 h-4 mr-2" />
            新增競爭對手
          </Button>
        </div>
      </div>

      {/* 競爭對手卡片列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <AnimatePresence>
          {competitors?.data.map((competitor, index) => (
            <motion.div
              key={competitor.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              layout
            >
              <CompetitorCard
                competitor={competitor}
                onEdit={() => setEditingCompetitor(competitor)}
                onDelete={() => {
                  if (confirm(`確定要刪除「${competitor.name}」？所有相關商品數據也會被刪除。`)) {
                    deleteMutation.mutate(competitor.id)
                  }
                }}
                onScrape={() => handleScrape(competitor.id)}
                isScraping={scrapingId === competitor.id}
              />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* 空狀態 */}
      {(!competitors?.data || competitors.data.length === 0) && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-panel rounded-2xl p-16 text-center border-dashed border-2 border-slate-200"
        >
          <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6">
            <Building2 className="w-10 h-10 text-blue-500" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900">尚無競爭對手</h3>
          <p className="text-gray-500 mt-2 max-w-md mx-auto">
            開始監測您的第一個競爭對手，AI 將自動為您收集價格情報。
          </p>
          <Button
            onClick={() => setShowAddForm(true)}
            className="mt-8"
            size="lg"
          >
            <Plus className="w-5 h-5 mr-2" />
            立即新增
          </Button>
        </motion.div>
      )}

      {/* 新增表單彈窗 */}
      <CompetitorFormDialog
        open={showAddForm}
        onOpenChange={setShowAddForm}
        onSubmit={(data) => createMutation.mutate(data)}
        isLoading={createMutation.isPending}
        title="新增競爭對手"
      />

      {/* 編輯表單彈窗 */}
      <CompetitorFormDialog
        open={!!editingCompetitor}
        onOpenChange={(open) => !open && setEditingCompetitor(null)}
        initialData={editingCompetitor || undefined}
        onSubmit={(data) => editingCompetitor && updateMutation.mutate({ id: editingCompetitor.id, data })}
        isLoading={updateMutation.isPending}
        title="編輯競爭對手"
      />
    </div>
  )
}
'''

p3 = r'''
// -----------------------------------------------------------------------------
// 子組件
// -----------------------------------------------------------------------------

function CompetitorCard({
  competitor,
  onEdit,
  onDelete,
  onScrape,
  isScraping,
}: {
  competitor: Competitor
  onEdit: () => void
  onDelete: () => void
  onScrape: () => void
  isScraping: boolean
}) {
  const platformLabel = PLATFORMS.find((p) => p.value === competitor.platform)?.label || competitor.platform

  return (
    <div className={cn(
      "glass-card rounded-xl overflow-hidden group relative border border-white/40",
      isScraping && "ring-2 ring-blue-400/50"
    )}>
      {/* 掃描動畫效果 */}
      {isScraping && (
        <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
          <div className="absolute inset-0 bg-blue-500/5" />
          <motion.div
            className="absolute top-0 l
