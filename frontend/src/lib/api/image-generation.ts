// =============================================
// 圖片生成 API 客戶端
// =============================================

import { apiClient } from './client'

export type GenerationMode = 'white_bg_topview' | 'professional_photo'
export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed'

export interface ImageGenerationTask {
  id: string
  mode: GenerationMode
  style_description?: string
  outputs_per_image: number
  status: TaskStatus
  progress: number
  error_message?: string
  created_at: string
  updated_at: string
  completed_at?: string
  input_images: InputImage[]
  output_images: OutputImage[]
}

export interface InputImage {
  id: string
  file_name: string
  file_path: string
  file_size: number
  upload_order: number
  analysis_result?: any
  created_at: string
}

export interface OutputImage {
  id: string
  file_name: string
  file_path: string
  file_size?: number
  prompt_used?: string
  created_at: string
}

export interface CreateTaskRequest {
  mode: GenerationMode
  style_description?: string
  outputs_per_image?: number
}

export interface TaskListResponse {
  tasks: ImageGenerationTask[]
  total: number
  page: number
  page_size: number
}

/**
 * 創建圖片生成任務
 */
export async function createTask(data: CreateTaskRequest): Promise<ImageGenerationTask> {
  const response = await apiClient.post('/image-generation/tasks', data)
  return response as unknown as ImageGenerationTask  // 響應攔截器已返回 data
}

/**
 * 上傳輸入圖片
 */
export async function uploadImages(taskId: string, files: File[]): Promise<InputImage[]> {
  const formData = new FormData()
  files.forEach((file) => {
    formData.append('files', file)
  })

  const response = await apiClient.post(`/image-generation/tasks/${taskId}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })

  return response as unknown as InputImage[]  // 響應攔截器已返回 data
}

/**
 * 開始圖片生成
 */
export async function startGeneration(taskId: string): Promise<ImageGenerationTask> {
  const response = await apiClient.post(`/image-generation/tasks/${taskId}/start`)
  return response as unknown as ImageGenerationTask  // 響應攔截器已返回 data
}

/**
 * 獲取任務狀態
 */
export async function getTaskStatus(taskId: string): Promise<ImageGenerationTask> {
  const response = await apiClient.get(`/image-generation/tasks/${taskId}`)
  return response as unknown as ImageGenerationTask  // 響應攔截器已返回 data
}

/**
 * 列出任務
 */
export async function listTasks(page = 1, pageSize = 20): Promise<TaskListResponse> {
  const response = await apiClient.get('/image-generation/tasks', {
    params: { page, page_size: pageSize },
  })
  return response as unknown as TaskListResponse  // 響應攔截器已返回 data
}

/**
 * 獲取預簽名 URL（繞過 CORS 限制）
 */
export interface PresignedUrlResponse {
  presigned_url: string
  expires_in: number
  original_url: string
}

export async function getPresignedUrl(fileUrl: string, expiresIn = 3600): Promise<PresignedUrlResponse> {
  const response = await apiClient.get('/image-generation/presigned-url', {
    params: { file_url: fileUrl, expires_in: expiresIn },
  })
  return response as unknown as PresignedUrlResponse
}

/**
 * 通過後端代理下載圖片（繞過 CORS）
 */
export async function downloadImage(fileUrl: string, fileName: string): Promise<void> {
  const { downloadFile } = await import('./client')
  const encodedUrl = encodeURIComponent(fileUrl)
  await downloadFile(`/image-generation/download?file_url=${encodedUrl}`, fileName)
}

/**
 * 刪除單個任務
 */
export async function deleteTask(taskId: string): Promise<{ message: string; task_id: string }> {
  const response = await apiClient.delete(`/image-generation/tasks/${taskId}`)
  return response as unknown as { message: string; task_id: string }
}

/**
 * 批量刪除任務
 */
export async function deleteTasksBatch(taskIds: string[]): Promise<{
  message: string
  deleted_count: number
  requested_count: number
}> {
  const response = await apiClient.delete('/image-generation/tasks/batch', {
    data: taskIds
  })
  return response as unknown as {
    message: string
    deleted_count: number
    requested_count: number
  }
}
