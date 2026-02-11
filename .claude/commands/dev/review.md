---
name: "Dev: Review"
description: "Quick code review using the Code Reviewer agent"
category: Development
tags: [workflow, agent-team, review, quality]
---

快速啟動代碼審查。

**Input**: `/dev:review` 後面的參數可以是：
- 文件路徑（審查特定文件）
- `--staged`（審查 git staged 的修改）
- `--last-commit`（審查最後一次 commit）
- 留空（審查所有未提交的修改）

---

## 工作流程

### Step 1 — 確定審查範圍

根據輸入確定要審查什麼：

**如果指定了文件路徑**：審查該文件
**如果 `--staged`**：運行 `git diff --staged` 獲取修改
**如果 `--last-commit`**：運行 `git diff HEAD~1` 獲取修改
**如果留空**：運行 `git diff` + `git status` 獲取所有未提交修改

### Step 2 — Code Review

使用 `Task(subagent_type="code-reviewer")` 執行審查。

在 prompt 中包含以下上下文：

```
項目：GoGoJap - HKTVmall AI 智能運營系統
技術棧：FastAPI + SQLAlchemy async + Next.js 14 + TanStack Query + shadcn/ui

GoGoJap 專用審查規則：
1. HKTVmall SKU 正則必須用 [A-Z]\d{7,}[A-Za-z0-9_-]*（不僅限 H 開頭）
2. Firecrawl 調用必須考慮 credit 成本（優先用 HTTP metadata）
3. 所有改價操作必須經過 PriceProposal 審批流程
4. 前端 API 調用必須使用 lib/api.ts 中的集中方法
5. 數據庫操作必須使用 async session
6. 不允許任何 mock 模式代碼

審查維度：
- 正確性（邏輯、邊界情況）
- 一致性（命名、結構、錯誤處理）
- 安全性（注入、XSS、數據洩露）
- 性能（N+1 查詢、不必要 API 調用）
- 可維護性（函數長度 ≤20 行、縮進 ≤3 層、無重複代碼）
```

### Step 3 — 報告結果

向用戶報告審查結果：
- **Critical**：必須修復的問題（安全漏洞、邏輯錯誤）
- **Warning**：建議修復的問題（性能、可維護性）
- **Info**：風格建議（命名、結構）
- **Pass**：做得好的地方

### Step 4 — Security Review（可選）

如果 Code Review 發現安全相關問題，或修改涉及 API 端點/用戶輸入/Token，自動追加：

使用 `Task(subagent_type="security-reviewer")` 執行安全審查。

**Code Review 和 Security Review 可以並行執行。**

---

## Guardrails

- 審查結果必須有具體的文件和行號引用
- 不要只說「看起來沒問題」— 必須列出具體檢查了什麼
- 如果修改範圍太大（>500 行），建議分批審查
- 審查完成後詢問用戶是否需要修復發現的問題
