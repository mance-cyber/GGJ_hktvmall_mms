import { useState } from 'react';
import { Sidebar } from './Sidebar';
import { StatsGrid } from './StatsGrid';
import { QuickActions } from './QuickActions';
import { CompetitorMonitoring } from './CompetitorMonitoring';
import { RecentAlerts } from './RecentAlerts';
import { Bell, Settings, Sparkles } from 'lucide-react';

export function Dashboard() {
  return (
    <div className="flex min-h-screen relative overflow-hidden">
      {/* Animated background */}
      <div className="fixed inset-0 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 pointer-events-none">
        <div className="absolute inset-0 opacity-40">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-300/30 rounded-full blur-[120px] animate-pulse"></div>
          <div className="absolute bottom-1/3 right-1/4 w-96 h-96 bg-cyan-300/30 rounded-full blur-[120px] animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 right-1/3 w-64 h-64 bg-pink-300/30 rounded-full blur-[100px] animate-pulse delay-500"></div>
        </div>
        {/* Grid pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(99,102,241,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(99,102,241,0.05)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
        
        {/* Floating particles */}
        <div className="absolute top-20 left-20 w-2 h-2 bg-purple-400 rounded-full animate-float opacity-60"></div>
        <div className="absolute top-40 right-40 w-1.5 h-1.5 bg-cyan-400 rounded-full animate-float-delayed opacity-60"></div>
        <div className="absolute bottom-32 left-1/3 w-2 h-2 bg-pink-400 rounded-full animate-float-slow opacity-60"></div>
        <div className="absolute top-1/3 right-1/4 w-1 h-1 bg-purple-400 rounded-full animate-float opacity-60"></div>
        <div className="absolute bottom-1/4 right-1/3 w-1.5 h-1.5 bg-cyan-400 rounded-full animate-float-delayed opacity-60"></div>
      </div>

      <Sidebar />
      
      <main className="flex-1 relative z-10 p-8 ml-72">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-4xl font-light text-gray-900 relative">
                歡迎回來 👋
                <div className="absolute -bottom-1 left-0 h-0.5 w-32 bg-gradient-to-r from-purple-500 via-cyan-500 to-transparent"></div>
              </h1>
              <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-gradient-to-r from-purple-100 to-cyan-100 border border-purple-300/50">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.6)]"></div>
                <span className="text-xs font-medium text-gray-700">在線</span>
              </div>
            </div>
            <p className="text-gray-600 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-500" />
              2025年1月9日星期五
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <button className="relative p-3 rounded-xl bg-white/60 border border-purple-200/50 backdrop-blur-xl hover:bg-white/80 transition-all hover:border-purple-400 hover:shadow-[0_0_20px_rgba(168,85,247,0.3)] group">
              <Bell className="w-5 h-5 text-gray-600 group-hover:text-purple-600 transition-colors" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-purple-500 rounded-full animate-ping"></span>
              <span className="absolute top-1 right-1 w-2 h-2 bg-purple-500 rounded-full shadow-[0_0_8px_rgba(168,85,247,0.6)]"></span>
              {/* Scan line */}
              <div className="absolute inset-0 rounded-xl overflow-hidden opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-purple-400 to-transparent animate-scan-vertical"></div>
              </div>
            </button>
            
            <button className="relative px-6 py-3 rounded-xl bg-gradient-to-r from-purple-500 to-cyan-500 text-white font-medium hover:shadow-[0_8px_30px_rgba(168,85,247,0.4)] transition-all duration-300 hover:scale-105 overflow-hidden group">
              <span className="relative z-10">新增專案</span>
              {/* Animated shine */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700"></div>
              {/* Holographic edge */}
              <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-purple-400/0 via-white/20 to-cyan-400/0 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </button>
          </div>
        </div>

        <StatsGrid />
        <QuickActions />
        
        {/* Competitor Monitoring and Recent Alerts Grid */}
        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-2">
            <CompetitorMonitoring />
          </div>
          <div className="col-span-1">
            <RecentAlerts />
          </div>
        </div>
      </main>
    </div>
  );
}