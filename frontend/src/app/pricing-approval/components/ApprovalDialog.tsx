// =============================================
// Approval Confirmation Dialog
// =============================================

'use client'

import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { HoloButton } from '@/components/ui/future-tech'
import { ArrowRight, Check, X } from 'lucide-react'
import type { PriceProposal } from '@/lib/api/pricing'
import { calculatePriceChangePercent } from '@/lib/api/pricing'

interface ApprovalDialogProps {
  proposal: PriceProposal | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: (finalPrice?: number) => void
  isLoading?: boolean
}

export function ApprovalDialog({
  proposal,
  open,
  onOpenChange,
  onConfirm,
  isLoading,
}: ApprovalDialogProps) {
  const [finalPrice, setFinalPrice] = useState<string>('')
  const [useCustomPrice, setUseCustomPrice] = useState(false)

  // Reset state
  useEffect(() => {
    if (open && proposal) {
      setFinalPrice(proposal.proposed_price.toString())
      setUseCustomPrice(false)
    }
  }, [open, proposal])

  if (!proposal) return null

  const formatPrice = (price: number) => {
    return `$${price.toLocaleString('zh-HK', { minimumFractionDigits: 0 })}`
  }

  const priceChange = calculatePriceChangePercent(
    proposal.current_price,
    proposal.proposed_price
  )

  const handleConfirm = () => {
    if (useCustomPrice && finalPrice) {
      onConfirm(parseFloat(finalPrice))
    } else {
      onConfirm()
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Confirm Price Change Approval</DialogTitle>
          <DialogDescription>
            Please confirm the following pricing proposal. Once approved, HKTVmall prices will be automatically updated.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Product Info */}
          <div>
            <Label className="text-gray-500">Product</Label>
            <p className="font-medium">{proposal.product_name || 'Unknown Product'}</p>
            {proposal.product_sku && (
              <p className="text-sm text-gray-500">SKU: {proposal.product_sku}</p>
            )}
          </div>

          {/* Price Change */}
          <div>
            <Label className="text-gray-500">Price Change</Label>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-lg font-semibold text-gray-700">
                {formatPrice(proposal.current_price)}
              </span>
              <ArrowRight className="w-4 h-4 text-gray-400" />
              <span className="text-lg font-semibold text-gray-900">
                {formatPrice(proposal.proposed_price)}
              </span>
              <span
                className={`px-2 py-0.5 rounded-full text-sm font-medium ${
                  priceChange < 0
                    ? 'bg-green-100 text-green-600'
                    : 'bg-red-100 text-red-600'
                }`}
              >
                {priceChange >= 0 ? '+' : ''}{priceChange.toFixed(1)}%
              </span>
            </div>
          </div>

          {/* AI Reasoning */}
          {proposal.reason && (
            <div>
              <Label className="text-gray-500">AI Suggestion Rationale</Label>
              <p className="text-sm mt-1">{proposal.reason}</p>
            </div>
          )}

          {/* Custom Price */}
          <div className="pt-2 border-t">
            <div className="flex items-center gap-2 mb-2">
              <input
                type="checkbox"
                id="useCustomPrice"
                checked={useCustomPrice}
                onChange={(e) => setUseCustomPrice(e.target.checked)}
                className="rounded border-gray-300"
              />
              <Label htmlFor="useCustomPrice" className="cursor-pointer">
                Use custom final price
              </Label>
            </div>

            {useCustomPrice && (
              <div className="mt-2">
                <Label htmlFor="finalPrice">Final Execution Price</Label>
                <Input
                  id="finalPrice"
                  type="number"
                  step="0.01"
                  value={finalPrice}
                  onChange={(e) => setFinalPrice(e.target.value)}
                  placeholder="Enter final price"
                  className="mt-1"
                />
              </div>
            )}
          </div>
        </div>

        <DialogFooter className="gap-2">
          <HoloButton
            variant="secondary"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
          >
            <X className="w-4 h-4 mr-1" />
            Cancel
          </HoloButton>
          <HoloButton
            variant="primary"
            onClick={handleConfirm}
            disabled={isLoading}
            className="bg-green-500 hover:bg-green-600 text-white"
          >
            <Check className="w-4 h-4 mr-1" />
            {isLoading ? 'Processing...' : 'Confirm Approval'}
          </HoloButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
