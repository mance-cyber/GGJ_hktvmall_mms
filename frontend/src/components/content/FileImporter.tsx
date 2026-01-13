'use client'

import { useState, useCallback, useRef } from 'react'
import { api, ProductInfo } from '@/lib/api'
import {
  Upload,
  Download,
  FileSpreadsheet,
  AlertCircle,
  X,
  Check,
  Trash2,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { HoloBadge } from '@/components/ui/future-tech'

interface ParsedProduct extends ProductInfo {
  _rowIndex: number
  _errors: string[]
}

interface FileImporterProps {
  onProductsChange: (products: ProductInfo[]) => void
  className?: string
}

export function FileImporter({ onProductsChange, className }: FileImporterProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [parsedProducts, setParsedProducts] = useState<ParsedProduct[]>([])
  const [parseError, setParseError] = useState<string | null>(null)
  const [fileName, setFileName] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // 下載模板
  const handleDownloadTemplate = () => {
    window.open(api.getImportTemplateUrl(), '_blank')
  }

  // 解析 CSV 內容
  const parseCSV = (content: string): ParsedProduct[] => {
    const lines = content.trim().split('\n')
    if (lines.length < 2) {
      throw new Error('文件至少需要包含表頭和一行數據')
    }

    // 解析表頭
    const headers = lines[0].split(',').map((h) => h.trim().toLowerCase())
    const nameIndex = headers.indexOf('name')

    if (nameIndex === -1) {
      throw new Error('缺少必填字段: name')
    }

    // 解析數據行
    const products: ParsedProduct[] = []

    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim()
      if (!line) continue

      // 簡單 CSV 解析（不處理引號內的逗號）
      const values = line.split(',').map((v) => v.trim())
      const errors: string[] = []

      // 獲取字段值
      const getValue = (field: string): string => {
        const index = headers.indexOf(field)
        return index >= 0 && values[index] ? values[index] : ''
      }

      const name = getValue('name')
      if (!name) {
        errors.push('商品名稱不能為空')
      }

      // 解析 features（逗號分隔轉數組，但要處理中文逗號）
      const featuresRaw = getValue('features')
      const features = featuresRaw
        ? featuresRaw.split(/[,，]/).map((f) => f.trim()).filter(Boolean)
        : []

      products.push({
        name: name || `未命名商品 ${i}`,
        brand: getValue('brand') || undefined,
        features,
        target_audience: getValue('target_audience') || undefined,
        price: getValue('price') || undefined,
        category: getValue('category') || undefined,
        _rowIndex: i + 1,
        _errors: errors,
      })
    }

    return products
  }

  // 處理文件
  const handleFile = useCallback(
    (file: File) => {
      setParseError(null)
      setFileName(file.name)

      // 檢查文件類型
      const validTypes = [
        'text/csv',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      ]
      const isValidType =
        validTypes.includes(file.type) ||
        file.name.endsWith('.csv') ||
        file.name.endsWith('.xlsx')

      if (!isValidType) {
        setParseError('請上傳 CSV 或 Excel 文件')
        return
      }

      // 讀取文件
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const content = e.target?.result as string
          const products = parseCSV(content)

          if (products.length === 0) {
            throw new Error('未找到有效數據')
          }

          if (products.length > 100) {
            throw new Error('單次最多導入 100 個商品')
          }

          setParsedProducts(products)

          // 過濾掉有錯誤的項目，傳遞給父組件
          const validProducts = products
            .filter((p) => p._errors.length === 0)
            .map(({ _rowIndex, _errors, ...product }) => product)

          onProductsChange(validProducts)
        } catch (err) {
          setParseError(err instanceof Error ? err.message : '解析文件失敗')
          setParsedProducts([])
          onProductsChange([])
        }
      }

      reader.onerror = () => {
        setParseError('讀取文件失敗')
      }

      reader.readAsText(file)
    },
    [onProductsChange]
  )

  // 拖放處理
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setIsDragging(false)

      const file = e.dataTransfer.files[0]
      if (file) {
        handleFile(file)
      }
    },
    [handleFile]
  )

  // 文件選擇處理
  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) {
        handleFile(file)
      }
    },
    [handleFile]
  )

  // 清除導入
  const handleClear = () => {
    setParsedProducts([])
    setFileName(null)
    setParseError(null)
    onProductsChange([])
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  // 移除單個商品
  const handleRemoveProduct = (index: number) => {
    const newProducts = parsedProducts.filter((_, i) => i !== index)
    setParsedProducts(newProducts)

    const validProducts = newProducts
      .filter((p) => p._errors.length === 0)
      .map(({ _rowIndex, _errors, ...product }) => product)

    onProductsChange(validProducts)
  }

  const validCount = parsedProducts.filter((p) => p._errors.length === 0).length
  const errorCount = parsedProducts.filter((p) => p._errors.length > 0).length

  return (
    <div className={cn('space-y-4', className)}>
      {/* 模板下載 */}
      <div className="flex items-center justify-between px-3 py-2 bg-blue-50 rounded-lg">
        <div className="flex items-center gap-2 text-sm text-blue-700">
          <FileSpreadsheet className="w-4 h-4" />
          <span>請按照模板格式填寫商品資訊</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleDownloadTemplate}
          className="text-blue-600 hover:text-blue-800"
        >
          <Download className="w-4 h-4 mr-1" />
          下載模板
        </Button>
      </div>

      {/* 上傳區域 */}
      {parsedProducts.length === 0 ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={cn(
            'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
            isDragging
              ? 'border-cyan-400 bg-cyan-50'
              : 'border-slate-200 hover:border-cyan-300 hover:bg-slate-50'
          )}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv,.xlsx"
            onChange={handleFileSelect}
            className="hidden"
          />

          <Upload
            className={cn(
              'w-10 h-10 mx-auto mb-3',
              isDragging ? 'text-cyan-500' : 'text-slate-400'
            )}
          />

          <p className="text-sm font-medium text-slate-700">
            {isDragging ? '放開以上傳文件' : '拖放文件到此處，或點擊選擇文件'}
          </p>
          <p className="text-xs text-slate-500 mt-1">支持 CSV、Excel 格式，最多 100 個商品</p>

          {parseError && (
            <div className="mt-4 flex items-center justify-center gap-2 text-sm text-red-600">
              <AlertCircle className="w-4 h-4" />
              <span>{parseError}</span>
            </div>
          )}
        </div>
      ) : (
        /* 預覽列表 */
        <div className="space-y-3">
          {/* 摘要 */}
          <div className="flex items-center justify-between px-3 py-2 bg-slate-50 rounded-lg">
            <div className="flex items-center gap-3">
              <span className="text-sm text-slate-600">
                文件: <span className="font-medium">{fileName}</span>
              </span>
              <HoloBadge variant="success">
                <Check className="w-3 h-3 mr-1" /> {validCount} 個有效
              </HoloBadge>
              {errorCount > 0 && (
                <HoloBadge variant="error">
                  <AlertCircle className="w-3 h-3 mr-1" /> {errorCount} 個錯誤
                </HoloBadge>
              )}
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClear}
              className="text-slate-500 hover:text-red-500"
            >
              <Trash2 className="w-4 h-4 mr-1" />
              清除
            </Button>
          </div>

          {/* 商品列表 */}
          <div className="border border-slate-200 rounded-lg overflow-hidden max-h-[300px] overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 sticky top-0">
                <tr>
                  <th className="px-3 py-2 text-left font-medium text-slate-600">行號</th>
                  <th className="px-3 py-2 text-left font-medium text-slate-600">商品名稱</th>
                  <th className="px-3 py-2 text-left font-medium text-slate-600">品牌</th>
                  <th className="px-3 py-2 text-left font-medium text-slate-600">狀態</th>
                  <th className="px-3 py-2 text-center font-medium text-slate-600">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {parsedProducts.map((product, index) => (
                  <tr
                    key={index}
                    className={cn(
                      product._errors.length > 0 ? 'bg-red-50' : 'hover:bg-slate-50'
                    )}
                  >
                    <td className="px-3 py-2 text-slate-500">{product._rowIndex}</td>
                    <td className="px-3 py-2 font-medium text-slate-900">{product.name}</td>
                    <td className="px-3 py-2 text-slate-600">{product.brand || '-'}</td>
                    <td className="px-3 py-2">
                      {product._errors.length > 0 ? (
                        <span className="text-red-600 text-xs">{product._errors.join(', ')}</span>
                      ) : (
                        <Check className="w-4 h-4 text-green-500" />
                      )}
                    </td>
                    <td className="px-3 py-2 text-center">
                      <button
                        onClick={() => handleRemoveProduct(index)}
                        className="p-1 text-slate-400 hover:text-red-500 transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
