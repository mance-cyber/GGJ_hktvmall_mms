'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { motion } from 'framer-motion'
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
  Target
} from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

// =============================================
// Interfaces
// =============================================

interface MrcStats {
  total_skus: number
  products_with_competitors: number
  seasonal_products: number
  unread_alerts: number
}

interface CategoryData {
  name: string
  count: number
  percentage: number
}

interface SeasonalProduct {
  id: string
  name: string
  season: string
  status: string
  price: number
  image_url?: string
}

interface SearchResult {
  id: string
  name: string
  sku: string
  category: string
  price: number
  stock_status: string
}

// =============================================
// Page Component
// =============================================

export default function MarketResponsePage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')

  // Handle search debounce
  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
    // Simple debounce logic could be added here, currently just setting state
    // In a real app, use a debounce hook
    const timeoutId = setTimeout(() => {
      setDebouncedQuery(e.target.value)
    }, 500)
    return () => clearTimeout(timeoutId)
  }

  // Fetch Data
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['mrc-stats'],
    queryFn: () => api.getMrcStatsOverview(),
  })

  const { data: categories, isLoading: categoriesLoading } = useQuery({
    queryKey: ['mrc-categories'],
    queryFn: () => api.getMrcCategories(),
  })

  const { data: seasonalProducts, isLoading: seasonalLoading } = useQuery({
    queryKey: ['mrc-seasonal'],
    queryFn: () => api.getMrcSeasonalProducts(),
  })

  const { data: searchResults, isLoading: searchLoading } = useQuery({
    queryKey: ['mrc-search', debouncedQuery],
    queryFn: () => api.searchMrcProducts(debouncedQuery),
    enabled: debouncedQuery.length > 0,
  })

  return (
    <div className="space-y-8 animate-fade-in-up p-6">
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
          <Button variant="outline" className="glass-card">
            匯出報告
          </Button>
        </div>
      </div>

      {/* Feature Introduction Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <FeatureCard 
          icon={Eye}
          title="競品監測"
          description="自動追蹤 HKTVmall 競爭對手的價格變動，當價格波動超過閾值時即時通知。"
          color="blue"
        />
        <FeatureCard 
          icon={Target}
          title="SKU 自動配對"
          description="AI 智能配對您的 SKU 與競品商品，自動識別相同或相似產品。"
          color="purple"
        />
        <FeatureCard 
          icon={TrendingUp}
          title="價格趨勢分析"
          description="追蹤歷史價格走勢，識別最佳調價時機與市場週期規律。"
          color="green"
        />
        <FeatureCard 
          icon={Bell}
          title="智能警報"
          description="自訂價格警報規則，競品降價、缺貨、新品上架即時推送通知。"
          color="orange"
        />
        <FeatureCard 
          icon={Sparkles}
          title="AI 文案生成"
          description="根據商品特性與競品描述，AI 自動生成優化的商品標題與描述。"
          color="pink"
        />
        <FeatureCard 
          icon={FileBarChart}
          title="報表匯出"
          description="一鍵匯出市場分析報告，支援 Excel、PDF 格式，方便團隊分享。"
          color="cyan"
        />
      </div>

      {/* Search Section */}
      <div className="relative">
        <div className="glass-panel p-2 rounded-2xl flex items-center shadow-lg shadow-blue-500/10 border-blue-100/50">
          <SearchIcon className="w-5 h-5 ml-3 text-muted-foreground" />
          <Input 
            className="border-none shadow-none focus-visible:ring-0 bg-transparent text-lg placeholder:text-muted-foreground/50 h-12"
            placeholder="搜尋商品 (支援 SKU、中文、日文、英文)..."
            value={searchQuery}
            onChange={handleSearch}
          />
          {searchLoading && <Loader2 className="w-5 h-5 mr-3 animate-spin text-primary" />}
        </div>
        
        {/* Search Results Dropdown */}
        {debouncedQuery && searchResults && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white/90 backdrop-blur-xl rounded-xl border border-slate-200 shadow-xl z-50 overflow-hidden max-h-[400px] overflow-y-auto">
            {searchResults.length > 0 ? (
              <div className="divide-y divide-slate-100">
                {searchResults.map((product: SearchResult) => (
                  <div key={product.id} className="p-4 hover:bg-blue-50/50 transition-colors flex items-center justify-between cursor-pointer group">
                    <div>
                      <h4 className="font-medium text-slate-800 group-hover:text-primary transition-colors">{product.name}</h4>
                      <p className="text-xs text-slate-500 flex items-center gap-2 mt-1">
                        <Badge variant="secondary" className="text-[10px] h-5">{product.sku}</Badge>
                        <span>{product.category}</span>
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-slate-800">${product.price}</p>
                      <p className={cn(
                        "text-xs",
                        product.stock_status === 'in_stock' ? "text-green-600" : "text-red-500"
                      )}>{product.stock_status === 'in_stock' ? '有貨' : product.stock_status === 'out_of_stock' ? '缺貨' : product.stock_status}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-muted-foreground">
                找不到符合「{debouncedQuery}」的商品
              </div>
            )}
          </div>
        )}
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="SKU 總數" 
          value={stats?.total_skus || 0} 
          icon={Package}
          color="blue"
          trend="GogoJap 商品庫"
        />
        <StatCard 
          title="已監測競品" 
          value={stats?.products_with_competitors || 0} 
          icon={Layers}
          color="purple"
          trend="自動配對中"
        />
        <StatCard 
          title="當季商品" 
          value={stats?.seasonal_products || 0} 
          icon={ThermometerSun}
          color="orange"
          trend="季節限定"
        />
        <StatCard 
          title="待處理警報" 
          value={stats?.unread_alerts || 0} 
          icon={Zap}
          color="red"
          trend="需要關注"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Category Breakdown */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-6 border border-white/40">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-primary" />
              分類分佈
            </h2>
            <Button variant="ghost" size="sm">查看全部</Button>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {categoriesLoading ? (
              <div className="col-span-2 py-12 flex justify-center"><Loader2 className="animate-spin" /></div>
            ) : categories?.map((cat: CategoryData, idx: number) => (
              <CategoryCard key={idx} category={cat} index={idx} />
            ))}
          </div>
        </div>

        {/* Seasonal Products */}
        <div className="glass-panel rounded-2xl p-6 border border-white/40 bg-gradient-to-b from-orange-50/30 to-transparent">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
              <ThermometerSun className="w-5 h-5 text-orange-500" />
              當季精選
            </h2>
            <Badge className="bg-orange-100 text-orange-700 hover:bg-orange-200 border-none">當季</Badge>
          </div>

          <div className="space-y-4">
            {seasonalLoading ? (
              <div className="py-12 flex justify-center"><Loader2 className="animate-spin" /></div>
            ) : seasonalProducts?.slice(0, 5).map((product: SeasonalProduct) => (
              <div key={product.id} className="flex items-center gap-3 p-3 rounded-xl bg-white/50 hover:bg-white/80 transition-all cursor-pointer group border border-transparent hover:border-orange-100">
                <div className="w-12 h-12 rounded-lg bg-gray-100 overflow-hidden flex-shrink-0 relative">
                  {/* Placeholder for image */}
                  <div className="absolute inset-0 flex items-center justify-center text-gray-400">
                    <Package className="w-6 h-6" />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-slate-800 truncate group-hover:text-orange-600 transition-colors">
                    {product.name}
                  </h4>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-muted-foreground">{product.season}</span>
                    <span className="font-bold text-sm">${product.price}</span>
                  </div>
                </div>
                <ArrowUpRight className="w-4 h-4 text-slate-300 group-hover:text-orange-500 transition-colors" />
              </div>
            ))}
          </div>
          
          <Button className="w-full mt-4 bg-white hover:bg-orange-50 text-orange-600 border border-orange-200 shadow-sm" variant="outline">
            查看所有當季商品
          </Button>
        </div>
      </div>
    </div>
  )
}

// =============================================
// Sub Components
// =============================================

function StatCard({ 
  title, 
  value, 
  icon: Icon, 
  color,
  trend
}: { 
  title: string
  value: number
  icon: any
  color: 'blue' | 'purple' | 'orange' | 'red'
  trend: string
}) {
  const colors = {
    blue: 'bg-blue-500/10 text-blue-600',
    purple: 'bg-purple-500/10 text-purple-600',
    orange: 'bg-orange-500/10 text-orange-600',
    red: 'bg-red-500/10 text-red-600',
  }

  return (
    <motion.div 
      whileHover={{ y: -5 }}
      className="glass-card rounded-2xl p-6"
    >
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <h3 className="text-3xl font-bold mt-2 text-slate-800">{value}</h3>
        </div>
        <div className={cn("p-3 rounded-xl", colors[color])}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
      <div className="mt-4 flex items-center text-xs font-medium text-muted-foreground bg-slate-50 w-fit px-2 py-1 rounded-full">
        {trend}
      </div>
    </motion.div>
  )
}

function CategoryCard({ category, index }: { category: CategoryData, index: number }) {
  return (
    <div className="flex items-center p-4 rounded-xl bg-slate-50/50 border border-slate-100 hover:border-blue-200 transition-all">
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
  color 
}: { 
  icon: any
  title: string
  description: string
  color: 'blue' | 'purple' | 'green' | 'orange' | 'pink' | 'cyan'
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
