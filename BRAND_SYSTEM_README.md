# GoGoJap 品牌設計系統文檔索引

## 文檔結構

本專案的品牌設計系統包含以下核心文檔：

### 1. BRAND_GUIDELINES.md（完整品牌指南）
**路徑**: `e:\Mance\Mercury\Project\7. App dev\4. GoGoJap - HKTVmall AI system\BRAND_GUIDELINES.md`

**內容概要**:
- 品牌核心定位與個性
- 完整視覺識別系統（色彩、字型、間距、圓角、陰影、動畫）
- 組件風格指南（按鈕、卡片、表單、表格、徽章、圖表）
- 品牌語調指南
- 無障礙指南
- 品牌資產管理規範

**適用對象**: 設計師、產品經理、品牌管理者

---

### 2. DESIGN_TOKENS.md（設計 Token 快速參考）
**路徑**: `e:\Mance\Mercury\Project\7. App dev\4. GoGoJap - HKTVmall AI system\DESIGN_TOKENS.md`

**內容概要**:
- 所有設計 Token 的快速查閱表
- 色彩、字型、間距、圓角、陰影、動畫的具體數值
- 常用組合類別（按鈕、卡片、輸入框等）
- 快速複製範本
- 工具類別集合

**適用對象**: 前端開發者、設計師

---

### 3. COMPONENT_EXAMPLES.md（組件使用範例）
**路徑**: `e:\Mance\Mercury\Project\7. App dev\4. GoGoJap - HKTVmall AI system\COMPONENT_EXAMPLES.md`

**內容概要**:
- 所有 UI 組件的完整程式碼範例
- 按鈕、卡片、表單、表格、對話框、圖表等的實際用法
- 不同變體與狀態的示範
- 頁面佈局範例
- 最佳實踐建議

**適用對象**: 前端開發者

---

### 4. tailwind.config.ts（Tailwind 配置）
**路徑**: `e:\Mance\Mercury\Project\7. App dev\4. GoGoJap - HKTVmall AI system\tailwind.config.ts`

**內容概要**:
- 完整的 Tailwind CSS 擴展配置
- 所有品牌色彩、字型、間距等的 Token 定義
- 自訂動畫與工具類別
- 與 shadcn/ui 的完整整合

**適用對象**: 前端開發者

---

### 5. app/globals.css（全局樣式）
**路徑**: `e:\Mance\Mercury\Project\7. App dev\4. GoGoJap - HKTVmall AI system\app\globals.css`

**內容概要**:
- CSS 變數定義（亮色/暗色模式）
- 全局基礎樣式
- 自訂組件類別（stat-card, badge, trend-indicator 等）
- 工具類別（truncate-2-lines, text-gradient 等）
- 圖表樣式覆寫

**適用對象**: 前端開發者

---

### 6. lib/utils.ts（工具函數）
**路徑**: `e:\Mance\Mercury\Project\7. App dev\4. GoGoJap - HKTVmall AI system\lib\utils.ts`

**內容概要**:
- 數字格式化（貨幣、百分比、千分位）
- 日期格式化（相對時間）
- 字串處理（截斷、轉換）
- 價格計算與競爭力判斷
- 陣列處理（去重、分組）
- 驗證工具（Email、URL、電話）
- 防抖與節流函數
- 本地儲存與剪貼簿操作

**適用對象**: 前端開發者

---

## 快速開始指南

### 設計師工作流程
1. **理解品牌**: 閱讀 `BRAND_GUIDELINES.md` 了解品牌核心與視覺系統
2. **使用 Token**: 參考 `DESIGN_TOKENS.md` 查找具體數值
3. **設計工具設定**:
   - Figma: 使用 8px 網格系統
   - 匯入色彩與字型 Token

### 開發者工作流程
1. **環境設定**: 確認已安裝 Tailwind CSS 與 shadcn/ui
2. **參考範例**: 查看 `COMPONENT_EXAMPLES.md` 了解組件用法
3. **快速查閱**: 使用 `DESIGN_TOKENS.md` 快速複製類別名稱
4. **工具函數**: 引入 `lib/utils.ts` 中的格式化函數

### 程式碼範例
```tsx
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { formatCurrency, formatPercent } from "@/lib/utils";

export default function DashboardCard() {
  const revenue = 1234567.89;
  const growth = 0.125;

  return (
    <Card className="stat-card">
      <CardHeader className="stat-card-header">
        <CardTitle className="text-sm font-medium text-gray-600">
          總收益
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="stat-card-value">
          {formatCurrency(revenue)}
        </div>
        <div className="stat-card-footer">
          <span className="trend-indicator trend-up">
            {formatPercent(growth)} 較上月
          </span>
        </div>
      </CardContent>
    </Card>
  );
}
```

---

## 設計系統特色

### 色彩系統
- **主色**: 品牌藍 (#1570EF) - 專業、科技感
- **輔助色**: 品牌深藍 (#4F46E5) - 權威感
- **功能色**: 成功/警告/錯誤/資訊 - 清晰的狀態指示
- **圖表色**: 8 色和諧配色方案 - 易於辨識

### 字型系統
- **繁體中文優先**: Noto Sans TC、PingFang TC、微軟正黑體
- **等寬數字**: 確保數據對齊
- **清晰階層**: Display > Heading > Body > Caption

### 間距系統
- **4px 基礎單位**: 確保視覺節奏一致
- **8px 網格系統**: 與設計工具完美配合

### 組件系統
- **shadcn/ui 基礎**: 無障礙、可自訂、高品質
- **自訂擴展**: 針對營運系統的專用組件（stat-card, trend-indicator）

---

## 品牌核心價值

### 品牌個性
- **專業 Professional**: 企業級可靠性
- **高效 Efficient**: 自動化工作流
- **智能 Intelligent**: AI 賦能決策
- **可靠 Trustworthy**: 穩定系統

### 品牌承諾
「讓數據說話，讓 AI 賦能，讓營運更簡單」

---

## 無障礙標準

- **WCAG AA 合規**: 所有色彩對比度達標
- **鍵盤導航**: 完整支援
- **螢幕閱讀器**: 語義化標籤
- **減少動畫**: 尊重 `prefers-reduced-motion`

---

## 響應式設計

### 斷點
```
手機直式: 0px
手機橫式: 640px (sm)
平板: 768px (md)
筆電: 1024px (lg)
桌機: 1280px (xl)
大螢幕: 1536px (2xl)
```

### 行動優先
所有組件採用行動優先設計，確保在小螢幕上的可用性。

---

## 圖表配色方案

專為數據可視化設計的 8 色和諧配色：

1. **藍色 (#2E90FA)**: 主要數據
2. **紫色 (#7C3AED)**: 次要數據
3. **青色 (#14B8A6)**: 第三數據
4. **橙色 (#F97316)**: 對比數據
5. **粉色 (#EC4899)**: 強調數據
6. **綠色 (#10B981)**: 正向指標
7. **紅色 (#EF4444)**: 負向指標
8. **琥珀色 (#F59E0B)**: 中性指標

---

## 常見問題

### Q: 如何選擇按鈕變體？
- **Primary**: 主要動作（儲存、提交）
- **Secondary/Outline**: 次要動作（取消、返回）
- **Destructive**: 危險操作（刪除、清除）
- **Ghost**: 最低優先級（查看詳情）

### Q: 何時使用 stat-card？
用於儀表板的 KPI 指標展示，包含標題、數值、趨勢指標。

### Q: 如何確保數字對齊？
使用 `font-tabular` 類別或 `font-numeric` 字體家族。

### Q: 圖表應該用什麼顏色？
按順序使用圖表配色（chart-blue, chart-purple, chart-teal...），確保可辨識性。

---

## 維護與更新

### 版本控制
- 當前版本: **v1.0.0** (2026-01-05)
- 每次重大變更更新版本號
- 在 `BRAND_GUIDELINES.md` 底部記錄變更日誌

### 提案流程
1. 在團隊會議中討論變更需求
2. 設計師提供視覺方案
3. 開發者評估實施成本
4. 更新相關文檔
5. 團隊審核通過後實施

---

## 參考資源

### 設計靈感
- [Tailwind UI](https://tailwindui.com/)
- [shadcn/ui](https://ui.shadcn.com/)
- [Radix UI](https://www.radix-ui.com/)

### 無障礙指南
- [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/)
- [A11y Project](https://www.a11yproject.com/)

### 字體下載
- [Noto Sans TC](https://fonts.google.com/noto/specimen/Noto+Sans+TC)
- [JetBrains Mono](https://www.jetbrains.com/lp/mono/)
- [Roboto Mono](https://fonts.google.com/specimen/Roboto+Mono)

---

## 聯絡資訊

**維護者**: GoGoJap 設計團隊
**最後更新**: 2026-01-05
**狀態**: 生效中

---

## 文檔地圖

```
GoGoJap 品牌設計系統
│
├── BRAND_GUIDELINES.md ········· 完整品牌指南（策略層）
│   ├── 品牌核心與定位
│   ├── 視覺識別系統
│   ├── 組件風格規範
│   └── 語調與無障礙指南
│
├── DESIGN_TOKENS.md ············ 設計 Token 快速參考（實施層）
│   ├── 色彩/字型/間距數值
│   ├── 常用組合類別
│   └── 快速複製範本
│
├── COMPONENT_EXAMPLES.md ······· 組件程式碼範例（實作層）
│   ├── 按鈕/卡片/表單範例
│   ├── 頁面佈局範例
│   └── 最佳實踐建議
│
├── tailwind.config.ts ·········· Tailwind 配置（技術層）
│   ├── 色彩/字型/間距 Token
│   ├── 自訂動畫與工具
│   └── shadcn/ui 整合
│
├── app/globals.css ············· 全局樣式（技術層）
│   ├── CSS 變數定義
│   ├── 自訂組件類別
│   └── 工具類別
│
└── lib/utils.ts ················ 工具函數（技術層）
    ├── 數字/日期格式化
    ├── 字串/陣列處理
    └── 驗證與工具函數
```

---

**提示**: 將此文檔加入書籤，作為品牌設計系統的入口點。
