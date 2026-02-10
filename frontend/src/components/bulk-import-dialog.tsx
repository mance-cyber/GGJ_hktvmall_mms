'use client'

import { useState, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Upload,
  FileSpreadsheet,
  X,
  Check,
  AlertTriangle,
  RefreshCw,
  Download,
  CheckSquare,
  Square,
  Trash2,
  HelpCircle,
  FileText,
  Link as LinkIcon
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { cn } from '@/lib/utils'

// =============================================
// 類型定義
// =============================================

export interface ImportRow {
  url: string
  name?: string
  category?: string
  isValid: boolean
  error?: string
}

interface BulkImportDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onImport: (rows: ImportRow[]) => Promise<void>
  isLoading?: boolean
}

// =============================================
// 主組件
// =============================================

export function BulkImportDialog({
  open,
  onOpenChange,
  onImport,
  isLoading = false
}: BulkImportDialogProps) {
  const [step, setStep] = useState<'upload' | 'preview' | 'importing'>('upload')
  const [importData, setImportData] = useState<ImportRow[]>([])
  const [selectedRows, setSelectedRows] = useState<Set<number>>(new Set())
  const [dragActive, setDragActive] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // 重置狀態
  const resetState = () => {
    setStep('upload')
    setImportData([])
    setSelectedRows(new Set())
  }

  // 關閉對話框
  const handleClose = (open: boolean) => {
    if (!open) {
      resetState()
    }
    onOpenChange(open)
  }

  // 解析 CSV
  const parseCSV = (text: string): ImportRow[] => {
    const lines = text.trim().split('\n')
    const rows: ImportRow[] = []
    
    // 跳過標題行（如果有）
    const startIndex = lines[0]?.toLowerCase().includes('url') ? 1 : 0
    
    for (let i = startIndex; i < lines.length; i++) {
      const line = lines[i].trim()
      if (!line) continue
      
      // 支持逗號或 Tab 分隔
      const parts = line.includes('\t') ? line.split('\t') : line.split(',')
      const url = parts[0]?.trim().replace(/^["']|["']$/g, '')
      const name = parts[1]?.trim().replace(/^["']|["']$/g, '') || undefined
      const category = parts[2]?.trim().replace(/^["']|["']$/g, '') || undefined
      
      // 驗證 URL
      const isValid = url ? isValidUrl(url) : false
      let error: string | undefined
      if (!url) {
        error = '缺少 URL'
      } else if (!isValid) {
        if (url.includes('hktvmall.com')) {
          error = 'HKTVmall URL 需包含 /p/H{SKU}，如 /p/H0340001'
        } else {
          error = '無效的 URL 格式'
        }
      }
      
      rows.push({ url, name, category, isValid, error })
    }
    
    return rows
  }

  // 驗證 URL
  const isValidUrl = (str: string): boolean => {
    try {
      const url = new URL(str)
      if (url.protocol !== 'http:' && url.protocol !== 'https:') return false
      // HKTVmall URL 必須包含 /p/H{SKU} 格式（SKU 可帶後綴如 H9423001_S_WNF-003A）
      if (url.hostname.includes('hktvmall.com') && !/\/p\/[A-Z]\d{7,}[A-Za-z0-9_-]*/i.test(url.pathname)) {
        return false
      }
      return true
    } catch {
      return false
    }
  }

  // 處理文件上傳
  const handleFileUpload = useCallback((file: File) => {
    if (!file.name.endsWith('.csv') && !file.name.endsWith('.txt')) {
      alert('請上傳 CSV 或 TXT 文件')
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      const text = e.target?.result as string
      const rows = parseCSV(text)
      setImportData(rows)
      // 默認選中所有有效行
      setSelectedRows(new Set(rows.map((r, i) => r.isValid ? i : -1).filter(i => i >= 0)))
      setStep('preview')
    }
    reader.readAsText(file)
  }, [])

  // 處理拖放
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0])
    }
  }, [handleFileUpload])

  // 處理文件選擇
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0])
    }
  }

  // 切換選擇
  const toggleRow = (index: number) => {
    const newSet = new Set(selectedRows)
    if (newSet.has(index)) {
      newSet.delete(index)
    } else {
      newSet.add(index)
    }
    setSelectedRows(newSet)
  }

  // 全選/取消全選
  const toggleSelectAll = () => {
    const validIndices = importData.map((r, i) => r.isValid ? i : -1).filter(i => i >= 0)
    if (selectedRows.size === validIndices.length) {
      setSelectedRows(new Set())
    } else {
      setSelectedRows(new Set(validIndices))
    }
  }

  // 開始導入
  const handleImport = async () => {
    const rowsToImport = importData.filter((_, i) => selectedRows.has(i))
    setStep('importing')
    try {
      await onImport(rowsToImport)
      handleClose(false)
    } catch (error) {
      setStep('preview')
    }
  }

  // 下載模板
  const downloadTemplate = () => {
    const template = 'URL,名稱（可選）,分類（可選）\nhttps://www.hktvmall.com/hktv/zh/main/body-care/hair-care/shampoo/p/H0340001,洗髮水,護髮\nhttps://www.hktvmall.com/hktv/zh/main/health/supplements/p/H9423001_S_WNF-003A,保健品,保健品'
    const blob = new Blob([template], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = 'import_template.csv'
    link.click()
  }

  // 統計
  const validCount = importData.filter(r => r.isValid).length
  const invalidCount = importData.filter(r => !r.isValid).length

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[700px] max-h-[85vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center text-xl">
            <FileSpreadsheet className="w-5 h-5 mr-2 text-blue-500" />
            批量導入商品
          </DialogTitle>
          <DialogDescription>
            上傳 CSV 文件批量添加監測商品，支持一次導入多個商品 URL
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-auto">
          <AnimatePresence mode="wait">
            {/* ========== 上傳步驟 ========== */}
            {step === 'upload' && (
              <motion.div
                key="upload"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6 py-4"
              >
                {/* 拖放區域 */}
                <div
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                  className={cn(
                    "border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all",
                    dragActive 
                      ? "border-blue-500 bg-blue-50" 
                      : "border-slate-200 hover:border-blue-300 hover:bg-slate-50"
                  )}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv,.txt"
                    onChange={handleFileSelect}
                    className="hidden"
                  />
                  <div className={cn(
                    "w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 transition-colors",
                    dragActive ? "bg-blue-100" : "bg-slate-100"
                  )}>
                    <Upload className={cn(
                      "w-8 h-8 transition-colors",
                      dragActive ? "text-blue-500" : "text-slate-400"
                    )} />
                  </div>
                  <h3 className="text-lg font-medium text-slate-800 mb-2">
                    {dragActive ? '放開以上傳文件' : '拖放文件到此處'}
                  </h3>
                  <p className="text-sm text-slate-500 mb-4">
                    或點擊選擇文件（支持 .csv, .txt）
                  </p>
                  <Badge variant="secondary" className="text-xs">
                    每行一個 URL，可選名稱和分類
                  </Badge>
                </div>

                {/* 格式說明 */}
                <div className="bg-slate-50 rounded-xl p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-slate-700 flex items-center">
                      <HelpCircle className="w-4 h-4 mr-2" />
                      文件格式說明
                    </h4>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={downloadTemplate}
                      className="h-8"
                    >
                      <Download className="w-4 h-4 mr-1" />
                      下載模板
                    </Button>
                  </div>
                  <div className="text-sm text-slate-600 space-y-2">
                    <p>每行包含一個商品，使用逗號或 Tab 分隔：</p>
                    <code className="block bg-white p-3 rounded-lg text-xs font-mono">
                      URL,名稱（可選）,分類（可選）<br/>
                      https://www.hktvmall.com/hktv/zh/main/.../p/H0340001,商品A,飲品<br/>
                      https://www.watsons.com.hk/product2,,保健品
                    </code>
                  </div>
                </div>
              </motion.div>
            )}

            {/* ========== 預覽步驟 ========== */}
            {step === 'preview' && (
              <motion.div
                key="preview"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-4 py-4"
              >
                {/* 統計 */}
                <div className="flex items-center justify-between bg-slate-50 rounded-lg p-3">
                  <div className="flex items-center space-x-4">
                    <Badge variant="outline" className="bg-white">
                      共 {importData.length} 行
                    </Badge>
                    <Badge className="bg-green-100 text-green-700">
                      <Check className="w-3 h-3 mr-1" />
                      {validCount} 有效
                    </Badge>
                    {invalidCount > 0 && (
                      <Badge className="bg-red-100 text-red-700">
                        <AlertTriangle className="w-3 h-3 mr-1" />
                        {invalidCount} 無效
                      </Badge>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={toggleSelectAll}
                      className="h-8"
                    >
                      {selectedRows.size === validCount ? '取消全選' : '全選有效'}
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={resetState}
                      className="h-8 text-slate-500"
                    >
                      重新上傳
                    </Button>
                  </div>
                </div>

                {/* 預覽列表 */}
                <div className="border border-slate-200 rounded-lg overflow-hidden max-h-[350px] overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-slate-50 sticky top-0">
                      <tr>
                        <th className="w-10 px-3 py-2"></th>
                        <th className="px-3 py-2 text-left font-medium text-slate-600">URL</th>
                        <th className="px-3 py-2 text-left font-medium text-slate-600 w-32">名稱</th>
                        <th className="px-3 py-2 text-left font-medium text-slate-600 w-24">分類</th>
                        <th className="px-3 py-2 text-center font-medium text-slate-600 w-20">狀態</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {importData.map((row, index) => (
                        <tr 
                          key={index}
                          className={cn(
                            "hover:bg-slate-50/50",
                            !row.isValid && "bg-red-50/50",
                            selectedRows.has(index) && "bg-blue-50/50"
                          )}
                        >
                          <td className="px-3 py-2">
                            <button
                              onClick={() => row.isValid && toggleRow(index)}
                              disabled={!row.isValid}
                              className="p-1"
                            >
                              {selectedRows.has(index) ? (
                                <CheckSquare className="w-4 h-4 text-blue-500" />
                              ) : (
                                <Square className={cn(
                                  "w-4 h-4",
                                  row.isValid ? "text-slate-400" : "text-slate-200"
                                )} />
                              )}
                            </button>
                          </td>
                          <td className="px-3 py-2">
                            <div className="flex items-center max-w-[280px]">
                              <LinkIcon className="w-3.5 h-3.5 text-slate-400 mr-2 flex-shrink-0" />
                              <span className="truncate text-slate-700">{row.url || '-'}</span>
                            </div>
                          </td>
                          <td className="px-3 py-2 text-slate-600 truncate">
                            {row.name || <span className="text-slate-300">自動抓取</span>}
                          </td>
                          <td className="px-3 py-2 text-slate-600 truncate">
                            {row.category || <span className="text-slate-300">-</span>}
                          </td>
                          <td className="px-3 py-2 text-center">
                            {row.isValid ? (
                              <Badge className="bg-green-100 text-green-700 text-xs">有效</Badge>
                            ) : (
                              <Badge className="bg-red-100 text-red-700 text-xs" title={row.error}>
                                無效
                              </Badge>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* 操作按鈕 */}
                <div className="flex items-center justify-between pt-2">
                  <p className="text-sm text-slate-500">
                    已選擇 <span className="font-medium text-slate-700">{selectedRows.size}</span> 個商品準備導入
                  </p>
                  <div className="flex space-x-3">
                    <Button variant="outline" onClick={() => handleClose(false)}>
                      取消
                    </Button>
                    <Button
                      onClick={handleImport}
                      disabled={selectedRows.size === 0 || isLoading}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      {isLoading ? (
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Check className="w-4 h-4 mr-2" />
                      )}
                      導入 {selectedRows.size} 個商品
                    </Button>
                  </div>
                </div>
              </motion.div>
            )}

            {/* ========== 導入中 ========== */}
            {step === 'importing' && (
              <motion.div
                key="importing"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="py-16 text-center"
              >
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
                </div>
                <h3 className="text-lg font-medium text-slate-800 mb-2">
                  正在導入商品...
                </h3>
                <p className="text-sm text-slate-500">
                  正在處理 {selectedRows.size} 個商品，請稍候
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </DialogContent>
    </Dialog>
  )
}
