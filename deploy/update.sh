#!/bin/bash
# =============================================
# GoGoJap 系統更新腳本
# =============================================
# 功能：滾動更新到新版本（最小停機時間）
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
NEW_VERSION=${1}

if [ -z "${NEW_VERSION}" ]; then
    log_error "請指定要更新的版本號"
    log_info "用法: $0 <version>"
    log_info "範例: $0 v1.2.3"
    exit 1
fi

# ==================== 前置檢查 ====================
log_info "檢查環境..."

if [ ! -f ".env" ]; then
    log_error ".env 文件不存在"
    exit 1
fi

# 載入配置
set -a
source .env
set +a

CURRENT_VERSION=${VERSION}

# ==================== 確認更新 ====================
echo ""
log_warning "準備更新 GoGoJap 系統"
log_info "當前版本: ${CURRENT_VERSION}"
log_info "目標版本: ${NEW_VERSION}"
echo ""
read -p "確認要更新嗎？(y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "更新已取消"
    exit 0
fi

# ==================== 備份 ====================
log_info "自動備份當前數據..."
./backup.sh

# ==================== 更新版本號 ====================
log_info "更新 .env 文件中的版本號..."
sed -i "s/VERSION=.*/VERSION=${NEW_VERSION}/" .env

# ==================== 拉取新鏡像 ====================
log_info "拉取新版本鏡像..."
docker-compose -f docker-compose.production.yml pull

# ==================== 滾動更新 ====================
log_info "執行滾動更新（逐個服務重啟）..."

# 定義更新順序
SERVICES=("backend" "celery-worker" "celery-beat" "frontend")

for SERVICE in "${SERVICES[@]}"; do
    log_info "更新服務: ${SERVICE}"

    # 更新單個服務
    docker-compose -f docker-compose.production.yml up -d --no-deps ${SERVICE}

    # 等待服務就緒
    log_info "等待 ${SERVICE} 就緒..."
    sleep 5

    # 健康檢查
    if [ "${SERVICE}" == "backend" ]; then
        for i in {1..12}; do
            if curl -f http://localhost:8000/health &> /dev/null; then
                log_success "${SERVICE} 健康檢查通過"
                break
            fi
            if [ $i -eq 12 ]; then
                log_error "${SERVICE} 健康檢查失敗"
                log_info "正在回滾..."
                sed -i "s/VERSION=.*/VERSION=${CURRENT_VERSION}/" .env
                docker-compose -f docker-compose.production.yml up -d --no-deps ${SERVICE}
                exit 1
            fi
            sleep 5
        done
    elif [ "${SERVICE}" == "frontend" ]; then
        for i in {1..12}; do
            if curl -f http://localhost:3000/ &> /dev/null; then
                log_success "${SERVICE} 健康檢查通過"
                break
            fi
            if [ $i -eq 12 ]; then
                log_warning "${SERVICE} 健康檢查未通過，但繼續流程"
                break
            fi
            sleep 5
        done
    else
        # Worker 和 Beat 檢查日誌
        if docker-compose -f docker-compose.production.yml logs --tail=10 ${SERVICE} | grep -q "ready"; then
            log_success "${SERVICE} 啟動成功"
        else
            log_warning "${SERVICE} 狀態未確認，請手動檢查"
        fi
    fi
done

# ==================== 清理舊鏡像 ====================
log_info "清理舊版本鏡像..."
docker image prune -f

# ==================== 完成 ====================
echo ""
log_success "========================================="
log_success "系統已成功更新到 ${NEW_VERSION}"
log_success "========================================="
echo ""
log_info "服務狀態："
docker-compose -f docker-compose.production.yml ps
echo ""
log_info "查看日誌："
log_info "  docker-compose -f docker-compose.production.yml logs -f"
echo ""
