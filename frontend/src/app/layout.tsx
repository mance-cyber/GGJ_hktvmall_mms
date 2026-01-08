import type { Metadata, Viewport } from 'next'
import './globals.css'
import { Sidebar, MobileBottomNav } from '@/components/Sidebar'
import { QueryProvider } from '@/components/QueryProvider'

export const metadata: Metadata = {
  title: 'GoGoJap AI 營運系統',
  description: '競品監測與價格追踪儀表板',
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
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
          <div className="flex min-h-screen">
            <Sidebar />
            <main className="flex-1 p-4 lg:p-6 lg:ml-64 pb-20 lg:pb-6">
              {children}
            </main>
            <MobileBottomNav />
          </div>
        </QueryProvider>
      </body>
    </html>
  )
}
