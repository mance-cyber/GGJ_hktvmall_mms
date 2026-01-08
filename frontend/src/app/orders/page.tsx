'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { orderApi } from '@/lib/api'
import { format } from 'date-fns'
import {
  RefreshCw,
  Package,
  Truck,
  CheckCircle2,
  Clock,
  AlertCircle,
  Search,
  Filter
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useToast } from '@/components/ui/use-toast'
import { cn } from '@/lib/utils'

export default function OrdersPage() {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState('all')

  const { data: ordersData, isLoading } = useQuery({
    queryKey: ['orders', page, statusFilter],
    queryFn: () => orderApi.getOrders(page, statusFilter === 'all' ? undefined : statusFilter),
  })

  const syncMutation = useMutation({
    mutationFn: () => orderApi.syncOrders(7),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['orders'] })
      toast({
        title: "同步完成",
        description: `成功同步 ${data.synced_count} 張訂單`,
      })
    },
    onError: (error: any) => {
      toast({
        title: "同步失敗",
        description: error.message,
        variant: "destructive",
      })
    }
  })

  return (
    <div className="space-y-8 animate-fade-in-up">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">訂單管理</h1>
          <p className="text-muted-foreground mt-1">查看與管理 HKTVmall 訂單</p>
        </div>
        <Button 
          onClick={() => syncMutation.mutate()} 
          disabled={syncMutation.isPending}
          className="gap-2"
        >
          <RefreshCw className={cn("w-4 h-4", syncMutation.isPending && "animate-spin")} />
          同步訂單
        </Button>
      </div>

      <div className="glass-panel p-4 rounded-xl flex flex-col sm:flex-row gap-4 border border-white/40">
        <div className="flex gap-2 w-full sm:w-auto">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[180px] bg-white/50 border-white/20">
              <SelectValue placeholder="訂單狀態" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">所有狀態</SelectItem>
              <SelectItem value="Pending">待處理 (Pending)</SelectItem>
              <SelectItem value="Shipped">已出貨 (Shipped)</SelectItem>
              <SelectItem value="Delivered">已送達 (Delivered)</SelectItem>
              <SelectItem value="Cancelled">已取消 (Cancelled)</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="space-y-4">
        {isLoading ? (
          <div className="flex justify-center py-12">
            <RefreshCw className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : ordersData?.data.length === 0 ? (
          <div className="py-16 text-center text-slate-500 glass-panel rounded-xl">
            <Package className="w-12 h-12 mx-auto mb-4 text-slate-300" />
            <p>暫無訂單資料</p>
            <Button variant="link" onClick={() => syncMutation.mutate()}>點擊同步</Button>
          </div>
        ) : (
          ordersData?.data.map((order) => (
            <div key={order.id} className="glass-panel p-6 rounded-xl border border-white/40 hover:shadow-md transition-all">
              <div className="flex flex-col md:flex-row justify-between gap-4 mb-4 pb-4 border-b border-slate-100">
                <div className="flex items-start gap-4">
                  <div className="p-3 bg-blue-50 rounded-lg text-blue-600">
                    <Package className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-bold text-lg text-slate-900">{order.order_number}</h3>
                    <div className="flex items-center gap-2 text-sm text-slate-500 mt-1">
                      <Clock className="w-3 h-3" />
                      {format(new Date(order.order_date), 'yyyy-MM-dd HH:mm')}
                      <span className="mx-1">•</span>
                      {order.delivery_mode}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <Badge className={cn(
                    "mb-2",
                    order.status === 'Pending' ? "bg-yellow-100 text-yellow-700 hover:bg-yellow-100" :
                    order.status === 'Shipped' ? "bg-blue-100 text-blue-700 hover:bg-blue-100" :
                    "bg-slate-100 text-slate-700 hover:bg-slate-100"
                  )}>
                    {order.status}
                  </Badge>
                  <div className="font-mono font-bold text-lg">${order.total_amount}</div>
                </div>
              </div>
              
              <div className="space-y-2">
                {order.items.map((item) => (
                  <div key={item.id} className="flex justify-between items-center text-sm">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="font-mono text-xs">{item.sku_code}</Badge>
                      <span className="text-slate-700">{item.product_name}</span>
                    </div>
                    <div className="text-slate-500">
                      x{item.quantity} <span className="mx-2 text-slate-300">|</span> ${item.unit_price}
                    </div>
                  </div>
                ))}
              </div>
              
              {order.ship_by_date && (
                <div className="mt-4 pt-3 border-t border-slate-50 text-xs text-red-500 flex items-center">
                  <AlertCircle className="w-3 h-3 mr-1" />
                  最遲出貨: {format(new Date(order.ship_by_date), 'yyyy-MM-dd HH:mm')}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
