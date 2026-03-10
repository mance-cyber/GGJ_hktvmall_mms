// Spot-check: fetch a 食尚煮意 product page and verify stockLevel
const https = require('https');

const skus = [
  { sku: 'H8360001_S_FK0071', name: '挪威帶皮三文魚柳', db_stock: 1873 },
  { sku: 'H8360001_S_FK0004', name: '西班牙豬梅肉片', db_stock: 1134 },
  { sku: 'H8360001_S_FK0025', name: '急凍蒲燒鰻魚', db_stock: 859 },
];

// We need the actual SKUs from DB first
const { Client } = require('pg');

async function main() {
  const c = new Client({
    connectionString: 'postgresql://neondb_owner:npg_6TXrmNOqePM4@ep-ancient-brook-a1zdi9wo-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'
  });
  await c.connect();

  // Get 3 random 食尚煮意 SKUs with high stock
  const r = await c.query(`
    SELECT cp.sku, cp.name, ps.stock_level
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
    console.log(`\nVerifying: ${row.name.substring(0,40)} (DB stock: ${row.stock_level})`);
    console.log(`  SKU: ${row.sku}`);
    
    // Fetch product page
    const url = `https://www.hktvmall.com/hktv/en/main/search/product/${row.sku}`;
    try {
      const html = await fetch(url).then(r => r.text());
      const matches = html.match(/"stockLevel"\s*:\s*(\d+)/g);
      if (matches) {
        const levels = matches.map(m => parseInt(m.match(/(\d+)/)[1]));
        console.log(`  HKTVmall stockLevel values: ${levels.join(', ')}`);
        console.log(`  DB value: ${row.stock_level} | Live value: ${levels[0]} | Match: ${levels[0] === row.stock_level ? '✅' : '❌ DIFFERENT'}`);
      } else {
        console.log('  ⚠️ Could not find stockLevel in page');
      }
    } catch(e) {
      console.log(`  Error: ${e.message}`);
    }
  }
}

main().catch(e => console.error(e.message));
