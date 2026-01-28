// ==================== Playwright 測試 HKTVmall 抓取 ====================
// 用途: 直接用 Playwright 測試 HKTVmall 商品頁面
// 使用: node scripts/test-playwright-hktv.js

const { chromium } = require('playwright');

// 測試 URL（可以改成任何 HKTVmall 商品頁面）
const TEST_URLS = [
  'https://www.hktvmall.com/hktv/zh',  // HKTVmall 首頁（簡化版）
  'https://example.com',  // 簡單測試頁面
];

async function testHKTV() {
  console.log('🚀 Playwright HKTVmall 抓取測試\n');
  console.log('=' .repeat(60));

  let browser;
  const startTime = Date.now();

  try {
    // 啟動瀏覽器
    console.log('🌐 啟動 Chromium...');
    browser = await chromium.launch({
      headless: true,  // 無頭模式
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-blink-features=AutomationControlled'
      ]
    });

    const context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      viewport: { width: 1920, height: 1080 },
      locale: 'zh-HK',
    });

    const page = await context.newPage();

    // 測試簡單頁面
    console.log('\n📡 測試 1: 簡單頁面 (example.com)');
    console.log('-'.repeat(60));

    await page.goto('https://example.com', {
      waitUntil: 'domcontentloaded',
      timeout: 15000
    });

    const title1 = await page.title();
    console.log(`✅ 成功！標題: ${title1}`);

    // 測試 HKTVmall
    console.log('\n📡 測試 2: HKTVmall 首頁');
    console.log('-'.repeat(60));

    await page.goto('https://www.hktvmall.com/hktv/zh', {
      waitUntil: 'domcontentloaded',  // 更寬鬆的等待條件
      timeout: 30000
    });

    // 等待頁面穩定
    await page.waitForTimeout(3000);

    const title2 = await page.title();
    const url = page.url();

    console.log(`✅ 成功加載！`);
    console.log(`  - 標題: ${title2}`);
    console.log(`  - URL: ${url}`);

    // 嘗試截圖
    console.log('\n📸 保存截圖...');
    await page.screenshot({
      path: 'hktvmall-screenshot.png',
      fullPage: false
    });
    console.log(`✅ 截圖已保存: hktvmall-screenshot.png`);

    // 提取頁面信息
    console.log('\n📊 提取頁面信息...');
    const pageInfo = await page.evaluate(() => {
      return {
        title: document.title,
        url: window.location.href,
        bodyLength: document.body.innerText.length,
        hasProducts: !!document.querySelector('[class*="product"]'),
        mainContent: document.body.innerText.substring(0, 200)
      };
    });

    console.log(`  - 標題: ${pageInfo.title}`);
    console.log(`  - 內容長度: ${pageInfo.bodyLength} 字符`);
    console.log(`  - 是否有商品元素: ${pageInfo.hasProducts ? '是' : '否'}`);
    console.log(`  - 內容片段: ${pageInfo.mainContent}...`);

    const duration = Date.now() - startTime;

    console.log('\n' + '='.repeat(60));
    console.log('✅ 測試完成！');
    console.log('='.repeat(60));
    console.log(`總耗時: ${(duration / 1000).toFixed(1)}秒`);
    console.log('\n💡 結論: Playwright 工作正常！可以抓取 HKTVmall 頁面。');
    console.log('問題在於 Clawdbot 的集成層面。');
    console.log('='.repeat(60));

  } catch (error) {
    const duration = Date.now() - startTime;
    console.log('\n' + '='.repeat(60));
    console.log('❌ 測試失敗！');
    console.log('='.repeat(60));
    console.error(`\n錯誤: ${error.message}`);
    console.log(`耗時: ${(duration / 1000).toFixed(1)}秒`);

    if (error.message.includes('Timeout')) {
      console.log('\n💡 提示: HKTVmall 頁面加載較慢，這是正常的。');
      console.log('在實際應用中可以增加超時時間或優化等待策略。');
    }

    console.log('='.repeat(60));
  } finally {
    if (browser) {
      await browser.close();
    }
  }
}

// 執行測試
testHKTV();
