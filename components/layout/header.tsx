"use client";

import { useState } from "react";
import { Bell, Search, User, LogOut, Settings, Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { cn } from "@/lib/utils";

// ==================== 通知項目類型 ====================

interface Notification {
  id: number;
  title: string;
  message: string;
  time: string;
  isRead: boolean;
}

// 模擬通知數據（實際應從 API 獲取）
const mockNotifications: Notification[] = [
  {
    id: 1,
    title: "價格預警",
    message: "iPhone 15 Pro 價格低於競爭對手 5%",
    time: "5 分鐘前",
    isRead: false,
  },
  {
    id: 2,
    title: "AI 內容完成",
    message: "已生成 10 件商品描述",
    time: "1 小時前",
    isRead: false,
  },
  {
    id: 3,
    title: "系統通知",
    message: "每日價格爬取已完成",
    time: "2 小時前",
    isRead: true,
  },
];

// ==================== 頂部欄組件 ====================

export function Header() {
  const [searchQuery, setSearchQuery] = useState("");
  const [notifications] = useState(mockNotifications);

  const unreadCount = notifications.filter((n) => !n.isRead).length;

  // 處理搜尋
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("Searching for:", searchQuery);
    // TODO: 實現全局搜尋邏輯
  };

  // 處理登出
  const handleLogout = () => {
    console.log("Logging out...");
    // TODO: 實現登出邏輯
  };

  return (
    <header className="sticky top-0 z-30 h-16 bg-white border-b border-gray-200">
      <div className="flex h-full items-center justify-between px-4 md:px-6">
        {/* 左側：手機端菜單按鈕 + 搜尋 */}
        <div className="flex items-center gap-3 flex-1">
          {/* 手機端菜單按鈕 */}
          <Sheet>
            <SheetTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="md:hidden"
                aria-label="開啟選單"
              >
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-[280px] sm:w-[320px]">
              <SheetHeader>
                <SheetTitle>GoGoJap</SheetTitle>
              </SheetHeader>
              {/* 手機端導航菜單內容 */}
              <nav className="mt-6">
                <p className="text-sm text-gray-500">導航菜單</p>
                {/* TODO: 複用導航菜單組件 */}
              </nav>
            </SheetContent>
          </Sheet>

          {/* 全局搜尋 */}
          <form onSubmit={handleSearch} className="hidden md:flex flex-1 max-w-md">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                type="search"
                placeholder="搜尋商品、競爭對手..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 w-full"
              />
            </div>
          </form>
        </div>

        {/* 右側：通知 + 用戶菜單 */}
        <div className="flex items-center gap-2">
          {/* 通知下拉 */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="relative"
                aria-label="通知"
              >
                <Bell className="h-5 w-5" />
                {unreadCount > 0 && (
                  <span className="absolute top-1 right-1 h-4 w-4 bg-error text-white text-[10px] font-semibold rounded-full flex items-center justify-center">
                    {unreadCount > 9 ? "9+" : unreadCount}
                  </span>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[320px]">
              <DropdownMenuLabel className="flex items-center justify-between">
                <span>通知</span>
                {unreadCount > 0 && (
                  <span className="text-xs font-normal text-gray-500">
                    {unreadCount} 則未讀
                  </span>
                )}
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <div className="max-h-[400px] overflow-y-auto">
                {notifications.length === 0 ? (
                  <div className="py-8 text-center text-sm text-gray-500">
                    暫無通知
                  </div>
                ) : (
                  notifications.map((notification) => (
                    <DropdownMenuItem
                      key={notification.id}
                      className={cn(
                        "flex flex-col items-start gap-1 p-3 cursor-pointer",
                        !notification.isRead && "bg-brand-primary/5"
                      )}
                    >
                      <div className="flex items-start justify-between w-full">
                        <p className="text-sm font-medium text-gray-900">
                          {notification.title}
                        </p>
                        {!notification.isRead && (
                          <div className="h-2 w-2 bg-brand-primary rounded-full flex-shrink-0 mt-1" />
                        )}
                      </div>
                      <p className="text-xs text-gray-600 line-clamp-2">
                        {notification.message}
                      </p>
                      <p className="text-xs text-gray-400">
                        {notification.time}
                      </p>
                    </DropdownMenuItem>
                  ))
                )}
              </div>
              {notifications.length > 0 && (
                <>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="text-center text-sm text-brand-primary cursor-pointer">
                    查看所有通知
                  </DropdownMenuItem>
                </>
              )}
            </DropdownMenuContent>
          </DropdownMenu>

          {/* 用戶下拉菜單 */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="rounded-full"
                aria-label="用戶菜單"
              >
                <div className="h-8 w-8 rounded-full bg-brand-primary/10 flex items-center justify-center">
                  <User className="h-4 w-4 text-brand-primary" />
                </div>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[200px]">
              <DropdownMenuLabel>
                <div className="flex flex-col gap-1">
                  <p className="text-sm font-medium">營運人員</p>
                  <p className="text-xs text-gray-500">operator@gogojap.com</p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem className="cursor-pointer">
                <User className="mr-2 h-4 w-4" />
                個人資料
              </DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer">
                <Settings className="mr-2 h-4 w-4" />
                系統設定
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="cursor-pointer text-error-600"
                onClick={handleLogout}
              >
                <LogOut className="mr-2 h-4 w-4" />
                登出
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {/* 手機端搜尋（顯示在頂部欄下方） */}
      <div className="md:hidden border-t border-gray-200 px-4 py-2">
        <form onSubmit={handleSearch}>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              type="search"
              placeholder="搜尋..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 w-full"
            />
          </div>
        </form>
      </div>
    </header>
  );
}
