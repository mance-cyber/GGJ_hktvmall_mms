"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Users,
  AlertTriangle,
  Package,
  Sparkles,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  ShoppingCart,
  Database,
  Wand2,
  RefreshCw,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

// ==================== 導航項目配置 ====================

interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
}

interface NavGroup {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  items: NavItem[];
}

// 分組導航結構
const navigationGroups: NavGroup[] = [
  {
    title: "HKTVmall 商品",
    icon: ShoppingCart,
    items: [
      {
        title: "商品管理",
        href: "/products",
        icon: Package,
      },
      // 未來可擴展：訂單、庫存等
    ],
  },
  {
    title: "數據抓取分析",
    icon: Database,
    items: [
      {
        title: "總覽儀表板",
        href: "/dashboard",
        icon: Home,
      },
      {
        title: "競爭對手",
        href: "/competitors",
        icon: Users,
      },
      {
        title: "抓取管理",
        href: "/scrape",
        icon: RefreshCw,
      },
      {
        title: "價格警報",
        href: "/alerts",
        icon: AlertTriangle,
      },
      {
        title: "數據分析",
        href: "/analytics",
        icon: BarChart3,
      },
    ],
  },
  {
    title: "內容生成",
    icon: Wand2,
    items: [
      {
        title: "AI 生成",
        href: "/content",
        icon: Sparkles,
      },
      // 未來可擴展：歷史記錄、模板等
    ],
  },
];

// 扁平化用於移動端
const mobileNavItems: NavItem[] = [
  { title: "儀表板", href: "/dashboard", icon: Home },
  { title: "商品", href: "/products", icon: Package },
  { title: "競爭對手", href: "/competitors", icon: Users },
  { title: "AI 內容", href: "/content", icon: Sparkles },
  { title: "警報", href: "/alerts", icon: AlertTriangle },
];

// ==================== 側邊欄組件 ====================

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const [expandedGroups, setExpandedGroups] = useState<string[]>(
    navigationGroups.map((g) => g.title) // 預設全部展開
  );
  const pathname = usePathname();

  const toggleGroup = (title: string) => {
    setExpandedGroups((prev) =>
      prev.includes(title)
        ? prev.filter((t) => t !== title)
        : [...prev, title]
    );
  };

  const isGroupActive = (group: NavGroup) => {
    return group.items.some(
      (item) => pathname === item.href || pathname.startsWith(item.href + "/")
    );
  };

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 z-40 h-screen bg-white border-r border-gray-200",
        "transition-all duration-300 ease-in-out",
        "hidden md:flex md:flex-col",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo 區域 */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-gray-200 flex-shrink-0">
        {!collapsed && (
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="h-8 w-8 bg-brand-primary rounded-md flex items-center justify-center">
              <span className="text-white font-bold text-sm">GJ</span>
            </div>
            <span className="font-bold text-lg text-gray-900">GoGoJap</span>
          </Link>
        )}

        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
          className={cn(
            "h-8 w-8 hover:bg-gray-100",
            collapsed && "mx-auto"
          )}
          aria-label={collapsed ? "展開側邊欄" : "收合側邊欄"}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* 導航菜單 */}
      <nav className="flex-1 overflow-y-auto py-4">
        {navigationGroups.map((group) => {
          const GroupIcon = group.icon;
          const isExpanded = expandedGroups.includes(group.title);
          const groupActive = isGroupActive(group);

          return (
            <div key={group.title} className="mb-2">
              {/* 分組標題 */}
              {collapsed ? (
                // 收合時只顯示圖標分隔線
                <div className="px-2 py-2">
                  <div
                    className={cn(
                      "flex items-center justify-center p-2 rounded-md",
                      groupActive ? "bg-brand-primary/10" : "bg-gray-50"
                    )}
                    title={group.title}
                  >
                    <GroupIcon
                      className={cn(
                        "h-5 w-5",
                        groupActive ? "text-brand-primary" : "text-gray-400"
                      )}
                    />
                  </div>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={() => toggleGroup(group.title)}
                  className={cn(
                    "w-full flex items-center gap-2 px-4 py-2 text-xs font-semibold uppercase tracking-wider",
                    "transition-colors hover:bg-gray-50",
                    groupActive ? "text-brand-primary" : "text-gray-500"
                  )}
                >
                  <GroupIcon className="h-4 w-4" />
                  <span className="flex-1 text-left">{group.title}</span>
                  <ChevronDown
                    className={cn(
                      "h-4 w-4 transition-transform",
                      isExpanded ? "rotate-0" : "-rotate-90"
                    )}
                  />
                </button>
              )}

              {/* 分組項目 */}
              {(collapsed || isExpanded) && (
                <ul className="space-y-0.5 px-2 mt-1">
                  {group.items.map((item) => {
                    const Icon = item.icon;
                    const isActive =
                      pathname === item.href ||
                      pathname.startsWith(item.href + "/");

                    return (
                      <li key={item.href}>
                        <Link
                          href={item.href}
                          className={cn(
                            "flex items-center gap-3 px-3 py-2 rounded-md",
                            "text-sm font-medium transition-colors duration-fast",
                            "hover:bg-gray-100",
                            isActive
                              ? "bg-brand-primary/10 text-brand-primary"
                              : "text-gray-700 hover:text-gray-900",
                            collapsed && "justify-center px-2"
                          )}
                          title={collapsed ? item.title : undefined}
                        >
                          <Icon
                            className={cn(
                              "h-5 w-5 flex-shrink-0",
                              isActive ? "text-brand-primary" : "text-gray-500"
                            )}
                          />
                          {!collapsed && (
                            <>
                              <span className="flex-1">{item.title}</span>
                              {item.badge && item.badge > 0 && (
                                <span className="badge-count">{item.badge}</span>
                              )}
                            </>
                          )}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          );
        })}

        {/* 分隔線 */}
        <div className="divider mx-2 my-4" />

        {/* 設定連結 */}
        <ul className="space-y-1 px-2">
          <li>
            <Link
              href="/settings"
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md",
                "text-sm font-medium transition-colors duration-fast",
                "text-gray-700 hover:bg-gray-100 hover:text-gray-900",
                collapsed && "justify-center px-2"
              )}
              title={collapsed ? "設定" : undefined}
            >
              <Settings className="h-5 w-5 flex-shrink-0 text-gray-500" />
              {!collapsed && <span>設定</span>}
            </Link>
          </li>
        </ul>
      </nav>

      {/* 底部資訊（完整模式） */}
      {!collapsed && (
        <div className="border-t border-gray-200 p-4 flex-shrink-0">
          <div className="text-xs text-gray-500">
            <p>版本 1.0.0</p>
            <p className="mt-1">© 2026 GoGoJap</p>
          </div>
        </div>
      )}
    </aside>
  );
}

// ==================== 移動端導航欄 ====================

export function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 md:hidden">
      <ul className="flex justify-around items-center h-16">
        {mobileNavItems.map((item) => {
          const Icon = item.icon;
          const isActive =
            pathname === item.href || pathname.startsWith(item.href + "/");

          return (
            <li key={item.href} className="flex-1">
              <Link
                href={item.href}
                className={cn(
                  "flex flex-col items-center justify-center gap-1 py-2",
                  "text-xs font-medium transition-colors duration-fast",
                  isActive
                    ? "text-brand-primary"
                    : "text-gray-600 hover:text-gray-900"
                )}
              >
                <div className="relative">
                  <Icon className="h-5 w-5" />
                  {item.badge && item.badge > 0 && (
                    <span className="absolute -top-1 -right-1 badge-count text-[10px] min-w-4 h-4 leading-4 px-1">
                      {item.badge > 99 ? "99+" : item.badge}
                    </span>
                  )}
                </div>
                <span className="truncate max-w-full px-1">{item.title}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
