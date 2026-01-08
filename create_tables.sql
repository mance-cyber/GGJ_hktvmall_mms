-- 創建類別數據庫表
CREATE TABLE IF NOT EXISTS category_databases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    hktv_category_url TEXT,
    total_products INTEGER DEFAULT 0,
    last_scraped_at TIMESTAMP,
    scrape_frequency VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 創建類別商品表
CREATE TABLE IF NOT EXISTS category_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES category_databases(id) ON DELETE CASCADE NOT NULL,
    name VARCHAR(500) NOT NULL,
    url TEXT NOT NULL,
    sku VARCHAR(255),
    brand VARCHAR(255),
    price NUMERIC(10, 2),
    original_price NUMERIC(10, 2),
    discount_percent NUMERIC(5, 2),
    attributes JSONB,
    unit_price NUMERIC(10, 2),
    unit_type VARCHAR(50) DEFAULT 'per_100g',
    stock_status VARCHAR(50),
    is_available BOOLEAN DEFAULT true,
    rating NUMERIC(3, 2),
    review_count INTEGER,
    image_url TEXT,
    first_seen_at TIMESTAMP DEFAULT NOW(),
    last_updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_category_products_category ON category_products(category_id);
CREATE INDEX IF NOT EXISTS idx_category_products_url ON category_products(url);
CREATE INDEX IF NOT EXISTS idx_category_products_brand ON category_products(brand);
CREATE INDEX IF NOT EXISTS idx_category_products_unit_price ON category_products(unit_price);

-- 創建價格快照表
CREATE TABLE IF NOT EXISTS category_price_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_product_id UUID REFERENCES category_products(id) ON DELETE CASCADE NOT NULL,
    price NUMERIC(10, 2),
    original_price NUMERIC(10, 2),
    discount_percent NUMERIC(5, 2),
    unit_price NUMERIC(10, 2),
    stock_status VARCHAR(50),
    is_available BOOLEAN,
    scraped_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_price_snapshots_product ON category_price_snapshots(category_product_id);
CREATE INDEX IF NOT EXISTS idx_price_snapshots_scraped_at ON category_price_snapshots(scraped_at);

-- 創建 AI 分析報告表
CREATE TABLE IF NOT EXISTS category_analysis_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id UUID REFERENCES category_databases(id) ON DELETE CASCADE NOT NULL,
    report_type VARCHAR(50),
    report_title VARCHAR(255),
    summary TEXT,
    key_findings JSONB,
    recommendations JSONB,
    data_snapshot JSONB,
    generated_by VARCHAR(50),
    generated_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analysis_reports_category ON category_analysis_reports(category_id);
CREATE INDEX IF NOT EXISTS idx_analysis_reports_type ON category_analysis_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_analysis_reports_generated_at ON category_analysis_reports(generated_at);
