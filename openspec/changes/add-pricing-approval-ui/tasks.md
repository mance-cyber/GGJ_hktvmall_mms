# Tasks: Add Pricing Approval UI

## 1. API Client

- [x] 1.1 Create `frontend/src/lib/api/pricing.ts`:
  - Type definitions (PriceProposal, ProposalStatus)
  - `getPendingProposals()` - GET /pricing/proposals/pending
  - `approveProposal(id)` - POST /pricing/proposals/{id}/approve
  - `rejectProposal(id)` - POST /pricing/proposals/{id}/reject
  - `triggerAIAnalysis()` - POST /pricing/analyze

## 2. React Query Hooks

- [x] 2.1 Create `frontend/src/app/pricing-approval/hooks/usePricingApproval.ts`:
  - `usePendingProposals()` - query hook
  - `useApproveProposal()` - mutation with cache invalidation
  - `useRejectProposal()` - mutation with cache invalidation
  - `useTriggerAIAnalysis()` - mutation with cache invalidation
  - `useBatchApprove()` - batch mutation
  - `useBatchReject()` - batch mutation

## 3. UI Components

- [x] 3.1 Create `ProposalCard.tsx`:
  - Checkbox for selection
  - Product name + SKU display
  - Price change visualization (current → proposed, with %)
  - AI reason display
  - Relative timestamp
  - Approve/Reject buttons

- [x] 3.2 Create `ProposalList.tsx`:
  - Map proposals to ProposalCard
  - Select all checkbox
  - Selected count display
  - Batch approve/reject buttons
  - Empty state handling

- [x] 3.3 Create `ProposalStats.tsx`:
  - 4 stat cards (Pending, Approved, Rejected, Failed)
  - Use HoloCard style from ROI dashboard

- [x] 3.4 Create `ApprovalDialog.tsx`:
  - Dialog/AlertDialog wrapper
  - Proposal details display
  - Optional final_price input
  - Confirm/Cancel buttons

## 4. Main Page

- [x] 4.1 Create `frontend/src/app/pricing-approval/page.tsx`:
  - Page header with title
  - AI Analysis trigger button
  - ProposalStats component
  - ProposalList component
  - Selection state management (Set<string>)
  - Toast notifications for actions

## 5. Navigation

- [x] 5.1 Update `frontend/src/components/Sidebar.tsx`:
  - Add "改價審批" entry in "商品管理" group
  - Icon: ClipboardCheck from lucide-react
  - href: /pricing-approval

## 6. Validation

- [x] 6.1 Verify frontend build: `npm run build` (構建成功)
- [ ] 6.2 Manual test: View pending proposals
- [ ] 6.3 Manual test: Approve single proposal
- [ ] 6.4 Manual test: Reject single proposal
- [ ] 6.5 Manual test: Batch operations
- [ ] 6.6 Manual test: Trigger AI analysis

## Dependencies

- Task 1.1 must complete before Task 2.1
- Task 2.1 must complete before Tasks 3.x and 4.1
- Tasks 3.x can run in parallel
- Task 4.1 requires Tasks 2.1 and 3.x complete
- Task 5.1 can run in parallel with other tasks
- Task 6.x requires all previous tasks complete

## Notes

- Backend API already exists and is fully functional
- No database migrations required
- Follow existing patterns from alerts page for batch selection
- Follow ROI dashboard patterns for HoloCard styling

## Completed Files

### New Files
- `frontend/src/lib/api/pricing.ts` - API 客戶端
- `frontend/src/components/ui/checkbox.tsx` - Checkbox 組件 (shadcn/ui)
- `frontend/src/app/pricing-approval/hooks/usePricingApproval.ts` - React Query Hooks
- `frontend/src/app/pricing-approval/components/ProposalCard.tsx` - 提案卡片
- `frontend/src/app/pricing-approval/components/ProposalList.tsx` - 提案列表
- `frontend/src/app/pricing-approval/components/ProposalStats.tsx` - 統計卡片
- `frontend/src/app/pricing-approval/components/ApprovalDialog.tsx` - 批准對話框
- `frontend/src/app/pricing-approval/page.tsx` - 主頁面

### Modified Files
- `frontend/src/components/Sidebar.tsx` - 添加導航入口
