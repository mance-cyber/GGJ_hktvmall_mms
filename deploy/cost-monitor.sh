#!/bin/bash
# =============================================
# GoGoJap 成本監控腳本
# =============================================
# 功能：追蹤資源使用情況，估算運營成本
# =============================================

# ==================== 顏色輸出 ====================
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_metric() { echo -e "${YELLOW}▶${NC} $1"; }

# ==================== 配置 ====================
REPORT_FILE="./cost-reports/cost-report-$(date +%Y%m%d).txt"
mkdir -p ./cost-reports

# ==================== 費用配置（根據實際情況調整）====================
# 單位：USD/月
COST_PER_GB_RAM=5          # 每 GB RAM 成本
COST_PER_CORE=10           # 每 CPU 核心成本
COST_PER_GB_STORAGE=0.10   # 每 GB 存儲成本
COST_PER_GB_BANDWIDTH=0.09 # 每 GB 帶寬成本

# ==================== 收集系統信息 ====================
log_info "收集系統資源使用情況..."

# CPU 核心數
CPU_CORES=$(nproc)

# 總內存（GB）
TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')

# 已用內存（GB）
USED_RAM=$(free -g | awk '/^Mem:/{print $3}')

# 磁盤使用（GB）
DISK_USED=$(df -BG / | awk 'NR==2 {print $3}' | sed 's/G//')

# Docker 卷使用
DOCKER_VOLUMES=$(docker system df -v --format "{{.Size}}" 2>/dev/null | head -1 || echo "N/A")

# ==================== Docker 容器資源 ====================
log_info "收集容器資源使用情況..."

echo "" > /tmp/gogojap_container_stats.txt

# 獲取所有 GoGoJap 容器的資源使用
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep gogojap >> /tmp/gogojap_container_stats.txt || echo "No containers running" >> /tmp/gogojap_container_stats.txt

# ==================== API 調用成本（需要從日誌或 DB 獲取）====================
# Firecrawl API 調用次數（示例，需要實際實現）
FIRECRAWL_CALLS=$(docker exec -it gogojap-backend python -c "
import asyncio
from app.models import ScrapeLog
from sqlalchemy import func
from datetime import datetime, timedelta

# 這裡需要實際的數據庫查詢邏輯
print(0)
" 2>/dev/null || echo "0")

# Anthropic API 調用次數（示例）
ANTHROPIC_CALLS=0

# ==================== 估算成本 ====================
MONTHLY_COMPUTE_COST=$(echo "$CPU_CORES * $COST_PER_CORE + $TOTAL_RAM * $COST_PER_GB_RAM" | bc)
MONTHLY_STORAGE_COST=$(echo "$DISK_USED * $COST_PER_GB_STORAGE" | bc)

# 假設每月 100GB 帶寬
ESTIMATED_BANDWIDTH=100
MONTHLY_BANDWIDTH_COST=$(echo "$ESTIMATED_BANDWIDTH * $COST_PER_GB_BANDWIDTH" | bc)

# API 成本（需要根據實際定價）
FIRECRAWL_COST=$(echo "$FIRECRAWL_CALLS * 0.001" | bc)  # 假設 $0.001/call
ANTHROPIC_COST=$(echo "$ANTHROPIC_CALLS * 0.003" | bc)  # 假設 $0.003/call

TOTAL_MONTHLY_COST=$(echo "$MONTHLY_COMPUTE_COST + $MONTHLY_STORAGE_COST + $MONTHLY_BANDWIDTH_COST + $FIRECRAWL_COST + $ANTHROPIC_COST" | bc)

# ==================== 生成報告 ====================
cat > ${REPORT_FILE} << EOF
=============================================
GoGoJap 系統成本報告
生成時間: $(date '+%Y-%m-%d %H:%M:%S')
=============================================

==================== 系統資源 ====================
CPU 核心數: ${CPU_CORES}
總內存: ${TOTAL_RAM} GB
已用內存: ${USED_RAM} GB ($(echo "scale=1; $USED_RAM * 100 / $TOTAL_RAM" | bc)%)
磁盤使用: ${DISK_USED} GB
Docker 卷: ${DOCKER_VOLUMES}

==================== 容器資源使用 ====================
$(cat /tmp/gogojap_container_stats.txt)

==================== 月度成本估算 ====================
計算資源 (${CPU_CORES} cores + ${TOTAL_RAM} GB RAM): \$${MONTHLY_COMPUTE_COST}
存儲成本 (${DISK_USED} GB): \$${MONTHLY_STORAGE_COST}
帶寬成本 (${ESTIMATED_BANDWIDTH} GB): \$${MONTHLY_BANDWIDTH_COST}
Firecrawl API: \$${FIRECRAWL_COST}
Anthropic API: \$${ANTHROPIC_COST}
-------------------------------------------
總計（估算）: \$${TOTAL_MONTHLY_COST}/月

==================== 優化建議 ====================
EOF

# 添加優化建議
if (( $(echo "$USED_RAM * 100 / $TOTAL_RAM < 50" | bc -l) )); then
    echo "✓ 內存使用率低於 50%，可考慮縮減 RAM 配置" >> ${REPORT_FILE}
fi

if (( $(echo "$TOTAL_MONTHLY_COST > 100" | bc -l) )); then
    echo "⚠ 月度成本超過 \$100，建議檢討資源配置" >> ${REPORT_FILE}
    echo "  - 考慮使用預留實例節省 30-60%" >> ${REPORT_FILE}
    echo "  - 檢查 API 調用是否有優化空間" >> ${REPORT_FILE}
fi

echo "" >> ${REPORT_FILE}
echo "詳細監控數據請訪問 Grafana: http://localhost:3001" >> ${REPORT_FILE}
echo "==============================================" >> ${REPORT_FILE}

# ==================== 顯示報告 ====================
cat ${REPORT_FILE}

# ==================== 清理 ====================
rm -f /tmp/gogojap_container_stats.txt

log_success "成本報告已保存到: ${REPORT_FILE}"
