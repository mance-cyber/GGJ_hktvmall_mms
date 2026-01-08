'use client'

import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react'
import { useQueryClient } from '@tanstack/react-query'

// =============================================
// 類型定義
// =============================================

export type ScrapeTaskStatus = 'pending' | 'running' | 'success' | 'failed'

export interface ScrapeJob {
  id: string
  type: 'competitor' | 'category'
  targetId: string
  targetName: string
  status: ScrapeTaskStatus
  progress: number
  startedAt?: Date
  completedAt?: Date
  error?: string
  productCount?: number
}

interface ScrapeContextType {
  // 任務列表
  jobs: ScrapeJob[]
  activeJobsCount: number
  
  // 操作方法
  addJob: (job: Omit<ScrapeJob, 'status' | 'progress'>) => string
  updateJob: (id: string, updates: Partial<ScrapeJob>) => void
  removeJob: (id: string) => void
  clearCompleted: () => void
  
  // 狀態檢查
  isJobRunning: (targetId: string) => boolean
  getJobByTarget: (targetId: string) => ScrapeJob | undefined
  
  // 全局狀態
  isAnyScraping: boolean
  lastActivity?: Date
}

// =============================================
// Context
// =============================================

const ScrapeContext = createContext<ScrapeContextType | undefined>(undefined)

export function ScrapeProvider({ children }: { children: ReactNode }) {
  const [jobs, setJobs] = useState<ScrapeJob[]>([])
  const [lastActivity, setLastActivity] = useState<Date>()
  const queryClient = useQueryClient()

  // 計算活躍任務數
  const activeJobsCount = jobs.filter(j => j.status === 'running' || j.status === 'pending').length
  const isAnyScraping = activeJobsCount > 0

  // 添加任務
  const addJob = useCallback((job: Omit<ScrapeJob, 'status' | 'progress'>): string => {
    const newJob: ScrapeJob = {
      ...job,
      status: 'pending',
      progress: 0,
      startedAt: new Date(),
    }
    setJobs(prev => [...prev, newJob])
    setLastActivity(new Date())
    return job.id
  }, [])

  // 更新任務
  const updateJob = useCallback((id: string, updates: Partial<ScrapeJob>) => {
    setJobs(prev => prev.map(job => 
      job.id === id ? { ...job, ...updates } : job
    ))
    setLastActivity(new Date())
    
    // 如果任務完成，刷新相關數據
    if (updates.status === 'success' || updates.status === 'failed') {
      const job = jobs.find(j => j.id === id)
      if (job) {
        if (job.type === 'competitor') {
          queryClient.invalidateQueries({ queryKey: ['competitors'] })
          queryClient.invalidateQueries({ queryKey: ['competitor', job.targetId] })
          queryClient.invalidateQueries({ queryKey: ['competitor-products', job.targetId] })
        } else if (job.type === 'category') {
          queryClient.invalidateQueries({ queryKey: ['categories'] })
          queryClient.invalidateQueries({ queryKey: ['category', job.targetId] })
        }
        queryClient.invalidateQueries({ queryKey: ['alerts'] })
      }
    }
  }, [jobs, queryClient])

  // 移除任務
  const removeJob = useCallback((id: string) => {
    setJobs(prev => prev.filter(job => job.id !== id))
  }, [])

  // 清除已完成任務
  const clearCompleted = useCallback(() => {
    setJobs(prev => prev.filter(job => job.status === 'running' || job.status === 'pending'))
  }, [])

  // 檢查任務是否正在運行
  const isJobRunning = useCallback((targetId: string): boolean => {
    return jobs.some(j => j.targetId === targetId && (j.status === 'running' || j.status === 'pending'))
  }, [jobs])

  // 獲取目標的任務
  const getJobByTarget = useCallback((targetId: string): ScrapeJob | undefined => {
    return jobs.find(j => j.targetId === targetId)
  }, [jobs])

  // 自動清理過期任務（超過 5 分鐘的已完成任務）
  useEffect(() => {
    const interval = setInterval(() => {
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000)
      setJobs(prev => prev.filter(job => {
        if (job.status === 'success' || job.status === 'failed') {
          return job.completedAt ? job.completedAt > fiveMinutesAgo : true
        }
        return true
      }))
    }, 60000) // 每分鐘檢查一次

    return () => clearInterval(interval)
  }, [])

  const value: ScrapeContextType = {
    jobs,
    activeJobsCount,
    addJob,
    updateJob,
    removeJob,
    clearCompleted,
    isJobRunning,
    getJobByTarget,
    isAnyScraping,
    lastActivity,
  }

  return (
    <ScrapeContext.Provider value={value}>
      {children}
    </ScrapeContext.Provider>
  )
}

// =============================================
// Hook
// =============================================

export function useScrapeContext() {
  const context = useContext(ScrapeContext)
  if (context === undefined) {
    throw new Error('useScrapeContext must be used within a ScrapeProvider')
  }
  return context
}

// =============================================
// 輔助 Hook：模擬抓取進度
// =============================================

export function useSimulatedScrape(
  jobId: string,
  onProgress?: (progress: number) => void,
  onComplete?: () => void
) {
  const { updateJob } = useScrapeContext()

  const startSimulation = useCallback(async (durationMs: number = 5000) => {
    const steps = 20
    const stepDuration = durationMs / steps
    
    updateJob(jobId, { status: 'running', progress: 0 })
    
    for (let i = 1; i <= steps; i++) {
      await new Promise(resolve => setTimeout(resolve, stepDuration))
      const progress = (i / steps) * 100
      updateJob(jobId, { progress })
      onProgress?.(progress)
    }
    
    updateJob(jobId, { 
      status: 'success', 
      progress: 100, 
      completedAt: new Date() 
    })
    onComplete?.()
  }, [jobId, updateJob, onProgress, onComplete])

  return { startSimulation }
}
