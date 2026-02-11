# GoGoJap AWS 全面迁移指南

**文档版本：** v1.0
**创建日期：** 2026-02-10
**迁移类型：** 短暂停机迁移
**预计停机时间：** 30-60 分钟

---

## 📋 迁移概览

### 迁移范围

| 组件 | 源 | 目标 | 状态 |
|-----|-----|------|------|
| **前端** | Cloudflare Pages | Cloudflare Pages | ✅ 保持不变 |
| **后端** | Zeabur | AWS Lightsail | 🔄 需迁移 |
| **数据库** | Neon PostgreSQL | AWS RDS PostgreSQL | 🔄 需迁移 |
| **存储** | Cloudflare R2 | AWS S3 + CloudFront | 🔄 需迁移 |
| **Redis** | Zeabur Redis | Lightsail Redis | 🔄 需迁移 |

### 成本变化

```
迁移前（月费）:
├─ Zeabur: ~$20
├─ Neon: $0 (免费层)
├─ Cloudflare R2: ~$5
└─ 总计: ~$25/月

迁移后（月费）:
├─ AWS Lightsail: $44
├─ AWS RDS: $15-30 (db.t4g.micro)
├─ AWS S3 + CloudFront: ~$5
└─ 总计: ~$64-79/月
```

**成本增加原因：** 更高的性能、可靠性和 AWS 生态整合

---

## 🚀 Phase 1: AWS 基础设施准备

### 1.1 创建 AWS Lightsail 实例

#### 通过 AWS Console:

1. 登录 [AWS Lightsail Console](https://lightsail.aws.amazon.com/)
2. 点击 "Create instance"
3. 选择配置：
   - **Region**: Asia Pacific (Singapore) 或 Asia Pacific (Tokyo)
   - **Platform**: Linux/Unix
   - **Blueprint**: OS Only → Ubuntu 22.04 LTS
   - **Instance plan**: $44/month (2 vCPU, 4GB RAM, 80GB SSD)
   - **Instance name**: `gogojap-production`
4. 创建静态 IP：
   - 进入实例详情 → Networking → Create static IP
   - 名称: `gogojap-static-ip`

#### 获取 SSH 访问:

```bash
# 下载默认 SSH 密钥
# 在 Lightsail Console → Account → SSH keys → Download

# 连接到实例
ssh -i LightsailDefaultKey-ap-southeast-1.pem ubuntu@YOUR_STATIC_IP
```

### 1.2 创建 AWS RDS PostgreSQL

#### 通过 AWS Console:

1. 登录 [AWS RDS Console](https://console.aws.amazon.com/rds/)
2. 点击 "Create database"
3. 配置：
   - **Engine**: PostgreSQL 14.x
   - **Template**: Free tier (或 Dev/Test for better performance)
   - **DB instance identifier**: `gogojap-db`
   - **Master username**: `postgres`
   - **Master password**: `生成强密码并保存`
   - **DB instance class**: db.t4g.micro (2 vCPU, 1GB RAM, $15/月)
   - **Storage**: 20 GB SSD (gp3)
   - **VPC**: Default VPC
   - **Public access**: Yes (稍后可限制为 Lightsail IP)
   - **Initial database name**: `gogojap`
4. 等待实例创建完成（约 10-15 分钟）
5. 记录 endpoint: `gogojap-db.xxxx.ap-southeast-1.rds.amazonaws.com`

#### 配置安全组:

```bash
# 在 RDS Security Group 中添加入站规则
Type: PostgreSQL
Protocol: TCP
Port: 5432
Source: <Lightsail Static IP>/32
Description: Allow Lightsail instance
```

### 1.3 创建 AWS S3 存储桶

#### 通过 AWS CLI:

```bash
# 安装 AWS CLI (本地机器)
pip install awscli

# 配置 AWS credentials
aws configure
# AWS Access Key ID: 输入你的 key
# AWS Secret Access Key: 输入你的 secret
# Default region: ap-southeast-1
# Default output: json

# 创建 S3 bucket
aws s3 mb s3://gogojap-media --region ap-southeast-1

# 配置公开访问（用于 CDN）
aws s3api put-public-access-block \
  --bucket gogojap-media \
  --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# 设置 CORS 配置
cat > cors.json << 'EOF'
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }
  ]
}
EOF

aws s3api put-bucket-cors --bucket gogojap-media --cors-configuration file://cors.json
```

### 1.4 创建 CloudFront 分发

#### 通过 AWS Console:

1. 登录 [CloudFront Console](https://console.aws.amazon.com/cloudfront/)
2. 点击 "Create distribution"
3. 配置：
   - **Origin domain**: `gogojap-media.s3.ap-southeast-1.amazonaws.com`
   - **Origin access**: Public
   - **Viewer protocol policy**: Redirect HTTP to HTTPS
   - **Cache policy**: CachingOptimized
   - **Price class**: Use all edge locations (或选择 Asia/Europe only 节省成本)
4. 创建并等待部署（约 15-20 分钟）
5. 记录 CloudFront 域名: `d1234abcd.cloudfront.net`

---

## 📊 Phase 2: 数据库迁移 (Neon → RDS)

### 2.1 准备工作

#### 获取 Neon 连接信息:

```bash
# 从当前 backend/.env 文件中获取
# DATABASE_URL=postgresql://user:password@host/database
```

#### 在本地安装 PostgreSQL 工具:

```bash
# Ubuntu/Debian
sudo apt install postgresql-client

# macOS
brew install postgresql

# Windows (MSYS2/Git Bash)
pacman -S mingw-w64-x86_64-postgresql
```

### 2.2 导出 Neon 数据库

```bash
# ==================== 导出数据 ====================

# 设置环境变量
export NEON_URL="postgresql://user:password@host/database"
export RDS_URL="postgresql://postgres:password@gogojap-db.xxxx.rds.amazonaws.com:5432/gogojap"

# 导出 schema + data
pg_dump "$NEON_URL" \
  --format=custom \
  --no-owner \
  --no-acl \
  --verbose \
  --file=gogojap_backup_$(date +%Y%m%d_%H%M%S).dump

# 导出纯 SQL 格式（备用）
pg_dump "$NEON_URL" \
  --format=plain \
  --no-owner \
  --no-acl \
  --verbose \
  --file=gogojap_backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2.3 恢复到 RDS

```bash
# ==================== 恢复数据 ====================

# 使用 custom format (推荐)
pg_restore "$RDS_URL" \
  --verbose \
  --clean \
  --if-exists \
  --no-owner \
  --no-acl \
  gogojap_backup_YYYYMMDD_HHMMSS.dump

# 或使用 SQL format
psql "$RDS_URL" < gogojap_backup_YYYYMMDD_HHMMSS.sql
```

### 2.4 验证数据完整性

```bash
# ==================== 验证数据 ====================

# 连接到 RDS
psql "$RDS_URL"

# 检查表数量
\dt

# 检查每个表的行数
SELECT
  schemaname,
  tablename,
  n_live_tup as row_count
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;

# 检查索引
\di

# 检查序列
\ds

# 退出
\q
```

---

## 📦 Phase 3: 存储迁移 (R2 → S3)

### 3.1 安装 Rclone

```bash
# Ubuntu/Debian
sudo apt install rclone

# macOS
brew install rclone

# Windows
# 下载: https://rclone.org/downloads/
```

### 3.2 配置 Rclone

```bash
# ==================== 配置 Rclone ====================

rclone config

# 配置 Cloudflare R2
# Name: r2
# Storage: s3
# Provider: Cloudflare
# Access Key ID: <R2 Access Key>
# Secret Access Key: <R2 Secret Key>
# Endpoint: https://<account-id>.r2.cloudflarestorage.com

# 配置 AWS S3
# Name: s3
# Storage: s3
# Provider: AWS
# Access Key ID: <AWS Access Key>
# Secret Access Key: <AWS Secret Key>
# Region: ap-southeast-1
```

### 3.3 同步数据

```bash
# ==================== 同步 R2 → S3 ====================

# 测试运行（不实际复制）
rclone sync r2:gogojap-bucket s3:gogojap-media \
  --dry-run \
  --progress \
  --verbose

# 实际同步
rclone sync r2:gogojap-bucket s3:gogojap-media \
  --progress \
  --transfers=10 \
  --checkers=20 \
  --verbose \
  --stats=10s

# 验证文件数量和大小
rclone size r2:gogojap-bucket
rclone size s3:gogojap-media
```

---

## 🖥️ Phase 4: 部署后端到 Lightsail

### 4.1 系统初始化

SSH 到 Lightsail 实例:

```bash
ssh -i LightsailDefaultKey.pem ubuntu@YOUR_STATIC_IP
```

安装系统依赖:

```bash
# ==================== 更新系统 ====================
sudo apt update && sudo apt upgrade -y

# ==================== 安装 Python 3.11 ====================
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# 设置 python3.11 为默认
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# ==================== 安装其他依赖 ====================
sudo apt install -y \
  git \
  nginx \
  redis-server \
  postgresql-client \
  supervisor \
  build-essential \
  libpq-dev

# ==================== 配置防火墙 ====================
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 4.2 部署应用代码

```bash
# ==================== 创建应用目录 ====================
sudo mkdir -p /var/www/gogojap
sudo chown ubuntu:ubuntu /var/www/gogojap
cd /var/www/gogojap

# ==================== 克隆代码 ====================
# 方式 1: 从 Git 仓库
git clone <your-repo-url> .

# 方式 2: 从本地上传（在本地机器运行）
# rsync -avz --exclude='node_modules' --exclude='__pycache__' \
#   -e "ssh -i LightsailDefaultKey.pem" \
#   ./backend/ ubuntu@YOUR_STATIC_IP:/var/www/gogojap/

# ==================== 创建虚拟环境 ====================
python3 -m venv venv
source venv/bin/activate

# ==================== 安装依赖 ====================
cd backend
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 4.3 配置环境变量

```bash
# ==================== 创建生产环境配置 ====================
cat > /var/www/gogojap/backend/.env << 'EOF'
# ==================== 应用配置 ====================
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<生成一个强随机密钥>

# ==================== 数据库配置 ====================
DATABASE_URL=postgresql://postgres:<password>@gogojap-db.xxxx.rds.amazonaws.com:5432/gogojap

# ==================== Redis 配置 ====================
REDIS_URL=redis://localhost:6379/0

# ==================== AWS S3 配置 ====================
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_S3_BUCKET=gogojap-media
AWS_S3_REGION=ap-southeast-1
AWS_CLOUDFRONT_DOMAIN=d1234abcd.cloudfront.net

# ==================== AI 配置 ====================
ANTHROPIC_API_KEY=<your-claude-key>

# ==================== Firecrawl 配置 ====================
FIRECRAWL_API_KEY=<your-firecrawl-key>

# ==================== CORS 配置 ====================
ALLOWED_ORIGINS=https://your-frontend-domain.pages.dev,https://gogojap.com
EOF

# 设置权限
chmod 600 /var/www/gogojap/backend/.env
```

### 4.4 配置 Gunicorn

```bash
# ==================== 创建 Gunicorn 配置 ====================
cat > /var/www/gogojap/backend/gunicorn.conf.py << 'EOF'
import multiprocessing

# ==================== 服务器配置 ====================
bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1  # 2 CPU * 2 + 1 = 5 workers
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 10000
max_requests_jitter = 1000
timeout = 120
keepalive = 5

# ==================== 日志配置 ====================
accesslog = "/var/log/gogojap/access.log"
errorlog = "/var/log/gogojap/error.log"
loglevel = "info"

# ==================== 进程命名 ====================
proc_name = "gogojap"
EOF

# 创建日志目录
sudo mkdir -p /var/log/gogojap
sudo chown ubuntu:ubuntu /var/log/gogojap
```

### 4.5 配置 Nginx

```bash
# ==================== 创建 Nginx 配置 ====================
sudo tee /etc/nginx/sites-available/gogojap << 'EOF'
upstream gogojap_backend {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name YOUR_STATIC_IP;  # 稍后替换为域名

    client_max_body_size 100M;

    # ==================== API 路由 ====================
    location /api {
        proxy_pass http://gogojap_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # ==================== 健康检查 ====================
    location /health {
        proxy_pass http://gogojap_backend;
        access_log off;
    }

    # ==================== 静态文件 ====================
    location /static {
        alias /var/www/gogojap/backend/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# 启用站点
sudo ln -sf /etc/nginx/sites-available/gogojap /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 4.6 配置 Supervisor (自动启动)

```bash
# ==================== Gunicorn 服务 ====================
sudo tee /etc/supervisor/conf.d/gogojap.conf << 'EOF'
[program:gogojap]
directory=/var/www/gogojap/backend
command=/var/www/gogojap/venv/bin/gunicorn app.main:app -c gunicorn.conf.py
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gogojap/supervisor.log
environment=PATH="/var/www/gogojap/venv/bin"
EOF

# ==================== Celery Worker 服务 ====================
sudo tee /etc/supervisor/conf.d/gogojap-celery.conf << 'EOF'
[program:gogojap-celery]
directory=/var/www/gogojap/backend
command=/var/www/gogojap/venv/bin/celery -A app.celery_app worker --loglevel=info
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gogojap/celery.log
environment=PATH="/var/www/gogojap/venv/bin"
EOF

# ==================== Celery Beat 服务 (定时任务) ====================
sudo tee /etc/supervisor/conf.d/gogojap-celery-beat.conf << 'EOF'
[program:gogojap-celery-beat]
directory=/var/www/gogojap/backend
command=/var/www/gogojap/venv/bin/celery -A app.celery_app beat --loglevel=info
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gogojap/celery-beat.log
environment=PATH="/var/www/gogojap/venv/bin"
EOF

# 重新加载 Supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl status
```

### 4.7 运行数据库迁移

```bash
# ==================== 激活虚拟环境 ====================
cd /var/www/gogojap/backend
source ../venv/bin/activate

# ==================== 运行 Alembic 迁移 ====================
alembic upgrade head

# ==================== 验证应用启动 ====================
sudo supervisorctl restart gogojap
sudo supervisorctl status

# 检查日志
tail -f /var/log/gogojap/supervisor.log
```

---

## 🌐 Phase 5: 前端配置更新

### 5.1 更新前端环境变量

在 Cloudflare Pages 设置中更新：

```bash
# ==================== 生产环境变量 ====================
NEXT_PUBLIC_API_URL=http://YOUR_LIGHTSAIL_STATIC_IP/api
NEXT_PUBLIC_CDN_URL=https://d1234abcd.cloudfront.net
```

### 5.2 配置 SSL 证书

#### 使用 Certbot (Let's Encrypt):

```bash
# 在 Lightsail 实例上运行

# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书（替换为你的域名）
sudo certbot --nginx -d api.gogojap.com

# 验证自动续期
sudo certbot renew --dry-run
```

### 5.3 更新 DNS 记录

在你的 DNS 提供商（如 Cloudflare）中：

```
类型    名称              值                          TTL
──────────────────────────────────────────────────────────
A       api.gogojap.com   <Lightsail Static IP>     Auto
```

### 5.4 更新 Nginx 配置（启用域名）

```bash
# 编辑 Nginx 配置
sudo nano /etc/nginx/sites-available/gogojap

# 更新 server_name
server_name api.gogojap.com;

# 重启 Nginx
sudo systemctl restart nginx
```

---

## ✅ Phase 6: 验证和切换

### 6.1 功能测试清单

```bash
# ==================== API 健康检查 ====================
curl https://api.gogojap.com/health

# ==================== 测试数据库连接 ====================
curl https://api.gogojap.com/api/v1/products?limit=10

# ==================== 测试文件上传 ====================
curl -X POST https://api.gogojap.com/api/v1/upload \
  -F "file=@test-image.jpg" \
  -H "Authorization: Bearer <token>"

# ==================== 测试 AI 功能 ====================
curl -X POST https://api.gogojap.com/api/v1/content/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"product_id": 1}'
```

### 6.2 性能测试

```bash
# ==================== API 响应时间 ====================
for i in {1..10}; do
  curl -w "Response time: %{time_total}s\n" -o /dev/null -s https://api.gogojap.com/health
done

# ==================== 数据库查询性能 ====================
psql "$RDS_URL" -c "EXPLAIN ANALYZE SELECT * FROM products LIMIT 100;"
```

### 6.3 监控设置

```bash
# ==================== 安装监控工具 ====================
sudo apt install -y htop iotop nethogs

# ==================== 查看系统资源 ====================
htop

# ==================== 查看日志 ====================
sudo tail -f /var/log/gogojap/error.log
sudo tail -f /var/log/nginx/error.log

# ==================== 监控数据库连接 ====================
psql "$RDS_URL" -c "SELECT * FROM pg_stat_activity;"
```

---

## 🔄 Phase 7: 切换和清理

### 7.1 维护模式

在前端显示维护通知：

```typescript
// frontend/src/components/MaintenanceMode.tsx
export function MaintenanceMode() {
  return (
    <div className="maintenance-notice">
      <h1>系统维护中</h1>
      <p>预计 30 分钟后恢复，感谢您的耐心等待。</p>
    </div>
  );
}
```

### 7.2 最终切换

```bash
# 1. 停止旧的 Zeabur 应用（防止数据冲突）
# 2. 更新前端环境变量指向新的 Lightsail API
# 3. 触发前端重新部署
# 4. 验证所有功能正常
# 5. 移除维护通知
```

### 7.3 旧服务清理

⚠️ **等待 1-2 周确认稳定后再执行**

```bash
# ==================== 保留作为备份 ====================
# 1. Neon 数据库：保留只读备份（免费）
# 2. Zeabur 应用：暂停但不删除
# 3. Cloudflare R2：保留 1 个月作为备份

# ==================== 最终清理（确认稳定后）====================
# 1. 取消 Zeabur 订阅
# 2. 删除 Neon 数据库（或保留作为历史备份）
# 3. 清空 Cloudflare R2（或保留冷备份）
```

---

## 📊 Phase 8: 成本优化

### 8.1 AWS 成本告警

```bash
# 在 AWS Billing Console 设置预算告警
# Budget amount: $100/month
# Alert threshold: 80%, 90%, 100%
# Email: your-email@example.com
```

### 8.2 RDS 优化建议

```bash
# ==================== 考虑使用 Reserved Instances ====================
# 1年期预付：节省约 40%
# 3年期预付：节省约 60%

# ==================== 启用自动备份 ====================
# 保留期：7 天
# 备份窗口：凌晨 3:00-4:00（低峰期）
```

### 8.3 S3 生命周期策略

```bash
# ==================== 旧文件自动归档 ====================
aws s3api put-bucket-lifecycle-configuration \
  --bucket gogojap-media \
  --lifecycle-configuration file://lifecycle.json

# lifecycle.json:
{
  "Rules": [{
    "Id": "ArchiveOldFiles",
    "Status": "Enabled",
    "Transitions": [{
      "Days": 90,
      "StorageClass": "STANDARD_IA"  # 不常访问层（便宜 50%）
    }, {
      "Days": 180,
      "StorageClass": "GLACIER"  # 归档层（便宜 80%）
    }]
  }]
}
```

---

## 🚨 应急回滚方案

如果迁移后出现严重问题：

### 回滚步骤

```bash
# 1. 立即切换 DNS 回旧的 Zeabur 服务
# 2. 重启 Zeabur 应用
# 3. 前端环境变量回滚到旧的 API URL
# 4. 触发前端重新部署

# ==================== DNS 回滚 ====================
# 将 api.gogojap.com 的 A 记录改回 Zeabur IP

# ==================== 前端环境变量回滚 ====================
# NEXT_PUBLIC_API_URL=<old-zeabur-url>
# NEXT_PUBLIC_CDN_URL=https://r2-cdn-url

# 5. 调查问题，修复后再次尝试迁移
```

### 常见问题排查

| 问题 | 可能原因 | 解决方案 |
|-----|---------|---------|
| API 无法访问 | 防火墙 / 安全组配置 | 检查 Lightsail 和 RDS 安全组 |
| 数据库连接失败 | 连接字符串错误 | 验证 DATABASE_URL 和 RDS endpoint |
| 文件上传失败 | S3 权限配置 | 检查 IAM policy 和 bucket policy |
| 500 错误 | 应用配置错误 | 查看 `/var/log/gogojap/error.log` |
| 性能下降 | Worker 不足 | 增加 Gunicorn workers 数量 |

---

## 📈 迁移后监控指标

### 关键指标

```bash
# ==================== 每日检查 ====================
1. API 响应时间 (目标: < 200ms)
2. 数据库查询性能 (目标: < 50ms)
3. 错误率 (目标: < 0.1%)
4. 系统资源使用率 (CPU < 70%, RAM < 80%)

# ==================== 每周检查 ====================
1. AWS 成本趋势
2. 存储空间增长
3. 备份完整性
4. 安全更新
```

### 监控脚本

```bash
# ==================== 创建监控脚本 ====================
cat > /home/ubuntu/monitor.sh << 'EOF'
#!/bin/bash
# GoGoJap 系统监控脚本

echo "==================== 系统资源 ===================="
echo "CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')%"
echo "内存: $(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2}')"
echo "磁盘: $(df -h / | awk 'NR==2{print $5}')"

echo "\n==================== 应用状态 ===================="
sudo supervisorctl status

echo "\n==================== 最新错误 ===================="
tail -n 5 /var/log/gogojap/error.log

echo "\n==================== 数据库连接 ===================="
psql "$DATABASE_URL" -c "SELECT count(*) FROM pg_stat_activity;" -t

echo "\n==================== Nginx 访问统计 ===================="
tail -n 100 /var/log/nginx/access.log | awk '{print $9}' | sort | uniq -c | sort -rn
EOF

chmod +x /home/ubuntu/monitor.sh

# 每小时运行一次
(crontab -l 2>/dev/null; echo "0 * * * * /home/ubuntu/monitor.sh >> /var/log/gogojap/monitor.log 2>&1") | crontab -
```

---

## 🎯 总结

### 迁移检查清单

- [ ] AWS Lightsail 实例已创建并配置
- [ ] AWS RDS PostgreSQL 已创建并导入数据
- [ ] AWS S3 + CloudFront 已配置并同步文件
- [ ] 后端应用已部署到 Lightsail
- [ ] Nginx + SSL 证书已配置
- [ ] Celery + Redis 已正常运行
- [ ] 前端环境变量已更新
- [ ] DNS 记录已切换
- [ ] 所有功能测试通过
- [ ] 监控和告警已设置
- [ ] 成本控制措施已实施
- [ ] 应急回滚方案已准备

### 预期收益

✅ **性能提升**: Lightsail + RDS 提供更稳定的性能
✅ **AWS 生态整合**: 未来可轻松扩展到 Lambda, SQS 等服务
✅ **可靠性提升**: 企业级 SLA 保证
✅ **可扩展性**: 支持无缝升级到更高配置

### 下一步

完成迁移后：
1. 更新 `CLAUDE.md` 架构文档
2. 更新 `INFRASTRUCTURE-COSTS.md` 成本文档
3. 监控系统运行 1-2 周
4. 确认稳定后清理旧服务
5. 考虑进一步的成本优化（Reserved Instances）

---

**迁移负责人：** Mance
**创建日期：** 2026-02-10
**预计完成：** 2026-02-11
