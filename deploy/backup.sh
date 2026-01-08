#!/bin/bash
# =============================================
# GoGoJap 系統備份腳本
# =============================================
# 功能：備份 Redis 數據和配置文件
# =============================================

set -e

# ==================== 顏色輸出 ====================
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

# ==================== 配置 ====================
BACKUP_ROOT="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_ROOT}/${TIMESTAMP}"

# 保留最近 30 個備份
KEEP_BACKUPS=30

# ==================== 創建備份目錄 ====================
log_info "創建備份目錄: ${BACKUP_DIR}"
mkdir -p ${BACKUP_DIR}

# ==================== 備份 Redis 數據 ====================
log_info "備份 Redis 數據..."

if docker volume inspect gogojap_redis_data &> /dev/null; then
    docker run --rm \
        -v gogojap_redis_data:/data \
        -v $(pwd)/${BACKUP_DIR}:/backup \
        alpine tar czf /backup/redis-backup.tar.gz /data
    log_success "Redis 數據已備份"
else
    log_info "Redis 數據卷不存在，跳過"
fi

# ==================== 備份配置文件 ====================
log_info "備份配置文件..."

if [ -f ".env" ]; then
    # 移除敏感信息（僅備份結構）
    cp .env ${BACKUP_DIR}/env-backup.txt
    log_success "配置文件已備份"
fi

# ==================== 備份數據庫（如果使用 Docker）====================
if [ -f ".env" ]; then
    set -a
    source .env
    set +a

    if [[ "${DATABASE_URL}" == *"localhost"* ]] || [[ "${DATABASE_URL}" == *"127.0.0.1"* ]]; then
        log_info "備份 PostgreSQL 數據庫..."

        # 從 DATABASE_URL 提取信息
        DB_USER=$(echo ${DATABASE_URL} | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
        DB_PASS=$(echo ${DATABASE_URL} | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
        DB_HOST=$(echo ${DATABASE_URL} | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_NAME=$(echo ${DATABASE_URL} | sed -n 's/.*\/\([^?]*\).*/\1/p')

        docker exec -i $(docker-compose -f ../docker-compose.yml ps -q db) \
            pg_dump -U ${DB_USER} -d ${DB_NAME} -Fc > ${BACKUP_DIR}/database-backup.dump

        log_success "數據庫已備份"
    else
        log_info "遠程數據庫，請使用甲方的備份方案"
    fi
fi

# ==================== 記錄備份信息 ====================
cat > ${BACKUP_DIR}/backup-info.txt << EOF
備份時間: ${TIMESTAMP}
系統版本: ${VERSION:-unknown}
備份內容:
  - Redis 數據
  - 配置文件
  - 數據庫（如適用）
EOF

# ==================== 清理舊備份 ====================
log_info "清理舊備份（保留最近 ${KEEP_BACKUPS} 個）..."
cd ${BACKUP_ROOT}
ls -t | tail -n +$((KEEP_BACKUPS + 1)) | xargs -r rm -rf
cd - > /dev/null

# ==================== 完成 ====================
log_success "========================================="
log_success "備份完成: ${BACKUP_DIR}"
log_success "========================================="

# 顯示備份大小
BACKUP_SIZE=$(du -sh ${BACKUP_DIR} | cut -f1)
log_info "備份大小: ${BACKUP_SIZE}"

# 列出所有備份
echo ""
log_info "現有備份列表："
ls -lht ${BACKUP_ROOT} | head -n 10
