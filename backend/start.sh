#!/bin/sh
# =============================================
# GoGoJap Backend - 统一启动脚本
# 支持启动 API Server 或 Celery Worker
# =============================================

set -e

# 根据 SERVICE_TYPE 环境变量决定启动模式
SERVICE_TYPE=${SERVICE_TYPE:-api}

case "$SERVICE_TYPE" in
  api)
    echo "🚀 Starting FastAPI server..."
    exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
    ;;

  worker)
    echo "🔧 Starting Celery worker..."
    exec celery -A app.tasks.celery_app worker --loglevel=info --concurrency=2
    ;;

  beat)
    echo "⏰ Starting Celery beat scheduler..."
    exec celery -A app.tasks.celery_app beat --loglevel=info
    ;;

  *)
    echo "❌ Unknown SERVICE_TYPE: $SERVICE_TYPE"
    echo "Available types: api, worker, beat"
    exit 1
    ;;
esac
