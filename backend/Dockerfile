# =============================================
# HKTVmall AI 營運系統 - 後端 Dockerfile
# 多階段構建，優化鏡像大小和安全性
# =============================================

# -------------------- 依賴階段 --------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# 配置 apt 使用多個鏡像源並添加重試機制
RUN echo "Acquire::Retries \"3\";" > /etc/apt/apt.conf.d/80-retries && \
    echo "Acquire::http::Timeout \"30\";" >> /etc/apt/apt.conf.d/80-retries && \
    echo "Acquire::ftp::Timeout \"30\";" >> /etc/apt/apt.conf.d/80-retries

# 安裝構建依賴（移除 postgresql-client，不需要在構建階段）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
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

# 配置 apt 重試機制
RUN echo "Acquire::Retries \"3\";" > /etc/apt/apt.conf.d/80-retries && \
    echo "Acquire::http::Timeout \"30\";" >> /etc/apt/apt.conf.d/80-retries

# 安裝運行時依賴（最小化依賴，postgresql-client 通常不需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
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

# 暴露端口（Zeabur 會自動注入 PORT 環境變量）
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# 啟動命令 - 使用 shell 形式以支持環境變量
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
