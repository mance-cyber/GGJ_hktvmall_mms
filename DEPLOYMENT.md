# GoGoJap 系統完整部署指南

> **目標讀者**：技術決策者、運維工程師
> **內容**：從成本分析到具體部署的完整方案

---

## 目錄

1. [部署策略選擇](#部署策略選擇)
2. [成本分析對比](#成本分析對比)
3. [推薦部署路徑](#推薦部署路徑)
4. [快速開始](#快速開始)
5. [升級與擴展](#升級與擴展)
6. [監控與成本控制](#監控與成本控制)
7. [故障排除](#故障排除)

---

## 部署策略選擇

### Serverless vs 租用伺服器

| 維度 | Serverless (Vercel/AWS Lambda) | 租用伺服器 (VPS/雲端) |
|------|--------------------------------|----------------------|
| **初始成本** | 免費/$20/月起 | $50-500/月 |
| **擴展性** | 自動無限擴展 | 需手動調整配置 |
| **運維複雜度** | 極低（幾乎零運維） | 中等（需要基礎 DevOps 知識） |
| **冷啟動** | 有（1-3 秒） | 無 |
| **執行時間限制** | 有（10-900 秒） | 無 |
| **數據庫** | 需外部托管（PlanetScale, Supabase） | 可自行部署 |
| **長期成本** | 高流量時昂貴 | 可預測，固定成本 |
| **適用階段** | MVP、低流量產品 | 中高流量、穩定產品 |

### GoGoJap 系統的特殊考量

對於 GoGoJap 這類**數據密集型 + 長時間運行任務**的系統：

```
✅ 推薦：租用伺服器
❌ 不推薦：純 Serverless
```

**原因**：

1. **Celery 後台任務**：需要長時間運行的 Worker 進程，Serverless 無法滿足
2. **Redis 持久化**：需要可靠的緩存和隊列服務
3. **數據庫密集操作**：頻繁的 DB 連接，Serverless 連接池限制嚴重
4. **成本可預測性**：爬取任務會產生大量 API 調用，Serverless 成本難以控制

---

## 成本分析對比

### 階段 1：開發測試（0-100 用戶）

| 方案 | 配置 | 月成本 | 適用場景 |
|------|------|--------|---------|
| **本地開發** | Docker Desktop | $0 | 純開發環境 |
| **最小雲端** | DigitalOcean 1GB | $6/月 | 個人測試 |
| **小型雲端** | Linode 2GB RAM + 外部 DB | $50/月 | 小團隊開發 |

### 階段 2：小型生產（100-1000 用戶）

| 方案 | 配置 | 月成本 | 性能 |
|------|------|--------|------|
| **DigitalOcean** | 4GB RAM, 2 vCPU, 80GB SSD | $24/月 | 基礎 |
| **Linode** | 4GB RAM, 2 vCPU, 80GB SSD | $24/月 | 基礎 |
| **Vultr** | 4GB RAM, 2 vCPU, 80GB SSD | $24/月 | 基礎 |
| **AWS Lightsail** | 4GB RAM, 2 vCPU, 80GB SSD | $40/月 | 中等 |
| **+ 外部數據庫** | PlanetScale Free / $29 | $0-29/月 | - |
| **+ Cloudflare R2** | 10GB 存儲 | $0.75/月 | - |
| **總計** | - | **$50-95/月** | - |

### 階段 3：中型生產（1000-10000 用戶）

| 方案 | 配置 | 月成本 |
|------|------|--------|
| **計算** | 8GB RAM, 4 vCPU, 160GB SSD | $96/月 |
| **數據庫** | AWS RDS PostgreSQL (t3.small) | $30/月 |
| **緩存** | AWS ElastiCache Redis (t3.micro) | $15/月 |
| **存儲** | Cloudflare R2 100GB | $7.50/月 |
| **CDN** | Cloudflare Pro | $20/月 |
| **監控** | Datadog Basic | $15/月 |
| **備份** | S3 備份 | $5/月 |
| **總計** | - | **$190/月** |

### 階段 4：大型生產（10000+ 用戶）

| 方案 | 配置 | 月成本 |
|------|------|--------|
| **負載均衡器** | AWS ALB | $16/月 |
| **應用伺服器 x 2** | 16GB RAM, 8 vCPU each | $384/月 |
| **數據庫主從** | RDS db.m5.large (主) + 只讀副本 | $280/月 |
| **Redis 集群** | ElastiCache m5.large | $150/月 |
| **存儲 + CDN** | R2 1TB + Cloudflare Business | $130/月 |
| **監控告警** | Datadog Pro | $45/月 |
| **備份與災難恢復** | 自動備份 + 跨區域 | $50/月 |
| **總計** | - | **$1055/月** |

### 成本優化策略

1. **預留實例**（Reserved Instances）：節省 30-60%
2. **Spot 實例**：非關鍵任務節省 70-90%
3. **CDN 緩存**：減少伺服器流量 50-80%
4. **數據庫查詢優化**：降低 CPU 使用 30-50%
5. **圖片壓縮與 WebP**：節省存儲與帶寬 60%

---

## 推薦部署路徑

### 🚀 路徑 1：從零到 MVP（最快路徑）

```
階段 1: 本地 Docker (1-2 週) → 免費
階段 2: DigitalOcean $12 方案 (1-3 月) → $12/月
階段 3: 升級到 $24 方案 (有付費用戶後) → $24/月
```

### 💼 路徑 2：小型企業穩健路線

```
階段 1: Linode $24 + PlanetScale $29 → $53/月
階段 2: Linode $96 + AWS RDS → $190/月
階段 3: 遷移到 AWS 完整方案 → $1000+/月
```

### 🏢 路徑 3：中大型企業直接起步

```
直接使用 AWS / GCP / Azure 完整方案
初始配置: $500-800/月
包含：高可用、自動備份、監控告警、多區域部署
```

### 針對 GoGoJap 的推薦

**初期（前 3 個月）：**
```
方案: DigitalOcean Droplet $24/月
配置: 4GB RAM, 2 vCPU, 80GB SSD
數據庫: DigitalOcean Managed PostgreSQL $15/月
總成本: $40/月
```

**成長期（3-12 個月）：**
```
方案: Linode 8GB RAM $96/月
配置: 8GB RAM, 4 vCPU, 160GB SSD
數據庫: AWS RDS t3.small $30/月
Redis: 內置於伺服器
總成本: $130/月
```

**穩定期（1 年後）：**
```
方案: AWS EC2 預留實例
配置: m5.xlarge (16GB RAM, 4 vCPU)
數據庫: RDS db.m5.large 主從
Redis: ElastiCache m5.large
總成本: $600-800/月（已優化）
```

---

## 快速開始

### 前置需求

- Docker 20.10+
- Docker Compose 2.0+
- Git

### 本地開發環境

```bash
# 克隆代碼
git clone <repository>
cd gogojap

# 啟動本地開發服務
docker-compose up -d

# 訪問
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### 雲端部署（生產環境）

#### 步驟 1：準備伺服器

以 DigitalOcean 為例：

```bash
# 創建 Droplet
# - 選擇 Ubuntu 22.04 LTS
# - 4GB RAM / 2 vCPU
# - 選擇最近的數據中心

# SSH 登入
ssh root@your-server-ip

# 安裝 Docker
curl -fsSL https://get.docker.com | sh
systemctl start docker
systemctl enable docker

# 安裝 Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

#### 步驟 2：配置環境

```bash
# 進入部署目錄
cd /opt
git clone <repository> gogojap
cd gogojap/deploy

# 複製配置模板
cp .env.production.template .env

# 編輯配置（填入實際值）
nano .env

# 必填項目：
# - DATABASE_URL
# - FIRECRAWL_API_KEY
# - ANTHROPIC_API_KEY
# - SECRET_KEY (使用 openssl rand -hex 32 生成)
```

#### 步驟 3：執行部署

```bash
# 賦予腳本執行權限
chmod +x deploy.sh update.sh backup.sh

# 首次部署
./deploy.sh

# 部署完成後檢查
docker-compose -f docker-compose.production.yml ps
```

#### 步驟 4：配置 Nginx（可選但推薦）

```bash
# 安裝 Nginx
apt update && apt install nginx -y

# 複製配置
cp nginx.conf /etc/nginx/sites-available/gogojap
ln -s /etc/nginx/sites-available/gogojap /etc/nginx/sites-enabled/

# 編輯配置，替換域名
nano /etc/nginx/sites-available/gogojap

# 測試配置
nginx -t

# 重啟 Nginx
systemctl restart nginx
```

#### 步驟 5：配置 SSL（使用 Let's Encrypt）

```bash
# 安裝 Certbot
apt install certbot python3-certbot-nginx -y

# 獲取證書
certbot --nginx -d your-domain.com

# 自動續期
certbot renew --dry-run
```

---

## 升級與擴展

### 垂直擴展（Vertical Scaling）

**適用場景**：流量增長 2-3 倍

**操作步驟**：

```bash
# 1. 備份數據
./backup.sh

# 2. 停止服務
docker-compose -f docker-compose.production.yml down

# 3. 在雲端控制台升級伺服器配置
# （例如從 4GB 升級到 8GB）

# 4. 重啟服務
docker-compose -f docker-compose.production.yml up -d
```

**停機時間**：5-30 分鐘

### 水平擴展（Horizontal Scaling）

**適用場景**：需要高可用、零停機升級

**架構**：

```
               [Load Balancer]
                    |
      +-------------+-------------+
      |                           |
[App Server 1]             [App Server 2]
      |                           |
      +-------------+-------------+
                    |
            [Shared Database]
            [Shared Redis]
```

**部署步驟**：

1. **設置負載均衡器**（AWS ALB / DigitalOcean Load Balancer）
2. **複製應用伺服器**（從現有伺服器克隆）
3. **配置數據庫外部化**（使用 RDS 或 Managed Database）
4. **配置 Redis 外部化**（使用 ElastiCache 或 Managed Redis）

### 無停機升級（Blue-Green Deployment）

```bash
# 使用 update.sh 腳本
./update.sh v1.2.3

# 腳本會自動：
# 1. 備份當前數據
# 2. 拉取新鏡像
# 3. 逐個服務滾動更新
# 4. 健康檢查
# 5. 失敗自動回滾
```

---

## 監控與成本控制

### 啟動監控服務

```bash
cd deploy

# 啟動 Prometheus + Grafana
docker-compose -f docker-compose.monitoring.yml up -d

# 訪問 Grafana
# URL: http://your-server:3001
# 用戶名: admin
# 密碼: gogojap_admin
```

### 成本監控報告

```bash
# 生成成本報告
chmod +x cost-monitor.sh
./cost-monitor.sh

# 報告包含：
# - 資源使用情況
# - 月度成本估算
# - 優化建議
```

### 告警配置

在 Grafana 中配置告警：

1. **CPU 使用率 > 80%**（持續 5 分鐘）
2. **內存使用率 > 85%**
3. **磁盤使用率 > 90%**
4. **API 響應時間 > 2 秒**
5. **錯誤率 > 5%**

### 成本優化 Checklist

- [ ] 使用預留實例（節省 30-60%）
- [ ] 啟用 CDN 緩存（節省帶寬成本）
- [ ] 優化數據庫查詢（降低 CPU）
- [ ] 圖片壓縮與 WebP 格式
- [ ] 清理未使用的 Docker 鏡像和卷
- [ ] 使用 Spot 實例運行非關鍵任務
- [ ] 設置自動關閉開發/測試環境
- [ ] 監控 API 調用頻率，優化爬取策略

---

## 故障排除

### 問題 1：容器無法啟動

```bash
# 檢查日誌
docker-compose -f docker-compose.production.yml logs backend

# 常見原因：
# 1. 數據庫連接失敗 → 檢查 DATABASE_URL
# 2. API 密鑰錯誤 → 檢查 .env 文件
# 3. 端口衝突 → 檢查 8000/3000 端口是否被佔用
```

### 問題 2：數據庫連接失敗

```bash
# 測試數據庫連接
docker exec -it gogojap-backend python -c "
from sqlalchemy import create_engine
engine = create_engine('$DATABASE_URL')
conn = engine.connect()
print('Connection successful!')
"

# 檢查數據庫防火牆規則
# 確保應用伺服器 IP 在白名單中
```

### 問題 3：Redis 連接失敗

```bash
# 檢查 Redis 狀態
docker-compose -f docker-compose.production.yml ps redis

# 測試連接
docker exec -it gogojap-redis redis-cli ping

# 應該返回 PONG
```

### 問題 4：Celery Worker 不執行任務

```bash
# 檢查 Worker 日誌
docker-compose -f docker-compose.production.yml logs celery-worker

# 檢查隊列
docker exec -it gogojap-redis redis-cli LLEN celery

# 手動重啟 Worker
docker-compose -f docker-compose.production.yml restart celery-worker
```

### 問題 5：內存不足

```bash
# 檢查內存使用
free -h

# 檢查 Docker 資源
docker stats

# 臨時解決：重啟服務釋放內存
docker-compose -f docker-compose.production.yml restart

# 長期解決：升級伺服器配置
```

### 問題 6：磁盤空間不足

```bash
# 檢查磁盤使用
df -h

# 清理 Docker 資源
docker system prune -a --volumes

# 清理日誌
journalctl --vacuum-time=7d

# 清理舊備份
cd deploy/backups
ls -t | tail -n +11 | xargs rm -rf
```

### 緊急回滾

```bash
# 使用備份恢復
./restore.sh ./backups/<backup-timestamp>

# 或手動回滾到上一版本
# 1. 修改 .env 中的 VERSION
# 2. 執行 update.sh
```

---

## 附錄

### A. 推薦雲端服務商

| 服務商 | 優勢 | 劣勢 | 適合階段 |
|--------|------|------|----------|
| **DigitalOcean** | 簡單、便宜、文檔好 | 功能較少 | 初期 |
| **Linode** | 性價比高、可靠 | 界面較舊 | 初期-中期 |
| **Vultr** | 全球節點多 | 支援一般 | 初期-中期 |
| **AWS** | 功能最全、生態好 | 複雜、貴 | 中期-大型 |
| **GCP** | 技術先進、AI 友好 | 文檔較差 | 中期-大型 |
| **Azure** | 企業級、合規好 | 貴、複雜 | 大型企業 |

### B. 關鍵配置文件清單

```
deploy/
├── docker-compose.production.yml  # 生產環境容器編排
├── docker-compose.monitoring.yml  # 監控服務
├── .env.production.template       # 環境變數模板
├── nginx.conf                     # Nginx 反向代理
├── prometheus.yml                 # Prometheus 配置
├── grafana-datasources.yml        # Grafana 數據源
├── deploy.sh                      # 部署腳本
├── update.sh                      # 更新腳本
├── backup.sh                      # 備份腳本
├── restore.sh                     # 恢復腳本
└── cost-monitor.sh                # 成本監控腳本
```

### C. 安全檢查清單

- [ ] 更改所有默認密碼
- [ ] 配置防火牆（僅開放必要端口）
- [ ] 使用 SSH 密鑰認證（禁用密碼登入）
- [ ] 配置 SSL/TLS 證書
- [ ] 定期更新系統和 Docker
- [ ] 啟用自動備份
- [ ] 設置日誌監控和告警
- [ ] 限制數據庫遠程訪問
- [ ] 使用環境變數管理敏感信息
- [ ] 定期審計訪問日誌

### D. 性能優化建議

1. **數據庫**
   - 添加適當索引
   - 使用連接池
   - 配置查詢緩存
   - 定期 VACUUM

2. **應用層**
   - 啟用 Gzip 壓縮
   - 使用 Redis 緩存
   - 優化 N+1 查詢
   - 異步處理耗時任務

3. **前端**
   - 使用 CDN
   - 圖片懶加載
   - Code Splitting
   - 啟用瀏覽器緩存

---

**文檔版本**：2.0
**最後更新**：2026-01
**維護者**：GoGoJap 技術團隊