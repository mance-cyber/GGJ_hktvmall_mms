import { Target, TrendingUp, Building2, AlertCircle } from 'lucide-react';

const competitors = [
  {
    name: '大公司名',
    company: '24/12/27',
    score: 0,
    status: '高威',
    trend: 'up',
  },
  {
    name: 'AEON',
    company: '24/12',
    score: 10,
    status: '高威',
    trend: 'up',
  },
  {
    name: '華夏',
    company: '09/01/2025',
    score: 10,
    status: '高威',
    trend: 'up',
  },
  {
    name: '日本',
    company: '24/01/2025',
    score: 10,
    status: '高威',
    trend: 'up',
  },
];

export function CompetitorMonitoring() {
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="relative">
            <Target className="w-5 h-5 text-purple-600" />
            <div className="absolute inset-0 animate-ping opacity-75">
              <Target className="w-5 h-5 text-purple-400" />
            </div>
          </div>
          <h2 className="text-xl font-light text-gray-900">競爭對手監測</h2>
          <div className="h-px flex-1 bg-gradient-to-r from-purple-300 via-transparent to-transparent ml-4"></div>
        </div>
        
        <button className="group flex items-center gap-2 text-sm text-purple-600 hover:text-purple-700 transition-colors font-medium px-4 py-2 rounded-lg hover:bg-purple-50 border border-transparent hover:border-purple-200">
          查看全部 →
        </button>
      </div>

      <div className="rounded-2xl bg-white/70 backdrop-blur-xl border border-white/60 shadow-lg overflow-hidden relative">
        {/* Holographic top edge */}
        <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-400/50 to-transparent"></div>
        
        {/* Table header */}
        <div className="grid grid-cols-12 gap-4 px-6 py-4 border-b border-gray-200/60 bg-gradient-to-r from-purple-50/50 to-cyan-50/50 relative">
          <div className="col-span-3 text-xs text-gray-600 uppercase tracking-wider font-medium">競爭對手</div>
          <div className="col-span-3 text-xs text-gray-600 uppercase tracking-wider font-medium">更新時間</div>
          <div className="col-span-2 text-xs text-gray-600 uppercase tracking-wider font-medium">威脅等級</div>
          <div className="col-span-2 text-xs text-gray-600 uppercase tracking-wider font-medium">分數</div>
          <div className="col-span-2 text-xs text-gray-600 uppercase tracking-wider font-medium text-right">趨勢</div>
          
          {/* Corner accents */}
          <div className="absolute top-0 left-0 w-3 h-3 border-l-2 border-t-2 border-purple-300/50"></div>
          <div className="absolute top-0 right-0 w-3 h-3 border-r-2 border-t-2 border-cyan-300/50"></div>
        </div>

        {/* Table rows */}
        <div className="divide-y divide-gray-200/40">
          {competitors.map((competitor, index) => (
            <div
              key={index}
              className="grid grid-cols-12 gap-4 px-6 py-5 hover:bg-white/60 transition-all duration-300 group relative"
            >
              {/* Hover scan effect */}
              <div className="absolute left-0 top-0 w-1 h-full bg-gradient-to-b from-purple-500 via-cyan-500 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              
              <div className="col-span-3 flex items-center gap-3 relative z-10">
                <div className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-purple-100 to-cyan-100 flex items-center justify-center border border-purple-200/60 group-hover:border-purple-300 transition-colors shadow-sm">
                  <Building2 className="w-5 h-5 text-purple-600" />
                  {/* Rotating corner */}
                  <div className="absolute top-0 right-0 w-2 h-2 border-r border-t border-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                </div>
                <div>
                  <div className="text-gray-900 font-medium group-hover:text-purple-700 transition-colors">{competitor.name}</div>
                </div>
              </div>

              <div className="col-span-3 flex items-center relative z-10">
                <div className="text-sm text-gray-600">{competitor.company}</div>
              </div>

              <div className="col-span-2 flex items-center relative z-10">
                <span className="relative px-3 py-1 rounded-lg text-xs font-medium overflow-hidden bg-red-100 text-red-700 border border-red-300">
                  <span className="relative z-10">{competitor.status}</span>
                  <div className="absolute inset-0 bg-gradient-to-r from-red-200/50 to-transparent animate-shimmer"></div>
                </span>
              </div>

              <div className="col-span-2 flex items-center relative z-10">
                <div className="text-lg font-bold text-gray-900">{competitor.score}</div>
              </div>

              <div className="col-span-2 flex items-center justify-end gap-2 relative z-10">
                <div className="flex items-center gap-1 px-2 py-1 rounded-lg bg-green-100 text-green-700 border border-green-300">
                  <TrendingUp className="w-4 h-4" />
                  <span className="text-xs font-medium">{competitor.status}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
