# Design: Human-in-the-Loop Pricing Approval UI

## Overview

建立前端審批界面，讓經理可以審核 AI 建議的價格變動。利用現有後端 API，無需後端改動。

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (新增)                          │
├─────────────────────────────────────────────────────────────┤
│  pricing.ts (API Client)                                     │
│       ↓                                                      │
│  usePricingApproval.ts (React Query Hooks)                  │
│       ↓                                                      │
│  page.tsx ← ProposalList ← ProposalCard                     │
│           ← ProposalStats                                    │
│           ← ApprovalDialog                                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ↓ HTTP
┌─────────────────────────────────────────────────────────────┐
│                     Backend (現有)                           │
├─────────────────────────────────────────────────────────────┤
│  GET  /api/v1/pricing/proposals/pending                     │
│  POST /api/v1/pricing/proposals/{id}/approve                │
│  POST /api/v1/pricing/proposals/{id}/reject                 │
│  POST /api/v1/pricing/analyze                               │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. 獲取待審批提案

```
usePendingProposals()
  → GET /pricing/proposals/pending
  → 返回 PriceProposal[] (含 product_name, product_sku)
  → ProposalList 渲染
```

### 2. 批准提案

```
用戶點擊「批准」
  → ApprovalDialog 打開 (可選修改 final_price)
  → useApproveProposal.mutate(id, finalPrice?)
  → POST /pricing/proposals/{id}/approve
  → 後端執行 HKTVmall API 更新
  → 返回更新後的提案 (status: executed)
  → invalidateQueries(['pending-proposals'])
  → UI 自動刷新
```

### 3. 批量操作

```
用戶勾選多個提案 → selectedIds: Set<string>
  → 點擊「批量批准」
  → Promise.allSettled(ids.map(id => approveProposal(id)))
  → 顯示成功/失敗統計
  → invalidateQueries
```

## UI Design

### 頁面佈局

```
┌─────────────────────────────────────────────────────────────┐
│ 改價審批中心                            [觸發 AI 分析]       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ 待審批   │ │ 已批准   │ │ 已拒絕   │ │ 執行失敗 │       │
│  │   12     │ │   45     │ │    3     │ │    1     │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
├─────────────────────────────────────────────────────────────┤
│ ☐ 全選                                                      │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ☐ 日本零食禮盒 (SKU: JP-001)                           │ │
│ │   現價: $128 → 建議價: $119 (-7%)                       │ │
│ │   理由: 競品「松本清」降價至 $115，建議跟進             │ │
│ │   建議時間: 2 小時前                    [✓ 批准] [✗ 拒絕]│ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ ☐ 美妝套裝 (SKU: BT-002)                               │ │
│ │   ...                                                   │ │
│ └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ 已選 2 項           [批量批准] [批量拒絕]                   │
└─────────────────────────────────────────────────────────────┘
```

### 視覺風格

- 遵循 Future Tech 設計系統
- 使用 HoloCard 容器
- 價格變化使用顏色標識：
  - 降價：綠色 (text-green-500)
  - 漲價：紅色 (text-red-500)
- 批准按鈕：綠色
- 拒絕按鈕：灰色/紅色

## Component Design

### 1. pricing.ts (API Client)

```typescript
// Types
interface PriceProposal {
  id: string
  product_id: string
  product_name: string | null
  product_sku: string | null
  current_price: number
  proposed_price: number
  final_price: number | null
  reason: string | null
  status: 'pending' | 'approved' | 'rejected' | 'executed' | 'failed'
  ai_model_used: string | null
  created_at: string
}

// Functions
getPendingProposals(): Promise<PriceProposal[]>
approveProposal(id: string): Promise<PriceProposal>
rejectProposal(id: string): Promise<PriceProposal>
triggerAIAnalysis(): Promise<{ status: string; generated_proposals: number }>
```

### 2. usePricingApproval.ts (Hooks)

```typescript
// Query
usePendingProposals() → useQuery(['pending-proposals'], getPendingProposals)

// Mutations
useApproveProposal() → useMutation(approveProposal, { onSuccess: invalidate })
useRejectProposal() → useMutation(rejectProposal, { onSuccess: invalidate })
useTriggerAIAnalysis() → useMutation(triggerAIAnalysis, { onSuccess: invalidate })
```

### 3. ProposalCard.tsx

Props:
- proposal: PriceProposal
- isSelected: boolean
- onSelect: (id: string) => void
- onApprove: (id: string) => void
- onReject: (id: string) => void

顯示：
- Checkbox
- 產品名稱 + SKU
- 價格變化（現價 → 建議價，含百分比）
- AI 理由
- 創建時間 (相對時間)
- 操作按鈕

### 4. ApprovalDialog.tsx

Props:
- proposal: PriceProposal | null
- open: boolean
- onOpenChange: (open: boolean) => void
- onConfirm: (finalPrice?: number) => void

功能：
- 顯示提案詳情
- 允許修改最終價格 (final_price)
- 確認批准

## Error Handling

1. **API 錯誤**：Toast 提示，保留當前狀態
2. **批量操作部分失敗**：顯示成功/失敗數量統計
3. **空狀態**：顯示「暫無待審批提案」+ 觸發分析按鈕

## Performance

- 使用 React Query 的 staleTime 避免重複請求
- 批量操作使用 Promise.allSettled 並行處理
- 列表虛擬化（如超過 50 項）

## Security

- 依賴後端 JWT 認證
- 前端不存儲敏感數據
- 審計日誌由後端記錄
