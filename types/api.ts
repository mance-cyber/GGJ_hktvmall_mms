// ==================== 基礎 API 類型 ====================

/**
 * API 響應包裝器
 */
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

/**
 * 分頁響應
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

/**
 * API 錯誤
 */
export interface ApiError {
  message: string;
  code: string;
  details?: Record<string, any>;
}

// ==================== 儀表板類型 ====================

/**
 * 後端 Dashboard API 原始響應結構
 */
export interface DashboardApiResponse {
  competitors: {
    total: number;
    active: number;
    products_monitored: number;
  };
  alerts: {
    unread: number;
    today: number;
    price_drops: number;
    price_increases: number;
  };
  content: {
    generated_today: number;
    pending_approval: number;
  };
  recent_alerts: Array<{
    id: string;
    product_name: string;
    alert_type: string;
    change_percent: number | null;
    created_at: string;
  }>;
  price_trends: Array<{
    date: string;
    avg_price_change: number;
  }>;
}

/**
 * 儀表板統計數據
 */
export interface DashboardStats {
  competitorsCount: number;
  monitoredProductsCount: number;
  todayAlertsCount: number;
  pendingContentCount: number;
}

/**
 * 價格預警項目
 */
export interface PriceAlert {
  id: number;
  productId: number;
  productName: string;
  productSku: string;
  competitorId: number;
  competitorName: string;
  ourPrice: number;
  competitorPrice: number;
  priceDifference: number;
  priceDifferencePercent: number;
  alertType:
    | "price_higher"
    | "price_lower"
    | "price_equal"
    | "price_drop"
    | "price_increase"
    | "out_of_stock"
    | "back_in_stock";
  severity: "info" | "warning" | "critical";
  isRead: boolean;
  createdAt: string;
}

/**
 * 價格趨勢數據點
 */
export interface PriceTrendDataPoint {
  date: string;
  ourPrice: number;
  competitorPrice?: number;
  averagePrice?: number;
}

/**
 * 儀表板完整數據
 */
export interface DashboardData {
  stats: DashboardStats;
  recentAlerts: PriceAlert[];
  priceTrend: PriceTrendDataPoint[];
}

// ==================== 競爭對手類型 ====================

/**
 * 競爭對手
 */
export interface Competitor {
  id: number;
  name: string;
  platform: "hktvmall" | "taobao" | "jd" | "amazon" | "other";
  baseUrl: string;
  monitoredProductsCount: number;
  lastScrapedAt: string | null;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

/**
 * 新增競爭對手 DTO
 */
export interface CreateCompetitorDto {
  name: string;
  platform: string;
  baseUrl: string;
  isActive?: boolean;
}

/**
 * 更新競爭對手 DTO
 */
export interface UpdateCompetitorDto {
  name?: string;
  platform?: string;
  baseUrl?: string;
  isActive?: boolean;
}

/**
 * 競爭對手商品
 */
export interface CompetitorProduct {
  id: number;
  competitorId: number;
  productId: number;
  productName: string;
  productSku: string;
  competitorProductUrl: string;
  currentPrice: number;
  lastPrice: number | null;
  priceChangePercent: number | null;
  lastScrapedAt: string | null;
  isAvailable: boolean;
  createdAt: string;
  updatedAt: string;
}

/**
 * 新增競爭對手商品 DTO
 */
export interface CreateCompetitorProductDto {
  productId: number;
  competitorProductUrl: string;
}

// ==================== 價格預警類型 ====================

/**
 * 預警篩選參數
 */
export interface AlertFilterParams {
  alertType?: string;
  isRead?: boolean;
  competitorId?: number;
  productId?: number;
  dateFrom?: string;
  dateTo?: string;
  page?: number;
  limit?: number;
}

/**
 * 更新預警狀態 DTO
 */
export interface UpdateAlertDto {
  isRead: boolean;
}

// ==================== 商品類型 ====================

/**
 * 商品
 */
export interface Product {
  id: string; // UUID from backend
  sku: string;
  name: string;
  description: string | null;
  price: number;
  cost: number | null;
  stock: number;
  category: string | null;
  brand: string | null;
  imageUrl: string | null;
  status: "active" | "inactive" | "out_of_stock";
  createdAt: string;
  updatedAt: string;
}

/**
 * 新增商品 DTO
 */
export interface CreateProductDto {
  sku: string;
  name: string;
  description?: string;
  price: number;
  cost?: number;
  stock: number;
  category?: string;
  brand?: string;
  imageUrl?: string;
  status?: "active" | "inactive" | "out_of_stock";
}

/**
 * 更新商品 DTO
 */
export interface UpdateProductDto {
  sku?: string;
  name?: string;
  description?: string;
  price?: number;
  cost?: number;
  stock?: number;
  category?: string;
  brand?: string;
  imageUrl?: string;
  status?: "active" | "inactive" | "out_of_stock";
}

/**
 * 商品篩選參數
 */
export interface ProductFilterParams {
  search?: string;
  category?: string;
  brand?: string;
  status?: "active" | "inactive" | "out_of_stock";
  minPrice?: number;
  maxPrice?: number;
  page?: number;
  pageSize?: number;
  limit?: number;
  sortBy?: "name" | "price" | "stock" | "createdAt";
  sortOrder?: "asc" | "desc";
}

// ==================== AI 內容類型 ====================

/**
 * 內容類型
 */
export type ContentType =
  | "product_title"
  | "product_description"
  | "seo_keywords"
  | "social_media_post"
  | "email_campaign";

/**
 * 內容風格
 */
export type ContentStyle =
  | "professional"
  | "casual"
  | "persuasive"
  | "informative"
  | "creative";

/**
 * 內容語言
 */
export type ContentLanguage = "zh-HK" | "zh-CN" | "en" | "ja";

/**
 * AI 內容生成請求
 */
export interface GenerateContentRequest {
  productId: number;
  contentType: ContentType;
  style?: ContentStyle;
  language?: ContentLanguage;
  maxLength?: number;
  keywords?: string[];
}

/**
 * AI 內容生成響應
 */
export interface GenerateContentResponse {
  content: string;
  productId: number;
  contentType: ContentType;
  language: ContentLanguage;
  tokensUsed: number;
  generatedAt: string;
}

/**
 * 批量生成請求
 */
export interface BatchGenerateRequest {
  productIds: number[];
  contentType: ContentType;
  style?: ContentStyle;
  language?: ContentLanguage;
}

/**
 * 批量生成響應
 */
export interface BatchGenerateResponse {
  results: GenerateContentResponse[];
  totalProcessed: number;
  totalSuccess: number;
  totalFailed: number;
}

/**
 * 內容記錄
 */
export interface ContentRecord {
  id: number;
  productId: number;
  productName: string;
  contentType: ContentType;
  content: string;
  language: ContentLanguage;
  style: ContentStyle;
  status: "draft" | "pending_review" | "approved" | "rejected";
  createdAt: string;
  updatedAt: string;
  reviewedAt: string | null;
  reviewedBy: string | null;
}

/**
 * 更新內容狀態 DTO
 */
export interface UpdateContentStatusDto {
  status: "draft" | "pending_review" | "approved" | "rejected";
  reviewNote?: string;
}

// ==================== 用戶類型 ====================

/**
 * 用戶
 */
export interface User {
  id: number;
  email: string;
  name: string;
  role: "admin" | "operator" | "viewer";
  avatarUrl: string | null;
  createdAt: string;
  lastLoginAt: string | null;
}

/**
 * 登入請求
 */
export interface LoginRequest {
  email: string;
  password: string;
}

/**
 * 登入響應
 */
export interface LoginResponse {
  user: User;
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

// ==================== 通知類型 ====================

/**
 * 通知
 */
export interface Notification {
  id: number;
  userId: number;
  type: "alert" | "content" | "system";
  title: string;
  message: string;
  isRead: boolean;
  actionUrl: string | null;
  createdAt: string;
}

// ==================== 系統設定類型 ====================

/**
 * 系統設定
 */
export interface SystemSettings {
  priceAlertThreshold: number; // 價格警報閾值（百分比）
  scrapingInterval: number; // 爬蟲間隔（分鐘）
  enableNotifications: boolean;
  defaultLanguage: ContentLanguage;
  defaultContentStyle: ContentStyle;
}

/**
 * 更新系統設定 DTO
 */
export interface UpdateSettingsDto {
  priceAlertThreshold?: number;
  scrapingInterval?: number;
  enableNotifications?: boolean;
  defaultLanguage?: ContentLanguage;
  defaultContentStyle?: ContentStyle;
}

// ==================== 統計類型 ====================

/**
 * 時間範圍
 */
export type TimeRange = "7d" | "30d" | "90d" | "1y";

/**
 * 銷售統計
 */
export interface SalesStats {
  totalRevenue: number;
  totalOrders: number;
  averageOrderValue: number;
  topSellingProducts: {
    productId: number;
    productName: string;
    totalSold: number;
    revenue: number;
  }[];
}

/**
 * 價格競爭力統計
 */
export interface PriceCompetitivenessStats {
  advantageCount: number; // 價格優勢商品數
  neutralCount: number; // 價格持平商品數
  disadvantageCount: number; // 價格劣勢商品數
  averagePriceDifference: number; // 平均價格差異百分比
}

// ==================== 匯出類型 ====================

/**
 * 匯出格式
 */
export type ExportFormat = "csv" | "xlsx" | "json";

/**
 * 匯出請求
 */
export interface ExportRequest {
  type: "products" | "alerts" | "competitors" | "content";
  format: ExportFormat;
  filters?: Record<string, any>;
  dateFrom?: string;
  dateTo?: string;
}

/**
 * 匯出響應
 */
export interface ExportResponse {
  fileUrl: string;
  fileName: string;
  fileSize: number;
  expiresAt: string;
}
