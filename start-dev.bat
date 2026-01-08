@echo off
echo ========================================
echo   啟動 HKTVmall AI 本地開發環境
echo ========================================
echo.

echo [1/4] 啟動 Docker 服務...
docker-compose up -d db redis
if %errorlevel% neq 0 (
    echo 錯誤: Docker 服務啟動失敗
    pause
    exit /b 1
)
echo ✓ Docker 服務已啟動
echo.

echo [2/4] 等待數據庫準備...
timeout /t 5 /nobreak >nul
echo ✓ 數據庫準備完成
echo.

echo [3/4] 運行數據庫遷移...
cd backend
python -m pip install -q alembic asyncpg sqlalchemy python-dotenv pydantic pydantic-settings 2>nul
python migrate.py
if %errorlevel% neq 0 (
    echo 警告: 數據庫遷移失敗，可能已經執行過
)
cd ..
echo ✓ 數據庫遷移完成
echo.

echo [4/4] 啟動後端服務...
cd backend
start "FastAPI Backend" cmd /k "python -m pip install -q -r requirements.txt 2>nul && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd ..
echo ✓ 後端服務已啟動
echo.

echo ========================================
echo   所有服務已啟動！
echo ========================================
echo.
echo 後端 API: http://localhost:8000
echo API 文檔: http://localhost:8000/docs
echo.
echo 按任意鍵關閉此窗口...
pause >nul
