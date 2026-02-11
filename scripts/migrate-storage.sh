#!/bin/bash
# ==========================================
# GoGoJap 存储迁移脚本 (R2 → S3)
# ==========================================

set -e

echo "================================================"
echo "  GoGoJap 存储迁移工具"
echo "  Cloudflare R2 → AWS S3"
echo "================================================"
echo

# ==================== 颜色定义 ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ==================== 检查依赖 ====================
check_dependencies() {
    echo "检查必需工具..."

    if ! command -v rclone &> /dev/null; then
        echo -e "${RED}错误: rclone 未安装${NC}"
        echo "安装方法:"
        echo "  Ubuntu/Debian: sudo apt install rclone"
        echo "  macOS: brew install rclone"
        echo "  Windows: 访问 https://rclone.org/downloads/"
        exit 1
    fi

    if ! command -v aws &> /dev/null; then
        echo -e "${YELLOW}警告: AWS CLI 未安装（可选）${NC}"
        echo "安装方法: pip install awscli"
    fi

    echo -e "${GREEN}✓ 依赖检查通过${NC}\n"
}

# ==================== 配置 Rclone ====================
configure_rclone() {
    echo "==================== 配置 Rclone ===================="
    echo
    echo "是否需要配置 Rclone？(如果已配置可跳过)"
    read -p "(yes/no): " CONFIGURE

    if [ "$CONFIGURE" = "yes" ]; then
        echo
        echo -e "${BLUE}配置 Cloudflare R2:${NC}"
        rclone config create r2 s3 \
            provider Cloudflare \
            env_auth false

        echo
        echo -e "${BLUE}配置 AWS S3:${NC}"
        rclone config create s3 s3 \
            provider AWS \
            env_auth false \
            region ap-southeast-1

        echo -e "${GREEN}✓ Rclone 配置完成${NC}\n"
    else
        echo -e "${YELLOW}跳过配置${NC}\n"
    fi
}

# ==================== 读取路径 ====================
read_paths() {
    echo "请输入存储路径信息："
    echo

    read -p "R2 bucket 名称 (例如: gogojap-bucket): " R2_BUCKET
    if [ -z "$R2_BUCKET" ]; then
        echo -e "${RED}错误: R2 bucket 不能为空${NC}"
        exit 1
    fi

    read -p "S3 bucket 名称 (例如: gogojap-media): " S3_BUCKET
    if [ -z "$S3_BUCKET" ]; then
        echo -e "${RED}错误: S3 bucket 不能为空${NC}"
        exit 1
    fi

    echo
}

# ==================== 测试连接 ====================
test_connections() {
    echo "测试存储连接..."

    # 测试 R2
    if rclone lsd r2:$R2_BUCKET &> /dev/null; then
        echo -e "${GREEN}✓ R2 连接成功${NC}"
    else
        echo -e "${RED}✗ R2 连接失败${NC}"
        echo "请检查 Rclone 配置和 R2 访问凭证"
        exit 1
    fi

    # 测试 S3
    if rclone lsd s3:$S3_BUCKET &> /dev/null; then
        echo -e "${GREEN}✓ S3 连接成功${NC}"
    else
        echo -e "${RED}✗ S3 连接失败${NC}"
        echo "请检查 Rclone 配置和 AWS 访问凭证"
        exit 1
    fi

    echo
}

# ==================== 显示统计 ====================
show_statistics() {
    echo "==================== 源存储统计 (R2) ===================="
    rclone size r2:$R2_BUCKET --json | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"文件数量: {data['count']:,}")
print(f\"总大小: {data['bytes'] / 1024 / 1024 / 1024:.2f} GB\")
"
    echo

    echo "==================== 目标存储统计 (S3) ===================="
    rclone size s3:$S3_BUCKET --json | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"文件数量: {data['count']:,}")
print(f\"总大小: {data['bytes'] / 1024 / 1024 / 1024:.2f} GB\")
"
    echo
}

# ==================== 测试运行 ====================
dry_run() {
    echo "==================== 测试运行 (不实际复制) ===================="
    echo "预览将要复制的文件..."
    echo

    rclone sync r2:$R2_BUCKET s3:$S3_BUCKET \
        --dry-run \
        --progress \
        --verbose \
        --stats 5s \
        --max-depth 2

    echo
    read -p "以上是将要复制的文件，确认继续？(yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo -e "${YELLOW}操作已取消${NC}"
        exit 0
    fi
    echo
}

# ==================== 执行同步 ====================
sync_storage() {
    echo "==================== 开始同步 R2 → S3 ===================="
    echo "这可能需要较长时间，请耐心等待..."
    echo

    # 创建日志文件
    LOG_FILE="storage_migration_$(date +%Y%m%d_%H%M%S).log"

    rclone sync r2:$R2_BUCKET s3:$S3_BUCKET \
        --progress \
        --transfers 10 \
        --checkers 20 \
        --stats 10s \
        --log-file "$LOG_FILE" \
        --log-level INFO

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 同步完成${NC}"
        echo -e "  日志文件: $LOG_FILE"
        echo
    else
        echo -e "${RED}✗ 同步失败${NC}"
        echo -e "  查看日志: $LOG_FILE"
        exit 1
    fi
}

# ==================== 验证数据 ====================
verify_data() {
    echo "==================== 验证数据完整性 ===================="
    echo

    echo "检查文件数量和大小..."
    rclone check r2:$R2_BUCKET s3:$S3_BUCKET \
        --one-way \
        --size-only

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 验证通过：所有文件已正确复制${NC}"
    else
        echo -e "${YELLOW}⚠ 验证发现差异，请检查日志${NC}"
    fi

    echo
    echo "最终统计对比:"
    show_statistics
}

# ==================== 配置 S3 公开访问 ====================
configure_s3_public() {
    echo "==================== 配置 S3 公开访问 ===================="
    echo

    if ! command -v aws &> /dev/null; then
        echo -e "${YELLOW}跳过: AWS CLI 未安装${NC}"
        echo "请手动在 AWS Console 配置 S3 bucket policy"
        echo
        return
    fi

    read -p "是否配置 S3 bucket 为公开读取？(yes/no): " PUBLIC
    if [ "$PUBLIC" = "yes" ]; then
        echo "应用 bucket policy..."

        cat > /tmp/bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$S3_BUCKET/*"
    }
  ]
}
EOF

        aws s3api put-bucket-policy \
            --bucket "$S3_BUCKET" \
            --policy file:///tmp/bucket-policy.json

        echo -e "${GREEN}✓ Bucket policy 已应用${NC}"
        rm /tmp/bucket-policy.json
    fi

    echo
}

# ==================== 生成 CloudFront 配置建议 ====================
show_cloudfront_guide() {
    echo "================================================"
    echo "  CloudFront CDN 配置建议"
    echo "================================================"
    echo
    echo "1. 登录 AWS CloudFront Console"
    echo "2. 创建新分发，配置:"
    echo "   - Origin domain: $S3_BUCKET.s3.ap-southeast-1.amazonaws.com"
    echo "   - Viewer protocol: Redirect HTTP to HTTPS"
    echo "   - Cache policy: CachingOptimized"
    echo "   - Price class: Asia/Europe (推荐)"
    echo
    echo "3. 部署完成后，更新应用配置:"
    echo "   - AWS_CLOUDFRONT_DOMAIN=<your-cloudfront-domain>.cloudfront.net"
    echo
}

# ==================== 主流程 ====================
main() {
    check_dependencies
    configure_rclone
    read_paths
    test_connections
    show_statistics
    dry_run

    sync_storage
    verify_data
    configure_s3_public
    show_cloudfront_guide

    echo "================================================"
    echo -e "${GREEN}✓ 存储迁移完成！${NC}"
    echo "================================================"
    echo
    echo "后续步骤:"
    echo "1. 配置 CloudFront CDN"
    echo "2. 更新应用配置中的存储 URL"
    echo "3. 测试文件上传/下载功能"
    echo "4. 保留 R2 数据作为备份（至少 2 周）"
    echo
}

# 执行主流程
main
