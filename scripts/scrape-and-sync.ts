// ==================== 本地抓取 + 云端同步脚本 ====================
// 用途: 在本机用 Clawdbot 批量抓取，然后同步到云端数据库
// 使用: ts-node scripts/scrape-and-sync.ts

import { getUnifiedScraper } from '../lib/connectors/unified-scraper';
import fs from 'fs/promises';
import path from 'path';

// ==================== 配置 ====================

const CONFIG = {
  // 本地抓取配置
  localScrape: {
    batchSize: 10, // 每批抓取数量
    delayBetweenBatches: 2000, // 批次间延迟 (ms)
  },

  // 云端同步配置
  cloudSync: {
    apiUrl: process.env.CLOUD_API_URL || 'https://gogojap.zeabur.app/api/v1',
    apiKey: process.env.CLOUD_API_KEY,
    batchSize: 50, // 每批上传数量
  },

  // 输出配置
  output: {
    directory: './data/scraped',
    filename: 'docs-clawd-bot.json',
  },
};

// ==================== 主流程 ====================

async function main() {
  console.log('🚀 开始本地抓取 + 云端同步流程\n');

  // 步骤 1: 本地抓取
  console.log('📥 步骤 1: 本地批量抓取');
  const scrapedData = await localScrapeAll();

  // 步骤 2: 保存到本地文件
  console.log('\n💾 步骤 2: 保存到本地文件');
  await saveToFile(scrapedData);

  // 步骤 3: 同步到云端
  console.log('\n☁️ 步骤 3: 同步到云端数据库');
  await syncToCloud(scrapedData);

  console.log('\n✅ 全部完成！');
  printSummary(scrapedData);
}

// ==================== 步骤 1: 本地抓取 ====================

async function localScrapeAll() {
  // 1.1 获取所有页面 URL
  console.log('  → 获取文档索引...');
  const urls = await getDocUrls();
  console.log(`  → 发现 ${urls.length} 个页面`);

  // 1.2 批量抓取
  const scraper = getUnifiedScraper();
  const results: any[] = [];
  const { batchSize, delayBetweenBatches } = CONFIG.localScrape;

  for (let i = 0; i < urls.length; i += batchSize) {
    const batch = urls.slice(i, i + batchSize);
    const batchNumber = Math.floor(i / batchSize) + 1;
    const totalBatches = Math.ceil(urls.length / batchSize);

    console.log(`  → 抓取批次 ${batchNumber}/${totalBatches} (${batch.length} 页面)`);

    const batchResults = await Promise.all(
      batch.map(async (url) => {
        try {
          const result = await scraper.scrape({ url });
          return {
            url,
            success: result.success,
            data: result.data,
            scrapedAt: result.scrapedAt,
          };
        } catch (error) {
          console.error(`    ✗ 失败: ${url}`);
          return {
            url,
            success: false,
            error: error instanceof Error ? error.message : '未知错误',
          };
        }
      })
    );

    results.push(...batchResults);

    // 批次间休息
    if (i + batchSize < urls.length) {
      await new Promise((resolve) => setTimeout(resolve, delayBetweenBatches));
    }
  }

  const successCount = results.filter((r) => r.success).length;
  console.log(`  ✅ 抓取完成: ${successCount}/${results.length} 成功`);

  return results;
}

/**
 * 获取 docs.clawd.bot 的所有页面 URL
 */
async function getDocUrls(): Promise<string[]> {
  try {
    const response = await fetch('https://docs.clawd.bot/llms.txt');
    const text = await response.text();

    // 解析 URL (假设每行一个 URL)
    const urls = text
      .split('\n')
      .filter((line) => line.trim().startsWith('http'))
      .map((line) => line.trim());

    return urls;
  } catch (error) {
    console.error('获取文档索引失败:', error);
    throw error;
  }
}

// ==================== 步骤 2: 保存到文件 ====================

async function saveToFile(data: any[]) {
  const { directory, filename } = CONFIG.output;
  const filepath = path.join(directory, filename);

  // 确保目录存在
  await fs.mkdir(directory, { recursive: true });

  // 保存 JSON 文件
  await fs.writeFile(filepath, JSON.stringify(data, null, 2), 'utf-8');

  const fileSizeKB = (JSON.stringify(data).length / 1024).toFixed(2);
  console.log(`  ✅ 已保存: ${filepath} (${fileSizeKB} KB)`);
}

// ==================== 步骤 3: 同步到云端 ====================

async function syncToCloud(data: any[]) {
  const { apiUrl, apiKey, batchSize } = CONFIG.cloudSync;

  if (!apiKey) {
    console.warn('  ⚠️ 未配置 CLOUD_API_KEY，跳过云端同步');
    return;
  }

  const successData = data.filter((item) => item.success);

  for (let i = 0; i < successData.length; i += batchSize) {
    const batch = successData.slice(i, i + batchSize);
    const batchNumber = Math.floor(i / batchSize) + 1;
    const totalBatches = Math.ceil(successData.length / batchSize);

    console.log(`  → 上传批次 ${batchNumber}/${totalBatches} (${batch.length} 条)`);

    try {
      const response = await fetch(`${apiUrl}/docs/bulk-import`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${apiKey}`,
        },
        body: JSON.stringify({ docs: batch }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }

      console.log(`    ✓ 批次上传成功`);
    } catch (error) {
      console.error(`    ✗ 批次上传失败:`, error);
    }

    // 批次间休息
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  console.log(`  ✅ 云端同步完成`);
}

// ==================== 统计信息 ====================

function printSummary(data: any[]) {
  const successCount = data.filter((r) => r.success).length;
  const failCount = data.length - successCount;
  const totalDataSize = (JSON.stringify(data).length / 1024 / 1024).toFixed(2);

  console.log('\n==================== 统计信息 ====================');
  console.log(`总页面数: ${data.length}`);
  console.log(`抓取成功: ${successCount} (${((successCount / data.length) * 100).toFixed(1)}%)`);
  console.log(`抓取失败: ${failCount}`);
  console.log(`数据大小: ${totalDataSize} MB`);
  console.log(`保存位置: ${CONFIG.output.directory}/${CONFIG.output.filename}`);
  console.log('===============================================\n');

  console.log('💰 成本节省:');
  console.log(`  - 本地抓取: $0 (使用 Clawdbot)`);
  console.log(`  - 如使用 Firecrawl: 约 $${(data.length * 0.01).toFixed(2)}`);
  console.log(`  - 节省: 100%`);
}

// ==================== 执行 ====================

main().catch((error) => {
  console.error('❌ 脚本执行失败:', error);
  process.exit(1);
});
