'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { motion } from 'framer-motion'
import Link from 'next/link'
import {
  Search,
  BarChart3,
  Globe,
  ShoppingCart,
  Zap,
  Filter,
  ArrowUpRight,
  Package,
  ThermometerSun,
  Layers,
  Search as SearchIcon,
  Loader2,
  Eye,
  TrendingUp,
  Sparkles,
  Bell,
  FileBarChart,
  Target,
  Download
} from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { useToast } from '@/components/ui/use-toast'
import {
  PageTransition,
  HoloCard,
  HoloPanelHeader,
  HoloButton,
  DataMetric,
  StaggerContainer
} from '@/components/ui/future-tech'

// =============================================
// Interfaces
// =============================================

interface CategoryData {
  name: string
  count: number
  percentage: number
}

// =============================================
// Page Component
// =============================================

export default function MarketResponsePage() {
  const { toast } = useToast()
  const [searchQuery, setSearchQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')

  // Handle search debounce
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
    const timeoutId = setTimeout(() => {
      setDebouncedQuery(e.target.value)
    }, 500)
    return () => clearTimeout(timeoutId)
  }

  // 匯出報告功能
  const handleExportReport = () => {
    toast({
      title: '功能開發中',
      description: '報告匯出功能即將推出，敬請期待！',
    })
  }

  // 使用現有 API 獲取數據
  const { data: products } = useQuery({
    queryKey: ['products-for-mrc'],
    queryFn: () => api.getProducts(1, 100),
  })

  const { data: competitors } = useQuery({
    queryKey: ['competitors-for-mrc'],
    queryFn: () => api.getCompetitors(),
  })

  const { data: alerts } = useQuery({
    queryKey: ['alerts-for-mrc'],
    queryFn: () => api.getAlerts(false, undefined, 10),
  })

  const { data: categories, isLoading: categoriesLoading } = useQuery({
    queryKey: ['categories-for-mrc'],
    queryFn: () => api.getCategories(1, 20),
  })

  // 計算統計數據
  const stats = {
    total_skus: products?.total || 0,
    products_with_competitors: competitors?.data?.reduce((sum, c) => sum + c.product_count, 0) || 0,
    seasonal_products: products?.data?.filter((p) => p.status === 'active').length || 0,
    unread_alerts: alerts?.unread_count || 0,
  }

  // 搜索結果使用現有商品數據過濾
  const searchResults = debouncedQuery.length > 0
    ? products?.data?.filter((p) =>
        p.name?.toLowerCase().includes(debouncedQuery.toLowerCase()) ||
        p.sku?.toLowerCase().includes(debouncedQuery.toLowerCase())
      ) || []
    : []
  const searchLoading = false

  // 季節性商品（使用現有商品數據）
  const seasonalProducts = products?.data?.slice(0, 5) || []
  const seasonalLoading = !products

  // 分類數據轉換
  const categoryData = categories?.items?.map((cat, idx) => ({
    name: cat.name,
    count: cat.total_products,
    percentage: Math.min(100, (cat.total_products / (products?.total || 1)) * 100 * 5),
  })) || []

  return (
    <PageTransition>
      <div className="space-y-8 p-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-2">
              <Globe className="w-8 h-8 text-primary" />
              市場應對中心
            </h1>
            <p className="text-muted-foreground mt-2">
              實時市場分析與競品應對系統
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant="outline" className="px-3 py-1 bg-blue-50 text-blue-700 border-blue-200">
              <Zap className="w-3 h-3 mr-1 fill-blue-700" /> 即時數據
            </Badge>
            <HoloButton variant="secondary" icon={<Download className="w-4 h-4" />} onClick={handleExportReport}>
              匯出報告
            </HoloButton>
          </div>
        </div>

        {/* Feature Introduction Cards */}
        <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <Link href="/competitors">
            <FeatureCard
              icon={Eye}
              title="競品監測"
              description="自動追蹤 HKTVmall 競爭對手的價格變動，當價格波動超過閾值時即時通知。"
              color="blue"
            />
          </Link>
          <Link href="/products">
            <FeatureCard
              icon={Target}
              title="SKU 自動配對"
              description="AI 智能配對您的 SKU 與競品商品，自動識別相同或相似產品。"
              color="purple"
            />
          </Link>
          <Link href="/ai-analysis">
            <FeatureCard
              icon={TrendingUp}
              title="價格趨勢分析"
              description="追蹤歷史價格走勢，識別最佳調價時機與市場週期規律。"
              color="green"
            />
          </Link>
          <Link href="/alerts">
            <FeatureCard
              icon={Bell}
              title="智能警報"
              description="自訂價格警報規則，競品降價、缺貨、新品上架即時推送通知。"
              color="orange"
            />
          </Link>
          <Link href="/agent">
            <FeatureCard
              icon={Sparkles}
              title="AI 文案生成"
              description="根據商品特性與競品描述，AI 自動生成優化的商品標題與描述。"
              color="pink"
            />
          </Link>
          <FeatureCard
            icon={FileBarChart}
            title="報表匯出"
            description="一鍵匯出市場分析報告，支援 Excel、PDF 格式，方便團隊分享。"
            color="cyan"
            onClick={handleExportReport}
          />
        </StaggerContainer>

        {/* Search Section */}
        <HoloCard className="p-2" glowColor="blue">
          <div className="flex items-center">
            <SearchIcon className="w-5 h-5 ml-3 text-muted-foreground" />
            <Input
              className="border-none shadow-none focus-visible:ring-0 bg-transparent text-lg placeholder:text-muted-foreground/50 h-12"
              placeholder="搜尋商品 (支援 SKU、中文、日文、英文)..."
              value={searchQuery}
              onChange={handleSearch}
            />
            {searchLoading && <Loader2 className="w-5 h-5 mr-3 animate-spin text-primary" />}
          </div>
        </HoloCard>

        {/* Search Results Dropdown */}
        {debouncedQuery && searchResults && (
          <div className="relative -mt-6">
            <div className="absolute top-0 left-0 right-0 bg-white/90 backdrop-blur-xl rounded-xl border border-slate-200 shadow-xl z-50 overflow-hidden max-h-[400px] overflow-y-auto">
              {searchResults.length > 0 ? (
                <div className="divide-y divide-slate-100">
                  {searchResults.map((product) => (
                    <Link key={product.id} href={`/products`}>
                      <div className="p-4 hover:bg-blue-50/50 transition-colors flex items-center justify-between cursor-pointer group">
                        <div>
                          <h4 className="font-medium text-slate-800 group-hover:text-primary transition-colors">{product.name}</h4>
                          <p className="text-xs text-slate-500 flex items-center gap-2 mt-1">
                            <Badge variant="secondary" className="text-[10px] h-5">{product.sku}</Badge>
                            <span>{product.category || '未分類'}</span>
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-slate-800">${Number(product.price || 0).toFixed(2)}</p>
                          <p className={cn(
                            "text-xs",
                            product.status === 'active' ? "text-green-600" : "text-red-500"
                          )}>{product.status === 'active' ? '有貨' : '缺貨'}</p>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center text-muted-foreground">
                  找不到符合「{debouncedQuery}」的商品
                </div>
              )}
            </div>
          </div>
        )}

        {/* Stats Overview */}
        <StaggerContainer className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Link href="/products">
            <DataMetric
              label="SKU 總數"
              value={stats?.total_skus || 0}
              icon={<Package className="w-5 h-5 text-blue-600" />}
              color="blue"
            />
          </Link>
          <Link href="/competitors">
            <DataMetric
              label="已監測競品"
              value={stats?.products_with_competitors || 0}
              icon={<Layers className="w-5 h-5 text-purple-600" />}
              color="purple"
            />
          </Link>
          <Link href="/products">
            <DataMetric
              label="當季商品"
              value={stats?.seasonal_products || 0}
              icon={<ThermometerSun className="w-5 h-5 text-orange-600" />}
              color="orange"
            />
          </Link>
          <Link href="/alerts">
            <DataMetric
              label="待處理警報"
              value={stats?.unread_alerts || 0}
              icon={<Zap className="w-5 h-5 text-cyan-600" />}
              color="cyan"
            />
          </Link>
        </StaggerContainer>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Category Breakdown */}
          <HoloCard className="lg:col-span-2" glowColor="blue">
            <HoloPanelHeader
              title="分類分佈"
              icon={<BarChart3 className="w-5 h-5" />}
              action={
                <Link href="/categories">
                  <HoloButton variant="ghost" size="sm">查看全部</HoloButton>
                </Link>
              }
            />
            <div className="p-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {categoriesLoading ? (
                  <div className="col-span-2 py-12 flex justify-center"><Loader2 className="animate-spin" /></div>
                ) : categoryData.map((cat, idx) => (
                  <Link key={idx} href="/categories">
                    <CategoryCard category={cat} index={idx} />
                  </Link>
                ))}
              </div>
            </div>
          </HoloCard>

          {/* Seasonal Products */}
          <HoloCard glowColor="green" className="bg-gradient-to-b from-orange-50/30 to-transparent">
            <HoloPanelHeader
              title="熱門商品"
              icon={<ThermometerSun className="w-5 h-5 text-orange-500" />}
              action={
                <Badge className="bg-orange-100 text-orange-700 hover:bg-orange-200 border-none">精選</Badge>
              }
            />
            <div className="p-6">
              <div className="space-y-4">
                {seasonalLoading ? (
                  <div className="py-12 flex justify-center"><Loader2 className="animate-spin" /></div>
                ) : seasonalProducts.map((product) => (
                  <Link key={product.id} href="/products">
                    <div className="flex items-center gap-3 p-3 rounded-xl bg-white/50 hover:bg-white/80 transition-all cursor-pointer group border border-transparent hover:border-orange-100">
                      <div className="w-12 h-12 rounded-lg bg-gray-100 overflow-hidden flex-shrink-0 relative">
                        <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                          <Package className="w-6 h-6" />
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-medium text-slate-800 truncate group-hover:text-orange-600 transition-colors">
                          {product.name}
                        </h4>
                        <div className="flex items-center justify-between mt-1">
                          <span className="text-xs text-muted-foreground">{product.status === 'active' ? '有貨' : '缺貨'}</span>
                          <span className="font-bold text-sm">${Number(product.price || 0).toFixed(0)}</span>
                        </div>
                      </div>
                      <ArrowUpRight className="w-4 h-4 text-slate-300 group-hover:text-orange-500 transition-colors" />
                    </div>
                  </Link>
                ))}
              </div>

              <Link href="/products">
                <HoloButton className="w-full mt-4" variant="secondary">
                  查看所有商品
                </HoloButton>
              </Link>
            </div>
          </HoloCard>
        </div>
      </div>
    </PageTransition>
  )
}

// =============================================
// Sub Components
// =============================================

function CategoryCard({ category, index }: { category: CategoryData, index: number }) {
  return (
    <div className="flex items-center p-4 rounded-xl bg-slate-50/50 border border-slate-100 hover:border-blue-200 hover:bg-blue-50/50 transition-all cursor-pointer">
      <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center shadow-sm text-lg font-bold text-slate-300 mr-4">
        {index + 1}
      </div>
      <div className="flex-1">
        <div className="flex justify-between mb-1">
          <span className="font-medium text-slate-700">{category.name}</span>
          <span className="font-bold text-slate-900">{category.count}</span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${category.percentage}%` }}
            transition={{ duration: 1, delay: index * 0.1 }}
            className="bg-primary h-full rounded-full"
          />
        </div>
      </div>
    </div>
  )
}

// =============================================
// 功能介紹卡片組件
// =============================================

function FeatureCard({
  icon: Icon,
  title,
  description,
  color,
  onClick
}: {
  icon: any
  title: string
  description: string
  color: 'blue' | 'purple' | 'green' | 'orange' | 'pink' | 'cyan'
  onClick?: () => void
}) {
  const colorMap = {
    blue: {
      bg: 'bg-blue-50 hover:bg-blue-100/80',
      icon: 'bg-blue-500/10 text-blue-600',
      border: 'border-blue-100 hover:border-blue-200',
    },
    purple: {
      bg: 'bg-purple-50 hover:bg-purple-100/80',
      icon: 'bg-purple-500/10 text-purple-600',
      border: 'border-purple-100 hover:border-purple-200',
    },
    green: {
      bg: 'bg-green-50 hover:bg-green-100/80',
      icon: 'bg-green-500/10 text-green-600',
      border: 'border-green-100 hover:border-green-200',
    },
    orange: {
      bg: 'bg-orange-50 hover:bg-orange-100/80',
      icon: 'bg-orange-500/10 text-orange-600',
      border: 'border-orange-100 hover:border-orange-200',
    },
    pink: {
      bg: 'bg-pink-50 hover:bg-pink-100/80',
      icon: 'bg-pink-500/10 text-pink-600',
      border: 'border-pink-100 hover:border-pink-200',
    },
    cyan: {
      bg: 'bg-cyan-50 hover:bg-cyan-100/80',
      icon: 'bg-cyan-500/10 text-cyan-600',
      border: 'border-cyan-100 hover:border-cyan-200',
    },
  }

  const colors = colorMap[color]

  return (
    <motion.div
      whileHover={{ y: -2, scale: 1.01 }}
      transition={{ duration: 0.2 }}
      onClick={onClick}
      className={cn(
        "p-4 rounded-xl border transition-all cursor-pointer",
        colors.bg,
        colors.border
      )}
    >
      <div className="flex items-start gap-3">
        <div className={cn("p-2 rounded-lg flex-shrink-0", colors.icon)}>
          <Icon className="w-5 h-5" />
        </div>
        <div className="min-w-0">
          <h3 className="font-semibold text-slate-800 mb-1">{title}</h3>
          <p className="text-sm text-slate-500 leading-relaxed">{description}</p>
        </div>
      </div>
    </motion.div>
  )
}
