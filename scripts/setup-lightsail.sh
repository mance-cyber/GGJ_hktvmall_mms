#!/bin/bash
# ==========================================
# GoGoJap Lightsail 实例初始化脚本
# 在 Lightsail 实例上运行此脚本
# ==========================================

set -e

echo "================================================"
echo "  GoGoJap Lightsail 实例初始化"
echo "================================================"
echo

# ==================== 颜色定义 ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ==================== 检查 root ====================
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}请不要以 root 用户运行此脚本${NC}"
    echo "使用: ./setup-lightsail.sh"
    exit 1
fi

# ==================== 更新系统 ====================
update_system() {
    echo "==================== 更新系统 ===================="
    sudo apt update
    sudo apt upgrade -y
    echo -e "${GREEN}✓ 系统更新完成${NC}\n"
}

# ==================== 安装 Python 3.11 ====================
install_python() {
    echo "==================== 安装 Python 3.11 ===================="

    sudo apt install -y software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install -y \
        python3.11 \
        python3.11-venv \
        python3.11-dev \
        python3-pip

    # 设置默认 Python
    sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

    python3 --version
    echo -e "${GREEN}✓ Python 3.11 安装完成${NC}\n"
}

# ==================== 安装系统依赖 ====================
install_dependencies() {
    echo "==================== 安装系统依赖 ===================="

    sudo apt install -y \
        git \
        nginx \
        redis-server \
        postgresql-client \
        supervisor \
        build-essential \
        libpq-dev \
        curl \
        wget \
        htop \
        vim

    echo -e "${GREEN}✓ 系统依赖安装完成${NC}\n"
}

# ==================== 配置防火墙 ====================
setup_firewall() {
    echo "==================== 配置防火墙 ===================="

    sudo ufw allow 22/tcp    # SSH
    sudo ufw allow 80/tcp    # HTTP
    sudo ufw allow 443/tcp   # HTTPS
    sudo ufw --force enable

    echo -e "${GREEN}✓ 防火墙配置完成${NC}\n"
}

# ==================== 创建应用目录 ====================
setup_directories() {
    echo "==================== 创建应用目录 ===================="

    sudo mkdir -p /var/www/gogojap
    sudo chown $USER:$USER /var/www/gogojap

    sudo mkdir -p /var/log/gogojap
    sudo chown $USER:$USER /var/log/gogojap

    echo -e "${GREEN}✓ 目录创建完成${NC}\n"
}

# ==================== 克隆代码 ====================
clone_code() {
    echo "==================== 克隆代码 ===================="

    read -p "Git 仓库 URL (或留空稍后手动上传): " REPO_URL

    if [ -n "$REPO_URL" ]; then
        cd /var/www/gogojap
        git clone "$REPO_URL" .
        echo -e "${GREEN}✓ 代码克隆完成${NC}\n"
    else
        echo -e "${YELLOW}⚠ 跳过克隆，请稍后手动上传代码${NC}"
        echo "上传方法:"
        echo "  rsync -avz --exclude='node_modules' --exclude='__pycache__' \\"
        echo "    -e 'ssh -i your-key.pem' \\"
        echo "    ./backend/ ubuntu@YOUR_IP:/var/www/gogojap/"
        echo
    fi
}

# ==================== 设置 Python 虚拟环境 ====================
setup_venv() {
    echo "==================== 设置 Python 虚拟环境 ===================="

    if [ ! -d "/var/www/gogojap/backend" ]; then
        echo -e "${YELLOW}⚠ backend 目录不存在，跳过虚拟环境设置${NC}\n"
        return
    fi

    cd /var/www/gogojap
    python3 -m venv venv
    source venv/bin/activate

    pip install --upgrade pip

    if [ -f "backend/requirements.txt" ]; then
        pip install -r backend/requirements.txt
        pip install gunicorn
        echo -e "${GREEN}✓ Python 依赖安装完成${NC}\n"
    else
        echo -e "${YELLOW}⚠ requirements.txt 未找到${NC}\n"
    fi

    deactivate
}

# ==================== 配置环境变量模板 ====================
create_env_template() {
    echo "==================== 创建环境变量模板 ===================="

    cat > /var/www/gogojap/backend/.env.template << 'EOF'
# ==================== 应用配置 ====================
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=<生成一个强随机密钥>

# ==================== 数据库配置 ====================
DATABASE_URL=postgresql://postgres:<password>@<rds-endpoint>:5432/gogojap

# ==================== Redis 配置 ====================
REDIS_URL=redis://localhost:6379/0

# ==================== AWS S3 配置 ====================
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_S3_BUCKET=gogojap-media
AWS_S3_REGION=ap-southeast-1
AWS_CLOUDFRONT_DOMAIN=<your-cloudfront-domain>.cloudfront.net

# ==================== AI 配置 ====================
ANTHROPIC_API_KEY=<your-claude-key>

# ==================== Firecrawl 配置 ====================
FIRECRAWL_API_KEY=<your-firecrawl-key>

# ==================== CORS 配置 ====================
ALLOWED_ORIGINS=https://your-frontend.pages.dev,https://gogojap.com
EOF

    echo -e "${GREEN}✓ 环境变量模板已创建: /var/www/gogojap/backend/.env.template${NC}"
    echo -e "${YELLOW}⚠ 请复制模板并填写实际值:${NC}"
    echo "  cp /var/www/gogojap/backend/.env.template /var/www/gogojap/backend/.env"
    echo "  nano /var/www/gogojap/backend/.env"
    echo
}

# ==================== 配置 Gunicorn ====================
create_gunicorn_config() {
    echo "==================== 创建 Gunicorn 配置 ===================="

    cat > /var/www/gogojap/backend/gunicorn.conf.py << 'EOF'
import multiprocessing

# ==================== 服务器配置 ====================
bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 10000
max_requests_jitter = 1000
timeout = 120
keepalive = 5

# ==================== 日志配置 ====================
accesslog = "/var/log/gogojap/access.log"
errorlog = "/var/log/gogojap/error.log"
loglevel = "info"

# ==================== 进程命名 ====================
proc_name = "gogojap"
EOF

    echo -e "${GREEN}✓ Gunicorn 配置已创建${NC}\n"
}

# ==================== 配置 Nginx ====================
configure_nginx() {
    echo "==================== 配置 Nginx ===================="

    read -p "Lightsail 静态 IP (或域名): " SERVER_NAME

    sudo tee /etc/nginx/sites-available/gogojap << EOF
upstream gogojap_backend {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name $SERVER_NAME;

    client_max_body_size 100M;

    # ==================== API 路由 ====================
    location /api {
        proxy_pass http://gogojap_backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # ==================== 健康检查 ====================
    location /health {
        proxy_pass http://gogojap_backend;
        access_log off;
    }

    # ==================== 静态文件 ====================
    location /static {
        alias /var/www/gogojap/backend/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

    sudo ln -sf /etc/nginx/sites-available/gogojap /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default

    sudo nginx -t
    sudo systemctl restart nginx

    echo -e "${GREEN}✓ Nginx 配置完成${NC}\n"
}

# ==================== 配置 Supervisor ====================
configure_supervisor() {
    echo "==================== 配置 Supervisor ===================="

    # Gunicorn 服务
    sudo tee /etc/supervisor/conf.d/gogojap.conf << 'EOF'
[program:gogojap]
directory=/var/www/gogojap/backend
command=/var/www/gogojap/venv/bin/gunicorn app.main:app -c gunicorn.conf.py
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gogojap/supervisor.log
environment=PATH="/var/www/gogojap/venv/bin"
EOF

    # Celery Worker
    sudo tee /etc/supervisor/conf.d/gogojap-celery.conf << 'EOF'
[program:gogojap-celery]
directory=/var/www/gogojap/backend
command=/var/www/gogojap/venv/bin/celery -A app.celery_app worker --loglevel=info
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gogojap/celery.log
environment=PATH="/var/www/gogojap/venv/bin"
EOF

    # Celery Beat
    sudo tee /etc/supervisor/conf.d/gogojap-celery-beat.conf << 'EOF'
[program:gogojap-celery-beat]
directory=/var/www/gogojap/backend
command=/var/www/gogojap/venv/bin/celery -A app.celery_app beat --loglevel=info
user=ubuntu
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/gogojap/celery-beat.log
environment=PATH="/var/www/gogojap/venv/bin"
EOF

    sudo supervisorctl reread
    sudo supervisorctl update

    echo -e "${GREEN}✓ Supervisor 配置完成${NC}\n"
}

# ==================== 显示后续步骤 ====================
show_next_steps() {
    echo "================================================"
    echo -e "${GREEN}✓ Lightsail 实例初始化完成！${NC}"
    echo "================================================"
    echo
    echo "后续步骤:"
    echo
    echo "1. 配置环境变量:"
    echo "   nano /var/www/gogojap/backend/.env"
    echo
    echo "2. 运行数据库迁移:"
    echo "   cd /var/www/gogojap/backend"
    echo "   source ../venv/bin/activate"
    echo "   alembic upgrade head"
    echo
    echo "3. 启动应用:"
    echo "   sudo supervisorctl restart gogojap"
    echo "   sudo supervisorctl restart gogojap-celery"
    echo "   sudo supervisorctl restart gogojap-celery-beat"
    echo
    echo "4. 检查状态:"
    echo "   sudo supervisorctl status"
    echo "   curl http://localhost/health"
    echo
    echo "5. 配置 SSL 证书:"
    echo "   sudo apt install certbot python3-certbot-nginx"
    echo "   sudo certbot --nginx -d your-domain.com"
    echo
    echo "6. 查看日志:"
    echo "   tail -f /var/log/gogojap/error.log"
    echo "   tail -f /var/log/nginx/error.log"
    echo
}

# ==================== 主流程 ====================
main() {
    update_system
    install_python
    install_dependencies
    setup_firewall
    setup_directories
    clone_code
    setup_venv
    create_env_template
    create_gunicorn_config
    configure_nginx
    configure_supervisor
    show_next_steps
}

# 执行主流程
main
