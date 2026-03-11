'use client'

import { useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'

// =============================================
// Type definitions
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
// Default快捷鍵
// =============================================

export const defaultShortcuts: ShortcutConfig[] = [
  { key: 'g', ctrl: true, description: '前往儀表板', action: () => {} },
  { key: 'a', ctrl: true, description: '前往Alert中心', action: () => {} },
  { key: 'c', ctrl: true, shift: true, description: '前往CompetitorMonitor', action: () => {} },
  { key: 's', ctrl: true, description: '前往SystemSettings', action: () => {} },
  { key: '/', description: '聚焦Search box', action: () => {} },
  { key: '?', shift: true, description: 'Display快捷鍵幫助', action: () => {} },
  { key: 'Escape', description: 'ClosePopup', action: () => {} },
]

// =============================================
// Hook
// =============================================

export function useKeyboardShortcuts(customShortcuts?: ShortcutConfig[]) {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // IgnoreInput框中的快捷鍵
    const target = event.target as HTMLElement
    if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
      // But allow Escape key
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
// 快捷鍵Provide者 Hook
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
      description: '前往Alert中心', 
      action: () => router.push('/alerts') 
    },
    { 
      key: 'c', 
      ctrl: true, 
      shift: true, 
      description: '前往CompetitorMonitor', 
      action: () => router.push('/competitors') 
    },
    { 
      key: '/', 
      description: '聚焦Search box', 
      action: () => {
        const searchInput = document.querySelector('input[type="text"][placeholder*="搜"]') as HTMLInputElement
        searchInput?.focus()
      }
    },
    { 
      key: '?',
      shift: true,
      description: 'Display快捷鍵幫助', 
      action: onShowHelp 
    },
  ]

  useKeyboardShortcuts(shortcuts)

  return shortcuts
}
