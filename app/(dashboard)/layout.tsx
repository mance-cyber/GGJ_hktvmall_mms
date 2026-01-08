import { Sidebar, MobileNav } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";

// ==================== Dashboard 佈局 ====================

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* 側邊欄（桌面） */}
      <Sidebar />

      {/* 主內容區 */}
      <div className="md:pl-64 transition-all duration-300">
        {/* 頂部欄 */}
        <Header />

        {/* 頁面內容 */}
        <main className="pb-20 md:pb-8">
          {children}
        </main>
      </div>

      {/* 底部導航（移動端） */}
      <MobileNav />
    </div>
  );
}
