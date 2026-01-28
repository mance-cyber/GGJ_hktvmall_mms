// 测试简单的 URL 抓取
const TEST_URL = 'https://www.hktvmall.com';  // 首页，加载更快

async function testSimple() {
  console.log('🚀 测试简单 URL 抓取: ' + TEST_URL + '\n');

  try {
    const response = await fetch('http://localhost:3000/api/v1/scrape', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'scrape_url',
        params: { url: TEST_URL },
      }),
    });

    const result = await response.json();

    if (result.success) {
      console.log('✅ 抓取成功！');
      console.log(`使用爬虫: ${result.metadata?.scraper}`);
      console.log(`耗时: ${result.metadata?.durationMs}ms`);
      console.log('\n数据:');
      console.log(JSON.stringify(result.data, null, 2).substring(0, 500) + '...');
    } else {
      console.log('❌ 抓取失败:', result.error);
    }
  } catch (error) {
    console.error('❌ 错误:', error.message);
  }
}

testSimple();
