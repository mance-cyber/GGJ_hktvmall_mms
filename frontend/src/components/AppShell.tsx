'use client'

// =============================================
// 應用外殼 - Future Tech 風格佈局
// =============================================

import { usePathname } from 'next/navigation'
import { Sidebar, MobileBottomNav } from './Sidebar'
import { useAuth } from './providers/auth-provider'
import { ClickSpark } from './ui/click-spark'
import { GlobalChatWidget } from './GlobalChatWidget'

// 不需要顯示側邊欄的公共頁面
const publicPaths = ['/login', '/register']

// =============================================
// 動態背景組件
// =============================================
function AnimatedBackground() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      {/* 漸變光暈背景 */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
        <div className="absolute inset-0 opacity-40">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-300/30 rounded-full blur-[120px] animate-pulse" />
          <div className="absolute bottom-1/3 right-1/4 w-96 h-96 bg-cyan-300/30 rounded-full blur-[120px] animate-pulse delay-1000" />
          <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-pink-300/30 rounded-full blur-[100px] animate-pulse delay-500" />
        </div>
      </div>

      {/* 網格圖案 */}
      <div
        className="absolute inset-0 opacity-100"
        style={{
          backgroundImage: `
            linear-gradient(rgba(99, 102, 241, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99, 102, 241, 0.03) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px'
        }}
      />

      {/* 浮動粒子 */}
      <div className="absolute top-20 left-20 w-2 h-2 bg-purple-400 rounded-full animate-float opacity-60" />
      <div className="absolute top-40 right-40 w-1.5 h-1.5 bg-cyan-400 rounded-full animate-float-delayed opacity-60" />
      <div className="absolute bottom-32 left-1/3 w-2 h-2 bg-pink-400 rounded-full animate-float-slow opacity-60" />
      <div className="absolute top-1/3 right-1/4 w-1 h-1 bg-purple-400 rounded-full animate-float opacity-60" />
      <div className="absolute bottom-1/4 right-1/3 w-1.5 h-1.5 bg-cyan-400 rounded-full animate-float-delayed opacity-60" />
      <div className="absolute top-2/3 left-1/4 w-1 h-1 bg-pink-400 rounded-full animate-float-slow opacity-60" />
    </div>
  )
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const { user, loading } = useAuth()

  // 公共頁面不顯示側邊欄
  const isPublicPage = publicPaths.some(path => pathname.startsWith(path))

  // 如果是公共頁面或未登入，只渲染 children
  if (isPublicPage || (!loading && !user)) {
    return <>{children}</>
  }

  // 已登入用戶顯示完整佈局（Future Tech 風格）
  return (
    <ClickSpark
      sparkColor="#a855f7"
      sparkSize={12}
      sparkRadius={25}
      sparkCount={10}
      duration={500}
    >
      <div className="relative min-h-screen overflow-hidden">
        {/* 動態背景 */}
        <AnimatedBackground />

        {/* 主內容 */}
        <div className="relative z-10 flex min-h-screen">
          <Sidebar />
          <main className="flex-1 p-4 lg:p-8 lg:ml-72 pb-20 lg:pb-8">
            {children}
          </main>
          <MobileBottomNav />
        </div>

        {/* 全局浮動聊天組件 */}
        <GlobalChatWidget />
      </div>
    </ClickSpark>
  )
}
