const { Client } = require('pg');

async function main() {
  const c = new Client({
    connectionString: 'postgresql://neondb_owner:npg_6TXrmNOqePM4@ep-ancient-brook-a1zdi9wo-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'
  });
  await c.connect();

  const SHOKUJO_ID = '5186b208-34ba-4c10-bb23-6a1747b6dca1';

  // Get 食尚煮意 products with latest stock
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
  let over100 = 0;
  for (const row of r.rows) {
    const name = (row.name || '').substring(0, 50).padEnd(50);
    const stock = row.stock_level !== null ? String(row.stock_level).padStart(6) : '  null';
    if (row.stock_level > 100) over100++;
    console.log(`${name} | stock: ${stock} | status: ${row.stock_status || 'n/a'} | $${row.price} | ${new Date(row.scraped_at).toISOString().substring(0,16)}`);
  }
  console.log(`\n--- Summary ---`);
  console.log(`Total products: ${r.rows.length}`);
  console.log(`Stock > 100: ${over100}`);
  console.log(`Stock null: ${r.rows.filter(r => r.stock_level === null).length}`);

  // Check stock_level distribution
  const dist = await c.query(`
    SELECT 
      CASE 
        WHEN ps.stock_level IS NULL THEN 'null'
        WHEN ps.stock_level = 0 THEN '0'
        WHEN ps.stock_level <= 10 THEN '1-10'
        WHEN ps.stock_level <= 50 THEN '11-50'
        WHEN ps.stock_level <= 100 THEN '51-100'
        WHEN ps.stock_level <= 500 THEN '101-500'
        WHEN ps.stock_level <= 1000 THEN '501-1000'
        ELSE '1000+'
      END as range,
      COUNT(*) as cnt
    FROM competitor_products cp
    JOIN price_snapshots ps ON cp.id = ps.competitor_product_id
    WHERE cp.competitor_id = $1
    AND ps.scraped_at = (SELECT MAX(ps2.scraped_at) FROM price_snapshots ps2 WHERE ps2.competitor_product_id = cp.id)
    GROUP BY 1
    ORDER BY 1
  `, [SHOKUJO_ID]);
  console.log('\nStock distribution:');
  for (const row of dist.rows) {
    console.log(`  ${row.range}: ${row.cnt}`);
  }

  // Check HOW stock was probed - look at raw_data for hints
  const sample = await c.query(`
    SELECT cp.name, ps.stock_level, ps.raw_data
    FROM competitor_products cp
    JOIN price_snapshots ps ON cp.id = ps.competitor_product_id
    WHERE cp.competitor_id = $1
    AND ps.stock_level IS NOT NULL
    AND ps.scraped_at = (SELECT MAX(ps2.scraped_at) FROM price_snapshots ps2 WHERE ps2.competitor_product_id = cp.id)
    LIMIT 3
  `, [SHOKUJO_ID]);
  console.log('\nSample raw_data (to check probe method):');
  for (const row of sample.rows) {
    const raw = row.raw_data ? JSON.stringify(row.raw_data).substring(0, 200) : 'null';
    console.log(`  ${row.name?.substring(0,30)} | stock: ${row.stock_level} | raw: ${raw}`);
  }

  await c.end();
}

main().catch(e => console.error('Error:', e.message));
