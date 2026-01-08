-- =============================================
-- HKTVmall AI 營運系統 - 數據庫 Schema
-- PostgreSQL 16+
-- =============================================

-- =============================================
-- 競品監測相關表
-- =============================================

-- 競爭對手
CREATE TABLE competitors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(100) NOT NULL,  -- 'hktvmall', 'watsons', 'mannings', etc.
    base_url VARCHAR(500),
    notes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE competitors IS '競爭對手/店舖';
COMMENT ON COLUMN competitors.platform IS '平台名稱：hktvmall, watsons, mannings, ztore 等';

-- 競品商品
CREATE TABLE competitor_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competitor_id UUID REFERENCES competitors(id) ON DELETE CASCADE,
    name VARCHAR(500) NOT NULL,
    url VARCHAR(1000) NOT NULL UNIQUE,
    sku VARCHAR(100),
    category VARCHAR(255),
    image_url VARCHAR(1000),
    is_active BOOLEAN DEFAULT true,
    last_scraped_at TIMESTAMP WITH TIME ZONE,
    scrape_error TEXT,  -- 最後一次爬取錯誤
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE competitor_products IS '競品商品監測列表';

-- 價格快照（歷史記錄）
CREATE TABLE price_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competitor_product_id UUID REFERENCES competitor_products(id) ON DELETE CASCADE,
    price DECIMAL(10, 2),
    original_price DECIMAL(10, 2),  -- 原價（劃線價）
    discount_percent DECIMAL(5, 2),
    currency VARCHAR(10) DEFAULT 'HKD',
    stock_status VARCHAR(50),  -- 'in_stock', 'out_of_stock', 'low_stock', 'preorder'
    rating DECIMAL(3, 2),
    review_count INTEGER,
    promotion_text TEXT,  -- 促銷文字
    raw_data JSONB,  -- 完整爬取數據（保留原始資料）
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE price_snapshots IS '價格歷史快照';
COMMENT ON COLUMN price_snapshots.raw_data IS 'Firecrawl 返回的完整數據';

-- 價格警報
CREATE TABLE price_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competitor_product_id UUID REFERENCES competitor_products(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,  -- 'price_drop', 'price_increase', 'out_of_stock', 'back_in_stock'
    old_value VARCHAR(100),
    new_value VARCHAR(100),
    change_percent DECIMAL(5, 2),
    is_read BOOLEAN DEFAULT false,
    is_notified BOOLEAN DEFAULT false,  -- 是否已發送通知
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE price_alerts IS '價格/庫存變動警報';

-- =============================================
-- 自家商品相關表
-- =============================================

-- 商品
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(100) UNIQUE NOT NULL,
    hktv_product_id VARCHAR(100),  -- HKTVmall 商品 ID
    name VARCHAR(500) NOT NULL,
    description TEXT,
    category VARCHAR(255),
    brand VARCHAR(255),
    price DECIMAL(10, 2),
    cost DECIMAL(10, 2),  -- 成本價
    stock_quantity INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'active',  -- 'active', 'inactive', 'pending'
    images JSONB DEFAULT '[]',  -- ["url1", "url2"]
    attributes JSONB DEFAULT '{}',  -- {"color": "red", "size": "M", "weight": "500g"}
    hktv_data JSONB,  -- HKTVmall API 原始數據
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE products IS '自家商品';
COMMENT ON COLUMN products.hktv_data IS 'HKTVmall MMS API 返回的原始數據';

-- 商品歷史記錄
CREATE TABLE product_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    field_changed VARCHAR(100) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE product_history IS '商品修改歷史';

-- 商品-競品關聯（用於價格比較）
CREATE TABLE product_competitor_mapping (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    competitor_product_id UUID REFERENCES competitor_products(id) ON DELETE CASCADE,
    match_confidence DECIMAL(3, 2),  -- 0.00 - 1.00 匹配信心度
    is_verified BOOLEAN DEFAULT false,  -- 人工確認
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(product_id, competitor_product_id)
);

COMMENT ON TABLE product_competitor_mapping IS '自家商品與競品的對應關係';

-- =============================================
-- AI 內容相關表
-- =============================================

-- AI 生成內容
CREATE TABLE ai_contents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    content_type VARCHAR(50) NOT NULL,  -- 'title', 'description', 'selling_points', 'full_copy'
    style VARCHAR(50),  -- 'formal', 'casual', 'playful', 'professional'
    language VARCHAR(10) DEFAULT 'zh-HK',  -- 'zh-HK', 'zh-TW', 'en'
    content TEXT NOT NULL,
    content_json JSONB,  -- 結構化內容 {"title": "", "points": [], "description": ""}
    version INTEGER DEFAULT 1,
    status VARCHAR(50) DEFAULT 'draft',  -- 'draft', 'approved', 'published', 'rejected'
    metadata JSONB,  -- {"tokens_used": 500, "model": "claude-sonnet", "duration_ms": 1200}
    input_data JSONB,  -- 生成時的輸入資料
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_at TIMESTAMP WITH TIME ZONE,
    approved_by VARCHAR(255),
    rejected_reason TEXT
);

COMMENT ON TABLE ai_contents IS 'AI 生成的內容';

-- =============================================
-- 訂單相關表（為 MMS API 預留）
-- =============================================

-- 訂單
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hktv_order_id VARCHAR(100) UNIQUE,
    order_number VARCHAR(100),
    status VARCHAR(50),  -- 'pending', 'confirmed', 'shipped', 'delivered', 'cancelled'
    total_amount DECIMAL(10, 2),
    currency VARCHAR(10) DEFAULT 'HKD',
    customer_info JSONB,  -- {"name": "", "phone": "", "email": ""}
    shipping_info JSONB,  -- {"address": "", "method": "", "fee": 0}
    payment_info JSONB,   -- {"method": "", "status": ""}
    order_date TIMESTAMP WITH TIME ZONE,
    shipped_date TIMESTAMP WITH TIME ZONE,
    delivered_date TIMESTAMP WITH TIME ZONE,
    raw_data JSONB,  -- MMS API 原始數據
    synced_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE orders IS '訂單（從 HKTVmall 同步）';

-- 訂單項目
CREATE TABLE order_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    hktv_product_id VARCHAR(100),
    sku VARCHAR(100),
    name VARCHAR(500),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2),
    subtotal DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================
-- 系統相關表
-- =============================================

-- 爬取任務日誌
CREATE TABLE scrape_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(255),  -- Celery task ID
    task_type VARCHAR(50),  -- 'competitor_scrape', 'full_scrape', 'single_product'
    competitor_id UUID REFERENCES competitors(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL,  -- 'pending', 'running', 'success', 'partial', 'failed'
    products_total INTEGER DEFAULT 0,
    products_scraped INTEGER DEFAULT 0,
    products_failed INTEGER DEFAULT 0,
    errors JSONB,  -- [{"product_id": "", "error": ""}]
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE scrape_logs IS '爬取任務日誌';

-- 同步日誌
CREATE TABLE sync_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(255),
    sync_type VARCHAR(50),  -- 'products', 'orders', 'inventory'
    source VARCHAR(50),  -- 'hktv_mms'
    status VARCHAR(50) NOT NULL,
    records_total INTEGER DEFAULT 0,
    records_synced INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,
    errors JSONB,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE sync_logs IS 'HKTVmall 同步日誌';

-- 系統設定
CREATE TABLE settings (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE settings IS '系統設定';

-- =============================================
-- 索引
-- =============================================

-- 競品相關
CREATE INDEX idx_competitor_products_competitor_id ON competitor_products(competitor_id);
CREATE INDEX idx_competitor_products_url ON competitor_products(url);
CREATE INDEX idx_competitor_products_is_active ON competitor_products(is_active);

-- 價格快照
CREATE INDEX idx_price_snapshots_product_id ON price_snapshots(competitor_product_id);
CREATE INDEX idx_price_snapshots_scraped_at ON price_snapshots(scraped_at DESC);

-- 警報
CREATE INDEX idx_price_alerts_product_id ON price_alerts(competitor_product_id);
CREATE INDEX idx_price_alerts_created_at ON price_alerts(created_at DESC);
CREATE INDEX idx_price_alerts_is_read ON price_alerts(is_read) WHERE is_read = false;
CREATE INDEX idx_price_alerts_type ON price_alerts(alert_type);

-- 商品
CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_hktv_id ON products(hktv_product_id);
CREATE INDEX idx_products_status ON products(status);

-- AI 內容
CREATE INDEX idx_ai_contents_product_id ON ai_contents(product_id);
CREATE INDEX idx_ai_contents_status ON ai_contents(status);
CREATE INDEX idx_ai_contents_type ON ai_contents(content_type);

-- 訂單
CREATE INDEX idx_orders_hktv_id ON orders(hktv_order_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_date ON orders(order_date DESC);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);

-- 日誌
CREATE INDEX idx_scrape_logs_status ON scrape_logs(status);
CREATE INDEX idx_scrape_logs_created_at ON scrape_logs(created_at DESC);

-- =============================================
-- 觸發器：自動更新 updated_at
-- =============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_competitors_updated_at
    BEFORE UPDATE ON competitors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_competitor_products_updated_at
    BEFORE UPDATE ON competitor_products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orders_updated_at
    BEFORE UPDATE ON orders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_settings_updated_at
    BEFORE UPDATE ON settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- 初始設定數據
-- =============================================

INSERT INTO settings (key, value, description) VALUES
('scrape_schedule', '{"enabled": true, "frequency": "daily", "time": "09:00", "timezone": "Asia/Hong_Kong"}', '爬取排程設定'),
('notification', '{"email_enabled": true, "email": "", "price_change_threshold": 10}', '通知設定'),
('ai_generation', '{"default_style": "professional", "default_language": "zh-HK", "model": "claude-sonnet-4-20250514"}', 'AI 生成設定'),
('hktv_sync', '{"enabled": false, "products_interval_hours": 6, "orders_interval_minutes": 15, "inventory_interval_minutes": 30}', 'HKTVmall 同步設定');

-- =============================================
-- 示範數據（可選）
-- =============================================

-- 插入一個示範競爭對手
INSERT INTO competitors (name, platform, base_url, notes) VALUES
('Watsons', 'watsons', 'https://www.watsons.com.hk', '屈臣氏 - 監測保健品類'),
('Mannings', 'mannings', 'https://www.mannings.com.hk', '萬寧 - 監測保健品類'),
('HKTVmall 其他店', 'hktvmall', 'https://www.hktvmall.com', '監測 HKTVmall 其他商戶');


-- =============================================
-- Phase 1: 智能抓取引擎 - 新增表
-- =============================================

-- 平台爬取配置
CREATE TABLE scrape_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform VARCHAR(100) NOT NULL UNIQUE,  -- 'watsons', 'mannings', 'hktvmall', etc.
    name VARCHAR(255) NOT NULL,

    -- 解析配置
    product_schema JSONB,  -- JSON Schema for Firecrawl structured extraction
    selectors JSONB,       -- CSS/XPath selectors for fallback parsing

    -- 請求配置
    user_agents JSONB DEFAULT '[]',  -- User agent rotation pool
    request_headers JSONB DEFAULT '{}',  -- Custom headers
    wait_time_ms INTEGER DEFAULT 3000,
    use_actions BOOLEAN DEFAULT false,  -- Enable Firecrawl Actions
    actions_config JSONB,  -- Actions configuration (scroll, wait, click)

    -- 速率限制
    rate_limit_requests INTEGER DEFAULT 10,  -- Requests per window
    rate_limit_window_seconds INTEGER DEFAULT 60,  -- Window size in seconds
    concurrent_limit INTEGER DEFAULT 3,  -- Max concurrent requests

    -- 重試配置
    max_retries INTEGER DEFAULT 3,
    retry_delay_seconds INTEGER DEFAULT 5,
    exponential_backoff BOOLEAN DEFAULT true,

    -- 代理配置
    proxy_enabled BOOLEAN DEFAULT false,
    proxy_pool JSONB DEFAULT '[]',  -- Proxy server pool

    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE scrape_configs IS '平台爬取配置';
COMMENT ON COLUMN scrape_configs.product_schema IS 'Firecrawl JSON Mode 提取 Schema';
COMMENT ON COLUMN scrape_configs.rate_limit_requests IS '速率限制：每個時間窗口的請求數';

-- 批次導入任務
CREATE TABLE import_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    competitor_id UUID REFERENCES competitors(id) ON DELETE SET NULL,

    -- 任務狀態
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- 'pending', 'processing', 'completed', 'failed', 'cancelled'

    -- 導入來源
    source_type VARCHAR(50) NOT NULL,  -- 'file', 'url_list', 'discovery'
    source_data JSONB,  -- Source configuration {"filename": "", "urls": [], "base_url": ""}

    -- 處理統計
    total_urls INTEGER DEFAULT 0,
    processed_urls INTEGER DEFAULT 0,
    successful_urls INTEGER DEFAULT 0,
    failed_urls INTEGER DEFAULT 0,
    duplicate_urls INTEGER DEFAULT 0,

    -- 驗證結果
    validation_errors JSONB DEFAULT '[]',

    -- 時間戳
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE import_jobs IS '批次導入任務';

-- 導入任務項目
CREATE TABLE import_job_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    import_job_id UUID REFERENCES import_jobs(id) ON DELETE CASCADE,

    url VARCHAR(2000) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- 'pending', 'processing', 'success', 'failed', 'duplicate', 'skipped'

    -- 結果
    competitor_product_id UUID REFERENCES competitor_products(id) ON DELETE SET NULL,
    extracted_data JSONB,  -- Scraped product data before insertion
    error_message TEXT,

    -- 處理時間
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE import_job_items IS '導入任務項目';

-- =============================================
-- Phase 2: 數據分析儀表板 - 新增表
-- =============================================

-- 價格分析聚合表（按日/競品/類別）
CREATE TABLE price_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 聚合維度
    competitor_id UUID REFERENCES competitors(id) ON DELETE CASCADE,
    category VARCHAR(255),
    date DATE NOT NULL,

    -- 價格統計
    avg_price DECIMAL(10, 2),
    min_price DECIMAL(10, 2),
    max_price DECIMAL(10, 2),
    median_price DECIMAL(10, 2),
    price_std_dev DECIMAL(10, 2),

    -- 變動統計
    avg_price_change_percent DECIMAL(5, 2),
    price_drops_count INTEGER DEFAULT 0,
    price_increases_count INTEGER DEFAULT 0,

    -- 庫存統計
    in_stock_count INTEGER DEFAULT 0,
    out_of_stock_count INTEGER DEFAULT 0,
    low_stock_count INTEGER DEFAULT 0,

    -- 商品計數
    total_products INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(competitor_id, category, date)
);

COMMENT ON TABLE price_analytics IS '價格分析聚合數據（按日/競品/類別）';

-- 市場研究報告
CREATE TABLE market_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(255) NOT NULL,
    report_type VARCHAR(50) NOT NULL,  -- 'price_comparison', 'trend_analysis', 'category_overview', 'competitor_analysis'

    -- 報告配置
    config JSONB NOT NULL,  -- Report generation parameters

    -- 報告數據
    data JSONB,  -- Cached report data

    -- 生成狀態
    status VARCHAR(50) NOT NULL DEFAULT 'pending',  -- 'pending', 'generating', 'completed', 'failed'
    error_message TEXT,

    -- 導出
    export_formats JSONB DEFAULT '["csv", "xlsx", "pdf"]',
    file_urls JSONB DEFAULT '{}',  -- {"csv": "url", "xlsx": "url", "pdf": "url"}

    -- 時間
    generated_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,  -- Report cache expiry
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE market_reports IS '市場研究報告';

-- =============================================
-- Phase 3: 系統整合 - 新增表
-- =============================================

-- 通知記錄
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    type VARCHAR(50) NOT NULL,  -- 'price_alert', 'scrape_complete', 'scrape_failed', 'report_ready', 'import_complete'

    -- 關聯
    related_type VARCHAR(50),  -- 'price_alert', 'scrape_log', 'market_report', 'import_job'
    related_id UUID,

    -- 內容
    title VARCHAR(255) NOT NULL,
    message TEXT,
    data JSONB,  -- Additional notification data

    -- 發送狀態
    channels JSONB DEFAULT '["in_app"]',  -- ["in_app", "email", "webhook"]
    sent_at JSONB DEFAULT '{}',  -- {"in_app": "timestamp", "email": "timestamp"}

    -- 已讀狀態
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE notifications IS '系統通知';

-- Webhook 配置
CREATE TABLE webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(255) NOT NULL,
    url VARCHAR(1000) NOT NULL,
    secret VARCHAR(255),  -- HMAC signing secret

    -- 訂閱事件
    events JSONB NOT NULL DEFAULT '["price_alert"]',  -- ["price_alert", "scrape_complete", "report_ready"]

    -- 狀態
    is_active BOOLEAN DEFAULT true,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    last_status_code INTEGER,
    failure_count INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

COMMENT ON TABLE webhooks IS 'Webhook 配置';

-- =============================================
-- 擴展現有表
-- =============================================

-- 為 competitor_products 添加新欄位
ALTER TABLE competitor_products ADD COLUMN IF NOT EXISTS specs JSONB DEFAULT '{}';
ALTER TABLE competitor_products ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE competitor_products ADD COLUMN IF NOT EXISTS brand VARCHAR(255);
ALTER TABLE competitor_products ADD COLUMN IF NOT EXISTS images JSONB DEFAULT '[]';
ALTER TABLE competitor_products ADD COLUMN IF NOT EXISTS scrape_config_override JSONB;

COMMENT ON COLUMN competitor_products.specs IS '商品規格';
COMMENT ON COLUMN competitor_products.images IS '多張商品圖片';

-- 為 competitors 添加爬取配置關聯
ALTER TABLE competitors ADD COLUMN IF NOT EXISTS scrape_config_id UUID REFERENCES scrape_configs(id) ON DELETE SET NULL;
ALTER TABLE competitors ADD COLUMN IF NOT EXISTS category_patterns JSONB DEFAULT '[]';

COMMENT ON COLUMN competitors.scrape_config_id IS '關聯的爬取配置';
COMMENT ON COLUMN competitors.category_patterns IS '類別識別模式';

-- 為 price_snapshots 添加更多數據
ALTER TABLE price_snapshots ADD COLUMN IF NOT EXISTS specs JSONB;
ALTER TABLE price_snapshots ADD COLUMN IF NOT EXISTS images JSONB;
ALTER TABLE price_snapshots ADD COLUMN IF NOT EXISTS brand VARCHAR(255);
ALTER TABLE price_snapshots ADD COLUMN IF NOT EXISTS description TEXT;

-- =============================================
-- 新增索引
-- =============================================

-- 爬取配置
CREATE INDEX idx_scrape_configs_platform ON scrape_configs(platform);
CREATE INDEX idx_scrape_configs_is_active ON scrape_configs(is_active);

-- 導入任務
CREATE INDEX idx_import_jobs_status ON import_jobs(status);
CREATE INDEX idx_import_jobs_competitor_id ON import_jobs(competitor_id);
CREATE INDEX idx_import_jobs_created_at ON import_jobs(created_at DESC);
CREATE INDEX idx_import_job_items_job_id ON import_job_items(import_job_id);
CREATE INDEX idx_import_job_items_status ON import_job_items(status);

-- 價格分析
CREATE INDEX idx_price_analytics_date ON price_analytics(date DESC);
CREATE INDEX idx_price_analytics_competitor ON price_analytics(competitor_id, date DESC);
CREATE INDEX idx_price_analytics_category ON price_analytics(category, date DESC);

-- 報告
CREATE INDEX idx_market_reports_status ON market_reports(status);
CREATE INDEX idx_market_reports_type ON market_reports(report_type);
CREATE INDEX idx_market_reports_created_at ON market_reports(created_at DESC);

-- 通知
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX idx_notifications_is_read ON notifications(is_read) WHERE is_read = false;
CREATE INDEX idx_notifications_type ON notifications(type);

-- Webhooks
CREATE INDEX idx_webhooks_is_active ON webhooks(is_active);

-- =============================================
-- 觸發器：新表 updated_at
-- =============================================

CREATE TRIGGER update_scrape_configs_updated_at
    BEFORE UPDATE ON scrape_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_webhooks_updated_at
    BEFORE UPDATE ON webhooks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- 視圖：自家商品 vs 競品價格比較
-- =============================================

CREATE OR REPLACE VIEW product_price_comparison AS
SELECT
    p.id AS product_id,
    p.sku,
    p.name AS product_name,
    p.price AS our_price,
    p.cost AS our_cost,
    cp.id AS competitor_product_id,
    cp.name AS competitor_product_name,
    cp.url AS competitor_url,
    c.id AS competitor_id,
    c.name AS competitor_name,
    c.platform,
    ps.price AS competitor_price,
    ps.original_price AS competitor_original_price,
    ps.discount_percent AS competitor_discount,
    ps.stock_status AS competitor_stock_status,
    ps.scraped_at AS competitor_last_scraped,
    CASE
        WHEN p.price IS NOT NULL AND ps.price IS NOT NULL AND ps.price > 0
        THEN ROUND((p.price - ps.price) / ps.price * 100, 2)
        ELSE NULL
    END AS price_diff_percent,
    CASE
        WHEN p.price < ps.price THEN 'cheaper'
        WHEN p.price > ps.price THEN 'more_expensive'
        ELSE 'equal'
    END AS price_position,
    CASE
        WHEN p.price IS NOT NULL AND p.cost IS NOT NULL AND p.cost > 0
        THEN ROUND((p.price - p.cost) / p.cost * 100, 2)
        ELSE NULL
    END AS our_margin_percent
FROM products p
LEFT JOIN product_competitor_mapping pcm ON p.id = pcm.product_id
LEFT JOIN competitor_products cp ON pcm.competitor_product_id = cp.id
LEFT JOIN competitors c ON cp.competitor_id = c.id
LEFT JOIN LATERAL (
    SELECT * FROM price_snapshots
    WHERE competitor_product_id = cp.id
    ORDER BY scraped_at DESC
    LIMIT 1
) ps ON true
WHERE p.status = 'active';

COMMENT ON VIEW product_price_comparison IS '自家商品與競品價格比較視圖';

-- =============================================
-- 初始爬取配置
-- =============================================

INSERT INTO scrape_configs (platform, name, product_schema, wait_time_ms, rate_limit_requests, rate_limit_window_seconds) VALUES
('hktvmall', 'HKTVmall', '{
    "type": "object",
    "properties": {
        "product_name": {"type": "string"},
        "current_price": {"type": "number"},
        "original_price": {"type": "number"},
        "currency": {"type": "string"},
        "stock_status": {"type": "string"},
        "rating": {"type": "number"},
        "review_count": {"type": "integer"},
        "sku": {"type": "string"},
        "brand": {"type": "string"},
        "category": {"type": "string"},
        "description": {"type": "string"},
        "promotion_text": {"type": "string"},
        "image_url": {"type": "string"}
    }
}', 3000, 10, 60),
('watsons', 'Watsons 屈臣氏', '{
    "type": "object",
    "properties": {
        "product_name": {"type": "string"},
        "current_price": {"type": "number"},
        "original_price": {"type": "number"},
        "stock_status": {"type": "string"},
        "brand": {"type": "string"}
    }
}', 5000, 5, 60),
('mannings', 'Mannings 萬寧', '{
    "type": "object",
    "properties": {
        "product_name": {"type": "string"},
        "current_price": {"type": "number"},
        "original_price": {"type": "number"},
        "stock_status": {"type": "string"},
        "brand": {"type": "string"}
    }
}', 5000, 5, 60)
ON CONFLICT (platform) DO NOTHING;

-- =============================================
-- AI Agent 對話記錄表 (新增)
-- =============================================

CREATE TABLE IF NOT EXISTS agent_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255),
    slots JSONB DEFAULT '{}',
    current_intent VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES agent_conversations(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'message',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_messages_conversation_id ON agent_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_agent_conversations_updated_at ON agent_conversations(updated_at DESC);
