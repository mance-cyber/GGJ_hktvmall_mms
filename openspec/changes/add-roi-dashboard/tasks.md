# Tasks: Add ROI Dashboard

## 1. Backend - Schema & Service

- [x] 1.1 Create `backend/app/schemas/roi.py` with Pydantic models:
  - `ROISummary` (total_value, ai_contribution, monitoring_value, roi_percentage)
  - `ROITrendPoint` (date, cumulative_value, ai_pricing, monitoring)
  - `PricingProposalImpact` (product_name, old_price, new_price, impact)
  - `CompetitorInsights` (alerts_triggered, price_drops, price_increases, savings)

- [x] 1.2 Create `backend/app/services/roi_service.py`:
  - `get_summary(start_date, end_date)` - 計算期間 ROI 總覽
  - `get_trends(days, granularity)` - 獲取 ROI 趨勢
  - `get_pricing_impact(limit)` - 分析 AI 改價影響
  - `get_competitor_insights(period)` - 競品監測價值

## 2. Backend - API Endpoints

- [x] 2.1 Create `backend/app/api/v1/roi.py`:
  - `GET /roi/summary?period=today|week|month`
  - `GET /roi/trends?days=30&granularity=day`
  - `GET /roi/pricing-impact?limit=10`
  - `GET /roi/competitor-insights?period=month`

- [x] 2.2 Register router in `backend/app/api/v1/router.py`

- [ ] 2.3 Write unit tests for ROI calculation logic

## 3. Frontend - API Client & Hooks

- [x] 3.1 Create `frontend/src/lib/api/roi.ts`:
  - `getROISummary(period)`
  - `getROITrends(days)`
  - `getPricingImpact(limit)`
  - `getCompetitorInsights(period)`

- [x] 3.2 Create `frontend/src/app/roi/hooks/useROIData.ts`:
  - `useROISummary(period)`
  - `useROITrends(days)`
  - `usePricingImpact()`
  - `useCompetitorInsights(period)`

## 4. Frontend - UI Components

- [x] 4.1 Create `ROISummaryCards.tsx` - 4 個 KPI 卡片
  - 總價值創造 (green)
  - AI 定價貢獻 (purple)
  - 競品監測價值 (cyan)
  - 投資回報率 (green)

- [x] 4.2 Create `ROITrendChart.tsx` - Recharts 折線圖
  - 使用現有 `PriceTrendChart.tsx` 風格
  - 支持多數據線顯示/隱藏

- [x] 4.3 Create `TimeRangeSelector.tsx` - 時間範圍切換
  - 今日 / 本週 / 本月 / 自定義

- [x] 4.4 Create `PricingImpactTable.tsx` - AI 改價明細表

- [x] 4.5 Create `CompetitorValueCard.tsx` - 競品監測價值展示

## 5. Frontend - Page Assembly

- [x] 5.1 Create `frontend/src/app/roi/page.tsx`:
  - 整合所有組件
  - 使用 HoloCard 容器
  - 遵循 Future Tech 設計風格

- [x] 5.2 Add navigation entry (sidebar link)

## 6. Testing & Validation

- [ ] 6.1 Backend: Test ROI calculation with mock data
- [x] 6.2 Frontend: Verify components render correctly (構建成功)
- [ ] 6.3 E2E: Test full flow from API to UI
- [ ] 6.4 Performance: Verify query execution time < 500ms

## Dependencies

- Task 1.x must complete before Task 2.x
- Task 3.x can run parallel with Task 2.x
- Task 4.x can run parallel with Task 3.x
- Task 5.x requires Task 3.x and 4.x complete
- Task 6.x requires all previous tasks complete

## Completed Files

### Backend
- `backend/app/schemas/roi.py` - Pydantic 模型
- `backend/app/services/roi_service.py` - ROI 計算服務
- `backend/app/api/v1/roi.py` - API 端點
- `backend/app/api/v1/router.py` - 路由註冊 (已修改)

### Frontend
- `frontend/src/lib/api/roi.ts` - API 客戶端
- `frontend/src/app/roi/hooks/useROIData.ts` - React Query Hooks
- `frontend/src/app/roi/components/ROISummaryCards.tsx` - KPI 卡片
- `frontend/src/app/roi/components/ROITrendChart.tsx` - 趨勢圖表
- `frontend/src/app/roi/components/TimeRangeSelector.tsx` - 時間選擇器
- `frontend/src/app/roi/components/PricingImpactTable.tsx` - 改價明細表
- `frontend/src/app/roi/components/CompetitorValueCard.tsx` - 競品價值卡片
- `frontend/src/app/roi/page.tsx` - 主頁面
