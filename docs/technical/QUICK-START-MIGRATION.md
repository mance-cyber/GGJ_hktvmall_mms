# GoGoJap AWS 迁移 - 快速启动指南

⚡ **10 分钟快速上手版本** ⚡

---

## 📋 准备清单

在开始前，请确保拥有：

- [ ] AWS 账号（已创建 Lightsail、RDS、S3）
- [ ] Neon 数据库连接字符串
- [ ] Cloudflare R2 访问凭证
- [ ] 本地安装 PostgreSQL 客户端工具
- [ ] 本地安装 Rclone

---

## 🚀 5 步快速迁移

### Step 1: 创建 AWS 资源 (15 分钟)

#### 1.1 创建 Lightsail 实例

```bash
# 访问 AWS Lightsail Console
# https://lightsail.aws.amazon.com/

# 配置:
# - Region: Singapore (ap-southeast-1)
# - Platform: Ubuntu 22.04 LTS
# - Plan: $44/月 (2 vCPU, 4GB RAM)
# - 创建静态 IP

# 记录:
LIGHTSAIL_IP=<your-static-ip>
```

#### 1.2 创建 RDS 数据库

```bash
# 访问 AWS RDS Console
# https://console.aws.amazon.com/rds/

# 配置:
# - Engine: PostgreSQL 14.x
# - Instance: db.t4g.micro
# - Storage: 20GB
# - Public access: Yes

# 记录:
RDS_ENDPOINT=<your-rds-endpoint>.rds.amazonaws.com
RDS_PASSWORD=<your-password>
```

#### 1.3 创建 S3 存储桶

```bash
# 创建 bucket
aws s3 mb s3://gogojap-media --region ap-southeast-1

# 记录:
S3_BUCKET=gogojap-media
```

---

### Step 2: 迁移数据库 (10 分钟)

使用自动化脚本：

```bash
# 在本地机器运行
cd scripts
chmod +x migrate-database.sh
./migrate-database.sh

# 按提示输入:
# - Neon URL: postgresql://user:pass@host/db
# - RDS URL: postgresql://postgres:pass@rds-endpoint/gogojap
```

**手动方式（备选）：**

```bash
# 导出 Neon
pg_dump "postgresql://user:pass@neon-host/db" \
  --format=custom \
  --no-owner \
  --no-acl \
  --file=backup.dump

# 导入 RDS
pg_restore "postgresql://postgres:pass@rds-endpoint/gogojap" \
  --verbose \
  --clean \
  --if-exists \
  backup.dump
```

---

### Step 3: 迁移存储 (20 分钟)

使用自动化脚本：

```bash
# 在本地机器运行
cd scripts
chmod +x migrate-storage.sh
./migrate-storage.sh

# 按提示输入:
# - R2 bucket: gogojap-bucket
# - S3 bucket: gogojap-media
```

**手动方式（备选）：**

```bash
# 配置 rclone
rclone config

# 同步数据
rclone sync r2:gogojap-bucket s3:gogojap-media \
  --progress \
  --transfers 10
```

---

### Step 4: 部署到 Lightsail (30 分钟)

#### 4.1 SSH 到 Lightsail

```bash
# 下载 SSH 密钥 (Lightsail Console)
ssh -i LightsailDefaultKey.pem ubuntu@YOUR_STATIC_IP
```

#### 4.2 运行初始化脚本

上传并运行脚本：

```bash
# 在本地机器上传脚本
scp -i LightsailDefaultKey.pem \
  scripts/setup-lightsail.sh \
  ubuntu@YOUR_STATIC_IP:~/

# 在 Lightsail 实例上运行
ssh -i LightsailDefaultKey.pem ubuntu@YOUR_STATIC_IP
chmod +x setup-lightsail.sh
./setup-lightsail.sh
```

#### 4.3 上传代码

```bash
# 方式 1: Git clone (推荐)
cd /var/www/gogojap
git clone <your-repo-url> .

# 方式 2: 从本地上传
# (在本地机器运行)
rsync -avz \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='.git' \
  -e "ssh -i LightsailDefaultKey.pem" \
  ./backend/ \
  ubuntu@YOUR_IP:/var/www/gogojap/backend/
```

#### 4.4 配置环境变量

```bash
# 在 Lightsail 实例上
cd /var/www/gogojap/backend
cp .env.template .env
nano .env

# 填写:
DATABASE_URL=postgresql://postgres:<pass>@<rds-endpoint>/gogojap
AWS_S3_BUCKET=gogojap-media
ANTHROPIC_API_KEY=<your-key>
# ... 其他配置
```

#### 4.5 安装依赖并启动

```bash
# 安装依赖
cd /var/www/gogojap
source venv/bin/activate
cd backend
pip install -r requirements.txt
pip install gunicorn

# 运行数据库迁移
alembic upgrade head

# 启动服务
sudo supervisorctl restart all
sudo supervisorctl status
```

---

### Step 5: 配置前端和 DNS (10 分钟)

#### 5.1 配置 SSL 证书

```bash
# 在 Lightsail 实例上
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.gogojap.com
```

#### 5.2 更新 DNS 记录

```
类型    名称              值                    TTL
────────────────────────────────────────────────
A       api.gogojap.com   <Lightsail_IP>      Auto
```

#### 5.3 更新前端环境变量

在 Cloudflare Pages 设置中：

```bash
NEXT_PUBLIC_API_URL=https://api.gogojap.com/api
NEXT_PUBLIC_CDN_URL=https://<cloudfront-domain>.cloudfront.net
```

触发前端重新部署。

---

## ✅ 验证清单

```bash
# 1. API 健康检查
curl https://api.gogojap.com/health

# 2. 数据库连接测试
curl https://api.gogojap.com/api/v1/products?limit=5

# 3. 文件上传测试
# 在前端界面测试图片上传功能

# 4. 查看日志（检查错误）
tail -f /var/log/gogojap/error.log
tail -f /var/log/nginx/error.log

# 5. 查看服务状态
sudo supervisorctl status

# 6. 系统资源监控
htop
```

---

## 🔧 常用命令

### 服务管理

```bash
# 重启所有服务
sudo supervisorctl restart all

# 重启单个服务
sudo supervisorctl restart gogojap
sudo supervisorctl restart gogojap-celery

# 查看服务状态
sudo supervisorctl status

# 查看日志
tail -f /var/log/gogojap/error.log
tail -f /var/log/gogojap/supervisor.log
tail -f /var/log/gogojap/celery.log
```

### 数据库操作

```bash
# 连接到 RDS
psql "postgresql://postgres:<pass>@<rds-endpoint>/gogojap"

# 查看表
\dt

# 查看表数据量
SELECT tablename, n_live_tup FROM pg_stat_user_tables;
```

### Nginx 管理

```bash
# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx

# 查看日志
sudo tail -f /var/log/nginx/error.log
```

---

## 🚨 故障排查

### 问题 1: API 无法访问

```bash
# 检查防火墙
sudo ufw status

# 检查 Nginx
sudo systemctl status nginx
sudo nginx -t

# 检查应用
sudo supervisorctl status gogojap
tail -f /var/log/gogojap/error.log
```

### 问题 2: 数据库连接失败

```bash
# 测试连接
psql "postgresql://postgres:<pass>@<rds-endpoint>/gogojap" -c "SELECT 1;"

# 检查 RDS 安全组
# 确保允许来自 Lightsail IP 的入站连接
# Port: 5432, Source: <Lightsail_IP>/32
```

### 问题 3: 文件上传失败

```bash
# 检查 S3 配置
aws s3 ls s3://gogojap-media

# 检查 IAM 权限
# 确保 AWS_ACCESS_KEY 有 s3:PutObject 权限

# 查看应用日志
tail -f /var/log/gogojap/error.log
```

---

## 📊 性能优化

### 1. Gunicorn Workers

```python
# gunicorn.conf.py
workers = 5  # 2 CPU * 2 + 1 = 5
```

### 2. 数据库连接池

```python
# app/config.py
SQLALCHEMY_POOL_SIZE = 10
SQLALCHEMY_MAX_OVERFLOW = 20
```

### 3. Redis 缓存

```bash
# 启用 Redis 持久化
sudo nano /etc/redis/redis.conf

# 添加:
save 900 1
save 300 10
save 60 10000
```

---

## 💰 成本监控

### AWS 预算告警

```bash
# 在 AWS Billing Console 设置
# Budget: $100/月
# Alert: 80%, 90%, 100%
```

### 每月成本预估

```
AWS Lightsail:    $44
AWS RDS:          $15-30
AWS S3+CF:        $5-10
────────────────────────
总计:             $64-84/月
```

---

## 🔄 回滚方案

如果出现问题，快速回滚：

```bash
# 1. 切换 DNS 回旧服务
# 2. 在 Cloudflare Pages 恢复旧环境变量
# 3. 重新部署前端

# 回滚 DNS (Cloudflare):
A   api.gogojap.com   <old-zeabur-ip>

# 回滚前端环境变量:
NEXT_PUBLIC_API_URL=<old-zeabur-url>
```

---

## 📚 完整文档

详细步骤请参考：
- **完整迁移指南**: `docs/technical/AWS-MIGRATION-GUIDE.md`
- **脚本说明**:
  - `scripts/migrate-database.sh` - 数据库迁移
  - `scripts/migrate-storage.sh` - 存储迁移
  - `scripts/setup-lightsail.sh` - Lightsail 初始化

---

## 🎯 下一步

完成迁移后：

1. **监控运行 1-2 周**
   - 查看错误日志
   - 监控性能指标
   - 收集用户反馈

2. **优化成本**
   - 考虑 RDS Reserved Instances (节省 40-60%)
   - 配置 S3 生命周期策略
   - 启用 CloudFront 缓存

3. **清理旧服务**
   - 取消 Zeabur 订阅
   - 保留 Neon 作为冷备份（可选）
   - 清空 Cloudflare R2

4. **文档更新**
   - 更新 CLAUDE.md 架构文档
   - 更新 INFRASTRUCTURE-COSTS.md
   - 创建迁移总结报告

---

**需要帮助？** 查看详细文档或联系技术支持。

**创建日期:** 2026-02-10
**最后更新:** 2026-02-10
