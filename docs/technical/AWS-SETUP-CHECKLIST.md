# AWS 资源创建检查清单

**创建日期:** 2026-02-10
**状态:** 🔄 进行中

---

## ✅ 创建进度

- [ ] Step 1: AWS Lightsail 实例
- [ ] Step 2: AWS RDS PostgreSQL 数据库
- [ ] Step 3: AWS S3 存储桶
- [ ] Step 4: CloudFront CDN 分发
- [ ] Step 5: 配置安全组和网络

---

## 📋 Step 1: 创建 AWS Lightsail 实例

### 访问 Console

🔗 **链接:** https://lightsail.aws.amazon.com/

### 配置参数

```yaml
基本设置:
  Instance location: Singapore (ap-southeast-1)
  Platform: Linux/Unix
  Blueprint: OS Only → Ubuntu 22.04 LTS

实例计划:
  Plan: $44/月
  vCPU: 2
  RAM: 4 GB
  Storage: 80 GB SSD
  Transfer: 4 TB

网络:
  IPv4 Firewall:
    - SSH (22) - ✅ 已开启
    - HTTP (80) - ✅ 需添加
    - HTTPS (443) - ✅ 需添加

命名:
  Instance name: gogojap-production
  Key pair: 使用默认或创建新的
```

### 详细步骤

1. **登录 AWS Console** → 搜索 "Lightsail" → 点击进入
2. 点击 **"Create instance"** 橙色按钮
3. **选择位置:**
   - Instance location: `Asia Pacific (Singapore)`
4. **选择平台:**
   - Select a platform: `Linux/Unix`
5. **选择蓝图:**
   - Select a blueprint: `OS Only`
   - Operating system: `Ubuntu 22.04 LTS`
6. **选择实例计划:**
   - 向下滚动找到 `$44 USD` 计划
   - 配置: `2 vCPU, 4 GB RAM, 80 GB SSD, 4 TB transfer`
7. **命名实例:**
   - Instance name: `gogojap-production`
8. 点击 **"Create instance"** 按钮

### 创建静态 IP

**等待实例启动（约 2-3 分钟）后：**

1. 点击实例名称 `gogojap-production`
2. 点击 **"Networking"** 标签
3. 点击 **"Create static IP"**
4. Static IP name: `gogojap-static-ip`
5. 点击 **"Create"**

### 配置防火墙

1. 在 Networking 页面
2. 点击 **"Add rule"**
3. 添加以下规则:

```
Application: HTTP
Protocol: TCP
Port: 80

Application: HTTPS
Protocol: TCP
Port: 443
```

### 下载 SSH 密钥

1. 在实例详情页面
2. 点击 **"Connect"** 标签
3. 点击 **"Download default key"**
4. 保存为: `LightsailDefaultKey-ap-southeast-1.pem`

### 测试连接

```bash
# 设置密钥权限 (Linux/Mac)
chmod 400 LightsailDefaultKey-ap-southeast-1.pem

# 连接到实例
ssh -i LightsailDefaultKey-ap-southeast-1.pem ubuntu@YOUR_STATIC_IP

# 如果成功，你会看到 Ubuntu 欢迎界面
```

### ✅ 完成检查

- [ ] 实例状态显示 "Running"
- [ ] 静态 IP 已创建并关联
- [ ] 防火墙规则已添加 (HTTP, HTTPS)
- [ ] SSH 连接测试成功

### 📝 记录信息

```bash
LIGHTSAIL_IP=___________________
SSH_KEY_PATH=LightsailDefaultKey-ap-southeast-1.pem
INSTANCE_NAME=gogojap-production
```

---

## 📋 Step 2: 创建 AWS RDS PostgreSQL 数据库

### 访问 Console

🔗 **链接:** https://console.aws.amazon.com/rds/

### 配置参数

```yaml
引擎选项:
  Engine type: PostgreSQL
  Version: PostgreSQL 14.x (最新稳定版)

模板:
  Template: Free tier (如果符合条件)
  或: Dev/Test

设置:
  DB instance identifier: gogojap-db
  Master username: postgres
  Master password: <生成强密码>

实例配置:
  DB instance class: Burstable classes (includes t classes)
  Class: db.t4g.micro (2 vCPU, 1 GB RAM)

存储:
  Storage type: General Purpose SSD (gp3)
  Allocated storage: 20 GB
  Enable storage autoscaling: ✅
  Maximum storage threshold: 50 GB

连接:
  VPC: Default VPC
  Subnet group: default
  Public access: Yes (稍后限制 IP)
  VPC security group: Create new
  Security group name: gogojap-rds-sg
  Availability Zone: No preference

数据库选项:
  Initial database name: gogojap
  Port: 5432

备份:
  Enable automated backups: ✅
  Backup retention period: 7 days
  Backup window: 03:00-04:00 UTC (低峰期)

加密:
  Enable encryption: ✅ (推荐)

维护:
  Enable auto minor version upgrade: ✅
  Maintenance window: 日 03:00-04:00 UTC
```

### 详细步骤

1. **登录 AWS Console** → 搜索 "RDS" → 点击进入
2. 点击 **"Create database"** 橙色按钮
3. **选择引擎:**
   - Engine type: `PostgreSQL`
   - Version: `PostgreSQL 14.x` (选择最新的 14 版本)
4. **选择模板:**
   - 如果可用: `Free tier`
   - 否则: `Dev/Test`
5. **设置凭证:**
   - DB instance identifier: `gogojap-db`
   - Master username: `postgres`
   - Master password: **生成强密码并安全保存**
   - Confirm password: 再次输入
6. **实例配置:**
   - DB instance class: `Burstable classes`
   - 选择: `db.t4g.micro` (2 vCPU, 1 GB RAM)
7. **存储:**
   - Storage type: `General Purpose SSD (gp3)`
   - Allocated storage: `20` GB
   - ✅ Enable storage autoscaling
   - Maximum storage threshold: `50` GB
8. **连接:**
   - VPC: 选择默认 VPC
   - Public access: `Yes`
   - VPC security group: `Create new`
   - New VPC security group name: `gogojap-rds-sg`
9. **数据库选项:**
   - Initial database name: `gogojap`
   - Port: `5432`
10. **备份:**
    - ✅ Enable automated backups
    - Backup retention period: `7` days
    - Backup window: 选择 `03:00-04:00 UTC`
11. **加密:**
    - ✅ Enable encryption (推荐)
12. 点击 **"Create database"** 按钮

### 等待创建完成

⏱️ **预计时间:** 10-15 分钟

在等待时，可以继续创建 S3 存储桶。

### 配置安全组（创建完成后）

**数据库创建完成后：**

1. 点击数据库名称 `gogojap-db`
2. 点击 **"VPC security groups"** 下的安全组链接
3. 点击 **"Edit inbound rules"**
4. 找到 PostgreSQL 规则（Port 5432）
5. 修改 Source 为: `Custom` → `<Lightsail Static IP>/32`
6. Description: `Allow from Lightsail`
7. 点击 **"Save rules"**

### 测试连接

```bash
# 获取 RDS endpoint (在 RDS Console 中)
# 格式: gogojap-db.xxxxxx.ap-southeast-1.rds.amazonaws.com

# 测试连接 (在本地或 Lightsail 实例)
psql -h gogojap-db.xxxxxx.ap-southeast-1.rds.amazonaws.com \
     -U postgres \
     -d gogojap \
     -c "SELECT version();"

# 输入密码后，应该看到 PostgreSQL 版本信息
```

### ✅ 完成检查

- [ ] 数据库状态显示 "Available"
- [ ] Endpoint 地址已记录
- [ ] 安全组已配置（仅允许 Lightsail IP）
- [ ] 连接测试成功

### 📝 记录信息

```bash
RDS_ENDPOINT=___________.ap-southeast-1.rds.amazonaws.com
RDS_PORT=5432
RDS_DATABASE=gogojap
RDS_USERNAME=postgres
RDS_PASSWORD=___________________  # 安全保存！

# 完整连接字符串
DATABASE_URL=postgresql://postgres:<password>@<endpoint>:5432/gogojap
```

---

## 📋 Step 3: 创建 AWS S3 存储桶

### 方式 1: 通过 AWS CLI (推荐)

#### 安装 AWS CLI

```bash
# Windows (MSYS2/Git Bash)
pip install awscli

# 或下载安装包
# https://aws.amazon.com/cli/

# 验证安装
aws --version
```

#### 配置 AWS CLI

```bash
aws configure

# 输入:
AWS Access Key ID: <你的 Access Key>
AWS Secret Access Key: <你的 Secret Key>
Default region name: ap-southeast-1
Default output format: json
```

**如何获取 Access Key:**
1. AWS Console → 右上角用户名 → Security credentials
2. Access keys → Create access key
3. Use case: CLI
4. 下载或复制 Key ID 和 Secret Key

#### 创建 S3 Bucket

```bash
# 创建 bucket
aws s3 mb s3://gogojap-media --region ap-southeast-1

# 配置 CORS
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

aws s3api put-bucket-cors \
  --bucket gogojap-media \
  --cors-configuration file://cors.json

# 配置公开访问（用于 CloudFront）
aws s3api put-public-access-block \
  --bucket gogojap-media \
  --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# 测试上传
echo "test" > test.txt
aws s3 cp test.txt s3://gogojap-media/test.txt
aws s3 ls s3://gogojap-media/

# 清理测试文件
aws s3 rm s3://gogojap-media/test.txt
rm test.txt cors.json
```

### 方式 2: 通过 AWS Console

🔗 **链接:** https://s3.console.aws.amazon.com/s3/

1. 点击 **"Create bucket"**
2. Bucket name: `gogojap-media`
3. AWS Region: `Asia Pacific (Singapore) ap-southeast-1`
4. Object Ownership: `ACLs disabled`
5. Block Public Access settings:
   - **取消勾选** "Block all public access"
   - ✅ 确认警告
6. Versioning: `Disable`
7. Default encryption: `Enable` (SSE-S3)
8. 点击 **"Create bucket"**

### ✅ 完成检查

- [ ] Bucket 创建成功
- [ ] CORS 配置已应用
- [ ] 可以成功上传文件

### 📝 记录信息

```bash
S3_BUCKET=gogojap-media
S3_REGION=ap-southeast-1
```

---

## 📋 Step 4: 创建 CloudFront 分发

### 访问 Console

🔗 **链接:** https://console.aws.amazon.com/cloudfront/

### 配置参数

```yaml
源设置:
  Origin domain: gogojap-media.s3.ap-southeast-1.amazonaws.com
  Origin path: (留空)
  Name: gogojap-media-s3
  Origin access: Public

默认缓存行为:
  Viewer protocol policy: Redirect HTTP to HTTPS
  Allowed HTTP methods: GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE
  Cache policy: CachingOptimized
  Origin request policy: CORS-S3Origin

设置:
  Price class: Use all edge locations
  或: Use only North America and Europe (节省成本)

自定义错误响应:
  (可选) 配置 404 错误页面
```

### 详细步骤

1. **登录 CloudFront Console**
2. 点击 **"Create distribution"**
3. **源设置:**
   - Origin domain: 选择 `gogojap-media.s3.ap-southeast-1.amazonaws.com`
   - Origin path: 留空
   - Origin access: `Public`
4. **默认缓存行为:**
   - Viewer protocol policy: `Redirect HTTP to HTTPS`
   - Allowed HTTP methods: `GET, HEAD, OPTIONS, PUT, POST, PATCH, DELETE`
   - Cache policy: `CachingOptimized`
   - Origin request policy: `CORS-S3Origin`
5. **设置:**
   - Price class:
     - 全球: `Use all edge locations`
     - 节省成本: `Use only North America, Europe and Asia`
   - Alternate domain names (CNAME): (稍后配置)
6. 点击 **"Create distribution"**

### 等待部署完成

⏱️ **预计时间:** 15-20 分钟

### 测试 CloudFront

```bash
# 获取 CloudFront 域名 (Distribution domain name)
# 格式: dxxxxxx.cloudfront.net

# 上传测试文件
aws s3 cp test.jpg s3://gogojap-media/test.jpg

# 通过 CloudFront 访问
curl -I https://dxxxxxx.cloudfront.net/test.jpg

# 应该看到 200 OK 响应
```

### ✅ 完成检查

- [ ] Distribution 状态显示 "Enabled"
- [ ] 可以通过 CloudFront URL 访问文件
- [ ] HTTPS 正常工作

### 📝 记录信息

```bash
CLOUDFRONT_DOMAIN=dxxxxxx.cloudfront.net
CLOUDFRONT_DISTRIBUTION_ID=EXXXXXXXXX
```

---

## 📋 Step 5: 安全和网络配置总结

### Lightsail 安全组

```yaml
Inbound Rules:
  - SSH (22): 仅允许你的 IP
  - HTTP (80): 0.0.0.0/0 (所有)
  - HTTPS (443): 0.0.0.0/0 (所有)
```

### RDS 安全组

```yaml
Inbound Rules:
  - PostgreSQL (5432): <Lightsail Static IP>/32
```

### S3 Bucket Policy (可选 - 如果需要公开访问)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::gogojap-media/*"
    }
  ]
}
```

---

## 📊 所有资源创建完成检查清单

### ✅ 最终验证

- [ ] **Lightsail:**
  - [ ] 实例运行中
  - [ ] 静态 IP 已关联
  - [ ] SSH 连接正常
  - [ ] 防火墙规则正确

- [ ] **RDS:**
  - [ ] 数据库可用
  - [ ] Endpoint 可访问
  - [ ] 安全组配置正确
  - [ ] 连接测试通过

- [ ] **S3:**
  - [ ] Bucket 创建成功
  - [ ] CORS 配置完成
  - [ ] 可以上传文件

- [ ] **CloudFront:**
  - [ ] Distribution 已部署
  - [ ] HTTPS 正常工作
  - [ ] 可以访问文件

### 📝 环境变量汇总

创建文件: `aws-credentials.env`

```bash
# ==================== Lightsail ====================
LIGHTSAIL_IP=
LIGHTSAIL_SSH_KEY=LightsailDefaultKey-ap-southeast-1.pem

# ==================== RDS ====================
RDS_ENDPOINT=
RDS_PORT=5432
RDS_DATABASE=gogojap
RDS_USERNAME=postgres
RDS_PASSWORD=

# 完整连接字符串
DATABASE_URL=postgresql://postgres:<password>@<endpoint>:5432/gogojap

# ==================== S3 ====================
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=gogojap-media
AWS_S3_REGION=ap-southeast-1

# ==================== CloudFront ====================
AWS_CLOUDFRONT_DOMAIN=
AWS_CLOUDFRONT_DISTRIBUTION_ID=

# ==================== 其他 ====================
ANTHROPIC_API_KEY=
FIRECRAWL_API_KEY=
```

⚠️ **重要:** 妥善保存此文件，不要提交到 Git！

---

## 💰 成本确认

### 预估月费

```
AWS Lightsail:     $44.00
AWS RDS:           $15.00 - $30.00
AWS S3:            $1.00 - $5.00
AWS CloudFront:    $1.00 - $5.00
──────────────────────────────
总计:              $61.00 - $84.00 / 月
```

### 成本控制

1. **设置预算告警:**
   - AWS Console → Billing → Budgets
   - 创建预算: $100/月
   - 告警阈值: 80%, 90%, 100%

2. **启用成本探索器:**
   - 监控每日成本
   - 识别成本高的服务

---

## 🎯 下一步

完成所有资源创建后：

1. ✅ 保存所有凭证和 endpoint
2. 🔄 继续 **Step 2: 迁移数据库**
3. 🔄 运行 `scripts/migrate-database.sh`

---

**创建日期:** 2026-02-10
**最后更新:** 2026-02-10
**状态:** 🔄 进行中
