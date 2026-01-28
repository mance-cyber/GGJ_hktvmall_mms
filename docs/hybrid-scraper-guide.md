# GoGoJap 混合爬虫架构实施指南

> 版本: 2.0
> 更新日期: 2026-01-27
> 作者: GoGoJap 开发团队

---

## 🎯 架构概述

混合架构方案实现了**自动环境切换**：
- **开发环境**: 使用本地 Clawdbot (免费测试、完全自定义)
- **生产环境**: 使用云端 Firecrawl (稳定可靠、自动扩展)

### 核心优势

✅ **开发体验好**: 本地免费测试，无需消耗 API 配额
✅ **生产环境稳定**: 使用成熟的云端服务
✅ **零代码修改**: 系统自动根据环境切换
✅ **成本可控**: 开发免费，生产按需付费

---

## 📂 新增文件清单

```
lib/
├── config/
│   └── scraper.config.ts          # 统一爬虫配置
├── connectors/
│   ├── clawdbot-connector.ts      # Clawdbot 连接器 (已存在)
│   └── unified-scraper.ts         # 统一爬虫接口 (新增)

frontend/src/app/
├── api/v1/scrape/
│   ├── route.ts                   # 统一 API 路由 (新增)
│   └── clawdbot/route.ts          # 保留向后兼容
└── scrape/
    └── unified-test/page.tsx      # 测试页面 (新增)

.env.scraper.example               # 环境变量配置示例
docs/hybrid-scraper-guide.md       # 本文档
```

---

## 🚀 快速开始

### 步骤 1: 配置环境变量

#### 本地开发环境

在项目根目录创建或修改 `.env.local` 文件：

```env
# ==================== 开发环境配置 ====================
NODE_ENV=development

# Clawdbot WebSocket 地址
CLAWDBOT_GATEWAY_URL=ws://127.0.0.1:18789
```

#### Zeabur 生产环境

在 Zeabur 控制台配置环境变量：

```env
# ==================== 生产环境配置 ====================
NODE_ENV=production

# Firecrawl API 配置
FIRECRAWL_API_URL=https://api.firecrawl.dev/v1
FIRECRAWL_API_KEY=fc-your-production-key-here
```

> ⚠️ **重要**: 生产环境必须配置 `FIRECRAWL_API_KEY`，否则系统会抛出错误。

---

### 步骤 2: 启动本地 Clawdbot (仅开发环境需要)

在项目根目录执行：

```bash
# Windows
.\start-clawdbot.bat

# Linux/macOS
./start-clawdbot.sh
```

看到以下输出表示启动成功：

```
✅ Clawdbot Gateway 已启动
🌐 WebSocket 监听: ws://127.0.0.1:18789
```

---

### 步骤 3: 启动 GoGoJap 应用

```bash
npm run dev
```

应用会在 http://localhost:3000 启动。

---

### 步骤 4: 验证配置

访问测试页面：http://localhost:3000/scrape/unified-test

你应该看到：
- **当前爬虫配置**: 显示 "🤖 Clawdbot" (开发环境)
- **连接状态**: "已连接" (绿色圆点)
- **环境**: "development"

---

## 💻 使用方法

### 方法 1: 使用统一 API (推荐)

```typescript
// 自动根据环境选择爬虫
const response = await fetch('/api/v1/scrape', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'scrape_product',
    params: {
      url: 'https://www.hktvmall.com/...'
    }
  })
});

const result = await response.json();
console.log('使用的爬虫:', result.metadata.scraper); // 'clawdbot' 或 'firecrawl'
```

### 方法 2: 直接导入使用

```typescript
import { getUnifiedScraper } from '@/lib/connectors/unified-scraper';

const scraper = getUnifiedScraper();

// 抓取商品
const result = await scraper.scrapeHKTVProduct('https://www.hktvmall.com/...');

// 抓取搜索排名
const rankResult = await scraper.scrapeHKTVSearchRank('日本零食', 'https://...');

// 批量抓取
const batchResults = await scraper.scrapeBatch([url1, url2, url3]);
```

### 方法 3: 便捷方法

```typescript
import { scrapeUrl, scrapeHKTVProduct, scrapeSearchRank } from '@/lib/connectors/unified-scraper';

// 快速抓取任意 URL
const result1 = await scrapeUrl('https://example.com');

// 快速抓取商品
const result2 = await scrapeHKTVProduct('https://www.hktvmall.com/...');

// 快速抓取排名
const result3 = await scrapeSearchRank('关键词', 'https://...');
```

---

## 🔍 支持的操作类型

| Action | 说明 | 参数 |
|--------|------|------|
| `scrape_url` | 抓取任意 URL | `{ url }` |
| `scrape_product` | 抓取 HKTVmall 商品 | `{ url }` |
| `scrape_search_rank` | 抓取搜索排名 | `{ keyword, targetUrl }` |
| `scrape_batch` | 批量抓取 | `{ urls: string[] }` |
| `scrape_custom` | 自定义任务 | `{ task }` |

---

## 🧪 测试验证

### 1. 检查爬虫配置

```bash
# 访问健康检查端点
curl http://localhost:3000/api/v1/scrape
```

**预期响应**：
```json
{
  "success": true,
  "scraper": {
    "type": "clawdbot",
    "status": "connected",
    "endpoint": "ws://127.0.0.1:18789",
    "hasApiKey": false
  },
  "environment": "development"
}
```

### 2. 测试抓取功能

访问测试页面：http://localhost:3000/scrape/unified-test

1. 查看爬虫配置信息
2. 输入测试 URL
3. 点击 "开始抓取"
4. 查看抓取结果

### 3. 测试环境切换

#### 切换到生产模式 (测试 Firecrawl)

临时修改 `.env.local`:

```env
NODE_ENV=production
FIRECRAWL_API_KEY=fc-your-test-key
```

重启开发服务器，访问测试页面，应该看到：
- **当前爬虫配置**: "🔥 Firecrawl"

---

## 🐛 故障排除

### 问题 1: Clawdbot 连接失败

**症状**: 测试页面显示 "未连接"

**解决方案**:
1. 确认 Clawdbot 正在运行:
   ```bash
   # Windows
   tasklist | findstr node

   # Linux/macOS
   ps aux | grep clawdbot
   ```

2. 检查端口 18789 是否被占用:
   ```bash
   netstat -an | findstr 18789
   ```

3. 重启 Clawdbot:
   ```bash
   cd clawdbot
   pnpm start
   ```

---

### 问题 2: Firecrawl API Key 无效

**症状**: 生产环境报错 "API Key 错误"

**解决方案**:
1. 检查环境变量是否正确配置:
   ```bash
   echo $FIRECRAWL_API_KEY  # Linux/macOS
   ```

2. 验证 API Key 有效性:
   ```bash
   curl -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
        https://api.firecrawl.dev/v1/health
   ```

3. 在 Zeabur 控制台重新配置环境变量

---

### 问题 3: 环境变量未生效

**症状**: 明明配置了 `NODE_ENV=production`，但仍使用 Clawdbot

**解决方案**:
1. 重启开发服务器:
   ```bash
   # Ctrl+C 停止
   npm run dev  # 重新启动
   ```

2. 清除 Next.js 缓存:
   ```bash
   rm -rf .next
   npm run dev
   ```

3. 检查环境变量是否正确加载:
   ```typescript
   // 在任意页面添加
   console.log('NODE_ENV:', process.env.NODE_ENV);
   ```

---

## 📊 成本分析

### 开发环境 (Clawdbot)

```
月度抓取量: 无限制
成本: $0 (完全免费)
优势: 快速迭代，完全自定义
```

### 生产环境 (Firecrawl)

```
月度抓取量: 1000 次
成本: ~$10/月

月度抓取量: 5000 次
成本: ~$50/月

月度抓取量: 10000 次
成本: ~$100/月
```

**建议**:
- 日常开发: 使用 Clawdbot (免费)
- 生产部署: 使用 Firecrawl (稳定)
- 当月抓取量 > 5000 时，考虑将 Clawdbot 部署到云端

---

## 🔄 迁移指南

### 从旧版 Clawdbot API 迁移

#### 旧版代码:
```typescript
import { getClawdbotConnector } from '@/lib/connectors/clawdbot-connector';

const connector = getClawdbotConnector();
const result = await connector.scrapeHKTVProduct(url);
```

#### 新版代码:
```typescript
import { getUnifiedScraper } from '@/lib/connectors/unified-scraper';

const scraper = getUnifiedScraper();
const result = await scraper.scrapeHKTVProduct(url);
```

**变化**:
- ✅ API 接口完全兼容
- ✅ 返回结果格式一致
- ✅ 新增 `metadata.scraper` 字段标识使用的爬虫

---

## 📈 下一步优化

### 短期 (1-2 周)
- [x] 实现混合架构
- [x] 创建测试页面
- [ ] 更新所有现有代码使用统一 API
- [ ] 添加监控与日志

### 中期 (1 个月)
- [ ] 评估生产环境抓取量
- [ ] 根据成本决定是否部署 Clawdbot 到云端
- [ ] 实现智能降级 (Firecrawl 失败时回退到 Clawdbot)

### 长期 (3 个月)
- [ ] 构建抓取任务队列
- [ ] 实现分布式抓取
- [ ] 添加数据缓存层

---

## 🤝 技术支持

遇到问题？

1. 查看本文档的故障排除章节
2. 访问测试页面查看配置状态
3. 查看控制台日志:
   ```bash
   # 查看服务器日志
   npm run dev

   # 查看 Clawdbot 日志
   cd clawdbot && pnpm logs
   ```

4. 联系开发团队

---

## 📝 变更日志

### v2.0 (2026-01-27)
- ✨ 实现混合架构 (Clawdbot + Firecrawl)
- ✨ 添加统一配置系统
- ✨ 创建统一 API 接口
- ✨ 添加测试页面
- 📝 完善文档

### v1.0 (2026-01-26)
- ✨ 初始 Clawdbot 集成

---

**🎉 恭喜！你已成功配置混合爬虫架构。现在可以享受本地免费测试 + 生产稳定部署的双重优势。**
