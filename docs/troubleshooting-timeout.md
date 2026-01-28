# Clawdbot 抓取超时问题诊断指南

## 🔴 问题现象
- WebSocket 连接状态: ✅ 已连接
- 端口 18789: ✅ 监听中
- 抓取任务: ❌ 60秒超时

## 🔍 可能原因

### 原因 1: Clawdbot 未完全启动
WebSocket Gateway 启动了，但浏览器池未初始化。

**诊断步骤**:
```bash
# 检查 Clawdbot 进程
tasklist | findstr node

# 查看 Clawdbot 是否在运行
ps aux | grep clawdbot  # Linux/macOS
```

**检查点**:
- 是否看到类似 `node scripts/run-node.mjs` 的进程？
- 进程内存占用是否合理（应该 > 100MB）？

---

### 原因 2: 缺少环境变量或配置

Clawdbot 需要 Anthropic API Key 才能工作。

**检查配置**:
```bash
cd clawdbot
cat .env  # Linux/macOS
type .env  # Windows
```

**必需配置**:
```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

如果缺少，创建 `.env` 文件并添加。

---

### 原因 3: Clawdbot 实际未启动

WebSocket 端口可能被其他服务占用。

**验证**:
```bash
# 停止所有 Node.js 进程
taskkill /F /IM node.exe  # Windows

# 重新启动 Clawdbot
cd clawdbot
pnpm start
```

**预期输出**:
```
✅ Clawdbot Gateway 已启动
🌐 WebSocket 监听: ws://127.0.0.1:18789
🔧 浏览器池大小: 3
```

---

### 原因 4: 我们实现的连接器不兼容

Clawdbot 的实际 API 可能与我们的实现不匹配。

**测试方法**: 切换到 Firecrawl 验证架构

---

## ✅ 推荐解决方案

### 方案 A: 切换到 Firecrawl 测试（最快）

1. **获取 Firecrawl API Key**:
   - 访问 https://firecrawl.dev
   - 注册账号
   - 获取 API Key

2. **配置环境变量**:
   ```bash
   # 在 frontend/.env.local 添加
   NODE_ENV=production
   FIRECRAWL_API_KEY=fc-your-api-key-here
   ```

3. **重启开发服务器**:
   ```bash
   cd frontend
   npm run dev
   ```

4. **重新测试**:
   访问 http://localhost:3000/test-scraper.html

**优势**:
- ✅ 立即可用，无需调试 Clawdbot
- ✅ 验证混合架构是否正常工作
- ✅ 云端服务，稳定可靠

---

### 方案 B: 修复 Clawdbot（适合调试）

#### 步骤 1: 完全重启 Clawdbot

```bash
# 1. 停止所有 Node.js 进程
taskkill /F /IM node.exe

# 2. 检查端口是否释放
netstat -an | findstr 18789
# 应该没有输出

# 3. 进入 clawdbot 目录
cd clawdbot

# 4. 确保环境变量存在
echo ANTHROPIC_API_KEY=sk-ant-api03-xxxxx > .env

# 5. 安装依赖（如果需要）
pnpm install

# 6. 启动
pnpm start
```

#### 步骤 2: 观察启动日志

成功启动应该看到：
```
✅ Clawdbot started successfully
🌐 WebSocket listening on ws://127.0.0.1:18789
🔧 Browser pool initialized (size: 3)
📊 Ready to handle requests
```

如果缺少这些输出，说明启动不完整。

#### 步骤 3: 测试简单任务

```bash
# 使用 wscat 测试 WebSocket
npm install -g wscat
wscat -c ws://127.0.0.1:18789

# 发送测试消息
{"type": "ping"}
# 应该收到 {"type": "pong"}
```

---

### 方案 C: 简化连接器实现

可能 Clawdbot 的实际协议与我们的实现不匹配。

**检查点**:
1. WebSocket 消息格式
2. 任务 ID 生成方式
3. 超时处理逻辑

**调试方法**:
在 `frontend/src/lib/connectors/clawdbot-connector.ts` 添加日志：

```typescript
async scrape(task: ScrapeTask): Promise<ScrapeResult> {
  console.log('📤 发送任务:', task);

  this.ws?.send(message);

  console.log('⏳ 等待响应...');
  // 等待超时或响应
}
```

---

## 🎯 立即可行的操作

### 选项 1: 切换到 Firecrawl（推荐）

**为什么推荐**:
- ✅ 5分钟内可以验证架构是否正常
- ✅ 如果 Firecrawl 能用，说明问题在 Clawdbot
- ✅ 可以先完成测试，再回来调试 Clawdbot

**如何操作**:
1. 获取 Firecrawl API Key
2. 修改 `frontend/.env.local`:
   ```env
   NODE_ENV=production
   FIRECRAWL_API_KEY=fc-xxxxx
   ```
3. 重启开发服务器
4. 刷新测试页面

---

### 选项 2: 检查 Clawdbot 是否真的在运行

**Windows 命令**:
```bash
# 查看所有 Node.js 进程及其命令行
wmic process where "name='node.exe'" get commandline,processid
```

**查找**:
- 是否有 `node scripts/run-node.mjs`？
- PID 是多少？

**如果没有**:
```bash
cd clawdbot
pnpm start
```

---

### 选项 3: 使用浏览器自动化库直接测试

不依赖 Clawdbot，直接用 Playwright 抓取：

```bash
# 安装 Playwright
npm install playwright

# 运行测试脚本
node scripts/test-playwright-direct.js
```

我可以创建这个脚本。

---

## 📊 决策树

```
Clawdbot 抓取超时
    │
    ├─ 想快速验证架构？
    │   └─ 使用 Firecrawl（推荐）
    │
    ├─ 想调试 Clawdbot？
    │   ├─ 检查进程是否运行
    │   ├─ 检查配置文件
    │   └─ 查看启动日志
    │
    └─ 想完全跳过 Clawdbot？
        └─ 直接用 Playwright
```

---

## 🤔 你现在想要？

1. **快速验证** → 切换到 Firecrawl
2. **深入调试** → 重启 Clawdbot 并查看日志
3. **完全替代** → 直接用 Playwright

告诉我你的选择，我会立即协助！
