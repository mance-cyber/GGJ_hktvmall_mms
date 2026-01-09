'use client'

// =============================================
// 對話列表組件 - 支持編輯模式和批量刪除
// =============================================

import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Plus,
  MessageSquare,
  Clock,
  Trash2,
  Check,
  X,
  Edit3,
  CheckSquare,
  Square,
  Loader2,
  AlertTriangle,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { api } from '@/lib/api'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

// =============================================
// Types
// =============================================

interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
}

interface ConversationListProps {
  conversations: Conversation[]
  currentId: string | null
  onSelect: (id: string) => void
  onNew: () => void
  formatDate: (date: string) => string
}

// =============================================
// 相對時間格式化
// =============================================

function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return '剛剛'
  if (diffMins < 60) return `${diffMins} 分鐘前`
  if (diffHours < 24) return `${diffHours} 小時前`
  if (diffDays < 7) return `${diffDays} 天前`

  return date.toLocaleDateString('zh-HK', {
    month: 'short',
    day: 'numeric',
  })
}

// =============================================
// Main Component
// =============================================

export function ConversationList({
  conversations,
  currentId,
  onSelect,
  onNew,
  formatDate
}: ConversationListProps) {
  const [isEditMode, setIsEditMode] = useState(false)
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  const queryClient = useQueryClient()

  // 批量刪除 mutation
  const deleteMutation = useMutation({
    mutationFn: (ids: string[]) => api.deleteAgentConversations(ids),
    onSuccess: (data) => {
      // 刷新對話列表
      queryClient.invalidateQueries({ queryKey: ['agent-history'] })
      // 重置狀態
      setSelectedIds(new Set())
      setIsEditMode(false)
      setShowDeleteDialog(false)
    },
  })

  // 切換選擇
  const toggleSelect = (id: string) => {
    const newSelected = new Set(selectedIds)
    if (newSelected.has(id)) {
      newSelected.delete(id)
    } else {
      newSelected.add(id)
    }
    setSelectedIds(newSelected)
  }

  // 全選/取消全選
  const toggleSelectAll = () => {
    if (selectedIds.size === conversations.length) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(conversations.map(c => c.id)))
    }
  }

  // 退出編輯模式
  const exitEditMode = () => {
    setIsEditMode(false)
    setSelectedIds(new Set())
  }

  // 確認刪除
  const handleDeleteConfirm = () => {
    if (selectedIds.size > 0) {
      deleteMutation.mutate(Array.from(selectedIds))
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-3 border-b bg-white">
        {isEditMode ? (
          // 編輯模式 Header
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleSelectAll}
                className="text-slate-600"
              >
                {selectedIds.size === conversations.length ? (
                  <CheckSquare className="w-4 h-4 mr-1" />
                ) : (
                  <Square className="w-4 h-4 mr-1" />
                )}
                {selectedIds.size === conversations.length ? '取消全選' : '全選'}
              </Button>
              <span className="text-sm text-slate-500">
                已選 {selectedIds.size} 個
              </span>
            </div>
            <div className="flex items-center gap-1">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDeleteDialog(true)}
                disabled={selectedIds.size === 0}
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                <Trash2 className="w-4 h-4 mr-1" />
                刪除
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={exitEditMode}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>
        ) : (
          // 正常模式 Header
          <div className="flex items-center gap-2">
            <Button
              onClick={onNew}
              className="flex-1 gap-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-sm"
            >
              <Plus className="w-4 h-4" />
              新對話
            </Button>
            {conversations.length > 0 && (
              <Button
                variant="outline"
                size="icon"
                onClick={() => setIsEditMode(true)}
                className="flex-shrink-0"
                title="編輯"
              >
                <Edit3 className="w-4 h-4" />
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {conversations.length === 0 ? (
          <div className="text-center text-slate-400 py-8 text-sm">
            <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-30" />
            暫無歷史對話
          </div>
        ) : (
          <AnimatePresence>
            {conversations.map((conv) => (
              <motion.div
                key={conv.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                transition={{ duration: 0.15 }}
              >
                <button
                  onClick={() => isEditMode ? toggleSelect(conv.id) : onSelect(conv.id)}
                  className={cn(
                    "w-full text-left px-3 py-2.5 rounded-lg transition-all text-sm group",
                    "hover:bg-slate-100",
                    !isEditMode && currentId === conv.id
                      ? "bg-purple-50 border border-purple-200 text-purple-700"
                      : "text-slate-600",
                    isEditMode && selectedIds.has(conv.id)
                      ? "bg-red-50 border border-red-200"
                      : ""
                  )}
                >
                  <div className="flex items-start gap-2">
                    {/* Checkbox (Edit Mode) */}
                    {isEditMode && (
                      <div className="flex-shrink-0 mt-0.5">
                        {selectedIds.has(conv.id) ? (
                          <CheckSquare className="w-4 h-4 text-red-500" />
                        ) : (
                          <Square className="w-4 h-4 text-slate-400" />
                        )}
                      </div>
                    )}

                    {/* Icon (Normal Mode) */}
                    {!isEditMode && (
                      <MessageSquare className="w-4 h-4 mt-0.5 flex-shrink-0 opacity-60" />
                    )}

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="font-medium truncate">
                        {conv.title || '新對話'}
                      </div>
                      <div className="flex items-center gap-1 text-xs text-slate-400 mt-0.5">
                        <Clock className="w-3 h-3" />
                        {formatRelativeTime(conv.created_at)}
                      </div>
                    </div>
                  </div>
                </button>
              </motion.div>
            ))}
          </AnimatePresence>
        )}
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              確認刪除
            </AlertDialogTitle>
            <AlertDialogDescription>
              確定要刪除選中的 {selectedIds.size} 個對話嗎？此操作無法撤銷。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleteMutation.isPending}>
              取消
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={deleteMutation.isPending}
              className="bg-red-600 hover:bg-red-700"
            >
              {deleteMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  刪除中...
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4 mr-2" />
                  確認刪除
                </>
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}

export default ConversationList
