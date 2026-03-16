// =============================================
// Individual Proposal Card Component
// =============================================

'use client'

import { Check, X, ArrowRight, Bot, AlertTriangle, User, MessageSquare } from 'lucide-react'
import { useLocale } from '@/components/providers/locale-provider'
import Link from 'next/link'
import { HoloCard, HoloBadge, HoloButton } from '@/components/ui/future-tech'
import { Checkbox } from '@/components/ui/checkbox'
import type { PriceProposal, SourceType } from '@/lib/api/pricing'
import { calculatePriceChangePercent } from '@/lib/api/pricing'

// =============================================
// Source Type Badge
// =============================================

interface SourceBadgeProps {
  sourceType: SourceType
  conversationId?: string | null
}

function SourceBadge({ sourceType, conversationId }: SourceBadgeProps) {
  const { t } = useLocale()

  const config: Record<SourceType, { label: string; icon: React.ReactNode; variant: 'default' | 'info' | 'warning' }> = {
    manual: {
      label: t('pricing.card.source_manual'),
      icon: <User className="w-3 h-3" />,
      variant: 'info',
    },
    ai_suggestion: {
      label: t('pricing.card.source_ai'),
      icon: <Bot className="w-3 h-3" />,
      variant: 'default',
    },
    auto_alert: {
      label: t('pricing.card.source_alert'),
      icon: <AlertTriangle className="w-3 h-3" />,
      variant: 'warning',
    },
  }

  const { label, icon, variant } = config[sourceType] || config.manual

  return (
    <HoloBadge variant={variant} size="sm" className="flex items-center gap-1">
      {icon}
      {label}
    </HoloBadge>
  )
}

// =============================================
// Conversation Link Component
// =============================================

interface ConversationLinkProps {
  conversationId: string
}

function ConversationLink({ conversationId }: ConversationLinkProps) {
  const { t } = useLocale()

  return (
    <Link
      href={`/agent?conversation=${conversationId}`}
      className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 hover:underline"
    >
      <MessageSquare className="w-3 h-3" />
      {t('pricing.card.view_conversation')}
    </Link>
  )
}

interface ProposalCardProps {
  proposal: PriceProposal
  isSelected: boolean
  onSelect: (id: string) => void
  onApprove: (id: string) => void
  onReject: (id: string) => void
  isApproving?: boolean
  isRejecting?: boolean
}

export function ProposalCard({
  proposal,
  isSelected,
  onSelect,
  onApprove,
  onReject,
  isApproving,
  isRejecting,
}: ProposalCardProps) {
  const { t } = useLocale()

  const priceChange = calculatePriceChangePercent(
    proposal.current_price,
    proposal.proposed_price
  )
  const isDecrease = priceChange < 0
  const changeColor = isDecrease ? 'text-green-600' : 'text-red-600'
  const changeBg = isDecrease ? 'bg-green-100' : 'bg-red-100'

  // Format relative time
  const formatRelativeTime = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / (1000 * 60))
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

    if (diffMins < 60) return t('pricing.card.min_ago', { n: diffMins })
    if (diffHours < 24) return t('pricing.card.hr_ago', { n: diffHours })
    return t('pricing.card.days_ago', { n: diffDays })
  }

  // Format price
  const formatPrice = (price: number) => {
    return `$${price.toLocaleString('zh-HK', { minimumFractionDigits: 0 })}`
  }

  return (
    <HoloCard className="p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-4">
        {/* Checkbox */}
        <div className="pt-1">
          <Checkbox
            checked={isSelected}
            onCheckedChange={() => onSelect(proposal.id)}
          />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {/* Product Info */}
          <div className="flex items-center gap-2 mb-2">
            <h3 className="font-medium text-gray-900 truncate">
              {proposal.product_name || t('pricing.dialog.unknown_product')}
            </h3>
            {proposal.product_sku && (
              <HoloBadge variant="default" size="sm">
                {proposal.product_sku}
              </HoloBadge>
            )}
            {/* Source Type Badge */}
            <SourceBadge
              sourceType={proposal.source_type || 'manual'}
              conversationId={proposal.source_conversation_id}
            />
          </div>

          {/* Price Change */}
          <div className="flex items-center gap-2 mb-3">
            <span className="text-lg font-semibold text-gray-700">
              {formatPrice(proposal.current_price)}
            </span>
            <ArrowRight className="w-4 h-4 text-gray-400" />
            <span className="text-lg font-semibold text-gray-900">
              {formatPrice(proposal.proposed_price)}
            </span>
            <span className={`px-2 py-0.5 rounded-full text-sm font-medium ${changeBg} ${changeColor}`}>
              {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(1)}%
            </span>
          </div>

          {/* AI Reasoning */}
          {proposal.reason && (
            <p className="text-sm text-gray-600 mb-2 line-clamp-2">
              {proposal.reason}
            </p>
          )}

          {/* Meta Info */}
          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span>{t('pricing.card.suggested_at', { time: formatRelativeTime(proposal.created_at) })}</span>
            {proposal.ai_model_used && (
              <span>{t('pricing.card.model', { model: proposal.ai_model_used })}</span>
            )}
            {/* Conversation Link */}
            {proposal.source_conversation_id && (
              <ConversationLink conversationId={proposal.source_conversation_id} />
            )}
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <HoloButton
            variant="primary"
            size="sm"
            onClick={() => onApprove(proposal.id)}
            disabled={isApproving || isRejecting}
            className="bg-green-500 hover:bg-green-600 text-white"
          >
            <Check className="w-4 h-4 mr-1" />
            {t('pricing.card.approve')}
          </HoloButton>
          <HoloButton
            variant="secondary"
            size="sm"
            onClick={() => onReject(proposal.id)}
            disabled={isApproving || isRejecting}
            className="hover:bg-red-50 hover:text-red-600 hover:border-red-200"
          >
            <X className="w-4 h-4 mr-1" />
            {t('pricing.card.reject')}
          </HoloButton>
        </div>
      </div>
    </HoloCard>
  )
}
