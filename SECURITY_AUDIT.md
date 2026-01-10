# GoGoJap 安全審計報告

> **審計日期**: 2026-01-10
> **審計範圍**: Frontend (Next.js) + Backend (FastAPI)
> **審計類型**: 靜態代碼分析 + 配置審查

---

## 目錄

- [執行摘要](#執行摘要)
- [風險等級說明](#風險等級說明)
- [關鍵漏洞 (CRITICAL)](#關鍵漏洞-critical)
- [高危漏洞 (HIGH)](#高危漏洞-high)
- [中等風險 (MEDIUM)](#中等風險-medium)
- [低風險 (LOW)](#低風險-low)
- [安全優勢](#安全優勢)
- [修復優先順序](#修復優先順序)
- [修復代碼範例](#修復代碼範例)
- [安全檢查清單](#安全檢查清單)

---

## 執行摘要

| 嚴重程度 | 數量 |
|----------|------|
| 🔴 CRITICAL | 4 |
| 🟠 HIGH | 4 |
| 🟡 MEDIUM | 9 |
| 🟢 LOW | 2 |

**整體評估**: 代碼庫具備良好的安全基礎架構（ORM、密碼哈希、RBAC），但存在**關鍵的生產環境配置漏洞**，需在部署前立即修復。

---

## 風險等級說明

| 等級 | 定義 | 修復時間 |
|------|------|----------|
| 🔴 CRITICAL | 可直接導致系統被入侵或數據洩露 | 立即 |
| 🟠 HIGH | 可被攻擊者利用造成重大損害 | 1-3 天 |
| 🟡 MEDIUM | 存在安全風險但利用難度較高 | 1-2 週 |
| 🟢 LOW | 輕微風險或資訊洩露 | 按計劃處理 |

---

## 關鍵漏洞 (CRITICAL)

### C-01: 硬編碼預設 Secret Key

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/app/config.py:16` |
| **類型** | 認證繞過 |
| **CVSS** | 9.8 |

**問題代碼**:
```python
secret_key: str = Field(default="dev-secret-key", alias="SECRET_KEY")
```

**風險說明**:
- 若環境變量 `SECRET_KEY` 未設置，系統使用硬編碼的 `dev-secret-key`
- 攻擊者可利用此預設值偽造任意 JWT token
- 可冒充任何用戶（包括管理員）訪問系統

**修復方案**:
```python
# 移除預設值，強制要求環境變量
secret_key: str = Field(..., alias="SECRET_KEY")

# 或添加驗證器
@field_validator('secret_key')
@classmethod
def validate_secret_key(cls, v):
    if v == "dev-secret-key" or len(v) < 32:
        raise ValueError("SECRET_KEY must be a strong random string (min 32 chars)")
    return v
```

**驗證方式**:
```bash
# 確認環境變量已設置
echo $SECRET_KEY | wc -c  # 應大於 32

# 生成安全的 secret key
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

### C-02: 生產環境 CORS 完全開放

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/app/main.py:48-60` |
| **類型** | 跨域安全 |
| **CVSS** | 9.1 |

**問題代碼**:
```python
if not settings.debug:
    allowed_origins = ["*"]  # 生產環境允許所有來源！

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False if allowed_origins == ["*"] else True,
    allow_methods=["*"],      # 允許所有方法
    allow_headers=["*"],      # 允許所有標頭
    expose_headers=["*"],     # 暴露所有響應標頭
)
```

**風險說明**:
- 任何網站都可以調用你的 API
- CSRF 攻擊完全可行
- 敏感數據可被惡意網站讀取
- 用戶在訪問惡意網站時，其登錄狀態可被利用

**修復方案**:
```python
# 明確指定允許的來源
if settings.debug:
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
else:
    allowed_origins = [
        "https://gogojap.example.com",      # 你的生產域名
        "https://admin.gogojap.example.com", # 管理後台域名
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=["Content-Type", "X-Total-Count"],
)
```

---

### C-03: 敏感環境變量可能被提交到版本控制

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/.env`, `frontend/.env.local` |
| **類型** | 憑證洩露 |
| **CVSS** | 9.0 |

**風險說明**:
- `.env` 檔案包含數據庫密碼、API 密鑰等敏感信息
- 若被提交到 Git，任何有倉庫訪問權限的人都可獲取
- 即使後來刪除，仍存在於 Git 歷史中

**修復方案**:

1. 確認 `.gitignore` 包含以下內容:
```gitignore
# Environment files
.env
.env.*
.env.local
.env.*.local
!.env.example
!.env.template

# Backend specific
backend/.env
backend/*.env

# Frontend specific
frontend/.env.local
frontend/.env.*.local
```

2. 若已提交，從歷史中移除:
```bash
# 使用 git-filter-repo (推薦)
pip install git-filter-repo
git filter-repo --path backend/.env --invert-paths

# 或使用 BFG Repo-Cleaner
bfg --delete-files .env
git reflog expire --expire=now --all && git gc --prune=now --aggressive
```

3. 立即輪換所有已洩露的憑證

---

### C-04: DEBUG 模式預設開啟

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/app/config.py:15` |
| **類型** | 資訊洩露 |
| **CVSS** | 7.5 |

**問題代碼**:
```python
debug: bool = Field(default=True, alias="DEBUG")
```

**風險說明**:
- 生產環境若未設置 `DEBUG=false`，將默認開啟調試模式
- Swagger UI (`/docs`) 和 ReDoc (`/redoc`) 將對外暴露
- 攻擊者可獲取完整 API 結構進行針對性攻擊
- 錯誤信息可能包含敏感堆棧信息

**修復方案**:
```python
# 預設關閉 DEBUG
debug: bool = Field(default=False, alias="DEBUG")

# 或添加環境檢測
@field_validator('debug')
@classmethod
def validate_debug(cls, v, info):
    app_env = info.data.get('app_env', 'production')
    if v and app_env == 'production':
        import warnings
        warnings.warn("DEBUG is enabled in production!", SecurityWarning)
    return v
```

---

## 高危漏洞 (HIGH)

### H-01: Mock Token 開發後門

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/app/api/v1/auth.py:65-68` |
| **類型** | 認證繞過 |

**問題代碼**:
```python
if settings.app_env == "development" and login_data.credential.startswith("mock_"):
    # Mock logic for testing without real Google creds
    id_info = {"email": "mock@example.com", "name": "Mock User"}
```

**風險說明**:
- 若生產環境誤設為 `development`，攻擊者可使用 `mock_` 前綴繞過認證
- 測試邏輯不應存在於生產代碼中

**修復方案**:
```python
# 方案 1: 完全移除 mock 邏輯，使用專門的測試配置
# 方案 2: 添加額外的安全檢查
if settings.app_env == "development" and settings.allow_mock_auth:
    if login_data.credential.startswith("mock_") and request.client.host in ["127.0.0.1", "::1"]:
        # 僅允許本地請求
        id_info = {"email": "mock@example.com", "name": "Mock User"}
```

---

### H-02: 缺少安全響應標頭

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/app/main.py` |
| **類型** | 多種攻擊向量 |

**缺少的標頭**:
| 標頭 | 用途 |
|------|------|
| `X-Content-Type-Options` | 防止 MIME 類型嗅探 |
| `X-Frame-Options` | 防止點擊劫持 |
| `X-XSS-Protection` | XSS 過濾器 |
| `Strict-Transport-Security` | 強制 HTTPS |
| `Content-Security-Policy` | 限制資源加載來源 |
| `Referrer-Policy` | 控制 Referrer 信息 |

**修復方案**:
```python
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # 基礎安全標頭
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # HTTPS 相關 (僅生產環境)
        if not settings.debug:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # CSP (根據需要調整)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://accounts.google.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.anthropic.com; "
            "frame-ancestors 'none';"
        )

        return response

# 在 main.py 中添加
app.add_middleware(SecurityHeadersMiddleware)
```

---

### H-03: 限速未全局應用

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/app/api/v1/` (所有 endpoints) |
| **類型** | DoS / 暴力破解 |

**風險說明**:
- 限速基礎設施已實現 (`TokenBucketRateLimiter`)，但未應用到所有端點
- `/auth/login` 端點無限速保護，可被暴力破解
- `/scrape` 端點無保護，可被濫用消耗服務器資源

**修復方案**:
```python
# backend/app/api/deps.py - 添加限速依賴

from app.services.rate_limiter import TokenBucketRateLimiter

async def get_rate_limiter():
    return TokenBucketRateLimiter(
        redis_client=redis_client,
        max_tokens=100,
        refill_rate=10,
    )

# 全局限速中間件
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    limiter = TokenBucketRateLimiter(...)

    if not await limiter.acquire(f"global:{client_ip}", tokens=1):
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"}
        )

    return await call_next(request)

# 特定端點限速 (更嚴格)
@router.post("/login")
async def login(
    credentials: LoginRequest,
    limiter: TokenBucketRateLimiter = Depends(get_rate_limiter)
):
    if not await limiter.acquire(f"login:{credentials.email}", tokens=1, max_tokens=5):
        raise HTTPException(429, "Too many login attempts. Please try again later.")
```

---

### H-04: API Key 可能在日誌中暴露

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/app/connectors/`, `backend/app/services/` |
| **類型** | 憑證洩露 |

**風險說明**:
- 外部 API 調用的請求/響應可能被記錄
- 日誌中可能包含 API 密鑰
- 錯誤堆棧可能暴露敏感配置

**修復方案**:
```python
# backend/app/core/logging.py

import re
import logging

class SensitiveDataFilter(logging.Filter):
    """過濾日誌中的敏感數據"""

    PATTERNS = [
        (r'(api[_-]?key["\s:=]+)["\']?[\w-]{20,}["\']?', r'\1***REDACTED***'),
        (r'(password["\s:=]+)["\']?[^"\s,}]+["\']?', r'\1***REDACTED***'),
        (r'(token["\s:=]+)["\']?[\w.-]{20,}["\']?', r'\1***REDACTED***'),
        (r'(secret["\s:=]+)["\']?[\w-]{10,}["\']?', r'\1***REDACTED***'),
        (r'(Bearer\s+)[\w.-]+', r'\1***REDACTED***'),
    ]

    def filter(self, record):
        if isinstance(record.msg, str):
            for pattern, replacement in self.PATTERNS:
                record.msg = re.sub(pattern, replacement, record.msg, flags=re.IGNORECASE)
        return True

# 應用過濾器
logging.getLogger().addFilter(SensitiveDataFilter())
```

---

## 中等風險 (MEDIUM)

### M-01: JWT 過期時間過長

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/app/core/security.py:15` |
| **當前值** | 24 小時 |
| **建議值** | 15-30 分鐘 |

**問題代碼**:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day for convenience
```

**修復方案**:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 分鐘
REFRESH_TOKEN_EXPIRE_DAYS = 7     # 7 天

# 實現 refresh token 機制
@router.post("/refresh")
async def refresh_token(refresh_token: str):
    # 驗證 refresh token
    # 頒發新的 access token
    pass
```

---

### M-02: 缺少 CSRF 保護

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/app/main.py` |
| **類型** | 跨站請求偽造 |

**修復方案**:
```bash
pip install fastapi-csrf-protect
```

```python
from fastapi_csrf_protect import CsrfProtect
from pydantic import BaseModel

class CsrfSettings(BaseModel):
    secret_key: str = settings.secret_key
    cookie_samesite: str = "strict"
    cookie_secure: bool = not settings.debug

@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()

# 在需要保護的路由中
@router.post("/sensitive-action")
async def sensitive_action(csrf_protect: CsrfProtect = Depends()):
    await csrf_protect.validate_csrf()
    # ...
```

---

### M-03: JWT 存儲在 localStorage

| 屬性 | 值 |
|------|-----|
| **位置** | `frontend/src/lib/api.ts:9`, `frontend/src/components/providers/auth-provider.tsx:25,64` |
| **類型** | XSS 導致的 Token 洩露 |

**問題代碼**:
```typescript
const token = localStorage.getItem('token')
localStorage.setItem("token", res.access_token)
```

**風險說明**:
- localStorage 可被任何 JavaScript 代碼訪問
- 若存在 XSS 漏洞，攻擊者可輕易竊取 token

**修復方案** (推薦使用 httpOnly Cookie):

後端:
```python
from fastapi.responses import JSONResponse

@router.post("/login")
async def login(credentials: LoginRequest, response: Response):
    token = create_access_token(...)

    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,      # JavaScript 無法訪問
        secure=True,        # 僅 HTTPS
        samesite="strict",  # 防止 CSRF
        max_age=1800,       # 30 分鐘
    )
    return response
```

前端:
```typescript
// 不再手動管理 token，瀏覽器自動發送 cookie
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true,  // 發送 cookies
})
```

---

### M-04: 查詢參數缺少邊界驗證

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/app/api/v1/` (多個文件) |
| **類型** | DoS / 資源耗盡 |

**修復方案**:
```python
from fastapi import Query

@router.get("/items")
async def get_items(
    page: int = Query(default=1, ge=1, le=10000, description="頁碼"),
    page_size: int = Query(default=20, ge=1, le=100, description="每頁數量"),
    limit: int = Query(default=100, ge=1, le=1000, description="最大返回數量"),
):
    # ...
```

---

### M-05: 未驗證外部 URL (SSRF 風險)

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/app/api/v1/hktvmall.py` |
| **類型** | 服務端請求偽造 |

**修復方案**:
```python
from urllib.parse import urlparse

ALLOWED_DOMAINS = [
    "hktvmall.com",
    "www.hktvmall.com",
    "api.hktvmall.com",
]

def validate_url(url: str) -> bool:
    """驗證 URL 是否在允許的域名列表中"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        return any(domain == d or domain.endswith(f".{d}") for d in ALLOWED_DOMAINS)
    except Exception:
        return False

@router.post("/scrape")
async def scrape_url(url: str):
    if not validate_url(url):
        raise HTTPException(400, "URL not allowed")
    # ...
```

---

### M-06: 外部 API 響應未驗證

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/app/connectors/` |
| **類型** | 數據注入 / 崩潰 |

**修復方案**:
```python
from pydantic import BaseModel, ValidationError

class ClaudeResponse(BaseModel):
    content: str
    model: str
    usage: dict

async def call_claude_api(prompt: str) -> ClaudeResponse:
    response = await client.post(...)

    try:
        validated = ClaudeResponse(**response.json())
        return validated
    except ValidationError as e:
        logger.error(f"Invalid API response: {e}")
        raise HTTPException(502, "Invalid response from AI service")
```

---

### M-07: Token 過期檢查僅在頁面加載時執行

| 屬性 | 值 |
|------|-----|
| **位置** | `frontend/src/components/providers/auth-provider.tsx:32-35` |
| **類型** | 過期 Token 被使用 |

**修復方案**:
```typescript
// frontend/src/lib/api.ts - 添加請求攔截器

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      const decoded = jwtDecode(token)
      if (decoded.exp * 1000 < Date.now()) {
        // Token 已過期，清除並重定向
        localStorage.removeItem('token')
        window.location.href = '/login'
        return Promise.reject(new Error('Token expired'))
      }
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
```

---

### M-08: API Key 預設為空字符串

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/app/config.py:25,28,40-42` |
| **類型** | 靜默失敗 |

**問題代碼**:
```python
firecrawl_api_key: str = Field(default="", alias="FIRECRAWL_API_KEY")
anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
```

**修復方案**:
```python
from pydantic import field_validator

class Settings(BaseSettings):
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")

    @field_validator('anthropic_api_key')
    @classmethod
    def validate_anthropic_key(cls, v, info):
        app_env = info.data.get('app_env', 'production')
        if not v and app_env == 'production':
            raise ValueError("ANTHROPIC_API_KEY is required in production")
        return v
```

---

### M-09: 無 HTTPS 強制

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/app/main.py` |
| **類型** | 中間人攻擊 |

**修復方案**:
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if not settings.debug:
    app.add_middleware(HTTPSRedirectMiddleware)
```

---

## 低風險 (LOW)

### L-01: 健康檢查端點暴露環境信息

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/app/main.py:71-73` |

**問題代碼**:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "env": settings.app_env}
```

**修復方案**:
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

### L-02: 依賴版本未固定

| 屬性 | 值 |
|------|-----|
| **位置** | `backend/requirements.txt` |

**建議**:
```bash
# 生成固定版本
pip freeze > requirements.lock

# 定期檢查漏洞
pip install pip-audit
pip-audit

# 使用 dependabot 或 renovate 自動更新
```

---

## 安全優勢

本項目已具備以下良好的安全實踐：

| 項目 | 說明 |
|------|------|
| ✅ SQLAlchemy ORM | 使用參數化查詢，有效防止 SQL 注入 |
| ✅ BCrypt 密碼哈希 | 使用 `passlib[bcrypt]` 進行安全的密碼存儲 |
| ✅ RBAC 權限系統 | 完善的角色權限矩陣 (ADMIN, OPERATOR, VIEWER) |
| ✅ Pydantic 驗證 | 輸入數據有強類型驗證 |
| ✅ Redis 限速基礎 | `TokenBucketRateLimiter` 實現已就緒 |
| ✅ 異步數據庫訪問 | 使用 `asyncpg` 提高併發安全性 |
| ✅ 環境配置分離 | 使用 `pydantic-settings` 管理配置 |

---

## 修復優先順序

### Phase 1: 立即修復 (部署前必須完成)

```
┌─────────────────────────────────────────────────────────────┐
│ CRITICAL                                                     │
├─────────────────────────────────────────────────────────────┤
│ C-01  設置強 SECRET_KEY，移除預設值                          │
│ C-02  修復 CORS 配置，明確指定允許的來源                      │
│ C-03  確認 .env 已加入 .gitignore，輪換已洩露憑證            │
│ C-04  將 DEBUG 預設改為 False                                │
└─────────────────────────────────────────────────────────────┘
```

### Phase 2: 短期修復 (1-3 天)

```
┌─────────────────────────────────────────────────────────────┐
│ HIGH                                                         │
├─────────────────────────────────────────────────────────────┤
│ H-01  移除 Mock Token 後門                                   │
│ H-02  添加安全響應標頭中間件                                  │
│ H-03  將限速應用到所有公開端點                                │
│ H-04  實現日誌敏感數據過濾                                    │
└─────────────────────────────────────────────────────────────┘
```

### Phase 3: 中期改進 (1-2 週)

```
┌─────────────────────────────────────────────────────────────┐
│ MEDIUM                                                       │
├─────────────────────────────────────────────────────────────┤
│ M-01  縮短 JWT 過期時間至 30 分鐘，實現 Refresh Token        │
│ M-02  添加 CSRF 保護                                         │
│ M-03  將 JWT 改為 httpOnly Cookie 存儲                       │
│ M-04  為所有查詢參數添加邊界驗證                              │
│ M-05  實現 URL 白名單驗證                                    │
│ M-06  添加外部 API 響應驗證                                  │
│ M-07  實現前端請求攔截器檢查 Token                           │
│ M-08  為必要的 API Key 添加驗證器                            │
│ M-09  生產環境強制 HTTPS                                     │
└─────────────────────────────────────────────────────────────┘
```

### Phase 4: 持續改進

```
┌─────────────────────────────────────────────────────────────┐
│ LOW + 持續維護                                               │
├─────────────────────────────────────────────────────────────┤
│ L-01  移除健康檢查中的環境信息                               │
│ L-02  固定依賴版本，設置自動安全更新                          │
│ 持續  定期執行 pip-audit 和 npm audit                        │
│ 持續  設置安全監控和告警                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 修復代碼範例

### 完整的安全中間件配置

```python
# backend/app/core/security_middleware.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings

def setup_security_middleware(app: FastAPI):
    """配置所有安全中間件"""

    # 1. HTTPS 重定向 (僅生產環境)
    if not settings.debug:
        app.add_middleware(HTTPSRedirectMiddleware)

    # 2. 安全標頭
    app.add_middleware(SecurityHeadersMiddleware)

    # 3. CORS
    allowed_origins = (
        ["http://localhost:3000", "http://127.0.0.1:3000"]
        if settings.debug
        else ["https://gogojap.example.com"]
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
        expose_headers=["Content-Type", "X-Total-Count"],
    )

    # 4. 全局限速
    app.add_middleware(RateLimitMiddleware)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        if not settings.debug:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"

        # 實現限速邏輯...

        return await call_next(request)
```

---

## 安全檢查清單

部署前請確認以下所有項目：

### 環境配置
- [ ] `SECRET_KEY` 已設置為強隨機值 (≥64 字符)
- [ ] `DEBUG=false` 已在生產環境設置
- [ ] 所有 `.env` 文件已加入 `.gitignore`
- [ ] 數據庫連接使用 SSL/TLS
- [ ] 所有 API 密鑰已設置且非空

### 認證授權
- [ ] JWT 過期時間 ≤30 分鐘
- [ ] Refresh Token 機制已實現
- [ ] Mock/測試認證後門已移除
- [ ] CSRF 保護已啟用

### API 安全
- [ ] CORS 僅允許特定域名
- [ ] 所有端點已添加限速
- [ ] 查詢參數有邊界驗證
- [ ] 外部 URL 有白名單驗證

### 響應安全
- [ ] 所有安全標頭已配置
- [ ] HTTPS 已強制啟用
- [ ] 敏感數據未在響應中暴露

### 日誌監控
- [ ] 敏感數據過濾器已配置
- [ ] 安全事件告警已設置
- [ ] 登錄失敗監控已啟用

### 依賴安全
- [ ] `pip-audit` 檢查通過
- [ ] `npm audit` 檢查通過
- [ ] 依賴版本已固定

---

## 附錄：安全資源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security Guide](https://fastapi.tiangolo.com/tutorial/security/)
- [Next.js Security Headers](https://nextjs.org/docs/advanced-features/security-headers)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)

---

> **免責聲明**: 本報告基於靜態代碼分析，可能存在遺漏。建議定期進行專業滲透測試。
