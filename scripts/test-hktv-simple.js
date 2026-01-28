// ==================== HKTVmall 商品抓取简单测试 (JavaScript 版本) ====================
// 用途: 快速测试抓取 HKTVmall 商品功能（不需要 TypeScript 编译）
// 使用: node scripts/test-hktv-simple.js

const TEST_URL = 'https://www.hktvmall.com/hktv/zh/main/GoGo-Nihon/s/H8935001';

async function testHKTVScrape() {
  console.log('🚀 开始测试 HKTVmall 商品抓取\n');
  console.log('='.repeat(60));

  // 测试统一 API
  const apiUrl = 'http://localhost:3000/api/v1/scrape';

  // 步骤 1: 健康检查
  console.log('🏥 健康检查...');
  try {
    const healthResponse = await fetch(apiUrl);
    const healthData = await healthResponse.json();

    console.log(`✅ 爬虫服务状态:`);
    console.log(`  - 类型: ${healthData.scraper.type}`);
    console.log(`  - 状态: ${healthData.scraper.status}`);
    console.log(`  - 环境: ${healthData.environment}`);

    if (healthData.scraper.status !== 'connected') {
      console.error('\n❌ 爬虫服务未连接！');
      console.error('请检查:');
      console.error('  1. Clawdbot 是否已启动？');
      console.error('  2. 开发服务器是否运行？(npm run dev)');
      process.exit(1);
    }

    console.log('='.repeat(60) + '\n');

  } catch (error) {
    console.error('❌ 无法连接到 API 服务！');
    console.error('请确保开发服务器已启动: npm run dev');
    console.error('错误:', error.message);
    process.exit(1);
  }

  // 步骤 2: 测试抓取商品
  console.log(`🛍️ 测试商品抓取:`);
  console.log(`  URL: ${TEST_URL}\n`);

  const startTime = Date.now();

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'scrape_product',
        params: { url: TEST_URL },
      }),
    });

    const result = await response.json();
    const duration = Date.now() - startTime;

    console.log('='.repeat(60));

    if (result.success) {
      console.log('✅ 抓取成功！\n');

      console.log('📊 基本信息:');
      console.log(`  - 任务 ID: ${result.metadata?.taskId}`);
      console.log(`  - 使用爬虫: ${result.metadata?.scraper}`);
      console.log(`  - 耗时: ${duration}ms (${(duration / 1000).toFixed(1)}秒)`);
      console.log(`  - 抓取时间: ${new Date(result.metadata?.scrapedAt).toLocaleString('zh-HK')}`);

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
          if (result.data[field] !== undefined && result.data[field] !== null) {
            console.log(`  - ${field}: ${JSON.stringify(result.data[field])}`);
          }
        }

        // 显示完整 JSON
        console.log('\n📄 完整 JSON 数据:');
        console.log(JSON.stringify(result.data, null, 2));

      } else {
        console.log('  ⚠️ 未提取到商品数据');
        console.log('  提示: 可能需要调整 CSS 选择器以匹配 HKTVmall 页面结构');
      }

    } else {
      console.log('❌ 抓取失败！\n');
      console.log(`错误信息: ${result.error}`);
      console.log(`耗时: ${duration}ms`);
    }

    console.log('='.repeat(60));

  } catch (error) {
    const duration = Date.now() - startTime;
    console.log('='.repeat(60));
    console.log('❌ 测试失败！\n');
    console.error('错误详情:', error.message);
    console.log(`\n耗时: ${duration}ms`);
    console.log('='.repeat(60));
    process.exit(1);
  }

  // 测试总结
  console.log('\n🎉 测试完成！');
  console.log('\n💡 下一步:');
  console.log('  1. 访问测试页面: http://localhost:3000/scrape/unified-test');
  console.log('  2. 尝试不同的 HKTVmall 商品 URL');
  console.log('  3. 如需调整选择器，编辑: lib/connectors/clawdbot-connector.ts');
  console.log('');
}

// 执行测试
testHKTVScrape().catch(error => {
  console.error('测试失败:', error);
  process.exit(1);
});
