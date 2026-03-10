# GoGoJap System — Code Review
**日期：** 2026-03-10  
**審查者：** Eve  
**範圍：** backend/ + frontend/src/ 全部 source files

---

## 🔴 CRITICAL（必須立即修）

### 1. `/register` 端點完全無保護 — 任何人可創建任意角色帳號
**檔案：** `backend/app/api/v1/auth.py` 第 162 行

```python
@router.post("/register", response_model=UserSchema)
async def register_user(user_in: UserCreate, db: ...):
    # ⚠️ 無任何 auth 要求！
```

`UserCreate` 接受 `role` 欄位（預設 VIEWER，但可傳 ADMIN）。任何人可：
1. `POST /api/v1/auth/register` 加 `{"email": "evil@x.com", "password": "xxx", "role": "admin"}`
2. 立即獲得 admin 權限登入

**修復：**
```python
@router.post("/register", response_model=UserSchema)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(deps.get_current_active_superuser),  # ⬅️ 加呢行
) -> Any:
    # 且強制設 role=VIEWER，唔信客戶端傳嘅 role
    user_in.role = UserRole.VIEWER
```

---

### 2. `.env` 含真實 Secrets（DB、Telegram、Nano Banana、R2、Firecrawl）
**檔案：** `backend/.env`

雖然 `.gitignore` 已忽略，但本地 `.env` 含生產用 credentials：
- Neon PostgreSQL 連接串（含密碼）：`npg_6TXrmNOqePM4`
- Firecrawl API Key：`fc-cdaa6cb394d146c98245478aee91a5a8`
- Telegram Bot Token：`8580480031:AAGoRaIyMkq9wDv55WL5QmJyCt4aSQsmAVQ`
- Nano Banana API Key：`sk-DICIZZnXfXP6Jf6fYc05uRDZKv1Iptu5P39Cja3wuRLUhNVa`
- Cloudflare R2 keys：`cb143b4d307c80937d1429ff7bb6bd81` / `bced1e3dd2304b4c4c34ecb9719d45700c08f0b77790afdb2947dadead9d5669`
- AI 中轉 API Key：`sk-24ImtG1JBQGNo3mdL1QHPNGwtacnlCJctWfs5JhLujGH1vOB`

**風險：** 本地電腦被入侵或意外 commit 就全部洩漏。

**建議：**
- Zeabur production 用 Environment Variables，唔要 commit `.env`
- 考慮 rotate 已暴露的 Firecrawl key（已在本地 `.env`）
- 開發環境用 `.env.local` 存假 key，真 key 只在 Zeabur secrets

---

### 3. SSL 驗證被完全禁用（MITM 風險）
**檔案：** `backend/app/connectors/hktv_api.py` 第 135 行, `hktv_http_client.py` 第 171 行

```python
self._client = httpx.AsyncClient(verify=False)
```

`verify=False` = 完全不驗證 SSL 憑證，任何 MITM 攻擊者可攔截 HKTVmall API 通訊，注入假數據（觸發假警報、價格誤判）。

**修復：**
```python
self._client = httpx.AsyncClient(
    verify=True,  # 或指定 certifi 路徑
    timeout=self.REQUEST_TIMEOUT
)
```

若 HKTVmall 有自簽 cert，用 `verify="/path/to/cert.pem"` 而非 `verify=False`。

---

## 🟠 HIGH（盡快修）

### 4. Rate Limiter 用 In-Memory Dict，多實例部署會失效
**檔案：** `backend/app/main.py` 第 24-115 行

`RateLimitMiddleware` 用 `defaultdict` 儲存 IP 請求記錄。問題：
- Zeabur 任何時候可能起多個 instance —— 每個 instance 有獨立記錄，rate limit 實際上 ÷N
- 60 req/min 實際變成 60N req/min（N = instance 數）

**修復：** 改用 Redis-based rate limiting（`redis_url` 已有設定）：
```python
from app.tasks.celery_app import redis_client
# 用 Redis INCR + EXPIRE 做 sliding window
```

---

### 5. JWT Access Token 無 Refresh Token，24 小時後強制重新登入
**檔案：** `backend/app/core/security.py`

`ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24`（1 天），無 refresh token 機制。
- 用戶 token 過期 → 直接 401，需重新 Google 登入
- 更嚴重：token 無法 revoke（JWT 係 stateless）—— 即使 revoke 用戶，舊 token 24 小時內仍有效

**建議：**
- 加 refresh token（存 DB，可 revoke）
- 或縮短 access token 至 1 小時 + Redis blacklist for logout

---

### 6. `database.py` SSL Context 禁用 Hostname Check
**檔案：** `backend/app/models/database.py` 第 71-72 行

```python
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE
```

Neon PostgreSQL 連接 SSL 完全不驗證。雖然 DB 用 pgbouncer，但這等同 HTTP 而非 HTTPS。

**修復：**
```python
ssl_ctx = ssl.create_default_context()
# 唔要改 check_hostname 同 verify_mode
# Neon 有正規 CA-signed cert，直接用預設就可以
```

---

### 7. Agent Chat API 無輸入長度限制
**檔案：** `backend/app/api/v1/agent.py`（需確認）

根據 `lib/api.ts` 的 `agentChat()` 呼叫，無 content 長度 validation，用戶可發超長 prompt 消耗 AI token 配額（DoS）。

**建議：** 加 `max_length=4096` 到 AgentChat schema。

---

### 8. 競品配對：`match_level=3` 仍自動設為 is_match=True
**檔案：** `backend/app/services/competitor_matcher.py`（MEMORY.md 記錄過的已知問題）

Level 3 相關品類（如牡丹蝦 → 白蝦仁）被自動確認為配對，影響 Pricer 準確度。此問題已知但 `un_match_all.py` 仍 pending。

---

## 🟡 MEDIUM（Tech Debt）

### 9. `RateLimitMiddleware` 記憶體洩漏風險
**檔案：** `backend/app/main.py` 第 68-74 行

清理機制 `_cleanup_interval = 300` 秒，但 `_requests` dict 無上限。高流量下（DDoS、bot）可能積累數百萬 IP 記錄，耗盡記憶體。

**建議：** 加上限：`if len(self._requests) > 10000: # force cleanup`

---

### 10. Frontend scrape route 有 console.log token 相關輸出
**檔案：** `frontend/src/app/api/v1/scrape/route.ts` 第 130 行, `scraper.config.ts` 第 168 行

雖然 `scraper.config.ts` 用了 `getMaskedAPIKey()`，但 `route.ts` 有 `console.log` 輸出 keyword + targetUrl（可能含商業情報），在 production server logs 可見。

---

### 11. `auth.py` 登入失敗錯誤訊息過詳細（User Enumeration）
**檔案：** `backend/app/api/v1/auth.py` 第 28-35 行

```python
if not user or not security.verify_password(...):
    raise HTTPException(detail="Incorrect email or password")
elif not user.is_active:
    raise HTTPException(detail="Inactive user")  # ⬅️ 確認帳號存在！
```

攻擊者可區分：不存在帳號 vs 存在但禁用帳號 vs 密碼錯誤。

**建議：** 統一返回 `"Invalid credentials"` 不論哪種情況。

---

### 12. `init_db()` 內有 Raw ALTER TABLE，Migration 策略混亂
**檔案：** `backend/app/models/database.py` 第 97-120 行

同時用兩套 migration 策略：
1. `alembic/versions/` — 正規 Alembic migrations
2. `run_migrations()` — Startup 時跑 raw ALTER TABLE

兩者可能衝突。建議統一用 Alembic，刪除 `run_migrations()`。

---

### 13. `GlobalChatWidget.tsx` 拖曳狀態 cursor 不會即時更新
**檔案：** `frontend/src/components/GlobalChatWidget.tsx`

```jsx
className={isDragging.current ? "cursor-grabbing" : "cursor-grab"}
```

`isDragging.current` 係 ref（非 state），React 不會 re-render 更新 class。拖曳時 cursor 保持 `grab` 而非 `grabbing`。

**修復：** 加一個 `isDraggingState` useState 配合 ref。

---

### 14. `competitor_matcher.py` 缺乏 Retry 機制
**檔案：** `backend/app/services/competitor_matcher.py`

搜索 HKTVmall 失敗時直接返回空結果，無 retry。MEMORY.md 記錄嘅「爬蟲智能重試」功能尚未實現。

---

### 15. Celery Tasks 缺乏 Idempotency
**檔案：** `backend/app/tasks/scrape_tasks.py`

Scrape tasks 如果 crash 後重試，可能插入重複 PriceSnapshot。無 `unique_together` 或 deduplication 邏輯（除部分 `ON CONFLICT` 處理）。

---

## 🟢 LOW（Nice-to-Have）

### 16. `next.config.js` 缺 Security Headers
**檔案：** `frontend/next.config.js`

Backend 有 `SecurityHeadersMiddleware`，但 Next.js frontend 本身無設 `Content-Security-Policy`、`X-Frame-Options` 等。建議加：

```js
async headers() {
  return [{
    source: '/(.*)',
    headers: [
      { key: 'X-Frame-Options', value: 'DENY' },
      { key: 'X-Content-Type-Options', value: 'nosniff' },
    ]
  }]
}
```

---

### 17. 大量 tmpclaude-* 目錄殘留（Git Hygiene）
**位置：** Root, `backend/`, `frontend/`

唔知係唔係已 gitignored — 建議執行 `git clean -fdx --dry-run` 確認，並加 `.gitignore` 規則：`tmpclaude-*-cwd`

---

### 18. `append.py`, `write_comp_page.py` 等 Root Scripts 無文件
**位置：** Project root

`append.py`, `patch_report_generator.py`, `write_comp_page.py` 等 standalone scripts 功能不明，可能係舊工具。建議加 README 或刪除。

---

### 19. `backend/gogojap.db` SQLite 檔案係 Dev Artifact
**位置：** `backend/gogojap.db`

確保此檔案在 `.gitignore` 中，唔要 commit 本地 DB 到 repo（可能含測試數據）。

---

### 20. `UserCreate` Schema 允許客戶端設定 `is_active`
**檔案：** `backend/app/schemas/user.py`

```python
class UserBase:
    is_active: Optional[bool] = True  # 可被 UserCreate 繼承
```

即使修復 `/register` 端點，`is_active` 也不應由客戶端設定。建議從 `UserCreate` 移除。

---

## 優先行動清單

| 優先 | 問題 | 估計工時 |
|------|------|---------|
| 🔴 立即 | `/register` 加 admin 保護 | 15 分鐘 |
| 🔴 立即 | `.env` secrets review + 考慮 rotate | 30 分鐘 |
| 🔴 立即 | SSL `verify=False` 改回 `True` | 15 分鐘 |
| 🟠 今週 | Rate limiter 改 Redis | 2-3 小時 |
| 🟠 今週 | JWT refresh token | 4-6 小時 |
| 🟠 今週 | DB SSL cert 驗證修復 | 15 分鐘 |
| 🟡 下週 | Migration 策略統一（Alembic only） | 2 小時 |
| 🟡 下週 | User enumeration 修復 | 30 分鐘 |
| 🟡 下週 | Chat widget cursor fix | 15 分鐘 |

---

## 整體評價

**架構：** 8/10 — 結構清晰，RBAC 完善，分層清楚（router → service → model），有 async/await，有 OpenAPI。

**安全：** 5/10 — 有 security headers、rate limit、CORS 設定，但 `/register` 漏洞 + SSL 禁用係嚴重硬傷。

**可靠性：** 7/10 — Error handling 普遍有，但部分 `except: pass` 需注意。

**代碼品質：** 8/10 — TypeScript/Python 都有 type hints，有 docstring，命名規範。Tech debt 主要係 migration 策略不統一。

**前端：** 7/10 — Next.js App Router 用得正確，React Query 管理 server state，有 error/loading states。缺 security headers。
