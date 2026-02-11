---
name: "Dev: New Feature"
description: "Start a new feature with the full Agent Team workflow (brainstorm → architect → explore → TDD → implement → review → verify)"
category: Development
tags: [workflow, agent-team, feature]
---

啟動新功能開發的完整 Agent Team 工作流。

**Input**: `/dev:new-feature` 後面的參數是功能描述（中文或英文皆可）。

---

## 工作流程

按以下順序執行，每個步驟使用對應的 Agent：

### Phase 1：理解需求

**Step 1 — Brainstorming（創意探索）**

使用 `Skill(superpowers:brainstorming)` 探索需求：
- 確認用戶真正想要什麼
- 探索可能的實現方向
- 識別約束和風險

**如果需求已經非常清楚（用戶給了詳細規格），可跳過此步。**

### Phase 2：設計架構

**Step 2 — Architecture（架構設計）**

使用 `Task(subagent_type="architect")` 或 `EnterPlanMode` 設計方案：

需要輸出：
- 需修改的文件清單（哪些文件、改什麼）
- 數據流說明（新 API / 數據模型 / 前端狀態）
- 風險評估（可能影響的現有功能）

**GoGoJap 架構參考**：
- 後端三層：`api/v1/` → `services/` → `connectors/` + `models/`
- 前端：Next.js 14 App Router + TanStack Query + shadcn/ui
- 新 API 端點需同步修改：Schema → Router → Service → 前端 api.ts → 前端頁面

**Step 3 — Explore（代碼探索）**（如需深入理解現有代碼）

使用 `Task(subagent_type="Explore")` 深度探索相關代碼：
- 追蹤 API 端點的完整調用鏈
- 理解相關模組的現有實現
- 識別依賴關係和影響範圍

**可與 Step 2 並行，如果探索和設計是獨立的。**

### Phase 3：測試先行

**Step 4 — TDD（測試驅動開發）**

使用 `Task(subagent_type="tdd-guide")` 或 `Skill(testing-patterns)` 先寫測試：
- 後端：pytest + httpx.AsyncClient
- 前端：Jest + React Testing Library
- 外部 API（Firecrawl, Claude, HKTVmall）一律 mock
- 先寫失敗測試，確認需求理解正確

### Phase 4：實現

**Step 5 — 實現代碼**

Claude Code 主進程直接實現：
- 讓 Step 4 的測試通過
- 遵循現有代碼風格和模式
- 函數 ≤20 行，縮進 ≤3 層

### Phase 5：質量閘門（必須執行）

**Step 6 — Code Review（代碼審查）** [必須]

使用 `Task(subagent_type="code-reviewer")` 審查所有修改：

審查維度：
| 維度 | 檢查項 |
|------|--------|
| 正確性 | 邏輯、邊界情況 |
| 一致性 | 命名、結構、錯誤處理 |
| 安全性 | 注入、XSS、數據洩露 |
| 性能 | N+1 查詢、不必要 API 調用 |
| GoGoJap 規則 | SKU 正則、Firecrawl credit、改價審批流程 |

**Step 7 — Security Review（安全審查）** [涉及安全時必須]

如果修改涉及以下任一項，必須使用 `Task(subagent_type="security-reviewer")`：
- API 端點（用戶輸入處理）
- 認證/授權
- 外部 API 回應處理
- Token / API Key / 密碼
- 文件上傳

**Step 6 和 Step 7 可以並行執行。**

### Phase 6：收尾

**Step 8 — Build Check（構建驗證）**

如果構建失敗，使用 `Task(subagent_type="build-error-resolver")` 修復。

**Step 9 — Doc Update（文檔同步）** [架構變更時必須]

如果新增/刪除/移動了文件或目錄，使用 `Task(subagent_type="doc-updater")` 更新文檔。

**Step 10 — Verification（完成驗證）**

使用 `Skill(superpowers:verification-before-completion)` 確認一切完成。

---

## 並行策略

```
Phase 1: Brainstorming                      (串行)
Phase 2: Architecture + Explore             (可並行)
Phase 3: TDD                                (串行)
Phase 4: Implementation                     (串行)
Phase 5: Code Review + Security Review      (可並行)
Phase 6: Build + Doc + Verify               (串行)
```

---

## 快速模式

如果功能很小（只改 1-2 個文件），可以跳過 Phase 1-2，直接從 Phase 3（TDD）開始。但 Phase 5（Code Review）不可跳過。

---

## Guardrails

- **不可跳過 Code Review** — 每次修改 ≥3 文件必須 Code Review
- **不可跳過 Security Review** — 涉及安全的修改必須 Security Review
- **不可跳過 Doc Update** — 架構級變更必須更新文檔
- 每個 Phase 完成後，簡要向用戶報告進展
- 如果任何 Phase 發現問題，停下來與用戶討論，不要自行跳過
