'use client'

import { useState, useCallback } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, Competitor, CompetitorCreate } from '@/lib/api'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Plus,
  RefreshCw,
  AlertCircle,
  Zap,
  Building2,
  History,
  ChevronRight,
  Filter,
  LayoutGrid,
  List,
  Search
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import { ScrapeTerminal, LogEntry, ScrapeStats, createLogEntry } from '@/components/scrape-terminal'
import { ScrapeTaskQueue, ScrapeTask, ScrapeTaskIndicator } from '@/components/scrape-task-queue'
import { CompetitorCard } from '@/components/competitors/competitor-card'
import { CompetitorFormDialog } from '@/components/competitors/competitor-form-dialog'

// =============================================
// 主頁面組件
// =============================================

export default function CompetitorsPage() {
  const queryClient = useQueryClient()
  
  // UI 狀態
  const [showAddForm, setShowAddForm] = useState(false)
  const [editingCompetitor, setEditingCompetitor] = useState<Competitor | null>(null)
  const [scrapingId, setScrapingId] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [filterActive, setFilterActive] = useState<boolean | undefined>(undefined)
  
  // 批量抓取狀態
  const [isTerminalOpen, setIsTerminalOpen] = useState(false)
  const [batchScraping, setBatchScraping] = useState(false)
  const [scrapeLogs, setScrapeLogs] = useState<LogEntry[]>([])
  const [scrapeProgress, setScrapeProgress] = useState(0)
  const [scrapeStats, setScrapeStats] = useState<ScrapeStats>({
    total: 0,
    success: 0,
    failed: 0,
    skipped: 0
  })
  const [scrapeTasks, setScrapeTasks] = useState<ScrapeTask[]>([])
  const [showTaskQueue, setShowTaskQueue] = useState(false)
  const [abortController, setAbortController] = useState<AbortController | null>(null)

  // ========== 數據查詢 ==========
  
  const { data: competitors, isLoading, error, refetch } = useQuery({
    queryKey: ['competitors', filterActive],
    queryFn: () => api.getCompetitors(filterActive),
  })

  // 過濾搜索結果
  const filteredCompetitors = competitors?.data.filter(comp => 
    !searchQuery || 
    comp.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    comp.platform.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // ========== Mutations ==========
  
  const createMutation = useMutation({
    mutationFn: (data: CompetitorCreate) => api.createCompetitor(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitors'] })
      setShowAddForm(false)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CompetitorCreate> }) =>
      api.updateCompetitor(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitors'] })
      setEditingCompetitor(null)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.deleteCompetitor(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitors'] })
    },
  })

  const scrapeMutation = useMutation({
    mutationFn: (id: string) => api.triggerCompetitorScrape(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitors'] })
      setScrapingId(null)
    },
    onError: () => {
      setScrapingId(null)
    },
  })

  // ========== 抓取操作 ==========
  
  const addLog = useCallback((message: string, type: LogEntry['type'] = 'info') => {
    setScrapeLogs(prev => [...prev, createLogEntry(message, type)])
  }, [])

  const handleScrape = (id: string) => {
    setScrapingId(id)
    scrapeMutation.mutate(id)
  }

  const handleScrapeAll = async () => {
    if (!competitors?.data || competitors.data.length === 0) return
    
    // 創建新的 AbortController
    const controller = new AbortController()
    setAbortController(controller)
    
    // 初始化狀態
    setIsTerminalOpen(true)
    setBatchScraping(true)
    setScrapeLogs([])
    setScrapeProgress(0)
    
    const activeCompetitors = competitors.data.filter(c => c.is_active)
    const total = activeCompetitors.length
    
    setScrapeStats({
      total,
      success: 0,
      failed: 0,
      skipped: competitors.data.length - total
    })

    // 初始化任務隊列
    const initialTasks: ScrapeTask[] = activeCompetitors.map(comp => ({
      id: comp.id,
      name: comp.name,
      type: 'competitor' as const,
      status: 'pending' as const
    }))
    setScrapeTasks(initialTasks)
    
    addLog('═══════════════════════════════════════', 'info')
    addLog('INITIALIZING BATCH SCRAPE SEQUENCE...', 'info')
    addLog(`Target count: ${total} active competitors`, 'info')
    if (competitors.data.length - total > 0) {
      addLog(`Skipping ${competitors.data.length - total} inactive competitors`, 'warning')
    }
    addLog('═══════════════════════════════════════', 'info')
    
    let completed = 0
    let successCount = 0
    let failedCount = 0

    for (const comp of activeCompetitors) {
      // 檢查是否被取消
      if (controller.signal.aborted) {
        addLog('!! BATCH SCRAPE ABORTED BY USER', 'warning')
        break
      }

      // 更新當前任務狀態
      setScrapeTasks(prev => prev.map(t => 
        t.id === comp.id ? { ...t, status: 'running' as const, progress: 0 } : t
      ))
      setScrapeStats(prev => ({ ...prev, current: comp.name }))
      
      addLog(`[${completed + 1}/${total}] Connecting to: ${comp.name}`, 'info')
      
      try {
        await api.triggerCompetitorScrape(comp.id)
        successCount++
        addLog(`>> SUCCESS: Scrape task queued for ${comp.name}`, 'success')
        
        // 更新任務狀態為成功
        setScrapeTasks(prev => prev.map(t => 
          t.id === comp.id ? { 
            ...t, 
            status: 'success' as const, 
            completedAt: new Date().toISOString(),
            productCount: comp.product_count
          } : t
        ))
      } catch (err) {
        failedCount++
        const errorMsg = err instanceof Error ? err.message : 'Unknown error'
        addLog(`!! FAILED: ${comp.name} - ${errorMsg}`, 'error')
        
        // 更新任務狀態為失敗
        setScrapeTasks(prev => prev.map(t => 
          t.id === comp.id ? { 
            ...t, 
            status: 'failed' as const,
            error: errorMsg
          } : t
        ))
      }
      
      completed++
      const progress = (completed / total) * 100
      setScrapeProgress(progress)
      setScrapeStats(prev => ({
        ...prev,
        success: successCount,
        failed: failedCount
      }))
      
      // 短暫延遲以避免 API 過載
      await new Promise(r => setTimeout(r, 500))
    }

    addLog('═══════════════════════════════════════', 'info')
    if (!controller.signal.aborted) {
      addLog(`BATCH SEQUENCE COMPLETED`, 'success')
      addLog(`Results: ${successCount} success, ${failedCount} failed`, 
        failedCount > 0 ? 'warning' : 'success')
    }
    addLog('═══════════════════════════════════════', 'info')
    
    setBatchScraping(false)
    setScrapeStats(prev => ({ ...prev, current: undefined }))
    setAbortController(null)
    queryClient.invalidateQueries({ queryKey: ['competitors'] })
  }

  const handleCancelScrape = () => {
    if (abortController) {
      abortController.abort()
      addLog('Cancellation requested...', 'warning')
    }
  }

  // ========== 渲染 ==========
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="relative">
          <div className="absolute inset-0 bg-blue-500/20 blur-xl rounded-full animate-pulse" />
          <RefreshCw className="relative w-12 h-12 animate-spin text-primary" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="glass-panel border-destructive/20 bg-destructive/5 p-6 rounded-xl flex items-center text-destructive">
        <AlertCircle className="w-5 h-5 mr-3" />
        <span className="font-medium">無法載入競爭對手列表，請稍後再試。</span>
      </div>
    )
  }

  return (
    <div className="space-y-6 animate-fade-in-up">
      {/* ========== 頁面標題 ========== */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
            競品監測
            <Badge variant="outline" className="text-primary border-primary/30 bg-primary/5">
              Live
            </Badge>
          </h1>
          <p className="text-muted-foreground mt-1 sm:mt-2 text-base sm:text-lg hidden sm:block">
            即時追蹤競爭對手動態，AI 智能分析價格趨勢
          </p>
        </div>

        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* 任務隊列指示器 */}
          <AnimatePresence>
            {scrapeTasks.filter(t => t.status === 'running' || t.status === 'pending').length > 0 && (
              <ScrapeTaskIndicator
                tasks={scrapeTasks}
                onClick={() => setShowTaskQueue(!showTaskQueue)}
              />
            )}
          </AnimatePresence>

          <Button
            variant="outline"
            onClick={handleScrapeAll}
            disabled={batchScraping}
            size="sm"
            className={cn(
              "shadow-lg shadow-green-500/20 transition-all hover:scale-105",
              batchScraping
                ? "bg-green-600 border-green-500 text-white"
                : "bg-slate-900 hover:bg-slate-800 text-white border-slate-800"
            )}
          >
            {batchScraping ? (
              <RefreshCw className="w-4 h-4 sm:mr-2 animate-spin" />
            ) : (
              <Zap className="w-4 h-4 sm:mr-2 text-green-400" />
            )}
            <span className="hidden sm:inline">全網抓取</span>
          </Button>
          <Button
            variant="outline"
            onClick={() => refetch()}
            size="sm"
            className="glass-card hover:bg-white/60"
          >
            <RefreshCw className="w-4 h-4 sm:mr-2" />
            <span className="hidden sm:inline">刷新</span>
          </Button>
          <Button
            onClick={() => setShowAddForm(true)}
            size="sm"
            className="bg-primary hover:bg-primary/90 shadow-lg shadow-blue-500/20 transition-all hover:scale-105"
          >
            <Plus className="w-4 h-4 sm:mr-2" />
            <span className="hidden sm:inline">新增</span>
          </Button>
        </div>
      </div>

      {/* ========== 工具欄 ========== */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4">
        {/* 搜索框 */}
        <div className="relative flex-1 sm:max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <Input
            type="text"
            placeholder="搜索競爭對手..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9 bg-white/50 border-slate-200"
          />
        </div>

        <div className="flex items-center justify-between sm:justify-end space-x-2">
          {/* 過濾器 */}
          <div className="flex items-center bg-slate-100 rounded-lg p-1">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setFilterActive(undefined)}
              className={cn(
                "h-7 px-2 sm:px-3 text-xs",
                filterActive === undefined && "bg-white shadow-sm"
              )}
            >
              全部
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setFilterActive(true)}
              className={cn(
                "h-7 px-2 sm:px-3 text-xs",
                filterActive === true && "bg-white shadow-sm"
              )}
            >
              監測中
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setFilterActive(false)}
              className={cn(
                "h-7 px-2 sm:px-3 text-xs",
                filterActive === false && "bg-white shadow-sm"
              )}
            >
              已暫停
            </Button>
          </div>

          {/* 視圖切換 - 桌面版才顯示 */}
          <div className="hidden sm:flex items-center bg-slate-100 rounded-lg p-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setViewMode('grid')}
              className={cn(
                "h-7 w-7",
                viewMode === 'grid' && "bg-white shadow-sm"
              )}
            >
              <LayoutGrid className="w-4 h-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setViewMode('list')}
              className={cn(
                "h-7 w-7",
                viewMode === 'list' && "bg-white shadow-sm"
              )}
            >
              <List className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* ========== 任務隊列面板（可展開） ========== */}
      <AnimatePresence>
        {showTaskQueue && scrapeTasks.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="glass-panel rounded-xl p-4 border border-slate-200/60">
              <ScrapeTaskQueue 
                tasks={scrapeTasks}
                maxVisible={6}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ========== 競爭對手卡片/列表 ========== */}
      {/* 卡片視圖 - 手機版強制顯示，桌面版根據 viewMode 決定 */}
      <div className={cn(
        "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6",
        viewMode === 'list' ? "sm:hidden" : ""
      )}>
        <AnimatePresence mode="popLayout">
          {filteredCompetitors?.map((competitor, index) => (
            <motion.div
              key={competitor.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ delay: index * 0.05 }}
              layout
            >
              <CompetitorCard
                competitor={competitor}
                onEdit={() => setEditingCompetitor(competitor)}
                onDelete={() => {
                  if (confirm(`確定要刪除「${competitor.name}」？所有相關商品數據也會被刪除。`)) {
                    deleteMutation.mutate(competitor.id)
                  }
                }}
                onScrape={() => handleScrape(competitor.id)}
                isScraping={scrapingId === competitor.id ||
                  scrapeTasks.find(t => t.id === competitor.id)?.status === 'running'}
              />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* 列表視圖 - 僅桌面版顯示 */}
      {viewMode === 'list' && (
        <div className="hidden sm:block glass-panel rounded-xl overflow-hidden border border-slate-200/60">
          <table className="w-full">
            <thead className="bg-slate-50/80">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">競爭對手</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-slate-600 uppercase">平台</th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-slate-600 uppercase">商品數</th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-slate-600 uppercase">狀態</th>
                <th className="px-4 py-3 text-center text-xs font-semibold text-slate-600 uppercase">最後更新</th>
                <th className="px-4 py-3 text-right text-xs font-semibold text-slate-600 uppercase">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredCompetitors?.map((competitor) => (
                <CompetitorListRow
                  key={competitor.id}
                  competitor={competitor}
                  onEdit={() => setEditingCompetitor(competitor)}
                  onDelete={() => {
                    if (confirm(`確定要刪除「${competitor.name}」？`)) {
                      deleteMutation.mutate(competitor.id)
                    }
                  }}
                  onScrape={() => handleScrape(competitor.id)}
                  isScraping={scrapingId === competitor.id}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* ========== 空狀態 ========== */}
      {(!filteredCompetitors || filteredCompetitors.length === 0) && (
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="glass-panel rounded-2xl p-16 text-center border-dashed border-2 border-slate-200"
        >
          <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6">
            <Building2 className="w-10 h-10 text-blue-500" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900">
            {searchQuery ? '未找到匹配的競爭對手' : '尚無競爭對手'}
          </h3>
          <p className="text-gray-500 mt-2 max-w-md mx-auto">
            {searchQuery 
              ? '請嘗試其他搜索關鍵詞'
              : '開始監測您的第一個競爭對手，AI 將自動為您收集價格情報。'
            }
          </p>
          {!searchQuery && (
            <Button
              onClick={() => setShowAddForm(true)}
              className="mt-8"
              size="lg"
            >
              <Plus className="w-5 h-5 mr-2" />
              立即新增
            </Button>
          )}
        </motion.div>
      )}

      {/* ========== 對話框 ========== */}
      <CompetitorFormDialog
        open={showAddForm}
        onOpenChange={setShowAddForm}
        onSubmit={(data) => createMutation.mutate(data)}
        isLoading={createMutation.isPending}
        title="新增競爭對手"
      />

      <CompetitorFormDialog
        open={!!editingCompetitor}
        onOpenChange={(open) => !open && setEditingCompetitor(null)}
        initialData={editingCompetitor || undefined}
        onSubmit={(data) => editingCompetitor && updateMutation.mutate({ id: editingCompetitor.id, data })}
        isLoading={updateMutation.isPending}
        title="編輯競爭對手"
      />

      {/* ========== 抓取終端 ========== */}
      <ScrapeTerminal 
        isOpen={isTerminalOpen}
        onClose={() => setIsTerminalOpen(false)}
        logs={scrapeLogs}
        isScraping={batchScraping}
        progress={scrapeProgress}
        stats={scrapeStats}
        onCancel={handleCancelScrape}
        title="BATCH_CRAWLER"
      />
    </div>
  )
}

// =============================================
// 列表視圖行組件
// =============================================

function CompetitorListRow({
  competitor,
  onEdit,
  onDelete,
  onScrape,
  isScraping
}: {
  competitor: Competitor
  onEdit: () => void
  onDelete: () => void
  onScrape: () => void
  isScraping: boolean
}) {
  return (
    <tr className={cn(
      "hover:bg-slate-50/50 transition-colors",
      isScraping && "bg-blue-50/30"
    )}>
      <td className="px-4 py-3">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
            <Building2 className="w-5 h-5 text-slate-400" />
          </div>
          <div>
            <p className="font-medium text-slate-900">{competitor.name}</p>
            {competitor.notes && (
              <p className="text-xs text-slate-500 truncate max-w-[200px]">{competitor.notes}</p>
            )}
          </div>
        </div>
      </td>
      <td className="px-4 py-3 text-sm text-slate-600">{competitor.platform}</td>
      <td className="px-4 py-3 text-center">
        <Badge variant="secondary">{competitor.product_count}</Badge>
      </td>
      <td className="px-4 py-3 text-center">
        <Badge variant={competitor.is_active ? "default" : "secondary"}
          className={competitor.is_active ? "bg-green-100 text-green-700" : ""}
        >
          {competitor.is_active ? '監測中' : '已暫停'}
        </Badge>
      </td>
      <td className="px-4 py-3 text-center text-sm text-slate-500">
        {competitor.last_scraped_at 
          ? new Date(competitor.last_scraped_at).toLocaleDateString('zh-HK')
          : '-'
        }
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center justify-end space-x-1">
          <Button
            size="sm"
            variant="ghost"
            onClick={onScrape}
            disabled={isScraping}
            className="h-8 px-2"
          >
            {isScraping ? (
              <RefreshCw className="w-4 h-4 animate-spin" />
            ) : (
              <Zap className="w-4 h-4" />
            )}
          </Button>
          <Button size="sm" variant="ghost" onClick={onEdit} className="h-8 px-2">
            編輯
          </Button>
          <Button 
            size="sm" 
            variant="ghost" 
            onClick={onDelete}
            className="h-8 px-2 text-red-600 hover:text-red-700 hover:bg-red-50"
          >
            刪除
          </Button>
          <a href={`/competitors/${competitor.id}`}>
            <Button size="sm" variant="ghost" className="h-8 px-2">
              <ChevronRight className="w-4 h-4" />
            </Button>
          </a>
        </div>
      </td>
    </tr>
  )
}
