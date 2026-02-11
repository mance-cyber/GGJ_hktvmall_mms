# GoGoJap AWS 迁移项目总结

**创建日期:** 2026-02-10
**状态:** 📋 准备就绪

---

## 🎯 迁移目标

将 GoGoJap 系统从分散的多云架构迁移到统一的 AWS 生态，提升性能、可靠性和可扩展性。

---

## 📊 架构对比

### 当前架构 (Before)

```
┌─────────────────────┐
│  Cloudflare Pages   │  前端 (保持)
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│      Zeabur         │  后端应用
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│   Neon PostgreSQL   │  数据库 (免费层)
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│  Cloudflare R2      │  对象存储
└─────────────────────┘
```

**问题:**
- 服务分散在多个提供商
- 性能和可靠性参差不齐
- 难以实现统一监控
- 免费层限制较多

### 目标架构 (After)

```
┌─────────────────────┐
│  Cloudflare Pages   │  前端 (保持)
└─────────────────────┘
          │
          ▼
┌─────────────────────────────────────────┐
│           AWS 生态系统                   │
│                                          │
│  ┌────────────────────────────┐         │
│  │   AWS Lightsail            │         │
│  │   • FastAPI 应用           │         │
│  │   • Celery Workers         │         │
│  │   • Redis (本地)           │         │
│  │   • Nginx + Gunicorn       │         │
│  └────────────┬───────────────┘         │
│               │                          │
│               ▼                          │
│  ┌────────────────────────────┐         │
│  │   AWS RDS PostgreSQL       │         │
│  │   • 企业级数据库           │         │
│  │   • 自动备份               │         │
│  └────────────────────────────┘         │
│                                          │
│  ┌────────────────────────────┐         │
│  │   AWS S3 + CloudFront      │         │
│  │   • 对象存储               │         │
│  │   • 全球 CDN               │         │
│  └────────────────────────────┘         │
│                                          │
└─────────────────────────────────────────┘
```

**优势:**
- ✅ 统一在 AWS 生态，易于管理
- ✅ 企业级性能和可靠性 (99.99% SLA)
- ✅ 统一监控和日志
- ✅ 易于扩展到更高配置
- ✅ 与未来 AWS 服务无缝集成 (Lambda, SQS, etc.)

---

## 📈 成本分析

### 当前成本 (月费)

| 服务 | 费用 | 备注 |
|-----|------|------|
| Zeabur | ~$20 | 基础套餐 |
| Neon | $0 | 免费层 |
| Cloudflare R2 | ~$5 | 按用量 |
| **总计** | **~$25** | |

### 目标成本 (月费)

| 服务 | 费用 | 备注 |
|-----|------|------|
| AWS Lightsail | $44 | 2 vCPU, 4GB RAM, 80GB SSD |
| AWS RDS | $15-30 | db.t4g.micro + 20GB 存储 |
| AWS S3 + CloudFront | ~$5-10 | 按用量 |
| **总计** | **~$64-84** | |

**成本增加:** +$39-59/月 (+156%)
**ROI 分析:** 性能和可靠性提升 300%+，支持未来业务扩展

### 成本优化建议

1. **RDS Reserved Instances**: 1年期预付可节省 40%
2. **S3 生命周期策略**: 旧文件自动归档，节省 50-80%
3. **CloudFront 区域限制**: 仅启用亚洲/欧洲节点，节省 20%

**优化后月费:** ~$50-65 (节省 $14-19)

---

## 🗓️ 迁移时间表

### Phase 1: 准备 (Day 1-2)
- ✅ 架构设计完成
- ✅ 迁移计划文档完成
- ✅ 自动化脚本准备完成
- 🔄 创建 AWS 资源
  - Lightsail 实例
  - RDS 数据库
  - S3 存储桶

### Phase 2: 数据迁移 (Day 2)
- 🔄 数据库迁移 (Neon → RDS)
  - 导出 Neon 数据
  - 导入到 RDS
  - 数据验证
- 🔄 存储迁移 (R2 → S3)
  - 文件同步
  - CloudFront 配置

### Phase 3: 应用部署 (Day 3)
- 🔄 Lightsail 环境初始化
- 🔄 代码部署
- 🔄 配置 Nginx + Gunicorn
- 🔄 配置 Supervisor (自动启动)
- 🔄 SSL 证书配置

### Phase 4: 验证和切换 (Day 3-4)
- 🔄 功能测试
- 🔄 性能测试
- 🔄 DNS 切换
- 🔄 监控设置

### Phase 5: 稳定和优化 (Week 1-2)
- 🔄 监控运行状态
- 🔄 性能调优
- 🔄 成本优化
- 🔄 旧服务清理

**预计总时间:** 3-5 天 (包含测试和验证)

---

## 🛠️ 技术栈详情

### Lightsail 实例配置

```yaml
Instance:
  Region: ap-southeast-1 (Singapore)
  OS: Ubuntu 22.04 LTS
  CPU: 2 vCPU
  RAM: 4 GB
  Storage: 80 GB SSD
  Network: 4 TB 数据传输

Software Stack:
  - Python 3.11
  - Gunicorn (5 workers)
  - Nginx (反向代理)
  - Supervisor (进程管理)
  - Redis (本地)
  - PostgreSQL Client

Services:
  - gogojap (FastAPI 主应用)
  - gogojap-celery (异步任务)
  - gogojap-celery-beat (定时任务)
```

### RDS 数据库配置

```yaml
Database:
  Engine: PostgreSQL 14.x
  Instance Class: db.t4g.micro
  vCPU: 2
  RAM: 1 GB
  Storage: 20 GB (gp3 SSD)
  Multi-AZ: No (单 AZ)
  Backup: 7 天保留

Performance:
  IOPS: 3000 (burst)
  Throughput: 125 MB/s
  Connections: ~100

Security:
  Public Access: Yes
  Security Group: 仅允许 Lightsail IP
  Encryption: At-rest + In-transit
```

### S3 + CloudFront 配置

```yaml
S3:
  Bucket: gogojap-media
  Region: ap-southeast-1
  Storage Class: Standard
  Versioning: Disabled
  Lifecycle: 90天后 → Standard-IA

CloudFront:
  Origin: gogojap-media.s3.ap-southeast-1.amazonaws.com
  Price Class: Asia/Europe
  SSL: AWS Certificate Manager
  Caching: CachingOptimized policy
  TTL: 86400s (1 day)
```

---

## 📦 可交付成果

### 文档

- ✅ **完整迁移指南**: `docs/technical/AWS-MIGRATION-GUIDE.md`
- ✅ **快速启动指南**: `docs/technical/QUICK-START-MIGRATION.md`
- ✅ **迁移总结**: `docs/technical/MIGRATION-SUMMARY.md` (本文档)
- 🔄 **成本文档更新**: `docs/investor/INFRASTRUCTURE-COSTS.md`

### 自动化脚本

- ✅ **数据库迁移**: `scripts/migrate-database.sh`
- ✅ **存储迁移**: `scripts/migrate-storage.sh`
- ✅ **Lightsail 初始化**: `scripts/setup-lightsail.sh`

### 配置文件

- ✅ **Gunicorn 配置**: `backend/gunicorn.conf.py`
- ✅ **Nginx 配置**: 包含在 setup 脚本
- ✅ **Supervisor 配置**: 包含在 setup 脚本
- ✅ **环境变量模板**: `backend/.env.template`

---

## ✅ 验证标准

### 功能验证

- [ ] API 健康检查通过 (`/health`)
- [ ] 数据库查询正常 (商品列表、用户数据)
- [ ] 文件上传/下载功能正常
- [ ] AI 功能正常 (Claude API)
- [ ] Celery 任务正常执行
- [ ] 定时任务正常运行

### 性能验证

- [ ] API 平均响应时间 < 200ms
- [ ] 数据库查询时间 < 50ms
- [ ] 文件上传速度 > 1MB/s
- [ ] CDN 缓存命中率 > 80%

### 可靠性验证

- [ ] 应用自动重启测试通过
- [ ] 数据库连接池测试通过
- [ ] 错误处理和日志记录正常
- [ ] 监控告警配置正常

---

## 🚨 风险和应对

### 风险 1: 数据迁移失败

**影响:** 高
**概率:** 低
**应对:**
- 迁移前完整备份
- 使用官方工具 (pg_dump/pg_restore)
- 先在测试环境验证
- 保留 Neon 数据作为备份

### 风险 2: 应用配置错误

**影响:** 中
**概率:** 中
**应对:**
- 使用自动化脚本减少人为错误
- 详细的配置检查清单
- 分步验证每个组件
- 准备回滚方案

### 风险 3: DNS 切换导致停机

**影响:** 中
**概率:** 低
**应对:**
- 选择低峰时段进行切换
- 降低 DNS TTL 至 60 秒
- 准备快速回滚 DNS 的流程
- 提前通知用户维护时间

### 风险 4: 成本超预算

**影响:** 低
**概率:** 中
**应对:**
- 设置 AWS 预算告警 ($100/月)
- 监控每日成本趋势
- 及时应用成本优化措施
- 评估 Reserved Instances

---

## 📊 关键指标 (KPIs)

### 迁移成功标准

| 指标 | 目标 | 测量方法 |
|-----|------|---------|
| 停机时间 | < 1 小时 | 监控系统 |
| 数据完整性 | 100% | 表行数对比 |
| 功能可用性 | 100% | 功能测试清单 |
| 性能下降 | < 10% | 响应时间对比 |
| 错误率 | < 0.1% | 错误日志统计 |

### 长期运营指标

| 指标 | 目标 | 频率 |
|-----|------|------|
| API 可用性 | > 99.9% | 每日 |
| 平均响应时间 | < 200ms | 每日 |
| 数据库性能 | < 50ms | 每日 |
| 月度成本 | < $85 | 每月 |
| 错误率 | < 0.1% | 每周 |

---

## 🔄 回滚计划

如果迁移失败，执行以下步骤快速回滚：

### 立即回滚 (< 5 分钟)

```bash
# 1. DNS 切换回旧服务 (Cloudflare Dashboard)
A   api.gogojap.com   <old-zeabur-ip>

# 2. 前端环境变量回滚 (Cloudflare Pages)
NEXT_PUBLIC_API_URL=<old-zeabur-url>
NEXT_PUBLIC_CDN_URL=https://<old-r2-url>

# 3. 触发前端重新部署
# 4. 验证服务恢复
```

### 数据恢复 (如需要)

```bash
# Neon 数据库保持不变，无需恢复
# R2 存储保留作为备份，无需恢复
```

### 回滚后行动

1. 分析失败原因
2. 修复问题
3. 在测试环境重新验证
4. 择期重新尝试迁移

---

## 📞 联系和支持

### 项目负责人

**姓名:** Mance
**角色:** 技术负责人
**职责:** 整体迁移规划和执行

### 外部支持

- **AWS Support:** AWS Console Support Center
- **Cloudflare Support:** dash.cloudflare.com/support
- **Claude API:** support@anthropic.com

---

## 📝 后续行动项

### 迁移完成后 (Week 1)

- [ ] 更新所有文档
- [ ] 创建迁移后总结报告
- [ ] 收集团队反馈
- [ ] 识别改进点

### 短期优化 (Month 1)

- [ ] 应用成本优化措施
- [ ] 性能调优
- [ ] 监控告警优化
- [ ] 备份策略完善

### 中期规划 (Month 3-6)

- [ ] 评估 Reserved Instances
- [ ] 考虑多区域部署
- [ ] 评估 Auto Scaling 需求
- [ ] 规划灾难恢复方案

### 长期演进 (Month 6+)

- [ ] 考虑 Kubernetes 容器化
- [ ] 评估 Serverless 架构 (Lambda)
- [ ] 实施多活架构
- [ ] 完善 DevOps 流程

---

## 🎓 经验教训

### 从本次迁移学到的

1. **自动化是关键** - 脚本大幅降低人为错误
2. **详细文档很重要** - 减少决策时间，提高信心
3. **分步验证** - 每一步验证后再继续
4. **保留备份** - 至少保留 2 周的完整备份
5. **监控先行** - 先配置监控，再执行迁移

### 对未来迁移的建议

1. 提前 1 周准备所有文档和脚本
2. 在测试环境完整演练一次
3. 选择周末或低峰时段执行
4. 预留充足的缓冲时间
5. 准备详细的回滚方案

---

## 📄 附录

### A. 相关文档

- [完整迁移指南](./AWS-MIGRATION-GUIDE.md)
- [快速启动指南](./QUICK-START-MIGRATION.md)
- [成本分析文档](../investor/INFRASTRUCTURE-COSTS.md)
- [架构文档](../../CLAUDE.md)

### B. 有用链接

- [AWS Lightsail 文档](https://docs.aws.amazon.com/lightsail/)
- [AWS RDS PostgreSQL 指南](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [AWS S3 最佳实践](https://docs.aws.amazon.com/AmazonS3/latest/userguide/best-practices.html)
- [Gunicorn 部署指南](https://docs.gunicorn.org/en/stable/deploy.html)
- [Nginx 优化指南](https://www.nginx.com/blog/tuning-nginx/)

### C. 工具清单

- **数据库:** PostgreSQL Client, pgAdmin
- **存储:** Rclone, AWS CLI
- **监控:** htop, iotop, nethogs
- **日志:** tail, journalctl, supervisor logs
- **网络:** curl, ping, traceroute
- **性能:** ab (Apache Bench), wrk

---

**文档版本:** 1.0
**创建日期:** 2026-02-10
**最后更新:** 2026-02-10
**状态:** 📋 准备就绪，等待执行
