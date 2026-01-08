'use client'

import { Competitor } from '@/lib/api'
import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  Edit,
  Trash2,
  RefreshCw,
  ExternalLink,
  Globe,
  Building2,
  Activity,
  Clock,
  Zap
} from 'lucide-react'
import { Button } from '@/components/ui/button'
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

export function CompetitorCard({
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
            className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-blue-400 to-transparent opacity-50"
            animate={{ top: ['0%', '100%'] }}
            transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
          />
        </div>
      )}

      <div className="p-6 relative z-10">
        {/* 頭部 */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-4">
            <div className={cn(
              "w-14 h-14 rounded-2xl flex items-center justify-center shadow-inner",
              "bg-gradient-to-br from-white to-slate-50 border border-slate-100"
            )}>
              <Building2 className="w-7 h-7 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                {competitor.name}
              </h3>
              <div className="flex items-center text-xs font-medium text-slate-500 mt-1 bg-slate-100/50 px-2 py-0.5 rounded-full w-fit">
                <Globe className="w-3 h-3 mr-1" />
                {platformLabel}
              </div>
            </div>
          </div>
          <Badge 
            variant={competitor.is_active ? "default" : "secondary"}
            className={cn(
              competitor.is_active ? "bg-green-500/10 text-green-700 hover:bg-green-500/20" : "bg-slate-100 text-slate-500"
            )}
          >
            <div className={cn("w-1.5 h-1.5 rounded-full mr-1.5", competitor.is_active ? "bg-green-500 animate-pulse" : "bg-slate-400")} />
            {competitor.is_active ? '監測中' : '已暫停'}
          </Badge>
        </div>

        {/* 描述 */}
        {competitor.notes && (
          <p className="text-sm text-slate-500 line-clamp-2 mb-4 h-10">
            {competitor.notes}
          </p>
        )}

        {/* 數據網格 */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-slate-50/50 rounded-lg p-3 border border-slate-100">
            <div className="flex items-center text-xs text-slate-500 mb-1">
              <Activity className="w-3 h-3 mr-1" />
              監測商品
            </div>
            <div className="text-xl font-bold text-slate-800">{competitor.product_count}</div>
          </div>
          <div className="bg-slate-50/50 rounded-lg p-3 border border-slate-100">
            <div className="flex items-center text-xs text-slate-500 mb-1">
              <Clock className="w-3 h-3 mr-1" />
              最後更新
            </div>
            <div className="text-sm font-semibold text-slate-800 pt-1">
              {competitor.last_scraped_at
                ? new Date(competitor.last_scraped_at).toLocaleDateString('zh-HK')
                : '尚未抓取'}
            </div>
          </div>
        </div>
      </div>

      {/* 底部操作欄 */}
      <div className="px-6 py-4 bg-slate-50/30 border-t border-slate-100/60 backdrop-blur-sm flex items-center justify-between relative z-10">
        <div className="flex items-center space-x-1">
          <Button
            size="sm"
            variant="ghost"
            onClick={onScrape}
            disabled={isScraping}
            className={cn(
              "h-8 px-2 text-slate-600 hover:text-blue-600 hover:bg-blue-50",
              isScraping && "text-blue-600 bg-blue-50"
            )}
            title="立即抓取"
          >
            {isScraping ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Zap className="w-4 h-4" />
            )}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={onEdit}
            className="h-8 px-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100"
          >
            <Edit className="w-4 h-4" />
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={onDelete}
            className="h-8 px-2 text-slate-600 hover:text-red-600 hover:bg-red-50"
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
        
        <Link href={`/competitors/${competitor.id}`}>
          <Button size="sm" variant="link" className="text-blue-600 hover:text-blue-700 p-0 h-auto font-medium">
            查看詳情
            <ExternalLink className="w-3 h-3 ml-1" />
          </Button>
        </Link>
      </div>
    </div>
  )
}
