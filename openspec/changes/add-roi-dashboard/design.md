# Design: ROI Dashboard

## Context

GoGoJap 需要向 HKTVmall 賣家展示平台創造的價值，以支持 RaaS 商業模式轉型。現有數據源包括：
- `price_proposals` - AI 改價提案記錄
- `order_items` - 訂單商品明細
- `price_alerts` - 競品價格告警
- `settlements` - HKTVmall 結算數據

## Goals / Non-Goals

### Goals
- 計算並展示 AI 定價帶來的額外收益
- 量化競品監測的價值
- 提供時間維度的 ROI 趨勢分析
- 遵循現有 Future Tech UI 設計風格

### Non-Goals
- 不實現多租戶隔離（留待後續）
- 不實現導出報告功能（Phase 2）
- 不新增外部 API 依賴

## Decisions

### 1. ROI 計算公式

**Decision**: 採用三維度計算模型

```
AI 定價貢獻 = SUM((final_price - current_price) × quantity)
             WHERE status = 'executed' AND final_price > current_price

競品監測價值 = COUNT(price_alerts) × AVG(change_percent) × avg_order_value
             WHERE alert_type IN ('price_drop', 'price_increase')

風險規避價值 = 基於警報響應率的估算值

總 ROI = (AI貢獻 + 監測價值 + 風險規避 - 服務成本) / 服務成本 × 100%
```

**Alternatives considered**:
- 僅計算實際訂單利潤差異 - 數據不完整，難以追蹤
- 使用 AB 測試對照組 - 實現複雜度過高

### 2. 數據聚合策略

**Decision**: 實時計算 + 5 分鐘緩存

**Rationale**: 數據量不大（<10K 提案），實時計算可接受。前端使用 TanStack Query 的 `staleTime: 5 * 60 * 1000` 緩存。

**Alternatives considered**:
- 預聚合表 + Celery 任務 - 過度工程，留待 Phase 2
- Redis 緩存 - 增加複雜度，暫不需要

### 3. 前端組件架構

**Decision**: 獨立頁面 + 專用組件

```
frontend/src/app/roi/
├── page.tsx                    # 主頁面
├── components/
│   ├── ROISummaryCards.tsx     # KPI 卡片組
│   ├── ROITrendChart.tsx       # 趨勢圖表
│   ├── TimeRangeSelector.tsx   # 時間選擇
│   ├── PricingImpactTable.tsx  # 改價明細
│   └── CompetitorValueCard.tsx # 競品價值
└── hooks/
    └── useROIData.ts           # 數據 hooks
```

**Rationale**: 遵循現有 feature-based 目錄結構（參考 `trends/`）

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| 計算邏輯可能不準確 | 提供詳細的計算說明，允許用戶理解數據來源 |
| 大數據量時性能下降 | 添加數據庫索引，預留預聚合升級路徑 |
| UI 與現有風格不一致 | 複用 `future-tech.tsx` 組件，遵循 HoloCard 設計 |

## Migration Plan

1. 後端 API 先行，不影響現有功能
2. 前端頁面獨立部署，通過導航菜單入口
3. 無數據庫 schema 變更，無遷移腳本需求

## Open Questions

- [ ] 服務成本如何定義？（月訂閱費 vs 按使用量）
- [ ] 是否需要支持自定義時間範圍？
- [ ] 是否需要導出 PDF/Excel 報告？
