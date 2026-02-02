// =============================================
// 工作流 API 客戶端
// =============================================

import { apiClient } from './client'

// ==================== Types ====================

export type ScheduleFrequency = 'daily' | 'weekly' | 'monthly' | 'custom'
export type ScheduleStatus = 'active' | 'paused' | 'completed' | 'failed'
export type ExecutionStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped'
export type ReportType = 'price_analysis' | 'competitor_report' | 'sales_summary' | 'inventory_alert' | 'custom'

export interface ScheduledReport {
  id: string
  name: string
  description: string | null
  report_type: ReportType
  report_config: Record<string, unknown> | null
  frequency: ScheduleFrequency
  schedule_time: string | null
  schedule_day: number | null
  cron_expression: string | null
  timezone: string
  delivery_channels: Record<string, unknown> | null
  status: ScheduleStatus
  last_run_at: string | null
  next_run_at: string | null
  run_count: number
  success_count: number
  failure_count: number
  consecutive_failures: number
  source_conversation_id: string | null
  created_by: string | null
  created_at: string
  updated_at: string
}

export interface ReportExecution {
  id: string
  schedule_id: string
  status: ExecutionStatus
  scheduled_at: string
  started_at: string | null
  completed_at: string | null
  duration_ms: number | null
  report_content: string | null
  report_data: Record<string, unknown> | null
  delivery_status: Record<string, unknown> | null
  error_message: string | null
  retry_count: number
  created_at: string
}

export interface ScheduleCreateRequest {
  name: string
  description?: string
  report_type?: ReportType
  report_config?: Record<string, unknown>
  frequency: ScheduleFrequency
  schedule_time?: string
  schedule_day?: number
  cron_expression?: string
  timezone?: string
  delivery_channels?: Record<string, unknown>
}

export interface ScheduleUpdateRequest {
  name?: string
  description?: string
  report_type?: ReportType
  report_config?: Record<string, unknown>
  frequency?: ScheduleFrequency
  schedule_time?: string
  schedule_day?: number
  cron_expression?: string
  timezone?: string
  delivery_channels?: Record<string, unknown>
  status?: ScheduleStatus
}

export interface ScheduleListResponse {
  items: ScheduledReport[]
  total: number
  limit: number
  offset: number
}

export interface ExecutionListResponse {
  items: ReportExecution[]
  total: number
}

export interface ScheduleActionResponse {
  success: boolean
  message: string
  schedule: ScheduledReport | null
}

export interface TriggerResponse {
  success: boolean
  message: string
  execution_id: string | null
  task_id: string | null
}

export interface NextRunsPreview {
  schedule_id: string
  next_runs: string[]
}

// ==================== API Functions ====================

/**
 * 列出排程
 */
export async function listSchedules(params?: {
  status?: ScheduleStatus
  conversation_id?: string
  limit?: number
  offset?: number
}): Promise<ScheduleListResponse> {
  const searchParams = new URLSearchParams()
  if (params?.status) searchParams.set('status', params.status)
  if (params?.conversation_id) searchParams.set('conversation_id', params.conversation_id)
  if (params?.limit) searchParams.set('limit', params.limit.toString())
  if (params?.offset) searchParams.set('offset', params.offset.toString())

  const query = searchParams.toString()
  const response = await apiClient.get(`/workflow/schedules${query ? `?${query}` : ''}`)
  return response as unknown as ScheduleListResponse
}

/**
 * 獲取排程詳情
 */
export async function getSchedule(scheduleId: string): Promise<ScheduledReport> {
  const response = await apiClient.get(`/workflow/schedules/${scheduleId}`)
  return response as unknown as ScheduledReport
}

/**
 * 創建排程
 */
export async function createSchedule(data: ScheduleCreateRequest): Promise<ScheduledReport> {
  const response = await apiClient.post('/workflow/schedules', data)
  return response as unknown as ScheduledReport
}

/**
 * 更新排程
 */
export async function updateSchedule(
  scheduleId: string,
  data: ScheduleUpdateRequest
): Promise<ScheduledReport> {
  const response = await apiClient.patch(`/workflow/schedules/${scheduleId}`, data)
  return response as unknown as ScheduledReport
}

/**
 * 刪除排程
 */
export async function deleteSchedule(scheduleId: string): Promise<void> {
  await apiClient.delete(`/workflow/schedules/${scheduleId}`)
}

/**
 * 暫停排程
 */
export async function pauseSchedule(scheduleId: string): Promise<ScheduleActionResponse> {
  const response = await apiClient.post(`/workflow/schedules/${scheduleId}/pause`)
  return response as unknown as ScheduleActionResponse
}

/**
 * 恢復排程
 */
export async function resumeSchedule(scheduleId: string): Promise<ScheduleActionResponse> {
  const response = await apiClient.post(`/workflow/schedules/${scheduleId}/resume`)
  return response as unknown as ScheduleActionResponse
}

/**
 * 立即觸發排程
 */
export async function triggerSchedule(scheduleId: string): Promise<TriggerResponse> {
  const response = await apiClient.post(`/workflow/schedules/${scheduleId}/trigger`)
  return response as unknown as TriggerResponse
}

/**
 * 預覽下次執行時間
 */
export async function previewNextRuns(
  scheduleId: string,
  count: number = 5
): Promise<NextRunsPreview> {
  const response = await apiClient.get(
    `/workflow/schedules/${scheduleId}/preview?count=${count}`
  )
  return response as unknown as NextRunsPreview
}

/**
 * 列出執行記錄
 */
export async function listExecutions(params?: {
  schedule_id?: string
  status?: ExecutionStatus
  limit?: number
}): Promise<ExecutionListResponse> {
  const searchParams = new URLSearchParams()
  if (params?.schedule_id) searchParams.set('schedule_id', params.schedule_id)
  if (params?.status) searchParams.set('status', params.status)
  if (params?.limit) searchParams.set('limit', params.limit.toString())

  const query = searchParams.toString()
  const response = await apiClient.get(`/workflow/executions${query ? `?${query}` : ''}`)
  return response as unknown as ExecutionListResponse
}

/**
 * 獲取執行記錄詳情
 */
export async function getExecution(executionId: string): Promise<ReportExecution> {
  const response = await apiClient.get(`/workflow/executions/${executionId}`)
  return response as unknown as ReportExecution
}

// ==================== Utility Functions ====================

/**
 * 格式化頻率顯示
 */
export function formatFrequency(frequency: ScheduleFrequency): string {
  const labels: Record<ScheduleFrequency, string> = {
    daily: '每日',
    weekly: '每週',
    monthly: '每月',
    custom: '自定義',
  }
  return labels[frequency] || frequency
}

/**
 * 格式化狀態顯示
 */
export function formatScheduleStatus(status: ScheduleStatus): string {
  const labels: Record<ScheduleStatus, string> = {
    active: '運行中',
    paused: '已暫停',
    completed: '已完成',
    failed: '失敗',
  }
  return labels[status] || status
}

/**
 * 格式化報告類型顯示
 */
export function formatReportType(reportType: ReportType): string {
  const labels: Record<ReportType, string> = {
    price_analysis: '價格分析',
    competitor_report: '競品報告',
    sales_summary: '銷售摘要',
    inventory_alert: '庫存警報',
    custom: '自定義',
  }
  return labels[reportType] || reportType
}

/**
 * 獲取狀態顏色
 */
export function getStatusColor(status: ScheduleStatus): string {
  const colors: Record<ScheduleStatus, string> = {
    active: 'text-green-600 bg-green-100',
    paused: 'text-yellow-600 bg-yellow-100',
    completed: 'text-blue-600 bg-blue-100',
    failed: 'text-red-600 bg-red-100',
  }
  return colors[status] || 'text-gray-600 bg-gray-100'
}
