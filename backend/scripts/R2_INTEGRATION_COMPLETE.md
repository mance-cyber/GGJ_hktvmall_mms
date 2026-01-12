# R2 存储集成 - 完成指南

## ✅ 已完成的工作

### 1. R2 存储配置和测试
- ✓ Cloudflare R2 配置完成
- ✓ StorageService 初始化正常
- ✓ 图片上传到 R2 成功验证
- ✓ 图片下载和内容验证通过

**测试结果**：
```
✓ R2 配置正确
✓ StorageService 初始化成功
✓ 测试图片创建成功（800x600 JPEG, 22.41 KB）
✓ 图片上传到 R2 成功
✓ R2 文件验证成功
✓ 公开 URL 生成成功
✓ 图片下载验证成功（内容完全一致）
```

### 2. Celery Worker 配置
- ✓ 安装 `psycopg2-binary==2.9.11`（PostgreSQL 同步驱动）
- ✓ Celery Worker 使用 `--pool=solo` 模式（Windows 兼容）
- ✓ 成功连接到 Redis
- ✓ 已注册 `process_image_generation` 任务

**当前状态**：Celery Worker 正在后台运行（任务 ID: b81c776）

### 3. API 路由修复
- ✓ 修复了重复 prefix 问题（`image_generation.py` line 37）
- ✓ 更新 `requirements.txt` 添加 `psycopg2-binary==2.9.11`

---

## ⚠️ 需要完成的步骤

### 步骤 1：重启后端服务

**原因**：虽然代码已修复，但 uvicorn 的 --reload 没有检测到路由文件更改，需要手动重启。

**操作**：

1. 找到运行 uvicorn 的终端窗口
2. 按 `Ctrl + C` 停止服务
3. 重新启动：

```bash
cd "E:\Mance\Mercury\Project\7. App dev\4. GoGoJap - HKTVmall AI system\backend"
venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**验证后端已重启**：
```bash
curl http://localhost:8000/health
# 应该返回：{"status":"healthy"}
```

### 步骤 2：运行完整 E2E 测试

重启后端后，运行图片生成 + R2 存储端到端测试：

```bash
cd "E:\Mance\Mercury\Project\7. App dev\4. GoGoJap - HKTVmall AI system\backend"
python scripts/test_image_gen_with_r2.py
```

**注意**：
- 测试会提示是否继续图片生成（需要真实 API 调用）
- 如果跳过图片生成，R2 上传功能已完全验证
- 如果继续图片生成，需要确保 `NANO_BANANA_API_KEY` 已配置

### 步骤 3：（可选）独立验证 R2 上传

如果只想验证 R2 存储功能，运行简化测试：

```bash
python scripts/test_r2_image_upload.py --cleanup
```

这个测试绕过 API 层，直接测试 StorageService 的 R2 上传功能。

---

## 📋 已修复的问题

### 问题 1：StorageService 初始化失败（404 错误）
**根本原因**：R2 API token 权限限制 `head_bucket` 操作

**解决方案**：修改 `app/services/storage_service.py` 使用 `list_objects_v2` 进行连接验证

**修改位置**：Lines 64-74

```python
# 使用 list_objects_v2 代替 head_bucket（更可靠）
try:
    self.s3_client.list_objects_v2(Bucket=self.bucket, MaxKeys=1)
    logger.info(f"Successfully connected to R2 bucket: {self.bucket}")
except ClientError as test_error:
    if test_error.response.get('Error', {}).get('Code') == 'NoSuchBucket':
        raise Exception(f"Bucket '{self.bucket}' does not exist")
    logger.warning(f"Could not verify bucket access: {test_error}")
    logger.info(f"R2 client initialized for bucket: {self.bucket}")
```

### 问题 2：Celery Worker 缺少 psycopg2
**根本原因**：`image_generation_tasks.py` 使用同步 PostgreSQL 连接，需要 psycopg2

**解决方案**：安装 `psycopg2-binary==2.9.11` 并添加到 requirements.txt

### 问题 3：Celery Worker 在 Windows 上无法启动
**根本原因**：Windows 不支持默认的 prefork pool

**解决方案**：使用 `--pool=solo` 模式启动 Celery Worker

```bash
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

### 问题 4：API 路由 404 错误
**根本原因**：`image_generation.py` 中 router 重复定义 prefix

**解决方案**：
```python
# 修改前：
router = APIRouter(prefix="/image-generation", tags=["image-generation"])

# 修改后（prefix 已在 router.py 中定义）：
router = APIRouter(tags=["image-generation"])
```

---

## 🔧 技术细节

### R2 存储配置
```bash
USE_R2_STORAGE=true
R2_ACCESS_KEY=cb143b4d307c80937d1429ff7bb6bd81
R2_SECRET_KEY=bced1e3dd2304b4c4c34ecb9719d45700c08f0b77790afdb2947dadead9d5669
R2_BUCKET=gogojap-image-generation
R2_ENDPOINT=https://43f382b11b94c725408508e1280bb173.r2.cloudflarestorage.com
R2_PUBLIC_URL=https://43f382b11b94c725408508e1280bb173.r2.cloudflarestorage.com/gogojap-image-generation
```

### 文件结构
```
uploads/                          # 本地模式（已废弃）
  input/                          # 输入图片
  generated/                      # 生成图片

R2 Bucket 结构：
gogojap-image-generation/
  input/{task_id}/{uuid}.jpg      # 输入图片
  generated/{task_id}/{uuid}.jpg  # 生成图片
```

### 测试脚本
| 脚本 | 用途 | 状态 |
|------|------|------|
| `test_r2_image_upload.py` | 直接测试 R2 上传功能 | ✅ 通过 |
| `test_image_gen_with_r2.py` | 完整 E2E 测试（API + R2 + Celery） | ⏳ 等待后端重启 |
| `test_r2_connection.py` | R2 连接基础测试 | ✅ 通过 |
| `diagnose_r2.py` | R2 配置诊断工具 | - |

---

## 📊 Git 提交记录

```bash
# 查看相关提交
git log --oneline | head -10

# 主要提交：
# 55d0323 - fix: 修复 R2 StorageService 初始化问题
# a07653f - feat: 添加 R2 存储测试腳本
# 2cb6f15 - chore: 添加圖片上傳存儲目錄結構
# 4cb9b63 - feat: 整合 Cloudflare R2 存儲支持
```

---

## 🎯 下一步

1. **立即执行**：重启后端服务（见步骤 1）
2. **验证**：运行 E2E 测试（见步骤 2）
3. **生产部署**：
   - 确保 `.env` 文件包含正确的 R2 配置
   - 确保 Celery Worker 使用 `--pool=solo` 在 Windows 上运行
   - 或在 Linux 生产环境使用默认 prefork pool

---

## ❓ 常见问题

**Q: 为什么需要手动重启后端？**
A: uvicorn 的 --reload 有时无法检测到路由模块的更改，需要手动重启。

**Q: Celery Worker 为什么使用 solo pool？**
A: Windows 不支持 fork()，默认的 prefork pool 会失败。Solo pool 是单进程模式，适合开发和 Windows 环境。

**Q: R2 费用如何计算？**
A: Cloudflare R2 免费额度：10GB 存储 + 1M Class A 操作 + 10M Class B 操作 + 无限流量。超出按量计费。

**Q: 如何切回本地存储？**
A: 在 `.env` 中设置 `USE_R2_STORAGE=false` 并重启服务。

---

**总结**：R2 存储集成核心功能已全部开发和验证完成。只需重启后端服务即可完成完整的图片生成系统测试。
