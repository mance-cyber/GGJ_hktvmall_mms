# =============================================
# GoGoJap - 前端 Dockerfile (Next.js)
# 多階段構建，優化生產環境性能
# =============================================

# -------------------- 依賴階段 --------------------
FROM node:20-alpine AS deps

# 安裝 libc6-compat 以支持某些 npm 包
RUN apk add --no-cache libc6-compat

WORKDIR /app

# 複製依賴文件
COPY package.json package-lock.json* ./

# 安裝依賴
RUN npm ci --only=production && \
    npm cache clean --force

# -------------------- 構建階段 --------------------
FROM node:20-alpine AS builder

WORKDIR /app

# 從依賴階段複製 node_modules
COPY --from=deps /app/node_modules ./node_modules

# 複製所有源代碼
COPY . .

# 設置構建環境變量
ENV NEXT_TELEMETRY_DISABLED 1
ENV NODE_ENV production

# 構建 Next.js 應用
RUN npm run build

# -------------------- 生產階段 --------------------
FROM node:20-alpine AS runner

WORKDIR /app

# 設置為生產環境
ENV NODE_ENV production
ENV NEXT_TELEMETRY_DISABLED 1

# 創建非 root 用戶
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# 複製必要文件
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# 切換到非 root 用戶
USER nextjs

# 暴露端口
EXPOSE 3000

# 設置環境變量
ENV PORT 3000
ENV HOSTNAME "0.0.0.0"

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/', (res) => { process.exit(res.statusCode === 200 ? 0 : 1); });"

# 啟動命令
CMD ["node", "server.js"]
