# Spec: Pricing Approval

## ADDED Requirements

### Requirement: View Pending Proposals

系統 **MUST** 允許經理查看所有待審批的 AI 改價提案。

#### Scenario: Display pending proposals list

- **Given** 有 3 個狀態為 pending 的改價提案
- **When** 用戶訪問 /pricing-approval 頁面
- **Then** 顯示 3 個提案卡片，按創建時間倒序排列
- **And** 每個卡片顯示：產品名稱、SKU、現價、建議價、價格變化百分比、AI 理由、創建時間

#### Scenario: Empty state

- **Given** 沒有待審批的提案
- **When** 用戶訪問 /pricing-approval 頁面
- **Then** 顯示「暫無待審批提案」空狀態
- **And** 顯示「觸發 AI 分析」按鈕

---

### Requirement: Approve Single Proposal

系統 **MUST** 允許經理批准單個改價提案並執行 HKTVmall 價格更新。

#### Scenario: Approve proposal successfully

- **Given** 一個狀態為 pending 的提案
- **When** 用戶點擊「批准」按鈕
- **Then** 調用 POST /pricing/proposals/{id}/approve
- **And** 提案從列表中移除
- **And** 顯示成功 Toast 通知

#### Scenario: Approve with modified price

- **Given** 一個狀態為 pending 的提案，建議價為 $119
- **When** 用戶修改最終價格為 $115 並確認批准
- **Then** 調用 API 時傳送 final_price: 115
- **And** 後端使用 $115 作為執行價格

---

### Requirement: Reject Single Proposal

系統 **MUST** 允許經理拒絕單個改價提案。

#### Scenario: Reject proposal successfully

- **Given** 一個狀態為 pending 的提案
- **When** 用戶點擊「拒絕」按鈕
- **Then** 調用 POST /pricing/proposals/{id}/reject
- **And** 提案從列表中移除
- **And** 顯示成功 Toast 通知

---

### Requirement: Batch Operations

系統 **SHALL** 支持批量批准或拒絕多個提案以提高效率。

#### Scenario: Select multiple proposals

- **Given** 顯示 5 個待審批提案
- **When** 用戶勾選其中 3 個提案
- **Then** 底部操作欄顯示「已選 3 項」
- **And** 「批量批准」和「批量拒絕」按鈕啟用

#### Scenario: Batch approve

- **Given** 選中 3 個提案
- **When** 用戶點擊「批量批准」
- **Then** 並行調用 3 次 approve API
- **And** 顯示結果統計「成功 3 項，失敗 0 項」

#### Scenario: Select all

- **Given** 顯示 5 個待審批提案
- **When** 用戶點擊「全選」checkbox
- **Then** 所有 5 個提案被選中
- **And** 底部顯示「已選 5 項」

---

### Requirement: Trigger AI Analysis

系統 **MUST** 允許用戶手動觸發 AI 價格分析以生成新的改價提案。

#### Scenario: Trigger analysis successfully

- **Given** 用戶在審批頁面
- **When** 點擊「觸發 AI 分析」按鈕
- **Then** 調用 POST /pricing/analyze
- **And** 按鈕顯示 loading 狀態
- **And** 完成後顯示「已生成 N 個新提案」Toast
- **And** 列表自動刷新

---

### Requirement: Proposal Statistics Display

系統 **SHALL** 在頁面頂部顯示提案狀態統計以便快速了解整體情況。

#### Scenario: Display stats cards

- **Given** 數據庫中有：12 pending, 45 executed, 3 rejected, 1 failed
- **When** 用戶訪問頁面
- **Then** 顯示 4 個統計卡片：
  - 待審批: 12 (橙色)
  - 已批准: 45 (綠色)
  - 已拒絕: 3 (灰色)
  - 執行失敗: 1 (紅色)

---

### Requirement: Navigation Entry

系統 **MUST** 在側邊欄添加改價審批的導航入口以便快速訪問。

#### Scenario: Navigate to pricing approval

- **Given** 用戶已登錄
- **When** 查看側邊欄「商品管理」分組
- **Then** 顯示「改價審批」導航項
- **And** 點擊後跳轉到 /pricing-approval
