// =============================================
// API 客戶端
// =============================================

import { getToken } from './secure-token'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

// =============================================
// Locale 感知：從 localStorage 讀取用戶語言偏好
// =============================================
const VALID_LOCALES = ['zh-HK', 'en'] as const

function getCurrentLocale(): string {
  if (typeof window === 'undefined') return 'zh-HK'
  const stored = localStorage.getItem('gogojap-locale')
  return stored && (VALID_LOCALES as readonly string[]).includes(stored) ? stored : 'zh-HK'
}

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${endpoint}`
  // 使用Security token Management器
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Accept-Language': getCurrentLocale(),
    ...(options?.headers as Record<string, string>),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (!response.ok) {
    // Try從 response body 讀取Error訊息
    let errorMessage = `API Error: ${response.status} ${response.statusText}`
    try {
      const errorData = await response.json()
      if (errorData.detail) {
        errorMessage = errorData.detail
      } else if (errorData.error) {
        errorMessage = errorData.error
      } else if (errorData.message) {
        errorMessage = errorData.message
      }
    } catch {
      // Cannot parse JSON, use defaultError訊息
    }
    throw new Error(errorMessage)
  }

  return response.json()
}

// =============================================
// 類別 API
// =============================================

export interface Category {
  id: string
  name: string
  description: string | null
  hktv_category_url: string | null
  total_products: number
  last_scraped_at: string | null
  scrape_frequency: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface CategoryListResponse {
  items: Category[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface Product {
  id: string
  category_id: string
  name: string
  url: string
  sku: string | null
  brand: string | null
  price: number | null
  original_price: number | null
  discount_percent: number | null
  unit_price: number | null
  unit_type: string | null
  stock_status: string | null
  is_available: boolean
  rating: number | null
  review_count: number | null
  image_url: string | null
  first_seen_at: string
  last_updated_at: string
}

export interface ProductListResponse {
  items: Product[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface CategoryStats {
  category_id: string
  category_name: string
  total_products: number
  available_products: number
  avg_price: number | null
  min_price: number | null
  max_price: number | null
  price_range: number | null
  brands_count: number
  last_scraped_at: string | null
}

export interface PriceOverview {
  category_id: string
  category_name: string
  total_products: number
  price_distribution: { range: string; count: number }[]
  brand_comparison: {
    brand: string
    avg_price: number
    min_price: number
    max_price: number
    product_count: number
  }[]
  top_deals: {
    name: string
    price: number | null
    original_price: number | null
    discount_percent: number | null
    url: string
  }[]
}

export interface PriceHistory {
  product_id: string
  product_name: string
  days: number
  data_points: number
  chart_data: {
    date: string
    datetime: string
    price: number | null
    original_price: number | null
    unit_price: number | null
    discount_percent: number | null
    is_available: boolean
  }[]
  statistics: {
    min_price: number | null
    max_price: number | null
    avg_price: number | null
    current_price: number | null
    price_trend: number | null
  }
}

// 預覽products
export interface PreviewProduct {
  url: string
  name: string
  price: number | null
  original_price: number | null
  discount_percent: number | null
  stock_status: string | null
  brand: string | null
  sku: string | null
  image_url: string | null
  rating: number | null
  review_count: number | null
  unit_price: number | null
  unit_type: string | null
}

// 預覽抓取Response
export interface PreviewScrapeResponse {
  preview_id: string
  category_id: string
  category_name: string
  total_scraped: number
  products: PreviewProduct[]
  errors: string[]
  expires_at: string
  duration_seconds: number
}

// ConfirmSaveResponse
export interface ConfirmScrapeResponse {
  success: boolean
  message: string
  saved_count: number
  skipped_count: number
  errors: string[]
}

// Batch deleteResponse
export interface BulkDeleteResponse {
  success: boolean
  deleted_count: number
  total_requested: number
  errors: string[]
  remaining_products: number
}

// =============================================
// 智能抓取相關Type
// =============================================

export interface SmartScrapeRequest {
  max_new_products?: number
  max_updates?: number
}

export interface SmartScrapeResponse {
  success: boolean
  message: string
  category_name: string
  new_products: number
  updated_products: number
  failed: number
  credits_used: number
  errors: string[]
}

export interface QuotaUsageResponse {
  // 本地統計
  daily_usage: number
  monthly_usage: number
  // Firecrawl API 真實Quota
  remaining_credits: number
  plan_credits: number
  used_credits: number
  usage_percent: number
  billing_period_start: string | null
  billing_period_end: string | null
  days_remaining: number
  // State
  is_low: boolean
  is_critical: boolean
  error_message: string | null
}

export interface QuotaHistoryItem {
  date: string
  credits_used: number
  operations_count: number
}

export interface QuotaHistoryResponse {
  days: number
  history: QuotaHistoryItem[]
  total_credits: number
}

export interface ProductPriority {
  id: string
  name: string
  monitor_priority: 'high' | 'normal' | 'low'
  update_frequency_hours: number
  last_updated_at: string | null
  is_monitored: boolean
}

// API Function
export const api = {
  // 類別
  getCategories: (page = 1, pageSize = 20) =>
    fetchAPI<CategoryListResponse>(`/categories?page=${page}&page_size=${pageSize}`),

  getCategory: (id: string) =>
    fetchAPI<Category>(`/categories/${id}`),

  getCategoryStats: (id: string) =>
    fetchAPI<CategoryStats>(`/categories/${id}/stats`),

  getCategoryPriceOverview: (id: string) =>
    fetchAPI<PriceOverview>(`/categories/${id}/price-overview`),

  // products
  getCategoryProducts: (categoryId: string, page = 1, pageSize = 20) =>
    fetchAPI<ProductListResponse>(`/categories/${categoryId}/products?page=${page}&page_size=${pageSize}`),

  getProductPriceHistory: (categoryId: string, productId: string, days = 30) =>
    fetchAPI<PriceHistory>(`/categories/${categoryId}/products/${productId}/price-history?days=${days}`),

  // 抓取（直接Save）
  triggerScrape: (categoryId: string, maxProducts = 20) =>
    fetchAPI<{ success: boolean; message: string }>(`/categories/${categoryId}/scrape-sync`, {
      method: 'POST',
      body: JSON.stringify({ max_products: maxProducts }),
    }),

  // 預覽抓取（不Save，NeedReview）
  previewScrape: (categoryId: string, maxProducts = 20) =>
    fetchAPI<PreviewScrapeResponse>(`/categories/${categoryId}/scrape-preview`, {
      method: 'POST',
      body: JSON.stringify({ max_products: maxProducts }),
    }),

  // ConfirmSave預覽Result
  confirmScrape: (categoryId: string, previewId: string, selectedIndices?: number[]) =>
    fetchAPI<ConfirmScrapeResponse>(`/categories/${categoryId}/scrape-confirm`, {
      method: 'POST',
      body: JSON.stringify({
        preview_id: previewId,
        selected_product_indices: selectedIndices,
      }),
    }),

  // Cancel preview
  cancelPreview: (categoryId: string, previewId: string) =>
    fetch(`${API_BASE}/categories/${categoryId}/scrape-preview/${previewId}`, {
      method: 'DELETE',
    }),

  // Delete single product
  deleteProduct: (categoryId: string, productId: string) =>
    fetch(`${API_BASE}/categories/${categoryId}/products/${productId}`, {
      method: 'DELETE',
    }),

  // Batch deleteproducts
  bulkDeleteProducts: (categoryId: string, productIds: string[]) =>
    fetchAPI<BulkDeleteResponse>(`/categories/${categoryId}/products/bulk-delete`, {
      method: 'POST',
      body: JSON.stringify({ product_ids: productIds }),
    }),

  // =============================================
  // 智能抓取 API（Optimize版）
  // =============================================

  // 智能抓取（使用Cache + 增量Update）
  smartScrape: (categoryId: string, options?: SmartScrapeRequest) =>
    fetchAPI<SmartScrapeResponse>(`/categories/${categoryId}/smart-scrape`, {
      method: 'POST',
      body: JSON.stringify(options || {}),
    }),

  // Set upproducts優先級
  setProductsPriority: (categoryId: string, priority: 'high' | 'normal' | 'low', productIds?: string[]) =>
    fetchAPI<{ success: boolean; message: string; updated_count: number }>(`/categories/${categoryId}/products/priority`, {
      method: 'PUT',
      body: JSON.stringify({ priority, product_ids: productIds }),
    }),

  // Fetchproducts優先級List
  getProductsPriorities: (categoryId: string, priority?: string, page = 1, pageSize = 50) => {
    const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) })
    if (priority) params.append('priority', priority)
    return fetchAPI<ProductPriority[]>(`/categories/${categoryId}/products/priorities?${params}`)
  },

  // FetchQuota使用情況
  getQuotaUsage: () =>
    fetchAPI<QuotaUsageResponse>('/categories/quota/usage'),

  // FetchQuota使用History
  getQuotaHistory: (days = 7) =>
    fetchAPI<QuotaHistoryResponse>(`/categories/quota/history?days=${days}`),

// Telegram
  getTelegramConfig: () =>
    fetchAPI<{ enabled: boolean; bot_configured: boolean; chat_configured: boolean; bot_username: string | null }>('/telegram/config'),

  testTelegram: () =>
    fetchAPI<{ success: boolean; message: string }>('/telegram/test', { method: 'POST' }),

  // =============================================
  // 競爭Competitor API
  // =============================================
  getCompetitors: (isActive?: boolean) =>
    fetchAPI<CompetitorListResponse>(`/competitors${isActive !== undefined ? `?is_active=${isActive}` : ''}`),

  createCompetitor: (data: CompetitorCreate) =>
    fetchAPI<Competitor>('/competitors', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getCompetitor: (id: string) =>
    fetchAPI<Competitor>(`/competitors/${id}`),

  updateCompetitor: (id: string, data: CompetitorUpdate) =>
    fetchAPI<Competitor>(`/competitors/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  deleteCompetitor: (id: string) =>
    fetch(`${API_BASE}/competitors/${id}`, { method: 'DELETE' }),

  getCompetitorProducts: (competitorId: string, page = 1, limit = 20, search?: string) =>
    fetchAPI<CompetitorProductListResponse>(
      `/competitors/${competitorId}/products?page=${page}&limit=${limit}${search ? `&search=${encodeURIComponent(search)}` : ''}`
    ),

  addCompetitorProduct: (competitorId: string, data: CompetitorProductCreate) =>
    fetchAPI<{ task_id: string; message: string }>(`/competitors/${competitorId}/products`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateCompetitorProduct: (productId: string, data: CompetitorProductUpdate) =>
    fetchAPI<CompetitorProduct>(`/competitors/products/${productId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  deleteCompetitorProduct: (productId: string) =>
    fetch(`${API_BASE}/competitors/products/${productId}`, { method: 'DELETE' }),

  getCompetitorProductHistory: (productId: string, days = 30) =>
    fetchAPI<CompetitorPriceHistoryResponse>(`/competitors/products/${productId}/history?days=${days}`),

  triggerCompetitorScrape: (competitorId: string) =>
    fetchAPI<{ task_id: string; message: string }>(`/competitors/${competitorId}/scrape`, {
      method: 'POST',
    }),

  // =============================================
  // 自家products API
  // =============================================
  getProducts: (page = 1, limit = 20, search?: string, status?: string, category?: string) => {
    const params = new URLSearchParams({ page: String(page), limit: String(limit) })
    if (search) params.append('search', search)
    if (status) params.append('status', status)
    if (category) params.append('category', category)
    return fetchAPI<OwnProductListResponse>(`/products?${params}`)
  },

  createOwnProduct: (data: OwnProductCreate) =>
    fetchAPI<OwnProduct>('/products', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getOwnProduct: (id: string) =>
    fetchAPI<OwnProduct>(`/products/${id}`),

  updateOwnProduct: (id: string, data: OwnProductUpdate) =>
    fetchAPI<OwnProduct>(`/products/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  deleteOwnProduct: (id: string) =>
    fetch(`${API_BASE}/products/${id}`, { method: 'DELETE' }),

  // =============================================
  // AI Content API
  // =============================================
  generateContent: (data: ContentGenerateRequest) =>
    fetchAPI<ContentGenerateResponse>('/content/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  batchGenerateContent: (data: ContentBatchGenerateRequest) =>
    fetchAPI<BatchGenerateResponse>('/content/batch-generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Query批量任務State
  getBatchTaskStatus: (taskId: string) =>
    fetchAPI<BatchTaskStatusResponse>(`/content/batch-generate/${taskId}/status`),

  // ExportContent為 CSV
  exportContentCsv: (contentIds: string[]) => {
    const params = new URLSearchParams({ content_ids: contentIds.join(',') })
    // BackDownload URL，Frontend needs window.open or <a> tag to triggerDownload
    return `${process.env.NEXT_PUBLIC_API_URL || '/api/v1'}/content/export?${params}`
  },

  // Download批量Import模板
  getImportTemplateUrl: () =>
    `${process.env.NEXT_PUBLIC_API_URL || '/api/v1'}/content/template/download`,

  getContentHistory: (productId?: string, status?: string, contentType?: string, limit = 50) => {
    const params = new URLSearchParams({ limit: String(limit) })
    if (productId) params.append('product_id', productId)
    if (status) params.append('status', status)
    if (contentType) params.append('content_type', contentType)
    return fetchAPI<ContentListResponse>(`/content/history?${params}`)
  },

  approveContent: (contentId: string) =>
    fetchAPI<{ id: string; status: string; approved_at: string }>(`/content/${contentId}/approve`, {
      method: 'PUT',
    }),

  rejectContent: (contentId: string, reason?: string) =>
    fetchAPI<{ message: string; reason: string | null }>(`/content/${contentId}/reject?reason=${encodeURIComponent(reason || '')}`, {
      method: 'PUT',
    }),

  // 文案對話式Optimize
  optimizeContent: (contentId: string, data: ContentOptimizeRequest) =>
    fetchAPI<ContentOptimizeResponse>(`/content/${contentId}/optimize`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Fetch快捷Optimizesuggestions
  getOptimizeSuggestions: () =>
    fetchAPI<QuickSuggestionsResponse>('/content/optimize/suggestions'),

  // =============================================
  // Alert API
  // =============================================
  getAlerts: (isRead?: boolean, alertType?: string, limit = 50) => {
    const params = new URLSearchParams({ limit: String(limit) })
    if (isRead !== undefined) params.append('is_read', String(isRead))
    if (alertType) params.append('alert_type', alertType)
    return fetchAPI<PriceAlertListResponse>(`/alerts?${params}`)
  },

  markAlertRead: (alertId: string) =>
    fetchAPI<{ message: string }>(`/alerts/${alertId}/read`, { method: 'PUT' }),

  markAllAlertsRead: () =>
    fetchAPI<{ message: string; count: number }>(`/alerts/mark-all-read`, { method: 'PUT' }),

  // =============================================
  // Market Response Center (MRC) API
  // =============================================
  getMrcDashboard: () =>
    fetchAPI<any>('/mrc/dashboard'),

  getMrcSeasonalProducts: () =>
    fetchAPI<any[]>('/mrc/products/seasonal'),

  searchMrcProducts: (query: string) =>
    fetchAPI<any[]>(`/mrc/products/search?q=${encodeURIComponent(query)}`),

  getMrcCategories: () =>
    fetchAPI<any[]>('/mrc/categories'),

  getMrcStatsOverview: () =>
    fetchAPI<any>('/mrc/stats/overview'),

  // 批量CompetitorMatch
  batchFindCompetitors: (limit: number = 50, categoryMain?: string, categorySub?: string) => {
    const params = new URLSearchParams({ limit: limit.toString() })
    if (categoryMain) params.append('category_main', categoryMain)
    if (categorySub) params.append('category_sub', categorySub)
    return fetchAPI<{
      processed: number
      results: Array<{
        product_id: string
        product_name: string
        candidates?: number
        matches?: number
        error?: string
      }>
    }>(`/mrc/batch/find-competitors?${params.toString()}`, { method: 'POST' })
  },

  // Batch competitor matching (SSE streaming)— BackFull URL, handled by caller stream
  batchFindCompetitorsStreamUrl: (limit: number, categoryMain?: string, platform?: string) => {
    const base = process.env.NEXT_PUBLIC_API_URL || '/api/v1'
    const params = new URLSearchParams({ limit: limit.toString() })
    if (categoryMain) params.append('category_main', categoryMain)
    if (platform) params.append('platform', platform)
    return `${base}/mrc/batch/find-competitors/stream?${params.toString()}`
  },

  // =============================================
  // Competitor建庫 API
  // =============================================

  // Start pipeline background task (returns task_id)
  startPipeline: (platform: string = 'all') =>
    fetchAPI<{ task_id: string }>(`/catalog/pipeline/start?platform=${platform}`, {
      method: 'POST',
    }),

  // 輪詢管線進度
  getPipelineProgress: (taskId: string) =>
    fetchAPI<{
      task_id: string
      status: 'running' | 'done' | 'error'
      current_step: string | null
      current_step_number: number
      total_steps: number
      elapsed: number
      step_results: Record<string, any>
      step_errors: Record<string, string>
      step_durations: Record<string, number>
      progress: { current: number; total: number; failed?: number; message?: string } | null
    }>(`/catalog/pipeline/progress/${taskId}`),

  // 建庫：抓取Competitor平台products（長TimeOperation，5 minutesTimeout）
  buildCatalog: (platform: string = 'all') =>
    fetchAPI<{ status: string; result: any }>(`/catalog/build?platform=${platform}`, {
      method: 'POST',
      signal: AbortSignal.timeout(300_000),
    }),

  // 打標：Auto分類標籤（3 minutesTimeout）
  tagCatalog: () =>
    fetchAPI<{ status: string; result: any }>('/catalog/tag', {
      method: 'POST',
      signal: AbortSignal.timeout(180_000),
    }),

  // Matching: AI pairs own products with competitors (5 min timeout)
  matchCatalog: (productId?: string) => {
    const params = productId ? `?product_id=${productId}` : ''
    return fetchAPI<{ status: string; result: any }>(`/catalog/match${params}`, {
      method: 'POST',
      signal: AbortSignal.timeout(300_000),
    })
  },

  // =============================================
  // AI Settings與Analysis API
  // =============================================
  
  // Fetch AI Configuration
  getAIConfig: () =>
    fetchAPI<AIConfigResponse>('/ai/config'),

  // Update AI Configuration
  updateAIConfig: (data: AIConfigUpdate) =>
    fetchAPI<AIConfigResponse>('/ai/config', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  // Test API Connection
  testAIConnection: (apiKey: string, baseUrl: string, model = 'gpt-3.5-turbo') =>
    fetchAPI<{ valid: boolean; error?: string; message?: string }>('/ai/test-connection', {
      method: 'POST',
      body: JSON.stringify({ api_key: apiKey, base_url: baseUrl, model }),
    }),

  // FetchDefault可用ModelList
  getAIModels: () =>
    fetchAPI<AIModel[]>('/ai/models'),

  // Dynamically fetch models from APIList
  fetchModelsFromAPI: (options: { apiKey?: string; baseUrl?: string; useSaved?: boolean }) =>
    fetchAPI<FetchModelsResponse>('/ai/fetch-models', {
      method: 'POST',
      body: JSON.stringify({
        api_key: options.apiKey,
        base_url: options.baseUrl,
        use_saved: options.useSaved ?? false,
      }),
    }),

  // GenerateData摘要
  generateDataInsights: (data: Record<string, any>) =>
    fetchAPI<AIAnalysisResponse>('/ai/generate-insights', {
      method: 'POST',
      body: JSON.stringify({ data }),
    }),

  // Generate marketing strategy
  generateMarketingStrategy: (insights: string, context: Record<string, any> = {}) =>
    fetchAPI<AIAnalysisResponse>('/ai/generate-strategy', {
      method: 'POST',
      body: JSON.stringify({ insights, context }),
    }),

  // 完整Analysis流程（兩個 AI 串聯）
  runFullAnalysis: (data: Record<string, any>, context: Record<string, any> = {}) =>
    fetchAPI<AIFullAnalysisResponse>('/ai/analyze-full', {
      method: 'POST',
      body: JSON.stringify({ data, context }),
    }),

  // =============================================
  // AI Agent API
  // =============================================

  // 發送聊天訊息
  agentChat: (message: AgentChatMessage) =>
    fetchAPI<AgentChatResponse>('/agent/chat', {
      method: 'POST',
      body: JSON.stringify(message),
    }),

  // Processing澄清回應
  agentClarify: (response: AgentClarificationResponse) =>
    fetchAPI<AgentChatResponse>('/agent/clarify', {
      method: 'POST',
      body: JSON.stringify(response),
    }),

  // Fetch對話State
  getAgentConversation: (conversationId: string) =>
    fetchAPI<AgentConversationState>(`/agent/conversation/${conversationId}`),

  // FetchQuerysuggestions
  getAgentSuggestions: () =>
    fetchAPI<{ suggestions: AgentSuggestion[] }>('/agent/suggestions'),

  // FetchProduct類別
  
  // Fetch對話History
  getAgentConversations: (limit = 50, offset = 0) =>
    fetchAPI<{ conversations: { id: string; title: string; created_at: string; updated_at: string }[] }>(`/agent/conversations?limit=${limit}&offset=${offset}`),

  getAgentProductCategories: () =>
    fetchAPI<{ categories: AgentProductCategory[] }>('/agent/product-categories'),

  // Delete單個對話
  deleteAgentConversation: (conversationId: string) =>
    fetchAPI<{ success: boolean; message: string }>(`/agent/conversation/${conversationId}`, {
      method: 'DELETE',
    }),

  // Batch delete對話
  deleteAgentConversations: (conversationIds: string[]) =>
    fetchAPI<{ success: boolean; deleted_count: number; message: string }>('/agent/conversations', {
      method: 'DELETE',
      body: JSON.stringify({ conversation_ids: conversationIds }),
    }),

  // =============================================
  // HKTVmall 集成 API
  // =============================================

  hktvSyncProducts: () =>
    fetchAPI<{ message: string }>('/hktvmall/sync/products', { method: 'POST' }),
    
  hktvUpdatePrice: (sku: string, price: number, promotionPrice?: number) =>
    fetchAPI<{ success: boolean; remote_response: any }>(`/hktvmall/products/${sku}/price`, {
      method: 'POST',
      body: JSON.stringify({ sku_code: sku, price, promotion_price: promotionPrice })
    }),

  hktvUpdateStock: (sku: string, quantity: number, status: string = 'Active') =>
    fetchAPI<{ success: boolean; remote_response: any }>(`/hktvmall/products/${sku}/stock`, {
      method: 'POST',
      body: JSON.stringify({ sku_code: sku, quantity, stock_status: status })
    }),
    
  hktvStatus: () =>
    fetchAPI<{ status: string; mode: string; base_url: string }>('/hktvmall/status'),

  // =============================================
  // Competitor v2 — Comparison Dashboard
  // =============================================

  getComparisonSummary: () =>
    fetchAPI<ComparisonSummary>('/competitors/comparison/summary'),

  getComparisonProducts: (scope: 'mapped' | 'all' = 'mapped') =>
    fetchAPI<{ items: ProductComparison[] }>(`/competitors/comparison/products?scope=${scope}`),

  getComparisonMerchants: () =>
    fetchAPI<{ items: MerchantOverview[] }>('/competitors/comparison/merchants'),

  getPriceHistory: (productId: string, days = 30) =>
    fetchAPI<PriceHistoryData>(`/competitors/comparison/products/${productId}/price-history?days=${days}`),

  getComparisonExportUrl: () =>
    `/api/v1/competitors/comparison/export`,

  getPricingSuggestions: () =>
    fetchAPI<{ suggestions: PricingSuggestion[] }>('/competitors/comparison/pricing-suggestions'),
}

// =============================================
// 競爭Competitor相關Type
// =============================================

export interface Competitor {
  id: string
  name: string
  platform: string
  base_url: string | null
  notes: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  product_count: number
  last_scraped_at: string | null
}

export interface CompetitorListResponse {
  data: Competitor[]
  total: number
}

export interface CompetitorCreate {
  name: string
  platform: string
  base_url?: string
  notes?: string
}

export interface CompetitorUpdate {
  name?: string
  platform?: string
  base_url?: string
  notes?: string
  is_active?: boolean
}

export interface CompetitorProduct {
  id: string
  competitor_id: string
  name: string
  name_en: string | null
  url: string
  sku: string | null
  category: string | null
  image_url: string | null
  is_active: boolean
  last_scraped_at: string | null
  current_price: number | null
  previous_price: number | null
  price_change: number | null
  stock_status: string | null
  created_at: string
}

export interface CompetitorProductListResponse {
  data: CompetitorProduct[]
  total: number
  page: number
  limit: number
}

export interface CompetitorProductCreate {
  url: string
  name?: string
  category?: string
}

export interface CompetitorProductUpdate {
  url?: string
  name?: string
  category?: string
  is_active?: boolean
}

export interface PriceSnapshot {
  id: string
  price: number | null
  original_price: number | null
  discount_percent: number | null
  stock_status: string | null
  rating: number | null
  review_count: number | null
  scraped_at: string
}

export interface CompetitorPriceHistoryResponse {
  product: CompetitorProduct
  history: PriceSnapshot[]
}

// =============================================
// 自家products相關Type
// =============================================

export interface OwnProduct {
  id: string
  sku: string
  hktv_product_id: string | null
  name: string
  name_zh: string | null
  name_ja: string | null
  name_en: string | null
  description: string | null
  category: string | null
  brand: string | null
  price: number | null
  cost: number | null
  stock_quantity: number
  status: string
  images: string[] | null
  attributes: Record<string, unknown> | null
  created_at: string
  updated_at: string
}

export interface OwnProductListResponse {
  data: OwnProduct[]
  total: number
  page: number
  limit: number
}

export interface OwnProductCreate {
  sku: string
  name: string
  description?: string
  category?: string
  brand?: string
  price?: number
  cost?: number
  stock_quantity?: number
  status?: string
  images?: string[]
  attributes?: Record<string, unknown>
}

export interface OwnProductUpdate {
  sku?: string
  name?: string
  description?: string | null
  category?: string | null
  brand?: string | null
  price?: number | null
  cost?: number | null
  stock_quantity?: number
  status?: string
  images?: string[] | null
  attributes?: Record<string, unknown> | null
}

// =============================================
// AI Content相關Type
// =============================================

export interface ProductInfo {
  name: string
  brand?: string
  features?: string[]
  target_audience?: string
  price?: string
  category?: string
}

export interface ContentGenerateRequest {
  product_id?: string
  product_info?: ProductInfo
  content_type: 'title' | 'description' | 'selling_points' | 'full_copy'
  style: 'formal' | 'casual' | 'playful' | 'professional'
  language?: string
  target_languages?: ('TC' | 'SC' | 'EN')[]
}

export interface GeneratedContent {
  title?: string
  selling_points?: string[]
  description?: string
  short_description?: string
  multilang?: {
    TC?: { title?: string; selling_points?: string[]; description?: string; short_description?: string }
    SC?: { title?: string; selling_points?: string[]; description?: string; short_description?: string }
    EN?: { title?: string; selling_points?: string[]; description?: string; short_description?: string }
  }
}

export interface ContentGenerateResponse {
  id: string
  content_type: string
  content: GeneratedContent
  metadata: Record<string, unknown>
}

// 舊版批量Request（已廢棄）
export interface ContentBatchGenerateRequestLegacy {
  product_ids: string[]
  content_type: 'title' | 'description' | 'selling_points' | 'full_copy'
  style: 'formal' | 'casual' | 'playful' | 'professional'
}

// 新版批量Generate
export interface BatchGenerateItem {
  product_id?: string
  product_info?: ProductInfo
}

export interface ContentBatchGenerateRequest {
  items: BatchGenerateItem[]
  content_type: 'title' | 'description' | 'selling_points' | 'full_copy'
  style: 'formal' | 'casual' | 'playful' | 'professional'
  target_languages?: ('TC' | 'SC' | 'EN')[]
}

export interface BatchResultItem {
  index: number
  success: boolean
  content_id?: string
  product_name: string
  product_name_en?: string
  content?: GeneratedContent
  error?: string
}

export interface BatchSummary {
  total: number
  success: number
  failed: number
}

export interface BatchGenerateSyncResponse {
  mode: 'sync'
  results: BatchResultItem[]
  summary: BatchSummary
}

export interface BatchGenerateAsyncResponse {
  mode: 'async'
  task_id: string
  total: number
  message: string
}

export type BatchGenerateResponse = BatchGenerateSyncResponse | BatchGenerateAsyncResponse

export interface BatchProgress {
  total: number
  completed: number
  failed: number
  percent: number
}

export interface BatchTaskStatusResponse {
  task_id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: BatchProgress
  results: BatchResultItem[]
}

export interface ContentItem {
  id: string
  product_id: string | null
  product_name: string | null
  content_type: string
  style: string | null
  language: string | null
  content: string
  content_json: GeneratedContent | null
  version: number
  status: string
  generated_at: string
  approved_at: string | null
  approved_by: string | null
}

export interface ContentListResponse {
  data: ContentItem[]
  total: number
}

// 文案Optimize相關Type
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ContentOptimizeRequest {
  instruction: string
  context?: ChatMessage[]
  target_languages?: ('TC' | 'SC' | 'EN')[]
  product_info?: ProductInfo
}

export interface ContentOptimizeResponse {
  content_id: string
  content: GeneratedContent
  suggestions: string[]
  version: number
  metadata: Record<string, unknown>
}

export interface QuickSuggestion {
  key: string
  label: string
  instruction: string
}

export interface QuickSuggestionsResponse {
  suggestions: QuickSuggestion[]
}

// =============================================
// Alert相關Type
// =============================================

export interface PriceAlert {
  id: string
  product_name: string
  competitor_name: string
  alert_type: string
  old_value: string | null
  new_value: string | null
  change_percent: number | null
  is_read: boolean
  created_at: string
}

export interface PriceAlertListResponse {
  data: PriceAlert[]
  unread_count: number
}

// =============================================
// AI Settings相關Type
// =============================================

export interface AIModel {
  id: string
  name: string
  description: string
}

export interface FetchedModel {
  id: string
  name: string
  owned_by?: string
  created?: number
}

export interface FetchModelsResponse {
  success: boolean
  models: FetchedModel[]
  total?: number
  error?: string
}

export interface AIConfigResponse {
  api_key_set: boolean
  api_key_preview: string
  base_url: string
  insights_model: string
  strategy_model: string
}

export interface AIConfigUpdate {
  api_key?: string
  base_url?: string
  insights_model?: string
  strategy_model?: string
}

export interface TestConnectionRequest {
  api_key: string
  base_url: string
  model?: string
}

export interface AIAnalysisResponse {
  success: boolean
  content: string
  model: string
  tokens_used: number
  error?: string
}

export interface AIFullAnalysisResponse {
  success: boolean
  stage?: string
  error?: string
  insights: {
    content: string
    model: string
    tokens_used: number
  } | null
  strategy: {
    content: string | null
    model: string
    tokens_used: number
    error?: string
  } | null
  total_tokens: number
}

// =============================================
// AI Agent Type
// =============================================

export interface AgentChatMessage {
  content: string
  conversation_id?: string
}

export interface AgentClarificationResponse {
  conversation_id: string
  selections: Record<string, any>
}

export interface AgentSlotOption {
  slot_name: string
  label: string
  type: 'single' | 'multi' | 'text'
  options: { value: string; label: string }[]
}

export interface AgentChartData {
  type: 'line' | 'bar' | 'pie'
  title: string
  data: any[]
  config: {
    xKey: string
    yKeys: { key: string; color: string; name: string }[]
  }
}

export interface AgentFollowUpSuggestion {
  text: string
  icon: string
}

export interface AgentChatResponse {
  type: 'thinking' | 'message' | 'clarification' | 'report' | 'error'
  content: string
  conversation_id: string
  options?: AgentSlotOption[]
  report?: {
    title: string
    markdown: string
    charts: AgentChartData[]
    tables: any[]
    summary: string
    generated_at: string
  }
  charts?: AgentChartData[]
  suggestions?: AgentFollowUpSuggestion[]  // 後續suggestionsbutton
}

export interface AgentConversationState {
  conversation_id: string
  messages: { role: string; content: string; timestamp: string }[]
  slots: Record<string, any>
  current_intent: string | null
}

export interface AgentSuggestion {
  text: string
  category: string
}

export interface AgentProductCategory {
  name: string
  aliases: string[]
  has_parts: boolean
  has_types: boolean
  example_query: string
}

// =============================================
// 智能Pricing API
// =============================================

export interface PriceProposal {
  id: string
  product_id: string
  product_name?: string
  product_sku?: string
  status: 'pending' | 'approved' | 'rejected' | 'executed' | 'failed'
  current_price: number | null
  proposed_price: number | null
  final_price: number | null
  reason: string | null
  created_at: string
  ai_model_used: string | null
}

export interface ProductPricingConfig {
  cost?: number
  min_price?: number
  max_price?: number
  auto_pricing_enabled?: boolean
}

export const pricingApi = {
  getPendingProposals: () => 
    fetchAPI<PriceProposal[]>('/pricing/proposals/pending'),
    
  approveProposal: (id: string) => 
    fetchAPI<PriceProposal>(`/pricing/proposals/${id}/approve`, { method: 'POST' }),
    
  rejectProposal: (id: string) => 
    fetchAPI<PriceProposal>(`/pricing/proposals/${id}/reject`, { method: 'POST' }),
    
  updateProductConfig: (productId: string, config: ProductPricingConfig) =>
    fetchAPI<{status: string}>(`/pricing/products/${productId}/config`, {
      method: 'POST',
      body: JSON.stringify(config)
    })
}

// =============================================
// 訂單 API
// =============================================

export interface OrderItem {
  id: string
  sku_code: string
  product_name: string
  quantity: number
  unit_price: number | null
  subtotal: number | null
}

export interface Order {
  id: string
  order_number: string
  order_date: string
  ship_by_date: string | null
  status: string
  hktv_status: string | null
  total_amount: number | null
  delivery_mode: string | null
  customer_region: string | null
  items: OrderItem[]
}

export interface OrderListResponse {
  data: Order[]
  total: number
  page: number
  limit: number
}

export const orderApi = {
  getOrders: (page: number = 1, status?: string) => 
    fetchAPI<OrderListResponse>(`/orders?page=${page}&limit=20${status ? `&status=${status}` : ''}`),
    
  syncOrders: (days: number = 7) => 
    fetchAPI<{status: string, synced_count: number}>(`/orders/sync?days=${days}`, { method: 'POST' })
}

// =============================================
// 客服收items箱 API
// =============================================

export interface Message {
  id: string
  content: string
  sender_type: string
  ai_generated: boolean
  is_draft: boolean
  sent_at: string
}

export interface Conversation {
  id: string
  subject: string
  customer_name: string
  status: string
  last_message_at: string
  last_message?: Message
}

export const inboxApi = {
  sync: () => fetchAPI<{status: string, synced_count: number}>('/inbox/sync', { method: 'POST' }),
  
  getConversations: () => fetchAPI<Conversation[]>('/inbox/conversations'),
  
  getMessages: (id: string) => fetchAPI<Message[]>(`/inbox/conversations/${id}/messages`),
  
  sendMessage: (id: string, content: string, is_draft: boolean = false) =>
    fetchAPI<Message>(`/inbox/conversations/${id}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content, is_draft })
    })
}

// =============================================
// 財務Management API
// =============================================

export interface SettlementItem {
  id: string
  order_number: string
  sku: string
  product_name: string | null
  quantity: number
  item_price: number
  commission_rate: number
  commission_amount: number
  transaction_date: string
}

export interface Settlement {
  id: string
  statement_no: string
  cycle_start: string
  cycle_end: string
  settlement_date: string
  total_sales_amount: number
  total_commission: number
  total_shipping_fee: number
  other_deductions: number
  net_settlement_amount: number
  status: string
  items: SettlementItem[]
}

export interface ProfitSummary {
  total_revenue: number
  total_commission: number
  total_profit: number
  profit_margin: number
  period_start: string
  period_end: string
}

export const financeApi = {
  getSettlements: (limit: number = 10) =>
    fetchAPI<Settlement[]>(`/finance/settlements?limit=${limit}`),

  getProfitSummary: () =>
    fetchAPI<ProfitSummary>('/finance/profit-summary')
}

// =============================================
// 智能推廣 API
// =============================================

export interface PromotionProposal {
  id: string
  product_id: string
  product_name?: string
  product_sku?: string
  promotion_type: string
  original_price: number
  discount_percent: number
  discounted_price: number
  projected_profit: number
  projected_margin: number
  start_date: string
  end_date: string
  reason: string
  marketing_copy: string
  status: string
}

export interface PromotionStats {
  active_count: number
  pending_count: number
  avg_discount: number
}

export const promotionApi = {
  getSuggestions: () => 
    fetchAPI<PromotionProposal[]>('/promotions/suggestions'),
    
  generateSuggestions: () => 
    fetchAPI<{status: string, generated_count: number}>('/promotions/generate', { method: 'POST' }),
    
  getStats: () =>
    fetchAPI<PromotionStats>('/promotions/stats'),
    
  approveProposal: (id: string) => 
    fetchAPI<{status: string}>(`/promotions/${id}/approve`, { method: 'POST' }),
    
  rejectProposal: (id: string) => 
    fetchAPI<{status: string}>(`/promotions/${id}/reject`, { method: 'POST' })
}

// =============================================
// Analysis總覽 API
// =============================================

export interface CommandCenterStats {
  orders_to_ship: number
  unread_messages: number
  pending_price_reviews: number
  pending_promotion_reviews: number
  unread_alerts: number
  monthly_revenue: number
  monthly_profit: number
}

export interface ActivityItem {
  type: string
  title: string
  desc: string
  time: string
}

export interface CommandCenterResponse {
  stats: CommandCenterStats
  recent_activity: ActivityItem[]
}

export const analyticsApi = {
  getCommandCenter: () =>
    fetchAPI<CommandCenterResponse>('/command-center')
}

// =============================================
// Authentication API
// =============================================

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface User {
  id: string
  email: string
  full_name?: string
  role: 'admin' | 'operator' | 'viewer'
  is_active: boolean
  permissions: string[]
}

export const authApi = {
  login: (data: any) => {
    const formData = new URLSearchParams();
    formData.append('username', data.username);
    formData.append('password', data.password);
    return fetchAPI<LoginResponse>('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData.toString(),
    });
  },

  loginGoogle: (credential: string) =>
    fetchAPI<LoginResponse>('/auth/google', {
      method: 'POST',
      body: JSON.stringify({ credential }),
    }),

  register: (data: any) =>
    fetchAPI<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getMe: () =>
    fetchAPI<User>('/auth/me'),
}

// =============================================
// SEO Optimize API Type
// =============================================

export interface SEOScoreBreakdown {
  title_score: number
  description_score: number
  keyword_score: number
  readability_score: number
}

export interface SEOContentData {
  meta_title: string
  meta_description: string
  primary_keyword?: string
  secondary_keywords?: string[]
  long_tail_keywords?: string[]
  og_title?: string
  og_description?: string
  seo_score?: number
  score_breakdown?: SEOScoreBreakdown
  improvement_suggestions?: string[]
  localized?: Record<string, any>
}

export interface SEOContentResponse {
  id: string
  product_id?: string
  content: SEOContentData
  language: string
  version: number
  status: string
  generation_metadata: Record<string, any>
  created_at: string
}

export interface SEOGenerateRequest {
  product_id?: string
  product_info?: ProductInfo
  target_keywords?: string[]
  target_languages?: string[]
  include_og?: boolean
}

export interface SEOBatchGenerateRequest {
  items: { product_id?: string; product_info?: ProductInfo; target_keywords?: string[] }[]
  target_languages?: string[]
  include_og?: boolean
}

export interface SEOBatchResultItem {
  index: number
  success: boolean
  product_name?: string
  content_id?: string
  content?: SEOContentData
  error?: string
}

export interface SEOBatchSyncResponse {
  mode: 'sync'
  results: SEOBatchResultItem[]
  summary: { total: number; success: number; failed: number }
}

export interface SEOBatchAsyncResponse {
  mode: 'async'
  task_id: string
  total: number
  message: string
}

export type SEOBatchResponse = SEOBatchSyncResponse | SEOBatchAsyncResponse

export interface SEOScoreResponse {
  product_id: string
  seo_score: number
  score_breakdown: SEOScoreBreakdown
  improvement_suggestions: string[]
  analyzed_at: string
}

export interface KeywordData {
  keyword: string
  search_volume?: number
  difficulty?: number
  intent?: string
}

export interface KeywordExtractionResponse {
  primary_keyword: string
  secondary_keywords: string[]
  long_tail_keywords: string[]
  all_keywords: KeywordData[]
}

export interface KeywordExtractRequest {
  product_id?: string
  product_info?: ProductInfo
  max_keywords?: number
  include_long_tail?: boolean
}

export interface KeywordSuggestionsResponse {
  query: string
  suggestions: KeywordData[]
  related_categories: string[]
}

export interface ContentAuditResponse {
  id: string
  product_id?: string
  audit_type: string
  overall_score: number
  scores: Record<string, number>
  issues: { type: string; severity: string; message: string; suggestion?: string }[]
  recommendations: string[]
  audited_at: string
}

// =============================================
// SEO Optimize API
// =============================================

export const seoApi = {
  // SEO ContentGenerate
  generateSEO: (data: SEOGenerateRequest) =>
    fetchAPI<SEOContentResponse>('/seo/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // 批量Generate SEO Content
  batchGenerateSEO: (data: SEOBatchGenerateRequest) =>
    fetchAPI<SEOBatchResponse>('/seo/batch-generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Fetch SEO Score
  getSEOScore: (productId: string) =>
    fetchAPI<SEOScoreResponse>(`/seo/${productId}/score`),

  // AnalysisContent
  analyzeSEO: (data: { product_id?: string; title: string; description: string; keywords?: string[]; audit_type?: string }) =>
    fetchAPI<ContentAuditResponse>('/seo/analyze', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // 提取關鍵詞
  extractKeywords: (data: KeywordExtractRequest) =>
    fetchAPI<KeywordExtractionResponse>('/seo/keywords/extract', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Get keyword suggestions
  getKeywordSuggestions: (query: string, category?: string, limit = 10) => {
    const params = new URLSearchParams({ query, limit: String(limit) })
    if (category) params.append('category', category)
    return fetchAPI<KeywordSuggestionsResponse>(`/seo/keywords/suggestions?${params}`)
  },

  // Fetch SEO ContentDetails
  getSEOContent: (contentId: string) =>
    fetchAPI<SEOContentResponse>(`/seo/${contentId}`),

  // 列出 SEO Content
  listSEOContents: (productId?: string, status?: string, limit = 20, offset = 0) => {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) })
    if (productId) params.append('product_id', productId)
    if (status) params.append('status', status)
    return fetchAPI<{ data: any[]; total: number }>(`/seo/?${params}`)
  },

  // 審批 SEO Content
  approveSEOContent: (contentId: string) =>
    fetchAPI<{ id: string; status: string; approved_at: string }>(`/seo/${contentId}/approve`, {
      method: 'PATCH',
    }),
}

// =============================================
// GEO Structured data API types
// =============================================

export interface StructuredDataResponse {
  id: string
  product_id?: string
  schema_type: string
  json_ld: Record<string, any>
  ai_summary?: string
  ai_facts?: string[]
  is_valid: boolean
  validation_errors?: string[]
  created_at: string
}

export interface ProductSchemaRequest {
  product_id?: string
  product_info?: ProductInfo
  include_reviews?: boolean
  include_offers?: boolean
}

export interface FAQSchemaRequest {
  product_id?: string
  product_info?: ProductInfo
  faqs?: { question: string; answer: string }[]
  max_faqs?: number
}

export interface BreadcrumbSchemaRequest {
  product_id?: string
  product_info?: ProductInfo
  breadcrumb_path?: { name: string; url: string }[]
}

export interface BatchSchemaResponse {
  results: StructuredDataResponse[]
  summary: { total_products: number; total_schemas: number; schema_types: string[] }
}

export interface AISummaryResponse {
  product_id?: string
  summary: string
  facts: string[]
  entities: Record<string, any>
}

export interface SchemaValidationResponse {
  is_valid: boolean
  errors: string[]
  warnings: string[]
  suggestions: string[]
}

export interface BrandKnowledgeResponse {
  id: string
  knowledge_type: string
  title: string
  content: string
  summary?: string
  related_products?: string[]
  related_categories?: string[]
  credibility_score?: number
  source_type: string
  source_reference?: string
  author?: string
  tags?: string[]
  is_active: boolean
  is_featured: boolean
  created_at: string
  updated_at: string
}

export interface BrandKnowledgeCreate {
  knowledge_type: string
  title: string
  content: string
  summary?: string
  related_products?: string[]
  related_categories?: string[]
  source_type?: string
  source_reference?: string
  author?: string
  tags?: string[]
}

export interface ExpertContentRequest {
  topic: string
  product_id?: string
  knowledge_type?: string
  tone?: string
}

// =============================================
// GEO 結構化Data API
// =============================================

export const geoApi = {
  // Generate Product Schema
  generateProductSchema: (data: ProductSchemaRequest) =>
    fetchAPI<StructuredDataResponse>('/geo/schema/product', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Generate FAQ Schema
  generateFAQSchema: (data: FAQSchemaRequest) =>
    fetchAPI<StructuredDataResponse>('/geo/schema/faq', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Generate Breadcrumb Schema
  generateBreadcrumbSchema: (data: BreadcrumbSchemaRequest) =>
    fetchAPI<StructuredDataResponse>('/geo/schema/breadcrumb', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // 批量Generate Schema
  batchGenerateSchemas: (productIds: string[], schemaTypes: string[]) =>
    fetchAPI<BatchSchemaResponse>('/geo/schema/batch', {
      method: 'POST',
      body: JSON.stringify({ product_ids: productIds, schema_types: schemaTypes }),
    }),

  // Generate AI 摘要
  generateAISummary: (data: { product_id?: string; product_info?: ProductInfo; max_facts?: number }) =>
    fetchAPI<AISummaryResponse>('/geo/ai-summary', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Validate Schema
  validateSchema: (jsonLd: Record<string, any>) =>
    fetchAPI<SchemaValidationResponse>('/geo/validate', {
      method: 'POST',
      body: JSON.stringify({ json_ld: jsonLd }),
    }),

  // Fetch結構化DataDetails
  getStructuredData: (dataId: string) =>
    fetchAPI<StructuredDataResponse>(`/geo/schema/${dataId}`),

  // 列出結構化Data
  listStructuredData: (productId?: string, schemaType?: string, limit = 20, offset = 0) => {
    const params = new URLSearchParams({ limit: String(limit), offset: String(offset) })
    if (productId) params.append('product_id', productId)
    if (schemaType) params.append('schema_type', schemaType)
    return fetchAPI<{ data: any[]; total: number }>(`/geo/schema?${params}`)
  },

  // 品牌知識 - Create
  createBrandKnowledge: (data: BrandKnowledgeCreate) =>
    fetchAPI<BrandKnowledgeResponse>('/geo/knowledge', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // 品牌知識 - Search
  searchBrandKnowledge: (query: string, knowledgeType?: string, limit = 10) => {
    const params = new URLSearchParams({ query, limit: String(limit) })
    if (knowledgeType) params.append('knowledge_type', knowledgeType)
    return fetchAPI<{ data: BrandKnowledgeResponse[]; total: number }>(`/geo/knowledge/search?${params}`)
  },

  // Brand knowledge - get product knowledge
  getProductKnowledge: (productId: string) =>
    fetchAPI<{ data: BrandKnowledgeResponse[]; total: number }>(`/geo/knowledge/product/${productId}`),

  // 品牌知識 - AI Generate專家Content
  generateExpertContent: (data: ExpertContentRequest) =>
    fetchAPI<BrandKnowledgeResponse>('/geo/knowledge/generate-expert', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // 品牌知識 - FetchDetails
  getBrandKnowledge: (knowledgeId: string) =>
    fetchAPI<BrandKnowledgeResponse>(`/geo/knowledge/${knowledgeId}`),
}


// =============================================
// ContentGenerate流水線 API (Content Pipeline)
// =============================================
// One AI call generates multilingual complete content pack: copy + SEO + GEO

export interface ContentPipelineInput {
  name: string
  brand?: string
  category?: string
  description?: string
  features?: string[]
  price?: number
  origin?: string
}

export interface ContentPipelineRequest {
  product_id?: string
  product_info?: ContentPipelineInput
  languages?: string[]  // 多語言Support，如 ['zh-HK', 'en']
  tone?: string
  include_faq?: boolean
  save_to_db?: boolean
}

// 單一語言的Content
export interface LocalizedContentResponse {
  language: string

  // 文案部分
  title: string
  selling_points: string[]
  description: string

  // SEO 部分
  meta_title: string
  meta_description: string
  primary_keyword: string
  secondary_keywords: string[]
  long_tail_keywords: string[]
  seo_score: number
  score_breakdown: Record<string, number>
  og_title: string
  og_description: string

  // AI 摘要部分
  ai_summary: string
  ai_facts: string[]
}

export interface ContentPipelineResponse {
  success: boolean
  product_info: Record<string, any>

  // Multilingual content (key = language code)
  localized: Record<string, LocalizedContentResponse>

  // 共用部分
  tone: string
  product_schema: Record<string, any>
  faq_schema?: Record<string, any>

  // 存儲 ID（每語言一個）
  content_ids: Record<string, string>
  seo_content_ids: Record<string, string>
  structured_data_id?: string

  // 元Data
  languages: string[]
  generation_time_ms: number
  model_used: string
  error?: string
}

export interface BatchPipelineRequest {
  products: ContentPipelineInput[]
  languages?: string[]  // 多語言Support
  tone?: string
  include_faq?: boolean
  save_to_db?: boolean
}

export interface BatchErrorItem {
  index: number
  product_name: string
  error: string
}

export interface BatchPipelineResponse {
  success: boolean
  total_products: number
  successful_count: number
  failed_count: number
  results: ContentPipelineResponse[]
  errors: BatchErrorItem[]
  total_time_ms: number
  languages: string[]
}

// =============================================
// ContentGenerateHistoryRecord
// =============================================

export interface PipelineHistoryItem {
  id: string
  product_id: string | null
  product_name: string
  languages: string[]
  tone: string
  preview_title: string | null
  preview_seo_score: number | null
  generation_time_ms: number
  model_used: string | null
  is_batch: boolean
  batch_index: number | null
  created_at: string
}

export interface PipelineHistoryDetail extends PipelineHistoryItem {
  product_info: Record<string, unknown> | null
  content_ids: Record<string, string> | null
  seo_content_ids: Record<string, string> | null
  structured_data_id: string | null
}

export interface PipelineHistoryListResponse {
  items: PipelineHistoryItem[]
  total: number
  page: number
  page_size: number
  has_more: boolean
}

export interface PipelineHistoryParams {
  page?: number
  page_size?: number
  language?: string
  is_batch?: boolean
  search?: string
}

export const contentPipelineApi = {
  // Generate multilingual content (copy + SEO + GEO)
  generate: (data: ContentPipelineRequest) =>
    fetchAPI<ContentPipelineResponse>('/content-pipeline/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // 批量Generate
  batchGenerate: (data: BatchPipelineRequest) =>
    fetchAPI<BatchPipelineResponse>('/content-pipeline/batch', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // FetchHistoryRecordList
  getHistory: (params?: PipelineHistoryParams) => {
    const searchParams = new URLSearchParams()
    if (params?.page) searchParams.set('page', params.page.toString())
    if (params?.page_size) searchParams.set('page_size', params.page_size.toString())
    if (params?.language) searchParams.set('language', params.language)
    if (params?.is_batch !== undefined) searchParams.set('is_batch', params.is_batch.toString())
    if (params?.search) searchParams.set('search', params.search)

    const queryString = searchParams.toString()
    return fetchAPI<PipelineHistoryListResponse>(
      `/content-pipeline/history${queryString ? `?${queryString}` : ''}`
    )
  },

  // FetchHistoryRecordDetails
  getHistoryDetail: (sessionId: string) =>
    fetchAPI<PipelineHistoryDetail>(`/content-pipeline/history/${sessionId}`),

  // DeleteHistoryRecord
  deleteHistory: (sessionId: string) =>
    fetchAPI<{ message: string; id: string }>(`/content-pipeline/history/${sessionId}`, {
      method: 'DELETE',
    }),

}


// =============================================
// Competitor v2 Types
// =============================================

export interface ComparisonSummary {
  total_competitors: number
  total_tracked_products: number
  our_products: number
  mapped_competitors: number
  price_alerts_24h: number
  we_are_cheapest_pct: number
  avg_price_diff_pct: number
  last_scan: string | null
}

export interface CompetitorPrice {
  competitor_name: string
  competitor_tier: number
  product_name: string
  product_name_en: string | null
  price: number | null
  original_price: number | null
  unit_price_per_100g: number | null
  price_change_7d: number | null
  stock_status: string | null
  stock_level: number | null
  url: string
  last_updated: string | null
}

export interface ProductComparison {
  product: {
    id: string
    name: string
    name_en: string | null
    sku: string
    price: number | null
    image_url: string | null
    category_tag: string | null
  }
  competitors: CompetitorPrice[]
  cheapest_competitor: string | null
  our_price_rank: number
  total_competitors: number
}

export interface MerchantOverview {
  competitor: {
    id: string
    name: string
    tier: number
    store_code: string | null
    total_products: number
    fresh_products: number
    overlap_products: number
    unique_products: number
  }
  price_comparison: {
    cheaper_count: number
    same_count: number
    expensive_count: number
    avg_price_diff_pct: number
  }
  recent_changes: Array<{
    product_name: string
    product_name_en: string | null
    change_type: string
    old_price: number | null
    new_price: number | null
    change_pct: number | null
    date: string
  }>
}

export interface PriceHistoryData {
  product: { id: string; name: string; name_en: string | null; price: number | null }
  dates: string[]
  our_price: number | null
  series: Array<{ id: string; name: string; data: (number | null)[] }>
}

export interface PricingSuggestion {
  product_id: string
  product_name: string
  product_name_en: string | null
  category: string | null
  our_price: number
  cheapest_competitor_price: number
  avg_competitor_price: number
  cheaper_count: number
  total_competitors: number
  price_diff_pct: number
  stockout_pct: number
  action: 'raise' | 'lower' | 'maintain'
  reason: string
  suggested_price: number | null
  priority: 'high' | 'medium' | 'low'
}
