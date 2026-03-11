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

  // Download模板
  const handleDownloadTemplate = () => {
    window.open(api.getImportTemplateUrl(), '_blank')
  }

  // Parse CSV Content
  const parseCSV = (content: string): ParsedProduct[] => {
    const lines = content.trim().split('\n')
    if (lines.length < 2) {
      throw new Error('File must contain at least a header and one data row')
    }

    // Parse表頭
    const headers = lines[0].split(',').map((h) => h.trim().toLowerCase())
    const nameIndex = headers.indexOf('name')

    if (nameIndex === -1) {
      throw new Error('缺少必填字段: name')
    }

    // ParseData行
    const products: ParsedProduct[] = []

    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim()
      if (!line) continue

      // Simple CSV parsing (does not handle commas in quotes)
      const values = line.split(',').map((v) => v.trim())
      const errors: string[] = []

      // Fetch字段值
      const getValue = (field: string): string => {
        const index = headers.indexOf(field)
        return index >= 0 && values[index] ? values[index] : ''
      }

      const name = getValue('name')
      if (!name) {
        errors.push('productsName不能為空')
      }

      // Parse features (comma-separated to array, handle Chinese commas)
      const featuresRaw = getValue('features')
      const features = featuresRaw
        ? featuresRaw.split(/[,，]/).map((f) => f.trim()).filter(Boolean)
        : []

      products.push({
        name: name || `未命名products ${i}`,
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

  // Processing文items
  const handleFile = useCallback(
    (file: File) => {
      setParseError(null)
      setFileName(file.name)

      // Check文itemsType
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
        setParseError('Please upload a CSV or Excel file')
        return
      }

      // 讀取文items
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const content = e.target?.result as string
          const products = parseCSV(content)

          if (products.length === 0) {
            throw new Error('未找到ValidData')
          }

          if (products.length > 100) {
            throw new Error('單次最多Import 100 個products')
          }

          setParsedProducts(products)

          // Filter掉有Error的項目，傳遞給父組items
          const validProducts = products
            .filter((p) => p._errors.length === 0)
            .map(({ _rowIndex, _errors, ...product }) => product)

          onProductsChange(validProducts)
        } catch (err) {
          setParseError(err instanceof Error ? err.message : 'Parse文itemsFailed')
          setParsedProducts([])
          onProductsChange([])
        }
      }

      reader.onerror = () => {
        setParseError('讀取文itemsFailed')
      }

      reader.readAsText(file)
    },
    [onProductsChange]
  )

  // 拖放Processing
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

  // 文itemsSelectProcessing
  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) {
        handleFile(file)
      }
    },
    [handleFile]
  )

  // ClearImport
  const handleClear = () => {
    setParsedProducts([])
    setFileName(null)
    setParseError(null)
    onProductsChange([])
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  // 移除單個products
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
      {/* 模板Download */}
      <div className="flex items-center justify-between px-3 py-2 bg-blue-50 rounded-lg">
        <div className="flex items-center gap-2 text-sm text-blue-700">
          <FileSpreadsheet className="w-4 h-4" />
          <span>Please fill in product info following the template format</span>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleDownloadTemplate}
          className="text-blue-600 hover:text-blue-800"
        >
          <Download className="w-4 h-4 mr-1" />
          Download模板
        </Button>
      </div>

      {/* UploadArea */}
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
            {isDragging ? '放開以Upload文items' : '拖放文items到此處，或點擊Select文items'}
          </p>
          <p className="text-xs text-slate-500 mt-1">Support CSV、Excel Format，最多 100 個products</p>

          {parseError && (
            <div className="mt-4 flex items-center justify-center gap-2 text-sm text-red-600">
              <AlertCircle className="w-4 h-4" />
              <span>{parseError}</span>
            </div>
          )}
        </div>
      ) : (
        /* 預覽List */
        <div className="space-y-3">
          {/* 摘要 */}
          <div className="flex items-center justify-between px-3 py-2 bg-slate-50 rounded-lg">
            <div className="flex items-center gap-3">
              <span className="text-sm text-slate-600">
                文items: <span className="font-medium">{fileName}</span>
              </span>
              <HoloBadge variant="success">
                <Check className="w-3 h-3 mr-1" /> {validCount} 個Valid
              </HoloBadge>
              {errorCount > 0 && (
                <HoloBadge variant="error">
                  <AlertCircle className="w-3 h-3 mr-1" /> {errorCount} 個Error
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
              Clear
            </Button>
          </div>

          {/* Product list */}
          <div className="border border-slate-200 rounded-lg overflow-hidden max-h-[300px] overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 sticky top-0">
                <tr>
                  <th className="px-3 py-2 text-left font-medium text-slate-600">行號</th>
                  <th className="px-3 py-2 text-left font-medium text-slate-600">productsName</th>
                  <th className="px-3 py-2 text-left font-medium text-slate-600">品牌</th>
                  <th className="px-3 py-2 text-left font-medium text-slate-600">State</th>
                  <th className="px-3 py-2 text-center font-medium text-slate-600">Operation</th>
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
