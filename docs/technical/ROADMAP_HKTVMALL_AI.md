# GoGoJap - HKTVmall AI System 全功能演進藍圖

本文件規劃將 GoGoJap 系統從單純的「數據分析工具」升級為「全自動化 AI 電商中樞」。
目標是整合 HKTVmall MMS API 的全方位功能：定價、庫存、訂單、客服及財務。

## ⚠️ 核心安全原則 (Critical Safety Protocols)

在實作任何「寫入/修改」功能前，必須嚴格遵守：
1.  **Human-in-the-Loop (人類確認機制)**：初期所有 AI 建議的操作（如改價、回覆訊息）預設為 `Pending Approval`，需人工點擊確認才執行。
2.  **Hard Limits (硬性限制)**：
    -   價格保護：設定最低售價 (Floor Price) 和單次最大跌幅 (e.g., 不超過 10%)。
    -   庫存保護：預留安全庫存 (Safety Stock)，避免超賣。
3.  **Audit Logs (審計日誌)**：記錄所有變更操作 (Who, What, When, Why)。

---

## Phase 1: AI 智能定價與庫存管理 (Dynamic Pricing & Inventory)
> **目標**：從「被動監測對手」轉變為「主動執行策略」。

### 1.1 基礎設施建設
- [ ] 擴充 `Product` 資料庫 Schema，加入成本價 (Cost)、最低售價 (Min Price)、目標利潤率。
- [ ] 建立 `AuditLog` 表，記錄系統操作。

### 1.2 庫存同步 (Inventory Sync)
- **MMS API**: `updateStock`
- **功能**:
    - 設定安全庫存水平 (例如：保留 2 件不賣)。
    - 缺貨預警 Dashboard。

### 1.3 智能改價 (Auto-Pricing Action)
- **MMS API**: `updatePrice` (Standard Price & Promotion Price)
- **AI 邏輯**:
    - 接收 AI 策略模型的建議 (例如："Competitor A 降價至 $100，建議跟進至 $98")。
    - 檢查是否低於 `Min Price`。
- **UI 交互**:
    - 在「策略建議」卡片上新增 `執行建議` 按鈕。
    - 執行後透過 API 更新 HKTVmall，並回傳結果。

---

## Phase 2: 智能訂單處理中心 (Intelligent Order Fulfillment)
> **目標**：自動化日常出貨流程，減少人手操作。

### 2.1 訂單同步與管理
- **MMS API**: `getOrders`, `updateOrderStatus`
- **功能**:
    - 自動定時 Sync 新訂單到本地資料庫。
    - 統一 Dashboard 查看所有狀態 (Pending, Packing, Shipped)。

### 2.2 智能出貨助手
- **MMS API**: `getLabel` (下載 AWB)
- **AI 邏輯**:
    - **異常單偵測**: AI 分析訂單內容（例如：同一人買 50 件牙膏），標記潛在風險。
    - **包裝建議**: 根據訂單體積，建議使用幾號箱/袋。
- **UI 交互**:
    - 批量打印 AWB 功能。
    - 一鍵更新訂單狀態為「已包裝」。

---

## Phase 3: AI 客服中樞 (AI Customer Service / Inbox)
> **目標**：利用 RAG (檢索增強生成) 技術，讓 AI 成為 24/7 客服。

### 3.1 訊息同步
- **MMS API**: `getConversations`, `getMessages`
- **UI**: 仿 Chat 介面，在系統內直接查看客人查詢。

### 3.2 AI 智慧回覆 (Draft Mode)
- **MMS API**: `sendMessage`
- **AI 邏輯 (RAG)**:
    - 讀取產品描述、FAQ、庫存狀態。
    - 當收到 "有冇現貨?"，AI 自動查庫存並 Draft 回覆："你好，現貨充足，今日落單預計後日送達。"
- **機制**:
    - 初期：AI 撰寫草稿 -> 人類由 Approve -> 發送。
    - 後期（高置信度）：自動回覆簡單問題。

### 3.3 情緒分析與警報
- AI 分析訊息情緒分數。
- 遇到憤怒/投訴訊息 (Sentiment Score < 0.3)，發送 Telegram/Email 警報給管理員優先處理。

---

## Phase 4: 產品內容優化 (Content & SEO)
> **目標**：提升產品在 HKTVmall 內部的搜尋排名與轉化率。

### 4.1 產品資料同步
- **MMS API**: `getProduct`, `updateProduct`
- **功能**: 下載現有產品描述作分析。

### 4.2 AI 內容生成工廠
- **AI 邏輯**:
    - **SEO 優化**: 根據熱門關鍵字，重寫產品標題與 HTML 描述。
    - **圖片處理**: (未來擴展) 自動檢查圖片規格，甚至生成場景圖。
- **UI**: 產品編輯器，支援 AI 一鍵優化文案並 Push 到 HKTVmall。

---

## Phase 5: 財務智能與報表 (Financial Intelligence)
> **目標**：了解真實利潤，不僅僅是營業額。

### 5.1 結算單整合
- **MMS API**: `getSettlementReport`
- **功能**: 自動下載並解析 Excel/CSV 結算單。

### 5.2 真實利潤儀表板
- **計算公式**: `最終利潤 = 訂單金額 - HKTVmall佣金 - 運費補貼扣除 - 產品成本`
- **AI 分析**:
    - 識別「賠錢貨」 (高銷量但負毛利)。
    - 識別「金牛產品」 (高利潤且穩定)。

---

## 技術架構演進 (Technical Evolution)

| 模組 | 現有架構 | 新增需求 |
| :--- | :--- | :--- |
| **Backend** | FastAPI (Sync) | 加入 **Task Queue (Celery/ARQ)** 處理異步任務 (如批量改價) |
| **Database** | PostgreSQL (Products, Prices) | 新增 `Orders`, `Messages`, `AuditLogs`, `Settlements` Tables |
| **AI Engine** | OpenAI/Claude API | 引入 **Vector DB (pgvector)** 用於客服 RAG 知識庫 |
| **Security** | Basic Auth | **Role-Based Access Control (RBAC)** (區分管理員與普通員工權限) |

## 執行順序建議

1.  **Phase 1.1 & 1.3**: 優先完成「改價」功能，實現分析到行動的閉環。(Current Priority)
2.  **Phase 1.2**: 補齊庫存管理。
3.  **Phase 2**: 訂單管理 (減輕日常運作負擔)。
4.  **Phase 3**: 客服功能。
5.  **Phase 4 & 5**: 內容與財務優化。
