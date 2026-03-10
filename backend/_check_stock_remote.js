const { Client } = require('pg');

async function main() {
  const c = new Client({
    connectionString: 'postgresql://neondb_owner:npg_6TXrmNOqePM4@ep-ancient-brook-a1zdi9wo-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'
  });
  await c.connect();

  // Check schema first
  const cols = await c.query(`
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'competitor_products' ORDER BY ordinal_position
  `);
  console.log('competitor_products columns:', cols.rows.map(r => r.column_name).join(', '));

  const psCols = await c.query(`
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'price_snapshots' ORDER BY ordinal_position
  `);
  console.log('price_snapshots columns:', psCols.rows.map(r => r.column_name).join(', '));

  // Check if there's a merchants/competitors table
  const tables = await c.query(`SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name`);
  console.log('All tables:', tables.rows.map(r => r.table_name).join(', '));

  // Find 食尚煮 - might be in a separate merchants table
  for (const t of tables.rows) {
    try {
      const r = await c.query(`SELECT * FROM ${t.table_name} WHERE CAST(${t.table_name} AS TEXT) LIKE '%食尚煮%' LIMIT 1`);
    } catch(e) {}
  }

  // Try querying with merchant join
  try {
    const r = await c.query(`
      SELECT cp.*, ps.price, ps.stock_level, ps.scraped_at
      FROM competitor_products cp
      JOIN price_snapshots ps ON cp.id = ps.competitor_product_id
      WHERE ps.stock_level IS NOT NULL
      ORDER BY ps.stock_level DESC
      LIMIT 5
    `);
    console.log('\nSample products with stock:');
    for (const row of r.rows) {
      console.log(JSON.stringify(row));
    }
  } catch(e) {
    console.log('Query error:', e.message);
  }

  // Find 食尚煮 by searching competitor_products
  try {
    const r = await c.query(`SELECT DISTINCT * FROM competitor_products WHERE name LIKE '%食尚煮%' OR sku LIKE '%食尚煮%' LIMIT 3`);
    console.log('\nDirect search 食尚煮:', r.rows.length, 'results');
    if (r.rows.length > 0) console.log(JSON.stringify(r.rows[0]));
  } catch(e) {}

  // Check if there's a merchant_id or competitor_id column
  try {
    const merch = await c.query(`SELECT DISTINCT competitor_id FROM competitor_products LIMIT 10`);
    console.log('\nDistinct competitor_ids:', merch.rows.map(r => r.competitor_id));
    
    // Check competitors table
    const comps = await c.query(`SELECT * FROM competitors LIMIT 10`);
    console.log('\nCompetitors:');
    for (const row of comps.rows) {
      console.log(`  id=${row.id} name=${row.name} merchant=${row.merchant_name || row.shop_name || ''}`);
    }
  } catch(e) {
    console.log('Competitor lookup error:', e.message);
  }

  await c.end();
}

main().catch(e => console.error('Error:', e.message));
