#!/bin/bash
# =============================================
# GoGoJap - 一鍵啟動 / 更新腳本
# =============================================
# 用法：
#   bash start.sh          # 首次啟動或更新
#   bash start.sh stop     # 停止所有服務
#   bash start.sh logs     # 查看日誌
#   bash start.sh status   # 查看狀態
#   bash start.sh backup   # 備份 Redis
#   bash start.sh ssl      # 設置 Let's Encrypt SSL
# =============================================

set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
COMPOSE_FILE="${APP_DIR}/docker-compose.vultr.yml"
COMPOSE="docker compose -f ${COMPOSE_FILE}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# ==================== 前置檢查 ====================
check_env() {
    if [ ! -f "${APP_DIR}/.env" ]; then
        log_error ".env 不存在"
        echo "  cp ${APP_DIR}/.env.template ${APP_DIR}/.env"
        echo "  nano ${APP_DIR}/.env"
        exit 1
    fi
}

# ==================== 啟動 / 更新 ====================
cmd_start() {
    check_env
    log_info "建構並啟動所有服務..."

    # 建構後端鏡像
    ${COMPOSE} build --parallel backend celery-worker celery-beat

    # 啟動所有服務
    ${COMPOSE} up -d

    log_info "等待服務就緒..."
    sleep 8

    # 健康檢查
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Backend 健康檢查通過"
    else
        log_error "Backend 啟動失敗"
        ${COMPOSE} logs --tail=30 backend
        exit 1
    fi

    echo ""
    ${COMPOSE} ps
    echo ""
    log_success "所有服務已啟動"
    echo ""
    echo "  API:      http://$(hostname -I | awk '{print $1}'):8000"
    echo "  API Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
    echo "  日誌:     bash start.sh logs"
}

# ==================== 停止 ====================
cmd_stop() {
    log_info "停止所有服務..."
    ${COMPOSE} down
    log_success "已停止"
}

# ==================== 日誌 ====================
cmd_logs() {
    ${COMPOSE} logs -f --tail=100 "${@:2}"
}

# ==================== 狀態 ====================
cmd_status() {
    ${COMPOSE} ps
    echo ""
    # Redis 記憶體
    if docker exec gogojap-redis redis-cli info memory 2>/dev/null | grep -q used_memory_human; then
        echo "Redis 記憶體: $(docker exec gogojap-redis redis-cli info memory | grep used_memory_human | cut -d: -f2 | tr -d '\r')"
    fi
    # 磁碟
    echo "磁碟用量: $(df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 ")"}')"
    echo "記憶體: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
}

# ==================== 備份 ====================
cmd_backup() {
    BACKUP_DIR="${APP_DIR}/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "${BACKUP_DIR}"

    log_info "備份 Redis..."
    docker exec gogojap-redis redis-cli BGSAVE
    sleep 2
    docker cp gogojap-redis:/data/dump.rdb "${BACKUP_DIR}/redis.rdb" 2>/dev/null || true

    log_success "備份完成: ${BACKUP_DIR}"
    echo "  保留最近 7 份備份..."
    ls -dt "${APP_DIR}/backups"/*/ 2>/dev/null | tail -n +8 | xargs rm -rf 2>/dev/null || true
}

# ==================== SSL (Let's Encrypt) ====================
cmd_ssl() {
    if [ -z "${GOGOJAP_DOMAIN:-}" ] && [ -f "${APP_DIR}/.env" ]; then
        source "${APP_DIR}/.env"
    fi

    if [ -z "${GOGOJAP_DOMAIN:-}" ]; then
        log_error "請設置 GOGOJAP_DOMAIN 環境變量"
        exit 1
    fi

    log_info "為 ${GOGOJAP_DOMAIN} 申請 SSL 證書..."

    apt-get install -y -qq certbot
    certbot certonly --standalone \
        -d "${GOGOJAP_DOMAIN}" \
        --non-interactive \
        --agree-tos \
        --email "admin@${GOGOJAP_DOMAIN}" \
        --http-01-port 80

    # 複製證書到 deploy/ssl
    cp "/etc/letsencrypt/live/${GOGOJAP_DOMAIN}/fullchain.pem" "${APP_DIR}/ssl/"
    cp "/etc/letsencrypt/live/${GOGOJAP_DOMAIN}/privkey.pem" "${APP_DIR}/ssl/"

    log_success "SSL 證書已安裝"
    log_info "請修改 nginx/conf.d/gogojap.conf 啟用 HTTPS 配置，然後重啟："
    echo "  bash start.sh start"
}

# ==================== 路由 ====================
case "${1:-start}" in
    start|up)     cmd_start ;;
    stop|down)    cmd_stop ;;
    logs)         cmd_logs "$@" ;;
    status|ps)    cmd_status ;;
    backup)       cmd_backup ;;
    ssl)          cmd_ssl ;;
    restart)      cmd_stop; cmd_start ;;
    *)
        echo "用法: bash start.sh {start|stop|restart|logs|status|backup|ssl}"
        exit 1
        ;;
esac
