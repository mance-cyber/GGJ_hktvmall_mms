const { Client } = require('pg');

async function main() {
  const c = new Client({
    connectionString: 'postgresql://neondb_owner:npg_6TXrmNOqePM4@ep-ancient-brook-a1zdi9wo-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'
  });
  await c.connect();

  const r = await c.query(`
    SELECT cp.sku, cp.name, ps.stock_level, ps.scraped_at
    FROM competitor_products cp
    JOIN price_snapshots ps ON cp.id = ps.competitor_product_id
    WHERE cp.competitor_id = '5186b208-34ba-4c10-bb23-6a1747b6dca1'
    AND ps.stock_level > 100
    AND ps.scraped_at = (SELECT MAX(ps2.scraped_at) FROM price_snapshots ps2 WHERE ps2.competitor_product_id = cp.id)
    ORDER BY RANDOM()
    LIMIT 3
  `);
  await c.end();

  for (const row of r.rows) {
    const store = row.sku.split('_S_')[0];
    const url = `https://www.hktvmall.com/hktv/zh/main/search/s/${store}/p/${row.sku}`;
    console.log(`\n${row.name.substring(0,45)}`);
    console.log(`  SKU: ${row.sku}`);
    console.log(`  DB stock: ${row.stock_level} (scraped: ${row.scraped_at})`);
    console.log(`  URL: ${url}`);
    
    try {
      const resp = await fetch(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
          'Accept': 'text/html',
          'Accept-Language': 'zh-TW,zh;q=0.9'
        },
        redirect: 'follow'
      });
      const html = await resp.text();
      
      const stockMatches = html.match(/"stockLevel"\s*:\s*(\d+)/g);
      if (stockMatches) {
        const levels = stockMatches.map(m => parseInt(m.match(/(\d+)/)[1]));
        const unique = [...new Set(levels)];
        console.log(`  Live stockLevel: ${unique.join(', ')}`);
        console.log(`  ${unique[0] === row.stock_level ? '✅ MATCH' : `❌ MISMATCH (DB: ${row.stock_level}, Live: ${unique[0]})`}`);
      } else {
        // Check if page loaded at all
        const hasTitle = html.includes('<title>');
        const hasProduct = html.includes('productName');
        console.log(`  ⚠️ No stockLevel found (hasTitle: ${hasTitle}, hasProduct: ${hasProduct})`);
        // Check for out of stock indicator
        if (html.includes('OUT_OF_STOCK') || html.includes('outOfStock')) {
          console.log('  📛 Product appears OUT OF STOCK');
        }
      }
    } catch(e) {
      console.log(`  Error: ${e.message}`);
    }
  }
}

main().catch(e => console.error(e.message));
