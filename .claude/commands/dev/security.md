---
name: "Dev: Security"
description: "Security review for code handling user input, auth, API endpoints, or sensitive data"
category: Development
tags: [workflow, agent-team, security, review]
---

啟動安全審查。

**Input**: `/dev:security` 後面的參數可以是：
- 文件路徑（審查特定文件）
- 模組名（如 `auth`、`api`、`payments`）
- 留空（審查所有近期修改）

---

## 工作流程

### Step 1 — 確定審查範圍

根據輸入確定要審查什麼：

**如果指定了文件/模組**：聚焦該範圍
**如果留空**：運行 `git diff HEAD~5` 獲取最近 5 次 commit 的修改

### Step 2 — Security Review

使用 `Task(subagent_type="security-reviewer")` 執行安全審查。

在 prompt 中包含以下上下文：

```
項目：GoGoJap - HKTVmall AI 智能運營系統

GoGoJap 安全架構：
1. .env 文件已被 settings.local.json 禁止讀取
2. Webhook secret 使用 Fernet 加密存儲（models/notification.py）
3. AI API Key 存數據庫 SystemSetting 表，前端只返回預覽（api_key[:8]...api_key[-4:]）
4. HKTVmall access_token 通過環境變量注入
5. 前端使用 secure-token.ts 管理 Token

重點檢查：
- OWASP Top 10 漏洞
- SQL 注入（SQLAlchemy 參數化查詢）
- XSS（React 默認轉義 + 手動 dangerouslySetInnerHTML）
- SSRF（外部 URL 處理，特別是 Firecrawl 抓取目標）
- 敏感數據洩露（API Key、Token、密碼）
- 權限繞過（API 端點認證）
- 不安全的反序列化（Pydantic 驗證）
- 依賴漏洞
```

### Step 3 — 報告結果

向用戶報告安全審查結果：

| 嚴重度 | 描述 | 處理方式 |
|--------|------|---------|
| **Critical** | 可被遠程利用的漏洞 | 立即修復 |
| **High** | 潛在的數據洩露或權限繞過 | 盡快修復 |
| **Medium** | 不安全的實踐但利用難度高 | 計劃修復 |
| **Low** | 防禦性改進建議 | 可選修復 |

### Step 4 — 修復建議

對每個發現的問題，提供：
- 問題位置（文件:行號）
- 攻擊向量說明
- 具體修復代碼

---

## Guardrails

- 不要忽略任何潛在的安全問題
- 所有發現必須有 CWE 編號引用（如適用）
- 如果發現 Critical 問題，必須在報告開頭醒目標記
- 不要發送敏感信息到外部服務
- 審查完成後詢問用戶是否需要修復
