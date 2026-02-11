---
name: agent-team
description: "GoGoJap Agent Team 知識庫。在使用 /dev:* 命令或調度開發 Agent 時自動載入。包含項目專用的模式、約定和質量規則。"
pairs-with:
  - skill: testing-patterns
    reason: TDD Agent 需要測試模式知識
  - skill: frontend-design
    reason: Frontend Designer Agent 需要設計系統知識
  - skill: superpowers:brainstorming
    reason: 新功能開發的第一步
  - skill: superpowers:systematic-debugging
    reason: Bug 修復的第一步
---

# GoGoJap Agent Team 知識庫

## Agent 速查表

```
場景                          → 調用
────────────────────────────────────────────
開始新功能                     → /dev:new-feature
                               → Skill(superpowers:brainstorming)
                               → EnterPlanMode / Task(architect)
修復 Bug                       → /dev:fix-bug
                               → Skill(superpowers:systematic-debugging)
重構代碼                       → /dev:refactor
代碼審查                       → /dev:review
                               → Task(code-reviewer)
安全審查                       → /dev:security
                               → Task(security-reviewer)
不確定代碼在哪                 → Task(Explore)
寫測試                         → Task(tdd-guide)
構建失敗                       → Task(build-error-resolver)
要做新 UI                      → Skill(frontend-design)
改了架構                       → Task(doc-updater) [必須]
代碼很亂                       → Task(refactor-cleaner)
完成前最終檢查                 → Skill(superpowers:verification-before-completion)
```

---

## 質量閘門

### 不可跳過

| 閘門 | Agent | 條件 |
|------|-------|------|
| **Code Review** | `code-reviewer` | 每次修改 ≥3 個文件 |
| **Security Review** | `security-reviewer` | 涉及 API 端點 / 用戶輸入 / Token |
| **Build Check** | `build-error-resolver` | 每次構建失敗 |
| **Doc Sync** | `doc-updater` | 新增/刪除/移動文件 |

### 推薦但可選

| 閘門 | Agent | 條件 |
|------|-------|------|
| TDD | `tdd-guide` | 新功能 / Bug 修復 |
| Architecture Review | `architect` | 影響多模組的修改 |
| Cleanup | `refactor-cleaner` | 功能完成後 |

---

## GoGoJap 專用規則

### 後端規範

- **三層架構**：`api/v1/` → `services/` → `connectors/` + `models/`
- **SKU 正則**：`[A-Z]\d{7,}[A-Za-z0-9_-]*`（不僅限 H 開頭，支持 B 等前綴和後綴）
- **Firecrawl 成本控制**：三層抓取策略 — HTTP metadata (0 credit) → Firecrawl price (1 credit) → Firecrawl full
- **改價必須審批**：所有價格修改必須通過 `PriceProposal` 表（AI 提案 → 人工審批 → 執行）
- **數據庫操作**：一律使用 async session（SQLAlchemy 2.0）
- **禁止 mock 模式**：不允許任何 mock client 或 fake data fallback

### 前端規範

- **API 調用**：必須使用 `lib/api.ts` 中的集中方法
- **狀態管理**：TanStack Query 5（所有 API 數據）
- **UI 組件**：shadcn/ui + Radix UI + Tailwind CSS
- **設計系統**：Future Tech 風格（HoloCard, PulseStatus, DataStreamBg）
- **動畫**：Framer Motion（PageTransition, StaggerContainer）

### 新增 API 端點清單

新增一個 API 端點需要同步修改：
1. `backend/app/schemas/{module}.py` — 請求/回應 Schema
2. `backend/app/api/v1/{module}.py` — 路由定義
3. `backend/app/services/{service}.py` — 業務邏輯
4. `backend/app/models/{model}.py` — 數據模型（如需）
5. `frontend/src/lib/api.ts` — 前端 API 方法
6. `frontend/src/app/{page}/page.tsx` — 前端頁面

### 新增數據表清單

新增一張數據表需要同步操作：
1. `backend/app/models/{model}.py` — SQLAlchemy Model
2. `alembic revision --autogenerate -m "描述"`
3. `alembic upgrade head`
4. `backend/app/schemas/{schema}.py` — Pydantic Schema

---

## Model 選擇指引

| Agent | 推薦 model | 理由 |
|-------|-----------|------|
| Architect | `opus` | 深度架構思考 |
| Explorer | `sonnet` | 搜索分析，速度優先 |
| TDD Guide | `sonnet` | 測試生成，平衡質量和速度 |
| Code Reviewer | `opus` | 深度審查不漏檢 |
| Security Reviewer | `opus` | 安全問題零容忍 |
| Build Fixer | `haiku` | 簡單修復，速度優先 |
| Doc Updater | `haiku` | 結構化任務 |
| Refactorer | `sonnet` | 需要理解上下文 |

---

## 並行調度策略

### 可並行的組合

```python
# 後端探索 + 前端探索（獨立代碼庫）
Task(subagent_type="Explore", prompt="分析後端 API 的調用鏈")
Task(subagent_type="Explore", prompt="分析前端頁面的狀態管理")

# Code Review + Security Review（獨立關注點）
Task(subagent_type="code-reviewer", prompt="審查代碼質量")
Task(subagent_type="security-reviewer", prompt="檢查安全漏洞")
```

### 必須串行的序列

```
Architect → TDD Guide → 實現 → Code Review → Security Review
   (1)         (2)       (3)       (4)            (5)
```

---

## 已知清理項

以下項目已識別但尚未清理，可在後續重構中處理：
- `backend/app/services/hktvmall.py` — `HKTVMallMockClient` 類（第 11-176 行）仍存在
- `backend/app/connectors/claude.py` — Legacy connector，正被 `ai_service.py` 取代
