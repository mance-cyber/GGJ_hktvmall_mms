import type { Metadata } from "next";
import { Noto_Sans_TC } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/components/providers/query-provider";
import { ToastProvider } from "@/components/providers/toast-provider";

// ==================== 字體配置 ====================

const notoSansTC = Noto_Sans_TC({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

// ==================== Metadata ====================

export const metadata: Metadata = {
  title: {
    default: "GoGoJap - HKTVmall AI 營運系統",
    template: "%s | GoGoJap",
  },
  description: "智能營運中樞，專為 HKTVmall 營運團隊打造的 AI 驅動管理平台",
  keywords: [
    "HKTVmall",
    "價格監控",
    "競爭對手分析",
    "AI 內容生成",
    "電商營運",
    "價格比較",
  ],
  authors: [{ name: "GoGoJap Team" }],
  creator: "GoGoJap",
  openGraph: {
    type: "website",
    locale: "zh_HK",
    url: "https://gogojap.com",
    title: "GoGoJap - HKTVmall AI 營運系統",
    description: "智能營運中樞，專為 HKTVmall 營運團隊打造的 AI 驅動管理平台",
    siteName: "GoGoJap",
  },
  robots: {
    index: false, // 內部系統，不索引
    follow: false,
  },
  icons: {
    icon: "/favicon.svg",
    apple: "/favicon.svg",
  },
};

// ==================== Root Layout ====================

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-HK" suppressHydrationWarning>
      <body className={notoSansTC.className}>
        {/* React Query Provider */}
        <QueryProvider>
          {children}
          {/* Toast 通知 */}
          <ToastProvider />
        </QueryProvider>
      </body>
    </html>
  );
}
