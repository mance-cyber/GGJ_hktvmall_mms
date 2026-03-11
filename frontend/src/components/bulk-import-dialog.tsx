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
// Type definitions
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
// 主組items
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

  // ResetState
  const resetState = () => {
    setStep('upload')
    setImportData([])
    setSelectedRows(new Set())
  }

  // CloseDialog
  const handleClose = (open: boolean) => {
    if (!open) {
      resetState()
    }
    onOpenChange(open)
  }

  // Parse CSV
  const parseCSV = (text: string): ImportRow[] => {
    const lines = text.trim().split('\n')
    const rows: ImportRow[] = []
    
    // SkipTitle行（如果有）
    const startIndex = lines[0]?.toLowerCase().includes('url') ? 1 : 0
    
    for (let i = startIndex; i < lines.length; i++) {
      const line = lines[i].trim()
      if (!line) continue
      
      // Support逗號或 Tab 分隔
      const parts = line.includes('\t') ? line.split('\t') : line.split(',')
      const url = parts[0]?.trim().replace(/^["']|["']$/g, '')
      const name = parts[1]?.trim().replace(/^["']|["']$/g, '') || undefined
      const category = parts[2]?.trim().replace(/^["']|["']$/g, '') || undefined
      
      // Validate URL
      const isValid = url ? isValidUrl(url) : false
      let error: string | undefined
      if (!url) {
        error = '缺少 URL'
      } else if (!isValid) {
        if (url.includes('hktvmall.com')) {
          error = 'HKTVmall URL 需Include /p/H{SKU}，如 /p/H0340001'
        } else {
          error = 'Invalid的 URL Format'
        }
      }
      
      rows.push({ url, name, category, isValid, error })
    }
    
    return rows
  }

  // Validate URL
  const isValidUrl = (str: string): boolean => {
    try {
      const url = new URL(str)
      if (url.protocol !== 'http:' && url.protocol !== 'https:') return false
      // HKTVmall URL RequiredInclude /p/H{SKU} Format（SKU 可帶後綴如 H9423001_S_WNF-003A）
      if (url.hostname.includes('hktvmall.com') && !/\/p\/[A-Z]\d{7,}[A-Za-z0-9_-]*/i.test(url.pathname)) {
        return false
      }
      return true
    } catch {
      return false
    }
  }

  // Processing文itemsUpload
  const handleFileUpload = useCallback((file: File) => {
    if (!file.name.endsWith('.csv') && !file.name.endsWith('.txt')) {
      alert('Please upload a CSV or TXT file')
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      const text = e.target?.result as string
      const rows = parseCSV(text)
      setImportData(rows)
      // Default選中所有Valid行
      setSelectedRows(new Set(rows.map((r, i) => r.isValid ? i : -1).filter(i => i >= 0)))
      setStep('preview')
    }
    reader.readAsText(file)
  }, [])

  // Processing拖放
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

  // Processing文itemsSelect
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0])
    }
  }

  // 切換Select
  const toggleRow = (index: number) => {
    const newSet = new Set(selectedRows)
    if (newSet.has(index)) {
      newSet.delete(index)
    } else {
      newSet.add(index)
    }
    setSelectedRows(newSet)
  }

  // Select all / Deselect all
  const toggleSelectAll = () => {
    const validIndices = importData.map((r, i) => r.isValid ? i : -1).filter(i => i >= 0)
    if (selectedRows.size === validIndices.length) {
      setSelectedRows(new Set())
    } else {
      setSelectedRows(new Set(validIndices))
    }
  }

  // StartImport
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

  // Download模板
  const downloadTemplate = () => {
    const template = 'URL,Name（Optional）,分類（Optional）\nhttps://www.hktvmall.com/hktv/zh/main/body-care/hair-care/shampoo/p/H0340001,洗髮水,護髮\nhttps://www.hktvmall.com/hktv/zh/main/health/supplements/p/H9423001_S_WNF-003A,保健品,保健品'
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
            批量Importproducts
          </DialogTitle>
          <DialogDescription>
            Upload CSV 文items批量添加Monitorproducts，Support一次Import多個products URL
          </DialogDescription>
        </DialogHeader>

        <div className="flex-1 overflow-auto">
          <AnimatePresence mode="wait">
            {/* ========== Upload步驟 ========== */}
            {step === 'upload' && (
              <motion.div
                key="upload"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6 py-4"
              >
                {/* 拖放Area */}
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
                    {dragActive ? '放開以Upload文items' : '拖放文items到此處'}
                  </h3>
                  <p className="text-sm text-slate-500 mb-4">
                    或點擊Select文items（Support .csv, .txt）
                  </p>
                  <Badge variant="secondary" className="text-xs">
                    One URL per line, optional name and category
                  </Badge>
                </div>

                {/* Format說明 */}
                <div className="bg-slate-50 rounded-xl p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-slate-700 flex items-center">
                      <HelpCircle className="w-4 h-4 mr-2" />
                      文itemsFormat說明
                    </h4>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={downloadTemplate}
                      className="h-8"
                    >
                      <Download className="w-4 h-4 mr-1" />
                      Download模板
                    </Button>
                  </div>
                  <div className="text-sm text-slate-600 space-y-2">
                    <p>One product per line, separated by comma or Tab：</p>
                    <code className="block bg-white p-3 rounded-lg text-xs font-mono">
                      URL,Name（Optional）,分類（Optional）<br/>
                      https://www.hktvmall.com/hktv/zh/main/.../p/H0340001,productsA,飲品<br/>
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
                      {validCount} Valid
                    </Badge>
                    {invalidCount > 0 && (
                      <Badge className="bg-red-100 text-red-700">
                        <AlertTriangle className="w-3 h-3 mr-1" />
                        {invalidCount} Invalid
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
                      {selectedRows.size === validCount ? 'Cancel全選' : '全選Valid'}
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={resetState}
                      className="h-8 text-slate-500"
                    >
                      Re-Upload
                    </Button>
                  </div>
                </div>

                {/* 預覽List */}
                <div className="border border-slate-200 rounded-lg overflow-hidden max-h-[350px] overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-slate-50 sticky top-0">
                      <tr>
                        <th className="w-10 px-3 py-2"></th>
                        <th className="px-3 py-2 text-left font-medium text-slate-600">URL</th>
                        <th className="px-3 py-2 text-left font-medium text-slate-600 w-32">Name</th>
                        <th className="px-3 py-2 text-left font-medium text-slate-600 w-24">分類</th>
                        <th className="px-3 py-2 text-center font-medium text-slate-600 w-20">State</th>
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
                            {row.name || <span className="text-slate-300">Auto抓取</span>}
                          </td>
                          <td className="px-3 py-2 text-slate-600 truncate">
                            {row.category || <span className="text-slate-300">-</span>}
                          </td>
                          <td className="px-3 py-2 text-center">
                            {row.isValid ? (
                              <Badge className="bg-green-100 text-green-700 text-xs">Valid</Badge>
                            ) : (
                              <Badge className="bg-red-100 text-red-700 text-xs" title={row.error}>
                                Invalid
                              </Badge>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {/* Action buttons */}
                <div className="flex items-center justify-between pt-2">
                  <p className="text-sm text-slate-500">
                    Selected擇 <span className="font-medium text-slate-700">{selectedRows.size}</span> 個productsReadyImport
                  </p>
                  <div className="flex space-x-3">
                    <Button variant="outline" onClick={() => handleClose(false)}>
                      Cancel
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
                      Import {selectedRows.size} 個products
                    </Button>
                  </div>
                </div>
              </motion.div>
            )}

            {/* ========== Import中 ========== */}
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
                  currentlyImportproducts...
                </h3>
                <p className="text-sm text-slate-500">
                  currentlyProcessing {selectedRows.size} 個products，請稍候
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </DialogContent>
    </Dialog>
  )
}
