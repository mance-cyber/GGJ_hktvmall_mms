"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { useState } from "react";

// ==================== React Query 配置 ====================

/**
 * 建立 QueryClient 實例
 * 配置全局預設設定
 */
function makeQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // 資料在 5 分鐘內視為新鮮
        staleTime: 5 * 60 * 1000,
        // 垃圾回收時間 10 分鐘（React Query v5 使用 gcTime 取代 cacheTime）
        gcTime: 10 * 60 * 1000,
        // 視窗聚焦時重新獲取數據
        refetchOnWindowFocus: true,
        // 重新連線時重新獲取數據
        refetchOnReconnect: true,
        // 失敗重試 3 次
        retry: 3,
        // 重試延遲（遞增）
        retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
      },
      mutations: {
        // 變更失敗時重試 1 次
        retry: 1,
      },
    },
  });
}

// ==================== Provider 組件 ====================

/**
 * React Query Provider
 * 提供查詢客戶端給整個應用
 */
export function QueryProvider({ children }: { children: React.ReactNode }) {
  // 使用 useState 確保每個用戶會話都有獨立的 QueryClient
  const [queryClient] = useState(() => makeQueryClient());

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* 開發環境顯示 DevTools */}
      {process.env.NODE_ENV === "development" && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </QueryClientProvider>
  );
}
