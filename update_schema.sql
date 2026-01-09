-- =============================================
-- 用戶與權限更新腳本
-- 請在數據庫中執行此 SQL 以添加用戶表
-- =============================================

-- 1. 創建用戶表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'viewer', -- 'admin', 'operator', 'viewer'
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 創建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 3. 創建自動更新時間戳的觸發器 (如果函數 update_updated_at_column 已存在)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_users_updated_at') THEN
        CREATE TRIGGER update_users_updated_at
            BEFORE UPDATE ON users
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    END IF;
END
$$;

-- 4. 插入初始管理員用戶 (密碼: admin123)
-- 注意: 這裡的 hashed_password 是 'admin123' 的 bcrypt hash
-- 如果您想使用不同的密碼，請使用 Python passlib 生成新的 hash
INSERT INTO users (email, hashed_password, full_name, role, is_active)
VALUES (
    'admin@example.com', 
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxwKc.60MHJ6.z1/..fN.js.F.s3.', 
    'System Admin', 
    'admin', 
    true
)
ON CONFLICT (email) DO NOTHING;

