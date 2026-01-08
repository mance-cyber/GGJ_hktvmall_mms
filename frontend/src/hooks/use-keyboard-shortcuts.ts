'use client'

import { useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'

// =============================================
// 類型定義
// =============================================

interface ShortcutConfig {
  key: string
  ctrl?: boolean
  shift?: boolean
  alt?: boolean
  action: () => void
  description: string
}

// =============================================
// 預設快捷鍵
// =============================================

export const defaultShortcuts: ShortcutConfig[] = [
  { key: 'g', ctrl: true, description: '前往儀表板', action: () => {} },
  { key: 'a', ctrl: true, description: '前往警報中心', action: () => {} },
  { key: 'c', ctrl: true, shift: true, description: '前往競品監測', action: () => {} },
  { key: 's', ctrl: true, description: '前往系統設定', action: () => {} },
  { key: '/', description: '聚焦搜索框', action: () => {} },
  { key: '?', shift: true, description: '顯示快捷鍵幫助', action: () => {} },
  { key: 'Escape', description: '關閉彈窗', action: () => {} },
]

// =============================================
// Hook
// =============================================

export function useKeyboardShortcuts(customShortcuts?: ShortcutConfig[]) {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // 忽略輸入框中的快捷鍵
    const target = event.target as HTMLElement
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
      // 但允許 Escape 鍵
      if (event.key !== 'Escape') return
    }

    const shortcuts = customShortcuts || []

    for (const shortcut of shortcuts) {
      const ctrlMatch = shortcut.ctrl ? (event.ctrlKey || event.metaKey) : !event.ctrlKey && !event.metaKey
      const shiftMatch = shortcut.shift ? event.shiftKey : !event.shiftKey
      const altMatch = shortcut.alt ? event.altKey : !event.altKey
      const keyMatch = event.key.toLowerCase() === shortcut.key.toLowerCase()

      if (ctrlMatch && shiftMatch && altMatch && keyMatch) {
        event.preventDefault()
        shortcut.action()
        return
      }
    }
  }, [customShortcuts])

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])
}

// =============================================
// 快捷鍵提供者 Hook
// =============================================

export function useGlobalShortcuts(onShowHelp: () => void) {
  const router = useRouter()

  const shortcuts: ShortcutConfig[] = [
    { 
      key: 'g', 
      ctrl: true, 
      description: '前往儀表板', 
      action: () => router.push('/') 
    },
    { 
      key: 'a', 
      ctrl: true, 
      description: '前往警報中心', 
      action: () => router.push('/alerts') 
    },
    { 
      key: 'c', 
      ctrl: true, 
      shift: true, 
      description: '前往競品監測', 
      action: () => router.push('/competitors') 
    },
    { 
      key: '/', 
      description: '聚焦搜索框', 
      action: () => {
        const searchInput = document.querySelector('input[type="text"][placeholder*="搜"]') as HTMLInputElement
        searchInput?.focus()
      }
    },
    { 
      key: '?',
      shift: true,
      description: '顯示快捷鍵幫助', 
      action: onShowHelp 
    },
  ]

  useKeyboardShortcuts(shortcuts)

  return shortcuts
}
