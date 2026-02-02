# Change: Add Human-in-the-Loop Pricing Approval UI

**Status**: `applied` ✅

## Why

GoGoJap 的核心商業約束是「改價必須人工審批」(Human-in-the-Loop)。後端已完整實現審批 API，但前端缺少審批界面，導致：

- AI 生成的改價提案無法被經理查看和審批
- 無法追蹤誰批准了什麼改動
- RaaS 價值無法量化展示給客戶

## What Changes

### Backend
- **無變更** - 後端 API 已完整 (`/pricing/proposals/pending`, `/approve`, `/reject`)

### Frontend (新增)
- **NEW** `frontend/src/lib/api/pricing.ts` - API 客戶端
- **NEW** `frontend/src/app/pricing-approval/page.tsx` - 審批頁面
- **NEW** `frontend/src/app/pricing-approval/hooks/usePricingApproval.ts` - React Query hooks
- **NEW** `frontend/src/app/pricing-approval/components/` - 4 個 UI 組件
- **MODIFIED** `frontend/src/components/Sidebar.tsx` - 添加導航入口

## Impact

- **Affected specs**: `pricing-approval` (新增)
- **Affected code**:
  - `backend/app/api/v1/pricing.py` (讀取，無修改)
  - `backend/app/services/pricing_service.py` (讀取，無修改)
  - `frontend/src/components/Sidebar.tsx` (添加導航)
- **Breaking changes**: 無
- **Dependencies**: 無新增外部依賴

## Scope

此變更僅涉及前端 UI 層，利用現有後端 API。核心功能：

1. 顯示待審批的改價提案列表
2. 單個/批量批准或拒絕提案
3. 查看 AI 改價理由
4. 觸發 AI 重新分析
