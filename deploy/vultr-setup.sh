#!/bin/bash
# =============================================
# GoGoJap - Vultr VPS 初始化腳本
# =============================================
# 目標環境：Ubuntu 22.04 LTS, Vultr Tokyo 2C/8GB
# 用途：一鍵安裝全部依賴 + 配置系統環境
# 執行：curl -fsSL <url> | bash 或 scp 到伺服器後 bash vultr-setup.sh
# =============================================

set -euo pipefail

# ==================== 顏色輸出 ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# ==================== 基本驗證 ====================
if [ "$(id -u)" -ne 0 ]; then
    log_error "請用 root 執行: sudo bash vultr-setup.sh"
    exit 1
fi

DEPLOY_USER="gogojap"
APP_DIR="/opt/gogojap"
DOMAIN="${GOGOJAP_DOMAIN:-}"

echo ""
echo "============================================="
echo "  GoGoJap VPS 初始化 (Vultr Tokyo)"
echo "============================================="
echo "  系統用戶: ${DEPLOY_USER}"
echo "  安裝目錄: ${APP_DIR}"
echo "============================================="
echo ""

# ==================== 1. 系統更新 ====================
log_info "1/8 系統更新..."
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq
log_success "系統更新完成"

# ==================== 2. 安裝基礎工具 ====================
log_info "2/8 安裝基礎工具..."
apt-get install -y -qq \
    curl wget git unzip htop \
    ca-certificates gnupg lsb-release \
    ufw fail2ban \
    software-properties-common
log_success "基礎工具安裝完成"

# ==================== 3. 安裝 Docker ====================
log_info "3/8 安裝 Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    log_success "Docker 安裝完成"
else
    log_success "Docker 已存在，跳過"
fi

# 安裝 Docker Compose plugin
if ! docker compose version &> /dev/null; then
    apt-get install -y -qq docker-compose-plugin
    log_success "Docker Compose 安裝完成"
else
    log_success "Docker Compose 已存在，跳過"
fi

# ==================== 4. 建立部署用戶 ====================
log_info "4/8 建立部署用戶 ${DEPLOY_USER}..."
if ! id "${DEPLOY_USER}" &> /dev/null; then
    useradd -m -s /bin/bash "${DEPLOY_USER}"
    usermod -aG docker "${DEPLOY_USER}"
    log_success "用戶 ${DEPLOY_USER} 已建立"
else
    usermod -aG docker "${DEPLOY_USER}"
    log_success "用戶 ${DEPLOY_USER} 已存在，已加入 docker 群組"
fi

# ==================== 5. 建立目錄結構 ====================
log_info "5/8 建立目錄結構..."
mkdir -p "${APP_DIR}"/{data,logs,backups,ssl,openclaw}
chown -R "${DEPLOY_USER}:${DEPLOY_USER}" "${APP_DIR}"
log_success "目錄結構建立完成"

# ==================== 6. 防火牆配置 ====================
log_info "6/8 配置防火牆..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 8000/tcp  # FastAPI (可在 nginx 就緒後關閉)
ufw --force enable
log_success "防火牆配置完成 (SSH + HTTP/S + 8000)"

# ==================== 7. Fail2ban 配置 ====================
log_info "7/8 配置 Fail2ban..."
systemctl enable fail2ban
systemctl start fail2ban
log_success "Fail2ban 已啟動"

# ==================== 8. 系統優化 ====================
log_info "8/8 系統優化..."

# 增加文件描述符限制（爬蟲需要）
cat > /etc/security/limits.d/gogojap.conf << 'EOF'
gogojap soft nofile 65535
gogojap hard nofile 65535
EOF

# 優化 TCP 連接（爬蟲大量短連接場景）
cat > /etc/sysctl.d/99-gogojap.conf << 'EOF'
# TCP 連接優化
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_tw_reuse = 1
net.ipv4.ip_local_port_range = 1024 65535

# 記憶體優化
vm.swappiness = 10
vm.overcommit_memory = 1
EOF
sysctl --system -q

log_success "系統優化完成"

# ==================== 輸出下一步指引 ====================
echo ""
echo "============================================="
echo -e "${GREEN}  VPS 初始化完成！${NC}"
echo "============================================="
echo ""
echo "下一步："
echo ""
echo "  1. 上傳代碼到 ${APP_DIR}："
echo "     scp -r ./deploy/* ${DEPLOY_USER}@<IP>:${APP_DIR}/"
echo ""
echo "  2. 配置環境變量："
echo "     sudo -u ${DEPLOY_USER} cp ${APP_DIR}/.env.template ${APP_DIR}/.env"
echo "     sudo -u ${DEPLOY_USER} nano ${APP_DIR}/.env"
echo ""
echo "  3. 啟動服務："
echo "     sudo -u ${DEPLOY_USER} bash ${APP_DIR}/start.sh"
echo ""
echo "============================================="
