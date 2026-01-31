# GoGoJap ROI 儀表板實現計劃

## 目標
向香港本地電商賣家展示「GoGoJap 幫你賺了多少錢」，支持 RaaS 轉型。

---

## ROI 核心指標

| 指標 | 計算公式 | 數據來源 |
|-----|---------|---------|
| **AI 定價貢獻** | SUM(final_price - current_price) × quantity | `price_proposals` + `order_items` |
| **競品監測價值** | 價格差異 × 預估銷量 | `price_snapshots` + `products` |
| **風險規避價值** | 警報數 × 平均變化率 × 訂單均值 | `price_alerts` |
| **總 ROI** | (總價值 - 服務成本) / 服務成本 × 100% | 聚合計算 |

---

## 實現內容

### 後端 (3 個新文件)

1. **`backend/app/schemas/roi.py`** - Pydantic 模型
   - `ROISummary` - 總覽數據
   - `ROITrendPoint` - 趨勢點
   - `PricingProposalImpact` - 改價影響
   - `CompetitorInsights` - 競品價值

2. **`backend/app/services/roi_service.py`** - 核心服務
   - `get_summary()` - 期間 ROI 總覽
   - `get_trends()` - ROI 趨勢
   - `get_pricing_impact()` - AI 改價影響
   - `get_competitor_insights()` - 競品監測價值

3. **`backend/app/api/v1/roi.py`** - API 端點
   - `GET /api/v1/roi/summary?period=month`
   - `GET /api/v1/roi/trends?days=30`
   - `GET /api/v1/roi/pricing-impact`
   - `GET /api/v1/roi/competitor-insights`

### 前端 (1 個新頁面 + 5 個組件)

1. **`frontend/src/app/roi/page.tsx`** - 主頁面

2. **組件:**
   - `ROISummaryCards.tsx` - 4 個 KPI 卡片（總價值、AI貢獻、競品價值、ROI%）
   - `ROITrendChart.tsx` - Recharts 折線圖
   - `TimeRangeSelector.tsx` - 今日/本週/本月切換
   - `PricingImpactTable.tsx` - AI 改價明細表
   - `CompetitorValueCard.tsx` - 競品監測價值展示

3. **`frontend/src/app/roi/hooks/useROIData.ts`** - React Query hooks

4. **`frontend/src/lib/api/roi.ts`** - API 客戶端

---

## 關鍵文件

| 參考/修改 | 路徑 |
|----------|-----|
| 數據模型 | `backend/app/models/pricing.py` (PriceProposal) |
| 財務數據 | `backend/app/models/finance.py` (Settlement) |
| UI 組件庫 | `frontend/src/components/ui/future-tech.tsx` |
| 參考圖表 | `frontend/src/app/trends/components/PriceTrendChart.tsx` |
| 參考 KPI | `frontend/src/app/trends/components/TrendKPICards.tsx` |
| 路由註冊 | `backend/app/api/v1/router.py` |

---

## 視覺設計

- **主題:** Future Tech 風格（青色 #06b6d4 + 紫色 #8b5cf6）
- **容器:** HoloCard 毛玻璃效果
- **圖表:** Recharts 折線圖
- **動畫:** Framer Motion 數字計數器

---

## 驗證方式

1. 啟動後端: `cd backend && uvicorn app.main:app --reload`
2. 測試 API: `curl http://localhost:8000/api/v1/roi/summary?period=month`
3. 啟動前端: `cd frontend && npm run dev`
4. 訪問頁面: `http://localhost:3000/roi`
5. 確認 KPI 卡片顯示數據
6. 確認趨勢圖表正確渲染
