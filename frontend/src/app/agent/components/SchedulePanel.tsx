'use client'

// =============================================
// 排程面板組件 - 顯示和管理 AI 排程報告
// =============================================

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Clock,
  Calendar,
  Play,
  Pause,
  Trash2,
  MoreHorizontal,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  ChevronRight,
  Loader2,
  CalendarClock,
  FileText,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import {
  listSchedules,
  pauseSchedule,
  resumeSchedule,
  deleteSchedule,
  triggerSchedule,
  formatFrequency,
  formatScheduleStatus,
  formatReportType,
  getStatusColor,
  type ScheduledReport,
  type ScheduleStatus,
} from '@/lib/api/workflow'

// =============================================
// Types
// =============================================

interface SchedulePanelProps {
  conversationId?: string | null
  onScheduleClick?: (scheduleId: string) => void
  compact?: boolean
}

// =============================================
// 相對時間格式化
// =============================================

function formatNextRunTime(dateStr: string | null): string {
  if (!dateStr) return '未設定'

  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = date.getTime() - now.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMs < 0) return '已過期'
  if (diffMins < 1) return '即將執行'
  if (diffMins < 60) return `${diffMins} 分鐘後`
  if (diffHours < 24) return `${diffHours} 小時後`
  if (diffDays < 7) return `${diffDays} 天後`

  return date.toLocaleDateString('zh-HK', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// =============================================
// 排程卡片組件
// =============================================

function ScheduleCard({
  schedule,
  onPause,
  onResume,
  onDelete,
  onTrigger,
  onClick,
  isLoading,
}: {
  schedule: ScheduledReport
  onPause: () => void
  onResume: () => void
  onDelete: () => void
  onTrigger: () => void
  onClick?: () => void
  isLoading?: boolean
}) {
  const isPaused = schedule.status === 'paused'
  const isFailed = schedule.status === 'failed'

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className={cn(
        "bg-white rounded-lg border p-3 transition-all hover:shadow-sm",
        onClick && "cursor-pointer hover:border-purple-200",
        isFailed && "border-red-200 bg-red-50/50"
      )}
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <FileText className="w-4 h-4 text-purple-500 flex-shrink-0" />
            <h4 className="font-medium text-slate-700 truncate">
              {schedule.name}
            </h4>
          </div>
          {schedule.description && (
            <p className="text-xs text-slate-500 mt-1 line-clamp-1">
              {schedule.description}
            </p>
          )}
        </div>

        {/* Status Badge */}
        <span className={cn(
          "px-2 py-0.5 rounded-full text-xs font-medium flex-shrink-0",
          getStatusColor(schedule.status as ScheduleStatus)
        )}>
          {formatScheduleStatus(schedule.status as ScheduleStatus)}
        </span>
      </div>

      {/* Info Row */}
      <div className="mt-3 flex items-center gap-4 text-xs text-slate-500">
        <span className="flex items-center gap-1">
          <Calendar className="w-3 h-3" />
          {formatFrequency(schedule.frequency as any)}
        </span>
        {schedule.schedule_time && (
          <span className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {schedule.schedule_time}
          </span>
        )}
        <span className="flex items-center gap-1">
          <RefreshCw className="w-3 h-3" />
          {schedule.run_count} 次
        </span>
      </div>

      {/* Next Run */}
      {schedule.status === 'active' && (
        <div className="mt-2 flex items-center gap-1 text-xs">
          <CalendarClock className="w-3 h-3 text-purple-500" />
          <span className="text-slate-600">
            下次執行: {formatNextRunTime(schedule.next_run_at)}
          </span>
        </div>
      )}

      {/* Actions */}
      <div className="mt-3 flex items-center justify-between border-t pt-2">
        <div className="flex items-center gap-1">
          {isPaused ? (
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onResume()
              }}
              disabled={isLoading}
              className="h-7 text-xs text-green-600 hover:text-green-700 hover:bg-green-50"
            >
              <Play className="w-3 h-3 mr-1" />
              恢復
            </Button>
          ) : (
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation()
                onPause()
              }}
              disabled={isLoading || isFailed}
              className="h-7 text-xs text-yellow-600 hover:text-yellow-700 hover:bg-yellow-50"
            >
              <Pause className="w-3 h-3 mr-1" />
              暫停
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation()
              onTrigger()
            }}
            disabled={isLoading || isPaused}
            className="h-7 text-xs"
          >
            <RefreshCw className="w-3 h-3 mr-1" />
            立即執行
          </Button>
        </div>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={(e) => e.stopPropagation()}
            >
              <MoreHorizontal className="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation()
                onDelete()
              }}
              className="text-red-600 focus:text-red-700 focus:bg-red-50"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              刪除排程
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </motion.div>
  )
}

// =============================================
// Main Component
// =============================================

export function SchedulePanel({
  conversationId,
  onScheduleClick,
  compact = false,
}: SchedulePanelProps) {
  const [deleteTarget, setDeleteTarget] = useState<ScheduledReport | null>(null)
  const queryClient = useQueryClient()

  // 獲取排程列表
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['schedules', conversationId],
    queryFn: () => listSchedules({
      conversation_id: conversationId || undefined,
      limit: compact ? 5 : 20,
    }),
    refetchInterval: 60000, // 每分鐘刷新
  })

  // 暫停排程
  const pauseMutation = useMutation({
    mutationFn: pauseSchedule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] })
    },
  })

  // 恢復排程
  const resumeMutation = useMutation({
    mutationFn: resumeSchedule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] })
    },
  })

  // 刪除排程
  const deleteMutation = useMutation({
    mutationFn: deleteSchedule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] })
      setDeleteTarget(null)
    },
  })

  // 立即觸發
  const triggerMutation = useMutation({
    mutationFn: triggerSchedule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] })
    },
  })

  const schedules = data?.items || []
  const isActionLoading =
    pauseMutation.isPending ||
    resumeMutation.isPending ||
    deleteMutation.isPending ||
    triggerMutation.isPending

  // Loading State
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="w-6 h-6 animate-spin text-purple-500" />
      </div>
    )
  }

  // Error State
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <AlertCircle className="w-8 h-8 text-red-400 mb-2" />
        <p className="text-sm text-slate-500">無法載入排程</p>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => refetch()}
          className="mt-2"
        >
          <RefreshCw className="w-4 h-4 mr-1" />
          重試
        </Button>
      </div>
    )
  }

  // Empty State
  if (schedules.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <CalendarClock className="w-10 h-10 text-slate-300 mb-3" />
        <p className="text-sm text-slate-500 mb-1">暫無排程報告</p>
        <p className="text-xs text-slate-400">
          同 Jap仔 講「每日 9 點發送價格報告」即可創建
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-slate-700 flex items-center gap-2">
          <CalendarClock className="w-4 h-4 text-purple-500" />
          排程報告
          <span className="text-xs text-slate-400">({schedules.length})</span>
        </h3>
        <Button
          variant="ghost"
          size="icon"
          className="h-7 w-7"
          onClick={() => refetch()}
          disabled={isLoading}
        >
          <RefreshCw className={cn("w-4 h-4", isLoading && "animate-spin")} />
        </Button>
      </div>

      {/* Schedule List */}
      <div className="space-y-2">
        <AnimatePresence>
          {schedules.map((schedule) => (
            <ScheduleCard
              key={schedule.id}
              schedule={schedule}
              onPause={() => pauseMutation.mutate(schedule.id)}
              onResume={() => resumeMutation.mutate(schedule.id)}
              onDelete={() => setDeleteTarget(schedule)}
              onTrigger={() => triggerMutation.mutate(schedule.id)}
              onClick={onScheduleClick ? () => onScheduleClick(schedule.id) : undefined}
              isLoading={isActionLoading}
            />
          ))}
        </AnimatePresence>
      </div>

      {/* View All Link (Compact Mode) */}
      {compact && data && data.total > 5 && (
        <Button
          variant="ghost"
          className="w-full text-purple-600 hover:text-purple-700"
          onClick={() => {
            // 可以導航到完整排程頁面或展開面板
          }}
        >
          查看全部 {data.total} 個排程
          <ChevronRight className="w-4 h-4 ml-1" />
        </Button>
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog
        open={!!deleteTarget}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-500" />
              確認刪除排程
            </AlertDialogTitle>
            <AlertDialogDescription>
              確定要刪除排程「{deleteTarget?.name}」嗎？此操作無法撤銷。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleteMutation.isPending}>
              取消
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={() => deleteTarget && deleteMutation.mutate(deleteTarget.id)}
              disabled={deleteMutation.isPending}
              className="bg-red-600 hover:bg-red-700"
            >
              {deleteMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  刪除中...
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4 mr-2" />
                  確認刪除
                </>
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

export default SchedulePanel
