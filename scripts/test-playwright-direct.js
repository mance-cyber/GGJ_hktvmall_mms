// ==================== 直接使用 Playwright 测试抓取 ====================
// 用途: 跳过 Clawdbot，直接用 Playwright 测试 HKTVmall 抓取
// 使用: node scripts/test-playwright-direct.js

const { chromium } = require('playwright');

const TEST_URL = 'https://www.hktvmall.com';

async function testDirectScrape() {
  console.log('🚀 开始 Playwright 直接抓取测试\n');
  console.log('=' .repeat(60));
  console.log(`测试 URL: ${TEST_URL}`);
  console.log('=' .repeat(60) + '\n');

  let browser;
  const startTime = Date.now();

  try {
    // 启动浏览器
    console.log('🌐 启动浏览器...');
    browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    const context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    });

    const page = await context.newPage();

    console.log('📡 导航到页面...');
    await page.goto(TEST_URL, {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    console.log('✅ 页面加载成功！');

    // 提取基本信息
    const title = await page.title();
    const url = page.url();

    // 尝试提取一些内容
    const bodyText = await page.evaluate(() => {
      return document.body.innerText.substring(0, 200);
    });

    const duration = Date.now() - startTime;

    console.log('\n' + '=' .repeat(60));
    console.log('✅ 抓取成功！');
    console.log('=' .repeat(60));
    console.log(`\n📊 结果:`);
    console.log(`  - 标题: ${title}`);
    console.log(`  - URL: ${url}`);
    console.log(`  - 耗时: ${(duration / 1000).toFixed(1)}秒`);
    console.log(`\n📄 页面内容片段:`);
    console.log(bodyText);
    console.log('\n' + '=' .repeat(60));

    console.log('\n✅ Playwright 工作正常！');
    console.log('这说明问题可能在 Clawdbot 的集成层面。');

  } catch (error) {
    const duration = Date.now() - startTime;
    console.log('\n' + '=' .repeat(60));
    console.log('❌ 抓取失败！');
    console.log('=' .repeat(60));
    console.error(`\n错误: ${error.message}`);
    console.log(`耗时: ${(duration / 1000).toFixed(1)}秒`);
    console.log('\n' + '=' .repeat(60));
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// 检查 Playwright 是否已安装
const checkPlaywright = () => {
  try {
    require('playwright');
    return true;
  } catch {
    console.error('❌ Playwright 未安装！');
    console.log('\n请先安装:');
    console.log('  npm install playwright');
    console.log('  npx playwright install chromium');
    return false;
  }
};

if (checkPlaywright()) {
  testDirectScrape();
}
