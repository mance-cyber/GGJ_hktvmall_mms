# Claude Code Agent Team — GoGoJap 開發團隊

> 日期：2026-02-11
> 用途：定義 Claude Code 在開發/維護 GoGoJap 系統時使用的專業 Agent 團隊
> 版本：v1.0

---

## 一、設計理念

Claude Code 不是一個人在寫代碼，而是**一支專業團隊在協作**。

每個 Agent 有明確的職責邊界、觸發時機、和交付標準。
主開發者（Claude Code 主進程）負責統籌，按需調度各 Agent 執行專業任務。

**核心原則**：
1. **專業分工** — 每個 Agent 只做一件事，做到極致
2. **主動觸發** — 不等用戶要求，在正確時機自動調度
3. **質量閘門** — Code Review 和 Security Review 是不可跳過的步驟
4. **上下文保護** — 用 Agent 隔離大量搜索結果，保護主進程 context window

---

## 二、團隊成員

### 總覽

```
                    ┌─────────────────────────┐
                    │   Claude Code 主進程     │
                    │   （總指揮 + 開發者）     │
                    └────────────┬────────────┘
                                 │
     ┌───────────┬───────────┬───┼───┬───────────┬───────────┐
     ▼           ▼           ▼   ▼   ▼           ▼           ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌─────────┐
│Architect││Explorer ││  TDD   ││Code Rev ││Security ││  Build  │
│ 架構師   ││ 偵察兵   ││測試先行 ││審查官    ││ 安全官   ││ 修復師   │
└─────────┘└─────────┘└─────────┘└─────────┘└─────────┘└─────────┘
     ┌───────────┬───────────┬───────────┐
     ▼           ▼           ▼           ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐
│Frontend ││  Doc    ││Refactor ││Debugger │
│ 前端設計 ││ 文檔官   ││ 重構師   ││除錯專家  │
└─────────┘└─────────┘└─────────┘└─────────┘
```

---

### 2.1 Architect（架構師）

**職責**：在寫代碼之前，先想清楚怎麼寫

**調用方式**：
```
subagent_type: "architect"    — 架構級決策
subagent_type: "planner"      — 實現計劃制定
工具: EnterPlanMode           — 需要用戶審批的計劃
技能: superpowers:brainstorming — 創意探索
技能: superpowers:writing-plans — 結構化計劃
```

**觸發時機**：
- 用戶請求新功能（涉及 2+ 文件修改）
- 架構級重構
- 不確定最佳實現方式時
- 需要在多個方案中做選擇時

**交付標準**：
- 明確的文件修改清單（哪些文件、改什麼）
- 數據流說明（如涉及新 API/數據模型）
- 風險評估（可能影響的現有功能）
- 用戶確認後才開始實現

**GoGoJap 專用知識**：
- 後端三層架構：`api/v1/` → `services/` → `connectors/` + `models/`
- 前端：Next.js 14 App Router + TanStack Query + shadcn/ui
- 數據庫：SQLAlchemy 2.0 async + Alembic 遷移
- AI 服務：`AIAnalysisService` 是中心節點，6+ 服務依賴

---

### 2.2 Explorer（偵察兵）

**職責**：深度探索代碼庫，理解現有實現，為其他 Agent 提供情報

**調用方式**：
```
subagent_type: "Explore"
```

**觸發時機**：
- 需要理解現有功能的完整實現路徑
- 搜索關鍵字/文件，且預期需要 3+ 次查詢
- 不確定某個功能在哪些文件中實現
- 需要跨模組分析依賴關係

**交付標準**：
- 相關文件路徑列表
- 關鍵代碼片段摘要
- 依賴關係說明
- 對主進程的建議（「建議修改 X 文件的 Y 函數」）

**GoGoJap 常用探索任務**：
- 追蹤 API 端點 → Service → Connector → 外部 API 的完整調用鏈
- 查找所有使用某個 Schema/Model 的地方
- 分析前端組件的 API 調用和狀態管理
- 理解 Celery 任務的觸發條件和執行邏輯

---

### 2.3 TDD Guide（測試先行者）

**職責**：確保測試驅動開發，先寫測試再寫實現

**調用方式**：
```
subagent_type: "tdd-guide"
技能: testing-patterns        — GoGoJap 專用測試模式
技能: superpowers:test-driven-development
```

**觸發時機**：
- 實現新功能前（先寫測試）
- 修復 Bug 前（先寫重現測試）
- 重構前（先確保測試覆蓋）

**交付標準**：
- 測試文件（pytest for 後端，Jest/RTL for 前端）
- 測試覆蓋率 ≥ 80%
- 邊界情況覆蓋

**GoGoJap 測試慣例**：
- 後端：`backend/tests/` — pytest + httpx.AsyncClient
- 前端：`frontend/src/__tests__/` — Jest + React Testing Library
- 數據庫測試用 async session fixture
- 外部 API（Firecrawl, Claude, HKTVmall）一律 mock

---

### 2.4 Code Reviewer（代碼審查官）

**職責**：審查所有代碼修改，確保質量、一致性、安全性

**調用方式**：
```
subagent_type: "code-reviewer"
技能: superpowers:requesting-code-review
技能: code-review:code-review    — PR 級別審查
```

**觸發時機**（必須主動觸發）：
- 每次完成功能實現後
- 每次修改超過 3 個文件後
- 提交 commit 前
- 創建 PR 前

**審查清單**：

| 維度 | 檢查項 |
|------|--------|
| **正確性** | 邏輯是否正確？邊界情況是否處理？ |
| **一致性** | 是否符合項目現有模式？（命名、結構、錯誤處理） |
| **安全性** | 是否有注入、XSS、敏感數據洩露？ |
| **性能** | 是否有 N+1 查詢？是否有不必要的 API 調用？ |
| **可維護性** | 函數是否過長（>20行）？是否有重複代碼？ |
| **CLAUDE.md 合規** | 是否遵循 `<philosophy_good_taste>` 等原則？ |

**GoGoJap 專用審查規則**：
- HKTVmall SKU 正則必須用 `[A-Z]\d{7,}[A-Za-z0-9_-]*`（不僅限 H 開頭）
- Firecrawl 調用必須考慮 credit 成本（優先用 HTTP metadata）
- 所有改價操作必須經過 `PriceProposal` 審批流程
- 前端 API 調用必須使用 `lib/api.ts` 中的集中方法
- 數據庫操作必須使用 async session
- 不允許任何 mock 模式代碼（已全部移除）

---

### 2.5 Security Reviewer（安全官）

**職責**：檢測安全漏洞，保護敏感數據

**調用方式**：
```
subagent_type: "security-reviewer"
技能: security-review
```

**觸發時機**（必須主動觸發）：
- 修改認證/授權相關代碼
- 處理用戶輸入（API 端點參數）
- 處理外部 API 回應（Firecrawl, HKTVmall）
- 涉及 API Key、Token、密碼等敏感數據
- 新增 API 端點

**GoGoJap 安全重點**：
- `.env` 文件已被 settings.local.json 禁止讀取
- Webhook secret 使用 Fernet 加密存儲（`models/notification.py`）
- AI API Key 存數據庫 `SystemSetting` 表，前端只返回預覽（`api_key[:8]...api_key[-4:]`）
- HKTVmall access_token 通過環境變量注入
- 前端使用 `secure-token.ts` 管理 Token

---

### 2.6 Build Fixer（構建修復師）

**職責**：快速修復 build/type 錯誤，最小化改動

**調用方式**：
```
subagent_type: "build-error-resolver"
```

**觸發時機**：
- `npm run build` 或 `tsc` 失敗
- `uvicorn` 啟動失敗
- `alembic upgrade head` 失敗
- 任何 CI/CD 構建錯誤

**工作原則**：
- 只修復 build 錯誤，不做架構改動
- 最小 diff 原則
- 修復後立即重新構建驗證

---

### 2.7 Frontend Designer（前端設計師）

**職責**：設計和實現高質量前端界面

**調用方式**：
```
技能: frontend-design
```

**觸發時機**：
- 創建新頁面或組件
- 重新設計現有 UI
- 需要響應式設計調整

**GoGoJap 前端規範**：
- 設計系統：Future Tech 風格（HoloCard, PulseStatus, DataStreamBg）
- UI 庫：shadcn/ui + Radix UI + Tailwind CSS
- 動畫：Framer Motion（PageTransition, StaggerContainer）
- 狀態：TanStack Query 5（所有 API 調用）
- 圖表：Recharts
- 響應式：手機優先（< 640px 簡化佈局）

---

### 2.8 Doc Updater（文檔官）

**職責**：保持文檔與代碼同步

**調用方式**：
```
subagent_type: "doc-updater"
```

**觸發時機**（依據 CLAUDE.md `<architecture_documentation>` 規則）：
- 創建/刪除/移動文件或目錄
- 模組重組、層級調整
- 職責重新劃分
- 新增 API 端點
- 數據庫 schema 變更

**必須更新的文件**：
- `CLAUDE.md` — 目錄結構樹、核心模塊表
- `docs/technical/DATABASE_SCHEMA.md` — 數據模型變更
- `docs/technical/ROADMAP_HKTVMALL_AI.md` — 功能進度

---

### 2.9 Refactorer（重構師）

**職責**：清理死代碼、消除重複、簡化結構

**調用方式**：
```
subagent_type: "refactor-cleaner"
subagent_type: "code-simplifier:code-simplifier"
```

**觸發時機**：
- 功能完成後，清理臨時代碼
- 發現代碼壞味道（重複、過長函數、過深嵌套）
- 依賴清理（unused imports, dead code）

**GoGoJap 已知可清理項**：
- `backend/app/services/hktvmall.py` — `HKTVMallMockClient` 類仍存在（第 11-176 行），mock 移除時漏刪
- `backend/app/connectors/claude.py` — Legacy connector，正逐步被 `ai_service.py` 取代

---

### 2.10 Debugger（除錯專家）

**職責**：系統化排錯，科學方法定位問題

**調用方式**：
```
技能: superpowers:systematic-debugging
```

**觸發時機**：
- 遇到任何 Bug 或測試失敗
- 行為不符合預期
- 性能問題排查

**工作方法**：
1. 觀察現象（錯誤信息、日誌、堆棧）
2. 形成假設（可能的原因）
3. 設計驗證（最小重現步驟）
4. 修復並驗證
5. 添加防護測試

---

## 三、開發工作流

### 3.1 新功能開發流程

```
用戶需求
    │
    ▼
┌─────────────────┐
│ 1. Brainstorming │  ← superpowers:brainstorming
│    創意探索       │     （探索需求、確認方向）
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. Architect     │  ← architect / planner / EnterPlanMode
│    架構設計       │     （文件清單、數據流、風險）
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. Explorer      │  ← Explore（如需深入理解現有代碼）
│    代碼探索       │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 4. TDD Guide     │  ← tdd-guide / testing-patterns
│    先寫測試       │     （寫失敗測試 → 確認需求）
└────────┬────────┘
         ▼
┌─────────────────┐
│ 5. 實現代碼       │  ← Claude Code 主進程
│    （讓測試通過）  │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 6. Code Review   │  ← code-reviewer [必須]
│    代碼審查       │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 7. Security Rev  │  ← security-reviewer [涉及安全時必須]
│    安全審查       │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 8. Build Check   │  ← build-error-resolver [構建失敗時]
│    構建驗證       │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 9. Doc Update    │  ← doc-updater [架構變更時]
│    文檔同步       │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 10. Cleanup      │  ← refactor-cleaner [可選]
│     代碼清理      │
└────────┬────────┘
         ▼
    完成 / Commit
```

### 3.2 Bug 修復流程

```
Bug 報告
    │
    ▼
┌─────────────────┐
│ 1. Debugger      │  ← superpowers:systematic-debugging
│    系統化排錯     │     （觀察 → 假設 → 驗證）
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. Explorer      │  ← Explore（追蹤調用鏈）
│    定位問題代碼   │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. TDD Guide     │  ← tdd-guide
│    寫重現測試     │     （先證明 Bug 存在）
└────────┬────────┘
         ▼
┌─────────────────┐
│ 4. 修復代碼       │  ← Claude Code 主進程
│    （讓測試通過）  │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 5. Code Review   │  ← code-reviewer [必須]
│    代碼審查       │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 6. Verify        │  ← superpowers:verification-before-completion
│    驗證完成       │
└────────┬────────┘
         ▼
    完成 / Commit
```

### 3.3 重構流程

```
重構需求
    │
    ▼
┌─────────────────┐
│ 1. Explorer      │  ← Explore（理解現有設計意圖）
│    全面理解       │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. Architect     │  ← architect（設計目標架構）
│    目標設計       │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. TDD Guide     │  ← tdd-guide（確保現有行為被測試覆蓋）
│    保護性測試     │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 4. Refactorer    │  ← refactor-cleaner
│    執行重構       │     + Claude Code 主進程
└────────┬────────┘
         ▼
┌─────────────────┐
│ 5. Code Review   │  ← code-reviewer [必須]
│    審查重構       │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 6. Doc Update    │  ← doc-updater [必須]
│    更新架構文檔   │
└────────┬────────┘
         ▼
    完成 / Commit
```

---

## 四、Agent 調用速查表

### 4.1 按 subagent_type 調用

| Agent | subagent_type | 用途 |
|-------|--------------|------|
| 架構師 | `architect` | 系統設計、架構決策 |
| 架構師 | `planner` | 功能實現計劃 |
| 偵察兵 | `Explore` | 深度代碼探索 |
| 測試先行 | `tdd-guide` | TDD 開發 |
| 審查官 | `code-reviewer` | 代碼質量審查 |
| 安全官 | `security-reviewer` | 安全漏洞檢測 |
| 修復師 | `build-error-resolver` | 構建錯誤修復 |
| 文檔官 | `doc-updater` | 文檔同步 |
| 重構師 | `refactor-cleaner` | 死代碼清理 |
| 重構師 | `code-simplifier:code-simplifier` | 代碼簡化 |
| 前端設計 | `feature-dev:code-architect` | 前端功能架構 |
| 前端探索 | `feature-dev:code-explorer` | 前端代碼分析 |
| 前端審查 | `feature-dev:code-reviewer` | 前端代碼審查 |

### 4.2 按 Skill 調用

| Agent | Skill 名稱 | 用途 |
|-------|-----------|------|
| 架構師 | `superpowers:brainstorming` | 創意探索（功能前必用） |
| 架構師 | `superpowers:writing-plans` | 結構化計劃 |
| 審查官 | `superpowers:requesting-code-review` | 請求代碼審查 |
| 審查官 | `code-review:code-review` | PR 級別審查 |
| 安全官 | `security-review` | 安全審查 |
| 測試先行 | `superpowers:test-driven-development` | TDD 流程 |
| 測試先行 | `testing-patterns` | GoGoJap 測試模式 |
| 除錯專家 | `superpowers:systematic-debugging` | 系統化除錯 |
| 前端設計 | `frontend-design` | UI 設計與實現 |
| 驗證 | `superpowers:verification-before-completion` | 完成前驗證 |

---

## 五、並行調度策略

### 5.1 可並行的 Agent 組合

```python
# 探索 + 測試模式研究（獨立任務，可同時進行）
Task(subagent_type="Explore", prompt="分析 competitors API 的完整調用鏈")
Task(subagent_type="Explore", prompt="分析前端 competitors 頁面的狀態管理")

# 後端審查 + 前端審查（獨立代碼庫）
Task(subagent_type="code-reviewer", prompt="審查 backend/app/api/v1/pricing.py 的修改")
Task(subagent_type="code-reviewer", prompt="審查 frontend/src/app/pricing-approval/page.tsx 的修改")

# 安全審查 + 構建檢查（獨立關注點）
Task(subagent_type="security-reviewer", prompt="檢查新增 API 端點的安全性")
Task(subagent_type="build-error-resolver", prompt="修復 TypeScript 構建錯誤")
```

### 5.2 必須串行的 Agent 序列

```
Architect → TDD Guide → 實現 → Code Review → Security Review
   (1)         (2)       (3)       (4)            (5)
```

---

## 六、GoGoJap 專案知識庫

### 6.1 後端關鍵路徑

```
backend/
├── app/
│   ├── api/v1/          # 27+ 路由模組（FastAPI Router）
│   ├── models/          # 54 張表（SQLAlchemy 2.0 async）
│   ├── schemas/         # Pydantic v2 Schema
│   ├── services/        # 30+ 業務邏輯服務
│   │   ├── agent/       # AI Agent「Jap仔」
│   │   └── workflow/    # 排程引擎
│   ├── connectors/      # 4 個外部 API 連接器
│   ├── tasks/           # Celery 任務（5 個定時任務）
│   └── config.py        # 集中配置
├── alembic/             # 數據庫遷移
└── tests/               # pytest 測試
```

### 6.2 前端關鍵路徑

```
frontend/src/
├── app/                 # Next.js 14 App Router（9 個頁面）
├── components/          # React 組件
│   ├── ui/              # shadcn/ui + Future Tech 設計系統
│   ├── competitors/     # 競品相關組件
│   ├── content/         # 內容生成組件
│   └── agent/           # AI Agent 組件
└── lib/
    ├── api.ts           # 集中 API 客戶端（60+ 方法）
    └── utils.ts         # 工具函數
```

### 6.3 常見修改模式

**新增 API 端點**：
1. `backend/app/api/v1/{module}.py` — 路由定義
2. `backend/app/schemas/{module}.py` — 請求/回應 Schema
3. `backend/app/services/{service}.py` — 業務邏輯
4. `backend/app/models/{model}.py` — 數據模型（如需）
5. `frontend/src/lib/api.ts` — 前端 API 方法
6. `frontend/src/app/{page}/page.tsx` — 前端頁面

**新增數據表**：
1. `backend/app/models/{model}.py` — SQLAlchemy Model
2. `backend/alembic/versions/` — Alembic 遷移腳本
3. `backend/app/schemas/{schema}.py` — Pydantic Schema
4. 運行 `alembic revision --autogenerate -m "描述"`
5. 運行 `alembic upgrade head`

---

## 七、質量閘門定義

### 7.1 不可跳過的閘門

| 閘門 | Agent | 條件 |
|------|-------|------|
| **Code Review** | code-reviewer | 每次修改 ≥3 文件 |
| **Security Review** | security-reviewer | 涉及 API 端點 / 用戶輸入 / Token |
| **Build Check** | build-error-resolver | 每次構建失敗 |
| **Doc Sync** | doc-updater | 架構級變更（新增/刪除/移動文件） |

### 7.2 推薦但可選的閘門

| 閘門 | Agent | 條件 |
|------|-------|------|
| **TDD** | tdd-guide | 新功能 / Bug 修復 |
| **Architecture Review** | architect | 影響多模組的修改 |
| **Cleanup** | refactor-cleaner | 功能完成後 |
| **E2E Test** | e2e-runner | 用戶流程變更 |

---

## 八、Agent 配置建議

### 8.1 推薦的 model 選擇

| Agent | 推薦 model | 理由 |
|-------|-----------|------|
| Architect | `opus` | 需要深度思考和架構決策 |
| Explorer | `sonnet` | 搜索和分析，速度優先 |
| TDD Guide | `sonnet` | 測試生成，平衡速度和質量 |
| Code Reviewer | `opus` | 需要深度審查，不能漏檢 |
| Security Reviewer | `opus` | 安全問題不能遺漏 |
| Build Fixer | `haiku` | 簡單的構建錯誤修復，速度優先 |
| Frontend Designer | `sonnet` | UI 實現，平衡速度和質量 |
| Doc Updater | `haiku` | 文檔同步，結構化任務 |
| Refactorer | `sonnet` | 代碼清理，需要理解上下文 |
| Debugger | `opus` | 需要深度推理定位根因 |

### 8.2 並行 vs 串行策略

```
快速任務（haiku/sonnet）→ 盡量並行
深度任務（opus）         → 串行執行，節省 Token
探索任務                 → 後台執行（run_in_background=true）
```

---

## 九、與 CLAUDE.md 的關係

本文檔定義的 Agent Team 與 `CLAUDE.md` 中的規則互補：

| CLAUDE.md 規則 | 對應 Agent |
|----------------|-----------|
| `<philosophy_good_taste>` — 消除特殊情況 | Code Reviewer 負責檢查 |
| `<philosophy_simplicity>` — 函數短小 | Refactorer 負責執行 |
| `<code_smells>` — 代碼壞味道 | Code Reviewer 負責識別 |
| `<architecture_documentation>` — 文檔同步 | Doc Updater 負責執行 |
| `<execution_habits>` — 不猜接口、不臆想業務 | Explorer 負責先查實際代碼 |
| `<code_output_structure>` — 品味自檢 | Code Reviewer 負責驗證 |

---

## 附錄：快速參考卡

```
場景                          → 調用
────────────────────────────────────────────
開始新功能                     → Skill(superpowers:brainstorming)
                                → EnterPlanMode / Task(architect)
不確定代碼在哪                 → Task(Explore)
寫測試                         → Task(tdd-guide)
代碼寫完了                     → Task(code-reviewer) [必須]
涉及安全敏感操作               → Task(security-reviewer) [必須]
構建失敗                       → Task(build-error-resolver)
遇到 Bug                      → Skill(superpowers:systematic-debugging)
要做新 UI                      → Skill(frontend-design)
改了架構                       → Task(doc-updater) [必須]
代碼很亂                       → Task(refactor-cleaner)
要做 PR                        → Skill(code-review:code-review)
完成前最終檢查                 → Skill(superpowers:verification-before-completion)
```
