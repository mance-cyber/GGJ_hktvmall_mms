# GoGoJap 部署工具包

> 一站式部署、監控和維護工具集

---

## 文件概覽

### 核心配置

| 文件 | 用途 | 重要性 |
|------|------|-------|
| `docker-compose.production.yml` | 生產環境容器編排 | ⭐⭐⭐⭐⭐ |
| `docker-compose.monitoring.yml` | Prometheus + Grafana 監控 | ⭐⭐⭐⭐ |
| `.env.production.template` | 環境變數模板 | ⭐⭐⭐⭐⭐ |
| `nginx.conf` | Nginx 反向代理配置 | ⭐⭐⭐⭐ |
| `prometheus.yml` | Prometheus 監控配置 | ⭐⭐⭐ |
| `grafana-datasources.yml` | Grafana 數據源 | ⭐⭐⭐ |

### 自動化腳本

| 腳本 | 功能 | 使用頻率 |
|------|------|---------|
| `deploy.sh` | 首次部署 | 一次性 |
| `update.sh` | 滾動更新（無停機） | 每次發版 |
| `backup.sh` | 數據備份 | 每日/每週 |
| `restore.sh` | 數據恢復 | 緊急情況 |
| `cost-monitor.sh` | 成本監控報告 | 每月 |

---

## 快速開始

### 1. 首次部署

```bash
# 配置環境
cp .env.production.template .env
nano .env  # 填入實際配置

# 賦予腳本執行權限
chmod +x *.sh

# 執行部署
./deploy.sh
```

### 2. 更新版本

```bash
# 無停機更新
./update.sh v1.2.3
```

### 3. 啟動監控

```bash
# 啟動 Grafana + Prometheus
docker-compose -f docker-compose.monitoring.yml up -d

# 訪問 Grafana
open http://your-server:3001
# 用戶名: admin
# 密碼: gogojap_admin
```

### 4. 數據備份

```bash
# 立即備份
./backup.sh

# 設置定時備份（每日 2:00 AM）
crontab -e
# 添加：0 2 * * * cd /opt/gogojap/deploy && ./backup.sh
```

### 5. 成本監控

```bash
# 生成成本報告
./cost-monitor.sh

# 查看報告
cat ./cost-reports/cost-report-*.txt
```

---

## 腳本詳解

### deploy.sh - 首次部署

**功能**：
- 環境檢查（Docker, Docker Compose）
- 配置文件驗證
- 登入 Container Registry
- 拉取最新鏡像
- 備份現有數據（如果有）
- 啟動所有服務
- 健康檢查

**用法**：
```bash
./deploy.sh
```

**適用場景**：
- 首次部署到新伺服器
- 完全重新部署

---

### update.sh - 滾動更新

**功能**：
- 自動備份當前數據
- 更新版本號
- 逐個服務滾動更新
- 健康檢查
- 失敗自動回滾

**用法**：
```bash
./update.sh v1.2.3
```

**優勢**：
- 最小停機時間（接近零停機）
- 自動回滾機制
- 逐個服務更新，降低風險

---

### backup.sh - 數據備份

**備份內容**：
- Redis 數據
- 配置文件
- PostgreSQL 數據庫（如果是本地）

**保留策略**：
- 保留最近 30 個備份
- 自動清理舊備份

**用法**：
```bash
./backup.sh
```

**自動化**：
```bash
# 每日 2:00 AM 自動備份
0 2 * * * cd /opt/gogojap/deploy && ./backup.sh

# 每週日完整備份
0 3 * * 0 cd /opt/gogojap/deploy && ./backup.sh
```

---

### restore.sh - 數據恢復

**功能**：
- 從備份恢復 Redis 數據
- 創建應急備份
- 恢復配置文件

**用法**：
```bash
# 查看可用備份
ls -lht ./backups

# 恢復指定備份
./restore.sh ./backups/20260106_143000
```

**注意事項**：
- 恢復前會創建應急備份
- 會停止所有服務
- 需要輸入 "yes" 確認

---

### cost-monitor.sh - 成本監控

**監控項目**：
- CPU 核心數與使用率
- 內存總量與使用量
- 磁盤使用情況
- Docker 卷大小
- 容器資源消耗

**成本估算**：
- 計算資源成本
- 存儲成本
- 帶寬成本
- API 調用成本

**用法**：
```bash
./cost-monitor.sh
```

**輸出**：
- 詳細成本報告（保存在 `./cost-reports/`）
- 優化建議

---

## Nginx 配置

### 功能

- **SSL 終止**：HTTPS 自動重定向
- **反向代理**：前端 + 後端統一入口
- **速率限制**：防止 API 濫用
- **Gzip 壓縮**：節省帶寬
- **安全 Headers**：XSS, CSRF 保護

### 配置步驟

```bash
# 安裝 Nginx
apt install nginx -y

# 複製配置
cp nginx.conf /etc/nginx/sites-available/gogojap
ln -s /etc/nginx/sites-available/gogojap /etc/nginx/sites-enabled/

# 編輯域名
nano /etc/nginx/sites-available/gogojap
# 替換 your-domain.com

# 測試配置
nginx -t

# 重啟
systemctl restart nginx
```

### SSL 證書（Let's Encrypt）

```bash
# 安裝 Certbot
apt install certbot python3-certbot-nginx -y

# 獲取證書
certbot --nginx -d your-domain.com

# 自動續期
crontab -e
# 添加：0 3 * * * certbot renew --quiet
```

---

## 監控服務

### 包含組件

1. **Prometheus**：指標收集與存儲
2. **Grafana**：可視化儀表板
3. **Node Exporter**：主機指標
4. **cAdvisor**：容器指標

### 啟動監控

```bash
# 啟動監控棧
docker-compose -f docker-compose.monitoring.yml up -d

# 查看狀態
docker-compose -f docker-compose.monitoring.yml ps
```

### 訪問地址

| 服務 | URL | 用途 |
|------|-----|------|
| Grafana | http://your-server:3001 | 儀表板 |
| Prometheus | http://your-server:9090 | 原始指標 |
| Node Exporter | http://your-server:9100 | 主機指標 |
| cAdvisor | http://your-server:8080 | 容器指標 |

### 預設告警

建議在 Grafana 中配置以下告警：

- CPU > 80%（持續 5 分鐘）
- 內存 > 85%
- 磁盤 > 90%
- API 響應時間 > 2 秒
- 錯誤率 > 5%

---

## 故障排查

### 日誌查看

```bash
# 所有服務日誌
docker-compose -f docker-compose.production.yml logs -f

# 特定服務日誌
docker-compose -f docker-compose.production.yml logs -f backend

# 最近 100 行
docker-compose -f docker-compose.production.yml logs --tail=100 celery-worker
```

### 服務重啟

```bash
# 重啟所有服務
docker-compose -f docker-compose.production.yml restart

# 重啟單個服務
docker-compose -f docker-compose.production.yml restart backend
```

### 健康檢查

```bash
# Backend 健康
curl http://localhost:8000/health

# Frontend 健康
curl http://localhost:3000/

# 容器狀態
docker-compose -f docker-compose.production.yml ps
```

---

## 安全建議

### 必做項目

- [ ] 更改 Grafana 默認密碼
- [ ] 配置防火牆（ufw/firewalld）
- [ ] 使用 SSH 密鑰認證
- [ ] 配置 SSL 證書
- [ ] 限制數據庫遠程訪問
- [ ] 定期更新系統和 Docker
- [ ] 啟用自動備份
- [ ] 配置日誌監控

### 防火牆配置

```bash
# 安裝 ufw
apt install ufw -y

# 允許 SSH
ufw allow 22/tcp

# 允許 HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# 啟用防火牆
ufw enable

# 查看狀態
ufw status
```

---

## 維護計劃

### 每日

- [ ] 檢查服務狀態
- [ ] 查看錯誤日誌
- [ ] 監控 Grafana 儀表板

### 每週

- [ ] 執行數據備份
- [ ] 清理 Docker 資源
- [ ] 檢查磁盤使用

### 每月

- [ ] 生成成本報告
- [ ] 檢查安全更新
- [ ] 審計訪問日誌
- [ ] 優化數據庫性能

---

## 聯繫支援

如遇到無法解決的問題：

1. 收集錯誤日誌
2. 記錄操作步驟
3. 檢查 [DEPLOYMENT.md](../DEPLOYMENT.md) 故障排除章節
4. 聯繫技術支援

---

**文檔版本**：1.0
**最後更新**：2026-01
**維護者**：GoGoJap 技術團隊
