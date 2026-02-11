# AWS EC2 替代方案（如果 Lightsail 不可用）

**创建日期:** 2026-02-10
**适用场景:** Lightsail 访问受限时的替代方案

---

## 📋 EC2 vs Lightsail 对比

| 特性 | Lightsail | EC2 |
|-----|----------|-----|
| **价格** | $44/月 固定 | $30-50/月 按需 |
| **配置** | 2 vCPU, 4GB RAM | t3.medium (2 vCPU, 4GB RAM) |
| **易用性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **灵活性** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **网络** | 4TB 固定 | 按用量计费 |
| **适合** | 简单应用 | 需要高级配置 |

**结论:** EC2 配置稍复杂，但功能更强大且成本相近。

---

## 🚀 创建 EC2 实例（替代 Lightsail）

### Step 1: 启动实例

访问 EC2 Console:
```
🔗 https://console.aws.amazon.com/ec2/
```

### Step 2: 配置实例

#### 1. 点击 "Launch Instance"

#### 2. 基本配置

```yaml
Name: gogojap-production

Application and OS Images:
  - Quick Start: Ubuntu
  - Ubuntu Server 22.04 LTS (HVM), SSD Volume Type
  - Architecture: 64-bit (x86)

Instance type:
  - Family: t3
  - Type: t3.medium
  - vCPU: 2
  - Memory: 4 GiB
  - Network Performance: Up to 5 Gigabit
```

**成本估算:** ~$30-40/月（比 Lightsail 便宜）

#### 3. 密钥对（Key pair）

```yaml
选项 1: 创建新密钥对
  - Key pair name: gogojap-ec2-key
  - Key pair type: RSA
  - Private key format: .pem
  - 点击 "Create key pair"
  - 自动下载: gogojap-ec2-key.pem

选项 2: 使用现有密钥对
  - 如果已有密钥对，选择即可
```

#### 4. 网络设置

```yaml
Network settings:
  VPC: (默认 VPC)
  Subnet: No preference
  Auto-assign public IP: Enable

Firewall (security groups):
  选择: Create security group

  Security group name: gogojap-sg
  Description: Security group for GoGoJap production

  Inbound rules:
    - Type: SSH, Port: 22, Source: My IP (你的 IP)
    - Type: HTTP, Port: 80, Source: Anywhere (0.0.0.0/0)
    - Type: HTTPS, Port: 443, Source: Anywhere (0.0.0.0/0)
```

#### 5. 存储配置

```yaml
Configure storage:
  - Root volume:
    - Size: 30 GiB (足够使用)
    - Volume type: gp3 (General Purpose SSD)
    - Delete on termination: Yes
    - Encrypted: Yes (推荐)
```

#### 6. 高级设置（可选）

```yaml
Advanced details:
  - Termination protection: Enable (防止误删)
  - Monitoring: Enable detailed monitoring (可选，额外费用)
```

#### 7. 启动实例

点击右侧 **"Launch instance"** 按钮

⏱️ **预计时间:** 2-3 分钟

---

## 🔒 配置 Elastic IP（静态 IP）

### 创建 Elastic IP

1. 在 EC2 Console 左侧菜单
2. 点击 **"Elastic IPs"** (在 Network & Security 下)
3. 点击 **"Allocate Elastic IP address"**
4. Network border group: `ap-southeast-1`
5. 点击 **"Allocate"**

### 关联到实例

1. 选择刚创建的 Elastic IP
2. 点击 **"Actions"** → **"Associate Elastic IP address"**
3. Instance: 选择 `gogojap-production`
4. 点击 **"Associate"**

### 📝 记录 Elastic IP

```bash
EC2_ELASTIC_IP=_________________
```

---

## 🔐 配置安全组

### 更新安全组规则

如果需要添加规则：

1. EC2 Console → Security Groups
2. 选择 `gogojap-sg`
3. 点击 **"Inbound rules"** → **"Edit inbound rules"**
4. 确保有以下规则：

```yaml
规则 1:
  Type: SSH
  Protocol: TCP
  Port: 22
  Source: My IP (你的当前 IP)

规则 2:
  Type: HTTP
  Protocol: TCP
  Port: 80
  Source: 0.0.0.0/0

规则 3:
  Type: HTTPS
  Protocol: TCP
  Port: 443
  Source: 0.0.0.0/0
```

---

## 🔌 连接到 EC2 实例

### 设置 SSH 密钥权限

```bash
# Linux/Mac
chmod 400 gogojap-ec2-key.pem

# Windows (Git Bash/MSYS2)
chmod 400 gogojap-ec2-key.pem
```

### SSH 连接

```bash
# 使用 Elastic IP 连接
ssh -i gogojap-ec2-key.pem ubuntu@YOUR_ELASTIC_IP

# 首次连接会提示，输入 yes
# Are you sure you want to continue connecting? yes

# 成功连接后会看到 Ubuntu 欢迎界面
```

---

## 📊 成本对比

### Lightsail vs EC2

```
Lightsail (2 vCPU, 4GB):
  固定月费: $44

EC2 t3.medium (2 vCPU, 4GB):
  实例: $0.0416/小时 × 730小时 = $30.37
  存储: 30GB gp3 × $0.08/GB = $2.40
  Elastic IP: $0 (关联时免费)
  数据传输: 前 100GB 免费，后续 $0.09/GB
  ─────────────────────────────────────
  预估月费: $32.77 - $40 (取决于流量)
```

**结论:** EC2 通常更便宜！

### 成本优化

1. **使用 Reserved Instances**
   - 1年期: 节省 40%
   - 3年期: 节省 60%

2. **使用 Savings Plans**
   - 灵活的折扣计划
   - 可节省 20-70%

3. **启用自动关闭**
   - 开发环境下班后自动关闭
   - 可节省 50%+

---

## ✅ 验证清单

完成 EC2 创建后：

- [ ] 实例状态显示 "Running"
- [ ] Elastic IP 已关联
- [ ] 安全组规则正确配置
- [ ] SSH 连接测试成功
- [ ] 可以执行 `sudo apt update`

---

## 🔄 后续步骤与 Lightsail 相同

完成 EC2 创建后，后续步骤完全相同：

1. **运行初始化脚本:**
   ```bash
   # 上传脚本
   scp -i gogojap-ec2-key.pem \
     scripts/setup-lightsail.sh \
     ubuntu@YOUR_ELASTIC_IP:~/

   # 连接并运行（脚本名称虽然叫 setup-lightsail，但同样适用于 EC2）
   ssh -i gogojap-ec2-key.pem ubuntu@YOUR_ELASTIC_IP
   chmod +x setup-lightsail.sh
   ./setup-lightsail.sh
   ```

2. **继续数据库和存储迁移**
3. **部署应用**

---

## 💡 EC2 的额外优势

### 1. 更灵活的实例类型

可以轻松调整实例大小：
```bash
t3.small  (1 vCPU, 2GB) - $15/月
t3.medium (2 vCPU, 4GB) - $30/月
t3.large  (2 vCPU, 8GB) - $60/月
```

### 2. Auto Scaling

可配置自动扩展（未来需要时）：
```yaml
最小实例: 1
最大实例: 5
目标 CPU 使用率: 70%
```

### 3. 负载均衡

可添加 Application Load Balancer：
```yaml
高可用架构:
  ALB → 多个 EC2 实例
  自动健康检查
  自动故障转移
```

### 4. 更详细的监控

CloudWatch 提供更多指标：
- CPU 使用率
- 网络流量
- 磁盘 I/O
- 自定义指标

---

## 🚨 常见问题

### Q1: EC2 比 Lightsail 难配置吗？

**A:** 稍微复杂一点，但我们提供的脚本可以自动化大部分配置。

### Q2: 可以随时切换回 Lightsail 吗？

**A:** 可以！等 Lightsail 可用后，可以创建 AMI 镜像迁移过去。

### Q3: EC2 会不会突然产生高额费用？

**A:** 不会，我们的配置是固定实例 + 有限流量，成本可控。建议设置预算告警。

---

## 📝 凭证记录（EC2 版本）

更新 `aws-credentials.env`:

```bash
# ==================== EC2 (替代 Lightsail) ====================
EC2_INSTANCE_ID=i-xxxxxxxxxx
EC2_ELASTIC_IP=
EC2_SSH_KEY=gogojap-ec2-key.pem
EC2_SECURITY_GROUP=gogojap-sg

# 其他配置与 Lightsail 相同
```

---

## 🎯 总结

**如果 Lightsail 不可用，使用 EC2 是完美替代方案：**

✅ 成本更低（$30-40 vs $44）
✅ 功能更强大
✅ 后续步骤完全相同
✅ 可随时升级配置

**唯一缺点:** 配置稍复杂（但我们的脚本已简化）

---

**创建日期:** 2026-02-10
**适用于:** AWS 新账号或 Lightsail 访问受限场景
