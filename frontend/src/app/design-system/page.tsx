'use client'

// =============================================
// Future Tech Design System showcase page
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
        {/* Background data stream */}
        <DataStreamBg density="low" color="cyan" className="opacity-30" />

        <div className="relative z-10 max-w-6xl mx-auto space-y-12 pb-20">
          {/* ========== Page title ========== */}
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
              Futuristic UI Component Library
            </h1>
            <p className="text-slate-500 max-w-xl mx-auto">
              Light-theme, professional-grade React components with rich animations for an immersive tech experience
            </p>
          </div>

          <TechDivider label="Status Indicators" />

          {/* ========== Status Indicators ========== */}
          <HoloCard className="p-6">
            <HoloPanelHeader
              title="System Status Monitor"
              subtitle="Real-time monitoring of all service statuses"
              icon={<Activity className="w-5 h-5" />}
            />
            <div className="p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-slate-500">API Service</h4>
                  <PulseStatus status="online" size="md" />
                </div>
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-slate-500">Database</h4>
                  <PulseStatus status="online" label="PostgreSQL" size="md" />
                </div>
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-slate-500">AI Engine</h4>
                  <PulseStatus status="processing" size="md" />
                </div>
                <div className="space-y-3">
                  <h4 className="text-sm font-medium text-slate-500">Backup Service</h4>
                  <PulseStatus status="warning" label="Needs Attention" size="md" />
                </div>
              </div>
            </div>
          </HoloCard>

          <TechDivider label="Data Metrics" />

          {/* ========== Data Metrics Cards ========== */}
          <StaggerContainer className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <DataMetric
              label="Total Revenue"
              value={1258430}
              prefix="$"
              trend={12.5}
              color="cyan"
              icon={<TrendingUp className="w-5 h-5 text-cyan-500" />}
            />
            <DataMetric
              label="Active Users"
              value={3847}
              trend={8.2}
              color="blue"
              icon={<Users className="w-5 h-5 text-blue-500" />}
            />
            <DataMetric
              label="Product Count"
              value={12458}
              trend={-2.1}
              color="purple"
              icon={<Package className="w-5 h-5 text-violet-500" />}
            />
            <DataMetric
              label="System Load"
              value={67}
              suffix="%"
              color="green"
              icon={<Cpu className="w-5 h-5 text-emerald-500" />}
            />
          </StaggerContainer>

          <TechDivider label="Holographic Cards" />

          {/* ========== Holographic Card showcase ========== */}
          <div className="grid md:grid-cols-2 gap-6">
            <HoloCard glowColor="cyan" scanLine className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-slate-800">Real-time Data Analysis</h3>
                  <p className="text-sm text-slate-500">AI-powered Intelligent Insights</p>
                </div>
                <div className="p-2 rounded-xl bg-cyan-50">
                  <BarChart3 className="w-6 h-6 text-cyan-500" />
                </div>
              </div>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-slate-600">Processing Progress</span>
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
                  <h3 className="text-lg font-semibold text-slate-800">Security Center</h3>
                  <p className="text-sm text-slate-500">Comprehensive Security Monitoring</p>
                </div>
                <div className="p-2 rounded-xl bg-violet-50">
                  <Shield className="w-6 h-6 text-violet-500" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 mt-4">
                <div className="p-3 rounded-xl bg-slate-50">
                  <div className="text-2xl font-bold text-slate-800">99.9%</div>
                  <div className="text-xs text-slate-500">Uptime</div>
                </div>
                <div className="p-3 rounded-xl bg-slate-50">
                  <div className="text-2xl font-bold text-emerald-600">0</div>
                  <div className="text-xs text-slate-500">Security Incidents</div>
                </div>
              </div>
            </HoloCard>
          </div>

          <TechDivider label="Buttons & Badges" />

          {/* ========== Buttons & Badges showcase ========== */}
          <HoloCard className="p-6">
            <h3 className="text-lg font-semibold text-slate-800 mb-6">Interactive Elements</h3>

            <div className="space-y-6">
              {/* Buttons */}
              <div>
                <h4 className="text-sm font-medium text-slate-500 mb-3">Button Styles</h4>
                <div className="flex flex-wrap gap-3">
                  <HoloButton variant="primary" icon={<Zap className="w-4 h-4" />}>
                    Primary
                  </HoloButton>
                  <HoloButton variant="secondary" icon={<Settings className="w-4 h-4" />}>
                    Secondary
                  </HoloButton>
                  <HoloButton variant="ghost">
                    Ghost
                  </HoloButton>
                  <HoloButton
                    variant="primary"
                    loading={loading}
                    onClick={() => {
                      setLoading(true)
                      setTimeout(() => setLoading(false), 2000)
                    }}
                  >
                    {loading ? 'Processing...' : 'Click to Load'}
                  </HoloButton>
                </div>
              </div>

              {/* Badges */}
              <div>
                <h4 className="text-sm font-medium text-slate-500 mb-3">Badge Styles</h4>
                <div className="flex flex-wrap gap-2">
                  <HoloBadge variant="default">Default</HoloBadge>
                  <HoloBadge variant="success">
                    <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full" />
                    Success
                  </HoloBadge>
                  <HoloBadge variant="warning">Warning</HoloBadge>
                  <HoloBadge variant="error">Error</HoloBadge>
                  <HoloBadge variant="info" pulse>
                    <RefreshCw className="w-3 h-3 animate-spin" />
                    Syncing
                  </HoloBadge>
                </div>
              </div>

              {/* Tooltips */}
              <div>
                <h4 className="text-sm font-medium text-slate-500 mb-3">Tooltips</h4>
                <div className="flex gap-4">
                  <HoloTooltip content="Top tooltip" position="top">
                    <HoloButton variant="secondary" size="sm">Top</HoloButton>
                  </HoloTooltip>
                  <HoloTooltip content="Bottom tooltip" position="bottom">
                    <HoloButton variant="secondary" size="sm">Bottom</HoloButton>
                  </HoloTooltip>
                  <HoloTooltip content="Right tooltip" position="right">
                    <HoloButton variant="secondary" size="sm">Right</HoloButton>
                  </HoloTooltip>
                </div>
              </div>
            </div>
          </HoloCard>

          <TechDivider label="Progress Indicators" />

          {/* ========== Progress ring showcase ========== */}
          <HoloCard className="p-6">
            <h3 className="text-lg font-semibold text-slate-800 mb-6">Progress Display</h3>
            <div className="flex justify-around items-center">
              <div className="text-center">
                <ProgressRing progress={25} color="cyan" size={80} />
                <p className="mt-2 text-sm text-slate-500">Data Sync</p>
              </div>
              <div className="text-center">
                <ProgressRing progress={68} color="blue" size={80} />
                <p className="mt-2 text-sm text-slate-500">AI Processing</p>
              </div>
              <div className="text-center">
                <ProgressRing progress={92} color="green" size={80} />
                <p className="mt-2 text-sm text-slate-500">Storage</p>
              </div>
              <div className="text-center">
                <ProgressRing progress={45} color="purple" size={80} />
                <p className="mt-2 text-sm text-slate-500">Task Completion</p>
              </div>
            </div>
          </HoloCard>

          <TechDivider label="Skeleton" />

          {/* ========== Skeleton Showcase ========== */}
          <HoloCard className="p-6">
            <h3 className="text-lg font-semibold text-slate-800 mb-6">Loading state</h3>
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

          <TechDivider label="Full Example" />

          {/* ========== Full panel example ========== */}
          <HoloCard glowColor="blue" scanLine>
            <HoloPanelHeader
              title="System Control Panel"
              subtitle="One-stop management for all services"
              icon={<Database className="w-5 h-5" />}
              action={
                <HoloButton variant="secondary" size="sm" icon={<ChevronRight className="w-4 h-4" />}>
                  View All
                </HoloButton>
              }
            />
            <div className="p-6">
              <div className="grid md:grid-cols-3 gap-6">
                {/* Service Cards */}
                {[
                  { name: 'API Gateway', status: 'online', metric: '12.3k/s', icon: Wifi },
                  { name: 'Database', status: 'online', metric: '98%', icon: Database },
                  { name: 'AI Engine', status: 'processing', metric: 'Processing', icon: Cpu },
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

          {/* ========== Design philosophy ========== */}
          <HoloCard className="p-6 bg-gradient-to-br from-cyan-50/50 to-blue-50/50">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">Design Philosophy</h3>
            <div className="grid md:grid-cols-2 gap-6 text-sm text-slate-600">
              <div className="space-y-2">
                <h4 className="font-medium text-slate-700">🎨 Visual Style</h4>
                <ul className="space-y-1 text-slate-500">
                  <li>• Light background to reduce visual fatigue</li>
                  <li>• Cyan-blue tones conveying a tech and professional feel</li>
                  <li>• Glassmorphism effect, adds depth</li>
                  <li>• Subtle gradients, avoiding excessive ornamentation</li>
                </ul>
              </div>
              <div className="space-y-2">
                <h4 className="font-medium text-slate-700">✨ Animation Design</h4>
                <ul className="space-y-1 text-slate-500">
                  <li>• Page entrance animations, enhance experience</li>
                  <li>• Data count animations to capture attention</li>
                  <li>• Hover glow effects to enhance interactivity</li>
                  <li>• Pulse status indicators for real-time feedback</li>
                </ul>
              </div>
            </div>
          </HoloCard>
        </div>
      </div>
    </PageTransition>
  )
}
