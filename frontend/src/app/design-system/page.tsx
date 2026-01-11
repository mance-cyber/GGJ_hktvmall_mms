'use client'

// =============================================
// Future Tech Design System 展示頁面
// =============================================

import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  HoloCard,
  DataMetric,
  PulseStatus,
  DataStreamBg,
  HoloButton,
  HoloBadge,
  TechDivider,
  PageTransition,
  StaggerContainer,
  HoloPanelHeader,
  HoloTooltip,
  ProgressRing,
  HoloSkeleton,
} from '@/components/ui/future-tech'
import {
  Zap,
  TrendingUp,
  Package,
  Users,
  Activity,
  Bell,
  Settings,
  ChevronRight,
  Sparkles,
  BarChart3,
  Shield,
  Cpu,
  Database,
  Wifi,
  RefreshCw,
} from 'lucide-react'

export default function DesignSystemPage() {
  const [loading, setLoading] = useState(false)

  return (
    <PageTransition>
      <div className="relative min-h-screen">
        {/* 背景數據流 */}
        <DataStreamBg density="low" color="cyan" className="opacity-30" />

        <div className="relative z-10 max-w-6xl mx-auto space-y-12 pb-20">
          {/* ========== 頁面標題 ========== */}
          <div className="text-center pt-8">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-50 border border-cyan-200 mb-4"
            >
              <Sparkles className="w-4 h-4 text-cyan-500" />
              <span className="text-sm font-medium text-cyan-700">Future Tech Design System</span>
            </motion.div>
            <h1 className="text-4xl font-bold text-slate-800 mb-2">
              未來科技感組件庫
            </h1>
            <p className="text-slate-500 max-w-xl mx-auto">
              淺色系、專業感、豐富動畫的 React 組件，打造沉浸式科技體驗
            </p>
          </div>

          <TechDivider label="狀態指示器" />

          {/* ========== 狀態指示器 ========== */}
          <HoloCard className="p-6">
            <HoloPanelHeader
              title="系統狀態監控"
              subtitle="即時監測各服務運行狀況"
              icon={<Activity className="w-5 h-5" />}
            />
            <div className="p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-slate-500">API 服務</h4>
                  <PulseStatus status="online" size="md" />
                </div>
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-slate-500">數據庫</h4>
                  <PulseStatus status="online" label="PostgreSQL" size="md" />
                </div>
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-slate-500">AI 引擎</h4>
                  <PulseStatus status="processing" size="md" />
                </div>
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-slate-500">備份服務</h4>
                  <PulseStatus status="warning" label="需要注意" size="md" />
                </div>
              </div>
            </div>
          </HoloCard>

          <TechDivider label="數據指標" />

          {/* ========== 數據指標卡片 ========== */}
          <StaggerContainer className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <DataMetric
              label="總營收"
              value={1258430}
              prefix="$"
              trend={12.5}
              color="cyan"
              icon={<TrendingUp className="w-5 h-5 text-cyan-500" />}
            />
            <DataMetric
              label="活躍用戶"
              value={3847}
              trend={8.2}
              color="blue"
              icon={<Users className="w-5 h-5 text-blue-500" />}
            />
            <DataMetric
              label="商品數量"
              value={12458}
              trend={-2.1}
              color="purple"
              icon={<Package className="w-5 h-5 text-violet-500" />}
            />
            <DataMetric
              label="系統負載"
              value={67}
              suffix="%"
              color="green"
              icon={<Cpu className="w-5 h-5 text-emerald-500" />}
            />
          </StaggerContainer>

          <TechDivider label="全息卡片" />

          {/* ========== 全息卡片展示 ========== */}
          <div className="grid md:grid-cols-2 gap-6">
            <HoloCard glowColor="cyan" scanLine className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-slate-800">實時數據分析</h3>
                  <p className="text-sm text-slate-500">AI 驅動的智能洞察</p>
                </div>
                <div className="p-2 rounded-xl bg-cyan-50">
                  <BarChart3 className="w-6 h-6 text-cyan-500" />
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600">處理進度</span>
                  <ProgressRing progress={78} size={50} color="cyan" />
                </div>
                <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: '78%' }}
                    transition={{ duration: 1.5, ease: [0.22, 1, 0.36, 1] }}
                  />
                </div>
              </div>
            </HoloCard>

            <HoloCard glowColor="purple" className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-slate-800">安全防護中心</h3>
                  <p className="text-sm text-slate-500">全方位安全監控</p>
                </div>
                <div className="p-2 rounded-xl bg-violet-50">
                  <Shield className="w-6 h-6 text-violet-500" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 mt-4">
                <div className="p-3 rounded-xl bg-slate-50">
                  <div className="text-2xl font-bold text-slate-800">99.9%</div>
                  <div className="text-xs text-slate-500">正常運行時間</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-50">
                  <div className="text-2xl font-bold text-emerald-600">0</div>
                  <div className="text-xs text-slate-500">安全事件</div>
                </div>
              </div>
            </HoloCard>
          </div>

          <TechDivider label="按鈕與標籤" />

          {/* ========== 按鈕展示 ========== */}
          <HoloCard className="p-6">
            <h3 className="text-lg font-semibold text-slate-800 mb-6">互動元素</h3>

            <div className="space-y-6">
              {/* 按鈕 */}
              <div>
                <h4 className="text-sm font-medium text-slate-500 mb-3">按鈕樣式</h4>
                <div className="flex flex-wrap gap-3">
                  <HoloButton variant="primary" icon={<Zap className="w-4 h-4" />}>
                    主要按鈕
                  </HoloButton>
                  <HoloButton variant="secondary" icon={<Settings className="w-4 h-4" />}>
                    次要按鈕
                  </HoloButton>
                  <HoloButton variant="ghost">
                    幽靈按鈕
                  </HoloButton>
                  <HoloButton
                    variant="primary"
                    loading={loading}
                    onClick={() => {
                      setLoading(true)
                      setTimeout(() => setLoading(false), 2000)
                    }}
                  >
                    {loading ? '處理中...' : '點擊加載'}
                  </HoloButton>
                </div>
              </div>

              {/* 標籤 */}
              <div>
                <h4 className="text-sm font-medium text-slate-500 mb-3">標籤樣式</h4>
                <div className="flex flex-wrap gap-2">
                  <HoloBadge variant="default">默認</HoloBadge>
                  <HoloBadge variant="success">
                    <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
                    成功
                  </HoloBadge>
                  <HoloBadge variant="warning">警告</HoloBadge>
                  <HoloBadge variant="error">錯誤</HoloBadge>
                  <HoloBadge variant="info" pulse>
                    <RefreshCw className="w-3 h-3 animate-spin" />
                    同步中
                  </HoloBadge>
                </div>
              </div>

              {/* 工具提示 */}
              <div>
                <h4 className="text-sm font-medium text-slate-500 mb-3">工具提示</h4>
                <div className="flex gap-4">
                  <HoloTooltip content="這是頂部提示" position="top">
                    <HoloButton variant="secondary" size="sm">頂部</HoloButton>
                  </HoloTooltip>
                  <HoloTooltip content="這是底部提示" position="bottom">
                    <HoloButton variant="secondary" size="sm">底部</HoloButton>
                  </HoloTooltip>
                  <HoloTooltip content="這是右側提示" position="right">
                    <HoloButton variant="secondary" size="sm">右側</HoloButton>
                  </HoloTooltip>
                </div>
              </div>
            </div>
          </HoloCard>

          <TechDivider label="進度指示器" />

          {/* ========== 進度環展示 ========== */}
          <HoloCard className="p-6">
            <h3 className="text-lg font-semibold text-slate-800 mb-6">進度展示</h3>
            <div className="flex justify-around items-center">
              <div className="text-center">
                <ProgressRing progress={25} color="cyan" size={80} />
                <p className="mt-2 text-sm text-slate-500">數據同步</p>
              </div>
              <div className="text-center">
                <ProgressRing progress={68} color="blue" size={80} />
                <p className="mt-2 text-sm text-slate-500">AI 處理</p>
              </div>
              <div className="text-center">
                <ProgressRing progress={92} color="green" size={80} />
                <p className="mt-2 text-sm text-slate-500">儲存空間</p>
              </div>
              <div className="text-center">
                <ProgressRing progress={45} color="purple" size={80} />
                <p className="mt-2 text-sm text-slate-500">任務完成</p>
              </div>
            </div>
          </HoloCard>

          <TechDivider label="骨架屏" />

          {/* ========== 骨架屏展示 ========== */}
          <HoloCard className="p-6">
            <h3 className="text-lg font-semibold text-slate-800 mb-6">加載狀態</h3>
            <div className="space-y-4">
              <div className="flex items-center gap-4">
                <HoloSkeleton variant="circular" width={48} height={48} />
                <div className="flex-1 space-y-2">
                  <HoloSkeleton variant="text" width="60%" height={16} />
                  <HoloSkeleton variant="text" width="40%" height={12} />
                </div>
              </div>
              <HoloSkeleton variant="rectangular" width="100%" height={120} />
              <div className="grid grid-cols-3 gap-4">
                <HoloSkeleton variant="rectangular" height={80} />
                <HoloSkeleton variant="rectangular" height={80} />
                <HoloSkeleton variant="rectangular" height={80} />
              </div>
            </div>
          </HoloCard>

          <TechDivider label="完整示例" />

          {/* ========== 完整面板示例 ========== */}
          <HoloCard glowColor="blue" scanLine>
            <HoloPanelHeader
              title="系統控制面板"
              subtitle="一站式管理所有服務"
              icon={<Database className="w-5 h-5" />}
              action={
                <HoloButton variant="secondary" size="sm" icon={<ChevronRight className="w-4 h-4" />}>
                  查看全部
                </HoloButton>
              }
            />
            <div className="p-6">
              <div className="grid md:grid-cols-3 gap-6">
                {/* 服務卡片 */}
                {[
                  { name: 'API Gateway', status: 'online', metric: '12.3k/s', icon: Wifi },
                  { name: 'Database', status: 'online', metric: '98%', icon: Database },
                  { name: 'AI Engine', status: 'processing', metric: '處理中', icon: Cpu },
                ].map((service) => (
                  <motion.div
                    key={service.name}
                    whileHover={{ scale: 1.02 }}
                    className="p-4 rounded-xl bg-slate-50/80 border border-slate-100 hover:border-cyan-200 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <service.icon className="w-5 h-5 text-slate-400" />
                      <PulseStatus status={service.status as any} size="sm" />
                    </div>
                    <h4 className="font-medium text-slate-800">{service.name}</h4>
                    <p className="text-sm text-slate-500">{service.metric}</p>
                  </motion.div>
                ))}
              </div>
            </div>
          </HoloCard>

          {/* ========== 設計說明 ========== */}
          <HoloCard className="p-6 bg-gradient-to-br from-cyan-50/50 to-blue-50/50">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">設計理念</h3>
            <div className="grid md:grid-cols-2 gap-6 text-sm text-slate-600">
              <div className="space-y-2">
                <h4 className="font-medium text-slate-700">🎨 視覺風格</h4>
                <ul className="space-y-1 text-slate-500">
                  <li>• 淺色系背景，減少視覺疲勞</li>
                  <li>• 青-藍色調，傳達科技與專業感</li>
                  <li>• 玻璃擬態效果，增加層次感</li>
                  <li>• 微妙漸變，避免過於花哨</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium text-slate-700">✨ 動效設計</h4>
                <ul className="space-y-1 text-slate-500">
                  <li>• 頁面入場動畫，提升體驗</li>
                  <li>• 數據計數動畫，吸引注意</li>
                  <li>• 懸停光效，增強互動感</li>
                  <li>• 脈衝狀態指示，傳達即時性</li>
                </ul>
              </div>
            </div>
          </HoloCard>
        </div>
      </div>
    </PageTransition>
  )
}
