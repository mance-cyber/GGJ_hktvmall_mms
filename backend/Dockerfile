# =============================================
# HKTVmall AI 營運系統 - 後端 Dockerfile
# 極簡構建 - 完全避免 apt-get 網絡問題
# =============================================

FROM python:3.11-slim

WORKDIR /app

# 設置環境變量
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 創建虛擬環境並安裝依賴
# 所有依賴都使用預編譯的 wheels，不需要 gcc
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install -r requirements.txt

# 創建非 root 用戶
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# 複製代碼
COPY --chown=appuser:appuser . .

# 切換到非 root 用戶
USER appuser

# 暴露端口（Zeabur 會自動注入 PORT 環境變量）
EXPOSE 8000

# 啟動命令 - 使用 exec 形式以支持信號處理
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2"]
