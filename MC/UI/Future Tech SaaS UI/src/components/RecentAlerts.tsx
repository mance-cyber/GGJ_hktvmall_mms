import { Bell, AlertTriangle, TrendingUp, Clock } from 'lucide-react';

const alerts = [
  {
    title: '競爭對手降價',
    description: 'AEON 推出新促銷活動',
    time: '2小時前',
    type: 'urgent',
  },
  {
    title: '市場趨勢變化',
    description: '消費者偏好轉向線上購物',
    time: '5小時前',
    type: 'warning',
  },
  {
    title: '新產品發布',
    description: '華夏推出新品線',
    time: '1天前',
    type: 'info',
  },
];

export function RecentAlerts() {
  return (
    <div className="rounded-2xl bg-white/70 backdrop-blur-xl border border-white/60 shadow-lg p-6 relative overflow-hidden h-full">
      {/* Holographic edge effect */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-purple-400/50 to-transparent"></div>
      
      <div className="flex items-center gap-2 mb-6">
        <div className="relative">
          <Bell className="w-5 h-5 text-purple-600" />
          <div className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
        </div>
        <h3 className="text-lg font-medium text-gray-900">最近警報</h3>
      </div>

      {/* Empty state */}
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="relative w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-100 to-cyan-100 flex items-center justify-center border border-purple-200/60 mb-4">
          <Bell className="w-10 h-10 text-purple-400" />
          {/* Pulsing rings */}
          <div className="absolute inset-0 rounded-2xl border-2 border-purple-300 animate-ping opacity-30"></div>
          <div className="absolute inset-0 rounded-2xl border-2 border-cyan-300 animate-ping opacity-20" style={{ animationDelay: '0.5s' }}></div>
        </div>
        
        <p className="text-gray-600 mb-1">暫無最新警報提示</p>
        <p className="text-gray-500 text-sm">當有重要市場變化時會通知您</p>
        
        <div className="mt-6 text-xs text-gray-400">
          系統持續監控中...
        </div>
      </div>

      {/* If there are alerts - currently hidden 
      <div className="space-y-3">
        {alerts.map((alert, index) => (
          <div
            key={index}
            className="group relative p-4 rounded-xl bg-white/50 border border-purple-200/40 hover:bg-white/70 hover:border-purple-300/60 transition-all duration-300 cursor-pointer"
          >
            <div className="flex items-start gap-3">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                alert.type === 'urgent' 
                  ? 'bg-red-100 text-red-600' 
                  : alert.type === 'warning'
                  ? 'bg-orange-100 text-orange-600'
                  : 'bg-blue-100 text-blue-600'
              }`}>
                <AlertTriangle className="w-4 h-4" />
              </div>
              
              <div className="flex-1">
                <div className="text-sm font-medium text-gray-900 mb-1">{alert.title}</div>
                <div className="text-xs text-gray-600 mb-2">{alert.description}</div>
                <div className="flex items-center gap-1 text-xs text-gray-500">
                  <Clock className="w-3 h-3" />
                  {alert.time}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      */}

      {/* Corner decorations */}
      <div className="absolute bottom-0 right-0 w-24 h-24 bg-gradient-to-tl from-purple-100/30 to-transparent rounded-tl-full"></div>
    </div>
  );
}
