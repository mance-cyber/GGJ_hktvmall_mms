# Zeabur 部署 Celery Worker 指南

## 问题诊断

**症状**：图片生成任务创建后，卡在 0% 一直"处理中"

**原因**：Zeabur 只部署了 Backend API 服务，Celery Worker 服务未启动

**解决方案**：在 Zeabur 部署一个独立的 Celery Worker 服务

---

## 部署步骤

### 1️⃣ 在 Zeabur 项目中添加新服务

1. 登录 Zeabur 控制台
2. 打开项目：**GoGoJap HKTVmall AI System**
3. 点击 **Add Service** → **Git**
4. 选择同一个 GitHub 仓库（`GGJ_hktvmall_mms`）

### 2️⃣ 配置 Celery Worker 服务

**服务名称**：`celery-worker`

**构建配置**：
- **Root Directory**: `backend`
- **Dockerfile Path**: `Dockerfile`（使用相同的 Dockerfile）

### 3️⃣ 设置环境变量

在 Celery Worker 服务中，配置以下环境变量：

#### 🔴 必需环境变量

| 环境变量 | 值 | 说明 |
|---------|-----|------|
| `SERVICE_TYPE` | `worker` | ⚠️ **关键**：指定启动 Celery Worker |
| `DATABASE_URL` | `postgresql+asyncpg://...` | 数据库连接（与 Backend 相同） |
| `REDIS_URL` | `redis://...` | Redis 连接（与 Backend 相同） |
| `CELERY_BROKER_URL` | `redis://...` | Celery 消息队列（与 REDIS_URL 相同） |
| `CELERY_RESULT_BACKEND` | `redis://...` | Celery 结果存储（与 REDIS_URL 相同） |
| `SECRET_KEY` | `(你的 SECRET_KEY)` | 应用密钥（与 Backend 相同） |

#### 🟡 图片生成相关环境变量

| 环境变量 | 值 | 说明 |
|---------|-----|------|
| `NANO_BANANA_API_KEY` | `(你的 API Key)` | Nano-Banana 图片生成 API |
| `NANO_BANANA_API_BASE` | `https://ai.t8star.cn/v1` | API 基础 URL |
| `NANO_BANANA_MODEL` | `nano-banana` | 使用的模型 |

#### 🟢 Cloudflare R2 存储环境变量

| 环境变量 | 值 | 说明 |
|---------|-----|------|
| `USE_R2_STORAGE` | `true` | 启用 R2 存储 |
| `R2_ACCESS_KEY` | `(你的 Access Key)` | R2 访问密钥 |
| `R2_SECRET_KEY` | `(你的 Secret Key)` | R2 密钥 |
| `R2_BUCKET` | `gogojap-image-generation` | R2 存储桶名称 |
| `R2_ENDPOINT` | `https://...r2.cloudflarestorage.com` | R2 端点 |
| `R2_PUBLIC_URL` | `https://...` | R2 公开访问 URL |

#### 🔵 其他可选环境变量

| 环境变量 | 值 | 说明 |
|---------|-----|------|
| `ANTHROPIC_API_KEY` | `(你的 API Key)` | Claude AI（如需 AI 功能） |
| `APP_ENV` | `production` | 运行环境 |

### 4️⃣ 部署并验证

1. 点击 **Deploy** 启动 Celery Worker 服务
2. 查看日志，确认看到：
   ```
   🔧 Starting Celery worker...
   celery@... ready.
   ```

3. 测试图片生成功能：
   - 前端创建任务并上传图片
   - 点击"开始生成"
   - 应该看到进度从 0% → 10% → 20% ... → 100%

---

## 验证清单

- [ ] Backend API 服务正常运行
- [ ] Celery Worker 服务已部署
- [ ] Celery Worker 环境变量 `SERVICE_TYPE=worker` 已设置
- [ ] Redis 服务可访问（Zeabur 自动部署）
- [ ] Celery Worker 日志显示 "ready"
- [ ] 图片生成任务能正常完成

---

## 故障排查

### ❌ Worker 启动失败

**检查**：
- 确认 `SERVICE_TYPE=worker` 已设置
- 查看日志中的错误信息
- 确认所有必需环境变量已配置

### ❌ 任务仍然卡在 0%

**检查**：
1. Worker 日志是否有任务执行记录
2. Redis 连接是否正常
3. `CELERY_BROKER_URL` 与 Backend 的 `REDIS_URL` 是否一致

### ❌ 图片生成失败

**检查**：
- `NANO_BANANA_API_KEY` 是否正确
- `R2_ACCESS_KEY`、`R2_SECRET_KEY` 是否正确
- Worker 日志中的详细错误信息

---

## 架构示意图

```
┌─────────────────────────────────────────────────────┐
│                   Zeabur 项目                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐      ┌──────────────┐            │
│  │   Frontend   │─────▶│   Backend    │            │
│  │  (Next.js)   │      │   (FastAPI)  │            │
│  └──────────────┘      └──────┬───────┘            │
│                               │                     │
│                               ▼                     │
│                        ┌─────────────┐             │
│                        │    Redis    │             │
│                        │  (消息队列)  │             │
│                        └──────┬──────┘             │
│                               │                     │
│                               ▼                     │
│                     ┌─────────────────┐            │
│                     │ Celery Worker   │            │
│                     │ ⚙️ SERVICE_TYPE=worker       │
│                     │ ✅ 处理图片生成任务           │
│                     └─────────────────┘            │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 后续优化建议

1. **监控**：添加 Celery Flower 监控服务
2. **扩展**：根据负载调整 Worker 并发数（`--concurrency=N`）
3. **定时任务**：部署 Celery Beat 服务（`SERVICE_TYPE=beat`）

---

## 联系支持

如遇问题，请提供：
- Celery Worker 日志
- Backend API 日志
- 环境变量配置截图
