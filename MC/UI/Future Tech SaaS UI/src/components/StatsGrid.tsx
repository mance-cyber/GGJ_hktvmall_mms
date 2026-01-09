import { TrendingUp, TrendingDown, ArrowUpRight, Users, FileText, Calendar, Target, Activity } from 'lucide-react';

const stats = [
  {
    label: '今日訪客',
    value: '0',
    subtext: '今日',
    icon: Users,
    color: 'from-blue-600 to-cyan-600',
    trend: '+0%',
    trendUp: false,
  },
  {
    label: '新增訪客',
    value: '0',
    subtext: '今天共 0 次',
    icon: TrendingUp,
    color: 'from-green-600 to-emerald-600',
    trend: '+0%',
    trendUp: false,
  },
  {
    label: '新資源',
    value: '4',
    subtext: '今天共 0 次',
    icon: FileText,
    color: 'from-purple-600 to-violet-600',
    trend: '+12%',
    trendUp: true,
  },
  {
    label: '月度統計',
    value: '10',
    subtext: '總計人次',
    icon: Target,
    color: 'from-pink-600 to-rose-600',
    trend: '+8%',
    trendUp: true,
  },
];

const metrics = [
  { label: '新增訪客', value: '0', subtext: '今天共 0 次', color: 'blue', icon: Users },
  { label: '訪客統計', value: '0', subtext: '今天共 0 次', color: 'green', icon: TrendingUp },
  { label: '新資源', value: '4', subtext: '今天共 0 次', color: 'purple', icon: FileText },
  { label: '月度統計', value: '10', subtext: '總計人次', color: 'pink', icon: Calendar },
];

export function StatsGrid() {
  const getColorClasses = (color: string) => {
    const colors = {
      blue: 'from-blue-600 to-cyan-600',
      green: 'from-green-600 to-emerald-600',
      purple: 'from-purple-600 to-violet-600',
      pink: 'from-pink-600 to-rose-600',
    };
    return colors[color as keyof typeof colors];
  };

  return (
    <div className="mb-8">
      {/* Main stats */}
      <div className="grid grid-cols-4 gap-6 mb-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div
              key={index}
              className="group relative rounded-2xl bg-white/70 backdrop-blur-xl border border-white/60 shadow-lg p-6 hover:bg-white/90 transition-all duration-300 hover:scale-105 hover:shadow-2xl overflow-hidden"
            >
              {/* Animated gradient background */}
              <div className={`absolute inset-0 bg-gradient-to-br ${stat.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}></div>
              
              {/* Glow effect */}
              <div className={`absolute -top-12 -right-12 w-24 h-24 bg-gradient-to-br ${stat.color} rounded-full blur-2xl opacity-0 group-hover:opacity-30 transition-opacity duration-300`}></div>

              {/* Holographic corners */}
              <div className="absolute top-0 left-0 w-4 h-4 border-l-2 border-t-2 border-purple-300/50 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="absolute top-0 right-0 w-4 h-4 border-r-2 border-t-2 border-cyan-300/50 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="absolute bottom-0 left-0 w-4 h-4 border-l-2 border-b-2 border-purple-300/50 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="absolute bottom-0 right-0 w-4 h-4 border-r-2 border-b-2 border-cyan-300/50 opacity-0 group-hover:opacity-100 transition-opacity"></div>

              {/* Data stream effect */}
              <div className="absolute left-0 top-1/2 w-px h-8 bg-gradient-to-b from-transparent via-purple-400/50 to-transparent animate-data-stream opacity-0 group-hover:opacity-100"></div>

              <div className="relative z-10">
                <div className="flex items-start justify-between mb-4">
                  <div className={`relative w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center shadow-md group-hover:shadow-lg transition-shadow`}>
                    <Icon className="w-6 h-6 text-white" />
                    {/* Icon glow */}
                    <div className={`absolute inset-0 rounded-xl bg-gradient-to-br ${stat.color} blur-md opacity-0 group-hover:opacity-50 transition-opacity`}></div>
                  </div>
                  
                  <div className={`flex items-center gap-1 px-2 py-1 rounded-lg border ${
                    stat.trendUp 
                      ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-300 text-green-600' 
                      : 'bg-gradient-to-r from-gray-50 to-slate-50 border-gray-300 text-gray-600'
                  }`}>
                    {stat.trendUp ? (
                      <TrendingUp className="w-3 h-3" />
                    ) : (
                      <TrendingDown className="w-3 h-3" />
                    )}
                    <span className="text-xs font-medium">{stat.trend}</span>
                  </div>
                </div>

                <div className="text-3xl font-bold text-gray-900 mb-1 relative">
                  {stat.value}
                  {/* Number underline */}
                  <div className={`absolute -bottom-0.5 left-0 h-0.5 w-0 bg-gradient-to-r ${stat.color} group-hover:w-full transition-all duration-500`}></div>
                </div>
                <div className="text-sm text-gray-700 mb-1 font-medium">{stat.label}</div>
                <div className="text-xs text-gray-500 flex items-center gap-1">
                  <Activity className="w-3 h-3" />
                  {stat.subtext}
                </div>
              </div>

              {/* Corner accent with animation */}
              <div className={`absolute bottom-0 right-0 w-20 h-20 bg-gradient-to-tl ${stat.color} opacity-5 rounded-tl-full group-hover:opacity-10 transition-opacity`}></div>
              
              {/* Scan line */}
              <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-purple-400/50 to-transparent -translate-y-full group-hover:translate-y-[200%] transition-transform duration-1000 ease-out"></div>
            </div>
          );
        })}
      </div>

      {/* Secondary metrics */}
      <div className="grid grid-cols-4 gap-6">
        {metrics.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <div
              key={index}
              className="group relative rounded-xl bg-white/70 backdrop-blur-xl border border-white/60 shadow-md p-5 hover:bg-white/90 transition-all duration-300 hover:shadow-lg overflow-hidden"
            >
              {/* Circuit pattern background */}
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="absolute top-2 right-2 w-12 h-12">
                  <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-purple-300/50"></div>
                  <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-cyan-300/50"></div>
                  <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-purple-300/50"></div>
                  <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-cyan-300/50"></div>
                </div>
              </div>

              <div className="flex items-center gap-3 mb-3 relative z-10">
                <div className={`relative w-10 h-10 rounded-lg bg-gradient-to-br ${getColorClasses(metric.color)} flex items-center justify-center shadow-sm`}>
                  <Icon className="w-5 h-5 text-white" />
                  {/* Rotating ring */}
                  <div className="absolute inset-0 rounded-lg border border-white/30 animate-spin-slow opacity-0 group-hover:opacity-100 transition-opacity"></div>
                </div>
                <div className="text-sm text-gray-700 font-medium">{metric.label}</div>
              </div>
              
              <div className="flex items-end justify-between relative z-10">
                <div>
                  <div className="text-2xl font-bold text-gray-900 mb-1">{metric.value}</div>
                  <div className="text-xs text-gray-500">{metric.subtext}</div>
                </div>
                
                <div className="relative">
                  <ArrowUpRight className="w-4 h-4 text-gray-400 group-hover:text-purple-600 transition-colors" />
                  {/* Arrow trail effect */}
                  <ArrowUpRight className="w-4 h-4 text-purple-400 absolute inset-0 opacity-0 group-hover:opacity-50 group-hover:translate-x-1 group-hover:-translate-y-1 transition-all duration-300" />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}