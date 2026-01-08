-- GogoJap SKU Import SQL
-- Generated: 2026-01-07T20:00:30.456860
-- Total: 600 records

BEGIN;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a64a1076-0f4d-4f3b-8748-452fd7369887',
    'GGJ-AIR-FSH-0001',
    '本鮪腩(不連赤身)',
    '本鮪腩(不連赤身)',
    'No.1 Otoro',
    'Fresh Bluefin Tuna No.1 Belly (4kg~6kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449498',
    '2026-01-07T12:00:30.449683'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a71fa150-fce9-4486-af01-4a62a8024475',
    'GGJ-AIR-FSH-0002',
    '本鮪腩 (連赤身)',
    '本鮪腩 (連赤身)',
    'No.1 Otoro',
    'Fresh Bluefin Tuna No.1 Belly (5kg~8kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449722',
    '2026-01-07T12:00:30.449724'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '6c09fa06-3e9f-4789-b026-a1334cb362fb',
    'GGJ-AIR-FSH-0003',
    '本鮪中腩',
    '本鮪中腩',
    'CHU-toro',
    'Fresh Bluefin Tuna No.2 belly (4kg~7kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449741',
    '2026-01-07T12:00:30.449742'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '07083a8f-d516-454a-a022-526eb97dde10',
    'GGJ-AIR-FSH-0004',
    '本鮪赤身',
    '本鮪赤身',
    'Akami',
    'Fresh Bluefin Tuna Akami (1kg~5KG)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449754',
    '2026-01-07T12:00:30.449756'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '75b906ff-d62b-4250-be2f-0cebc582102f',
    'GGJ-AIR-FSH-0005',
    '天然劍魚',
    '天然劍魚',
    'Kajiki Maguro',
    'Fresh Wild Swordfish No.1 Belly (3-4kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449766',
    '2026-01-07T12:00:30.449768'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e8a9f4f3-b961-4722-9e17-3da8bd74268e',
    'GGJ-AIR-FSH-0006',
    '銀鱈魚',
    '銀鱈魚',
    'Gindara',
    'Fresh Wild Japanese sablefish (1.7-2.5kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449779',
    '2026-01-07T12:00:30.449780'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'ca18455d-f956-4118-94bc-d2f8d1ac006b',
    'GGJ-AIR-FSH-0007',
    '鰆魚',
    '鰆魚',
    'Sawara',
    'Fresh Wild Japanese Spanish Mackerel (3-4kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449792',
    '2026-01-07T12:00:30.449794'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3b433357-8d3f-404c-8499-101e83e5551f',
    'GGJ-AIR-FSH-0008',
    '油甘魚',
    '油甘魚',
    'Hamachi',
    'Fresh Aquaculture Yellowtail (4-6kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449804',
    '2026-01-07T12:00:30.449806'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '2ab77c64-1e2d-4c3d-b6ba-53874c44e130',
    'GGJ-AIR-FSH-0009',
    '油甘魚片半身',
    '油甘魚片半身',
    'Hamachi 1/2',
    'Fresh Aquaculture Yellowtail Half (2-3kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449815',
    '2026-01-07T12:00:30.449817'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '58671ac7-74d3-430f-bb29-51fdbacfb710',
    'GGJ-AIR-FSH-0010',
    '鱆紅魚/間八',
    '鱆紅魚/間八',
    'Kanpachi',
    'Fresh Pirplish Amberjack (2.8-5kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449826',
    '2026-01-07T12:00:30.449828'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c6a74ecb-f5cf-4d7d-8404-422a2497ec6b',
    'GGJ-AIR-FSH-0011',
    '鱆紅魚/間八 半身',
    '鱆紅魚/間八 半身',
    'Kanpachi 1/2',
    'Fresh Pirplish Amberjack half (1.5-2.5kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449837',
    '2026-01-07T12:00:30.449838'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'ed8aa0ee-6bf7-45d9-a0ab-3cb991973917',
    'GGJ-AIR-FSH-0012',
    '鰤魚腩 1/4',
    '鰤魚腩 1/4',
    'Buri (HARA )',
    'Fresh Aquaculture amberjack 1/4 (2-4kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449847',
    '2026-01-07T12:00:30.449849'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'ec6ad3dd-c29b-4d65-aba5-2c6e742a644f',
    'GGJ-AIR-FSH-0013',
    '平政',
    '平政',
    'Hiramasa',
    'Fresh yellowtail amberjack (4.5-7kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449858',
    '2026-01-07T12:00:30.449859'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '298d2ab3-f56c-4784-afdc-9627acbf2368',
    'GGJ-AIR-FSH-0014',
    '平政(半身)',
    '平政(半身)',
    'Hiramasa (Half)',
    'Fresh yellowtail amberjack Half (3-4kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449868',
    '2026-01-07T12:00:30.449870'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9080cd05-dcf9-4a42-817a-cb603b549c07',
    'GGJ-AIR-FSH-0015',
    '鰹',
    '鰹',
    'Katsuo',
    'Fresh Wild bonito (4-5kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449879',
    '2026-01-07T12:00:30.449880'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5940f145-d510-47c8-b3e7-d484d24bc40d',
    'GGJ-AIR-FSH-0016',
    '鰹半身',
    '鰹半身',
    'Katsuo (half)',
    'Fresh Wild Bonito half (2-3kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449889',
    '2026-01-07T12:00:30.449890'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '685f3fe9-8ba0-401e-948a-9649839f42ff',
    'GGJ-AIR-FSH-0017',
    '鰹1/4腹',
    '鰹1/4腹',
    'Katsuo (1/4)',
    'Fresh Wild Bonito 1/4 (1.2-1.8kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449903',
    '2026-01-07T12:00:30.449905'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '0fa24d5a-924a-44dd-b886-4737aed8f9fe',
    'GGJ-AIR-FSH-0018',
    '大池魚',
    '大池魚',
    'Shimaaji',
    'Fresh White trevally (1.0kg~2kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449914',
    '2026-01-07T12:00:30.449916'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f1f1f6d9-6c8f-4dc9-89f7-d5712b91c5c0',
    'GGJ-AIR-FSH-0019',
    '櫻鱒',
    '櫻鱒',
    'Sakura masu',
    'Fresh Wild Masu salmon (3kg~4kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449926',
    '2026-01-07T12:00:30.449927'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '748571b7-fc75-4ddd-aa23-948da2ee778d',
    'GGJ-AIR-FSH-0020',
    '沙甸魚',
    '沙甸魚',
    'IWASHI',
    'Fresh Wild Japanese Sardine (80g~120g)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449936',
    '2026-01-07T12:00:30.449937'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'efec32cf-716d-43ec-a7d3-51ff8f6830db',
    'GGJ-AIR-FSH-0021',
    '秋刀魚',
    '秋刀魚',
    'Sanma',
    'Fresh Wild Pacific Saury (80g-140g)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'AUTUMN',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449946',
    '2026-01-07T12:00:30.449948'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'ef38ca58-fe1c-4840-8c07-ae8727eaa5a9',
    'GGJ-AIR-FSH-0022',
    '池魚',
    '池魚',
    'Aji',
    'Fresh Wild jack mackerel (160g~300g)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449956',
    '2026-01-07T12:00:30.449958'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e97e5248-b5d2-44a1-8a5c-47e5e55144cb',
    'GGJ-AIR-FSH-0023',
    '釣池魚',
    '釣池魚',
    'Tsuriaji',
    'Fresh Wild jack mackerel (160g~300g)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449967',
    '2026-01-07T12:00:30.449968'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1ab57092-f8f5-49da-a81f-8dc077e97112',
    'GGJ-AIR-FSH-0024',
    '伊佐木',
    '伊佐木',
    'Isaki',
    'Fresh Wild Chicken grunt (400G-1Kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449976',
    '2026-01-07T12:00:30.449978'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '81a50612-4c2a-44b6-bab6-b9e9a224ebbd',
    'GGJ-AIR-FSH-0025',
    '魴鮄魚',
    '魴鮄魚',
    'Houbou',
    'Fresh Wild Bluefin searobin (0.4kg~1kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449987',
    '2026-01-07T12:00:30.449988'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b745af37-f678-4e7c-aac7-955583b98d99',
    'GGJ-AIR-FSH-0026',
    '飛魚',
    '飛魚',
    'Tobiuo',
    'Fresh Wild flyingfish (0.3kg~0.8kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.449997',
    '2026-01-07T12:00:30.449999'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e80d6129-85a1-4b19-aaff-3ef1e5bdbd59',
    'GGJ-AIR-FSH-0027',
    '赤鯥魚',
    '赤鯥魚',
    'Akamutsu',
    'Fresh Blackthroat Seaperch (400～800g)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450009',
    '2026-01-07T12:00:30.450010'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3483c251-198a-4335-a673-b6133d07c4a7',
    'GGJ-AIR-FSH-0028',
    '黑鯥魚',
    '黑鯥魚',
    'Kuromutsu',
    'Fresh Gnomefish (1kg~1.8kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450019',
    '2026-01-07T12:00:30.450021'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '59640796-65db-4450-9486-c3f2b5e22205',
    'GGJ-AIR-FSH-0029',
    '鱸魚',
    '鱸魚',
    'Suzuki',
    'Fresh Wild Japanese Sea Bass (1.5kg~3kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450029',
    '2026-01-07T12:00:30.450031'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'cd6923fc-9a57-4ee2-87b8-8d95db4e42c5',
    'GGJ-AIR-FSH-0030',
    '剝皮魚',
    '剝皮魚',
    'KAWAHAGI',
    'Fresh Wild Leatherfish (250-500g)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'WINTER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450039',
    '2026-01-07T12:00:30.450041'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd3f6e5dc-0f23-4e64-a270-af8f17ea9d28',
    'GGJ-AIR-FSH-0031',
    '馬面剝',
    '馬面剝',
    'UMAZURAHAGI',
    'Fresh Wild Black scraper (250-400g)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'WINTER-SPRING',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450050',
    '2026-01-07T12:00:30.450051'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '25a02ef7-7fd7-4cd5-bebe-1bc53171eddb',
    'GGJ-AIR-FSH-0032',
    '鯛魚',
    '鯛魚',
    'Tai',
    'Fresh Red Sea Bream (2kg~3kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450060',
    '2026-01-07T12:00:30.450061'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '734fee38-8442-4e58-b872-6020a5661dfd',
    'GGJ-AIR-FSH-0033',
    '金目鯛',
    '金目鯛',
    'Kinmedai',
    'Fresh Wild Splendid alfonsino (1.0kg~2.5kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450070',
    '2026-01-07T12:00:30.450071'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c7447704-0cbf-4bc9-906e-6804a2fd5b74',
    'GGJ-AIR-FSH-0034',
    '地金目鯛',
    '地金目鯛',
    'Ji-Kinmedai',
    'Fresh Wild Splendid alfonsino (1.0kg~1.8kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450080',
    '2026-01-07T12:00:30.450082'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '139ca631-d7aa-43b5-8ecb-4b229c1b924c',
    'GGJ-AIR-FSH-0035',
    '赤甘鯛',
    '赤甘鯛',
    'Akaamadai',
    'Fresh Wild Japanese Barnquillo (800g-1.3kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450091',
    '2026-01-07T12:00:30.450093'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '0888a956-2bf5-42de-9fba-d68dc338a52a',
    'GGJ-AIR-FSH-0036',
    '的鯛',
    '的鯛',
    'Matoudai',
    'Fresh Wild JOHN Dory (1kg~1.5kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450101',
    '2026-01-07T12:00:30.450103'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7307c215-939a-4cf4-914e-2bf9e92571a0',
    'GGJ-AIR-FSH-0037',
    '石垣鯛',
    '石垣鯛',
    'Ishigakidai',
    'Fresh Wild Spotted Parrotfish (1kg~1.5kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450113',
    '2026-01-07T12:00:30.450115'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b0134a8b-9881-467e-a4d8-6b7b9119d957',
    'GGJ-AIR-FSH-0038',
    '石鯛',
    '石鯛',
    'Ishidai',
    'Japanese Fresh Rock Bream (1kg~1.5kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450123',
    '2026-01-07T12:00:30.450125'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c52fcb6b-df15-412d-8a76-ff4bce45ac48',
    'GGJ-AIR-FSH-0039',
    '疣鯛',
    '疣鯛',
    'Ebodai',
    'Fresh Pacific rudderfish (180g~300g)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'SPRING-AUTUMN',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450134',
    '2026-01-07T12:00:30.450135'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'aac26bcd-033a-47d6-8136-fb9459ced694',
    'GGJ-AIR-FSH-0040',
    '尾長鯛',
    '尾長鯛',
    'Onagadai',
    'Fresh Etelis (700g~1.8kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'AUTUMN-SPRING',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450144',
    '2026-01-07T12:00:30.450145'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a203d85f-8d9b-488c-ab88-bcda59ae0c05',
    'GGJ-AIR-FSH-0041',
    '喜之次',
    '喜之次',
    'Kinki',
    'Fresh Wild Idiot (300～800g)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450154',
    '2026-01-07T12:00:30.450156'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'ade21c7f-6c75-4c5d-aa47-49245b094a28',
    'GGJ-AIR-FSH-0042',
    '鮫鰈',
    '鮫鰈',
    'Samegarei',
    'Fresh Wild Roughscale Sole (2kg~4kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450165',
    '2026-01-07T12:00:30.450166'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '48bef9c5-fef1-4781-9cff-c4923bad97b6',
    'GGJ-AIR-FSH-0043',
    '泳鮃目魚',
    '泳鮃目魚',
    'Live Hirame',
    'Live Bastard Halibut (1.2～1.6kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450175',
    '2026-01-07T12:00:30.450177'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1c0d27e0-26c7-4583-840d-8d272748411a',
    'GGJ-AIR-FSH-0044',
    '鮃目魚 (活殺)',
    '鮃目魚 (活殺)',
    'Hirame (Ike jime)',
    'Fresh Wild Bastard Halibut (1.2～1.6kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450187',
    '2026-01-07T12:00:30.450189'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a8ba33e7-b95b-464a-a0fc-496894d4817c',
    'GGJ-AIR-FSH-0045',
    '金線鯛/紅杉魚',
    '金線鯛/紅杉魚',
    'Itoyori',
    'Fresh Wild Goldenthread (400g~1kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450197',
    '2026-01-07T12:00:30.450199'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c9c877fa-817a-456e-a44b-31dc68bb0631',
    'GGJ-AIR-FSH-0046',
    '鯖魚',
    '鯖魚',
    'Saba',
    'Fresh Wild Mackerel (500g~1kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450207',
    '2026-01-07T12:00:30.450209'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7dbd4fa0-5b1c-4a28-bf4a-fd415d6528f6',
    'GGJ-AIR-FSH-0047',
    '眼仁奈',
    '眼仁奈',
    'Mejina',
    'Fresh Wild Girella Leonina (0.5kg~1kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450218',
    '2026-01-07T12:00:30.450220'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '0db2966e-9d63-471f-8788-e5eba8a5a494',
    'GGJ-AIR-FSH-0048',
    '赤目張/目張',
    '赤目張/目張',
    'Mebaru',
    'Fresh White-edged rockfish (300g~500g)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'SPRING-SUMMER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450229',
    '2026-01-07T12:00:30.450230'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4d772d86-42a0-44c0-8dba-3c20f455862a',
    'GGJ-AIR-FSH-0049',
    '石頭魚',
    '石頭魚',
    'Okoze',
    'Fresh Stone fish (250g~400g)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'SPRING-SUMMER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450239',
    '2026-01-07T12:00:30.450240'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'ec0581c2-93c8-4177-a059-1d25cb4dabf1',
    'GGJ-AIR-FSH-0050',
    '石斑(九絵)',
    '石斑(九絵)',
    'Kue',
    'Fresh tawny grouper (1.5kg~10kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'WINTER-SPRING',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450249',
    '2026-01-07T12:00:30.450250'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'fbc7caed-1a05-4e5e-abed-d86f7033f743',
    'GGJ-AIR-FSH-0051',
    '赤血引',
    '赤血引',
    'Akachibiki',
    'Fresh Bonnet mouth Fish (1kg~2kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'AUTUMN-WINTER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450259',
    '2026-01-07T12:00:30.450261'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5975f3e5-20b9-41d5-a666-0f200b8eee27',
    'GGJ-AIR-FSH-0052',
    '笠子魚',
    '笠子魚',
    'Kasago',
    'Fresh Wild Marbled rockfish (0.4kg~1kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450270',
    '2026-01-07T12:00:30.450272'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '849f2caa-c2c0-4366-b7b8-92d5255ed72c',
    'GGJ-AIR-FSH-0053',
    '愛女魚',
    '愛女魚',
    'Ainame',
    'Fresh Fat greenling (600g~1.5kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'SPRING-AUTUMN',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450281',
    '2026-01-07T12:00:30.450282'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3f536166-5c7c-48cb-b220-24e2f23a2c62',
    'GGJ-AIR-FSH-0054',
    '赤矢柄',
    '赤矢柄',
    'Yagara',
    'Fresh Red Fistularia (1kg~2.5kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450291',
    '2026-01-07T12:00:30.450292'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '92be1259-62d8-434b-9e62-5491b747dffb',
    'GGJ-AIR-FSH-0055',
    '太刀魚',
    '太刀魚',
    'Tachuo',
    'Fresh Wild Cutlassfish (0.8kg~1.5kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450301',
    '2026-01-07T12:00:30.450303'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a4b2fd48-aa0e-4373-969e-8f32cc584208',
    'GGJ-AIR-FSH-0056',
    '白倉魚',
    '白倉魚',
    'MANA KATSUO',
    'Live Japanese Harvestfish (2kg~3kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450312',
    '2026-01-07T12:00:30.450314'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9d4974ef-1d75-4a31-bd96-7ae2dd8f855d',
    'GGJ-AIR-FSH-0057',
    '赤羽太',
    '赤羽太',
    'Akahata',
    'Fresh Red grouper (400g~1kg)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450323',
    '2026-01-07T12:00:30.450325'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9a98b1aa-1311-49f1-b869-45d8735a3b3d',
    'GGJ-AIR-FSH-0058',
    '青羽太',
    '青羽太',
    'Kihata',
    'Fresh Green grouper (600g~1.2KG)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450333',
    '2026-01-07T12:00:30.450335'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'dc26c052-85f0-4015-b9bf-25cc91fbe599',
    'GGJ-AIR-FSH-0059',
    '八角',
    '八角',
    'Hakkaku',
    'Fresh Agonus (400g~800g)',
    '飛機貨(鮮活) > 鮮魚/活口海鮮',
    '飛機貨(鮮活)',
    '鮮魚/活口海鮮',
    'KG',
    'WINTER-SPRING',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450343',
    '2026-01-07T12:00:30.450345'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'fe18ea3a-8276-423a-abf9-8c1b76f3e1aa',
    'GGJ-AIR-SMF-0060',
    '梭子魚',
    '梭子魚',
    'Kamasu',
    'Fresh Barracuda Fish (200g~250g)',
    '飛機貨(鮮活) > 小型魚/細魚',
    '飛機貨(鮮活)',
    '小型魚/細魚',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450354',
    '2026-01-07T12:00:30.450355'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd57d1a55-6f33-4c83-9e61-6e68c1e90563',
    'GGJ-AIR-SMF-0061',
    '針魚',
    '針魚',
    'Sayori',
    'Fresh Wild Japanese halfbeak (100-150G)',
    '飛機貨(鮮活) > 小型魚/細魚',
    '飛機貨(鮮活)',
    '小型魚/細魚',
    'KG',
    'WINTER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450365',
    '2026-01-07T12:00:30.450367'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '440229f7-12f9-4d5c-9bad-c5b93d917830',
    'GGJ-AIR-SMF-0062',
    '小肌',
    '小肌',
    'Kohada',
    'Fresh Wild Dottedgizzardshad (30g~50g)',
    '飛機貨(鮮活) > 小型魚/細魚',
    '飛機貨(鮮活)',
    '小型魚/細魚',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450375',
    '2026-01-07T12:00:30.450377'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '03aff069-c9b8-4055-abb7-db0a1d9b460a',
    'GGJ-AIR-SMF-0063',
    '沙搥魚',
    '沙搥魚',
    'Kisu',
    'Fresh Wild Sillaginidae (30g~50g)',
    '飛機貨(鮮活) > 小型魚/細魚',
    '飛機貨(鮮活)',
    '小型魚/細魚',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450385',
    '2026-01-07T12:00:30.450387'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '92cd0da8-7b93-4fa3-8987-b37857f44618',
    'GGJ-AIR-SMF-0064',
    '目光魚',
    '目光魚',
    'Mehikari',
    'Fresh Green Eyes Fish (20~60g)',
    '飛機貨(鮮活) > 小型魚/細魚',
    '飛機貨(鮮活)',
    '小型魚/細魚',
    'KG',
    'OCT-MAY',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450395',
    '2026-01-07T12:00:30.450397'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1389fa9c-71d3-4030-8ac3-655d72573966',
    'GGJ-AIR-SMF-0065',
    '公魚',
    '公魚',
    'Wakasaki',
    'Fresh wild Japanese smelt (10g~35g)',
    '飛機貨(鮮活) > 小型魚/細魚',
    '飛機貨(鮮活)',
    '小型魚/細魚',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450406',
    '2026-01-07T12:00:30.450407'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '8e2989a1-d8ae-4b8c-935b-7cb1ec35dc64',
    'GGJ-AIR-SMF-0066',
    '鮎魚(幼)',
    '鮎魚(幼)',
    'Chiayu',
    'Fresh Ayu sweetfish (200g/pk)',
    '飛機貨(鮮活) > 小型魚/細魚',
    '飛機貨(鮮活)',
    '小型魚/細魚',
    'PK',
    'SUMMER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450416',
    '2026-01-07T12:00:30.450417'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '67052940-c8f9-4883-99dd-ccb9fbc76af2',
    'GGJ-AIR-SMF-0067',
    '希靈魚',
    '希靈魚',
    'NISHIN',
    'Fresh Japan Herring (200g~600g)',
    '飛機貨(鮮活) > 小型魚/細魚',
    '飛機貨(鮮活)',
    '小型魚/細魚',
    'KG',
    'SPRING-SUMMER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450427',
    '2026-01-07T12:00:30.450428'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4cf4ecc2-e284-4419-abd6-98a631069115',
    'GGJ-AIR-SMF-0068',
    '穴子(開邊)',
    '穴子(開邊)',
    'ANAGO (HIRAKI)',
    'Cut Japanese conger eel (120g～300g)',
    '飛機貨(鮮活) > 小型魚/細魚',
    '飛機貨(鮮活)',
    '小型魚/細魚',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450437',
    '2026-01-07T12:00:30.450439'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd740fc34-d9eb-4e2e-9738-55f016a06d66',
    'GGJ-AIR-SMF-0069',
    '活〆穴子',
    '活〆穴子',
    'ANAGO',
    'Japanese conger eel (50g~200g)',
    '飛機貨(鮮活) > 小型魚/細魚',
    '飛機貨(鮮活)',
    '小型魚/細魚',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450448',
    '2026-01-07T12:00:30.450449'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '740cf9c1-1c39-43f3-9b88-61fc24fe0ce2',
    'GGJ-AIR-SMF-0070',
    '素白魚',
    '素白魚',
    'Isaza',
    'Live Ice goby (200g/pk)',
    '飛機貨(鮮活) > 小型魚/細魚',
    '飛機貨(鮮活)',
    '小型魚/細魚',
    'PK',
    'MARCH-APRIL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450458',
    '2026-01-07T12:00:30.450459'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a7512502-7173-44c0-8fcc-026252ec3dd5',
    'GGJ-AIR-SMF-0071',
    '穴子小魚',
    '穴子小魚',
    'Sorenore',
    'Fresh Japanese Baby conger eel (200g/pk)',
    '飛機貨(鮮活) > 小型魚/細魚',
    '飛機貨(鮮活)',
    '小型魚/細魚',
    'PK',
    'JAN-MAR',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450468',
    '2026-01-07T12:00:30.450470'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9210a6ae-cc6b-44f7-9a07-913a844d68a1',
    'GGJ-AIR-SHL-0072',
    '錫烏賊',
    '錫烏賊',
    'Surumeika',
    'Fresh Wild Japanese Common Squid (800G-1KG)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450478',
    '2026-01-07T12:00:30.450480'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '004f472b-d3d2-47d4-8d98-ba14c7d99e3c',
    'GGJ-AIR-SHL-0073',
    '槍烏賊',
    '槍烏賊',
    'Yariika',
    'Fresh Wild Spear Squid (300g~500g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450489',
    '2026-01-07T12:00:30.450490'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a462d949-36ba-4d28-b467-39c10292f70d',
    'GGJ-AIR-SHL-0074',
    '障泥烏賊',
    '障泥烏賊',
    'Aoriika',
    'Fresh Wild Big Fin Reef Squid (1kg~3kg)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450499',
    '2026-01-07T12:00:30.450500'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd4b466ed-fd2a-4f44-be86-2887e87b21b3',
    'GGJ-AIR-SHL-0075',
    '墨烏賊',
    '墨烏賊',
    'Sumiika',
    'Fresh Small cuttlefish (200g~500g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'NOV-JUN',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450510',
    '2026-01-07T12:00:30.450511'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '18049301-2788-4ec2-9d31-f5510f46dddd',
    'GGJ-AIR-SHL-0076',
    '水蛸足',
    '水蛸足',
    'MizuTako Ashi',
    'Fresh Otopus leg (800g~1.3kg)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450520',
    '2026-01-07T12:00:30.450521'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '49c5be55-f86a-4b15-849e-66bba1e54daa',
    'GGJ-AIR-SHL-0077',
    '劍先烏賊',
    '劍先烏賊',
    'Shiro ika',
    'White squid (200~800g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'SPRING-AUTUMN',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450531',
    '2026-01-07T12:00:30.450532'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4927bf4c-2061-4526-a70e-ca9e6ca19f58',
    'GGJ-AIR-SHL-0078',
    '熟螢烏賊',
    '熟螢烏賊',
    'Hotaruika (Boiru)',
    'Boiled Firefly Squid (200g/pk)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'PK',
    'FEB-MAY',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450576',
    '2026-01-07T12:00:30.450578'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '2ebf1939-aa7b-432e-b8a1-41dd07c15542',
    'GGJ-AIR-SHL-0079',
    '生螢烏賊',
    '生螢烏賊',
    'Nama Hotaruika',
    'Fresh Firefly Squid (200g/pk)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'PK',
    'MARCH-MAY',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450587',
    '2026-01-07T12:00:30.450589'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '39824114-f9ca-4e45-83c0-3eecfde04427',
    'GGJ-AIR-SHL-0080',
    '帆立貝肉 12玉',
    '帆立貝肉 12玉',
    'Hotate Mukimi 12pc',
    'Fresh Scallop meat (500g/pk)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450598',
    '2026-01-07T12:00:30.450599'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a5f7b615-623c-4bc4-9e3f-0581c09a7f5f',
    'GGJ-AIR-SHL-0081',
    '帆立貝肉 15玉',
    '帆立貝肉 15玉',
    'Hotate Mukimi 15pc',
    'Fresh Scallop meat (500g/pk)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450608',
    '2026-01-07T12:00:30.450609'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'cd00a3a8-764d-43cf-b94e-aa6b4f977e15',
    'GGJ-AIR-SHL-0082',
    '帆立貝肉 18玉',
    '帆立貝肉 18玉',
    'Hotate Mukimi 18pc',
    'Fresh Scallop meat (500g/pk)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450617',
    '2026-01-07T12:00:30.450619'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '58f98b9a-b692-4eb3-b012-bc0986863116',
    'GGJ-AIR-SHL-0083',
    '帆立貝(殼付)',
    '帆立貝(殼付)',
    'Karatsuki Hotate',
    'Live Scallop With Shell (150-400g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'PC',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450628',
    '2026-01-07T12:00:30.450630'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9d3a039b-4f97-4760-805d-28c00aadaa1b',
    'GGJ-AIR-SHL-0084',
    '平貝(殼付)',
    '平貝(殼付)',
    'Karatsuki Tairagai',
    'Live Japanese Pen Shell (500g~1Kg)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'PC',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450638',
    '2026-01-07T12:00:30.450640'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3b37be13-25b3-4514-9448-24a1eb8cdf74',
    'GGJ-AIR-SHL-0085',
    '(活)牡蠣',
    '(活)牡蠣',
    'Japanese Kaki',
    'Live Oyster (80G- 200g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'PC',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450649',
    '2026-01-07T12:00:30.450651'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '28e2728d-d7ab-4172-968a-ae78aa98248d',
    'GGJ-AIR-SHL-0086',
    '(活)岩牡蠣',
    '(活)岩牡蠣',
    'Japanese IwaKaki',
    'Live Rock Oyster (200G- 500g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'PC',
    'SUMMER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450659',
    '2026-01-07T12:00:30.450660'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'fdf8df68-0719-4b9b-84b2-4cbf87bf582f',
    'GGJ-AIR-SHL-0087',
    '生蠔肉',
    '生蠔肉',
    'Muki kaki',
    'Oyster Meat (500g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'WINTER-SPRING',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450670',
    '2026-01-07T12:00:30.450672'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'be7c26ce-e794-40d2-948e-df4cb9ca6fe9',
    'GGJ-AIR-SHL-0088',
    '小柱(黃)',
    '小柱(黃)',
    'Kobashira(Yellow)',
    'Fresh Wild Hen Clam (150g/pk)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450680',
    '2026-01-07T12:00:30.450682'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'bd27054f-c529-45c5-9881-faa9823f72bc',
    'GGJ-AIR-SHL-0089',
    '剝身青柳',
    '剝身青柳',
    'Aoyaki Mukimi',
    'Fresh Wild Mactra chinensis meat (100g/pk)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450690',
    '2026-01-07T12:00:30.450692'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '2a604042-38d0-4c51-9000-ce681a746fcd',
    'GGJ-AIR-SHL-0090',
    '青柳 (殼付)',
    '青柳 (殼付)',
    'Aoyaki with shell',
    'Fresh Mactra chinensis (60g~80g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'AUTUMN-SPRING',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450700',
    '2026-01-07T12:00:30.450702'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '8520f5ea-769c-4bed-882f-6a2e26c84a39',
    'GGJ-AIR-SHL-0091',
    '蜆',
    '蜆',
    'Asari',
    'Live Japanese Short-Neck Clam (20g~30g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450710',
    '2026-01-07T12:00:30.450712'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7fadf541-25c6-43a8-b2ea-dca3fcaed79a',
    'GGJ-AIR-SHL-0092',
    '大和蜆',
    '大和蜆',
    'YamatoShizimi',
    'Live Japanese Freshwater Clam (5g~10g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450720',
    '2026-01-07T12:00:30.450722'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1cf8c065-bdee-4196-ba05-9426e10ff50a',
    'GGJ-AIR-SHL-0093',
    '大蛤',
    '大蛤',
    'Hamaguri',
    'Live Japanese Hard Clam (40g~120g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450732',
    '2026-01-07T12:00:30.450734'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a41cfeb1-0f58-4fb9-9af6-a77220a56c69',
    'GGJ-AIR-SHL-0094',
    '地蛤',
    '地蛤',
    'JI-Hamaguri',
    'Live Japanese Hard Clam (60g~150g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450742',
    '2026-01-07T12:00:30.450744'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '8904ca1f-bfb7-4ce1-822f-4e024670b597',
    'GGJ-AIR-SHL-0095',
    '粒貝',
    '粒貝',
    'Tsubugai',
    'Live boiled spiral shellfish (200g~600g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450752',
    '2026-01-07T12:00:30.450754'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b014c080-3a78-48b5-8e7f-5c287a9eb4fd',
    'GGJ-AIR-SHL-0096',
    '赤貝(中國)',
    '赤貝(中國)',
    'Akagai (China)',
    'Fresh Ark Shell Clam (130~160g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450762',
    '2026-01-07T12:00:30.450764'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3ddc3168-175f-4a84-b24b-de63f2ace9b2',
    'GGJ-AIR-SHL-0097',
    '赤貝(日本)',
    '赤貝(日本)',
    'Akagai (Japan)',
    'Fresh Ark Shell Clam (120~180g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450773',
    '2026-01-07T12:00:30.450775'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '465f0083-124b-4c1e-8e5a-176fb94fc85f',
    'GGJ-AIR-SHL-0098',
    '北寄貝(殼付)',
    '北寄貝(殼付)',
    'Karatsuki Hokkigai',
    'Live Surf Clam With Shell (250g~500g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450783',
    '2026-01-07T12:00:30.450785'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'adec2768-5f80-4c75-9804-65532a8f0e1e',
    'GGJ-AIR-SHL-0099',
    '白象拔蚌(殼付)',
    '白象拔蚌(殼付)',
    'Shio Mirugai',
    'Live Japanese White Geoduck (300g~500g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450793',
    '2026-01-07T12:00:30.450795'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b47f219a-fbce-4fbb-b2a1-68c17afdb286',
    'GGJ-AIR-SHL-0100',
    '本象拔蚌(殼付)',
    '本象拔蚌(殼付)',
    'Hon mirugai',
    'Live Japanese Geoduck (400g~650g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450803',
    '2026-01-07T12:00:30.450805'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a1fc67a1-dd70-47e7-bfc6-cfaa3ba1f35b',
    'GGJ-AIR-SHL-0101',
    '白貝(殼付)',
    '白貝(殼付)',
    'Shirogai',
    'Fresh Northern great tellin (40g~60g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'SPRING-SUMMER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450815',
    '2026-01-07T12:00:30.450816'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '574deff7-0555-4247-9dc0-abacb6c64ae5',
    'GGJ-AIR-SHL-0102',
    '白梅貝(殼付)',
    '白梅貝(殼付)',
    'Shiro Baigai',
    'Fresh white Areola Babylon (20g~50g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450825',
    '2026-01-07T12:00:30.450827'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '475efd6a-bae0-4127-9ff2-8a0f017ffc0b',
    'GGJ-AIR-SHL-0103',
    '黑梅貝(殼付)',
    '黑梅貝(殼付)',
    'Kuro Baigai',
    'Fresh black Areola Babylon (30g~50g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450835',
    '2026-01-07T12:00:30.450837'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '64603125-2c92-45b9-90a4-744fef7ab5ad',
    'GGJ-AIR-SHL-0104',
    '亀の手(殼付)',
    '亀の手(殼付)',
    'Kamenote',
    'Fresh Japanese Goose barnacles (60g~120g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'FEB-AUGUST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450845',
    '2026-01-07T12:00:30.450847'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '8c5d5d71-066d-4b92-876e-6d718f909240',
    'GGJ-AIR-SHL-0105',
    '馬蹄螺(殼付)',
    '馬蹄螺(殼付)',
    'Shittaka gai',
    'Fresh Trochus snail (30g~50g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'APRIL-SEP',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450855',
    '2026-01-07T12:00:30.450857'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '6e3b8260-69b0-4be6-80d8-9713e4baf27c',
    'GGJ-AIR-SHL-0106',
    '內ムラメムラメ貝(殼付)',
    '內ムラメムラメ貝(殼付)',
    'Uchimurasaki gai',
    'Fresh Purple butter clam (150g~250g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'MARCH-DEC',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450865',
    '2026-01-07T12:00:30.450867'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '04c2fbfe-4540-4345-b06a-91445c498614',
    'GGJ-AIR-SHL-0107',
    '烏貝(殼付)',
    '烏貝(殼付)',
    'Torigai',
    'Fresh Japanese Cockle (80g~150g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'FEB-JUNE',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450877',
    '2026-01-07T12:00:30.450878'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'de5fb96a-2eb7-4540-b45e-4e9801630fc3',
    'GGJ-AIR-SHL-0108',
    '石垣貝(殼付)',
    '石垣貝(殼付)',
    'Ishigaki gai',
    'Fresh Japanese Bering Sea cockle (50g~80g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'JULY-OCT',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450887',
    '2026-01-07T12:00:30.450888'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '651820fd-f37b-4a4d-8e00-4337d7cffbad',
    'GGJ-AIR-SHL-0109',
    '姬榮螺(殼付)',
    '姬榮螺(殼付)',
    'Himesazae',
    'Fresh Horned Turban SMALL (40g~60g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'MARCH-JUNE',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450898',
    '2026-01-07T12:00:30.450900'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'cc749e28-8f56-4610-9dc6-2c7c8bb01a92',
    'GGJ-AIR-SHL-0110',
    '榮螺(殼付)',
    '榮螺(殼付)',
    'Sazae',
    'Fresh Japanese Horned Turban (100g~400g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450909',
    '2026-01-07T12:00:30.450910'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd5ddfb34-edf7-471d-bf4d-32e0d4329294',
    'GGJ-AIR-SHL-0111',
    '檜扇貝(殼付)',
    '檜扇貝(殼付)',
    'Hiougi gai',
    'Fresh Noble scallop (90g~130g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'PC',
    'NOV-MAY',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450919',
    '2026-01-07T12:00:30.450921'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '89a8fb1a-f23c-464f-a220-17f2fa920a77',
    'GGJ-AIR-SHL-0112',
    '大溝貝',
    '大溝貝',
    'Oomizo kai',
    'Fresh Razor clam (70g~150g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'WINTER-SPRING',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450930',
    '2026-01-07T12:00:30.450932'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4bdb0a4a-1e23-4e02-9664-6be6471e32e0',
    'GGJ-AIR-SHL-0113',
    '(活)黑鮑魚',
    '(活)黑鮑魚',
    'Kuro Awabi',
    'Live Japanese Disk Abalone (200g~500g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450942',
    '2026-01-07T12:00:30.450943'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1ab06629-6d0d-4bde-902f-57ef0704b4d1',
    'GGJ-AIR-SHL-0114',
    '(活)赤鮑魚',
    '(活)赤鮑魚',
    'Aka Awabi',
    'Live Japanese Ruber Abalone (200g~490g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450953',
    '2026-01-07T12:00:30.450955'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '78606685-21d2-40fb-974f-aa212b83b086',
    'GGJ-AIR-SHL-0115',
    '(活)蝦夷鮑魚',
    '(活)蝦夷鮑魚',
    'EzoAwabi',
    'Live Japanese Disk Abalone Small (100~150g)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450964',
    '2026-01-07T12:00:30.450965'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '248014c7-8412-4219-bf82-b0ae7cac0350',
    'GGJ-AIR-SHL-0116',
    '韓國鮑',
    '韓國鮑',
    'Kankoku Awabi',
    'Live Korean Abalone (100～110ｇ)',
    '飛機貨(鮮活) > 貝類/軟體海鮮',
    '飛機貨(鮮活)',
    '貝類/軟體海鮮',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450974',
    '2026-01-07T12:00:30.450976'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b6a5e871-d14b-47a9-b229-e402dfc099b8',
    'GGJ-AIR-CRU-0117',
    '(活)牡丹蝦',
    '(活)牡丹蝦',
    'Botan Ebi',
    'Live Japanese Botan shrimp (30g~50g)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450986',
    '2026-01-07T12:00:30.450988'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3e8912b7-0bcb-4057-b112-baf35d43060e',
    'GGJ-AIR-CRU-0118',
    '(活)縞蝦',
    '(活)縞蝦',
    'Shima ebi',
    'Fresh morotoge shrimp (16g~40g)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.450996',
    '2026-01-07T12:00:30.450998'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5906b205-c89b-4e98-8a38-0fb1d87e9979',
    'GGJ-AIR-CRU-0119',
    '(活)車海老',
    '(活)車海老',
    'Kuruma Ebi',
    'Live Japanese Tiger Prawn (20g~45g)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451007',
    '2026-01-07T12:00:30.451009'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f26f494c-e7d2-4c6c-9c47-a1089cb84af9',
    'GGJ-AIR-CRU-0120',
    '(活)伊勢海老',
    '(活)伊勢海老',
    'IseEbi',
    'Live Japanese Spiny Lobster (250g~800g)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451017',
    '2026-01-07T12:00:30.451019'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f603a42b-3d17-4da4-b4b1-d86ca5f0e11a',
    'GGJ-AIR-CRU-0121',
    '赤座海老',
    '赤座海老',
    'Akazaebi',
    'Live Japanese langoustine (100g~130g)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451028',
    '2026-01-07T12:00:30.451029'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '32c1fb88-4a4b-413d-974c-2ff8c0dfee0d',
    'GGJ-AIR-CRU-0122',
    '葡萄海老',
    '葡萄海老',
    'Budouebi',
    'Fresh Hokkaido Pandalus (50g~80g)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'KG',
    'SPRING-SUMMER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451038',
    '2026-01-07T12:00:30.451039'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '227fa9f4-21eb-4388-ab13-e1080ef0ecc4',
    'GGJ-AIR-CRU-0123',
    '白海老肉',
    '白海老肉',
    'Muki Shiroebi',
    'Fresh small Wihte shrimp w/ no shell (200g~300/pk)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451048',
    '2026-01-07T12:00:30.451050'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '71377ac0-9afb-44c5-be9e-e011f3bb0fab',
    'GGJ-AIR-CRU-0124',
    '生櫻花蝦',
    '生櫻花蝦',
    'Namarei sakuraebi',
    'Fresh Sakura shrimp (500g/pk)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'PK',
    'APRIL-JUNE',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451058',
    '2026-01-07T12:00:30.451060'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '79937a51-b593-4ea2-9d34-9de07512533b',
    'GGJ-AIR-CRU-0125',
    '有殻白蝦',
    '有殻白蝦',
    'Karatsuki shiroebi',
    'Fresh small Wihte shrimp w/ shell (200g/ 500g)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'PK',
    'SUMMER-AUTUMN',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451070',
    '2026-01-07T12:00:30.451071'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3c5d9569-b0fb-4102-829d-2272d465a9a2',
    'GGJ-AIR-CRU-0126',
    '冷凍芝蝦 (剝身)',
    '冷凍芝蝦 (剝身)',
    'Shibaebi (Muki)',
    'Frozen Shiba shrimp (500 g/pk)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451080',
    '2026-01-07T12:00:30.451081'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '84d4515e-ef88-4f39-97af-ab1127199514',
    'GGJ-AIR-CRU-0127',
    '瀬尿蝦 (PK)',
    '瀬尿蝦 (PK)',
    'Shako(Chilled)',
    'Chilled Mantis Shrimp (300g~500g/pk)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'PK',
    'SUMMER-AUTUMN',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451092',
    '2026-01-07T12:00:30.451093'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '0f4f328c-e166-4457-a29c-eb908e154f19',
    'GGJ-AIR-CRU-0128',
    '(活)松葉蟹',
    '(活)松葉蟹',
    'Zuwaigani',
    'Live Queen crab (600g~1.2KG)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'KG',
    'WINTER-SPRING',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451102',
    '2026-01-07T12:00:30.451104'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '410752ad-271f-46ec-bd7a-d57e0b5304b3',
    'GGJ-AIR-CRU-0129',
    '花咲蟹',
    '花咲蟹',
    'Hanasakigani',
    'Fresh brown king crab (600g~1KG)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'KG',
    'SUMMER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451112',
    '2026-01-07T12:00:30.451114'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c3632266-be9c-45d8-88c0-367ff41d3017',
    'GGJ-AIR-CRU-0130',
    '毛蟹',
    '毛蟹',
    'Kegani',
    'Fresh Hairy Crab (400ｇ～1KG)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451122',
    '2026-01-07T12:00:30.451124'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '34c01fe9-baaa-466f-a0ec-216fbaafb93c',
    'GGJ-AIR-CRU-0131',
    '(活)香箱蟹',
    '(活)香箱蟹',
    'Seikogani',
    'Live Fresh Kobako crab (100g~200g)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'PC',
    'WINTER-SPRING',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451132',
    '2026-01-07T12:00:30.451134'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '98870a96-62db-41c4-ae56-05325a5c55ea',
    'GGJ-AIR-CRU-0132',
    '拆肉香箱蟹',
    '拆肉香箱蟹',
    'Muki Seikogani',
    'Kobako crab Meat w/ shell boiled (100g~200g)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'PC',
    'WINTER-SPRING',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451142',
    '2026-01-07T12:00:30.451144'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5ae3f00c-aa0c-42aa-ba85-af033a838862',
    'GGJ-AIR-CRU-0133',
    '栗蟹',
    '栗蟹',
    'Kurigani',
    'Fresh Helmet crab (300g~800g)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'KG',
    'APRIL-JUNE',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451152',
    '2026-01-07T12:00:30.451154'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '6ece2af8-7f2f-4b37-9019-28d6dc560234',
    'GGJ-AIR-CRU-0134',
    '渡蟹',
    '渡蟹',
    'Watarigani',
    'Fresh Swimming crabs (500g~600g)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'KG',
    'MAY-JAN',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451162',
    '2026-01-07T12:00:30.451164'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1be4cf11-8a61-43e9-9df6-ccfba6753bec',
    'GGJ-AIR-CRU-0135',
    '(活)沢蟹',
    '(活)沢蟹',
    'Japanese Zawagani',
    'Live Japanese Zawagani (100g/pk)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'PK',
    'MID MAR-NOV',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451173',
    '2026-01-07T12:00:30.451175'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'facfbae3-7f93-4dde-ad27-18f837f57494',
    'GGJ-AIR-CRU-0136',
    '蟹棒',
    '蟹棒',
    'Kani Bou',
    'Queen crab leg meat (350g~400g)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451183',
    '2026-01-07T12:00:30.451185'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b80bdb04-3566-470c-a901-21d12709807c',
    'GGJ-AIR-CRU-0137',
    '松葉蟹肉碎',
    '松葉蟹肉碎',
    'Zuwai gani meat',
    'Fresh Queen crab meat (200g)',
    '飛機貨(鮮活) > 蝦蟹類',
    '飛機貨(鮮活)',
    '蝦蟹類',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451194',
    '2026-01-07T12:00:30.451196'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9832b6b2-9f1f-4271-80aa-7e197b71383f',
    'GGJ-AIR-ROE-0138',
    '海膽 (並排／亂排)',
    '海膽 (並排／亂排)',
    'Uni(Narabi/Bara)',
    'Japanese sea urchin (250G~400g)',
    '飛機貨(鮮活) > 海膽/魚卵/肝',
    '飛機貨(鮮活)',
    '海膽/魚卵/肝',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451204',
    '2026-01-07T12:00:30.451206'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'ec038d77-bd65-4fd7-a1e2-b3da857294fb',
    'GGJ-AIR-ROE-0139',
    '塩水海膽',
    '塩水海膽',
    'Kaisui uni',
    'Japanese urchin In sea water (100g)',
    '飛機貨(鮮活) > 海膽/魚卵/肝',
    '飛機貨(鮮活)',
    '海膽/魚卵/肝',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451214',
    '2026-01-07T12:00:30.451216'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd7cc7cd5-b1b3-4755-a5e3-d23cc2bbd6a1',
    'GGJ-AIR-ROE-0140',
    '(活)原隻海膽',
    '(活)原隻海膽',
    'Karatsuki Bafu Uni',
    'Live Japanese Sea Urchin With Shell (30g~35g)',
    '飛機貨(鮮活) > 海膽/魚卵/肝',
    '飛機貨(鮮活)',
    '海膽/魚卵/肝',
    'PC',
    'MAY-AUGUST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451224',
    '2026-01-07T12:00:30.451226'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4e0c04fb-131c-4ab7-9997-330aa920b67b',
    'GGJ-AIR-ROE-0141',
    '白子',
    '白子',
    'SHIRAKO',
    'Fresh Japanese COD sperm (500g/pk)',
    '飛機貨(鮮活) > 海膽/魚卵/肝',
    '飛機貨(鮮活)',
    '海膽/魚卵/肝',
    'PK',
    'WINTER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451234',
    '2026-01-07T12:00:30.451236'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '16a0824f-03fe-486a-8dde-faf9f44f73a6',
    'GGJ-AIR-ROE-0142',
    '鯛白子',
    '鯛白子',
    'Tai shirako',
    'Fresh Japanese sea bream sperm (500g/pk)',
    '飛機貨(鮮活) > 海膽/魚卵/肝',
    '飛機貨(鮮活)',
    '海膽/魚卵/肝',
    'PK',
    'MARCH-MAY',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451245',
    '2026-01-07T12:00:30.451247'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '2de348d4-1d3e-4db7-9aa1-b0781b708558',
    'GGJ-AIR-ROE-0143',
    '生筋子',
    '生筋子',
    'Sujiko',
    'Fresh salmon roe (150g~180g)',
    '飛機貨(鮮活) > 海膽/魚卵/肝',
    '飛機貨(鮮活)',
    '海膽/魚卵/肝',
    'KG',
    'AUG-DEC',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451255',
    '2026-01-07T12:00:30.451258'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b8318a33-0f11-4810-a209-6267871d6795',
    'GGJ-AIR-ROE-0144',
    '烏魚籽',
    '烏魚籽',
    'Borako',
    'Fresh Mullet Roe (200~250g)',
    '飛機貨(鮮活) > 海膽/魚卵/肝',
    '飛機貨(鮮活)',
    '海膽/魚卵/肝',
    'KG',
    'NOV-DEC',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451266',
    '2026-01-07T12:00:30.451268'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '52cad965-f1b9-4ae9-a32f-3f7b0c542a0d',
    'GGJ-AIR-ROE-0145',
    '数之子',
    '数之子',
    'Kazunoko',
    'Fresh Herring Roe (500g~1KG)',
    '飛機貨(鮮活) > 海膽/魚卵/肝',
    '飛機貨(鮮活)',
    '海膽/魚卵/肝',
    'PK',
    'SEASONAL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451276',
    '2026-01-07T12:00:30.451278'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '6280c842-0666-459d-8ab4-36b40e4e7208',
    'GGJ-AIR-ROE-0146',
    '赤海參',
    '赤海參',
    'Akanomako',
    'Fresh Red sea cucumbers (150g~400g)',
    '飛機貨(鮮活) > 海膽/魚卵/肝',
    '飛機貨(鮮活)',
    '海膽/魚卵/肝',
    'KG',
    'NOV-MARCH',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451286',
    '2026-01-07T12:00:30.451288'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'fd93df10-4a2f-4f02-8e23-dc76454082a0',
    'GGJ-AIR-ROE-0147',
    '魚子醤',
    '魚子醤',
    'Kyabia',
    'Caviar in can (30g/50g/100g)',
    '飛機貨(鮮活) > 海膽/魚卵/肝',
    '飛機貨(鮮活)',
    '海膽/魚卵/肝',
    'CAN',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451298',
    '2026-01-07T12:00:30.451299'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a1a6a457-1879-4acd-8428-7b2445d9051d',
    'GGJ-AIR-ROE-0148',
    '鮟肝 (中國)',
    '鮟肝 (中國)',
    'ANKIMO(CHINESE)',
    'Fresh Chinese Anglerfish LIVER (500g up)',
    '飛機貨(鮮活) > 海膽/魚卵/肝',
    '飛機貨(鮮活)',
    '海膽/魚卵/肝',
    'KG',
    'WINTER-SPRING',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451308',
    '2026-01-07T12:00:30.451309'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '2cdde90b-8015-40d8-a2cf-4d213c149187',
    'GGJ-AIR-ROE-0149',
    '鮟肝 (日本)',
    '鮟肝 (日本)',
    'ANKIMO',
    'Fresh Japanese Anglerfish LIVER (500g up)',
    '飛機貨(鮮活) > 海膽/魚卵/肝',
    '飛機貨(鮮活)',
    '海膽/魚卵/肝',
    'KG',
    'AUTUMN-SPRING',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451318',
    '2026-01-07T12:00:30.451319'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9c528049-57c8-4f92-9d9b-ff5a552f4007',
    'GGJ-AIR-ROE-0150',
    '鮑肝',
    '鮑肝',
    'Awabi kimo',
    'FrozenAbalone liver (1kg/pk)',
    '飛機貨(鮮活) > 海膽/魚卵/肝',
    '飛機貨(鮮活)',
    '海膽/魚卵/肝',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451328',
    '2026-01-07T12:00:30.451329'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd42a81a0-4c03-4b22-8f7a-0829f5fe98e5',
    'GGJ-AIR-PRC-0151',
    '冷凍切骨門鱔',
    '冷凍切骨門鱔',
    'Homo (honekira)',
    'Boneless blotched snakehead (500g/pk)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451338',
    '2026-01-07T12:00:30.451340'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3f2ed303-8ec6-458b-b1bd-924089139ee8',
    'GGJ-AIR-PRC-0152',
    '煮八爪足',
    '煮八爪足',
    'Takonoyawarakani',
    'Slow cooked Octopus Leg (600~750g)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451369',
    '2026-01-07T12:00:30.451370'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'dcfccab8-0cdf-4563-bf5f-6803f5f8a29c',
    'GGJ-AIR-PRC-0153',
    '海雲 (粗/幼)',
    '海雲 (粗/幼)',
    'Mozuku',
    'Small Thin marine alga (500g/1kg)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451388',
    '2026-01-07T12:00:30.451390'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5cd3377f-29d4-4e83-929d-6c1bfff40a3e',
    'GGJ-AIR-PRC-0154',
    '子持昆布',
    '子持昆布',
    'Komochi Konbu',
    'Fresh herring spawn on kelp',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'KG',
    'SUMMER-AUTUMN',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451399',
    '2026-01-07T12:00:30.451401'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '002fa82e-e25c-40e6-8784-f56b5a2bb0ee',
    'GGJ-AIR-PRC-0155',
    '生紫菜',
    '生紫菜',
    'Nama nori',
    'Fresh Seaweed (100g)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451410',
    '2026-01-07T12:00:30.451412'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5600dfae-da54-4755-8a79-921095413bf9',
    'GGJ-AIR-PRC-0156',
    '絹豆腐',
    '絹豆腐',
    'Kinu tofu',
    'Silk Tofu (200g)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451421',
    '2026-01-07T12:00:30.451422'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'afa4faaa-15dc-4f67-a2c7-3623db088714',
    'GGJ-AIR-PRC-0157',
    '高野豆腐',
    '高野豆腐',
    'Kouya tofu',
    'Freeze-dried tofu (200g)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451432',
    '2026-01-07T12:00:30.451433'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'eecc8398-2a41-4a6b-af01-524257caf7db',
    'GGJ-AIR-PRC-0158',
    '厚揚 (AIR)',
    '厚揚 (AIR)',
    'Atsuage',
    'Fried tofu in pack (1-6pc)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451442',
    '2026-01-07T12:00:30.451444'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e82f8b8b-b48c-4dab-af14-ba17df9f94d5',
    'GGJ-AIR-PRC-0159',
    '海膽豆腐',
    '海膽豆腐',
    'Uni tofu',
    'Sea Urchin Tofu (200g)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451453',
    '2026-01-07T12:00:30.451454'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '570e902d-1d1e-41d5-a843-be5c99bb43f4',
    'GGJ-AIR-PRC-0160',
    '蟹味噌豆腐',
    '蟹味噌豆腐',
    'Gani miso tofu',
    'Crab Miso Tofu (200g)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451464',
    '2026-01-07T12:00:30.451465'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '10130612-b563-4e3d-9e05-f6d9ca9744c0',
    'GGJ-AIR-PRC-0161',
    '刺身湯葉',
    '刺身湯葉',
    'Yuba toro',
    'Fresh Yuba (300g)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451630',
    '2026-01-07T12:00:30.451632'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9c7aa231-e10a-4b23-bfb7-6a0331394fce',
    'GGJ-AIR-PRC-0162',
    '板湯葉',
    '板湯葉',
    'Itayuba',
    'Yuba in sheet (100g)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451643',
    '2026-01-07T12:00:30.451645'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b61dcb93-f0dd-4cac-a41f-6d14738a9757',
    'GGJ-AIR-PRC-0163',
    '新鮮海草',
    '新鮮海草',
    'Nama wakame',
    'Fresh Wakame (500g~1KG)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451653',
    '2026-01-07T12:00:30.451655'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd8fc6db5-2967-46d5-971c-ddbafa728413',
    'GGJ-AIR-PRC-0164',
    '鮮雞冠草',
    '鮮雞冠草',
    'Nama Tosaka',
    'Fresh Tosaka MIX (500ｇ/pc)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451664',
    '2026-01-07T12:00:30.451665'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '58ecf2d2-6998-4adc-a3eb-fdd774c6483c',
    'GGJ-AIR-PRC-0165',
    '海葡萄',
    '海葡萄',
    'Umi budou',
    'Fresh Sea Grape (100g/pk)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'SUMMER-AUTUMN',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451674',
    '2026-01-07T12:00:30.451676'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '28b05f06-020a-412c-bc2d-ee18d6c6c44b',
    'GGJ-AIR-PRC-0166',
    '鯛魚酒盗',
    '鯛魚酒盗',
    'Tai shuto',
    'Pickled salted sea Bream (500g/pk)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'BTL',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451684',
    '2026-01-07T12:00:30.451686'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c6ec92bf-5ae6-4721-a14d-dfadcadba94b',
    'GGJ-AIR-PRC-0167',
    '呑拿魚酒盗',
    '呑拿魚酒盗',
    'Maguro shuto',
    'Pickled salted tuna (250g~380g)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'BTL',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451696',
    '2026-01-07T12:00:30.451697'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '86c6ff57-a7bc-446d-8b11-887060d344f5',
    'GGJ-AIR-PRC-0168',
    '鱈魚塩辛',
    '鱈魚塩辛',
    'Chanja',
    'Pickled salted COD fish guts (500g)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'BTL',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451709',
    '2026-01-07T12:00:30.451710'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '03eff8b7-e020-4c51-9f0a-9b107af9aff3',
    'GGJ-AIR-PRC-0169',
    '鮎塩辛',
    '鮎塩辛',
    'Ayu Uruka',
    'Pickled salted Ayu sweetfish guts (50g~80g)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'BTL',
    'SUMMER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451719',
    '2026-01-07T12:00:30.451721'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '16cb0692-0259-4b5b-ab36-5eed8be0b3e6',
    'GGJ-AIR-PRC-0170',
    '白板昆布',
    '白板昆布',
    'Hattera',
    'Dried White Konbu (100PC/PK)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451729',
    '2026-01-07T12:00:30.451731'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '84d728d1-5d8f-4d5d-9083-0816928ef659',
    'GGJ-AIR-PRC-0171',
    '岩塩板',
    '岩塩板',
    'Ganen plate',
    'Japanese Pink salt plate (400g~800g)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PC',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451739',
    '2026-01-07T12:00:30.451741'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '809761a7-b0a6-4b16-8de5-d827eed2c396',
    'GGJ-AIR-PRC-0172',
    '酢味噌',
    '酢味噌',
    'Sumiso',
    'Mustard sour Miso paste (1kg/pc)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451749',
    '2026-01-07T12:00:30.451751'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '51c7206f-9eeb-4dc9-9a0e-a0a7ad4c0d00',
    'GGJ-AIR-PRC-0173',
    '味付鰻魚骨 (小吃)',
    '味付鰻魚骨 (小吃)',
    'Tsuke Unagi Hone',
    'Flavored fried eel bone snack (500g/pk)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451759',
    '2026-01-07T12:00:30.451761'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '79c6f20d-84f1-4f17-8c70-b506d69284e0',
    'GGJ-AIR-PRC-0174',
    '青桔JELLY',
    '青桔JELLY',
    'Kabosu Jelly',
    'Kabosu Fruits Jelly',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451770',
    '2026-01-07T12:00:30.451771'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'de2f44b2-e573-486d-8245-60c6a34a8a7c',
    'GGJ-AIR-PRC-0175',
    '酢橘JELLY',
    '酢橘JELLY',
    'Sudachi Jelly',
    'Citrus Sudachi Jelly',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451780',
    '2026-01-07T12:00:30.451782'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a521315e-5ab9-4ef5-82ad-34961bb1d3bb',
    'GGJ-AIR-PRC-0176',
    '最中皮',
    '最中皮',
    'Monaka',
    'Japanese Wagashi Monaka shell (100pc/box)',
    '飛機貨(鮮活) > 加工/其他',
    '飛機貨(鮮活)',
    '加工/其他',
    'BOX',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451790',
    '2026-01-07T12:00:30.451793'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7a082497-db1a-40a9-964d-dd4b37b07625',
    'GGJ-AIR-VEG-0177',
    '日本大葉',
    '日本大葉',
    'Ohba',
    'Japanese Shiso (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451804',
    '2026-01-07T12:00:30.451806'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '84466eda-e8f2-4fe4-8364-cd19c3a3418a',
    'GGJ-AIR-VEG-0178',
    '本地大葉',
    '本地大葉',
    'Ohba',
    'Local Shiso (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451815',
    '2026-01-07T12:00:30.451817'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f44b2927-7d92-49b1-adb9-fc909978ac58',
    'GGJ-AIR-VEG-0179',
    '花穗',
    '花穗',
    'Hanahojiso',
    'Japanese Hanahojiso (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451826',
    '2026-01-07T12:00:30.451827'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '8442f27c-3b78-402d-a31c-51ab7cf408aa',
    'GGJ-AIR-VEG-0180',
    '食用花',
    '食用花',
    'Edible flower',
    'Japanese Edible Flower (30g/pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451835',
    '2026-01-07T12:00:30.451837'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'dd5e0bdc-fba1-4d8f-986e-198b13361367',
    'GGJ-AIR-VEG-0181',
    '三葉',
    '三葉',
    'Mitsuba',
    'Japanese Hornwort (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451846',
    '2026-01-07T12:00:30.451847'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '110b2e8a-84c6-4139-8b17-8b29a35c84d7',
    'GGJ-AIR-VEG-0182',
    '水菜',
    '水菜',
    'Mizuna',
    'Japanese Potherb Mustard (100g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451856',
    '2026-01-07T12:00:30.451857'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e4cd8700-3388-4fc0-9d20-69661801b05f',
    'GGJ-AIR-VEG-0183',
    '四季紅',
    '四季紅',
    'Benitade',
    'Japanese Benitade (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451866',
    '2026-01-07T12:00:30.451868'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1255fe29-ffad-4c92-8cf8-cabc61f2ca66',
    'GGJ-AIR-VEG-0184',
    '水晶菜',
    '水晶菜',
    'Barafu',
    'Japanese Barafu (100g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451876',
    '2026-01-07T12:00:30.451878'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b5393c05-4312-4066-82a9-a3a59ca1b5ca',
    'GGJ-AIR-VEG-0185',
    '紅楓葉/ 青楓葉',
    '紅楓葉/ 青楓葉',
    'AKA/AO Momiji',
    'Japanese Red Momiji (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451887',
    '2026-01-07T12:00:30.451889'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '752253ed-43ff-4cad-8a3e-9a09af040571',
    'GGJ-AIR-VEG-0186',
    '板本菊',
    '板本菊',
    'Sakamotogiku',
    'Japanese Edible Chrysanthemum (80g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451897',
    '2026-01-07T12:00:30.451899'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c64ea2e6-b606-4ee6-9222-2e8464d828c5',
    'GGJ-AIR-VEG-0187',
    '小菊',
    '小菊',
    'Kogiku',
    'Japanese Mini Edible Chrysanthemum (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451908',
    '2026-01-07T12:00:30.451910'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '964a3a3a-fa2e-4574-83e5-83387bd95136',
    'GGJ-AIR-VEG-0188',
    '金魚草',
    '金魚草',
    'Kingyoso',
    'Japanese Antirrhinum Majus (30g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451918',
    '2026-01-07T12:00:30.451919'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3b17995d-5b29-459e-9194-4f86fd187d34',
    'GGJ-AIR-VEG-0189',
    '木之芽',
    '木之芽',
    'Kinome',
    'Japanese Kinome (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451928',
    '2026-01-07T12:00:30.451930'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3bd76be7-e8d1-4706-b142-fe35c8926568',
    'GGJ-AIR-VEG-0190',
    '紫芽',
    '紫芽',
    'Murame',
    'Purple Shiso bud (50g/pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'SPRING-AUTUMN',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451938',
    '2026-01-07T12:00:30.451940'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '262d18a1-269f-440c-a68c-4e78b3dd35df',
    'GGJ-AIR-VEG-0191',
    '黃柚子/青柚子',
    '黃柚子/青柚子',
    'Yellow/Green Yuzu',
    'Japanese Yuzu (20~30G/pc)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PC',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451948',
    '2026-01-07T12:00:30.451950'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '49c6967a-caa9-4e73-a097-81ec3e700569',
    'GGJ-AIR-VEG-0192',
    '青檸',
    '青檸',
    'Sudachi',
    'Japanese Sudachi (10g / pc)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451958',
    '2026-01-07T12:00:30.451960'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'ba955369-d1b7-42d9-a18f-de321ae61ef5',
    'GGJ-AIR-VEG-0193',
    '松葉(針)',
    '松葉(針)',
    'Matsuba',
    'Japanese Matsuba (80g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'SPRING-AUTUMN',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451972',
    '2026-01-07T12:00:30.451973'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e295b02e-8ea4-4a61-a34a-194b83f6e09b',
    'GGJ-AIR-VEG-0194',
    '松柏/檜葉',
    '松柏/檜葉',
    'Hiba',
    'Japanese Matsuba (200g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451982',
    '2026-01-07T12:00:30.451983'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '26166190-3a97-4446-ba57-24908bc360c2',
    'GGJ-AIR-VEG-0195',
    '青南天',
    '青南天',
    'Ao Nanntenn',
    'Japanese Green Nanntenn (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.451992',
    '2026-01-07T12:00:30.451993'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '60e5dd91-1ffc-4fb6-a896-eb9bde7991b7',
    'GGJ-AIR-VEG-0196',
    '赤南天',
    '赤南天',
    'Aka Nanntenn',
    'Japanese Red Nanntenn (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'WINTER-SPRING',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452003',
    '2026-01-07T12:00:30.452005'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b255cbbf-3694-4ad9-8986-30b8ea71713c',
    'GGJ-AIR-VEG-0197',
    '明日葉',
    '明日葉',
    'Asita No Ha',
    'Japanese Asita No Ha (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452016',
    '2026-01-07T12:00:30.452018'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '13ffbda2-9a61-4018-8fda-0fdf4ef7d8fe',
    'GGJ-AIR-VEG-0198',
    '立桂',
    '立桂',
    'Tachikatsura',
    'Japanese Tachitade (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452026',
    '2026-01-07T12:00:30.452028'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b2e84529-30e1-4d8b-8b4a-26179354f01e',
    'GGJ-AIR-VEG-0199',
    '白粟米',
    '白粟米',
    'White Corn',
    'Japanese White Corn (0.4kg / pc)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PC',
    'SUMMER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452036',
    '2026-01-07T12:00:30.452038'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '526330c5-f231-4456-a5ce-563c04286771',
    'GGJ-AIR-VEG-0200',
    '胡蔥/浅葱',
    '胡蔥/浅葱',
    'Asatsuki',
    'Japanese Shantou (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452047',
    '2026-01-07T12:00:30.452048'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '0fa291cd-7376-4671-8b73-815ad829077b',
    'GGJ-AIR-VEG-0201',
    '小笹／迷你竹葉',
    '小笹／迷你竹葉',
    'Ozasa',
    'Japanese Edazasa (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452057',
    '2026-01-07T12:00:30.452059'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '20c5c725-12b0-4592-b891-5067d25bb7de',
    'GGJ-AIR-VEG-0202',
    '防風',
    '防風',
    'Boufu',
    'Japanese Boufu (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452068',
    '2026-01-07T12:00:30.452069'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c953a94b-8862-445b-8112-badf3be31e18',
    'GGJ-AIR-VEG-0203',
    '新鮮芥辣根',
    '新鮮芥辣根',
    'Nama Wasabi',
    'Japanese Fresh Wasabi (80g~120g/pc)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PC',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452078',
    '2026-01-07T12:00:30.452079'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '172900dd-300f-4394-aa5d-04669d208db8',
    'GGJ-AIR-VEG-0204',
    '小玫瑰',
    '小玫瑰',
    'Rose',
    'Japanese Rose (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452088',
    '2026-01-07T12:00:30.452089'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7f54d7b7-f901-4420-b6d4-750a21cd9daf',
    'GGJ-AIR-VEG-0205',
    '丸茄子',
    '丸茄子',
    'Marunasu',
    'Japanese Round Egg Plant (180g~220g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PC',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452098',
    '2026-01-07T12:00:30.452099'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '167a18cc-ac41-4762-94f2-2629cb4c1aa6',
    'GGJ-AIR-VEG-0206',
    '長茄子',
    '長茄子',
    'Naganasu',
    'Japanese Long Egg Plant (80g~120g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452108',
    '2026-01-07T12:00:30.452109'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7b5dd804-5488-4b7e-ade7-9c9a8aa1d9e4',
    'GGJ-AIR-VEG-0207',
    '水茄子',
    '水茄子',
    'Mizunasu',
    'Japanese America Egg Plant (100g / pc)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PC',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452119',
    '2026-01-07T12:00:30.452121'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '2da3863f-e771-4918-b11e-a32fac996fb9',
    'GGJ-AIR-VEG-0208',
    '千兩茄子',
    '千兩茄子',
    'Senryo Nasu',
    'Japanese Senryo Egg Plant (70g~100g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452129',
    '2026-01-07T12:00:30.452131'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'cba25f40-8838-4ba2-8687-19c0ab409a53',
    'GGJ-AIR-VEG-0209',
    '小茄子',
    '小茄子',
    'Konasu',
    'Japanese Little Egg Plant (25pc~30pc)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452141',
    '2026-01-07T12:00:30.452143'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9a2f41f4-4004-4f66-9f07-3fdb88ca254d',
    'GGJ-AIR-VEG-0210',
    '日本蕃茄',
    '日本蕃茄',
    'Tomato',
    'Japanese Tomato (15g~20g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PC',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452151',
    '2026-01-07T12:00:30.452153'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f191da97-7f2a-478c-badf-56e11d3c2586',
    'GGJ-AIR-VEG-0211',
    '果蕃茄',
    '果蕃茄',
    'Fruit Tomato',
    'Japanese Fruit Tomato (12~18pc / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'BOX',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452161',
    '2026-01-07T12:00:30.452163'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '8e0f360e-0773-4772-bbc2-048fe72484fb',
    'GGJ-AIR-VEG-0212',
    '迷你蕃茄',
    '迷你蕃茄',
    'Mini Tomato',
    'Japanese Mini Tomato (20pc~25pc /pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452171',
    '2026-01-07T12:00:30.452173'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7e0b8dae-d306-4e3c-ac8f-08c4ae993880',
    'GGJ-AIR-VEG-0213',
    '米高蕃茄',
    '米高蕃茄',
    'Micro Tomato',
    'Micro Tomato (200g/pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452181',
    '2026-01-07T12:00:30.452183'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '141554dc-c493-44b2-a346-2910c2a28030',
    'GGJ-AIR-VEG-0214',
    '日本青瓜',
    '日本青瓜',
    'Kyuri',
    'Japanese Cucumber (100g~150g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452191',
    '2026-01-07T12:00:30.452193'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '2754c2ad-5593-4e70-b4f7-6bdeafb31614',
    'GGJ-AIR-VEG-0215',
    '苦瓜',
    '苦瓜',
    'GOYA',
    'Japanese Balsam pear (100g~150g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PC',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452201',
    '2026-01-07T12:00:30.452203'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '92178ee2-8a53-41ae-80fc-9fa121ab2860',
    'GGJ-AIR-VEG-0216',
    '南瓜',
    '南瓜',
    'Kabocha',
    'Japanese Pumpkin (1.5kg~2kg)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PC',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452212',
    '2026-01-07T12:00:30.452213'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e58dec8d-e10a-4bda-87ec-4fb7deefa108',
    'GGJ-AIR-VEG-0217',
    '洋蔥',
    '洋蔥',
    'Tamanegi',
    'Japanese Onion (200g~350g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452223',
    '2026-01-07T12:00:30.452225'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'afaac741-ec71-487e-94bd-8c27b23c6062',
    'GGJ-AIR-VEG-0218',
    '紅洋蔥',
    '紅洋蔥',
    'Aka Tamanegi',
    'Japanese Red Onion (150g~250g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452233',
    '2026-01-07T12:00:30.452235'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '07ae1698-828e-4faf-8ee5-16642e385133',
    'GGJ-AIR-VEG-0219',
    '蒜頭',
    '蒜頭',
    'Ninniku',
    'Japanese Garlic (1kg / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452243',
    '2026-01-07T12:00:30.452245'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '59403d96-04cc-47d4-a1a9-039adcd66b22',
    'GGJ-AIR-VEG-0220',
    '長蔥',
    '長蔥',
    'Naga Negi',
    'Japanese Weish Onion (3pc / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452253',
    '2026-01-07T12:00:30.452254'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '69ee9460-f4b3-4849-b86c-36d53b2375ca',
    'GGJ-AIR-VEG-0221',
    '下仁田蔥',
    '下仁田蔥',
    'Shimonita Negi',
    'Japanese Weish Onion (100~200g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452263',
    '2026-01-07T12:00:30.452265'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '546267ca-f84a-4ad8-9c47-660eb4006f49',
    'GGJ-AIR-VEG-0222',
    '九條蔥',
    '九條蔥',
    'Kujko Negi',
    'Japanese Spring Onion (100g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452273',
    '2026-01-07T12:00:30.452275'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'df92fe75-f499-40b0-8b82-59a0a53f5f0c',
    'GGJ-AIR-VEG-0223',
    '万能蔥',
    '万能蔥',
    'Bannou Negi',
    'Japanese Spring Onion (100g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452283',
    '2026-01-07T12:00:30.452285'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7d5df135-53fe-446a-b9b1-e16519b75763',
    'GGJ-AIR-VEG-0224',
    '芽蔥',
    '芽蔥',
    'Menegi',
    'Japanese Mini Chive (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452293',
    '2026-01-07T12:00:30.452294'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '624c6c4f-d402-4534-acae-65c5eb4f6420',
    'GGJ-AIR-VEG-0225',
    '包菜',
    '包菜',
    'LETTAUCE',
    'Japanese Lettuce (600g~800g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PC',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452303',
    '2026-01-07T12:00:30.452305'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3fcaeee5-4842-4527-ad8d-03977e6252e2',
    'GGJ-AIR-VEG-0226',
    '椰菜',
    '椰菜',
    'Kyapetsu',
    'Japanese Cabbage (600g~800g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PC',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452314',
    '2026-01-07T12:00:30.452315'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd45313c5-827b-4c7d-ab3a-f9c7601acfea',
    'GGJ-AIR-VEG-0227',
    '紅椰菜',
    '紅椰菜',
    'Aka Kyapetsu',
    'Japanese Red Cabbage (600g~800g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PC',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452325',
    '2026-01-07T12:00:30.452326'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '0b32e33b-476b-46aa-ab89-589073663c1d',
    'GGJ-AIR-VEG-0228',
    '春菊',
    '春菊',
    'Shun giku',
    'Garland Chrysanthemum (100g/pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452335',
    '2026-01-07T12:00:30.452336'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f9f88c04-2392-4c69-a2b1-5496f90b206e',
    'GGJ-AIR-VEG-0229',
    '生薑',
    '生薑',
    'Shouga',
    'Fresh Ginger (100~300g/pc)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452344',
    '2026-01-07T12:00:30.452346'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7490b237-d195-491b-8fe7-39ed93e7c621',
    'GGJ-AIR-VEG-0230',
    '日本蘿蔔',
    '日本蘿蔔',
    'Daikon',
    'Japanese Radish (1.2kg~1.5kg)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PC',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452354',
    '2026-01-07T12:00:30.452356'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '644d3b07-11c1-4b18-aab4-371c27a7e8ea',
    'GGJ-AIR-VEG-0231',
    '紅芯蘿蔔',
    '紅芯蘿蔔',
    'Koshindaikon',
    'Japanese Red Radish (300g~600g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PC',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452364',
    '2026-01-07T12:00:30.452366'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '61c08aaa-00ef-4f03-b00a-ea13a9200625',
    'GGJ-AIR-VEG-0232',
    '蕪菁 (1束3PC)',
    '蕪菁 (1束3PC)',
    'Kabu',
    'Japanese Turnip 3PC/Buddle',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'Buddle',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452374',
    '2026-01-07T12:00:30.452376'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7d4f8d1c-8923-409d-a6e0-8442d92b6d93',
    'GGJ-AIR-VEG-0233',
    '蕪菁 (1束5PC)',
    '蕪菁 (1束5PC)',
    'Kabu',
    'Japanese Turnip 5PC/Buddle',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'Buddle',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452385',
    '2026-01-07T12:00:30.452387'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c6984f5b-3ab6-48f9-8fb6-185e95126164',
    'GGJ-AIR-VEG-0234',
    '甘荀',
    '甘荀',
    'Ninjin',
    'Japanese Carrot (250g~300g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452395',
    '2026-01-07T12:00:30.452397'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '8a436a76-8ef6-44b8-810a-13c19b047c90',
    'GGJ-AIR-VEG-0235',
    '金時人參',
    '金時人參',
    'Kintokininjin',
    'Japanese Kyoto Carrot (200g~250g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PC',
    'WINTER-SPRING',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452409',
    '2026-01-07T12:00:30.452410'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '883368ab-96d9-4a07-a916-c084faf04678',
    'GGJ-AIR-VEG-0236',
    '牛蒡',
    '牛蒡',
    'Kobou',
    'Japanese Edible Burdock (200g~400g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452419',
    '2026-01-07T12:00:30.452420'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '8067b740-6f5b-4c48-a9b9-48ad3446f3a1',
    'GGJ-AIR-VEG-0237',
    '蕃薯',
    '蕃薯',
    'Satsumaimo',
    'Japanese Sweet Potato (300g~350g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452430',
    '2026-01-07T12:00:30.452432'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5733eb72-3053-4d32-917c-0468ef1a7ba9',
    'GGJ-AIR-VEG-0238',
    '大和芋',
    '大和芋',
    'Yamaimo',
    'Japanese Yam (0.8kg~1kg)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452440',
    '2026-01-07T12:00:30.452442'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'af4ba3fa-49ff-4c27-bb48-5d8613fa13cc',
    'GGJ-AIR-VEG-0239',
    '長芋',
    '長芋',
    'Nagaimo',
    'Japanese Chinese Yam (2kg~2.5kg)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452476',
    '2026-01-07T12:00:30.452478'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'fff3f011-d4ba-40ca-82a2-18d5a2f630ff',
    'GGJ-AIR-VEG-0240',
    '馬鈴薯',
    '馬鈴薯',
    'Jagaimo',
    'Japanese Potato (15g~20g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452487',
    '2026-01-07T12:00:30.452488'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '468ce200-6ba5-46e5-bee9-d5b574bc9e2c',
    'GGJ-AIR-VEG-0241',
    '蓮藕',
    '蓮藕',
    'Renkon',
    'Japanese Lotus Root (800g~1kg)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452497',
    '2026-01-07T12:00:30.452498'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9e90e955-5653-4a11-9ff0-da0e27ecfcc6',
    'GGJ-AIR-VEG-0242',
    '日產竹筍',
    '日產竹筍',
    'Japan Takenoko',
    'Japanese Bamboo Shoots (200g/PC)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'JAN-MAY',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452508',
    '2026-01-07T12:00:30.452509'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '79ec4378-ef16-4d84-880d-81910afacd87',
    'GGJ-AIR-VEG-0243',
    '青椒仔',
    '青椒仔',
    'Shishitou',
    'Japanese Green Pepper Short (30pc / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452518',
    '2026-01-07T12:00:30.452519'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '93555da7-6319-422c-a040-c6aba89da605',
    'GGJ-AIR-VEG-0244',
    '青圓椒',
    '青圓椒',
    'Piman',
    'Sweet Bell pepper (4~5pc/pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452528',
    '2026-01-07T12:00:30.452529'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b72f12cd-ec37-4391-bbaa-7411cfb421e7',
    'GGJ-AIR-VEG-0245',
    '万願寺唐辛子',
    '万願寺唐辛子',
    'Manganji Tougarashi',
    'Japanese Green Pepper Long (5-60g)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452538',
    '2026-01-07T12:00:30.452539'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'fd4adb9d-b45c-43a7-944b-8ee6818091f6',
    'GGJ-AIR-VEG-0246',
    '空豆',
    '空豆',
    'Soramame',
    'Japanese Broad Bean',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'KG',
    'SPRING-SUMMER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452548',
    '2026-01-07T12:00:30.452549'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '09a5b393-1bed-499f-bc53-112f34e0585c',
    'GGJ-AIR-VEG-0247',
    '貝割',
    '貝割',
    'Kaiware',
    'Japanese Sprouts (50g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452558',
    '2026-01-07T12:00:30.452560'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'bcd47481-6bd6-4bd8-a99b-9e6dcd2f91e2',
    'GGJ-AIR-VEG-0248',
    '銀杏 (殼付)',
    '銀杏 (殼付)',
    'GINNAN',
    'Japanese GINNAN (500/pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'AUG-FEB',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452569',
    '2026-01-07T12:00:30.452571'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a4e523ad-cab8-4dc7-b360-63128e5ee70f',
    'GGJ-AIR-VEG-0249',
    '菠菜',
    '菠菜',
    'Hourenso',
    'Japanese Spinach (150g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452579',
    '2026-01-07T12:00:30.452580'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7407486f-a2ba-485f-8dc9-266b145d8d4d',
    'GGJ-AIR-VEG-0250',
    '小松菜',
    '小松菜',
    'Komatsuna',
    'Japanese Saltgreen (150g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452590',
    '2026-01-07T12:00:30.452591'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4d8a86ec-797c-4953-b5f4-d46ef26f6ad9',
    'GGJ-AIR-VEG-0251',
    '冬菇',
    '冬菇',
    'Shiitake',
    'Japanese Mushroom (6~8pc / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452600',
    '2026-01-07T12:00:30.452601'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '63400b01-bf06-4d31-a7c7-436727366205',
    'GGJ-AIR-VEG-0252',
    '本占地',
    '本占地',
    'Honshimeji',
    'Japanese Mini Mushroom (100g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452609',
    '2026-01-07T12:00:30.452611'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1c9cad31-89a8-4ca1-8791-76f2f7ec0c5f',
    'GGJ-AIR-VEG-0253',
    '白本占地',
    '白本占地',
    'White Shimeji',
    'Japanese Mini White Mushroom (100g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452620',
    '2026-01-07T12:00:30.452621'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '88837cdf-759d-4da6-ab07-475dbd13c8ab',
    'GGJ-AIR-VEG-0254',
    '金菇',
    '金菇',
    'Enokitake',
    'Japanese Golden mushroom (100g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452630',
    '2026-01-07T12:00:30.452632'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '497b2815-5db4-4b75-8170-b32aff0fbac5',
    'GGJ-AIR-VEG-0255',
    '黃金菇',
    '黃金菇',
    'Yellow Enoki',
    'Japanese Golden Velvet-Stemmed Araric (100g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'SUMMER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452641',
    '2026-01-07T12:00:30.452642'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7e5a1609-eee8-4e5a-95f4-9c38ad078cd2',
    'GGJ-AIR-VEG-0256',
    '直菇',
    '直菇',
    'Eringi',
    'Japanese King Trumpet Mushroom (100g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'SPRING-SUMMER',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452651',
    '2026-01-07T12:00:30.452653'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c2c55022-5e81-4274-993d-9e9d0f9384ed',
    'GGJ-AIR-VEG-0257',
    '舞茸',
    '舞茸',
    'Maitake',
    'Japanese Hen Of The Woods (100g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452663',
    '2026-01-07T12:00:30.452665'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '581c8b77-1a2a-4328-9acc-5b590da93905',
    'GGJ-AIR-VEG-0258',
    '白舞茸',
    '白舞茸',
    'Shiro Maitake',
    'Japanese White Hen Of The Woods (100g / pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452674',
    '2026-01-07T12:00:30.452675'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '243c49d9-682f-49b7-b38f-dcc60f2b873c',
    'GGJ-AIR-VEG-0259',
    '獨活',
    '獨活',
    'Yama Udo',
    'Doubleteeth Angelicae Root',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PC',
    'NOV-MAY',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452685',
    '2026-01-07T12:00:30.452687'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '83fca94f-0333-47ed-9188-48b42ed32c72',
    'GGJ-AIR-VEG-0260',
    '楤木芽',
    '楤木芽',
    'Taranome',
    'Taranome (100g/pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'DEC-JUN',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452695',
    '2026-01-07T12:00:30.452697'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'fd43b249-253b-46db-bd3b-7861401e9009',
    'GGJ-AIR-VEG-0261',
    '露筍（緑色）PK',
    '露筍（緑色）PK',
    'Asuparagasu',
    'Asparagus Green (3pc/pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'ALL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452705',
    '2026-01-07T12:00:30.452707'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1d7a18da-63cc-4a79-af19-de76e7de134e',
    'GGJ-AIR-VEG-0262',
    '日本蒜葉',
    '日本蒜葉',
    'Gyojya Ninniku',
    'Japanese Ainu Negi (100g/pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'SPRING',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452715',
    '2026-01-07T12:00:30.452717'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '879962e2-464e-42c2-aa08-698cbde2debe',
    'GGJ-AIR-VEG-0263',
    '蕨菜',
    '蕨菜',
    'Warabi',
    'Wild brake (Box)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'BOX',
    'FEB-JUNE',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452726',
    '2026-01-07T12:00:30.452727'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '914c9c3d-479a-40ce-9deb-4bb4dabbe18f',
    'GGJ-AIR-VEG-0264',
    '草蘇鐵',
    '草蘇鐵',
    'Kogomi',
    'Sago palm Leaf (100g/pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'FEB-JUNE',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452736',
    '2026-01-07T12:00:30.452737'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'cbb4942e-9c9f-4b7d-a0c3-a4d6ebde50b4',
    'GGJ-AIR-VEG-0265',
    '平茸',
    '平茸',
    'Hirakake',
    'Oyster Mushroom (100g/pk)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'PK',
    'OCT-APRIL',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452746',
    '2026-01-07T12:00:30.452747'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '25056a39-3a48-4e2a-844e-79c8249a9609',
    'GGJ-AIR-VEG-0266',
    '蓴菜 (支装)',
    '蓴菜 (支装)',
    'Junsai',
    'Watershield Leaf (Btl)',
    '飛機貨(鮮活) > 野菜/果物',
    '飛機貨(鮮活)',
    '野菜/果物',
    'BTL',
    'APRIL-DEC',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452756',
    '2026-01-07T12:00:30.452757'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '8d4dc2a6-9d67-4d06-a73b-76df25ef4edd',
    'GGJ-20030033',
    '東海沢庵(L)',
    '東海沢庵(L)',
    'TAKUAN',
    'Radish pickle (~450g)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452766',
    '2026-01-07T12:00:30.452768'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '478a2881-b939-496e-93a2-1fa129c88dc7',
    'GGJ-20030023',
    '千本漬',
    '千本漬',
    'SENBONZUKE',
    'Radish pickle (~160g)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452780',
    '2026-01-07T12:00:30.452782'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'dc87e89e-516f-4817-9a89-988295a4831c',
    'GGJ-20030056',
    '甘酢姜',
    '甘酢姜',
    NULL,
    'Sushi ginger (1.5kg)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452789',
    '2026-01-07T12:00:30.452791'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4b0d84e6-7710-4a0a-b7dd-c7273fb504e6',
    'GGJ-20030056',
    '寿司姜（粉紅）',
    '寿司姜（粉紅）',
    NULL,
    'Sushi ginger pink (1.5kg)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452799',
    '2026-01-07T12:00:30.452800'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd1d1ad86-3d3e-411b-938d-c0010edff8a5',
    'GGJ-20030025',
    '芝漬／柴漬',
    '芝漬／柴漬',
    'SHIBAZUKE',
    'Red shiso pickle (2kg)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452808',
    '2026-01-07T12:00:30.452809'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '38244752-c578-4a91-a14d-b4dd8d1de7ec',
    'GGJ-20030016',
    '青瓜漬',
    '青瓜漬',
    NULL,
    'Cucumber pickle (2kg)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452816',
    '2026-01-07T12:00:30.452818'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '11fa112a-45b4-4410-bc9b-c4ebfbe69b2e',
    'GGJ-20030038',
    '柚子大根漬',
    '柚子大根漬',
    NULL,
    'Yuzu radish pickle (1kg)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452825',
    '2026-01-07T12:00:30.452827'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '32290e1a-6d91-488a-be9c-e3efaa7f0202',
    'GGJ-20030028',
    '高菜漬',
    '高菜漬',
    'TAKANAZUKE',
    'Leaf mustard pickle (1kg)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452834',
    '2026-01-07T12:00:30.452836'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '859f6844-808d-469b-ad22-2203a039e33e',
    'GGJ-20030014',
    '黃蘿蔔漬 (切碎)',
    '黃蘿蔔漬 (切碎)',
    'KIZAMITAKUANZUKE',
    'Radish pickle cut (1kg)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452843',
    '2026-01-07T12:00:30.452844'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '839d1c72-4cc8-49d1-b1ae-e2e7a3e94454',
    'GGJ-40070059',
    '山葵醤油漬（金印）',
    '山葵醤油漬（金印）',
    NULL,
    'Wasabi pickle w/ soy sauce (250g)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452852',
    '2026-01-07T12:00:30.452854'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e88b1580-47bf-4e59-ad70-e8c4ebf15b15',
    'GGJ-20030020',
    '白菜淺漬',
    '白菜淺漬',
    'HAKUSAIASAZUKE',
    'Chinese cabbage light pickle (1kg)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452861',
    '2026-01-07T12:00:30.452863'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b53639e1-26ca-4a34-95d6-da8895940c87',
    'GGJ-20030003',
    '甜酸喬頭漬',
    '甜酸喬頭漬',
    'AMARAKKYOU',
    'Sweet and sour shallot pickle (1kg)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452870',
    '2026-01-07T12:00:30.452871'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'eef58b43-90d3-4ce0-9947-86c8f3ec6e76',
    'GGJ-20030072',
    '味噌木魚粉蒜肉',
    '味噌木魚粉蒜肉',
    'MISO KATSUO NINNIKU',
    'Garlic pickle in miso/bonito flakes (1kg)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452879',
    '2026-01-07T12:00:30.452880'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b5115489-6fda-4929-a8fc-d7bb60c8266c',
    'GGJ-20030042',
    '山葵漬 (金印)',
    '山葵漬 (金印)',
    NULL,
    'Wasabi pickle (250g)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452888',
    '2026-01-07T12:00:30.452890'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '18ec67ba-690a-43b6-952a-002344460474',
    'GGJ-20030001',
    '紅蕪漬',
    '紅蕪漬',
    'AKAKABUZUKE',
    'Red turnip pickle (500g)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452897',
    '2026-01-07T12:00:30.452898'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'ffc4b6a4-2d57-4153-8589-9bcc8da30fa2',
    'GGJ-20030041',
    '長芋山葵漬',
    '長芋山葵漬',
    'NAGAIMOWASABIZUKE',
    'Chinese yam & wasabi pickle (500g)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452906',
    '2026-01-07T12:00:30.452907'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '33a3315c-ca42-4df3-9389-a78249a668ee',
    'GGJ-20030051',
    '沙律薑',
    '沙律薑',
    NULL,
    'Salad ginger (1kg)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452914',
    '2026-01-07T12:00:30.452916'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e0dbf8ab-d55b-4492-bda9-96678c0eaeb9',
    'GGJ-20030040',
    '牛蒡醬油漬',
    '牛蒡醬油漬',
    'GOBOSHOYUZUKE',
    'Burdock pickle (1kg)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452923',
    '2026-01-07T12:00:30.452924'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3b4296f4-0bed-4c0a-bb01-96f53cddc4da',
    'GGJ-20030037',
    '紅酒蕎頭漬',
    '紅酒蕎頭漬',
    'WAINRAKKYOU',
    'Wine shallot pickle (500g)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452931',
    '2026-01-07T12:00:30.452933'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '8669bb71-6c17-474c-8ab4-090b9da19d9a',
    'GGJ-20030018',
    '味噌木魚粉蒜肉漬',
    '味噌木魚粉蒜肉漬',
    'NINNIKUMORIMORIZUKE',
    'Garlic soy sauce pickle (1kg)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452940',
    '2026-01-07T12:00:30.452942'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '225bf11c-0547-4808-99a1-350a9b72f852',
    'GGJ-20030005',
    '皮付甜蘿蔔漬',
    '皮付甜蘿蔔漬',
    'BETTARAZUKE',
    'White radish pickle in malted rice (1kg)',
    '乾貨/調味 > 漬物',
    '乾貨/調味',
    '漬物',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452949',
    '2026-01-07T12:00:30.452951'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '872fd19b-0dbd-4fe1-a672-febf95c3d86f',
    'GGJ-30030012',
    '長州鶏皮',
    '長州鶏皮',
    'KAWA',
    'Chicken Skin (2kg)',
    '急凍/冷藏 > 肉類',
    '急凍/冷藏',
    '肉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452958',
    '2026-01-07T12:00:30.452959'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f8d0adf4-0b3f-4bf0-b3a3-8904a5e43004',
    'GGJ-30030014',
    '長州鶏胸',
    '長州鶏胸',
    'MUNE',
    'Chicken Chest (2kg)',
    '急凍/冷藏 > 肉類',
    '急凍/冷藏',
    '肉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452966',
    '2026-01-07T12:00:30.452968'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e9f72584-af0f-4fa3-882c-bc19ddd27b26',
    'GGJ-30030010',
    '長州鶏肝',
    '長州鶏肝',
    'KIMO',
    'Chicken Liver (2kg)',
    '急凍/冷藏 > 肉類',
    '急凍/冷藏',
    '肉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452975',
    '2026-01-07T12:00:30.452976'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5ee12e9b-f11c-482e-a805-bec771a5e95d',
    'GGJ-30030007',
    '長州鶏心',
    '長州鶏心',
    'HATSU',
    'Chicken Heart (2kg)',
    '急凍/冷藏 > 肉類',
    '急凍/冷藏',
    '肉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452983',
    '2026-01-07T12:00:30.452985'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '03705f6e-06c3-449d-a936-1781ef9c8e66',
    'GGJ-30030017',
    '長州鶏槌',
    '長州鶏槌',
    'TEBAMOTO',
    'Chicken Wing stick (2kg)',
    '急凍/冷藏 > 肉類',
    '急凍/冷藏',
    '肉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.452992',
    '2026-01-07T12:00:30.452994'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd9be3eb5-179d-4b9c-9960-b16256b1175c',
    'GGJ-30030016',
    '長州鶏腎',
    '長州鶏腎',
    'SUNAGIMO',
    'Chicken Gizzard (2kg)',
    '急凍/冷藏 > 肉類',
    '急凍/冷藏',
    '肉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453001',
    '2026-01-07T12:00:30.453002'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '8fa0e35a-c5b2-489e-8cf2-092b627cd258',
    'GGJ-30030015',
    '長州鶏柳',
    '長州鶏柳',
    'SASAMI',
    'Chicken Fillet (2kg)',
    '急凍/冷藏 > 肉類',
    '急凍/冷藏',
    '肉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453009',
    '2026-01-07T12:00:30.453011'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '870245fe-2636-4dc2-9f1c-3b5f66eb4b1f',
    'GGJ-30030018',
    '長州鶏翼',
    '長州鶏翼',
    'TEBASAKI',
    'Chicken Wing (2kg)',
    '急凍/冷藏 > 肉類',
    '急凍/冷藏',
    '肉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453018',
    '2026-01-07T12:00:30.453020'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'db8e99ce-4c95-442a-9c8c-178d53c78b7e',
    'GGJ-30030011',
    '長州鶏頸肉',
    '長州鶏頸肉',
    'SESERI',
    'Chicken Neck meat (2kg)',
    '急凍/冷藏 > 肉類',
    '急凍/冷藏',
    '肉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453027',
    '2026-01-07T12:00:30.453028'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f914ad5c-d227-42cc-9335-f8a5c3e699d9',
    'GGJ-30030013',
    '長州鶏腿肉',
    '長州鶏腿肉',
    'MOMO',
    'Chicken Thigh (2kg)',
    '急凍/冷藏 > 肉類',
    '急凍/冷藏',
    '肉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453036',
    '2026-01-07T12:00:30.453037'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'edda228c-9eac-42d1-9e9c-9c470dccc5c9',
    'GGJ-FRZ-MET-0298',
    '鶏堤燈 (連腸)',
    '鶏堤燈 (連腸)',
    NULL,
    'Chicken Chochin (2kg)',
    '急凍/冷藏 > 肉類',
    '急凍/冷藏',
    '肉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453046',
    '2026-01-07T12:00:30.453048'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'bdddf4c8-d9bd-4abf-ab6f-b44dfdc831f1',
    'GGJ-30030006',
    '長州鶏尾',
    '長州鶏尾',
    'BONJIRI',
    'Chicken Tail (2kg)',
    '急凍/冷藏 > 肉類',
    '急凍/冷藏',
    '肉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453056',
    '2026-01-07T12:00:30.453057'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f8f97e29-5cf5-4302-9ba4-586f55082dd0',
    'GGJ-30050017',
    '粗挽香腸 (~20pc)',
    '粗挽香腸 (~20pc)',
    NULL,
    'Miyazaki coarsely ground sausage (~500g)',
    '急凍/冷藏 > 肉類',
    '急凍/冷藏',
    '肉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453065',
    '2026-01-07T12:00:30.453066'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3f30e40c-7efe-4b28-8055-bd6caaf9b59d',
    'GGJ-30020001',
    '北海道豬腩',
    '北海道豬腩',
    NULL,
    'Miyazaki pork belly (4~6kg)',
    '急凍/冷藏 > 肉類',
    '急凍/冷藏',
    '肉類',
    'KG',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453074',
    '2026-01-07T12:00:30.453075'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '49fc2056-b56a-4475-af56-526c9f599e19',
    'GGJ-30020002',
    '北海道豬扒',
    '北海道豬扒',
    NULL,
    'Miyazaki pork striploin (4~5kg)',
    '急凍/冷藏 > 肉類',
    '急凍/冷藏',
    '肉類',
    'KG',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453082',
    '2026-01-07T12:00:30.453084'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c4c3c9a0-edd0-4d70-99ee-8e10dd35b86c',
    'GGJ-30040004',
    '白蛋（Ｍ）',
    '白蛋（Ｍ）',
    NULL,
    'White egg (10pc/pk)',
    '急凍/冷藏 > 蛋奶類',
    '急凍/冷藏',
    '蛋奶類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453091',
    '2026-01-07T12:00:30.453093'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '10e75076-838f-4537-b569-a1a358ccb9a8',
    'GGJ-30040004',
    '白蛋（L）',
    '白蛋（L）',
    NULL,
    'White egg (10pc/pk)',
    '急凍/冷藏 > 蛋奶類',
    '急凍/冷藏',
    '蛋奶類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453100',
    '2026-01-07T12:00:30.453101'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1c7251a7-3b85-43bf-b243-0e06435d878d',
    'GGJ-30040002',
    '太陽蛋',
    '太陽蛋',
    NULL,
    'TAIYOU EGG (10pc/pk)',
    '急凍/冷藏 > 蛋奶類',
    '急凍/冷藏',
    '蛋奶類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453109',
    '2026-01-07T12:00:30.453110'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '44a50244-774d-4878-b8df-781cc60d99e6',
    'GGJ-30040014',
    '溫泉蛋',
    '溫泉蛋',
    NULL,
    'Hot spring egg (180pc)',
    '急凍/冷藏 > 蛋奶類',
    '急凍/冷藏',
    '蛋奶類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453117',
    '2026-01-07T12:00:30.453119'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b4016ab9-905f-4c52-bc9a-da2562c5124b',
    'GGJ-30050004',
    '寿司蛋',
    '寿司蛋',
    NULL,
    'Cooked sushi egg block (500g)',
    '急凍/冷藏 > 蛋奶類',
    '急凍/冷藏',
    '蛋奶類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453126',
    '2026-01-07T12:00:30.453128'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7ce162bb-3993-45d0-8901-f30df177c8a0',
    'GGJ-30050006',
    '有塩牛油',
    '有塩牛油',
    NULL,
    'Salted butter (225g)',
    '急凍/冷藏 > 蛋奶類',
    '急凍/冷藏',
    '蛋奶類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453135',
    '2026-01-07T12:00:30.453136'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '61c50cf7-f36a-4f18-9803-c594ce42232c',
    'GGJ-30040001',
    '北海道3.6牛乳',
    '北海道3.6牛乳',
    NULL,
    'Hokkaido milk (1L)',
    '急凍/冷藏 > 蛋奶類',
    '急凍/冷藏',
    '蛋奶類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453144',
    '2026-01-07T12:00:30.453146'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a6108474-0e8e-460c-9037-0b30eae4b7ad',
    'GGJ-40030001',
    '甜蝦2L (50-70pc)',
    '甜蝦2L (50-70pc)',
    NULL,
    'Sweet shrimp 2L (1kg)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453153',
    '2026-01-07T12:00:30.453155'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '68f5b545-3bd0-47f2-b6b2-68a8d238ddfa',
    'GGJ-40030002',
    '甜蝦3L (40-50pc)',
    '甜蝦3L (40-50pc)',
    NULL,
    'Sweet shrimp 3L (1kg)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453163',
    '2026-01-07T12:00:30.453165'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7c8b5399-bcd3-44f7-9349-8a5357702106',
    'GGJ-40030002',
    '甜蝦4L (40-50pc)',
    '甜蝦4L (40-50pc)',
    NULL,
    'Sweet shrimp 4L (1kg)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453172',
    '2026-01-07T12:00:30.453173'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '02c27f6a-2694-41dd-8599-c70fe76212e5',
    'GGJ-40030025',
    '無頭去殼甜蝦',
    '無頭去殼甜蝦',
    NULL,
    'Sweet shrimp w/o head (50pc)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453181',
    '2026-01-07T12:00:30.453182'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '064e9c71-1201-41e2-84d9-cadcce9cb737',
    'GGJ-40030009',
    '牡丹蝦L (25-29pc)',
    '牡丹蝦L (25-29pc)',
    NULL,
    'Botan shrimp L (1kg)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453190',
    '2026-01-07T12:00:30.453191'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'bdc339e5-b920-409f-b1b1-efc045d5572b',
    'GGJ-40030010',
    '牡丹蝦XL (20-24pc)',
    '牡丹蝦XL (20-24pc)',
    NULL,
    'Botan shrimp XL (1kg)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453198',
    '2026-01-07T12:00:30.453200'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5c983749-bc8c-440f-9e8b-5111a2721116',
    'GGJ-40030013',
    '牡丹蝦J (15-19pc)',
    '牡丹蝦J (15-19pc)',
    NULL,
    'Botan shrimp J (1kg)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453207',
    '2026-01-07T12:00:30.453208'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1b8e73b2-43ad-4604-a388-8b743533d9cd',
    'GGJ-40030012',
    '牡丹蝦XJ (10-14pc)',
    '牡丹蝦XJ (10-14pc)',
    NULL,
    'Botan shrimp XJ (1kg)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453217',
    '2026-01-07T12:00:30.453218'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '2e4139c9-9e31-4b72-b555-04893f92a1b6',
    'GGJ-40030014',
    '俄羅斯牡丹蝦 (8~10pc)',
    '俄羅斯牡丹蝦 (8~10pc)',
    NULL,
    'Botan shrimp Russia (500G)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453225',
    '2026-01-07T12:00:30.453227'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7c476e94-52b7-40bf-a4a2-260560450884',
    'GGJ-40070052',
    '黄糠麵包炸虎蝦（10pc）',
    '黄糠麵包炸虎蝦（10pc）',
    NULL,
    'Fried tiger shrimp w/yellow crumb (250g)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453234',
    '2026-01-07T12:00:30.453236'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'df643c99-36f5-4a4b-a4c3-e2be3bbda4d1',
    'GGJ-40030028',
    '天婦羅蝦（21-25pc）',
    '天婦羅蝦（21-25pc）',
    NULL,
    'Tenpura shrimp (21-25pc)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453243',
    '2026-01-07T12:00:30.453245'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '62d58f90-90bb-48d5-8c5f-6c6e7a917f87',
    'GGJ-40030027',
    '天婦羅蝦（16-20pc）',
    '天婦羅蝦（16-20pc）',
    NULL,
    'Tenpura shrimp (16-20pc)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453253',
    '2026-01-07T12:00:30.453254'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4add773f-1672-4eef-8516-6918586cfd4a',
    'GGJ-40030006',
    '去頭虎蝦（16-20pc）',
    '去頭虎蝦（16-20pc）',
    NULL,
    'Headless black tiger shrimp (1.8kg)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453281',
    '2026-01-07T12:00:30.453283'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'aa2c0719-c971-42fc-8e27-9ab594c53a6e',
    'GGJ-40030018',
    '大崎蟹柳',
    '大崎蟹柳',
    'KANI KAMABOKO',
    'Imitation crab meat stick (500g)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453290',
    '2026-01-07T12:00:30.453292'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'cc81a70c-00d4-48f4-846c-a52a95bb7980',
    'GGJ-40030032',
    '軟殼蟹',
    '軟殼蟹',
    NULL,
    'Soft shell crab (1kg)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453299',
    '2026-01-07T12:00:30.453300'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'ca465e9c-e3e7-45c1-9c35-8b8c6ed6f102',
    'GGJ-40030125',
    '松葉蟹肉碎',
    '松葉蟹肉碎',
    NULL,
    'Zuwai crab meat flake (300g)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453308',
    '2026-01-07T12:00:30.453309'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '0c03e9f5-ec9b-411e-8e67-d6799fdb6620',
    'GGJ-40030075',
    '急凍松葉蟹肉混合裝',
    '急凍松葉蟹肉混合裝',
    NULL,
    'Zuwai crab mix flake (1kg)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453316',
    '2026-01-07T12:00:30.453318'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f27db9c7-ff80-42d0-a83c-9622cc7b919e',
    'GGJ-40030041',
    '熟鱈場蟹腳5L',
    '熟鱈場蟹腳5L',
    NULL,
    'King crab leg w/ shoulder (1~1.2kg)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453326',
    '2026-01-07T12:00:30.453328'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'bd94e062-c4b8-4a22-b624-3ef4a83c583e',
    'GGJ-40030041',
    '熟鱈場蟹腳4L',
    '熟鱈場蟹腳4L',
    NULL,
    'Boiled King crab leg w/ shoulder (1kg)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453335',
    '2026-01-07T12:00:30.453336'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f32575ee-adc4-46a8-808f-ece8201fb364',
    'GGJ-40030142',
    '松葉蟹鉗 (26~30pc)',
    '松葉蟹鉗 (26~30pc)',
    NULL,
    'Zuwai crab claw (1kg)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453343',
    '2026-01-07T12:00:30.453345'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '39841dcd-698a-420f-9470-b72b432f1efa',
    'GGJ-40030020',
    '松葉蟹棒肉 2L (40-50pc)',
    '松葉蟹棒肉 2L (40-50pc)',
    NULL,
    'Zuwai crab meat stick 2L (1kg)',
    '急凍/冷藏 > 海產(蝦蟹)',
    '急凍/冷藏',
    '海產(蝦蟹)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453352',
    '2026-01-07T12:00:30.453354'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'cf46baaa-a635-4392-a72b-decb1b27f8ac',
    'GGJ-40020006',
    '刺身帶子肉2S (36-40pc)',
    '刺身帶子肉2S (36-40pc)',
    NULL,
    'Scallop meat 2S (1kg)',
    '急凍/冷藏 > 海產(帶子/貝)',
    '急凍/冷藏',
    '海產(帶子/貝)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453361',
    '2026-01-07T12:00:30.453363'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f5e81c10-e38f-4d8a-94e8-d169112c61b7',
    'GGJ-40020005',
    '刺身帶子肉S (31-35pc)',
    '刺身帶子肉S (31-35pc)',
    NULL,
    'Scallop meat S (1kg)',
    '急凍/冷藏 > 海產(帶子/貝)',
    '急凍/冷藏',
    '海產(帶子/貝)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453370',
    '2026-01-07T12:00:30.453371'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '39a5a988-ce51-4a3c-b4d8-9e5ba6658afe',
    'GGJ-40020004',
    '刺身帶子肉M (26-30pc)',
    '刺身帶子肉M (26-30pc)',
    NULL,
    'Scallop meat M (1kg)',
    '急凍/冷藏 > 海產(帶子/貝)',
    '急凍/冷藏',
    '海產(帶子/貝)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453378',
    '2026-01-07T12:00:30.453380'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '67cd4b18-72d6-4756-b31c-e91a0eefa6cb',
    'GGJ-40020003',
    '刺身帶子肉L (21-25pc)',
    '刺身帶子肉L (21-25pc)',
    NULL,
    'Scallop meat L (1kg)',
    '急凍/冷藏 > 海產(帶子/貝)',
    '急凍/冷藏',
    '海產(帶子/貝)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453395',
    '2026-01-07T12:00:30.453396'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'cc58d78a-3040-4393-9372-953ce1479ec2',
    'GGJ-40020002',
    '刺身帶子肉2L (16-20pc)',
    '刺身帶子肉2L (16-20pc)',
    NULL,
    'Scallop meat 2L (1kg)',
    '急凍/冷藏 > 海產(帶子/貝)',
    '急凍/冷藏',
    '海產(帶子/貝)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453404',
    '2026-01-07T12:00:30.453405'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3d31d8c4-6cba-4ce7-92ec-8bc4239a740e',
    'GGJ-40020011',
    '北寄貝片',
    '北寄貝片',
    NULL,
    'Surf clam slice (30pc)',
    '急凍/冷藏 > 海產(帶子/貝)',
    '急凍/冷藏',
    '海產(帶子/貝)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453414',
    '2026-01-07T12:00:30.453415'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '11357cff-6acc-4762-8f5a-b7a695d8d85f',
    'GGJ-40020009',
    '北寄貝L',
    '北寄貝L',
    NULL,
    'Surf clam L (1kg)',
    '急凍/冷藏 > 海產(帶子/貝)',
    '急凍/冷藏',
    '海產(帶子/貝)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453423',
    '2026-01-07T12:00:30.453425'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c2a33f4c-e2cf-4701-9b84-a774594f01aa',
    'GGJ-40040008',
    '橙色飛魚子',
    '橙色飛魚子',
    NULL,
    'Flying fish roe orange (500g)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453432',
    '2026-01-07T12:00:30.453434'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1761c202-9f89-4938-85bf-fd7df8b9d708',
    'GGJ-40040024',
    '金色飛魚子',
    '金色飛魚子',
    NULL,
    'Flying fish roe gold (500g)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453442',
    '2026-01-07T12:00:30.453443'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'cbb019b7-086b-4e42-98f5-7a1f0a7569c3',
    'GGJ-FRZ-XXX-0340',
    '黑色飛魚子',
    '黑色飛魚子',
    NULL,
    'Flying fish roe black (1kg)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453452',
    '2026-01-07T12:00:30.453454'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'eb2711a8-9109-4f2b-8c5e-00d65c97e701',
    'GGJ-40040025',
    '芥辣飛魚子',
    '芥辣飛魚子',
    NULL,
    'Flying fish roe wasabi (500g)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453462',
    '2026-01-07T12:00:30.453463'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '732df402-4acd-466b-a0f4-42bab97afeee',
    'GGJ-40040002',
    '三文魚籽醬油漬',
    '三文魚籽醬油漬',
    NULL,
    'Salmon roe soy sauce (500g)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453470',
    '2026-01-07T12:00:30.453472'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '87bddc1f-c754-40db-8d95-16126214d831',
    'GGJ-40040001',
    '三文魚籽（三特）',
    '三文魚籽（三特）',
    NULL,
    'Salmon roe premium (1kg)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453479',
    '2026-01-07T12:00:30.453481'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c2876dfe-368b-4eeb-b383-548479111027',
    'GGJ-10010038',
    '目撥呑拿赤身',
    '目撥呑拿赤身',
    'BACHI MAGURO AKAMI',
    'Bigeye tuna red meat',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'KG',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453489',
    '2026-01-07T12:00:30.453491'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '61956aa2-6611-46a2-b3da-3574a6774f87',
    'GGJ-10010006',
    '吞拿魚赤身',
    '吞拿魚赤身',
    'HON MAGURO AKAMI',
    'Tuna red meat',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'KG',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453498',
    '2026-01-07T12:00:30.453500'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd589d72b-348b-475f-adf0-b3b2988576a8',
    'GGJ-10010007',
    '吞拿魚大拖羅',
    '吞拿魚大拖羅',
    'HON MAGURO O TORO',
    'Tuna belly',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'KG',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453507',
    '2026-01-07T12:00:30.453508'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a4d3f49a-3c74-4059-af30-193bead42636',
    'GGJ-10010046',
    '吞拿魚腩碎',
    '吞拿魚腩碎',
    'NEGI TORO',
    'Tuna minced with spring onion (500g)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453516',
    '2026-01-07T12:00:30.453518'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '6817be13-8e54-4f39-972a-d84f478627df',
    'GGJ-40010023',
    '多春魚',
    '多春魚',
    NULL,
    'Smelt',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453525',
    '2026-01-07T12:00:30.453526'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7b90eba3-8206-4225-8e61-f91dc4019dc8',
    'GGJ-40010062',
    '銀魚 (白色、濕身)',
    '銀魚 (白色、濕身)',
    'SHIRASU',
    'Sliver fish (50g)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453534',
    '2026-01-07T12:00:30.453535'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '14e957e7-2211-43a5-8e27-4564629f1ece',
    'GGJ-40010084',
    '希靈魚片',
    '希靈魚片',
    'NISHIN',
    'Herring fillet (170g)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453542',
    '2026-01-07T12:00:30.453544'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd4913cc7-0d47-4014-88cd-7d2b9f5dd8c6',
    'GGJ-40010015',
    '沙鎚開邊',
    '沙鎚開邊',
    'KISU',
    'Sillago cut open (25pc)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453551',
    '2026-01-07T12:00:30.453553'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '0c293f8c-da64-492a-95ff-ecb242a8d67b',
    'GGJ-40010019',
    '煮穴子 ５本',
    '煮穴子 ５本',
    'NI ANAGO',
    'Conger eel cooked (250g)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453561',
    '2026-01-07T12:00:30.453562'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'fc34503a-11ea-4e2c-b7ee-853804b9e6be',
    'GGJ-40010013',
    '炭焼鰹魚',
    '炭焼鰹魚',
    'KATSUO TATAKI',
    'Roasted bonito (300~500g)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453569',
    '2026-01-07T12:00:30.453571'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '35aafc79-cca0-4940-8e00-44e350ea8a8e',
    'GGJ-40010025',
    '魚肉生身',
    '魚肉生身',
    'SURIMI',
    'Ground fish paste (500g)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453578',
    '2026-01-07T12:00:30.453580'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '326e2510-22d2-4f25-9e19-878226fa4089',
    'GGJ-40010058',
    '油甘魚骹',
    '油甘魚骹',
    'HAMACHI KAMA',
    'Young yellowtail collar (1.2~1.5kg)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453588',
    '2026-01-07T12:00:30.453590'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '08471efd-6321-4735-9604-feee0c6eb9eb',
    'GGJ-10010043',
    '急凍劍魚腩',
    '急凍劍魚腩',
    'KAJIKI',
    'Frozen Swordfish (2~3kg)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'KG',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453597',
    '2026-01-07T12:00:30.453598'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b155f1ca-9944-40c7-a36b-a30f237d396e',
    'GGJ-40010007',
    '急凍銀鱈魚',
    '急凍銀鱈魚',
    'GIN DARA',
    'Frozen Cod fish (2-2.5kg)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'KG',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453607',
    '2026-01-07T12:00:30.453608'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3336cd37-c74a-483b-95d1-d4d9466cbdf4',
    'GGJ-60120077',
    '小女子',
    '小女子',
    'KONAGO',
    'Young sand lance cooked (2kg)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453615',
    '2026-01-07T12:00:30.453617'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd98d274b-83b1-4198-a47a-2d8c5d34ccba',
    'GGJ-40010045',
    '右口裙邊',
    '右口裙邊',
    'ENGAWA',
    'Olive flounder edge (500g)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453624',
    '2026-01-07T12:00:30.453629'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '28b178a1-e5d9-437f-8279-06241b53d2a7',
    'GGJ-40010037',
    '味淋魚乾 (魚勝)',
    '味淋魚乾 (魚勝)',
    'MIRIN FUGU',
    'Dried fish w/ sweet sake (500g)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453636',
    '2026-01-07T12:00:30.453638'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'afd264cd-c635-44d5-8bf2-2272df94e0f1',
    'GGJ-40010122',
    '鯖魚一夜干',
    '鯖魚一夜干',
    'IKA ICHIYABOSHI',
    'Mackerel overnight dried (16pc)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'Box',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453645',
    '2026-01-07T12:00:30.453647'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'dd5ab6d0-7c4c-4b24-9c8f-e8d81278609b',
    'GGJ-40010026',
    '中国産鰻蒲焼 (30pc)',
    '中国産鰻蒲焼 (30pc)',
    'KABAYAKI UNAGI',
    'Eel in soy-based sauce',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'KG',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453654',
    '2026-01-07T12:00:30.453656'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1bbe6647-2eae-4901-a2fc-a990a2efb56b',
    'GGJ-40010028',
    '中国産鰻蒲焼 (40pc)',
    '中国産鰻蒲焼 (40pc)',
    'KABAYAKI UNAGI',
    'Eel in soy-based sauce',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'KG',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453663',
    '2026-01-07T12:00:30.453664'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '64d2efa6-59de-4b25-ab78-e7c2a4dc5fb7',
    'GGJ-40010030',
    '中国産鰻蒲焼 (50pc)',
    '中国産鰻蒲焼 (50pc)',
    'KABAYAKI UNAGI',
    'Eel in soy-based sauce',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'KG',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453672',
    '2026-01-07T12:00:30.453673'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '11e89c43-a861-4110-a25d-b1008fe42bc8',
    'GGJ-40010048',
    '日本産鰻白焼',
    '日本産鰻白焼',
    'SHIRAYAKI UNAGI',
    'Eel w/o sauce Japan (~200g)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453680',
    '2026-01-07T12:00:30.453682'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5b58750a-494e-4eb6-8eff-370b24eda75f',
    'GGJ-40010064',
    '鰻魚片',
    '鰻魚片',
    NULL,
    'Eel slice (20pc)',
    '急凍/冷藏 > 海產(魚/魚子)',
    '急凍/冷藏',
    '海產(魚/魚子)',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453689',
    '2026-01-07T12:00:30.453691'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '665d3b3a-abfa-4a67-a346-6e74b0b85847',
    'GGJ-40050003',
    '冷凍日本稲庭烏冬',
    '冷凍日本稲庭烏冬',
    NULL,
    'Inaniwa udon (250g x 5)',
    '急凍/冷藏 > 麵類/小食',
    '急凍/冷藏',
    '麵類/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453701',
    '2026-01-07T12:00:30.453703'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5d73f17f-5a09-4dce-8a77-24a3f62444f9',
    'GGJ-40050008',
    '冷凍日本烏冬EX',
    '冷凍日本烏冬EX',
    NULL,
    'Sanuki udon (250g x 5)',
    '急凍/冷藏 > 麵類/小食',
    '急凍/冷藏',
    '麵類/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453731',
    '2026-01-07T12:00:30.453794'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7e997c00-ff59-4a84-abe0-5e93d88a5e48',
    'GGJ-40050012',
    '冷凍赤麵 武藏野',
    '冷凍赤麵 武藏野',
    NULL,
    'Soba (200g x 5)',
    '急凍/冷藏 > 麵類/小食',
    '急凍/冷藏',
    '麵類/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453842',
    '2026-01-07T12:00:30.453846'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f8d1f87b-b6da-44aa-a8b9-0f08669c884e',
    'GGJ-40040017',
    '熟鮟鱇魚肝',
    '熟鮟鱇魚肝',
    NULL,
    'Cooked monk fish liver (~200g)',
    '急凍/冷藏 > 加工/其他',
    '急凍/冷藏',
    '加工/其他',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453863',
    '2026-01-07T12:00:30.453866'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3d109be8-bac1-4236-a201-650e29cdd1d4',
    'GGJ-40010041',
    '烏賊一夜干',
    '烏賊一夜干',
    'IKA ICHIYABOSHI',
    'Squid overnight dried (2pc)',
    '急凍/冷藏 > 加工/其他',
    '急凍/冷藏',
    '加工/其他',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453886',
    '2026-01-07T12:00:30.453888'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '679656f6-0528-4dd6-ba91-fa4d2f3add7d',
    'GGJ-40030063',
    '芥辣蝦沙律',
    '芥辣蝦沙律',
    NULL,
    'Wasabi shrimp salad (600g)',
    '急凍/冷藏 > 加工/其他',
    '急凍/冷藏',
    '加工/其他',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453900',
    '2026-01-07T12:00:30.453903'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4e3f1fa3-ffed-45ab-810d-905806c1d663',
    'GGJ-40070028',
    '蛍光魷魚沖漬',
    '蛍光魷魚沖漬',
    NULL,
    'Firefly squid pickle (500g)',
    '急凍/冷藏 > 加工/其他',
    '急凍/冷藏',
    '加工/其他',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453915',
    '2026-01-07T12:00:30.453917'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '6e91b1ba-1e41-4007-b23e-0f2080fa6e06',
    'GGJ-40030037',
    '真八爪',
    '真八爪',
    NULL,
    'Octopus (2~3.5kg)',
    '急凍/冷藏 > 加工/其他',
    '急凍/冷藏',
    '加工/其他',
    'KG',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453929',
    '2026-01-07T12:00:30.453932'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd6e74d9f-dbfb-4b70-898a-75c6bf3ed8d5',
    'GGJ-40070011',
    '芥辣八爪魚粒',
    '芥辣八爪魚粒',
    NULL,
    'Wasabi octopus (1kg)',
    '急凍/冷藏 > 加工/其他',
    '急凍/冷藏',
    '加工/其他',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453949',
    '2026-01-07T12:00:30.453951'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1da6dd92-ef7b-42ef-9ce5-4a15468b4e16',
    'GGJ-40020001',
    '廣島蠔肉 2L',
    '廣島蠔肉 2L',
    NULL,
    'Hiroshima oyster meat (1kg)',
    '急凍/冷藏 > 加工/其他',
    '急凍/冷藏',
    '加工/其他',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453965',
    '2026-01-07T12:00:30.453968'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'dfee4758-dd6d-4bf3-aa1c-64737ca562af',
    'GGJ-40040019',
    '明太子沙律',
    '明太子沙律',
    NULL,
    'Mentaiko salad (1kg)',
    '急凍/冷藏 > 加工/其他',
    '急凍/冷藏',
    '加工/其他',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453983',
    '2026-01-07T12:00:30.453986'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '69679899-11e0-4cf1-a144-b18374aa13c0',
    'GGJ-10020233',
    '紋甲魷魚 (寿司用)',
    '紋甲魷魚 (寿司用)',
    NULL,
    'Cuttlefish for sushi use (1kg)',
    '急凍/冷藏 > 加工/其他',
    '急凍/冷藏',
    '加工/其他',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.453998',
    '2026-01-07T12:00:30.454001'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5978b6e7-2be2-4800-be79-8b0e034e8275',
    'GGJ-40070030',
    '龍蝦沙律',
    '龍蝦沙律',
    NULL,
    'Lobster salad (1kg)',
    '急凍/冷藏 > 加工/其他',
    '急凍/冷藏',
    '加工/其他',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454013',
    '2026-01-07T12:00:30.454016'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e4475222-ee5d-467c-ba8a-1141bd440ab1',
    'GGJ-40030024',
    '紋甲魷魚（寿司職人）',
    '紋甲魷魚（寿司職人）',
    NULL,
    'Cuttlefish big piece (200~300g)',
    '急凍/冷藏 > 加工/其他',
    '急凍/冷藏',
    '加工/其他',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454028',
    '2026-01-07T12:00:30.454031'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f55edc3b-20bd-4113-9a52-e4320826ddc8',
    'GGJ-60010015',
    '米糠',
    '米糠',
    'KOME NUKA',
    'Rice bran (1kg)',
    '米/穀類 > 米類',
    '米/穀類',
    '米類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454043',
    '2026-01-07T12:00:30.454046'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'bf53c1db-d549-4c0e-8ad5-597461569ac6',
    'GGJ-60010008',
    '白梅糯米',
    '白梅糯米',
    'MOCHI KOME',
    'Glutinous rice (900g)',
    '米/穀類 > 米類',
    '米/穀類',
    '米類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454058',
    '2026-01-07T12:00:30.454061'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4abee919-f336-4bc9-9442-afcf5534f589',
    'GGJ-60120004',
    '米通',
    '米通',
    'BUBUARARE',
    'Crispy rice (300g)',
    '米/穀類 > 米類',
    '米/穀類',
    '米類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454072',
    '2026-01-07T12:00:30.454075'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4c1a7ed7-85c5-48b9-a47f-62aa6a006f86',
    'GGJ-60120052',
    '五色米通',
    '五色米通',
    NULL,
    'Multi color crispy rice (500g)',
    '米/穀類 > 米類',
    '米/穀類',
    '米類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454086',
    '2026-01-07T12:00:30.454087'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e827dc04-552d-4712-a612-75225ce00e58',
    'GGJ-60120033',
    '粒裝飯油（炊飯用）',
    '粒裝飯油（炊飯用）',
    NULL,
    'Oil pellet for rice cooking (50pc)',
    '米/穀類 > 米類',
    '米/穀類',
    '米類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454095',
    '2026-01-07T12:00:30.454097'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a2411562-e69f-4b57-8159-6ed78dfa657b',
    'GGJ-60120020',
    '特麗素（炊飯用）',
    '特麗素（炊飯用）',
    NULL,
    'Miola for rice cooking (1kg)',
    '米/穀類 > 米類',
    '米/穀類',
    '米類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454106',
    '2026-01-07T12:00:30.454107'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a8c5ed16-b7ca-480e-8a4d-04c987fc27ed',
    'GGJ-60020004',
    '五木赤蕎麦麵',
    '五木赤蕎麦麵',
    NULL,
    'Itsuki tea soba (250g)',
    '乾貨/調味 > 麵類',
    '乾貨/調味',
    '麵類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454116',
    '2026-01-07T12:00:30.454118'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd7c04807-aa79-409c-9428-96e3fce17a75',
    'GGJ-60020019',
    '信州木曽路赤蕎麦麵',
    '信州木曽路赤蕎麦麵',
    NULL,
    'Shinshu Kisoji red soba (200g)',
    '乾貨/調味 > 麵類',
    '乾貨/調味',
    '麵類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454126',
    '2026-01-07T12:00:30.454127'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'be1d4522-8aff-4d5a-bdd1-3ae086c04cac',
    'GGJ-60020011',
    '氷見烏冬（乾）',
    '氷見烏冬（乾）',
    NULL,
    'Himi udon dried (1kg)',
    '乾貨/調味 > 麵類',
    '乾貨/調味',
    '麵類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454134',
    '2026-01-07T12:00:30.454136'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b6323609-4f17-489f-ba56-d76c35eb1306',
    'GGJ-60020049',
    '後文稲庭烏冬（乾）',
    '後文稲庭烏冬（乾）',
    NULL,
    'Gobun Inaniwa udon dried (1kg)',
    '乾貨/調味 > 麵類',
    '乾貨/調味',
    '麵類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454144',
    '2026-01-07T12:00:30.454146'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '72b1e6fc-ce3f-4e03-8127-b0b68ac5a42d',
    'GGJ-60030009',
    '天婦羅粉（昭和）',
    '天婦羅粉（昭和）',
    NULL,
    'Tempura powder (700g)',
    '乾貨/調味 > 粉類',
    '乾貨/調味',
    '粉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454153',
    '2026-01-07T12:00:30.454155'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '0f9f66c7-976e-45da-80b4-53f40e3ab261',
    'GGJ-60030004',
    '片栗粉',
    '片栗粉',
    'KATAKURIKO',
    'Potato powder (1kg)',
    '乾貨/調味 > 粉類',
    '乾貨/調味',
    '粉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454164',
    '2026-01-07T12:00:30.454166'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5c5a973d-aa08-4467-8c3d-28f14ddf394a',
    'GGJ-60090266',
    '紫蘇粉',
    '紫蘇粉',
    'YUKARIKO',
    'Shiso powder (26g)',
    '乾貨/調味 > 粉類',
    '乾貨/調味',
    '粉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454179',
    '2026-01-07T12:00:30.454182'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4d0e9c89-d952-405e-8317-92a4fefd511b',
    'GGJ-60030015',
    'Flower 薄力粉 (日清)',
    'Flower 薄力粉 (日清)',
    NULL,
    'Nissin weak flour (1kg)',
    '乾貨/調味 > 粉類',
    '乾貨/調味',
    '粉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454192',
    '2026-01-07T12:00:30.454193'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'da4c2a8d-e131-48a6-8db8-fa4ac68f71fd',
    'GGJ-60030010',
    '薄力小麥粉 (日清)',
    '薄力小麥粉 (日清)',
    NULL,
    'Nissin weak wheat flour (1kg)',
    '乾貨/調味 > 粉類',
    '乾貨/調味',
    '粉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454201',
    '2026-01-07T12:00:30.454202'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '019d9ffb-927c-4153-8560-bfe8180ed35e',
    'GGJ-60030063',
    '片栗粉',
    '片栗粉',
    'KATAKURIKO',
    'Potato powder (250G)',
    '乾貨/調味 > 粉類',
    '乾貨/調味',
    '粉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454210',
    '2026-01-07T12:00:30.454212'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '97c65f43-d1be-4f2d-9095-974877fecd21',
    'GGJ-60030018',
    '易炸天婦羅炸粉（日清）',
    '易炸天婦羅炸粉（日清）',
    NULL,
    'Nissin easy-to-use tempura powder (1kg)',
    '乾貨/調味 > 粉類',
    '乾貨/調味',
    '粉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454273',
    '2026-01-07T12:00:30.454277'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '0188aacf-d965-4b1a-b9ff-187776137db7',
    'GGJ-60030002',
    '純正麵包糠',
    '純正麵包糠',
    'SAKUSAKU PANKO',
    'Frozen crispy bread crumb (1kg)',
    '乾貨/調味 > 粉類',
    '乾貨/調味',
    '粉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454292',
    '2026-01-07T12:00:30.454295'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b9b224a9-4d78-4e1e-a1e2-5c702a60a3e5',
    'GGJ-60030020',
    '乾燥麵包糠',
    '乾燥麵包糠',
    NULL,
    'Dried bread crump (1kg)',
    '乾貨/調味 > 粉類',
    '乾貨/調味',
    '粉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454303',
    '2026-01-07T12:00:30.454305'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4eaa8b0a-1a74-413b-8614-e5da11418b22',
    'GGJ-40070041',
    '冷凍生麵包糠',
    '冷凍生麵包糠',
    NULL,
    'Frozen bread crump (2kg)',
    '乾貨/調味 > 粉類',
    '乾貨/調味',
    '粉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454313',
    '2026-01-07T12:00:30.454315'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '38bd63ce-a8d1-4c7b-a761-c5888d5b0bee',
    'GGJ-60030011',
    '蕨粉',
    '蕨粉',
    'WARABIKO',
    'Bracken powder (500g)',
    '乾貨/調味 > 粉類',
    '乾貨/調味',
    '粉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454324',
    '2026-01-07T12:00:30.454326'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd06b6662-f833-4c06-96e1-d518ba067c78',
    'GGJ-60030016',
    '吉野葛粉（日の本KING）',
    '吉野葛粉（日の本KING）',
    NULL,
    'Japanese arrowroot powder (1kg)',
    '乾貨/調味 > 粉類',
    '乾貨/調味',
    '粉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454336',
    '2026-01-07T12:00:30.454337'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'bf4dfae7-c204-4968-9802-d3247d1323ba',
    'GGJ-60120010',
    '魚膠片',
    '魚膠片',
    NULL,
    'Gelatin plate (300g)',
    '乾貨/調味 > 粉類',
    '乾貨/調味',
    '粉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454345',
    '2026-01-07T12:00:30.454347'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '72806a08-bee1-47e4-af00-f55ca198085f',
    'GGJ-60120146',
    '果凍粉',
    '果凍粉',
    NULL,
    'Pearl agar (1kg)',
    '乾貨/調味 > 粉類',
    '乾貨/調味',
    '粉類',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454355',
    '2026-01-07T12:00:30.454356'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '072c9ac8-8c0e-4ecb-8859-d5f77b0b7db0',
    'GGJ-60040009',
    '香味乾海苔',
    '香味乾海苔',
    NULL,
    'Fragrant dried seaweed (50g)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454364',
    '2026-01-07T12:00:30.454366'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a20cd475-2144-4416-84bc-1a39f3d63165',
    'GGJ-60040041',
    '青紫菜粉',
    '青紫菜粉',
    NULL,
    'Aosa seaweed powder (10g)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454374',
    '2026-01-07T12:00:30.454375'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '0354ddee-bf24-40ce-9955-db4bdb86a8f0',
    'GGJ-60040027',
    '寿司海苔A',
    '寿司海苔A',
    NULL,
    'Sushi seaweed (50pc)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454384',
    '2026-01-07T12:00:30.454386'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9ac69c0c-c766-4f0d-99da-b0b4d8746d76',
    'GGJ-60040007',
    '有明海壽司海苔-強焼',
    '有明海壽司海苔-強焼',
    NULL,
    'Kawaryou sushi seaweed half (50pc)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454394',
    '2026-01-07T12:00:30.454396'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '959989df-89f8-4ec8-b71a-ea37685bdb86',
    'GGJ-60040024',
    '有明海寿司海苔（全形）',
    '有明海寿司海苔（全形）',
    NULL,
    'Kawaryou sushi seaweed whole (100pc)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454406',
    '2026-01-07T12:00:30.454408'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '2868924a-8d62-4ef1-b838-6c00429339d4',
    'GGJ-60040036',
    '海草B-DORO白色',
    '海草B-DORO白色',
    'KAISO B-DORO',
    'White alga (500g)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454416',
    '2026-01-07T12:00:30.454418'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'cb1b98ef-21fa-4151-8397-5eea68ecb241',
    'GGJ-60040022',
    '青鶏冠草',
    '青鶏冠草',
    'AO TOSAKA',
    'Green alga (500g)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454426',
    '2026-01-07T12:00:30.454428'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b28aa6de-f3a8-47ed-820f-60f502ba8c01',
    'GGJ-60040023',
    '赤鶏冠草',
    '赤鶏冠草',
    'AKA TOSAKA',
    'Red alga (500g)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454436',
    '2026-01-07T12:00:30.454438'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '42ae4e73-f819-4fc9-906a-34b4d6af9f6b',
    'GGJ-60040038',
    '鹽海草',
    '鹽海草',
    NULL,
    'Salty wakame (500g)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454447',
    '2026-01-07T12:00:30.454449'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'cd466857-9c39-40fc-b638-5bf3debc7912',
    'GGJ-60040040',
    '碎海草',
    '碎海草',
    NULL,
    'Cut wakame (200g)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454457',
    '2026-01-07T12:00:30.454459'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'db780011-d639-492e-bd1a-3049e3a6d546',
    'GGJ-60040018',
    '鳴門海草',
    '鳴門海草',
    NULL,
    'Naruto wakame (34g)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454467',
    '2026-01-07T12:00:30.454469'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '867ef379-cd43-4df4-b286-f288ee0d4c47',
    'GGJ-60040029',
    '海草沙律C寒天',
    '海草沙律C寒天',
    NULL,
    'Alga salad w/ agar (100g)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454477',
    '2026-01-07T12:00:30.454479'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '201a30d6-bc60-429d-8a2c-3233853c84f3',
    'GGJ-60040028',
    '海草沙律A',
    '海草沙律A',
    NULL,
    'Alga salad (100g)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454489',
    '2026-01-07T12:00:30.454491'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '57aff7be-6d16-47fd-a935-ac5507b7e0c0',
    'GGJ-DRY-SEA-0418',
    '新鮮海草',
    '新鮮海草',
    NULL,
    'Fresh Wakame (500g)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454507',
    '2026-01-07T12:00:30.454509'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '642348cb-3a16-4299-9251-9ec330ab313b',
    'GGJ-DRY-SEA-0419',
    '鮮雞冠草',
    '鮮雞冠草',
    NULL,
    'Fresh Tosaka',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454521',
    '2026-01-07T12:00:30.454522'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '99d4e1f0-010c-4af1-9e03-d09f2b2f9d7d',
    'GGJ-60050004',
    '木魚花 (厚)',
    '木魚花 (厚)',
    NULL,
    'Bonito slice w/ bloodlines thick (1kg)',
    '乾貨/調味 > 削節/湯包',
    '乾貨/調味',
    '削節/湯包',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454530',
    '2026-01-07T12:00:30.454532'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5758289f-c9ad-4168-bf4c-c7346701ca62',
    'GGJ-60050002',
    '木魚花 (有血)',
    '木魚花 (有血)',
    NULL,
    'Bonito slice w/ bloodlines (1kg)',
    '乾貨/調味 > 削節/湯包',
    '乾貨/調味',
    '削節/湯包',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454540',
    '2026-01-07T12:00:30.454542'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '626af3cf-e17c-4957-8289-329da3eb8384',
    'GGJ-60050003',
    '木魚花 (無血)',
    '木魚花 (無血)',
    NULL,
    'Bonito slice w/o bloodlines (1kg)',
    '乾貨/調味 > 削節/湯包',
    '乾貨/調味',
    '削節/湯包',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454550',
    '2026-01-07T12:00:30.454552'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd8037fb7-86bb-4349-bd15-f18c127784da',
    'GGJ-60050011',
    '木魚絲',
    '木魚絲',
    NULL,
    'Bonito filament (20g)',
    '乾貨/調味 > 削節/湯包',
    '乾貨/調味',
    '削節/湯包',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454560',
    '2026-01-07T12:00:30.454562'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'db6f139d-4f47-4a7d-ba36-9d82d0827595',
    'GGJ-60050018',
    '混合鯖魚花',
    '混合鯖魚花',
    NULL,
    'Mixed mackerel slice (180g)',
    '乾貨/調味 > 削節/湯包',
    '乾貨/調味',
    '削節/湯包',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454569',
    '2026-01-07T12:00:30.454571'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'db0b355c-89aa-435d-8dd8-bf7dad9f7382',
    'GGJ-60050006',
    '鯖魚花 (厚)',
    '鯖魚花 (厚)',
    NULL,
    'Mackerel slice w/ bloodlines thick (1kg)',
    '乾貨/調味 > 削節/湯包',
    '乾貨/調味',
    '削節/湯包',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454579',
    '2026-01-07T12:00:30.454581'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b76d06f8-f6e7-45eb-b931-0e166353e58a',
    'GGJ-60050007',
    '鯖魚花 (煮干入)',
    '鯖魚花 (煮干入)',
    NULL,
    'Mackerel slice w/ bloodines & niboshi (1kg)',
    '乾貨/調味 > 削節/湯包',
    '乾貨/調味',
    '削節/湯包',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454589',
    '2026-01-07T12:00:30.454591'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1ae7255b-37df-4739-a1c1-7fb4ad8a23c4',
    'GGJ-60090128',
    '木魚精',
    '木魚精',
    'HON DASHI',
    'Bonito soup stock powder (1kg)',
    '乾貨/調味 > 削節/湯包',
    '乾貨/調味',
    '削節/湯包',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454600',
    '2026-01-07T12:00:30.454602'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '54a3e86e-68ed-48bd-9e39-e17c1aeae078',
    'GGJ-60050017',
    '白出汁',
    '白出汁',
    'SHIRO DASHI',
    'Soup stock in white soy sauce (1L)',
    '乾貨/調味 > 削節/湯包',
    '乾貨/調味',
    '削節/湯包',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454611',
    '2026-01-07T12:00:30.454612'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9e130cd4-b66d-4bf1-9137-3f3839163a30',
    'GGJ-60050034',
    '木魚花出汁包 紅色',
    '木魚花出汁包 紅色',
    NULL,
    'Bonito soup stock bag red (100g x 10)',
    '乾貨/調味 > 削節/湯包',
    '乾貨/調味',
    '削節/湯包',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454622',
    '2026-01-07T12:00:30.454623'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '146c5a87-8ab4-4304-ba06-fa7de3804aac',
    'GGJ-60090076',
    '出汁包 (割烹之味)',
    '出汁包 (割烹之味)',
    'KAPPOU UME',
    'Soup stock bag (50g x 10)',
    '乾貨/調味 > 削節/湯包',
    '乾貨/調味',
    '削節/湯包',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454631',
    '2026-01-07T12:00:30.454633'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'fe5b60f6-301c-4f9b-b753-e4c8a08de292',
    'GGJ-60050031',
    '出汁包 TB50（新丸正）',
    '出汁包 TB50（新丸正）',
    NULL,
    'Soup stock bag TB50 (20pc)',
    '乾貨/調味 > 削節/湯包',
    '乾貨/調味',
    '削節/湯包',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454641',
    '2026-01-07T12:00:30.454643'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '37193bb1-18d8-4a5d-91fa-b6f512c31018',
    'GGJ-60050010',
    '日出昆布',
    '日出昆布',
    'DASHI KONBU',
    'Soup stock kelp (1kg)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454651',
    '2026-01-07T12:00:30.454653'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1bb0f427-e83e-4ca6-80c3-5436d3f143f2',
    'GGJ-DRY-SEA-0433',
    '真昆布',
    '真昆布',
    'DASHI KONBU',
    'Soup stock kelp (1kg)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454663',
    '2026-01-07T12:00:30.454665'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e236ff47-162a-49bc-941e-5727f54ef361',
    'GGJ-60050035',
    '羅臼昆布',
    '羅臼昆布',
    'RAUSU KONBU',
    'Hokkaido soup stock kelp (1kg)',
    '乾貨/調味 > 紫菜/海草/昆布',
    '乾貨/調味',
    '紫菜/海草/昆布',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454676',
    '2026-01-07T12:00:30.454677'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f2b62942-d2f1-49de-9383-67c9df3d2eea',
    'GGJ-60050005',
    '煮干',
    '煮干',
    'NIBOSHI',
    'Dried sardine (1KG)',
    '乾貨/調味 > 魚乾',
    '乾貨/調味',
    '魚乾',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454686',
    '2026-01-07T12:00:30.454688'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7c176664-91f5-4544-8558-2409ad31d083',
    'GGJ-60090154',
    '萬字豉油',
    '萬字豉油',
    NULL,
    'Kikkoman soy sauce (1.8L)',
    '乾貨/調味 > 醬油/豉油',
    '乾貨/調味',
    '醬油/豉油',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454696',
    '2026-01-07T12:00:30.454698'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '0588ba87-95b5-4cc0-8e12-880587056fd7',
    'GGJ-60060020',
    '山亞豉油',
    '山亞豉油',
    NULL,
    'Yamaa sakura soy sauce (1.8L)',
    '乾貨/調味 > 醬油/豉油',
    '乾貨/調味',
    '醬油/豉油',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454707',
    '2026-01-07T12:00:30.454709'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3d1cec9d-f3f0-46a5-a167-42d789dee5ff',
    'GGJ-60060031',
    '山字豉油',
    '山字豉油',
    NULL,
    'Yamasa soy sauce (1.8L)',
    '乾貨/調味 > 醬油/豉油',
    '乾貨/調味',
    '醬油/豉油',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454716',
    '2026-01-07T12:00:30.454718'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b3509f28-ac8b-4546-ba61-9f8290457976',
    'GGJ-60060012',
    '溜溜豉油',
    '溜溜豉油',
    'TAMARI SHOYU',
    'Rich soy sauce (1.8L)',
    '乾貨/調味 > 醬油/豉油',
    '乾貨/調味',
    '醬油/豉油',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454725',
    '2026-01-07T12:00:30.454727'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '82648094-194e-470a-91c5-1c6bc2ff7327',
    'GGJ-60060014',
    '東丸淡口豉油',
    '東丸淡口豉油',
    NULL,
    'Higashimaru thin soy sauce (1L)',
    '乾貨/調味 > 醬油/豉油',
    '乾貨/調味',
    '醬油/豉油',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454735',
    '2026-01-07T12:00:30.454736'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f86134b8-7636-446c-91e0-d34d5b9cb173',
    'GGJ-60060032',
    '白豉油',
    '白豉油',
    'SHIRO SHOYU',
    'Amber thin soy sauce (1.8L)',
    '乾貨/調味 > 醬油/豉油',
    '乾貨/調味',
    '醬油/豉油',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454745',
    '2026-01-07T12:00:30.454746'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e49a0a88-73d2-4bcd-bcc2-f304c7c399a2',
    'GGJ-60090089',
    '上字豉油 <桶>',
    '上字豉油 <桶>',
    NULL,
    'Yamasa soy sauce (18L)',
    '乾貨/調味 > 醬油/豉油',
    '乾貨/調味',
    '醬油/豉油',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454755',
    '2026-01-07T12:00:30.454757'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a716141b-a3a9-4b36-97b9-427fe58d32be',
    'GGJ-60060002',
    '八丁赤出麵豉',
    '八丁赤出麵豉',
    NULL,
    'Haccho akadashi miso (1kg)',
    '乾貨/調味 > 麵豉/味噌',
    '乾貨/調味',
    '麵豉/味噌',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454764',
    '2026-01-07T12:00:30.454766'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '21bcb75c-488c-4d49-85cf-a9236d75092d',
    'GGJ-60060004',
    '京櫻赤出麵豉',
    '京櫻赤出麵豉',
    NULL,
    'Kyouzakura akadashi miso (4kg)',
    '乾貨/調味 > 麵豉/味噌',
    '乾貨/調味',
    '麵豉/味噌',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454774',
    '2026-01-07T12:00:30.454776'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e3d6ea49-2254-477f-90f7-93e512993b27',
    'GGJ-60060010',
    '信州白味噌',
    '信州白味噌',
    NULL,
    'Shinshu miso (1kg)',
    '乾貨/調味 > 麵豉/味噌',
    '乾貨/調味',
    '麵豉/味噌',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454789',
    '2026-01-07T12:00:30.454792'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '8f51447c-5ad3-4bfe-94af-264c2d6b49b8',
    'GGJ-60060019',
    '一休白味噌',
    '一休白味噌',
    NULL,
    'Marukome miso (1kg)',
    '乾貨/調味 > 麵豉/味噌',
    '乾貨/調味',
    '麵豉/味噌',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454803',
    '2026-01-07T12:00:30.454804'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'abe0a265-e542-43ed-8a85-1fc7ccaa85b0',
    'GGJ-60060006',
    '西京白味噌',
    '西京白味噌',
    NULL,
    'Saikyo miso w/o granule (500g)',
    '乾貨/調味 > 麵豉/味噌',
    '乾貨/調味',
    '麵豉/味噌',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454814',
    '2026-01-07T12:00:30.454815'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1de724f0-3a2f-4d6f-8bb4-bb919f216af2',
    'GGJ-60060027',
    '石野西京白味噌（無粒）',
    '石野西京白味噌（無粒）',
    NULL,
    'Ishino Saikyo miso w/o granule (1kg)',
    '乾貨/調味 > 麵豉/味噌',
    '乾貨/調味',
    '麵豉/味噌',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454823',
    '2026-01-07T12:00:30.454825'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '66ba4119-217d-4013-a682-54914950122c',
    'GGJ-60060025',
    '石野西京白味噌（有粒）',
    '石野西京白味噌（有粒）',
    NULL,
    'Ishino Saikyo miso w/ granule (1kg)',
    '乾貨/調味 > 麵豉/味噌',
    '乾貨/調味',
    '麵豉/味噌',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454832',
    '2026-01-07T12:00:30.454834'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '13a99b73-f495-4fe1-8100-8997043ca814',
    'GGJ-60060007',
    '石野西京白味噌（無粒）',
    '石野西京白味噌（無粒）',
    NULL,
    'Ishino Saikyo miso w/o granule (4kg)',
    '乾貨/調味 > 麵豉/味噌',
    '乾貨/調味',
    '麵豉/味噌',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454843',
    '2026-01-07T12:00:30.454844'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '79575dd3-c189-4199-acf7-fbd0a0397089',
    'GGJ-60060008',
    '石野西京白味噌（有粒）',
    '石野西京白味噌（有粒）',
    NULL,
    'Ishino Saikyo miso w/ granule (4kg)',
    '乾貨/調味 > 麵豉/味噌',
    '乾貨/調味',
    '麵豉/味噌',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454852',
    '2026-01-07T12:00:30.454854'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'bbcfe787-feab-45d5-ab6f-2391de1fa1d0',
    'GGJ-60060005',
    '麥粒麵豉',
    '麥粒麵豉',
    'MOROMI MISO',
    'Wheat granule miso (750g)',
    '乾貨/調味 > 麵豉/味噌',
    '乾貨/調味',
    '麵豉/味噌',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454862',
    '2026-01-07T12:00:30.454863'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '44931ed5-646a-484f-9d8f-0d0a8ce5ed72',
    'GGJ-60060003',
    '田舎麵豉',
    '田舎麵豉',
    'INAKA MISO',
    'Countryside miso (1kg)',
    '乾貨/調味 > 麵豉/味噌',
    '乾貨/調味',
    '麵豉/味噌',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454871',
    '2026-01-07T12:00:30.454873'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '04ba8182-a86f-4c0c-bfc2-ed5e4e08ee8d',
    'GGJ-40040003',
    '蟹膏麵豉',
    '蟹膏麵豉',
    NULL,
    'Crab miso (70g)',
    '乾貨/調味 > 麵豉/味噌',
    '乾貨/調味',
    '麵豉/味噌',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454880',
    '2026-01-07T12:00:30.454882'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'ab2735c1-5691-437d-9ef6-d8487ac66608',
    'GGJ-60060024',
    '金山寺麵豉',
    '金山寺麵豉',
    NULL,
    'Kinzanji miso',
    '乾貨/調味 > 麵豉/味噌',
    '乾貨/調味',
    '麵豉/味噌',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454889',
    '2026-01-07T12:00:30.454891'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5f53875b-042b-453b-af53-1e7596cb3d84',
    'GGJ-60060029',
    '朴葉麵豉',
    '朴葉麵豉',
    'HOBA MISO',
    'Magnolia leaf miso (800g)',
    '乾貨/調味 > 麵豉/味噌',
    '乾貨/調味',
    '麵豉/味噌',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454898',
    '2026-01-07T12:00:30.454900'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9d44e232-958f-4a05-b506-e4d0b489dd9a',
    'GGJ-60070006',
    '穀物醋 (Mizkan)',
    '穀物醋 (Mizkan)',
    'KOKUMOTSU SU',
    'Grain vinegar (1.8L)',
    '乾貨/調味 > 醋',
    '乾貨/調味',
    '醋',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454910',
    '2026-01-07T12:00:30.454912'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1a69ce27-4a54-47ac-a177-56dbbf09b717',
    'GGJ-60070037',
    '琥珀醸造醋（横井醸造）',
    '琥珀醸造醋（横井醸造）',
    NULL,
    'Yokoi amber color brewed vinegar (1.8L)',
    '乾貨/調味 > 醋',
    '乾貨/調味',
    '醋',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454924',
    '2026-01-07T12:00:30.454926'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '23304837-10cb-4c21-a400-2002996dce06',
    'GGJ-60070002',
    '橙醋',
    '橙醋',
    'DAIDAISU',
    'Bitter orange vinegar (1.8L)',
    '乾貨/調味 > 醋',
    '乾貨/調味',
    '醋',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454934',
    '2026-01-07T12:00:30.454936'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f8f18e96-dd3c-4045-976c-016479e86437',
    'GGJ-60070005',
    '檸檬醋（Mizkan）',
    '檸檬醋（Mizkan）',
    'PONZU',
    'Mizkan lemon vinegar (1.8L)',
    '乾貨/調味 > 醋',
    '乾貨/調味',
    '醋',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454944',
    '2026-01-07T12:00:30.454945'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b9803b61-e14d-49e0-9762-85bf53c5e7df',
    'GGJ-60070015',
    '味付酸汁 (Mizkan)',
    '味付酸汁 (Mizkan)',
    NULL,
    'Mizkan ajipon (1.8L)',
    '乾貨/調味 > 醋',
    '乾貨/調味',
    '醋',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454954',
    '2026-01-07T12:00:30.454955'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1ceb31a4-9426-437f-be33-6b02df3b9181',
    'GGJ-60070031',
    '三ッ判山吹（Mizkan）',
    '三ッ判山吹（Mizkan）',
    NULL,
    'Mizkan sake lees vinegar (900ml)',
    '乾貨/調味 > 醋',
    '乾貨/調味',
    '醋',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454962',
    '2026-01-07T12:00:30.454964'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e561868a-5656-4c49-8c8c-71e965419718',
    'GGJ-60070001',
    '千鳥醋',
    '千鳥醋',
    NULL,
    'Chidori vinegar (1.8L)',
    '乾貨/調味 > 醋',
    '乾貨/調味',
    '醋',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454972',
    '2026-01-07T12:00:30.454973'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '22a70bbc-e5c9-466e-963a-77c42d596d1a',
    'GGJ-60070032',
    '柚子醋 (Yamaa)',
    '柚子醋 (Yamaa)',
    'YUZU PONZU',
    'Yamaa citrus juice (1.8L)',
    '乾貨/調味 > 醋',
    '乾貨/調味',
    '醋',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454981',
    '2026-01-07T12:00:30.454982'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '449a1e3d-43b8-4dfd-8587-94f5a81f9c0c',
    'GGJ-60070010',
    '醋橘醋',
    '醋橘醋',
    NULL,
    'Sudachi vinegar (1.8L)',
    '乾貨/調味 > 醋',
    '乾貨/調味',
    '醋',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.454990',
    '2026-01-07T12:00:30.454992'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '751ef2df-964d-4b89-80c7-270135b8aa61',
    'GGJ-60090092',
    '柚子醋 (紙盒)',
    '柚子醋 (紙盒)',
    NULL,
    'Yuzu vinegar (1.8L)',
    '乾貨/調味 > 醋',
    '乾貨/調味',
    '醋',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455001',
    '2026-01-07T12:00:30.455003'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7a1a334b-5836-4088-b823-db2b02ef6a94',
    'GGJ-60070009',
    '白菊醋（Mizkan）',
    '白菊醋（Mizkan）',
    NULL,
    'White chrysanthemum vinegar (20L)',
    '乾貨/調味 > 醋',
    '乾貨/調味',
    '醋',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455013',
    '2026-01-07T12:00:30.455015'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '2d54d87f-0ced-42ab-8cdc-fe7b330574a7',
    'GGJ-60070021',
    '本味醂（三樂）',
    '本味醂（三樂）',
    NULL,
    'Sanraku sweet sake (1.8L)',
    '乾貨/調味 > 味醂/酒',
    '乾貨/調味',
    '味醂/酒',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455022',
    '2026-01-07T12:00:30.455024'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e5709f19-d992-4185-a498-5cded014beec',
    'GGJ-60070036',
    '本味醂（百万両）',
    '本味醂（百万両）',
    NULL,
    'Hyakumanryou sweet sake (1.8L)',
    '乾貨/調味 > 味醂/酒',
    '乾貨/調味',
    '味醂/酒',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455031',
    '2026-01-07T12:00:30.455033'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'eedbb1a1-1294-46cc-b34a-5f433f10abc0',
    'GGJ-60070008',
    '獅子煮酒',
    '獅子煮酒',
    NULL,
    'Mercian cooking sake (1.8L)',
    '乾貨/調味 > 味醂/酒',
    '乾貨/調味',
    '味醂/酒',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455040',
    '2026-01-07T12:00:30.455042'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1864049c-ac44-4209-b0b7-f761bedbbb3e',
    'GGJ-60070030',
    '赤酒 東肥',
    '赤酒 東肥',
    NULL,
    'Touhi red sake (1.8L)',
    '乾貨/調味 > 味醂/酒',
    '乾貨/調味',
    '味醂/酒',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455049',
    '2026-01-07T12:00:30.455051'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '662df2ea-8c5f-425b-a25f-3653abb9ddba',
    'GGJ-60080005',
    '沙律油（日清）',
    '沙律油（日清）',
    NULL,
    'Nissin salad oil (1.5kg)',
    '乾貨/調味 > 油',
    '乾貨/調味',
    '油',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455058',
    '2026-01-07T12:00:30.455060'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '710da3f3-0827-4773-bc3e-4406f4cfa1e6',
    'GGJ-60090190',
    '鶏油 (Ebara)',
    '鶏油 (Ebara)',
    NULL,
    'Ebara chicken oil (900g)',
    '乾貨/調味 > 油',
    '乾貨/調味',
    '油',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455068',
    '2026-01-07T12:00:30.455070'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '44bffb48-161d-4008-9675-0362dc73a49a',
    'GGJ-60080013',
    '吞拿魚油',
    '吞拿魚油',
    'TOROMIYU',
    'Thickened oil (900g)',
    '乾貨/調味 > 油',
    '乾貨/調味',
    '油',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455113',
    '2026-01-07T12:00:30.455114'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '0c7eccc1-751d-4765-b013-a4ee16d5ba74',
    'GGJ-60080026',
    '芝麻油（日清）',
    '芝麻油（日清）',
    NULL,
    'Nissin sesame oil (1.5L)',
    '乾貨/調味 > 油',
    '乾貨/調味',
    '油',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455126',
    '2026-01-07T12:00:30.455128'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'aeca139b-526c-4f4c-b11b-d1b2862cfd80',
    'GGJ-60080007',
    '天婦羅油（昭和）',
    '天婦羅油（昭和）',
    NULL,
    'Showa tempura oil (16.5kg)',
    '乾貨/調味 > 油',
    '乾貨/調味',
    '油',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455136',
    '2026-01-07T12:00:30.455138'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '47235edf-6cb1-4a7d-8756-d343d50b21e3',
    'GGJ-60080011',
    '米油',
    '米油',
    NULL,
    'Rice oil (16.5kg)',
    '乾貨/調味 > 油',
    '乾貨/調味',
    '油',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455146',
    '2026-01-07T12:00:30.455148'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '98b669ea-61ec-4688-b082-2bd584906f56',
    'GGJ-60080002',
    '芝麻油（松本）',
    '芝麻油（松本）',
    NULL,
    'Matsumoto sesame oil (16.5kg)',
    '乾貨/調味 > 油',
    '乾貨/調味',
    '油',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455156',
    '2026-01-07T12:00:30.455158'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b482abfb-d28d-43d4-81e2-cd6d2a51110d',
    'GGJ-60090047',
    '日本辣椒醬 (蘿白茸)',
    '日本辣椒醬 (蘿白茸)',
    'OROSHI MOMIJI',
    'Grated radish & red pepper (180g)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455166',
    '2026-01-07T12:00:30.455167'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c3ddc150-eab3-4f3a-a7ea-6c9867101516',
    'GGJ-60090019',
    '柚子胡椒（柚子胡椒本舗）',
    '柚子胡椒（柚子胡椒本舗）',
    'YUZU KOSHO',
    'Citrus pepper (150g)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455175',
    '2026-01-07T12:00:30.455177'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4953ca9a-3553-4379-a0ba-75dcb7cfbb96',
    'GGJ-60090109',
    '青芥辣粉 (S-07)',
    '青芥辣粉 (S-07)',
    'OROSHI WASABI',
    'Grated horseradish powder (1kg)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455185',
    '2026-01-07T12:00:30.455187'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7a06586c-1e5d-4c6f-bc33-44bb26d3a246',
    'GGJ-60090022',
    '當胡麻(白)（九鬼）',
    '當胡麻(白)（九鬼）',
    'KUKI ATARI GOMA',
    'White sesame paste (300g)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455195',
    '2026-01-07T12:00:30.455197'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7af917be-c969-4a46-b7cc-80dbc0f282c0',
    'GGJ-40070194',
    '柚子皮絲 (金久)',
    '柚子皮絲 (金久)',
    'KIZAMI YUZU KAWA',
    'Kinjirushi shredded citrus skin',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455205',
    '2026-01-07T12:00:30.455206'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '0790a69d-c89e-405f-a714-4fa190e599ac',
    'GGJ-60120086',
    '有馬山椒',
    '有馬山椒',
    'ARIMA SHASHO',
    'Arima Japanese pepper (210g)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455214',
    '2026-01-07T12:00:30.455216'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a4d14580-1314-4406-86d6-14c868f0fafe',
    'GGJ-60090101',
    '青芥辣粉 (金印)',
    '青芥辣粉 (金印)',
    'OROSHI WASABI',
    'Kinjirushi grated horseradish powder (1kg)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455224',
    '2026-01-07T12:00:30.455226'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '04da54eb-a444-4098-8c2d-a62f8753f7a3',
    'GGJ-60090018',
    '青芥辣粉 (金久)',
    '青芥辣粉 (金久)',
    'OROSHI WASABI',
    'Kaneku grated horseradish powder (1kg)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455233',
    '2026-01-07T12:00:30.455235'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '969e61c4-178a-467a-8b9b-7986a20bbbd4',
    'GGJ-60090108',
    '辣椒絲 (Gaban)',
    '辣椒絲 (Gaban)',
    'ITO TOGARASHI',
    'Red pepper filament (100g)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455244',
    '2026-01-07T12:00:30.455246'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '675de216-05d9-457c-8bfe-1387ac70f087',
    'GGJ-60090055',
    '青芥辣 (Miko)',
    '青芥辣 (Miko)',
    'OROSHI WASABI',
    'Miko grated horseradish (1kg)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455253',
    '2026-01-07T12:00:30.455255'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c86387d0-4703-4d3f-8647-40fd3ff1a9f8',
    'GGJ-60090024',
    '當胡麻（恵美福）',
    '當胡麻（恵美福）',
    'EMIFUKU ATARI GOMA',
    'Sesame paste (900ml)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455263',
    '2026-01-07T12:00:30.455265'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '2ab8cc55-2d99-4215-a5be-9b8ebc150043',
    'GGJ-60090112',
    '日本塩',
    '日本塩',
    NULL,
    'Japanese salt (1kg)',
    '乾貨/調味 > 鹽/糖',
    '乾貨/調味',
    '鹽/糖',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455273',
    '2026-01-07T12:00:30.455275'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c0b847c3-c5dc-4fad-93c3-2fd63615eeaa',
    'GGJ-60090001',
    '日本味鹽',
    '日本味鹽',
    'AJI SHIO',
    'Japanese seasoned salt (110g)',
    '乾貨/調味 > 鹽/糖',
    '乾貨/調味',
    '鹽/糖',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455283',
    '2026-01-07T12:00:30.455285'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '584980c4-986a-4c96-aeb3-d91994b95687',
    'GGJ-60090153',
    '伯方粗塩',
    '伯方粗塩',
    'HAKATA ARASHIO',
    'Hakata course salt (1kg)',
    '乾貨/調味 > 鹽/糖',
    '乾貨/調味',
    '鹽/糖',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455292',
    '2026-01-07T12:00:30.455294'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9cb57855-aa98-40c1-ab98-c5146aff7479',
    'GGJ-60090102',
    '伯方焼塩',
    '伯方焼塩',
    'HAKATA YAKISHIO',
    'Hakata baked salt (1kg)',
    '乾貨/調味 > 鹽/糖',
    '乾貨/調味',
    '鹽/糖',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455302',
    '2026-01-07T12:00:30.455303'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '93fc0822-b7ab-40b8-b329-26b871419808',
    'GGJ-60090135',
    '赤穂天塩',
    '赤穂天塩',
    'AKOU NO AMASHIO',
    'Akou salt (1kg)',
    '乾貨/調味 > 鹽/糖',
    '乾貨/調味',
    '鹽/糖',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455311',
    '2026-01-07T12:00:30.455313'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '6a3b2f9b-b027-4a4c-a3d5-4cc34de3c6ef',
    'GGJ-60090133',
    '柚子塩',
    '柚子塩',
    'YUZU SHIO',
    'Citrus salt (300g)',
    '乾貨/調味 > 鹽/糖',
    '乾貨/調味',
    '鹽/糖',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455320',
    '2026-01-07T12:00:30.455322'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '6bad669d-83bc-4b85-a9d7-13ad26062dfb',
    'GGJ-60090090',
    '抹茶塩',
    '抹茶塩',
    NULL,
    'Maccha salt (300g)',
    '乾貨/調味 > 鹽/糖',
    '乾貨/調味',
    '鹽/糖',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455329',
    '2026-01-07T12:00:30.455330'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'df32f6b4-7730-4257-a4f4-909dd694f98f',
    'GGJ-60090005',
    '上白糖',
    '上白糖',
    'JYOUHAKUTOU',
    'White sugar (1kg)',
    '乾貨/調味 > 鹽/糖',
    '乾貨/調味',
    '鹽/糖',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455339',
    '2026-01-07T12:00:30.455341'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'bd3962bb-7176-4a9b-bd87-0997e90f39a9',
    'GGJ-60090007',
    '咖啡糖',
    '咖啡糖',
    'ZARAME CHUSOUTOU',
    'Coffee sugar (1kg)',
    '乾貨/調味 > 鹽/糖',
    '乾貨/調味',
    '鹽/糖',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455348',
    '2026-01-07T12:00:30.455350'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '32253706-8364-4a5b-94c0-c00d781c0040',
    'GGJ-60090006',
    '三溫糖',
    '三溫糖',
    'KACHIWARI KUROTOU',
    'Brown sugar (1kg)',
    '乾貨/調味 > 鹽/糖',
    '乾貨/調味',
    '鹽/糖',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455358',
    '2026-01-07T12:00:30.455360'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f5c6d859-5505-414a-86b0-f051dfe8b105',
    'GGJ-DRY-SSG-0500',
    '日本沖縄黒糖粒 (300g)',
    '日本沖縄黒糖粒 (300g)',
    NULL,
    'Okinawa black Rock sugar (300G)',
    '乾貨/調味 > 鹽/糖',
    '乾貨/調味',
    '鹽/糖',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455371',
    '2026-01-07T12:00:30.455373'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a79cc881-7724-46a1-aa26-989ddb4bf668',
    'GGJ-60090118',
    '紫菜醬',
    '紫菜醬',
    'NORI TSUKUDANI',
    'Seaweed boiled in sweetened soy sauce (180g)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455382',
    '2026-01-07T12:00:30.455383'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '0fa693ee-dc23-4bdf-a381-5a87b262f301',
    'GGJ-60100017',
    'QP210蛋黃醬',
    'QP210蛋黃醬',
    NULL,
    'QP 210 Mayonnaise (1kg)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455392',
    '2026-01-07T12:00:30.455393'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4a8d9fd2-52c8-43f4-a4c7-bc914f8db732',
    'GGJ-60090043',
    '豬扒汁（Bulldog）',
    '豬扒汁（Bulldog）',
    'TONKATSU SAUCE',
    'Pork cutlet sauce (1.8L)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455402',
    '2026-01-07T12:00:30.455404'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '581842ca-a7fc-4e6e-a03d-d3c7a69274a4',
    'GGJ-60090065',
    '融醇中辛咖哩',
    '融醇中辛咖哩',
    'TOROKERU',
    'Curry flake (1kg)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455411',
    '2026-01-07T12:00:30.455413'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '11d0b6f0-c3cb-4fc5-9d68-549c9dd9e65d',
    'GGJ-60090113',
    '咖喱磚 (S & B)',
    '咖喱磚 (S & B)',
    NULL,
    'Dinner curry brick (1kg)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455421',
    '2026-01-07T12:00:30.455423'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'bbe74bc3-6555-499a-bd90-2a152bb8ef1d',
    'GGJ-60090295',
    '照焼汁（日本食研）',
    '照焼汁（日本食研）',
    NULL,
    'Teriyaki sauce (2kg)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455430',
    '2026-01-07T12:00:30.455432'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '37b6af4b-f868-443b-b7e0-9d38b06010ed',
    'GGJ-40040010',
    '辛辣明太子魚籽醬',
    '辛辣明太子魚籽醬',
    'MENTAIKO PASTE',
    'Cod roe paste (500g)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455443',
    '2026-01-07T12:00:30.455445'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'eb07a29b-06bc-4297-a713-cbf247f80415',
    'GGJ-60090085',
    '柚子之粋',
    '柚子之粋',
    'YUZU NO SUI',
    'Citrus essence (300ml)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455453',
    '2026-01-07T12:00:30.455454'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5ea0a683-92f2-4ac8-b16b-5b2cb2c0a6f6',
    'GGJ-60090030',
    '意粉牛肉汁 (Heinz)',
    '意粉牛肉汁 (Heinz)',
    NULL,
    'Heinz demi glace pasta sauce (3kg)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455462',
    '2026-01-07T12:00:30.455464'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '313f30f8-6daf-4710-a206-4af93669b85d',
    'GGJ-60090037',
    '燒鰻魚醬（日本食研）',
    '燒鰻魚醬（日本食研）',
    'UNAGI TARE',
    'Grill eel sauce (2kg)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455472',
    '2026-01-07T12:00:30.455473'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '41dd53d7-77ff-4d8a-9d5f-ef886af4bd95',
    'GGJ-60100004',
    '和風沙律汁（日本食研）',
    '和風沙律汁（日本食研）',
    NULL,
    'Japanese style dressing (1L)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455481',
    '2026-01-07T12:00:30.455482'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c5733f82-7a86-46ff-8af0-69ff02b7590c',
    'GGJ-60100006',
    '芥辣沙律油',
    '芥辣沙律油',
    NULL,
    'Wasabi soy sauce dressing (1L)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455490',
    '2026-01-07T12:00:30.455491'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '56b2ee4d-1884-4b38-a91d-043ab8ddb53d',
    'GGJ-60100010',
    '蒜香蕃茄沙律汁 (Mizkan)',
    '蒜香蕃茄沙律汁 (Mizkan)',
    NULL,
    'Italian Paccio Tomato garlic dressing (1L)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455499',
    '2026-01-07T12:00:30.455501'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '81441d1b-44f7-4327-a499-d743b88e9314',
    'GGJ-60100012',
    '香味和風沙律汁 (QP)',
    '香味和風沙律汁 (QP)',
    NULL,
    'Fragrant Japanese style dressing (1L)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455508',
    '2026-01-07T12:00:30.455510'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '6aea9411-9adb-46b4-a74f-df342cfc6fff',
    'GGJ-60100013',
    '香味柚子沙律汁 (QP)',
    '香味柚子沙律汁 (QP)',
    NULL,
    'Fragrant Citrus dressing (1L)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455532',
    '2026-01-07T12:00:30.455534'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '11352656-1a7f-4519-8ac8-18e52f53aa9c',
    'GGJ-60100030',
    '丘比焙煎芝麻沙律汁 (QP)',
    '丘比焙煎芝麻沙律汁 (QP)',
    NULL,
    'Roasted sesame dressing (1L)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455542',
    '2026-01-07T12:00:30.455543'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '8e607ef6-08d9-4e7d-b504-4b71179414dd',
    'GGJ-60100001',
    '青紫蘇沙律油（理研）',
    '青紫蘇沙律油（理研）',
    NULL,
    'Non-oil green shiso dressing (1L)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455553',
    '2026-01-07T12:00:30.455555'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '292a7d0a-464e-4dda-a994-266c7cca9019',
    'GGJ-60100067',
    '凱撒沙律汁 (QP)',
    '凱撒沙律汁 (QP)',
    NULL,
    'Caesar dressing (1.5L)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455565',
    '2026-01-07T12:00:30.455567'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '45be1c87-aa2b-43d8-a1f6-f5a9f2eba702',
    'GGJ-60100042',
    '博多豬骨拉麵湯 (Ebara)',
    '博多豬骨拉麵湯 (Ebara)',
    NULL,
    'Hakata pork ramen soup base (1kg)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455574',
    '2026-01-07T12:00:30.455576'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c587be42-42e9-4aa9-aec1-c68f7e41c74a',
    'GGJ-60100043',
    '雞骨豉油拉麵汁 (Ebara)',
    '雞骨豉油拉麵汁 (Ebara)',
    NULL,
    'Chicken soy sauce ramen soup base (2kg)',
    '乾貨/調味 > 調味/醬汁',
    '乾貨/調味',
    '調味/醬汁',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455584',
    '2026-01-07T12:00:30.455585'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a8850452-b62d-4051-ad25-c0acf694a382',
    'GGJ-60120089',
    '燒鱈魚卷',
    '燒鱈魚卷',
    NULL,
    'Roasted cod fish roll (35g)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455593',
    '2026-01-07T12:00:30.455595'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '72e16bd9-5d94-4fb8-a4c8-a4b6492957bc',
    'GGJ-40030053',
    '板白魚片',
    '板白魚片',
    'SHIRO KAMABOKO',
    'Boiled fish cake white (130g)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455605',
    '2026-01-07T12:00:30.455607'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '75182bb5-a8a2-4181-8b84-2c1129ab65e2',
    'GGJ-40030054',
    '板紅魚片',
    '板紅魚片',
    'AKA KAMABOKO',
    'Boiled fish cake red (130g)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455616',
    '2026-01-07T12:00:30.455618'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a81e2b60-ef0d-459d-a43d-49d585dc47ef',
    'GGJ-40030057',
    '燒板魚片',
    '燒板魚片',
    NULL,
    'Roasted fish cake',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455625',
    '2026-01-07T12:00:30.455627'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'da89c4ab-be7b-4d80-8242-be2b12096fe1',
    'GGJ-60120106',
    '蟹麵豉豆腐',
    '蟹麵豉豆腐',
    NULL,
    'Crab miso bean curd (210g)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455634',
    '2026-01-07T12:00:30.455636'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'cd2766a3-f3da-4288-91fc-3e5e59e3cb47',
    'GGJ-20040009',
    '海膽豆腐',
    '海膽豆腐',
    NULL,
    'Sea urchin bean curd (210g)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455643',
    '2026-01-07T12:00:30.455645'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '33ac8f41-6c58-4f7b-8efa-d797330d120e',
    'GGJ-60120256',
    '鮟鱇魚肝豆腐',
    '鮟鱇魚肝豆腐',
    NULL,
    'Monk fish liver bean curd (210g)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455653',
    '2026-01-07T12:00:30.455654'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '133cf302-bf5f-4800-8bc1-2c160eab8e91',
    'GGJ-20040012',
    '海膽醬',
    '海膽醬',
    'NERI URI',
    'Sea urchin paste (80g)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455662',
    '2026-01-07T12:00:30.455663'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f34af7d9-552c-4f94-92ad-1a545f4531f7',
    'GGJ-FRZ-XXX-0529',
    '海膽醬',
    '海膽醬',
    'NERI URI',
    'Sea urchin paste (1kg)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455675',
    '2026-01-07T12:00:30.455676'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '272d1432-3d60-41eb-903c-0fa44d8b36b7',
    'GGJ-10060013',
    '吞拿魚酒盗',
    '吞拿魚酒盗',
    'MAGURO SHUTO',
    'Tuna internal organs pickle',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455684',
    '2026-01-07T12:00:30.455685'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '2b4fc37e-1347-4720-b582-04930d8eaa05',
    'GGJ-10060017',
    '鰹魚酒盗',
    '鰹魚酒盗',
    'KATSUO SHUTO',
    'Bonito internal organs pickle (500g)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455693',
    '2026-01-07T12:00:30.455695'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '6e46cbdd-2f86-4734-8793-1dafee1dd210',
    'GGJ-40010036',
    '七味魚翅乾',
    '七味魚翅乾',
    'EIHIRE',
    'Dried mottled skate fin (500g)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455703',
    '2026-01-07T12:00:30.455704'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '6804e4ab-0649-4325-9df5-f4237ca0ca76',
    'GGJ-60120084',
    '山椒幼銀魚',
    '山椒幼銀魚',
    'SANSHO CHIRIMEN JAKO',
    'Dried baby sardine w/sansho (500g)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455712',
    '2026-01-07T12:00:30.455713'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9f6221d4-db41-454d-84c0-ce6b2731d343',
    'GGJ-60120076',
    '三文魚乾',
    '三文魚乾',
    'SAKE TOBA',
    'Dried salmon (~500g)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455722',
    '2026-01-07T12:00:30.455723'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '22860a19-d389-46d0-a17b-f55722992029',
    'GGJ-60120025',
    '桜花蝦乾（台湾）',
    '桜花蝦乾（台湾）',
    NULL,
    'Dried sakura shrimp Taiwan (500g)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455731',
    '2026-01-07T12:00:30.455733'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a5c95ed0-da5f-476e-b576-b7186e4e0f96',
    'GGJ-40030050',
    '魷魚鹽辛',
    '魷魚鹽辛',
    'IKA SHIOKARA',
    'Squid pickle in salt (1kg)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455744',
    '2026-01-07T12:00:30.455746'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '81b6f783-119a-46ed-a63c-401253f858c1',
    'GGJ-60120120',
    '梅水晶',
    '梅水晶',
    'UME SUISHO',
    'Shark cartilage w/ plum mix (700g)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455755',
    '2026-01-07T12:00:30.455756'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4a2e7e0d-f04c-4374-9564-82f87b416065',
    'GGJ-60120006',
    '幼銀魚',
    '幼銀魚',
    'CHIRIMEN JAKO',
    'Dried baby sardine (1kg)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455764',
    '2026-01-07T12:00:30.455765'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'acc970df-9ef8-4c8c-a56d-63ca798fbef9',
    'GGJ-40070003',
    '餃子',
    '餃子',
    NULL,
    'Dumpling (50pc)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455774',
    '2026-01-07T12:00:30.455775'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '83a87e81-1ee6-422a-83cf-2513fc95ada6',
    'GGJ-40070088',
    '煎餃子',
    '煎餃子',
    NULL,
    'Fry dumpling (30pc)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455783',
    '2026-01-07T12:00:30.455784'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c9aa9a48-0138-4273-b05d-08ad1d4aeae8',
    'GGJ-40070050',
    '牛肉薯餅',
    '牛肉薯餅',
    NULL,
    'Beef croquette (750g)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455792',
    '2026-01-07T12:00:30.455793'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '21ca779e-ec65-4f53-9e72-24d9b0f8506e',
    'GGJ-40070010',
    '雞肉軟骨棒',
    '雞肉軟骨棒',
    'TSUKUNE',
    'Cartilage on skewer (50 pc)',
    '急凍/冷藏 > 加工/小食',
    '急凍/冷藏',
    '加工/小食',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455801',
    '2026-01-07T12:00:30.455803'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7094fbb8-f8ec-4929-986b-d8f1b47d0ef0',
    'GGJ-60120015',
    '黒薯糕',
    '黒薯糕',
    NULL,
    'Black konjac (250g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455810',
    '2026-01-07T12:00:30.455812'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'ba83a1bf-3305-49b0-b140-558601fd5fd9',
    'GGJ-60120087',
    '白薯糕',
    '白薯糕',
    NULL,
    'White konjac (250g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455819',
    '2026-01-07T12:00:30.455821'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '50794862-3808-432a-ad97-20823c7fd8ad',
    'GGJ-60120027',
    '水浸粉絲',
    '水浸粉絲',
    'SHIRATAKI',
    'Konjac strings (200g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455829',
    '2026-01-07T12:00:30.455831'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c23dce4e-ae5d-4d0b-8ed0-91859612db5d',
    'GGJ-40070014',
    '油揚（炸豆腐）',
    '油揚（炸豆腐）',
    'ABURAAGE',
    'Fry bean curd (3pc)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455838',
    '2026-01-07T12:00:30.455840'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'be023298-c6d6-4503-a6eb-7fcea840a5a1',
    'GGJ-40070062',
    '味附水雲（三杯醋）',
    '味附水雲（三杯醋）',
    NULL,
    'Mozuku seaweed in vinegar (3pk)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455849',
    '2026-01-07T12:00:30.455850'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '37096c70-5244-44cc-a349-b13c9f4798eb',
    'GGJ-60120021',
    '罐裝蘑菇（滑子菇）',
    '罐裝蘑菇（滑子菇）',
    'NAMEKO',
    'Scotch mushroom canned (400g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455858',
    '2026-01-07T12:00:30.455861'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '509a634b-0493-45ce-b525-35fb7f17b2da',
    'GGJ-40070023',
    '餃子皮',
    '餃子皮',
    NULL,
    'Dumpling skin (24pc)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455868',
    '2026-01-07T12:00:30.455870'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd7ef4aea-2dc3-4b26-84b9-9808e86fd8bb',
    'GGJ-40070002',
    '急凍枝豆',
    '急凍枝豆',
    'EDAMAME',
    'Frozen green soybean (500g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455903',
    '2026-01-07T12:00:30.455905'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e4fe7adc-dbeb-4925-a32c-dd377cec4147',
    'GGJ-60120002',
    '紅豆（罐庄）',
    '紅豆（罐庄）',
    NULL,
    'Red bean canned (430g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455913',
    '2026-01-07T12:00:30.455915'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e75c625a-b67b-49ea-8d1b-bcb8ada600d4',
    'GGJ-60120016',
    '高野豆腐',
    '高野豆腐',
    'TAKANO TOFU',
    'Dried bean curd (16.4g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455922',
    '2026-01-07T12:00:30.455924'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1f29eeb0-a1dc-4aad-bb5c-508a9a01fe26',
    'GGJ-40070049',
    '急凍六方里芋',
    '急凍六方里芋',
    'SATOIMO',
    'Frozen dice-cut taro (500g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455932',
    '2026-01-07T12:00:30.455933'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f2883e3d-d2c6-4576-a49c-8228d7cb570f',
    'GGJ-60120069',
    '絹豆腐',
    '絹豆腐',
    'KINU TOFU',
    'Soft bean curd (400g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455940',
    '2026-01-07T12:00:30.455942'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5f5efc61-38f0-417b-a2de-68f7372ac1a2',
    'GGJ-60120079',
    '木棉豆腐',
    '木棉豆腐',
    'MOMEN TOFU',
    'Hard bean curd (400g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455949',
    '2026-01-07T12:00:30.455951'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e4ab38d8-b118-4bd4-ab0b-7d68a7172455',
    'GGJ-10060007',
    '厚揚（炸豆腐）',
    '厚揚（炸豆腐）',
    'ATSUAGE',
    'Deep-fried bean curd (6pc)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455959',
    '2026-01-07T12:00:30.455960'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e324d768-c736-4f86-8883-462cb1801116',
    'GGJ-60120060',
    '蜜柑（罐庄）',
    '蜜柑（罐庄）',
    NULL,
    'Mandarin orange canned (435g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455969',
    '2026-01-07T12:00:30.455970'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '96aeae9e-0518-4931-8098-c4118110e1d2',
    'GGJ-40070095',
    '無皮枝豆',
    '無皮枝豆',
    'MUKI EDAMAME',
    'Frozen green soybean w/o skin (500g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455980',
    '2026-01-07T12:00:30.455982'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '3dda5606-0ea6-4450-b30c-0ba88f664301',
    'GGJ-60120001',
    '味附乾瓢',
    '味附乾瓢',
    'AJITSUKE KANPYO',
    'Seasoned gourd (1kg)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455989',
    '2026-01-07T12:00:30.455990'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '6d28f601-e867-4bd1-ac28-9a0905d21b5f',
    'GGJ-60120116',
    '罐裝鵪鶉蛋',
    '罐裝鵪鶉蛋',
    'UZURA TAMAGO',
    'Quail egg canned (820g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.455998',
    '2026-01-07T12:00:30.455999'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '627a497a-5c24-4e5f-ba6f-6ff1dff3c470',
    'GGJ-40070208',
    '芝士年糕 (40g)',
    '芝士年糕 (40g)',
    NULL,
    'Rice cake w/ cheese & potato (20pc)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456007',
    '2026-01-07T12:00:30.456009'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'faceab3d-6a28-4154-a846-200142246318',
    'GGJ-40070015',
    '味附油揚（三角）',
    '味附油揚（三角）',
    NULL,
    'Seasoned fry bean curd triangular (60pc)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456016',
    '2026-01-07T12:00:30.456018'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f4169b9e-52f6-44dc-a699-feade9233e3b',
    'GGJ-40070102',
    '南瓜薯餅',
    '南瓜薯餅',
    NULL,
    'Pumpkin croquette (750g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456025',
    '2026-01-07T12:00:30.456027'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1f01faa1-37a2-4f63-a375-a095be71442f',
    'GGJ-60120037',
    '山桃蜜糖漬',
    '山桃蜜糖漬',
    'YAMAMOMO',
    'Bayberry w/ syrup (500g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456034',
    '2026-01-07T12:00:30.456035'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'ff016829-a5c1-410e-81d6-dbb37a654f15',
    'GGJ-40070077',
    '急凍一口甜薯(10g)',
    '急凍一口甜薯(10g)',
    'HITOKUCHI SATSUMAIMO',
    'Mouthful sweet potato (50pc)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456042',
    '2026-01-07T12:00:30.456044'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'ebfb45b3-cd60-4436-b811-0b9d618524b2',
    'GGJ-60120031',
    '京之豆乳',
    '京之豆乳',
    NULL,
    'Kyo soy milk (1L)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456051',
    '2026-01-07T12:00:30.456053'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'bdd7a503-57f6-4728-b81f-e5a5ef9ec1db',
    'GGJ-40070004',
    '大福皮',
    '大福皮',
    'GYUHI',
    'Crepe (10pc)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456061',
    '2026-01-07T12:00:30.456062'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5b4b31bf-815f-4fe8-a7b7-d01274207395',
    'GGJ-20010271',
    '味付竹筍',
    '味付竹筍',
    NULL,
    'Seasoned bamboo shoot canned (2.95kg)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456074',
    '2026-01-07T12:00:30.456076'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e5b31b51-886d-4671-825c-2e7634262eab',
    'GGJ-60120014',
    '千切大根',
    '千切大根',
    'KIRIBOSHI DAIKON',
    'Dried white radish cut (500g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456084',
    '2026-01-07T12:00:30.456085'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'b17eb005-2cbc-4251-a3a5-b65b2f0d18fb',
    'GGJ-60120018',
    '栗甘露煮',
    '栗甘露煮',
    'KURI KANRONI',
    'Chestnut cooked w/ honeydew (1kg)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456093',
    '2026-01-07T12:00:30.456095'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '897d48c4-20e2-497d-a2b6-efd7eafd2fdd',
    'GGJ-60120044',
    '黒豆蜜煮',
    '黒豆蜜煮',
    'KUROMAME',
    'Black bean cooked w/ syrup (1kg)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456102',
    '2026-01-07T12:00:30.456104'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '5831e390-e1ea-479e-b6a9-111edad5d8d4',
    'GGJ-60120043',
    '湯葉',
    '湯葉',
    'YUBA TORO',
    'Bean curd skin (500g)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456111',
    '2026-01-07T12:00:30.456112'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '36f2fcb4-cc92-42cc-b658-ee325aea93b3',
    'GGJ-MIS-MIS-0573',
    '味付乾瓢',
    '味付乾瓢',
    NULL,
    'Aji tsuki gourd',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456123',
    '2026-01-07T12:00:30.456124'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'e6f08800-2d0f-41c8-a521-77a7b107aaf0',
    'GGJ-60120011',
    '乾瓢（無味）',
    '乾瓢（無味）',
    NULL,
    'Dried gourd (1kg)',
    '雜項 > 雜項',
    '雜項',
    '雜項',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456132',
    '2026-01-07T12:00:30.456134'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '41db72a3-4ef3-452f-ae44-1e0e45d231d7',
    'GGJ-60090062',
    '岩鹽粉',
    '岩鹽粉',
    NULL,
    'Rock salt fine (1KG)',
    '雜項 > 廚具/清潔',
    '雜項',
    '廚具/清潔',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456141',
    '2026-01-07T12:00:30.456142'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'a14a0b54-a765-45c7-a959-a718aec0fa4e',
    'GGJ-MIS-KIT-0576',
    'Kitchen Gard 廚房消毒劑 1L　（填充）',
    'Kitchen Gard 廚房消毒劑 1L　（填充）',
    NULL,
    'Kitchen Sterilizer 1L Refill',
    '雜項 > 廚具/清潔',
    '雜項',
    '廚具/清潔',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456152',
    '2026-01-07T12:00:30.456153'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '578461c9-8eaf-4520-afd8-8adcea70226f',
    'GGJ-MIS-KIT-0577',
    'Kitchen Gard 廚房消毒劑 1L　(有噴咀)',
    'Kitchen Gard 廚房消毒劑 1L　(有噴咀)',
    NULL,
    'Kitchen Sterilizer 1L With Spray',
    '雜項 > 廚具/清潔',
    '雜項',
    '廚具/清潔',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456166',
    '2026-01-07T12:00:30.456167'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '47be86ad-f058-442f-91bf-f8f1403c6b44',
    'GGJ-70040014',
    '固形燃料',
    '固形燃料',
    NULL,
    'Solid fuel (40pc)',
    '雜項 > 廚具/清潔',
    '雜項',
    '廚具/清潔',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456175',
    '2026-01-07T12:00:30.456176'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '31ca2c95-a4d1-4bff-8be5-5768e2714f2a',
    'GGJ-70010042',
    '平串 (15cm)',
    '平串 (15cm)',
    NULL,
    'Flat bamboo stick (100pc)',
    '雜項 > 廚具/清潔',
    '雜項',
    '廚具/清潔',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456184',
    '2026-01-07T12:00:30.456186'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'c9d6757a-e222-4182-95e0-f9fa936b7d7a',
    'GGJ-MIS-KIT-0580',
    '花結串 (9cm)',
    '花結串 (9cm)',
    NULL,
    'bamboo stick 9cm (100pc)',
    '雜項 > 廚具/清潔',
    '雜項',
    '廚具/清潔',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456195',
    '2026-01-07T12:00:30.456197'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4c53ebc9-d69e-4d86-bab0-443e08c94097',
    'GGJ-70010068',
    '銀杏串',
    '銀杏串',
    NULL,
    'Ginkgo stick',
    '雜項 > 廚具/清潔',
    '雜項',
    '廚具/清潔',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456204',
    '2026-01-07T12:00:30.456206'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'cc4e1fa0-69b6-4b6d-98d9-66e9926e2b22',
    'GGJ-70010007',
    '天婦羅紙 (100PC)',
    '天婦羅紙 (100PC)',
    NULL,
    'Tempura paper (100pc)',
    '雜項 > 廚具/清潔',
    '雜項',
    '廚具/清潔',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456213',
    '2026-01-07T12:00:30.456214'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'ee0fe794-b59f-428a-b188-d67c26a2671d',
    'GGJ-70010003',
    '吸水紙',
    '吸水紙',
    NULL,
    'Fish paper (2roll/pk)',
    '雜項 > 廚具/清潔',
    '雜項',
    '廚具/清潔',
    'PK',
    'SOURCE: DRY LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456222',
    '2026-01-07T12:00:30.456223'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'ab929867-f803-4163-8e79-c2b406acba2b',
    'GGJ-MIS-TEA-0584',
    '宇治之露玄米茶 (200g)',
    '宇治之露玄米茶 (200g)',
    'GENMAI CHA',
    NULL,
    '雜項 > 茶類',
    '雜項',
    '茶類',
    '200g',
    'PK',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456233',
    '2026-01-07T12:00:30.456235'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1bc78747-f558-4e44-a4b7-6fddf4834cd1',
    'GGJ-MIS-TEA-0585',
    '香焙茶（宇治乃露）200G',
    '香焙茶（宇治乃露）200G',
    'HOUJICHA (UJINOTSUYU)',
    NULL,
    '雜項 > 茶類',
    '雜項',
    '茶類',
    '200g',
    'PK',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456244',
    '2026-01-07T12:00:30.456246'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '51d047f7-5dbc-45ff-9604-ef4ba1f23296',
    'GGJ-MIS-TEA-0586',
    '小山園 綠茶 200g',
    '小山園 綠茶 200g',
    NULL,
    'Green tea (Koyamaen)',
    '雜項 > 茶類',
    '雜項',
    '茶類',
    '200g',
    'PK',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456255',
    '2026-01-07T12:00:30.456257'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'db161472-4286-4141-bfa6-02383a508f7c',
    'GGJ-MIS-TEA-0587',
    '粉茶 (綱島園綠茶粉)',
    '粉茶 (綱島園綠茶粉)',
    'KONA CHA',
    NULL,
    '雜項 > 茶類',
    '雜項',
    '茶類',
    '400g',
    'PK',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456267',
    '2026-01-07T12:00:30.456269'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1648950c-e2ff-4b46-902a-aa4774e7e831',
    'GGJ-RIC-JRC-0588',
    '越光米（魚沼）',
    '越光米（魚沼）',
    'Uonuma Koshi Hikari',
    'MIDDLE-HIGH Stickiness',
    '米/穀類 > 日本米',
    '米/穀類',
    '日本米',
    'KG',
    'SOURCE: RICE LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456278',
    '2026-01-07T12:00:30.456279'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '6ed3a30b-046d-465c-a27f-2e7e4b21d1ba',
    'GGJ-RIC-JRC-0589',
    '越光米（新潟）香港精米',
    '越光米（新潟）香港精米',
    'Niigata Koshi Hikari',
    'MIDDLE-HIGH Stickiness',
    '米/穀類 > 日本米',
    '米/穀類',
    '日本米',
    'KG',
    'SOURCE: RICE LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456288',
    '2026-01-07T12:00:30.456290'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '7fb3e6c6-56bf-465e-84be-f6a0b9c5d8d5',
    'GGJ-RIC-JRC-0590',
    '山形生抜米',
    '山形生抜米',
    'Yamagata haenuki',
    'MIDDLE Stickiness',
    '米/穀類 > 日本米',
    '米/穀類',
    '日本米',
    'KG',
    'SOURCE: RICE LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456299',
    '2026-01-07T12:00:30.456300'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'f50f14e5-f474-4bf5-9c63-254d2840a4c9',
    'GGJ-RIC-JRC-0591',
    '越息吹',
    '越息吹',
    'Niigata Koshi Ibuki',
    'LOW Stickiness',
    '米/穀類 > 日本米',
    '米/穀類',
    '日本米',
    'KG',
    'SOURCE: RICE LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456310',
    '2026-01-07T12:00:30.456312'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4c549556-c989-4e97-881f-af3a22eddf97',
    'GGJ-RIC-JRC-0592',
    '久保田新鮮米(混合米)',
    '久保田新鮮米(混合米)',
    'KUBOTA MIX RICE',
    'LOW Stickiness',
    '米/穀類 > 日本米',
    '米/穀類',
    '日本米',
    'KG',
    'SOURCE: RICE LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456320',
    '2026-01-07T12:00:30.456322'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'd7e028ea-098f-460b-a1ee-9ae5eba04038',
    'GGJ-FRZ-WAG-0593',
    'A5 西冷',
    'A5 西冷',
    'A5 SIRLOIN',
    NULL,
    '急凍/冷藏 > 和牛/豚',
    '急凍/冷藏',
    '和牛/豚',
    'KG',
    'SOURCE: BEEF LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456331',
    '2026-01-07T12:00:30.456332'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '79feb8eb-391f-496e-b091-85fe61e068a6',
    'GGJ-FRZ-WAG-0594',
    'A5肉眼',
    'A5肉眼',
    'A5 RIB EYE',
    NULL,
    '急凍/冷藏 > 和牛/豚',
    '急凍/冷藏',
    '和牛/豚',
    'KG',
    'SOURCE: BEEF LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456342',
    '2026-01-07T12:00:30.456344'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9c8cd8cd-192e-45fb-857d-2c38229eaa82',
    'GGJ-FRZ-WAG-0595',
    'A5牛柳',
    'A5牛柳',
    'A5 TENDERLION',
    NULL,
    '急凍/冷藏 > 和牛/豚',
    '急凍/冷藏',
    '和牛/豚',
    'KG',
    'SOURCE: BEEF LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456353',
    '2026-01-07T12:00:30.456355'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '9190c51d-96df-4193-b674-cb9ca1bb22fb',
    'GGJ-FRZ-WAG-0596',
    'A4 西冷',
    'A4 西冷',
    'A4 SIRLOIN',
    NULL,
    '急凍/冷藏 > 和牛/豚',
    '急凍/冷藏',
    '和牛/豚',
    'KG',
    'SOURCE: BEEF LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456363',
    '2026-01-07T12:00:30.456365'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    'aeb2d0b4-3db9-421e-af35-002a04ed72ed',
    'GGJ-FRZ-WAG-0597',
    'A4肉眼',
    'A4肉眼',
    'A4 RIB EYE',
    NULL,
    '急凍/冷藏 > 和牛/豚',
    '急凍/冷藏',
    '和牛/豚',
    'KG',
    'SOURCE: BEEF LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456377',
    '2026-01-07T12:00:30.456378'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '8db9427b-f9a4-4bee-ad0a-3f3829cf74d5',
    'GGJ-FRZ-WAG-0598',
    'A4牛柳',
    'A4牛柳',
    'A4 TENDERLION',
    NULL,
    '急凍/冷藏 > 和牛/豚',
    '急凍/冷藏',
    '和牛/豚',
    'KG',
    'SOURCE: BEEF LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456387',
    '2026-01-07T12:00:30.456388'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '4a0e15eb-ac9b-4a50-b999-13634cae440d',
    'GGJ-FRZ-WAG-0599',
    '北海道豚腩肉',
    '北海道豚腩肉',
    'MIYAZAKI PORK BELLY',
    NULL,
    '急凍/冷藏 > 和牛/豚',
    '急凍/冷藏',
    '和牛/豚',
    'KG',
    'SOURCE: BEEF LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456397',
    '2026-01-07T12:00:30.456398'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

INSERT INTO products (id, sku, name, name_zh, name_ja, name_en, category, category_main, category_sub, unit, season_tag, source, status, stock_quantity, created_at, updated_at)
VALUES (
    '1ec4de10-68dc-4a09-a099-28c2f0962e94',
    'GGJ-FRZ-WAG-0600',
    '北海道豚扒',
    '北海道豚扒',
    'MIYAZAKI PORK STRIPLOIN',
    NULL,
    '急凍/冷藏 > 和牛/豚',
    '急凍/冷藏',
    '和牛/豚',
    'KG',
    'SOURCE: BEEF LIST',
    'gogojap_csv',
    'active',
    0,
    '2026-01-07T12:00:30.456407',
    '2026-01-07T12:00:30.456408'
) ON CONFLICT (sku) DO UPDATE SET
    name = EXCLUDED.name,
    name_zh = EXCLUDED.name_zh,
    name_ja = EXCLUDED.name_ja,
    name_en = EXCLUDED.name_en,
    category = EXCLUDED.category,
    category_main = EXCLUDED.category_main,
    category_sub = EXCLUDED.category_sub,
    unit = EXCLUDED.unit,
    season_tag = EXCLUDED.season_tag,
    updated_at = EXCLUDED.updated_at;

COMMIT;
