'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  FolderOpen,
  Plus,
  RefreshCw,
  Download,
  ExternalLink,
  Play,
  AlertCircle,
  Check
} from 'lucide-react'
import {
  PageTransition,
  HoloCard,
  HoloPanelHeader,
  HoloButton,
  HoloBadge,
  PulseStatus,
  HoloSkeleton,
  StaggerContainer,
  DataMetric
} from '@/components/ui/future-tech'

// =============================================
// 表格行動畫變體
// =============================================
const tableRowVariants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  hover: {
    backgroundColor: 'rgba(6, 182, 212, 0.05)',
    transition: { duration: 0.2 }
  }
}

// =============================================
// 載入骨架組件
// =============================================
function LoadingSkeleton() {
  return (
    <PageTransition>
      <div className="space-y-6">
        {/* 標題骨架 */}
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <HoloSkeleton width={200} height={32} />
            <HoloSkeleton width={300} height={20} />
          </div>
          <HoloSkeleton width={100} height={40} />
        </div>

        {/* 表格骨架 */}
        <HoloCard>
          <div className="p-4 border-b border-slate-100/80">
            <HoloSkeleton width={150} height={24} />
          </div>
          <div className="divide-y divide-slate-100">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="flex items-center gap-4 p-4">
                <HoloSkeleton variant="circular" width={40} height={40} />
                <div className="flex-1 space-y-2">
                  <HoloSkeleton width="60%" height={16} />
                  <HoloSkeleton width="40%" height={14} />
                </div>
                <HoloSkeleton width={80} height={24} />
                <HoloSkeleton width={100} height={24} />
              </div>
            ))}
          </div>
        </HoloCard>
      </div>
    </PageTransition>
  )
}

// =============================================
// 錯誤狀態組件
// =============================================
function ErrorState() {
  return (
    <PageTransition>
      <HoloCard glowColor="purple">
        <div className="p-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-red-50 flex items-center justify-center">
              <AlertCircle className="w-5 h-5 text-red-500" />
            </div>
            <div>
              <h3 className="font-semibold text-slate-800">無法載入類別列表</h3>
              <p className="text-sm text-slate-500">請檢查網絡連接或稍後重試</p>
            </div>
          </div>
        </div>
      </HoloCard>
    </PageTransition>
  )
}

// =============================================
// 空狀態組件
// =============================================
function EmptyState() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="px-6 py-12 text-center"
    >
      <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-cyan-50 to-blue-50 flex items-center justify-center">
        <FolderOpen className="w-8 h-8 text-cyan-500" />
      </div>
      <h3 className="text-lg font-semibold text-slate-800">尚未創建任何類別</h3>
      <p className="text-slate-500 mt-1">通過 API 創建第一個類別開始監測</p>
    </motion.div>
  )
}

// =============================================
// 主頁面組件
// =============================================
export default function CategoriesPage() {
  const queryClient = useQueryClient()
  const [scrapingId, setScrapingId] = useState<string | null>(null)

  const { data: categories, isLoading, error, refetch } = useQuery({
    queryKey: ['categories'],
    queryFn: () => api.getCategories(1, 100),
  })

  const scrapeMutation = useMutation({
    mutationFn: (categoryId: string) => api.triggerScrape(categoryId, 20),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] })
      setScrapingId(null)
    },
    onError: () => {
      setScrapingId(null)
    },
  })

  const handleScrape = (categoryId: string) => {
    setScrapingId(categoryId)
    scrapeMutation.mutate(categoryId)
  }

  // 載入狀態
  if (isLoading) {
    return <LoadingSkeleton />
  }

  // 錯誤狀態
  if (error) {
    return <ErrorState />
  }

  return (
    <PageTransition>
      <div className="space-y-6">
        {/* ==================== 頁面標題 ==================== */}
        <div className="flex items-center justify-between">
          <div>
            <motion.h1
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4 }}
              className="text-2xl font-bold text-slate-800"
            >
              類別管理
            </motion.h1>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className="text-slate-500 mt-1"
            >
              管理 HKTVmall 商品類別與價格追踪
            </motion.p>
          </div>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.2 }}
          >
            <HoloButton
              variant="secondary"
              icon={<RefreshCw className="w-4 h-4" />}
              onClick={() => refetch()}
            >
              刷新
            </HoloButton>
          </motion.div>
        </div>

        {/* ==================== 類別表格 ==================== */}
        <HoloCard glowColor="cyan" scanLine>
          <HoloPanelHeader
            title="類別列表"
            subtitle={`共 ${categories?.items?.length || 0} 個類別`}
            icon={<FolderOpen className="w-5 h-5" />}
          />

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-100">
              <thead className="bg-gradient-to-r from-slate-50/80 to-cyan-50/30">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    類別名稱
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    商品數量
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    最後更新
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    狀態
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-slate-600 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {categories?.items.map((category, index) => (
                  <motion.tr
                    key={category.id}
                    variants={tableRowVariants}
                    initial="initial"
                    animate="animate"
                    whileHover="hover"
                    transition={{ duration: 0.3, delay: index * 0.05 }}
                    className="group cursor-pointer"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <motion.div
                          whileHover={{ scale: 1.1, rotate: 5 }}
                          transition={{ duration: 0.2 }}
                          className="w-10 h-10 bg-gradient-to-br from-cyan-50 to-blue-50 rounded-xl flex items-center justify-center mr-3 group-hover:shadow-md transition-shadow"
                        >
                          <FolderOpen className="w-5 h-5 text-cyan-600" />
                        </motion.div>
                        <div>
                          <Link
                            href={`/categories/${category.id}`}
                            className="text-sm font-medium text-slate-800 hover:text-cyan-600 transition-colors"
                          >
                            {category.name}
                          </Link>
                          {category.description && (
                            <p className="text-sm text-slate-500 truncate max-w-xs">
                              {category.description}
                            </p>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-medium text-slate-700">
                        {category.total_products.toLocaleString()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-slate-500">
                        {category.last_scraped_at
                          ? new Date(category.last_scraped_at).toLocaleString('zh-HK')
                          : '尚未抓取'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {category.is_active ? (
                        <HoloBadge variant="success">
                          <Check className="w-3 h-3" />
                          活躍
                        </HoloBadge>
                      ) : (
                        <HoloBadge variant="default">
                          停用
                        </HoloBadge>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex items-center justify-end gap-1">
                        {/* 抓取按鈕 */}
                        <HoloButton
                          variant="ghost"
                          size="sm"
                          onClick={() => handleScrape(category.id)}
                          disabled={scrapingId === category.id}
                          loading={scrapingId === category.id}
                          icon={scrapingId !== category.id ? <Play className="w-4 h-4" /> : undefined}
                        >
                          {scrapingId === category.id ? '抓取中' : '抓取'}
                        </HoloButton>

                        {/* 導出按鈕 */}
                        <motion.a
                          href={`/api/v1/categories/${category.id}/export/excel`}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors"
                        >
                          <Download className="w-4 h-4" />
                          導出
                        </motion.a>

                        {/* 詳情按鈕 */}
                        <Link href={`/categories/${category.id}`}>
                          <motion.span
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                          >
                            <ExternalLink className="w-4 h-4" />
                            詳情
                          </motion.span>
                        </Link>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* 空狀態 */}
          {(!categories?.items || categories.items.length === 0) && <EmptyState />}
        </HoloCard>
      </div>
    </PageTransition>
  )
}
