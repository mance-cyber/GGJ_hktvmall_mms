import { useState } from 'react';
import { 
  LayoutDashboard, 
  MessageSquare,
  Globe,
  Eye,
  TrendingUp,
  Package,
  FolderOpen,
  FileText,
  PieChart,
  Bell,
  Zap
} from 'lucide-react';

const menuItems = [
  { 
    category: '總覽',
    items: [
      { icon: LayoutDashboard, label: '儀表板' },
    ]
  },
  { 
    category: '市場情報',
    items: [
      { icon: MessageSquare, label: 'AI 助手' },
      { icon: Globe, label: '市場應對中心' },
      { icon: Eye, label: '競品監測' },
      { icon: TrendingUp, label: '價格趨勢' },
    ]
  },
  { 
    category: '商品管理',
    items: [
      { icon: Package, label: '商品庫' },
      { icon: FolderOpen, label: '類別管理' },
      { icon: FileText, label: 'AI 文案' },
      { icon: PieChart, label: 'AI 分析' },
    ]
  },
  { 
    category: '通知',
    items: [
      { icon: Bell, label: '警報中心' },
    ]
  },
];

export function Sidebar() {
  const [activeIndex, setActiveIndex] = useState('0-0'); // category-item format

  return (
    <div className="fixed left-0 top-0 h-screen w-72 p-6 z-20">
      {/* Glassmorphic sidebar */}
      <div className="h-full rounded-2xl bg-white/80 backdrop-blur-2xl border border-white/60 shadow-[0_8px_32px_rgba(0,0,0,0.08)] p-6 relative overflow-hidden">
        {/* Subtle holographic edge effect */}
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-blue-100/20 via-transparent to-purple-100/20 pointer-events-none"></div>
        
        {/* Logo */}
        <div className="mb-8 relative">
          <div className="flex items-center gap-3">
            <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-cyan-500 flex items-center justify-center shadow-md">
              <Zap className="w-6 h-6 text-white" fill="white" />
            </div>
            <div>
              <div className="text-gray-900 font-semibold text-lg">GOGapp</div>
              <div className="text-gray-600 text-xs flex items-center gap-1">
                <div className="w-1 h-1 bg-green-500 rounded-full animate-pulse"></div>
                企業管理系統
              </div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="space-y-5 relative z-10 max-h-[calc(100vh-280px)] scrollbar-subtle pl-2 pr-1">
          <div className="space-y-5 pb-20">
          {menuItems.map((category, categoryIndex) => {
            // Define color themes for each category
            const categoryColors = [
              { 
                gradient: 'from-blue-500/10 via-blue-400/5 to-transparent',
                border: 'border-blue-300/30',
                accent: 'text-blue-600',
                activeBg: 'bg-blue-50',
                activeBorder: 'border-blue-400/50',
                activeGlow: 'shadow-[0_0_15px_rgba(59,130,246,0.15)]',
                indicator: 'from-blue-500 to-cyan-500',
              },
              { 
                gradient: 'from-emerald-500/10 via-emerald-400/5 to-transparent',
                border: 'border-emerald-300/30',
                accent: 'text-emerald-600',
                activeBg: 'bg-emerald-50',
                activeBorder: 'border-emerald-400/50',
                activeGlow: 'shadow-[0_0_15px_rgba(16,185,129,0.15)]',
                indicator: 'from-emerald-500 to-teal-500',
              },
              { 
                gradient: 'from-purple-500/10 via-purple-400/5 to-transparent',
                border: 'border-purple-300/30',
                accent: 'text-purple-600',
                activeBg: 'bg-purple-50',
                activeBorder: 'border-purple-400/50',
                activeGlow: 'shadow-[0_0_15px_rgba(168,85,247,0.15)]',
                indicator: 'from-purple-500 to-violet-500',
              },
              { 
                gradient: 'from-orange-500/10 via-orange-400/5 to-transparent',
                border: 'border-orange-300/30',
                accent: 'text-orange-600',
                activeBg: 'bg-orange-50',
                activeBorder: 'border-orange-400/50',
                activeGlow: 'shadow-[0_0_15px_rgba(249,115,22,0.15)]',
                indicator: 'from-orange-500 to-amber-500',
              },
            ];
            const colors = categoryColors[categoryIndex % categoryColors.length];
            
            return (
              <div key={categoryIndex} className={`relative p-3 rounded-xl bg-gradient-to-br ${colors.gradient} border ${colors.border} backdrop-blur-sm`}>
                {/* Category title */}
                <div className={`text-[10px] uppercase tracking-widest mb-2.5 px-2 font-bold ${colors.accent} flex items-center gap-2`}>
                  <div className={`h-px flex-1 bg-gradient-to-r ${colors.indicator} opacity-30`}></div>
                  <span>{category.category}</span>
                  <div className={`h-px flex-1 bg-gradient-to-l ${colors.indicator} opacity-30`}></div>
                </div>
                
                <div className="space-y-1">
                  {category.items.map((item, itemIndex) => {
                    const Icon = item.icon;
                    const itemKey = `${categoryIndex}-${itemIndex}`;
                    const isActive = activeIndex === itemKey;
                    
                    return (
                      <button
                        key={itemKey}
                        onClick={() => setActiveIndex(itemKey)}
                        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group relative overflow-hidden ${
                          isActive 
                            ? `${colors.activeBg} border ${colors.activeBorder} ${colors.activeGlow}` 
                            : 'hover:bg-white/50 border border-transparent'
                        }`}
                      >
                        <Icon className={`w-4 h-4 relative z-10 transition-all duration-200 flex-shrink-0 ${
                          isActive 
                            ? colors.accent
                            : 'text-gray-500 group-hover:text-gray-700'
                        }`} />
                        
                        <span className={`relative z-10 transition-all duration-200 text-[13px] whitespace-nowrap ${
                          isActive 
                            ? `text-gray-900 font-bold` 
                            : 'text-gray-700 font-medium group-hover:text-gray-900'
                        }`}>
                          {item.label}
                        </span>

                        {isActive && (
                          <div className={`absolute right-0 top-1/2 -translate-y-1/2 w-0.5 h-6 bg-gradient-to-b ${colors.indicator} rounded-l-full`}></div>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            );
          })}
          </div>
        </nav>

        {/* Bottom section */}
        <div className="absolute bottom-6 left-6 right-6">
          <div className="p-4 rounded-xl bg-gradient-to-br from-purple-50 to-cyan-50 border border-purple-200/50 backdrop-blur-sm cursor-pointer hover:shadow-md transition-all group">
            <div className="relative z-10">
              <div className="text-xs text-gray-600 mb-1">GOGapp 資源庫</div>
              <div className="text-gray-900 text-sm font-medium">立即升級 →</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}