// =============================================
// ImageGenerate API 客戶端
// =============================================

import { apiClient } from './client'

export type GenerationMode = 'white_bg_topview' | 'professional_photo'
export type TaskStatus = 'pending' | 'analyzing' | 'processing' | 'completed' | 'failed'

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
 * CreateImageGenerate任務
 */
export async function createTask(data: CreateTaskRequest): Promise<ImageGenerationTask> {
  const response = await apiClient.post('/image-generation/tasks', data)
  return response as unknown as ImageGenerationTask  // ResponseIntercept器已Back data
}

/**
 * UploadInputImage（Auto分批，每批最多 10 張）
 *
 * Uploading many images in one HTTP request will time out/爆記憶體，
 * 這裡拆成多次循序Request，Backend upload_order Auto接續。
 */
const UPLOAD_BATCH_SIZE = 10

export async function uploadImages(taskId: string, files: File[]): Promise<InputImage[]> {
  const allUploaded: InputImage[] = []

  for (let i = 0; i < files.length; i += UPLOAD_BATCH_SIZE) {
    const batch = files.slice(i, i + UPLOAD_BATCH_SIZE)
    const formData = new FormData()
    batch.forEach((file) => {
      formData.append('files', file)
    })

    const response = await apiClient.post(`/image-generation/tasks/${taskId}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    const uploaded = response as unknown as InputImage[]
    allUploaded.push(...uploaded)
  }

  return allUploaded
}

/**
 * Get current user image generation limits
 */
export interface ImageGenerationLimits {
  max_images: number          // 0 = 無Upper limit
  max_outputs_per_image: number
}

export async function getLimits(): Promise<ImageGenerationLimits> {
  const response = await apiClient.get('/image-generation/limits')
  return response as unknown as ImageGenerationLimits
}

/**
 * StartImageGenerate
 */
export async function startGeneration(taskId: string): Promise<ImageGenerationTask> {
  const response = await apiClient.post(`/image-generation/tasks/${taskId}/start`)
  return response as unknown as ImageGenerationTask  // ResponseIntercept器已Back data
}

/**
 * Fetch任務State
 */
export async function getTaskStatus(taskId: string): Promise<ImageGenerationTask> {
  const response = await apiClient.get(`/image-generation/tasks/${taskId}`)
  return response as unknown as ImageGenerationTask  // ResponseIntercept器已Back data
}

/**
 * 列出任務
 */
export async function listTasks(page = 1, pageSize = 20): Promise<TaskListResponse> {
  const response = await apiClient.get('/image-generation/tasks', {
    params: { page, page_size: pageSize },
  })
  return response as unknown as TaskListResponse  // ResponseIntercept器已Back data
}

/**
 * Fetch預簽名 URL（繞過 CORS Limit）
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
 * Download images via backend proxy (bypass CORS)
 */
export async function downloadImage(fileUrl: string, fileName: string): Promise<void> {
  const { downloadFile } = await import('./client')
  const encodedUrl = encodeURIComponent(fileUrl)
  await downloadFile(`/image-generation/download?file_url=${encodedUrl}`, fileName)
}

/**
 * Delete單個任務
 */
export async function deleteTask(taskId: string): Promise<{ message: string; task_id: string }> {
  const response = await apiClient.delete(`/image-generation/tasks/${taskId}`)
  return response as unknown as { message: string; task_id: string }
}

/**
 * Batch delete任務
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
