'use client'

// =============================================
// 應用外殼 - 根據路徑條件渲染側邊欄
// =============================================

import { usePathname } from 'next/navigation'
import { Sidebar, MobileBottomNav } from './Sidebar'
import { useAuth } from './providers/auth-provider'

// 不需要顯示側邊欄的公共頁面
const publicPaths = ['/login', '/register']

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const { user, loading } = useAuth()

  // 公共頁面不顯示側邊欄
  const isPublicPage = publicPaths.some(path => pathname.startsWith(path))

  // 如果是公共頁面或未登入，只渲染 children
  if (isPublicPage || (!loading && !user)) {
    return <>{children}</>
  }

  // 已登入用戶顯示完整佈局
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 p-4 lg:p-6 lg:ml-64 pb-20 lg:pb-6">
        {children}
      </main>
      <MobileBottomNav />
    </div>
  )
}
