---
name: "Dev: Refactor"
description: "Safe refactoring workflow (explore → architect → protection tests → refactor → review → docs)"
category: Development
tags: [workflow, agent-team, refactor]
---

啟動安全的重構工作流。

**Input**: `/dev:refactor` 後面的參數是重構目標（要重構什麼、為什麼重構）。

---

## 核心原則

> 重構 = 改變代碼結構，不改變外部行為。
> 先理解設計意圖，再動手。不理解就不重構。

---

## 工作流程

### Step 1 — Explore（全面理解現有代碼）

使用 `Task(subagent_type="Explore")` 深度理解要重構的代碼：
- 原設計意圖是什麼？
- 被哪些模組依賴？影響範圍多大？
- 有無隱含的業務邏輯（不明顯但重要的行為）？
- 現有測試覆蓋情況如何？

**GoGoJap 重構高風險區域**：
- `AIAnalysisService` — 6+ 服務依賴，改動影響範圍大
- `api.ts` — 60+ 前端方法，改簽名會破壞多個頁面
- `config.py` — 所有後端服務的配置入口
- Celery 任務 — 修改參數格式可能破壞排程

### Step 2 — Architect（設計目標架構）

使用 `Task(subagent_type="architect")` 或 `EnterPlanMode` 設計重構方案：
- 目標結構長什麼樣？
- 遷移路徑：現狀 → 目標 的具體步驟
- 每一步都是可獨立驗證的小改動
- 風險評估和回滾方案

### Step 3 — TDD（保護性測試）

使用 `Task(subagent_type="tdd-guide")` 確保現有行為被測試覆蓋：
- 為要重構的代碼寫（或補）測試
- 測試覆蓋所有公開 API / 函數的行為
- 這些測試在重構前必須全部通過
- 重構後這些測試仍然必須全部通過

### Step 4 — Refactor（執行重構）

使用 `Task(subagent_type="refactor-cleaner")` + Claude Code 主進程：
- 按 Step 2 的計劃逐步執行
- 每個小步驟後運行 Step 3 的測試
- 如果測試失敗，立即回退到上一步，分析原因

可選 `Task(subagent_type="code-simplifier:code-simplifier")` 進行代碼簡化。

### Step 5 — Code Review（審查重構）[必須]

使用 `Task(subagent_type="code-reviewer")` 審查：
- 外部行為是否保持不變？
- 代碼是否更簡潔清晰？
- 是否消除了代碼壞味道？
- 是否符合 CLAUDE.md 的設計哲學？

### Step 6 — Doc Update（更新架構文檔）[必須]

使用 `Task(subagent_type="doc-updater")` 更新文檔：
- 重構涉及的模組邊界變化
- 新的依賴關係
- CLAUDE.md 目錄結構（如有文件移動）

---

## 並行策略

```
Step 1: Explore                  (串行)
Step 2: Architect                (串行 - 依賴 Step 1)
Step 3: TDD                     (串行 - 依賴 Step 2)
Step 4: Refactor                 (串行 - 逐步執行)
Step 5: Code Review             (串行)
Step 6: Doc Update              (串行)
```

重構必須嚴格串行。不理解就不設計，不保護就不動刀。

---

## 常見重構場景

| 場景 | 重點 |
|------|------|
| 拆分大函數 | 確保每個小函數職責單一 |
| 消除重複代碼 | 先確認重複是真重複（非巧合相似） |
| 改變數據結構 | 先改類型定義，讓編譯器/類型檢查指出所有影響點 |
| 模組重組 | 確保 import 路徑全部更新 |
| 清理死代碼 | 用 grep 確認真的無人引用 |

---

## Guardrails

- **不要在理解之前重構** — Step 1 是最重要的步驟
- **不要沒有保護性測試就重構** — 無測試 = 盲飛
- **不要一次改太多** — 小步前進，每步驗證
- **Code Review 和 Doc Update 不可跳過**
- **不要順便加新功能** — 重構和新功能分開做
- 如果發現重構範圍比預期大，停下來重新評估
