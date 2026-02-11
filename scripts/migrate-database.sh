#!/bin/bash
# ==========================================
# GoGoJap 数据库迁移脚本 (Neon → AWS RDS)
# ==========================================

set -e  # 遇到错误立即退出

echo "================================================"
echo "  GoGoJap 数据库迁移工具"
echo "  Neon PostgreSQL → AWS RDS PostgreSQL"
echo "================================================"
echo

# ==================== 颜色定义 ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ==================== 检查依赖 ====================
check_dependencies() {
    echo "检查必需工具..."

    if ! command -v pg_dump &> /dev/null; then
        echo -e "${RED}错误: pg_dump 未安装${NC}"
        echo "请安装 PostgreSQL 客户端工具"
        exit 1
    fi

    if ! command -v pg_restore &> /dev/null; then
        echo -e "${RED}错误: pg_restore 未安装${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ 依赖检查通过${NC}\n"
}

# ==================== 读取配置 ====================
read_config() {
    echo "请输入数据库连接信息："
    echo

    # Neon 源数据库
    read -p "Neon 数据库 URL: " NEON_URL
    if [ -z "$NEON_URL" ]; then
        echo -e "${RED}错误: Neon URL 不能为空${NC}"
        exit 1
    fi

    # RDS 目标数据库
    read -p "RDS 数据库 URL: " RDS_URL
    if [ -z "$RDS_URL" ]; then
        echo -e "${RED}错误: RDS URL 不能为空${NC}"
        exit 1
    fi

    # 备份文件名
    BACKUP_FILE="gogojap_backup_$(date +%Y%m%d_%H%M%S).dump"
    echo
    echo -e "${YELLOW}备份文件: $BACKUP_FILE${NC}"
    echo
}

# ==================== 测试连接 ====================
test_connections() {
    echo "测试数据库连接..."

    # 测试 Neon
    if psql "$NEON_URL" -c "SELECT 1;" &> /dev/null; then
        echo -e "${GREEN}✓ Neon 连接成功${NC}"
    else
        echo -e "${RED}✗ Neon 连接失败${NC}"
        exit 1
    fi

    # 测试 RDS
    if psql "$RDS_URL" -c "SELECT 1;" &> /dev/null; then
        echo -e "${GREEN}✓ RDS 连接成功${NC}"
    else
        echo -e "${RED}✗ RDS 连接失败${NC}"
        exit 1
    fi

    echo
}

# ==================== 导出数据 ====================
export_database() {
    echo "==================== 第 1 步: 导出 Neon 数据库 ===================="
    echo "这可能需要几分钟，请耐心等待..."
    echo

    pg_dump "$NEON_URL" \
        --format=custom \
        --no-owner \
        --no-acl \
        --verbose \
        --file="$BACKUP_FILE" 2>&1 | grep -v "NOTICE"

    if [ -f "$BACKUP_FILE" ]; then
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        echo -e "${GREEN}✓ 导出成功！${NC}"
        echo -e "  文件: $BACKUP_FILE"
        echo -e "  大小: $BACKUP_SIZE"
        echo
    else
        echo -e "${RED}✗ 导出失败${NC}"
        exit 1
    fi
}

# ==================== 备份 RDS ====================
backup_rds() {
    echo "==================== 第 2 步: 备份当前 RDS (安全起见) ===================="

    RDS_BACKUP_FILE="rds_backup_before_migration_$(date +%Y%m%d_%H%M%S).dump"

    echo "创建 RDS 当前状态备份..."
    pg_dump "$RDS_URL" \
        --format=custom \
        --no-owner \
        --no-acl \
        --verbose \
        --file="$RDS_BACKUP_FILE" 2>&1 | grep -v "NOTICE"

    if [ -f "$RDS_BACKUP_FILE" ]; then
        echo -e "${GREEN}✓ RDS 备份成功${NC}"
        echo -e "  文件: $RDS_BACKUP_FILE"
        echo
    else
        echo -e "${YELLOW}⚠ RDS 备份失败（如果 RDS 是空的则正常）${NC}"
        echo
    fi
}

# ==================== 导入数据 ====================
import_database() {
    echo "==================== 第 3 步: 导入到 RDS ===================="
    echo "这可能需要几分钟，请耐心等待..."
    echo

    # 确认操作
    read -p "确认要导入数据到 RDS？这将覆盖现有数据。(yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo -e "${YELLOW}操作已取消${NC}"
        exit 0
    fi

    echo "开始导入..."
    pg_restore "$RDS_URL" \
        --verbose \
        --clean \
        --if-exists \
        --no-owner \
        --no-acl \
        "$BACKUP_FILE" 2>&1 | grep -v "NOTICE"

    echo -e "${GREEN}✓ 导入完成${NC}"
    echo
}

# ==================== 验证数据 ====================
verify_data() {
    echo "==================== 第 4 步: 验证数据完整性 ===================="
    echo

    echo "源数据库 (Neon) 统计:"
    psql "$NEON_URL" -c "
        SELECT
            schemaname,
            tablename,
            n_live_tup as row_count
        FROM pg_stat_user_tables
        WHERE schemaname = 'public'
        ORDER BY n_live_tup DESC;
    "

    echo
    echo "目标数据库 (RDS) 统计:"
    psql "$RDS_URL" -c "
        SELECT
            schemaname,
            tablename,
            n_live_tup as row_count
        FROM pg_stat_user_tables
        WHERE schemaname = 'public'
        ORDER BY n_live_tup DESC;
    "

    echo
    echo -e "${YELLOW}请手动对比两个数据库的表数量和行数${NC}"
    echo
}

# ==================== 主流程 ====================
main() {
    check_dependencies
    read_config
    test_connections

    export_database
    backup_rds
    import_database
    verify_data

    echo "================================================"
    echo -e "${GREEN}✓ 数据库迁移完成！${NC}"
    echo "================================================"
    echo
    echo "后续步骤:"
    echo "1. 验证数据完整性（表数量、行数）"
    echo "2. 测试应用连接到新 RDS"
    echo "3. 更新应用配置文件中的 DATABASE_URL"
    echo
    echo "备份文件:"
    echo "- Neon 备份: $BACKUP_FILE"
    echo "- RDS 备份: $RDS_BACKUP_FILE (如果存在)"
    echo
    echo -e "${YELLOW}⚠ 请保留备份文件至少 2 周${NC}"
    echo
}

# 执行主流程
main
