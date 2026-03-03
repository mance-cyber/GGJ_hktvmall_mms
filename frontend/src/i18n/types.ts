// =============================================
// i18n 類型定義 — 扁平化 key-value 結構
// =============================================

export type Locale = 'zh-HK' | 'en'

export interface TranslationDict {
  // ==================== 通用 ====================
  'common.loading': string
  'common.error': string
  'common.save': string
  'common.cancel': string
  'common.confirm': string
  'common.delete': string
  'common.search': string
  'common.more': string
  'common.logout': string
  'common.admin': string
  'common.operator': string
  'common.viewer': string

  // ==================== 側欄 ====================
  'sidebar.system_name': string
  'sidebar.overview': string
  'sidebar.dashboard': string
  'sidebar.roi': string
  'sidebar.roi_desc': string
  'sidebar.market_intel': string
  'sidebar.ai_assistant': string
  'sidebar.market_response': string
  'sidebar.competitor_monitor': string
  'sidebar.price_trends': string
  'sidebar.seo_ranking': string
  'sidebar.product_mgmt': string
  'sidebar.pricing_approval': string
  'sidebar.pricing_approval_desc': string
  'sidebar.product_library': string
  'sidebar.categories': string
  'sidebar.ai_image': string
  'sidebar.content_pipeline': string
  'sidebar.content_history': string
  'sidebar.ai_analysis': string
  'sidebar.notifications': string
  'sidebar.alert_center': string
  'sidebar.system': string
  'sidebar.agent_team': string
  'sidebar.agent_team_desc': string
  'sidebar.ai_settings': string
  'sidebar.data_export': string
  'sidebar.settings': string

  // ==================== 移動端底部導航 ====================
  'mobile.home': string
  'mobile.alerts': string
  'mobile.ai': string
  'mobile.competitor_monitor': string
  'mobile.product_library': string
  'mobile.ai_content': string
  'mobile.price_trends': string
  'mobile.settings': string

  // 各頁面 key 在遷移時逐步追加
  [key: string]: string
}
