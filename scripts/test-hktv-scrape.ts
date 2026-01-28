// ==================== HKTVmall 商品抓取测试脚本 ====================
// 用途: 快速测试抓取 HKTVmall 商品功能
// 使用: ts-node scripts/test-hktv-scrape.ts

import { getUnifiedScraper } from '../lib/connectors/unified-scraper';

// ==================== 测试商品 URL ====================

// 测试用的真实 HKTVmall 商品 URL
const TEST_URLS = [
  // 日本零食类（GoGoJap 相关）
  'https://www.hktvmall.com/hktv/zh/main/GoGo-Nihon/s/H8935001',

  // 备用测试 URL（如果上面的不可用）
  'https://www.hktvmall.com/hktv/zh/main/search?q=japanese+snacks',
];

// ==================== 主测试函数 ====================

async function testHKTVScrape() {
  console.log('🚀 开始测试 HKTVmall 商品抓取\n');
  console.log('=' .repeat(60));

  const scraper = getUnifiedScraper();

  // 显示当前配置
  console.log(`📋 当前配置:`);
  console.log(`  - 爬虫类型: ${scraper.getScraperType()}`);
  console.log(`  - 环境: ${process.env.NODE_ENV || 'development'}`);
  console.log('=' .repeat(60) + '\n');

  // 测试健康检查
  console.log('🏥 健康检查...');
  const isHealthy = await scraper.healthCheck();

  if (!isHealthy) {
    console.error('❌ 爬虫服务不可用！');
    console.error('');
    console.error('请检查:');
    console.error('  1. Clawdbot 是否已启动？ (./start-clawdbot.bat)');
    console.error('  2. WebSocket 端口 18789 是否可访问？');
    console.error('  3. 环境变量是否正确配置？');
    process.exit(1);
  }

  console.log('✅ 爬虫服务正常运行\n');
  console.log('=' .repeat(60) + '\n');

  // 测试抓取第一个 URL
  const testUrl = TEST_URLS[0];
  console.log(`🛍️ 测试商品抓取:`);
  console.log(`  URL: ${testUrl}\n`);

  const startTime = Date.now();

  try {
    const result = await scraper.scrapeHKTVProduct(testUrl);
    const duration = Date.now() - startTime;

    console.log('=' .repeat(60));

    if (result.success) {
      console.log('✅ 抓取成功！\n');

      console.log('📊 基本信息:');
      console.log(`  - 任务 ID: ${result.metadata?.taskId}`);
      console.log(`  - 使用爬虫: ${result.metadata?.scraper}`);
      console.log(`  - 耗时: ${duration}ms (${(duration / 1000).toFixed(1)}秒)`);
      console.log(`  - 抓取时间: ${new Date(result.scrapedAt).toLocaleString('zh-HK')}`);

      console.log('\n📦 商品数据:');
      if (result.data) {
        // 显示关键字段
        const fields = [
          'name',
          'price',
          'originalPrice',
          'discountPercent',
          'stockStatus',
          'brand',
          'rating',
          'reviewCount',
        ];

        for (const field of fields) {
          if (result.data[field] !== undefined) {
            console.log(`  - ${field}: ${JSON.stringify(result.data[field])}`);
          }
        }

        // 显示完整 JSON（缩进格式）
        console.log('\n📄 完整 JSON 数据:');
        console.log(JSON.stringify(result.data, null, 2));

        // 如果有截图
        if (result.screenshot) {
          console.log('\n📸 截图已生成 (Base64 编码)');
          console.log(`  - 大小: ${(result.screenshot.length / 1024).toFixed(2)} KB`);
        }
      } else {
        console.log('  ⚠️ 未提取到商品数据');
      }

    } else {
      console.log('❌ 抓取失败！\n');
      console.log(`错误信息: ${result.error}`);
      console.log(`耗时: ${duration}ms`);
    }

    console.log('=' .repeat(60));

  } catch (error) {
    const duration = Date.now() - startTime;
    console.log('=' .repeat(60));
    console.log('❌ 测试失败！\n');
    console.error('错误详情:');
    console.error(error);
    console.log(`\n耗时: ${duration}ms`);
    console.log('=' .repeat(60));
    process.exit(1);
  }

  // 测试总结
  console.log('\n🎉 测试完成！');
  console.log('\n💡 下一步:');
  console.log('  1. 访问测试页面: http://localhost:3000/scrape/unified-test');
  console.log('  2. 尝试批量抓取: 修改 TEST_URLS 数组添加更多 URL');
  console.log('  3. 集成到你的应用: 使用 getUnifiedScraper()');
  console.log('');
}

// ==================== 批量测试函数 ====================

async function testBatchScrape() {
  console.log('🚀 开始批量抓取测试\n');

  const scraper = getUnifiedScraper();

  console.log(`📦 准备抓取 ${TEST_URLS.length} 个商品...\n`);

  const results = await scraper.scrapeBatch(TEST_URLS);

  const successCount = results.filter(r => r.success).length;
  const failCount = results.length - successCount;

  console.log('=' .repeat(60));
  console.log('📊 批量抓取结果:');
  console.log(`  - 总数: ${results.length}`);
  console.log(`  - 成功: ${successCount} (${((successCount / results.length) * 100).toFixed(1)}%)`);
  console.log(`  - 失败: ${failCount}`);
  console.log('=' .repeat(60));

  // 显示每个结果
  results.forEach((result, index) => {
    const status = result.success ? '✅' : '❌';
    console.log(`\n${status} URL ${index + 1}: ${result.url}`);
    if (result.success && result.data) {
      console.log(`  商品名称: ${result.data.name || 'N/A'}`);
      console.log(`  价格: ${result.data.price || 'N/A'}`);
    } else {
      console.log(`  错误: ${result.error}`);
    }
  });
}

// ==================== 执行测试 ====================

const args = process.argv.slice(2);
const command = args[0];

if (command === 'batch') {
  testBatchScrape().catch(error => {
    console.error('批量测试失败:', error);
    process.exit(1);
  });
} else {
  testHKTVScrape().catch(error => {
    console.error('测试失败:', error);
    process.exit(1);
  });
}
