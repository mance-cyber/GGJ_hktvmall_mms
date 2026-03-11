'use client'

import { useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Keyboard } from 'lucide-react'

// =============================================
// Type definitions
// =============================================

interface KeyboardShortcutsDialogProps {
  open: boolean
  onClose: () => void
}

interface ShortcutItem {
  key: string
  ctrl?: boolean
  shift?: boolean
  alt?: boolean
  description: string
}

// =============================================
// 快捷鍵分組
// =============================================

const shortcutGroups = [
  {
    title: 'Navigation',
    shortcuts: [
      { key: 'G', ctrl: true, description: '前往儀表板' },
      { key: 'A', ctrl: true, description: '前往Alert中心' },
      { key: 'C', ctrl: true, shift: true, description: '前往CompetitorMonitor' },
    ]
  },
  {
    title: 'Operation',
    shortcuts: [
      { key: '/', description: '聚焦Search box' },
      { key: '?', shift: true, description: 'Display此幫助' },
      { key: 'Esc', description: 'ClosePopup' },
    ]
  },
]

// =============================================
// 按鍵Rendering組items
// =============================================

function KeyBadge({ children }: { children: React.ReactNode }) {
  return (
    <kbd className="inline-flex items-center justify-center min-w-[24px] h-6 px-1.5 text-xs font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded shadow-sm">
      {children}
    </kbd>
  )
}

function ShortcutKeys({ shortcut }: { shortcut: ShortcutItem }) {
  return (
    <div className="flex items-center gap-1">
      {shortcut.ctrl && (
        <>
          <KeyBadge>⌘/Ctrl</KeyBadge>
          <span className="text-gray-400">+</span>
        </>
      )}
      {shortcut.shift && (
        <>
          <KeyBadge>⇧</KeyBadge>
          <span className="text-gray-400">+</span>
        </>
      )}
      {shortcut.alt && (
        <>
          <KeyBadge>Alt</KeyBadge>
          <span className="text-gray-400">+</span>
        </>
      )}
      <KeyBadge>{shortcut.key}</KeyBadge>
    </div>
  )
}

// =============================================
// 主組items
// =============================================

export function KeyboardShortcutsDialog({ open, onClose }: KeyboardShortcutsDialogProps) {
  // ESC Close
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose()
    }
  }, [onClose])

  useEffect(() => {
    if (open) {
      document.addEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = ''
    }
  }, [open, handleKeyDown])

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* 背景遮罩 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/25 backdrop-blur-sm z-50"
            onClick={onClose}
          />

          {/* Dialog */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="w-full max-w-md bg-white rounded-2xl shadow-xl overflow-hidden"
              onClick={(e) => e.stopPropagation()}
            >
              {/* TitleBar */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Keyboard className="w-5 h-5 text-blue-600" />
                  </div>
                  <h2 className="text-lg font-semibold text-gray-900">
                    Keyboard shortcuts
                  </h2>
                </div>
                <button
                  onClick={onClose}
                  className="p-1 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* 快捷鍵List */}
              <div className="px-6 py-4 space-y-6 max-h-[60vh] overflow-y-auto">
                {shortcutGroups.map((group) => (
                  <div key={group.title}>
                    <h3 className="text-sm font-medium text-gray-500 mb-3">
                      {group.title}
                    </h3>
                    <div className="space-y-2">
                      {group.shortcuts.map((shortcut, idx) => (
                        <div
                          key={idx}
                          className="flex items-center justify-between py-2 px-3 rounded-lg hover:bg-gray-50 transition-colors"
                        >
                          <span className="text-sm text-gray-700">
                            {shortcut.description}
                          </span>
                          <ShortcutKeys shortcut={shortcut} />
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* 底部提示 */}
              <div className="px-6 py-4 bg-gray-50 border-t border-gray-200">
                <p className="text-xs text-gray-500 text-center">
                  Press <KeyBadge>Esc</KeyBadge> to close this window
                </p>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  )
}
