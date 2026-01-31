# Change: Add ROI Dashboard for RaaS Transformation

**Status**: `applied` ✅

## Why
GoGoJap 正在轉型為 Result-as-a-Service (RaaS) 模式。目前系統缺乏向客戶展示「GoGoJap 幫你賺了多少錢」的功能，導致獲客成本高、價值難以量化。需要一個 ROI 儀表板來：
- 展示 AI 定價的實際貢獻
- 量化競品監測帶來的價值
- 計算整體投資回報率

## What Changes

### Backend
- **NEW** `backend/app/schemas/roi.py` - ROI 相關 Pydantic 模型
- **NEW** `backend/app/services/roi_service.py` - ROI 計算服務
- **NEW** `backend/app/api/v1/roi.py` - ROI API 端點
- **MODIFIED** `backend/app/api/v1/router.py` - 註冊新路由

### Frontend
- **NEW** `frontend/src/app/roi/page.tsx` - ROI 儀表板頁面
- **NEW** `frontend/src/app/roi/components/` - 5 個 UI 組件
- **NEW** `frontend/src/app/roi/hooks/useROIData.ts` - React Query hooks
- **NEW** `frontend/src/lib/api/roi.ts` - API 客戶端

### Database
- **NEW** 建議新增索引優化查詢性能（可選）

## Impact

- **Affected specs**: `roi-analytics` (新增)
- **Affected code**:
  - `backend/app/models/pricing.py` (讀取 PriceProposal)
  - `backend/app/models/finance.py` (讀取 Settlement)
  - `backend/app/models/competitor.py` (讀取 PriceAlert)
  - `frontend/src/components/ui/future-tech.tsx` (複用 UI 組件)
- **Breaking changes**: 無
- **Dependencies**: 無新增外部依賴
