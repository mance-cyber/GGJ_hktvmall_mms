# =============================================
# HKTVmall AI 營運系統 - 後端 Dockerfile
# 多階段構建，優化鏡像大小和安全性
# =============================================

# -------------------- 依賴階段 --------------------
FROM python:3.11-slim as builder

WORKDIR /app

# 安裝構建依賴
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 安裝 Python 依賴到虛擬環境
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -------------------- 生產階段 --------------------
FROM python:3.11-slim

WORKDIR /app

# 安裝運行時依賴
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 從構建階段複製虛擬環境
COPY --from=builder /opt/venv /opt/venv

# 設置環境變量
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 創建非 root 用戶
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# 複製代碼
COPY --chown=appuser:appuser . .

# 切換到非 root 用戶
USER appuser

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 暴露端口
EXPOSE 8000

# 啟動命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
