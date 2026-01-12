# 環境變數配置說明

## 圖片生成功能配置

### Nano-Banana API 配置

```bash
# Nano-Banana API Base URL
NANO_BANANA_API_BASE=https://ai.t8star.cn/v1

# Nano-Banana API Key（必需）
NANO_BANANA_API_KEY=your-api-key-here

# 模型名稱
NANO_BANANA_MODEL=nano-banana

# 文件上傳目錄
UPLOAD_DIR=./uploads
```

### Celery 配置

```bash
# Redis URL（用於 Celery 消息隊列）
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 完整的 .env 配置示例

```bash
# =============================================
# 環境設定
# =============================================
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-here

# =============================================
# 資料庫
# =============================================
DATABASE_URL=postgresql://hktv:hktv_dev_password@localhost:5432/hktv_ops

# =============================================
# Redis
# =============================================
REDIS_URL=redis://localhost:6379/0

# =============================================
# Celery
# =============================================
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# =============================================
# AI 服務
# =============================================

# Claude AI
ANTHROPIC_API_KEY=your-anthropic-api-key
AI_MODEL=claude-sonnet-4-20250514

# Nano-Banana（圖片生成）
NANO_BANANA_API_BASE=https://ai.t8star.cn/v1
NANO_BANANA_API_KEY=your-nano-banana-api-key
NANO_BANANA_MODEL=nano-banana

# =============================================
# 文件存儲
# =============================================
UPLOAD_DIR=./uploads

# 存儲模式切換
USE_R2_STORAGE=false  # 設為 true 啟用 Cloudflare R2，false 使用本地存儲

# Cloudflare R2（當 USE_R2_STORAGE=true 時必需）
R2_ACCESS_KEY=your-r2-access-key
R2_SECRET_KEY=your-r2-secret-key
R2_BUCKET=hktv-ops-storage
R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
R2_PUBLIC_URL=https://your-public-url.com

# =============================================
# Google OAuth
# =============================================
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_ALLOWED_EMAILS=user1@example.com,user2@example.com
GOOGLE_ADMIN_EMAILS=admin@example.com
GOOGLE_OPERATOR_EMAILS=operator@example.com

# =============================================
# HKTVmall API
# =============================================
HKTVMALL_API_BASE_URL=https://merchant-oapi.shoalter.com/oapi/api
HKTVMALL_STORE_CODE=your-store-code
HKTVMALL_ACCESS_TOKEN=your-access-token

# =============================================
# 通知設定
# =============================================
NOTIFICATION_EMAIL=notifications@example.com

# Telegram
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
TELEGRAM_ENABLED=false

# =============================================
# 其他設定
# =============================================
SCRAPE_TIME=09:00
PRICE_ALERT_THRESHOLD=10
AGENT_MOCK_MODE=false
```

## 配置檢查清單

在部署前，請確保以下配置已正確設置：

### 必需配置

- [ ] `DATABASE_URL` - PostgreSQL 連接字符串
- [ ] `SECRET_KEY` - 應用密鑰（至少 32 字符）
- [ ] `NANO_BANANA_API_KEY` - 圖片生成 API 密鑰
- [ ] `REDIS_URL` - Redis 連接字符串
- [ ] `CELERY_BROKER_URL` - Celery 消息隊列
- [ ] `CELERY_RESULT_BACKEND` - Celery 結果後端

### 可選配置

- [ ] `USE_R2_STORAGE` - 啟用 R2 存儲（生產環境推薦）
- [ ] `R2_ACCESS_KEY` - Cloudflare R2 Access Key（當 USE_R2_STORAGE=true 時必需）
- [ ] `R2_SECRET_KEY` - Cloudflare R2 Secret Key（當 USE_R2_STORAGE=true 時必需）
- [ ] `R2_ENDPOINT` - Cloudflare R2 端點 URL（當 USE_R2_STORAGE=true 時必需）
- [ ] `R2_PUBLIC_URL` - R2 公開訪問 URL（當 USE_R2_STORAGE=true 時必需）
- [ ] `ANTHROPIC_API_KEY` - Claude AI（其他 AI 功能需要）
- [ ] `GOOGLE_CLIENT_ID` - Google OAuth 登入
- [ ] `TELEGRAM_BOT_TOKEN` - Telegram 通知

## 安全注意事項

1. **生產環境**：
   - 不要使用 `DEBUG=true`
   - 使用強隨機密鑰作為 `SECRET_KEY`
   - 使用 HTTPS

2. **API 密鑰**：
   - 不要將密鑰提交到版本控制
   - 定期輪換密鑰
   - 使用環境變數管理工具（如 Vault, AWS Secrets Manager）

3. **資料庫**：
   - 使用強密碼
   - 限制資料庫訪問權限
   - 定期備份

4. **Redis**：
   - 設置密碼保護
   - 限制訪問 IP
   - 使用 TLS 連接（生產環境）
