#!/bin/bash
# =============================================
# GoGoJap 系統部署腳本
# =============================================
# 功能：首次部署或完整重新部署
# =============================================

set -e  # 遇到錯誤立即退出

# ==================== 顏色輸出 ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ==================== 輔助函數 ====================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ==================== 前置檢查 ====================
log_info "開始前置檢查..."

# 檢查 Docker
if ! command -v docker &> /dev/null; then
    log_error "Docker 未安裝，請先安裝 Docker"
    exit 1
fi

# 檢查 Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    log_error "Docker Compose 未安裝，請先安裝 Docker Compose"
    exit 1
fi

# 檢查配置文件
if [ ! -f ".env" ]; then
    log_error ".env 文件不存在"
    log_info "請從 .env.production.template 複製並填入實際配置："
    log_info "  cp .env.production.template .env"
    log_info "  nano .env"
    exit 1
fi

log_success "前置檢查通過"

# ==================== 載入配置 ====================
log_info "載入環境配置..."
set -a
source .env
set +a

# ==================== 確認部署 ====================
echo ""
log_warning "即將部署 GoGoJap 系統"
log_info "Registry: ${REGISTRY_URL}"
log_info "Version: ${VERSION}"
echo ""
read -p "確認要繼續部署嗎？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "部署已取消"
    exit 0
fi

# ==================== 登入 Registry ====================
log_info "登入 Container Registry..."
if [ ! -z "${REGISTRY_URL}" ]; then
    docker login ${REGISTRY_URL}
fi

# ==================== 拉取最新鏡像 ====================
log_info "拉取最新鏡像..."
docker-compose -f docker-compose.production.yml pull

# ==================== 備份現有數據（如果有）====================
if docker-compose -f docker-compose.production.yml ps -q redis &> /dev/null; then
    log_info "備份現有 Redis 數據..."
    BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p ${BACKUP_DIR}

    docker run --rm \
        -v gogojap_redis_data:/data \
        -v ${BACKUP_DIR}:/backup \
        alpine tar czf /backup/redis-backup.tar.gz /data

    log_success "Redis 數據已備份到 ${BACKUP_DIR}"
fi

# ==================== 停止舊容器 ====================
log_info "停止舊容器..."
docker-compose -f docker-compose.production.yml down

# ==================== 啟動新容器 ====================
log_info "啟動新容器..."
docker-compose -f docker-compose.production.yml up -d

# ==================== 等待服務就緒 ====================
log_info "等待服務啟動..."
sleep 10

# ==================== 健康檢查 ====================
log_info "進行健康檢查..."

# 檢查 Backend
if curl -f http://localhost:8000/health &> /dev/null; then
    log_success "Backend 健康檢查通過"
else
    log_error "Backend 健康檢查失敗"
    docker-compose -f docker-compose.production.yml logs backend
    exit 1
fi

# 檢查 Frontend
if curl -f http://localhost:3000/ &> /dev/null; then
    log_success "Frontend 健康檢查通過"
else
    log_warning "Frontend 健康檢查失敗，請檢查日誌"
fi

# ==================== 檢查服務狀態 ====================
log_info "服務狀態："
docker-compose -f docker-compose.production.yml ps

# ==================== 完成 ====================
echo ""
log_success "========================================="
log_success "GoGoJap 系統部署完成！"
log_success "========================================="
echo ""
log_info "訪問地址："
log_info "  前端界面: http://localhost:3000"
log_info "  後端 API: http://localhost:8000"
log_info "  API 文檔: http://localhost:8000/docs"
echo ""
log_info "查看日誌："
log_info "  docker-compose -f docker-compose.production.yml logs -f"
echo ""
