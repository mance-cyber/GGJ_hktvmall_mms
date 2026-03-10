const { Client } = require('pg');

async function main() {
  const c = new Client({
    connectionString: 'postgresql://neondb_owner:npg_6TXrmNOqePM4@ep-ancient-brook-a1zdi9wo-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'
  });
  await c.connect();

  // 食尚煮意 id = 5186b208-34ba-4c10-bb23-6a1747b6dca1
  const SHOKUJO_ID = '5186b208-34ba-4c10-bb23-6a1747b6dca1';

  // Latest stock per product
  const r = await c.query(`
    SELECT cp.name, cp.sku, ps.price, ps.stock_level, ps.stock_status, ps.scraped_at
    FROM competitor_products cp
    JOIN price_snapshots ps ON cp.id = ps.competitor_product_id
    WHERE cp.competitor_id = $1
    AND ps.scraped_at = (
      SELECT MAX(ps2.scraped_at) FROM price_snapshots ps2 
      WHERE ps2.competitor_product_id = cp.id
    )
    ORDER BY ps.stock_level DESC NULLS LAST
  `, [SHOKUJO_ID]);

  console.log(`食尚煮意 products: ${r.rows.length}`);
  console.log('---');
  
  const withStock = r.rows.filter(x => x.stock_level !== null);
  const withoutStock = r.rows.filter(x => x.stock_level === null);
  
  console.log(`With stock_level: ${withStock.length} | Without: ${withoutStock.length}`);
  console.log('\nTop 20 by stock:');
  for (const row of r.rows.slice(0, 20)) {
    const name = (row.name || '').substring(0, 40).padEnd(40);
    console.log(`${name} | stock: ${String(row.stock_level ?? 'NULL').padStart(6)} | status: ${row.stock_status || '-'} | price: $${row.price} | ${row.scraped_at?.toISOString().substring(0,16)}`);
  }

  // Distribution
  const over100 = withStock.filter(x => x.stock_level > 100).length;
  const over1000 = withStock.filter(x => x.stock_level > 1000).length;
  const under100 = withStock.filter(x => x.stock_level <= 100).length;
  console.log(`\n--- Distribution ---`);
  console.log(`>1000: ${over1000}`);
  console.log(`>100:  ${over100}`);
  console.log(`<=100: ${under100}`);

  // Check the raw_data to see if stock came from page or cart
  const sample = await c.query(`
    SELECT cp.name, cp.sku, ps.stock_level, ps.stock_status, ps.raw_data
    FROM competitor_products cp
    JOIN price_snapshots ps ON cp.id = ps.competitor_product_id
    WHERE cp.competitor_id = $1
    AND ps.stock_level IS NOT NULL
    ORDER BY ps.scraped_at DESC
    LIMIT 3
  `, [SHOKUJO_ID]);

  console.log('\n--- Sample raw_data (to check probe method) ---');
  for (const row of sample.rows) {
    const raw = row.raw_data ? JSON.stringify(row.raw_data).substring(0, 300) : 'null';
    console.log(`${(row.name||'').substring(0,30)} | stock: ${row.stock_level} | raw: ${raw}`);
  }

  await c.end();
}

main().catch(e => console.error('Error:', e.message));
