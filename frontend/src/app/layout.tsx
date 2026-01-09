import type { Metadata, Viewport } from 'next'
import './globals.css'
import { QueryProvider } from '@/components/QueryProvider'
import { AppShell } from '@/components/AppShell'
import { Toaster } from '@/components/ui/toaster'

export const metadata: Metadata = {
  title: 'GoGoJap AI 營運系統',
  description: '競品監測與價格追踪儀表板',
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: 'cover', // 支持 iPhone 瀏海屏幕
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-HK">
      <body className="antialiased bg-slate-50">
        <QueryProvider>
          <AppShell>
            {children}
          </AppShell>
          <Toaster />
        </QueryProvider>
      </body>
    </html>
  )
}
