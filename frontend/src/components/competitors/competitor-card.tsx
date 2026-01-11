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
  Zap,
  ChevronRight
} from 'lucide-react'
import { cn } from '@/lib/utils'
import {
  HoloCard,
  HoloButton,
  HoloBadge,
} from '@/components/ui/future-tech'

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
    <HoloCard
      glowColor={isScraping ? 'blue' : 'cyan'}
      scanLine={isScraping}
      className={cn(
        "h-full flex flex-col overflow-hidden group",
        isScraping && "ring-2 ring-cyan-400/50"
      )}
    >
      <div className="p-5 flex-1 flex flex-col">
        {/* 頭部：圖標 + 名稱 + 狀態 */}
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="flex items-center space-x-3 min-w-0 flex-1">
            <div className={cn(
              "w-12 h-12 rounded-xl flex items-center justify-center shrink-0",
              "bg-gradient-to-br from-cyan-50 to-blue-50 border border-cyan-100/50",
              "shadow-lg shadow-cyan-100/30"
            )}>
              <Building2 className="w-6 h-6 text-cyan-600" />
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="text-base font-bold text-slate-800 group-hover:text-cyan-600 transition-colors truncate">
                {competitor.name}
              </h3>
              <div className="flex items-center text-xs font-medium text-slate-500 mt-1">
                <Globe className="w-3 h-3 mr-1 text-cyan-500" />
                {platformLabel}
              </div>
            </div>
          </div>
          <HoloBadge
            variant={competitor.is_active ? 'success' : 'default'}
            size="sm"
            pulse={competitor.is_active}
          >
            {competitor.is_active ? '監測中' : '已暫停'}
          </HoloBadge>
        </div>

        {/* 描述 - 固定高度確保卡片對齊 */}
        <div className="h-10 mb-4">
          {competitor.notes ? (
            <p className="text-sm text-slate-500 line-clamp-2">
              {competitor.notes}
            </p>
          ) : (
            <p className="text-sm text-slate-400 italic">暫無備註</p>
          )}
        </div>

        {/* 數據網格 */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gradient-to-br from-slate-50 to-white rounded-xl p-3 border border-slate-100/80">
            <div className="flex items-center text-xs text-slate-500 mb-1">
              <Activity className="w-3 h-3 mr-1 text-cyan-500" />
              監測商品
            </div>
            <div className="text-xl font-bold text-slate-800">{competitor.product_count}</div>
          </div>
          <div className="bg-gradient-to-br from-slate-50 to-white rounded-xl p-3 border border-slate-100/80">
            <div className="flex items-center text-xs text-slate-500 mb-1">
              <Clock className="w-3 h-3 mr-1 text-cyan-500" />
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
      <div className="px-5 py-3 bg-gradient-to-r from-slate-50/80 to-white/80 border-t border-slate-100/60 flex items-center justify-between">
        <div className="flex items-center space-x-1">
          <HoloButton
            size="sm"
            variant="ghost"
            onClick={onScrape}
            disabled={isScraping}
            icon={isScraping ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4 text-amber-500" />}
            className={cn(isScraping && "text-cyan-600 bg-cyan-50")}
          >
            <span className="sr-only">抓取</span>
          </HoloButton>
          <HoloButton
            size="sm"
            variant="ghost"
            onClick={onEdit}
            icon={<Edit className="w-4 h-4" />}
          >
            <span className="sr-only">編輯</span>
          </HoloButton>
          <HoloButton
            size="sm"
            variant="ghost"
            onClick={onDelete}
            icon={<Trash2 className="w-4 h-4" />}
            className="hover:text-red-600 hover:bg-red-50"
          >
            <span className="sr-only">刪除</span>
          </HoloButton>
        </div>

        <Link href={`/competitors/${competitor.id}`}>
          <HoloButton
            size="sm"
            variant="ghost"
            icon={<ChevronRight className="w-4 h-4" />}
            className="text-cyan-600 hover:text-cyan-700"
          >
            詳情
          </HoloButton>
        </Link>
      </div>
    </HoloCard>
  )
}
