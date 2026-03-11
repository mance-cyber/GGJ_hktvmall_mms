'use client'

// =============================================
// Schedule Editor Component - Create and Edit Scheduled Reports
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
  schedule?: ScheduledReport | null  // Pass in for edit mode
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
// Constants
// =============================================

const REPORT_TYPES: { value: ReportType; label: string }[] = [
  { value: 'price_analysis', label: 'Price Analysis' },
  { value: 'competitor_report', label: 'Competitor Report' },
  { value: 'sales_summary', label: 'Sales Summary' },
  { value: 'inventory_alert', label: 'Inventory Alert' },
  { value: 'custom', label: 'Custom' },
]

const FREQUENCIES: { value: ScheduleFrequency; label: string }[] = [
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
]

const WEEKDAYS = [
  { value: 1, label: 'Monday' },
  { value: 2, label: 'Tuesday' },
  { value: 3, label: 'Wednesday' },
  { value: 4, label: 'Thursday' },
  { value: 5, label: 'Friday' },
  { value: 6, label: 'Saturday' },
  { value: 7, label: 'Sunday' },
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

  // Form state
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

  // Populate form in edit mode
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
      // Reset form
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

  // Create schedule
  const createMutation = useMutation({
    mutationFn: (data: ScheduleCreateRequest) => createSchedule(data),
    onSuccess: (newSchedule) => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] })
      onOpenChange(false)
      onSuccess?.(newSchedule)
    },
  })

  // Update schedule
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

  // Validate form
  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof FormData, string>> = {}

    if (!formData.name.trim()) {
      newErrors.name = 'Please enter a schedule name'
    }

    if (!formData.schedule_time) {
      newErrors.schedule_time = 'Please select an execution time'
    }

    if (formData.frequency === 'weekly' && formData.schedule_day === null) {
      newErrors.schedule_day = 'Please select a day of the week'
    }

    if (formData.frequency === 'monthly' && formData.schedule_day === null) {
      newErrors.schedule_day = 'Please select a day of the month'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  // Submit form
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

  // Update form field
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
            {isEditMode ? 'Edit Schedule' : 'Create Scheduled Report'}
          </DialogTitle>
          <DialogDescription>
            {isEditMode
              ? 'After modifying schedule settings, the next run will use the new settings'
              : 'Set up scheduled reports to auto-generate and send to Telegram'}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="name">Schedule Name *</Label>
            <Input
              id="name"
              placeholder="e.g. Daily Price Report"
              value={formData.name}
              onChange={(e) => updateField('name', e.target.value)}
              className={errors.name ? 'border-red-300' : ''}
            />
            {errors.name && (
              <p className="text-xs text-red-500">{errors.name}</p>
            )}
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              placeholder="Purpose or notes for this schedule..."
              value={formData.description}
              onChange={(e) => updateField('description', e.target.value)}
              rows={2}
            />
          </div>

          {/* Report Type */}
          <div className="space-y-2">
            <Label>Report Type</Label>
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

          {/* Frequency */}
          <div className="space-y-2">
            <Label>Frequency</Label>
            <Select
              value={formData.frequency}
              onValueChange={(v) => {
                updateField('frequency', v as ScheduleFrequency)
                // Reset schedule_day
                if (v === 'daily') {
                  updateField('schedule_day', null)
                } else if (v === 'weekly') {
                  updateField('schedule_day', 1) // Default Monday
                } else if (v === 'monthly') {
                  updateField('schedule_day', 1) // Default 1st
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

          {/* Execution Day (Weekly) */}
          {formData.frequency === 'weekly' && (
            <div className="space-y-2">
              <Label>Day of Week</Label>
              <Select
                value={formData.schedule_day?.toString() || ''}
                onValueChange={(v) => updateField('schedule_day', parseInt(v))}
              >
                <SelectTrigger className={errors.schedule_day ? 'border-red-300' : ''}>
                  <SelectValue placeholder="Select day" />
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

          {/* Execution Day (Monthly) */}
          {formData.frequency === 'monthly' && (
            <div className="space-y-2">
              <Label>Day of Month</Label>
              <Select
                value={formData.schedule_day?.toString() || ''}
                onValueChange={(v) => updateField('schedule_day', parseInt(v))}
              >
                <SelectTrigger className={errors.schedule_day ? 'border-red-300' : ''}>
                  <SelectValue placeholder="Select date" />
                </SelectTrigger>
                <SelectContent>
                  {Array.from({ length: 28 }, (_, i) => i + 1).map((day) => (
                    <SelectItem key={day} value={day.toString()}>
                      {day}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.schedule_day && (
                <p className="text-xs text-red-500">{errors.schedule_day}</p>
              )}
            </div>
          )}

          {/* Execution Time */}
          <div className="space-y-2">
            <Label htmlFor="schedule_time">Execution Time *</Label>
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
            <p className="text-xs text-slate-400">Timezone: Hong Kong (GMT+8)</p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{(error as Error).message || 'Operation failed, please try again later'}</span>
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
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isLoading}
            className="bg-purple-600 hover:bg-purple-700"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                {isEditMode ? 'Saving...' : 'Creating...'}
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                {isEditMode ? 'Save Changes' : 'Create Schedule'}
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default ScheduleEditor
