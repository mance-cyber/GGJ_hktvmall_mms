import { Plus, TrendingUp, Sparkles, BarChart2, FileText, Lightbulb } from 'lucide-react';

const actions = [
  {
    label: '快捷數據',
    icon: BarChart2,
    color: 'from-blue-600 to-cyan-600',
  },
  {
    label: '主題創建',
    icon: Lightbulb,
    color: 'from-green-600 to-emerald-600',
  },
  {
    label: 'AI 工具',
    icon: Sparkles,
    color: 'from-purple-600 to-violet-600',
  },
  {
    label: '專案追蹤',
    icon: TrendingUp,
    color: 'from-pink-600 to-rose-600',
  },
];

export function QuickActions() {
  return (
    <div className="mb-8">
      <div className="flex items-center gap-2 mb-4">
        <div className="relative">
          <Sparkles className="w-5 h-5 text-purple-600" />
          <Sparkles className="w-5 h-5 text-purple-400 absolute inset-0 animate-ping opacity-75" />
        </div>
        <h2 className="text-xl font-light text-gray-900">快捷操作</h2>
        <div className="h-px flex-1 bg-gradient-to-r from-purple-300 via-transparent to-transparent ml-4"></div>
      </div>

      <div className="grid grid-cols-4 gap-6">
        {actions.map((action, index) => {
          const Icon = action.icon;
          return (
            <button
              key={index}
              className="group relative rounded-2xl bg-white/70 backdrop-blur-xl border border-white/60 shadow-lg p-8 hover:bg-white/90 transition-all duration-300 hover:scale-105 hover:shadow-2xl overflow-hidden"
            >
              {/* Animated gradient background */}
              <div className={`absolute inset-0 bg-gradient-to-br ${action.color} opacity-0 group-hover:opacity-10 transition-opacity duration-500`}></div>
              
              {/* Glow effect on hover */}
              <div className={`absolute inset-0 bg-gradient-to-br ${action.color} blur-2xl opacity-0 group-hover:opacity-20 transition-opacity duration-500`}></div>

              {/* Hexagonal pattern */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="absolute top-4 left-4 w-8 h-8 border-2 border-purple-300/30 rotate-45"></div>
                <div className="absolute bottom-4 right-4 w-6 h-6 border-2 border-cyan-300/30 rotate-45"></div>
              </div>

              {/* Holographic corners */}
              <div className="absolute top-0 left-0 w-6 h-6 border-l-2 border-t-2 border-purple-400/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-tl-2xl"></div>
              <div className="absolute top-0 right-0 w-6 h-6 border-r-2 border-t-2 border-cyan-400/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-tr-2xl"></div>
              <div className="absolute bottom-0 left-0 w-6 h-6 border-l-2 border-b-2 border-purple-400/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-bl-2xl"></div>
              <div className="absolute bottom-0 right-0 w-6 h-6 border-r-2 border-b-2 border-cyan-400/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-br-2xl"></div>

              <div className="relative z-10 flex flex-col items-center gap-4">
                <div className={`relative w-16 h-16 rounded-2xl bg-gradient-to-br ${action.color} flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110`}>
                  <Icon className="w-8 h-8 text-white relative z-10" />
                  {/* Icon glow */}
                  <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${action.color} blur-lg opacity-0 group-hover:opacity-70 transition-opacity`}></div>
                  {/* Rotating ring */}
                  <div className="absolute inset-0 rounded-2xl border-2 border-white/30 animate-spin-slow opacity-0 group-hover:opacity-100 transition-opacity"></div>
                </div>
                
                <span className="text-gray-900 font-medium">{action.label}</span>
              </div>

              {/* Scanning line effect */}
              <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-purple-400/70 to-transparent translate-x-[-100%] group-hover:animate-[scan_1.5s_ease-in-out]"></div>
              
              {/* Vertical scan line */}
              <div className="absolute top-0 left-0 h-full w-0.5 bg-gradient-to-b from-transparent via-cyan-400/70 to-transparent translate-y-[-100%] group-hover:animate-[scan-vertical_1.5s_ease-in-out_0.3s]"></div>
              
              {/* Data particles */}
              <div className="absolute top-1/4 left-1/4 w-1 h-1 bg-purple-400 rounded-full opacity-0 group-hover:animate-float-particle group-hover:opacity-60"></div>
              <div className="absolute bottom-1/4 right-1/4 w-1 h-1 bg-cyan-400 rounded-full opacity-0 group-hover:animate-float-particle-delayed group-hover:opacity-60"></div>
            </button>
          );
        })}
      </div>
    </div>
  );
}