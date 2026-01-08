import os

content = r"""'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, OwnProduct } from '@/lib/api'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search,
  Filter,
  Plus,
  MoreHorizontal,
  Edit,
  Trash2,
  Package,
  AlertCircle,
  CheckCircle2,
  XCircle,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

export default function ProductsPage() {
  const queryClient = useQueryClient()
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [categoryFilter, setCategoryFilter] = useState('all')
  
  // 獲取商品列表
  const { data: productsData, isLoading, error } = useQuery({
    queryKey: ['products', page, search, statusFilter, categoryFilter],
    queryFn: () => api.getProducts(
      page, 
      20, 
      search || undefined, 
      statusFilter === 'all' ? undefined : statusFilter, 
      categoryFilter === 'all' ? undefined : categoryFilter
    ),
  })

  // 刪除商品
  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.deleteOwnProduct(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
    },
  })

  // 同步商品
  const syncMutation = useMutation({
    mutationFn: () => api.hktvSyncProducts(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      alert(`同步已開始！\n模式: ${data.mode}\n${data.message}`)
    },
    onError: (err) => {
      alert(`同步失敗: ${err}`)
    }
  })

  const totalPages = productsData ? Math.ceil(productsData.total / productsData.limit) : 0

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
        <span className="font-medium">無法載入商品數據，請稍後再試。</span>
      </div>
    )
  }

  return (
    <div className="space-y-8 animate-fade-in-up">
      {/* 頁面標題與操作欄 */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">商品管理</h1>
          <p className="text-muted-foreground mt-1">管理您的商品庫存與價格策略</p>
        </div>
        <div className="flex gap-2">
          <Button 
            variant="outline" 
            onClick={() => syncMutation.mutate()}
            disabled={syncMutation.isPending}
            className="gap-2 border-blue-200 text-blue-700 hover:bg-blue-50"
          >
            <RefreshCw className={cn("w-4 h-4", syncMutation.isPending && "animate-spin")} />
            同步 HKTVmall
          </Button>
          <Button className="bg-primary hover:bg-primary/90 shadow-lg shadow-blue-500/20">
            <Plus className="w-4 h-4 mr-2" />
            新增商品
          </Button>
        </div>
      </div>

      {/* 篩選工具欄 */}
      <div className="glass-panel p-4 rounded-xl flex flex-col sm:flex-row gap-4 border border-white/40">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="搜索商品名稱、SKU..." 
            className="pl-9 bg-white/50 border-white/20"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[140px] bg-white/50 border-white/20">
              <SelectValue placeholder="狀態" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">所有狀態</SelectItem>
              <SelectItem value="active">上架中</SelectItem>
              <SelectItem value="draft">草稿</SelectItem>
              <SelectItem value="archived">已歸檔</SelectItem>
            </SelectContent>
          </Select>
          <Select value={categoryFilter} onValueChange={setCategoryFilter}>
            <SelectTrigger className="w-[140px] bg-white/50 border-white/20">
              <SelectValue placeholder="分類" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">所有分類</SelectItem>
              <SelectItem value="health">保健品</SelectItem>
              <SelectItem value="beauty">美容護膚</SelectItem>
              <SelectItem value="food">食品飲料</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* 商品表格 */}
      <div className="glass-panel rounded-xl border border-white/40 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-slate-50/50 text-slate-500 font-medium border-b border-slate-100">
              <tr>
                <th className="px-6 py-4">商品資訊</th>
                <th className="px-6 py-4">狀態</th>
                <th className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end cursor-pointer hover:text-primary">
                    售價 <ArrowUpDown className="w-3 h-3 ml-1" />
                  </div>
                </th>
                <th className="px-6 py-4 text-right">庫存</th>
                <th className="px-6 py-4 text-right">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100/50">
              {productsData?.data.map((product) => (
                <tr key={product.id} className="hover:bg-blue-50/30 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-lg bg-slate-100 flex items-center justify-center overflow-hidden border border-slate-200">
                        {product.images?.[0] ? (
                          <img src={product.images[0]} alt={product.name} className="w-full h-full object-cover" />
                        ) : (
                          <Package className="w-6 h-6 text-slate-400" />
                        )}
                      </div>
                      <div>
                        <div className="font-medium text-slate-900 group-hover:text-primary transition-colors">
                          {product.name}
                        </div>
                        <div className="text-xs text-slate-500 mt-0.5">SKU: {product.sku}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={product.status} />
                  </td>
                  <td className="px-6 py-4 text-right font-mono font-medium text-slate-700">
                    ${product.price?.toFixed(2) || '-'}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className={cn(
                      "font-medium",
                      product.stock_quantity < 10 ? "text-red-500" : "text-slate-600"
                    )}>
                      {product.stock_quantity}
                    </span>
                  </td>
                  <td classNam
