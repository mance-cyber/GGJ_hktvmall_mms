# 本地抓取 + 云端同步方案指南

> 版本: 1.0
> 更新日期: 2026-01-27
> 用途: 在本机用免费的 Clawdbot 批量抓取，然后同步到 Zeabur 云端数据库

---

## 🎯 方案对比

### 方案对比表

| 维度 | 混合架构（原方案） | 本地抓取+云端同步（新方案） |
|-----|------------------|------------------------|
| **运作方式** | 环境自动切换 | 本地抓取 → 手动同步 |
| **本地环境** | 本机数据库独立 | 本机抓取 → 云端数据库 |
| **生产环境** | Firecrawl 自动抓取 | 直接读取已同步数据 |
| **数据同步** | 不同步 | 手动/自动同步 |
| **成本** | 开发$0，生产按需 | 完全免费（仅抓取） |
| **适用场景** | 实时抓取 | 批量静态数据 |

---

## 📊 两种使用模式

### 模式 1: 混合架构（环境隔离）

```
本地开发:
┌────────────────────────────────────┐
│  本机                              │
│  ┌──────────┐    ┌──────────────┐ │
│  │ Clawdbot │───→│ 本机数据库    │ │
│  └──────────┘    └──────────────┘ │
└────────────────────────────────────┘

生产部署:
┌────────────────────────────────────┐
│  Zeabur                            │
│  ┌──────────┐    ┌──────────────┐ │
│  │Firecrawl │───→│ 云端数据库    │ │
│  └──────────┘    └──────────────┘ │
└────────────────────────────────────┘
```

**特点**:
- ✅ 两个环境完全独立
- ✅ 开发环境免费测试
- ✅ 生产环境实时抓取
- ❌ 生产环境需付费

**适合**:
- 实时抓取场景（如商品价格监控）
- 数据频繁变化
- 需要自动化定时抓取

---

### 模式 2: 本地抓取 + 云端同步（成本优化）

```
步骤 1: 本地批量抓取（免费）
┌────────────────────────────────────┐
│  本机                              │
│  ┌──────────┐    ┌──────────────┐ │
│  │ Clawdbot │───→│ JSON 文件     │ │
│  │ (免费)   │    │ data.json     │ │
│  └──────────┘    └──────────────┘ │
└────────────────────────────────────┘
           ↓
           ↓ 手动/自动上传
           ↓
步骤 2: 同步到云端
┌────────────────────────────────────┐
│  Zeabur                            │
│  ┌──────────────┐                 │
│  │ 云端数据库    │                 │
│  │ (已有数据)   │                 │
│  └──────────────┘                 │
└────────────────────────────────────┘
```

**特点**:
- ✅ 完全免费（本地抓取）
- ✅ 大量数据一次性处理
- ✅ 云端无需抓取服务
- ⚠️ 需手动触发同步

**适合**:
- 批量静态数据（如文档、教程）
- 数据不常变化
- 成本敏感场景

---

## 🚀 实施方案

### 方案 A: 手动批量同步（推荐 ⭐⭐⭐⭐⭐）

#### 步骤 1: 配置环境变量

在本机项目根目录的 `.env.local` 文件添加：

```env
# 本地抓取配置（使用 Clawdbot）
NODE_ENV=development
CLAWDBOT_GATEWAY_URL=ws://127.0.0.1:18789

# 云端同步配置
CLOUD_API_URL=https://gogojap.zeabur.app/api/v1
CLOUD_API_KEY=your-secure-api-key-here
```

#### 步骤 2: 启动本地 Clawdbot

```bash
.\start-clawdbot.bat
```

#### 步骤 3: 运行抓取脚本

```bash
# 安装 ts-node (如未安装)
npm install -g ts-node

# 运行抓取 + 同步脚本
ts-node scripts/scrape-and-sync.ts
```

**脚本会自动**:
1. ✅ 从 `https://docs.clawd.bot/llms.txt` 获取所有页面 URL
2. ✅ 使用本地 Clawdbot 批量抓取（247 页面，约 3-5 分钟）
3. ✅ 保存到本地 JSON 文件 (`data/scraped/docs-clawd-bot.json`)
4. ✅ 批量上传到云端数据库（Zeabur）

#### 步骤 4: 查看结果

```bash
# 查看本地文件
cat data/scraped/docs-clawd-bot.json

# 验证云端数据
curl -H "Authorization: Bearer $CLOUD_API_KEY" \
     https://gogojap.zeabur.app/api/v1/docs/bulk-import
```

---

### 方案 B: 实时同步（高级用法）

如果你希望**在本机抓取的同时自动同步到云端**，可以修改统一抓取器：

```typescript
// lib/connectors/unified-scraper-with-sync.ts

export class UnifiedScraperWithSync extends UnifiedScraper {
  private syncToCloud: boolean;
  private cloudApiUrl: string;
  private cloudApiKey: string;

  constructor(syncToCloud = false) {
    super();
    this.syncToCloud = syncToCloud;
    this.cloudApiUrl = process.env.CLOUD_API_URL || '';
    this.cloudApiKey = process.env.CLOUD_API_KEY || '';
  }

  async scrape(task: UnifiedScrapeTask): Promise<UnifiedScrapeResult> {
    // 本地抓取
    const result = await super.scrape(task);

    // 如果启用云端同步，且抓取成功
    if (this.syncToCloud && result.success) {
      await this.syncResultToCloud(result);
    }

    return result;
  }

  private async syncResultToCloud(result: UnifiedScrapeResult) {
    try {
      await fetch(`${this.cloudApiUrl}/docs/bulk-import`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${this.cloudApiKey}`,
        },
        body: JSON.stringify({
          docs: [
            {
              url: result.url,
              success: result.success,
              data: result.data,
              scrapedAt: result.scrapedAt,
            },
          ],
        }),
      });
      console.log(`☁️ 已同步到云端: ${result.url}`);
    } catch (error) {
      console.error(`❌ 云端同步失败: ${result.url}`, error);
    }
  }
}
```

**使用方式**：
```typescript
import { UnifiedScraperWithSync } from '@/lib/connectors/unified-scraper-with-sync';

// 启用实时同步
const scraper = new UnifiedScraperWithSync(true);

// 抓取时会自动同步到云端
const result = await scraper.scrapeHKTVProduct(url);
```

---

## 💰 成本对比

### 场景: 抓取 247 个文档页面

| 方案 | 成本 | 时间 | 说明 |
|-----|------|------|------|
| **Firecrawl 直接抓取** | $2.47 | 5 分钟 | 247 × $0.01 |
| **本地 Clawdbot** | $0 | 3-5 分钟 | 完全免费 |
| **本地抓取+云端同步** | $0 | 5-8 分钟 | 免费（仅上传流量） |

### 场景: 每月监控 1000 个商品价格

| 方案 | 月成本 | 说明 |
|-----|--------|------|
| **混合架构（生产用 Firecrawl）** | $300 | 1000 × 30 天 × $0.01 |
| **本地抓取+云端同步** | $0 | 本机运行定时任务 |

**结论**:
- ✅ 静态数据（文档）: 用**本地抓取+云端同步**，省 100% 成本
- ✅ 实时数据（价格）: 用**混合架构**，生产环境稳定

---

## 🛠️ Zeabur 云端配置

### 步骤 1: 添加环境变量

在 Zeabur 控制台添加：

```env
# API 密钥（用于验证上传请求）
CLOUD_API_KEY=your-secure-random-key-here
```

### 步骤 2: 数据库 Schema

如果使用 Prisma，添加模型：

```prisma
// prisma/schema.prisma

model ClawdbotDocs {
  id         String   @id @default(cuid())
  url        String   @unique
  title      String?
  content    String?  @db.Text
  html       String?  @db.Text
  markdown   String?  @db.Text
  scrapedAt  DateTime
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt
}
```

运行迁移：
```bash
npx prisma migrate dev --name add_clawdbot_docs
```

---

## 📋 脚本使用说明

### 基本用法

```bash
# 抓取 + 同步到云端
ts-node scripts/scrape-and-sync.ts

# 仅抓取，不同步（开发测试）
SKIP_SYNC=true ts-node scripts/scrape-and-sync.ts
```

### 高级配置

修改 `scripts/scrape-and-sync.ts` 中的配置：

```typescript
const CONFIG = {
  localScrape: {
    batchSize: 10,          // 每批抓取 10 个（可调整）
    delayBetweenBatches: 2000, // 批次间延迟 2 秒
  },
  cloudSync: {
    apiUrl: process.env.CLOUD_API_URL,
    apiKey: process.env.CLOUD_API_KEY,
    batchSize: 50,          // 每批上传 50 个
  },
  output: {
    directory: './data/scraped',
    filename: 'docs-clawd-bot.json',
  },
};
```

---

## 🎯 最佳实践建议

### 何时使用"混合架构"

✅ **实时抓取场景**
- 商品价格监控（每小时更新）
- SEO 排名追踪（每日更新）
- 竞品分析（频繁变化）

✅ **自动化场景**
- 定时任务自动运行
- 无需人工干预
- 需要稳定的云端服务

---

### 何时使用"本地抓取+云端同步"

✅ **批量静态数据**
- 文档站点（docs.clawd.bot）
- 产品目录（一次性导入）
- 历史数据迁移

✅ **成本敏感场景**
- 预算有限
- 大量数据抓取（> 1000 页面）
- 数据不常更新

---

### 混合使用策略（最优）

```
静态数据（文档、教程）:
  → 本地抓取 + 云端同步（免费）

动态数据（价格、库存）:
  → 混合架构（生产用 Firecrawl）

开发测试:
  → 本地 Clawdbot（免费）
```

---

## 🔒 安全注意事项

### 1. API Key 管理

```bash
# ❌ 不要硬编码
CLOUD_API_KEY=abc123

# ✅ 使用环境变量
CLOUD_API_KEY=$(cat .secrets/api-key.txt)

# ✅ 使用密钥管理工具
CLOUD_API_KEY=$(aws secretsmanager get-secret-value --secret-id api-key)
```

### 2. 验证上传来源

在云端 API 添加 IP 白名单：

```typescript
// frontend/src/app/api/v1/docs/bulk-import/route.ts

const ALLOWED_IPS = [
  '127.0.0.1',           // 本地
  'your-office-ip',      // 办公室 IP
];

const clientIp = request.headers.get('x-forwarded-for');
if (!ALLOWED_IPS.includes(clientIp)) {
  return NextResponse.json({ error: '未授权 IP' }, { status: 403 });
}
```

### 3. 限流保护

```typescript
// 添加限流中间件
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 分钟
  max: 100,                  // 最多 100 次请求
});

export { limiter as rateLimitMiddleware };
```

---

## 📊 监控与日志

### 查看同步状态

```bash
# 查看本地日志
tail -f data/scraped/sync.log

# 查看云端日志（Zeabur）
zeabur logs --service gogojap-api
```

### 统计脚本

```bash
# 统计抓取成功率
jq '[.[] | select(.success)] | length' data/scraped/docs-clawd-bot.json

# 统计失败的 URL
jq '[.[] | select(.success == false) | .url]' data/scraped/docs-clawd-bot.json
```

---

## 🎉 总结

| 方案 | 适用场景 | 成本 | 复杂度 |
|-----|---------|------|--------|
| **混合架构** | 实时抓取 | 中 | 低 |
| **本地抓取+云端同步** | 批量静态数据 | 免费 | 中 |
| **混合使用** | 最优策略 | 最低 | 中 |

**推荐策略**:
1. 文档等静态数据 → 本地抓取+云端同步（省 100% 成本）
2. 商品价格等动态数据 → 混合架构（稳定可靠）
3. 开发测试 → 本地 Clawdbot（免费快速）

---

**🚀 立即开始：运行 `ts-node scripts/scrape-and-sync.ts` 体验免费批量抓取！**
