'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'
import { GoogleOAuthProvider } from "@react-oauth/google"
import { ScrapeProvider } from '@/contexts/scrape-context'
import { AuthProvider } from '@/components/providers/auth-provider'
import { GlobalScrapeIndicator } from '@/components/global-scrape-indicator'
import { KeyboardShortcutsDialog } from '@/components/keyboard-shortcuts-dialog'
import { useGlobalShortcuts } from '@/hooks/use-keyboard-shortcuts'

// =============================================
// 全局快捷鍵啟用器（需要在 Provider 內部使用）
// =============================================

function GlobalShortcutsProvider({ children }: { children: React.ReactNode }) {
  const [showShortcutsHelp, setShowShortcutsHelp] = useState(false)
  
  // 啟用全局快捷鍵
  useGlobalShortcuts(() => setShowShortcutsHelp(true))

  return (
    <>
      {children}
      <KeyboardShortcutsDialog 
        open={showShortcutsHelp} 
        onClose={() => setShowShortcutsHelp(false)} 
      />
    </>
  )
}

// =============================================
// 主 Provider
// =============================================

export function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            refetchOnWindowFocus: false,
          },
        },
      })
  )

  // Use environment variable or fallback to mock for development
  const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "mock-client-id-for-dev"

  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <AuthProvider>
        <QueryClientProvider client={queryClient}>
          <ScrapeProvider>
            <GlobalShortcutsProvider>
              {children}
              <GlobalScrapeIndicator />
            </GlobalShortcutsProvider>
          </ScrapeProvider>
        </QueryClientProvider>
      </AuthProvider>
    </GoogleOAuthProvider>
  )
}
