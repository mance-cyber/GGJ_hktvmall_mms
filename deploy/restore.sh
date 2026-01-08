#!/bin/bash
# =============================================
# GoGoJap 系統恢復腳本
# =============================================
# 功能：從備份恢復 Redis 數據
# =============================================

set -e

# ==================== 顏色輸出 ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ==================== 參數處理 ====================
BACKUP_DIR=${1}

if [ -z "${BACKUP_DIR}" ]; then
    log_error "請指定要恢復的備份目錄"
    log_info "用法: $0 <backup_directory>"
    echo ""
    log_info "可用的備份："
    ls -lht ./backups | head -n 10
    exit 1
fi

if [ ! -d "${BACKUP_DIR}" ]; then
    log_error "備份目錄不存在: ${BACKUP_DIR}"
    exit 1
fi

# ==================== 確認恢復 ====================
echo ""
log_warning "========================================="
log_warning "危險操作：即將恢復數據"
log_warning "========================================="
log_warning "這將覆蓋當前的所有數據！"
echo ""
log_info "恢復來源: ${BACKUP_DIR}"

if [ -f "${BACKUP_DIR}/backup-info.txt" ]; then
    cat "${BACKUP_DIR}/backup-info.txt"
fi

echo ""
read -p "確認要恢復嗎？(輸入 yes 確認): " CONFIRM

if [ "${CONFIRM}" != "yes" ]; then
    log_info "恢復已取消"
    exit 0
fi

# ==================== 停止服務 ====================
log_info "停止服務..."
docker-compose -f docker-compose.production.yml down

# ==================== 備份當前數據 ====================
log_info "先備份當前數據（以防萬一）..."
EMERGENCY_BACKUP="./backups/emergency_$(date +%Y%m%d_%H%M%S)"
mkdir -p ${EMERGENCY_BACKUP}

if docker volume inspect gogojap_redis_data &> /dev/null; then
    docker run --rm \
        -v gogojap_redis_data:/data \
        -v $(pwd)/${EMERGENCY_BACKUP}:/backup \
        alpine tar czf /backup/redis-emergency.tar.gz /data
    log_success "應急備份已創建: ${EMERGENCY_BACKUP}"
fi

# ==================== 恢復 Redis 數據 ====================
if [ -f "${BACKUP_DIR}/redis-backup.tar.gz" ]; then
    log_info "恢復 Redis 數據..."

    # 刪除舊數據
    docker volume rm gogojap_redis_data 2>/dev/null || true

    # 創建新數據卷
    docker volume create gogojap_redis_data

    # 恢復數據
    docker run --rm \
        -v gogojap_redis_data:/data \
        -v $(pwd)/${BACKUP_DIR}:/backup \
        alpine sh -c "cd /data && tar xzf /backup/redis-backup.tar.gz --strip-components=1"

    log_success "Redis 數據已恢復"
else
    log_warning "備份中沒有 Redis 數據"
fi

# ==================== 恢復配置文件 ====================
if [ -f "${BACKUP_DIR}/env-backup.txt" ]; then
    log_info "配置文件參考："
    log_warning "請手動檢查 ${BACKUP_DIR}/env-backup.txt 並根據需要更新 .env"
fi

# ==================== 恢復數據庫 ====================
if [ -f "${BACKUP_DIR}/database-backup.dump" ]; then
    log_info "發現數據庫備份"
    log_warning "請手動恢復數據庫："
    log_info "  pg_restore -U <user> -d <database> ${BACKUP_DIR}/database-backup.dump"
fi

# ==================== 重啟服務 ====================
log_info "重啟服務..."
docker-compose -f docker-compose.production.yml up -d

# 等待服務就緒
log_info "等待服務啟動..."
sleep 10

# ==================== 完成 ====================
log_success "========================================="
log_success "恢復完成"
log_success "========================================="
echo ""
log_info "服務狀態："
docker-compose -f docker-compose.production.yml ps
echo ""
log_warning "應急備份保存在: ${EMERGENCY_BACKUP}"
log_info "如恢復出現問題，可用此備份回滾"
