const { Client } = require('pg');

async function main() {
  const c = new Client({
    connectionString: 'postgresql://neondb_owner:npg_6TXrmNOqePM4@ep-ancient-brook-a1zdi9wo-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'
  });
  await c.connect();

  // Find Foodianna competitor ID
  const comp = await c.query(`SELECT id, name FROM competitors WHERE name ILIKE '%foodianna%'`);
  console.log('Foodianna:', comp.rows);
  if (comp.rows.length === 0) { await c.end(); return; }

  const fid = comp.rows[0].id;

  // Check stock data
  const r = await c.query(`
    SELECT cp.name, cp.sku, ps.price, ps.stock_level, ps.stock_status, ps.scraped_at
    FROM competitor_products cp
    JOIN price_snapshots ps ON cp.id = ps.competitor_product_id
    WHERE cp.competitor_id = $1
    AND ps.scraped_at = (SELECT MAX(ps2.scraped_at) FROM price_snapshots ps2 WHERE ps2.competitor_product_id = cp.id)
    ORDER BY ps.stock_level DESC NULLS LAST
    LIMIT 20
  `, [fid]);

  console.log(`\nFoodianna products: ${r.rows.length}`);
  const hasStock = r.rows.filter(r => r.stock_level !== null).length;
  const noStock = r.rows.filter(r => r.stock_level === null).length;
  console.log(`  With stock data: ${hasStock}`);
  console.log(`  Without stock data (null): ${noStock}`);
  console.log('---');
  for (const row of r.rows) {
    const name = (row.name || '').substring(0, 50).padEnd(50);
    const stock = row.stock_level !== null ? String(row.stock_level).padStart(6) : '  null';
    console.log(`${name} | stock: ${stock} | status: ${row.stock_status || 'n/a'} | ${new Date(row.scraped_at).toISOString().substring(0,16)}`);
  }

  // Total count
  const total = await c.query(`SELECT count(*) FROM competitor_products WHERE competitor_id = $1`, [fid]);
  console.log(`\nTotal Foodianna products in DB: ${total.rows[0].count}`);

  // Spot check: try fetching one Foodianna product page live
  const sample = await c.query(`
    SELECT cp.sku, cp.name FROM competitor_products cp
    WHERE cp.competitor_id = $1 LIMIT 1
  `, [fid]);
  
  if (sample.rows.length > 0) {
    const sku = sample.rows[0].sku;
    const store = sku.split('_S_')[0];
    const url = `https://www.hktvmall.com/hktv/zh/main/search/s/${store}/p/${sku}`;
    console.log(`\nSpot check: ${sample.rows[0].name.substring(0,40)}`);
    console.log(`  URL: ${url}`);
    
    try {
      const resp = await fetch(url, {
        headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'Accept': 'text/html' },
        redirect: 'follow'
      });
      const html = await resp.text();
      const stockMatches = html.match(/"stockLevel"\s*:\s*(\d+)/g);
      if (stockMatches) {
        const levels = stockMatches.map(m => parseInt(m.match(/(\d+)/)[1]));
        console.log(`  Live stockLevel: ${[...new Set(levels)].join(', ')}`);
      } else {
        console.log('  ⚠️ No stockLevel in page HTML');
        // Check what data IS there
        const hasProduct = html.includes('"productName"');
        const hasStore = html.includes(store);
        const pageLen = html.length;
        console.log(`  Page length: ${pageLen}, hasProduct: ${hasProduct}, hasStore: ${hasStore}`);
      }
    } catch(e) {
      console.log(`  Error: ${e.message}`);
    }
  }

  await c.end();
}

main().catch(e => console.error(e.message));
