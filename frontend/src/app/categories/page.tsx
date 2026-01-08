'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import Link from 'next/link'
import {
  FolderOpen,
  Plus,
  RefreshCw,
  Download,
  ExternalLink,
  Play,
  AlertCircle,
  Check
} from 'lucide-react'

export default function CategoriesPage() {
  const queryClient = useQueryClient()
  const [scrapingId, setScrapingId] = useState<string | null>(null)

  const { data: categories, isLoading, error, refetch } = useQuery({
    queryKey: ['categories'],
    queryFn: () => api.getCategories(1, 100),
  })

  const scrapeMutation = useMutation({
    mutationFn: (categoryId: string) => api.triggerScrape(categoryId, 20),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] })
      setScrapingId(null)
    },
    onError: () => {
      setScrapingId(null)
    },
  })

  const handleScrape = (categoryId: string) => {
    setScrapingId(categoryId)
    scrapeMutation.mutate(categoryId)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
          <span className="text-red-700">無法載入類別列表</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 頁面標題 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">類別管理</h1>
          <p className="text-gray-500 mt-1">管理 HKTVmall 商品類別與價格追踪</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => refetch()}
            className="flex items-center px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            刷新
          </button>
        </div>
      </div>

      {/* 類別表格 */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                類別名稱
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                商品數量
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                最後更新
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                狀態
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {categories?.items.map((category) => (
              <tr key={category.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                      <FolderOpen className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <Link
                        href={`/categories/${category.id}`}
                        className="text-sm font-medium text-gray-900 hover:text-blue-600"
                      >
                        {category.name}
                      </Link>
                      {category.description && (
                        <p className="text-sm text-gray-500 truncate max-w-xs">
                          {category.description}
                        </p>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm text-gray-900">{category.total_products}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm text-gray-500">
                    {category.last_scraped_at
                      ? new Date(category.last_scraped_at).toLocaleString('zh-HK')
                      : '尚未抓取'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      category.is_active
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {category.is_active ? '活躍' : '停用'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div className="flex items-center justify-end space-x-2">
                    <button
                      onClick={() => handleScrape(category.id)}
                      disabled={scrapingId === category.id}
                      className={`p-2 rounded-lg transition-colors ${
                        scrapingId === category.id
                          ? 'bg-blue-100 text-blue-400 cursor-not-allowed'
                          : 'hover:bg-blue-50 text-blue-600'
                      }`}
                      title="開始抓取"
                    >
                      {scrapingId === category.id ? (
                        <RefreshCw className="w-4 h-4 animate-spin" />
                      ) : (
                        <Play className="w-4 h-4" />
                      )}
                    </button>
                    <a
                      href={`/api/v1/categories/${category.id}/export/excel`}
                      className="p-2 hover:bg-green-50 text-green-600 rounded-lg transition-colors"
                      title="導出 Excel"
                    >
                      <Download className="w-4 h-4" />
                    </a>
                    <Link
                      href={`/categories/${category.id}`}
                      className="p-2 hover:bg-gray-100 text-gray-600 rounded-lg transition-colors"
                      title="查看詳情"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </Link>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {(!categories?.items || categories.items.length === 0) && (
          <div className="px-6 py-12 text-center">
            <FolderOpen className="w-12 h-12 mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900">尚未創建任何類別</h3>
            <p className="text-gray-500 mt-1">通過 API 創建第一個類別開始監測</p>
          </div>
        )}
      </div>
    </div>
  )
}
