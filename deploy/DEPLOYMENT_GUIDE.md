# GoGoJap 系統部署指南

> 本指南供甲方運維人員使用，用於部署和管理系統容器。

## 前置條件

- Docker 20.10+
- Docker Compose 2.0+
- 可訪問技術方提供的 Container Registry
- 已配置好的 PostgreSQL 數據庫
- 已準備好的第三方 API 密鑰

## 快速部署

### 步驟 1：準備環境配置

```bash
# 複製配置範本
cp .env.production.template .env

# 編輯配置文件，填入實際值
nano .env
```

### 步驟 2：登入 Container Registry

```bash
# Azure Container Registry
docker login your-registry.azurecr.io -u username -p password

# AWS ECR
aws ecr get-login-password | docker login --username AWS --password-stdin your-registry

# Docker Hub
docker login -u username -p password
```

### 步驟 3：拉取鏡像

```bash
docker-compose -f docker-compose.production.yml pull
```

### 步驟 4：啟動服務

```bash
# 啟動所有服務
docker-compose -f docker-compose.production.yml up -d

# 查看服務狀態
docker-compose -f docker-compose.production.yml ps
```

## 服務端口

| 服務 | 端口 | 說明 |
|------|------|------|
| Frontend | 3000 | Web 界面 |
| Backend | 8000 | API 服務 |
| Redis | 6379 | 消息隊列（內部） |

## 常用操作

### 查看日誌

```bash
# 所有服務日誌
docker-compose -f docker-compose.production.yml logs -f

# 特定服務日誌
docker-compose -f docker-compose.production.yml logs -f backend
docker-compose -f docker-compose.production.yml logs -f celery-worker
```

### 重啟服務

```bash
# 重啟所有服務
docker-compose -f docker-compose.production.yml restart

# 重啟特定服務
docker-compose -f docker-compose.production.yml restart backend
```

### 更新版本

```bash
# 1. 更新 .env 中的 VERSION
VERSION=v1.2.3

# 2. 拉取新鏡像
docker-compose -f docker-compose.production.yml pull

# 3. 重新部署
docker-compose -f docker-compose.production.yml up -d
```

### 停止服務

```bash
# 停止但保留數據
docker-compose -f docker-compose.production.yml stop

# 完全停止並刪除容器
docker-compose -f docker-compose.production.yml down

# 停止並刪除數據卷（慎用）
docker-compose -f docker-compose.production.yml down -v
```

## 數據備份

### Redis 數據

```bash
# Redis 數據存儲在 Docker volume 中
docker run --rm -v gogojap_redis_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/redis-backup.tar.gz /data
```

### 數據庫備份

```bash
# 使用 pg_dump（數據庫由甲方管理）
pg_dump -h your-db-host -U username -d gogojap -Fc > backup.dump
```

## 監控與健康檢查

### 檢查服務健康狀態

```bash
# 檢查 API 健康
curl http://localhost:8000/health

# 檢查前端
curl http://localhost:3000/
```

### 檢查容器狀態

```bash
docker-compose -f docker-compose.production.yml ps
```

## 故障排除

### 問題：服務無法啟動

```bash
# 檢查日誌
docker-compose -f docker-compose.production.yml logs backend

# 常見原因：
# 1. 數據庫連接失敗 - 檢查 DATABASE_URL
# 2. API 密鑰錯誤 - 檢查 FIRECRAWL_API_KEY, ANTHROPIC_API_KEY
# 3. 鏡像拉取失敗 - 檢查 Registry 登入
```

### 問題：定時任務不執行

```bash
# 檢查 Celery Beat
docker-compose -f docker-compose.production.yml logs celery-beat

# 檢查 Celery Worker
docker-compose -f docker-compose.production.yml logs celery-worker
```

### 問題：Redis 連接失敗

```bash
# 檢查 Redis 是否運行
docker-compose -f docker-compose.production.yml ps redis

# 進入 Redis 容器測試
docker exec -it gogojap-redis redis-cli ping
```

## 聯繫技術支援

如遇到無法解決的問題，請聯繫技術方：

- 提供：錯誤日誌、操作步驟、環境信息
- 切勿：分享 .env 文件中的敏感密鑰

---

*文檔版本：1.0 | 最後更新：2026-01*
