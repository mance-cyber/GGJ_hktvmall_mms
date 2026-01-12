'use client'

import { CyberNavbar } from '@/components/ui/CyberNavbar'
import { motion } from 'framer-motion'
import { Sparkles, Zap, TrendingUp } from 'lucide-react'

/**
 * 全息賽博朋克導航欄示範頁面
 * Holographic Cyberpunk Navbar Demo Page
 */
export default function CyberDemoPage() {
  return (
    <>
      {/* 導入樣式 */}
      <link rel="stylesheet" href="/styles/cyber-navbar.css" />

      {/* 導航欄 */}
      <CyberNavbar />

      {/* 示範內容 */}
      <main className="min-h-screen pt-24 pb-16 px-4 bg-slate-950">
        {/* 背景效果 */}
        <div className="fixed inset-0 -z-10">
          <div className="absolute inset-0 cyber-grid opacity-10" />
          <div className="absolute inset-0 bg-gradient-radial from-cyan-500/5 via-transparent to-transparent" />
        </div>

        <div className="max-w-7xl mx-auto space-y-12">
          {/* Hero Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center space-y-6"
          >
            <h1 className="text-6xl md:text-8xl font-bold font-orbitron">
              <span className="neon-text">NEXUS</span>
            </h1>
            <p className="text-xl text-slate-400 font-rajdhani tracking-wide max-w-2xl mx-auto">
              Next-generation holographic interface system powered by advanced quantum computing
            </p>
          </motion.div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: Sparkles,
                title: 'Holographic UI',
                description: 'Immersive 3D interface with real-time rendering',
              },
              {
                icon: Zap,
                title: 'Quantum Speed',
                description: 'Ultra-fast processing with zero latency',
              },
              {
                icon: TrendingUp,
                title: 'AI Analytics',
                description: 'Predictive insights powered by neural networks',
              },
            ].map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + i * 0.1 }}
                className="holographic-border rounded-xl p-6 hover:bg-cyan-500/5 transition-colors group"
              >
                <feature.icon className="w-12 h-12 text-cyan-400 mb-4 group-hover:scale-110 transition-transform" />
                <h3 className="text-xl font-bold text-white mb-2 font-rajdhani">
                  {feature.title}
                </h3>
                <p className="text-slate-400 font-rajdhani">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>

          {/* Demo Section */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="holographic-border rounded-2xl p-8 space-y-4"
          >
            <h2 className="text-3xl font-bold text-cyan-400 font-orbitron mb-6">
              SYSTEM STATUS
            </h2>

            {/* Status Bars */}
            <div className="space-y-4">
              {[
                { label: 'NEURAL NETWORK', value: 94 },
                { label: 'QUANTUM CORE', value: 87 },
                { label: 'HOLOGRAPHIC ENGINE', value: 100 },
              ].map((stat) => (
                <div key={stat.label} className="space-y-2">
                  <div className="flex justify-between text-sm font-rajdhani">
                    <span className="text-slate-400">{stat.label}</span>
                    <span className="text-cyan-400">{stat.value}%</span>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${stat.value}%` }}
                      transition={{ duration: 1, delay: 0.5 }}
                      className="h-full bg-gradient-to-r from-cyan-500 to-purple-600 rounded-full"
                      style={{
                        boxShadow: '0 0 10px rgba(0, 240, 255, 0.5)',
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Documentation Link */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="text-center"
          >
            <a
              href="#docs"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-rajdhani font-medium hover:shadow-lg hover:shadow-cyan-500/30 transition-shadow"
            >
              <Sparkles className="w-4 h-4" />
              VIEW DOCUMENTATION
            </a>
          </motion.div>
        </div>
      </main>
    </>
  )
}
