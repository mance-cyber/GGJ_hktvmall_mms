import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Check, X, ArrowRight, AlertCircle, Loader2 } from 'lucide-react'
import { format } from 'date-fns'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { pricingApi, PriceProposal } from '@/lib/api'
import { useToast } from '@/components/ui/use-toast'

interface ProposalListProps {
  proposals: PriceProposal[]
  onUpdate: () => void
}

export function PricingProposalList({ proposals, onUpdate }: ProposalListProps) {
  if (proposals.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center bg-slate-50 rounded-lg border border-dashed border-slate-200">
        <div className="p-3 bg-white rounded-full shadow-sm mb-3">
          <Check className="w-6 h-6 text-green-500" />
        </div>
        <h3 className="font-medium text-slate-900">暫無待辦事項</h3>
        <p className="text-sm text-slate-500 mt-1">所有 AI 改價建議都已處理完畢</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <AnimatePresence mode="popLayout">
        {proposals.map((proposal) => (
          <ProposalItem key={proposal.id} proposal={proposal} onUpdate={onUpdate} />
        ))}
      </AnimatePresence>
    </div>
  )
}

function ProposalItem({ proposal, onUpdate }: { proposal: PriceProposal; onUpdate: () => void }) {
  const [isProcessing, setIsProcessing] = useState(false)
  const { toast } = useToast()

  const handleAction = async (action: 'approve' | 'reject') => {
    setIsProcessing(true)
    try {
      if (action === 'approve') {
        await pricingApi.approveProposal(proposal.id)
        toast({
          title: "已批准改價",
          description: `成功將 ${proposal.product_name || '商品'} 價格更新為 $${proposal.proposed_price}`,
          variant: "default",
        })
      } else {
        await pricingApi.rejectProposal(proposal.id)
        toast({
          title: "已拒絕建議",
          description: "已忽略該改價建議",
        })
      }
      onUpdate()
    } catch (error: any) {
      toast({
        title: "操作失敗",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setIsProcessing(false)
    }
  }

  // 計算價格變化百分比
  const priceDiff = (proposal.proposed_price || 0) - (proposal.current_price || 0)
  const percentChange = proposal.current_price 
    ? ((priceDiff / proposal.current_price) * 100).toFixed(1)
    : '0'
  
  const isPriceUp = priceDiff > 0

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="bg-white border rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow"
    >
      <div className="flex flex-col gap-4">
        {/* Header */}
        <div className="flex justify-between items-start">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-semibold text-slate-900 line-clamp-1">{proposal.product_name || '未命名商品'}</h4>
              <Badge variant="outline" className="font-mono text-xs text-slate-500">
                {proposal.product_sku}
              </Badge>
            </div>
            <p className="text-sm text-slate-500 line-clamp-2">{proposal.reason}</p>
          </div>
          <Badge className={isPriceUp ? "bg-red-100 text-red-700 hover:bg-red-100" : "bg-green-100 text-green-700 hover:bg-green-100"}>
            {isPriceUp ? '+' : ''}{percentChange}%
          </Badge>
        </div>

        {/* Price Change Visualization */}
        <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
          <div className="flex-1">
            <p className="text-xs text-slate-500 mb-1">目前價格</p>
            <p className="font-mono font-semibold text-slate-700 line-through decoration-slate-400 decoration-2">
              ${proposal.current_price}
            </p>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-400" />
          <div className="flex-1 text-right">
            <p className="text-xs text-slate-500 mb-1">建議價格</p>
            <p className="font-mono font-bold text-lg text-primary">
              ${proposal.proposed_price}
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2 justify-end pt-2 border-t border-slate-100">
          <Button
            size="sm"
            variant="ghost"
            className="text-slate-500 hover:text-slate-700 hover:bg-slate-100"
            onClick={() => handleAction('reject')}
            disabled={isProcessing}
          >
            {isProcessing ? <Loader2 className="w-4 h-4 animate-spin" /> : <X className="w-4 h-4 mr-1" />}
            拒絕
          </Button>
          <Button
            size="sm"
            className="bg-primary hover:bg-primary/90"
            onClick={() => handleAction('approve')}
            disabled={isProcessing}
          >
            {isProcessing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4 mr-1" />}
            批准執行
          </Button>
        </div>
      </div>
    </motion.div>
  )
}
