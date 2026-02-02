'use client'

// =============================================
// 排程編輯器組件 - 創建和編輯排程報告
// =============================================

import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Clock,
  Calendar,
  FileText,
  Save,
  X,
  Loader2,
  AlertCircle,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  createSchedule,
  updateSchedule,
  type ScheduledReport,
  type ScheduleCreateRequest,
  type ScheduleUpdateRequest,
  type ScheduleFrequency,
  type ReportType,
} from '@/lib/api/workflow'

// =============================================
// Types
// =============================================

interface ScheduleEditorProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  schedule?: ScheduledReport | null  // 編輯模式時傳入
  conversationId?: string | null
  onSuccess?: (schedule: ScheduledReport) => void
}

interface FormData {
  name: string
  description: string
  report_type: ReportType
  frequency: ScheduleFrequency
  schedule_time: string
  schedule_day: number | null
  timezone: string
}

// =============================================
// 常量
// =============================================

const REPORT_TYPES: { value: ReportType; label: string }[] = [
  { value: 'price_analysis', label: '價格分析' },
  { value: 'competitor_report', label: '競品報告' },
  { value: 'sales_summary', label: '銷售摘要' },
  { value: 'inventory_alert', label: '庫存警報' },
  { value: 'custom', label: '自定義' },
]

const FREQUENCIES: { value: ScheduleFrequency; label: string }[] = [
  { value: 'daily', label: '每日' },
  { value: 'weekly', label: '每週' },
  { value: 'monthly', label: '每月' },
]

const WEEKDAYS = [
  { value: 1, label: '週一' },
  { value: 2, label: '週二' },
  { value: 3, label: '週三' },
  { value: 4, label: '週四' },
  { value: 5, label: '週五' },
  { value: 6, label: '週六' },
  { value: 7, label: '週日' },
]

// =============================================
// Main Component
// =============================================

export function ScheduleEditor({
  open,
  onOpenChange,
  schedule,
  conversationId,
  onSuccess,
}: ScheduleEditorProps) {
  const isEditMode = !!schedule
  const queryClient = useQueryClient()

  // 表單狀態
  const [formData, setFormData] = useState<FormData>({
    name: '',
    description: '',
    report_type: 'price_analysis',
    frequency: 'daily',
    schedule_time: '09:00',
    schedule_day: null,
    timezone: 'Asia/Hong_Kong',
  })

  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({})

  // 編輯模式時填充表單
  useEffect(() => {
    if (schedule) {
      setFormData({
        name: schedule.name,
        description: schedule.description || '',
        report_type: schedule.report_type as ReportType,
        frequency: schedule.frequency as ScheduleFrequency,
        schedule_time: schedule.schedule_time || '09:00',
        schedule_day: schedule.schedule_day,
        timezone: schedule.timezone || 'Asia/Hong_Kong',
      })
    } else {
      // 重置表單
      setFormData({
        name: '',
        description: '',
        report_type: 'price_analysis',
        frequency: 'daily',
        schedule_time: '09:00',
        schedule_day: null,
        timezone: 'Asia/Hong_Kong',
      })
    }
    setErrors({})
  }, [schedule, open])

  // 創建排程
  const createMutation = useMutation({
    mutationFn: (data: ScheduleCreateRequest) => createSchedule(data),
    onSuccess: (newSchedule) => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] })
      onOpenChange(false)
      onSuccess?.(newSchedule)
    },
  })

  // 更新排程
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: ScheduleUpdateRequest }) =>
      updateSchedule(id, data),
    onSuccess: (updatedSchedule) => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] })
      onOpenChange(false)
      onSuccess?.(updatedSchedule)
    },
  })

  const isLoading = createMutation.isPending || updateMutation.isPending
  const error = createMutation.error || updateMutation.error

  // 驗證表單
  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof FormData, string>> = {}

    if (!formData.name.trim()) {
      newErrors.name = '請輸入排程名稱'
    }

    if (!formData.schedule_time) {
      newErrors.schedule_time = '請選擇執行時間'
    }

    if (formData.frequency === 'weekly' && formData.schedule_day === null) {
      newErrors.schedule_day = '請選擇執行日'
    }

    if (formData.frequency === 'monthly' && formData.schedule_day === null) {
      newErrors.schedule_day = '請選擇執行日'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  // 提交表單
  const handleSubmit = () => {
    if (!validate()) return

    const payload = {
      name: formData.name.trim(),
      description: formData.description.trim() || undefined,
      report_type: formData.report_type,
      frequency: formData.frequency,
      schedule_time: formData.schedule_time,
      schedule_day: formData.schedule_day || undefined,
      timezone: formData.timezone,
    }

    if (isEditMode && schedule) {
      updateMutation.mutate({ id: schedule.id, data: payload })
    } else {
      createMutation.mutate(payload)
    }
  }

  // 更新表單欄位
  const updateField = <K extends keyof FormData>(field: K, value: FormData[K]) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: undefined }))
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[480px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-purple-500" />
            {isEditMode ? '編輯排程' : '創建排程報告'}
          </DialogTitle>
          <DialogDescription>
            {isEditMode
              ? '修改排程設定後，下次執行將使用新設定'
              : '設定定時報告，自動生成並發送到 Telegram'}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* 名稱 */}
          <div className="space-y-2">
            <Label htmlFor="name">排程名稱 *</Label>
            <Input
              id="name"
              placeholder="例如：每日價格報告"
              value={formData.name}
              onChange={(e) => updateField('name', e.target.value)}
              className={errors.name ? 'border-red-300' : ''}
            />
            {errors.name && (
              <p className="text-xs text-red-500">{errors.name}</p>
            )}
          </div>

          {/* 描述 */}
          <div className="space-y-2">
            <Label htmlFor="description">描述</Label>
            <Textarea
              id="description"
              placeholder="排程的用途或備註..."
              value={formData.description}
              onChange={(e) => updateField('description', e.target.value)}
              rows={2}
            />
          </div>

          {/* 報告類型 */}
          <div className="space-y-2">
            <Label>報告類型</Label>
            <Select
              value={formData.report_type}
              onValueChange={(v) => updateField('report_type', v as ReportType)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {REPORT_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 頻率 */}
          <div className="space-y-2">
            <Label>執行頻率</Label>
            <Select
              value={formData.frequency}
              onValueChange={(v) => {
                updateField('frequency', v as ScheduleFrequency)
                // 重置 schedule_day
                if (v === 'daily') {
                  updateField('schedule_day', null)
                } else if (v === 'weekly') {
                  updateField('schedule_day', 1) // 預設週一
                } else if (v === 'monthly') {
                  updateField('schedule_day', 1) // 預設 1 號
                }
              }}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {FREQUENCIES.map((freq) => (
                  <SelectItem key={freq.value} value={freq.value}>
                    {freq.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 執行日 (週) */}
          {formData.frequency === 'weekly' && (
            <div className="space-y-2">
              <Label>執行日</Label>
              <Select
                value={formData.schedule_day?.toString() || ''}
                onValueChange={(v) => updateField('schedule_day', parseInt(v))}
              >
                <SelectTrigger className={errors.schedule_day ? 'border-red-300' : ''}>
                  <SelectValue placeholder="選擇週幾" />
                </SelectTrigger>
                <SelectContent>
                  {WEEKDAYS.map((day) => (
                    <SelectItem key={day.value} value={day.value.toString()}>
                      {day.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.schedule_day && (
                <p className="text-xs text-red-500">{errors.schedule_day}</p>
              )}
            </div>
          )}

          {/* 執行日 (月) */}
          {formData.frequency === 'monthly' && (
            <div className="space-y-2">
              <Label>執行日 (每月幾號)</Label>
              <Select
                value={formData.schedule_day?.toString() || ''}
                onValueChange={(v) => updateField('schedule_day', parseInt(v))}
              >
                <SelectTrigger className={errors.schedule_day ? 'border-red-300' : ''}>
                  <SelectValue placeholder="選擇日期" />
                </SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 28 }, (_, i) => i + 1).map((day) => (
                    <SelectItem key={day} value={day.toString()}>
                      {day} 號
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.schedule_day && (
                <p className="text-xs text-red-500">{errors.schedule_day}</p>
              )}
            </div>
          )}

          {/* 執行時間 */}
          <div className="space-y-2">
            <Label htmlFor="schedule_time">執行時間 *</Label>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-slate-400" />
              <Input
                id="schedule_time"
                type="time"
                value={formData.schedule_time}
                onChange={(e) => updateField('schedule_time', e.target.value)}
                className={errors.schedule_time ? 'border-red-300' : ''}
              />
            </div>
            {errors.schedule_time && (
              <p className="text-xs text-red-500">{errors.schedule_time}</p>
            )}
            <p className="text-xs text-slate-400">時區：香港時間 (GMT+8)</p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{(error as Error).message || '操作失敗，請稍後重試'}</span>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            <X className="w-4 h-4 mr-2" />
            取消
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isLoading}
            className="bg-purple-600 hover:bg-purple-700"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                {isEditMode ? '保存中...' : '創建中...'}
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                {isEditMode ? '保存變更' : '創建排程'}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default ScheduleEditor
