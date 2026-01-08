'use client'

import { useState } from 'react'
import { Competitor, CompetitorCreate } from '@/lib/api'
import { Check, RefreshCw } from 'lucide-react'
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

// 平台選項
const PLATFORMS = [
  { value: 'hktvmall', label: 'HKTVmall' },
  { value: 'watsons', label: 'Watsons' },
  { value: 'mannings', label: 'Mannings' },
  { value: 'parknshop', label: "PARKnSHOP" },
  { value: 'ztore', label: 'Ztore' },
  { value: 'other', label: '其他' },
]

export function CompetitorFormDialog({
  open,
  onOpenChange,
  initialData,
  onSubmit,
  isLoading,
  title
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  initialData?: Competitor
  onSubmit: (data: CompetitorCreate) => void
  isLoading: boolean
  title: string
}) {
  const [formData, setFormData] = useState<CompetitorCreate>({
    name: initialData?.name || '',
    platform: initialData?.platform || 'hktvmall',
    base_url: initialData?.base_url || '',
    notes: initialData?.notes || '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] glass-panel border-white/40">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">{title}</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-6 mt-4">
          <div className="space-y-4">
            <div className="grid gap-2">
              <Label htmlFor="name">名稱 <span className="text-destructive">*</span></Label>
              <Input
                id="name"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="例如：Watsons 屈臣氏"
                className="bg-white/50"
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="platform">平台 <span className="text-destructive">*</span></Label>
              <Select
                value={formData.platform}
                onValueChange={(value) => setFormData({ ...formData, platform: value })}
              >
                <SelectTrigger className="bg-white/50">
                  <SelectValue placeholder="選擇平台" />
                </SelectTrigger>
                <SelectContent>
                  {PLATFORMS.map((platform) => (
                    <SelectItem key={platform.value} value={platform.value}>
                      {platform.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="url">網站 URL</Label>
              <Input
                id="url"
                type="url"
                value={formData.base_url}
                onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
                placeholder="https://www.example.com"
                className="bg-white/50"
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="notes">備註</Label>
              <Textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                placeholder="關於此競爭對手的備註..."
                className="bg-white/50 min-h-[100px]"
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              取消
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
              className="bg-primary hover:bg-primary/90"
            >
              {isLoading ? (
                <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Check className="w-4 h-4 mr-2" />
              )}
              {initialData ? '保存修改' : '立即新增'}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
