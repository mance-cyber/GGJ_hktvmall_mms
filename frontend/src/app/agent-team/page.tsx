'use client'

// =============================================
// Agent Team Dashboard
// =============================================

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Bot,
  Power,
  PowerOff,
  Activity,
  Clock,
  RefreshCw,
  Loader2,
  Shield,
  Eye,
  DollarSign,
  FileText,
  Package,
  BarChart3,
  Zap,
  AlertTriangle,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { PageTransition, HoloCard } from '@/components/ui/future-tech'
import { apiClient } from '@/lib/api/client'

// =============================================
// Types
// =============================================

interface AgentInfo {
  name: string
  description: string
  enabled: boolean
  subscriptions: string[]
  rules?: Record<string, number>
  schedule?: Record<string, string[]>
  is_quiet_hours?: boolean
  low_stock_threshold?: number
  significant_drop_percent?: number
  promo_calendar?: Record<string, string>
}

interface EventLog {
  id: string
  type: string
  source: string
  payload_keys: string[]
  timestamp: string
}

interface TeamStatus {
  agents: AgentInfo[]
  event_bus: {
    handler_map: Record<string, string[]>
    recent_events: EventLog[]
  }
}

// =============================================
// Agent 圖標映射
// =============================================

const AGENT_ICONS: Record<string, typeof Bot> = {
  commander: Shield,
  scout: Eye,
  pricer: DollarSign,
  writer: FileText,
  ops: Package,
  strategist: BarChart3,
}

const AGENT_COLORS: Record<string, string> = {
  commander: 'from-blue-500 to-indigo-500',
  scout: 'from-emerald-500 to-teal-500',
  pricer: 'from-amber-500 to-orange-500',
  writer: 'from-purple-500 to-pink-500',
  ops: 'from-cyan-500 to-blue-500',
  strategist: 'from-rose-500 to-red-500',
}

// =============================================
// Agent Card
// =============================================

function AgentCard({
  agent,
  onToggle,
  isToggling,
}: {
  agent: AgentInfo
  onToggle: (name: string, enable: boolean) => void
  isToggling: boolean
}) {
  const Icon = AGENT_ICONS[agent.name] || Bot
  const gradient = AGENT_COLORS[agent.name] || 'from-slate-500 to-slate-600'

  return (
    <HoloCard className="p-5">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={cn(
            'w-10 h-10 rounded-lg bg-gradient-to-br flex items-center justify-center',
            gradient
          )}>
            <Icon className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-800">{agent.name}</h3>
            <p className="text-xs text-slate-500">{agent.description}</p>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          disabled={isToggling}
          onClick={() => onToggle(agent.name, !agent.enabled)}
          className={cn(
            'h-8 px-2',
            agent.enabled
              ? 'text-emerald-600 hover:text-emerald-700'
              : 'text-slate-400 hover:text-slate-600'
          )}
        >
          {isToggling ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : agent.enabled ? (
            <Power className="w-4 h-4" />
          ) : (
            <PowerOff className="w-4 h-4" />
          )}
        </Button>
      </div>

      {/* 狀態標籤 */}
      <div className="flex items-center gap-2 mb-3">
        <Badge variant={agent.enabled ? 'default' : 'secondary'} className={cn(
          'text-xs',
          agent.enabled
            ? 'bg-emerald-100 text-emerald-700 border-emerald-200'
            : 'bg-slate-100 text-slate-500'
        )}>
          {agent.enabled ? '運行中' : '已停用'}
        </Badge>
        {agent.is_quiet_hours && (
          <Badge variant="outline" className="text-xs text-amber-600 border-amber-200">
            靜默時段
          </Badge>
        )}
      </div>

      {/* 訂閱的事件 */}
      <div className="space-y-1">
        <span className="text-xs text-slate-400">訂閱事件:</span>
        <div className="flex flex-wrap gap-1">
          {agent.subscriptions.map(sub => (
            <span key={sub} className="text-xs px-2 py-0.5 bg-slate-100 rounded-full text-slate-600">
              {sub}
            </span>
          ))}
        </div>
      </div>

      {/* 擴展信息 */}
      {agent.rules && (
        <div className="mt-3 pt-3 border-t border-slate-100">
          <span className="text-xs text-slate-400">定價規則:</span>
          <div className="grid grid-cols-2 gap-1 mt-1">
            {Object.entries(agent.rules).map(([k, v]) => (
              <span key={k} className="text-xs text-slate-600">
                {k}: {typeof v === 'number' && v < 1 ? `${(v * 100).toFixed(0)}%` : v}
              </span>
            ))}
          </div>
        </div>
      )}

      {agent.schedule && (
        <div className="mt-3 pt-3 border-t border-slate-100">
          <span className="text-xs text-slate-400">排程:</span>
          <div className="space-y-1 mt-1">
            {Object.entries(agent.schedule).map(([time, events]) => (
              <div key={time} className="flex items-center gap-2 text-xs text-slate-600">
                <Clock className="w-3 h-3 text-slate-400" />
                <span className="font-mono">{time}</span>
                <span>{(events as string[]).join(', ')}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </HoloCard>
  )
}

// =============================================
// Event Log
// =============================================

function EventLogPanel({ events }: { events: EventLog[] }) {
  if (!events.length) {
    return (
      <div className="text-center py-8 text-slate-400">
        <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">尚無事件記錄</p>
      </div>
    )
  }

  return (
    <div className="space-y-1 max-h-96 overflow-y-auto">
      {events.map(event => (
        <div key={event.id} className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors">
          <Zap className={cn(
            'w-3.5 h-3.5 flex-shrink-0',
            event.type.includes('error') ? 'text-red-400' :
            event.type.includes('completed') ? 'text-emerald-400' :
            event.type.includes('escalation') ? 'text-amber-400' :
            'text-blue-400'
          )} />
          <div className="flex-1 min-w-0">
            <span className="text-xs font-mono text-slate-700 truncate block">
              {event.type}
            </span>
            <span className="text-xs text-slate-400">
              {event.source && `${event.source} \u00B7 `}
              {new Date(event.timestamp).toLocaleTimeString('zh-HK')}
            </span>
          </div>
          <span className="text-xs text-slate-300 font-mono">{event.id}</span>
        </div>
      ))}
    </div>
  )
}

// =============================================
// Main Page
// =============================================

export default function AgentTeamPage() {
  const queryClient = useQueryClient()
  const [togglingAgent, setTogglingAgent] = useState<string | null>(null)

  const { data, isLoading, error } = useQuery<TeamStatus>({
    queryKey: ['agent-team-status'],
    queryFn: () => apiClient.get('/agent-team/status'),
    refetchInterval: 10000,
  })

  const toggleMutation = useMutation({
    mutationFn: async ({ name, enable }: { name: string; enable: boolean }) => {
      setTogglingAgent(name)
      const action = enable ? 'enable' : 'disable'
      return apiClient.post(`/agent-team/${name}/${action}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['agent-team-status'] })
    },
    onSettled: () => {
      setTogglingAgent(null)
    },
  })

  const agents = data?.agents || []
  const events = data?.event_bus?.recent_events || []
  const handlerMap = data?.event_bus?.handler_map || {}

  const enabledCount = agents.filter(a => a.enabled).length
  const totalHandlers = Object.values(handlerMap).reduce(
    (sum, handlers) => sum + handlers.length, 0
  )

  return (
    <PageTransition className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 flex items-center gap-3">
            <Bot className="w-7 h-7 text-purple-500" />
            Agent Team
          </h1>
          <p className="text-slate-500 mt-1">
            6 Agent 協同運營 \u00B7 事件驅動架構
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => queryClient.invalidateQueries({ queryKey: ['agent-team-status'] })}
          disabled={isLoading}
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin mr-2" />
          ) : (
            <RefreshCw className="w-4 h-4 mr-2" />
          )}
          刷新
        </Button>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-3 gap-4">
        <HoloCard className="p-4 text-center">
          <div className="text-2xl font-bold text-emerald-600">{enabledCount}/{agents.length}</div>
          <div className="text-xs text-slate-500 mt-1">Agent 運行中</div>
        </HoloCard>
        <HoloCard className="p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">{totalHandlers}</div>
          <div className="text-xs text-slate-500 mt-1">事件處理器</div>
        </HoloCard>
        <HoloCard className="p-4 text-center">
          <div className="text-2xl font-bold text-purple-600">{events.length}</div>
          <div className="text-xs text-slate-500 mt-1">最近事件</div>
        </HoloCard>
      </div>

      {/* Error State */}
      {error && (
        <div className="flex items-center gap-2 p-4 bg-red-50 rounded-lg border border-red-200">
          <AlertTriangle className="w-5 h-5 text-red-500" />
          <span className="text-sm text-red-700">
            無法連接 Agent Team API: {(error as Error).message}
          </span>
        </div>
      )}

      {/* Agent Cards */}
      <div>
        <h2 className="text-lg font-semibold text-slate-700 mb-3">Agent 狀態</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map(agent => (
            <AgentCard
              key={agent.name}
              agent={agent}
              onToggle={(name, enable) =>
                toggleMutation.mutate({ name, enable })
              }
              isToggling={togglingAgent === agent.name}
            />
          ))}
        </div>
      </div>

      {/* Event Log */}
      <div>
        <h2 className="text-lg font-semibold text-slate-700 mb-3 flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-500" />
          事件日誌
        </h2>
        <HoloCard className="p-4">
          <EventLogPanel events={events} />
        </HoloCard>
      </div>

      {/* Handler Map */}
      {Object.keys(handlerMap).length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-slate-700 mb-3">事件訂閱圖</h2>
          <HoloCard className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {Object.entries(handlerMap).map(([eventType, handlers]) => (
                <div key={eventType} className="flex items-start gap-2">
                  <Zap className="w-3.5 h-3.5 text-blue-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="text-xs font-mono text-slate-700">{eventType}</span>
                    <div className="flex flex-wrap gap-1 mt-0.5">
                      {(handlers as string[]).map(h => (
                        <span key={h} className="text-xs px-1.5 py-0.5 bg-purple-50 text-purple-600 rounded">
                          {h}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </HoloCard>
        </div>
      )}
    </PageTransition>
  )
}
