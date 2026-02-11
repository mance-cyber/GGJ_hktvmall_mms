---
name: "Dev: Fix Bug"
description: "Systematic bug fix workflow (debug → explore → repro test → fix → review → verify)"
category: Development
tags: [workflow, agent-team, bugfix, debugging]
---

啟動系統化的 Bug 修復工作流。

**Input**: `/dev:fix-bug` 後面的參數是 Bug 描述（錯誤信息、重現步驟、或 issue 編號）。

---

## 工作流程

### Step 1 — Systematic Debugging（系統化排錯）

使用 `Skill(superpowers:systematic-debugging)` 進行科學排錯：

1. **觀察現象**：收集錯誤信息、日誌、堆棧
2. **形成假設**：列出可能的根因（≥2 個）
3. **設計驗證**：確定如何驗證/排除每個假設
4. **逐一排除**：從最可能的假設開始

**不要猜！不要直接動手修！先理解問題。**

### Step 2 — Explore（定位問題代碼）

使用 `Task(subagent_type="Explore")` 追蹤問題：
- 追蹤從 API 端點到數據庫的完整調用鏈
- 找出出錯的具體位置（文件:行號）
- 理解周邊代碼的設計意圖

**GoGoJap 常見 Bug 位置**：
- SKU 正則匹配問題 → `hktv_scraper.py` 的 `SKU_PATTERN`
- API 回應格式不一致 → `schemas/*.py` 的 Pydantic 驗證
- 前端 API 調用 → `lib/api.ts` 的方法簽名
- Celery 任務失敗 → `tasks/*.py` 的異常處理
- 數據庫查詢 → `services/*.py` 的 SQLAlchemy async session

### Step 3 — TDD（寫重現測試）

使用 `Task(subagent_type="tdd-guide")` 先寫一個會失敗的測試：
- 這個測試必須能**重現** Bug
- 測試通過 = Bug 已修復
- 防止未來回歸

```
測試模式：
1. 構造觸發 Bug 的輸入
2. 調用出 Bug 的函數/端點
3. Assert 期望的正確行為（目前應失敗）
```

### Step 4 — Fix（修復代碼）

Claude Code 主進程實施修復：
- 讓 Step 3 的測試通過
- 最小化修改（只改必要的代碼）
- 不順便重構（除非重構就是修復的一部分）

### Step 5 — Code Review（代碼審查）[必須]

使用 `Task(subagent_type="code-reviewer")` 審查修復：
- 修復是否正確？
- 是否有副作用？
- 是否引入新問題？
- 是否符合項目模式？

### Step 6 — Verification（完成驗證）

使用 `Skill(superpowers:verification-before-completion)` 確認：
- 重現測試現在通過
- 沒有破壞其他測試
- 修復理由清晰可追溯

---

## 並行策略

```
Step 1: Debugging                (串行 - 必須先理解問題)
Step 2: Explore                  (串行 - 在理解問題的基礎上)
Step 3: TDD                     (串行)
Step 4: Fix                     (串行)
Step 5: Code Review             (串行)
Step 6: Verification            (串行)
```

Bug 修復通常是嚴格串行的，每一步依賴前一步的結論。

---

## 快速模式

如果 Bug 非常明顯（例如明確的 typo、缺少 import），可以跳過 Step 1-2，直接從 Step 3（重現測試）開始。

---

## Guardrails

- **不要猜測根因** — 必須有證據支持假設
- **不要在沒有測試的情況下修復** — 先重現，再修復
- **不要順便重構** — Bug 修復只修復 Bug
- **Code Review 不可跳過** — 即使修改很小
- 如果排錯過程中發現更深層的架構問題，記錄下來但不在此次修復中處理
