@echo off
REM ==================== 安全配置快速設置腳本（Windows）====================
REM 用途: 自動生成 API Keys 並配置環境變量
REM 使用: scripts\setup-security.bat

setlocal enabledelayedexpansion

echo.
echo 🔒 開始安全配置...
echo.

REM 1. 檢查 Node.js 是否安裝
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
  echo ❌ 未找到 Node.js，請先安裝 Node.js
  exit /b 1
)

REM 2. 生成 API Key（使用 Node.js）
echo 📝 生成 Scraper API Key...
for /f "delims=" %%i in ('node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"') do set SCRAPER_API_KEY=%%i
echo ✅ 已生成: !SCRAPER_API_KEY!
echo.

REM 3. 檢查 .env.local 是否存在
if exist .env.local (
  echo ⚠️  .env.local 已存在
  set /p OVERWRITE="是否覆蓋？(y/N): "
  if /i not "!OVERWRITE!"=="y" (
    echo ❌ 已取消
    exit /b 1
  )
  move .env.local .env.local.backup >nul
  echo 📦 舊配置已備份為 .env.local.backup
)

REM 4. 獲取當前時間
for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value') do set datetime=%%i
set TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2% %datetime:~8,2%:%datetime:~10,2%:%datetime:~12,2%

REM 5. 創建 .env.local
echo 📝 創建 .env.local...
(
echo # ==================== Scraper API 安全配置 ====================
echo # 自動生成時間: %TIMESTAMP%
echo.
echo # 🔒 Scraper API Key（用於保護 /api/v1/scrape/* 端點）
echo SCRAPER_API_KEYS=!SCRAPER_API_KEY!
echo.
echo # 🔧 Clawdbot 配置
echo CLAWDBOT_GATEWAY_URL=ws://127.0.0.1:18789
echo.
echo # 🔧 環境
echo NODE_ENV=development
echo.
echo # 📝 如需使用 Firecrawl（生產環境），請手動添加：
echo # FIRECRAWL_API_KEY=fc-your-key-here
echo # FIRECRAWL_API_URL=https://api.firecrawl.dev/v1
echo # NODE_ENV=production
) > .env.local

echo ✅ .env.local 已創建
echo.

REM 6. 驗證 .gitignore
findstr /c:".env.local" .gitignore >nul 2>nul
if %ERRORLEVEL% neq 0 (
  echo 📝 添加 .env.local 到 .gitignore...
  echo .env.local >> .gitignore
  echo ✅ 已添加
) else (
  echo ✅ .gitignore 已包含 .env.local
)
echo.

REM 7. 顯示配置摘要
echo ==========================================
echo 🎉 安全配置完成！
echo ==========================================
echo.
echo 📋 配置摘要：
echo   - API Key: !SCRAPER_API_KEY:~0,8!***!SCRAPER_API_KEY:~-8!
echo   - 配置文件: .env.local
if exist .env.local.backup echo   - 備份文件: .env.local.backup
echo.
echo 📝 下一步：
echo   1. 查看配置: type .env.local
echo   2. 啟動開發服務器: npm run dev
echo   3. 測試 API:
echo.
echo      curl -X POST http://localhost:3000/api/v1/scrape/clawdbot ^
echo        -H "x-api-key: !SCRAPER_API_KEY!" ^
echo        -H "Content-Type: application/json" ^
echo        -d "{\"action\":\"scrape_product\",\"params\":{\"url\":\"https://hktvmall.com/...\"}}"
echo.
echo 🔒 重要提醒：
echo   - 不要將 .env.local 提交到 Git
echo   - 不要在日誌中輸出完整 API Key
echo   - 定期輪換 API Keys
echo.
echo ==========================================

pause
