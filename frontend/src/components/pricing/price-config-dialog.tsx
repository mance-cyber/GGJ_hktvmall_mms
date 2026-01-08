import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Loader2, DollarSign, ShieldAlert, Settings2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { useToast } from '@/components/ui/use-toast'
import { pricingApi } from '@/lib/api'

// Schema
const formSchema = z.object({
  cost: z.coerce.number().min(0, "成本不能為負數").optional(),
  min_price: z.coerce.number().min(0, "最低價不能為負數").optional(),
  max_price: z.coerce.number().min(0, "最高價不能為負數").optional(),
  auto_pricing_enabled: z.boolean().default(false),
})

interface PriceConfigDialogProps {
  productId: string
  productName: string
  currentConfig: {
    cost?: number | null
    min_price?: number | null
    max_price?: number | null
    auto_pricing_enabled?: boolean
  }
  trigger?: React.ReactNode
  open?: boolean
  onOpenChange?: (open: boolean) => void
  onSuccess?: () => void
}

export function PriceConfigDialog({
  productId,
  productName,
  currentConfig,
  trigger,
  open: controlledOpen,
  onOpenChange: setControlledOpen,
  onSuccess
}: PriceConfigDialogProps) {
  const [internalOpen, setInternalOpen] = useState(false)
  const { toast } = useToast()

  const isControlled = controlledOpen !== undefined
  const open = isControlled ? controlledOpen : internalOpen
  const setOpen = isControlled ? setControlledOpen : setInternalOpen

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      cost: currentConfig.cost || undefined,
      min_price: currentConfig.min_price || undefined,
      max_price: currentConfig.max_price || undefined,
      auto_pricing_enabled: currentConfig.auto_pricing_enabled || false,
    },
  })
  
  // Reset form when dialog opens or productId changes
  useEffect(() => {
    if (open) {
      form.reset({
        cost: currentConfig.cost || undefined,
        min_price: currentConfig.min_price || undefined,
        max_price: currentConfig.max_price || undefined,
        auto_pricing_enabled: currentConfig.auto_pricing_enabled || false,
      })
    }
  }, [open, productId, currentConfig, form])

  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      await pricingApi.updateProductConfig(productId, values)
      toast({
        title: "設定已更新",
        description: `已更新 ${productName} 的定價策略`,
      })
      setOpen && setOpen(false)
      if (onSuccess) onSuccess()
    } catch (error: any) {
      toast({
        title: "更新失敗",
        description: error.message,
        variant: "destructive",
      })
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      {trigger && <DialogTrigger asChild>{trigger}</DialogTrigger>}
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>智能定價設定</DialogTitle>
          <DialogDescription>
            設定 {productName} 的成本與價格保護範圍。AI 改價將嚴格遵守這些限制。
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            
            {/* 成本價 */}
            <FormField
              control={form.control}
              name="cost"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>成本價 (Cost)</FormLabel>
                  <FormControl>
                    <div className="relative">
                      <DollarSign className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input type="number" step="0.1" className="pl-8" placeholder="0.00" {...field} />
                    </div>
                  </FormControl>
                  <FormDescription>用於計算利潤率</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              {/* 最低售價 */}
              <FormField
                control={form.control}
                name="min_price"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-red-600 flex items-center gap-1">
                      <ShieldAlert className="w-3 h-3" />
                      最低售價
                    </FormLabel>
                    <FormControl>
                      <div className="relative">
                        <DollarSign className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input type="number" step="0.1" className="pl-8" placeholder="0.00" {...field} />
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              {/* 最高售價 */}
              <FormField
                control={form.control}
                name="max_price"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>最高售價</FormLabel>
                    <FormControl>
                      <div className="relative">
                        <DollarSign className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                        <Input type="number" step="0.1" className="pl-8" placeholder="0.00" {...field} />
                      </div>
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            {/* AI 自動定價開關 */}
            <FormField
              control={form.control}
              name="auto_pricing_enabled"
              render={({ field }) => (
                <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3 shadow-sm">
                  <div className="space-y-0.5">
                    <FormLabel>啟用 AI 監測</FormLabel>
                    <FormDescription>
                      允許 AI 根據競品價格提供改價建議
                    </FormDescription>
                  </div>
                  <FormControl>
                    <Switch
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button type="submit" disabled={form.formState.isSubmitting}>
                {form.formState.isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                保存設定
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
