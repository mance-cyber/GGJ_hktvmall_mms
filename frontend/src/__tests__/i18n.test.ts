// =============================================
// TDD: i18n 翻譯工具測試
// Phase 2: t['key'] → t('key', params) 升級
// =============================================

import { describe, it, expect } from 'vitest'
import { createTranslator, localeName } from '@/i18n/utils'
import type { TranslationDict } from '@/i18n/types'

// 測試用翻譯字典
const testDict: TranslationDict = {
  'common.loading': 'Loading...',
  'common.error': 'An error occurred',
  'common.save': 'Save',
  'common.cancel': 'Cancel',
  'common.confirm': 'Confirm',
  'common.delete': 'Delete',
  'common.search': 'Search',
  'common.more': 'More',
  'common.logout': 'Logout',
  'common.admin': 'Admin',
  'common.operator': 'Operator',
  'common.viewer': 'Viewer',
  'sidebar.system_name': 'AI Operations',
  'sidebar.overview': 'Overview',
  'sidebar.dashboard': 'Dashboard',
  'sidebar.roi': 'ROI',
  'sidebar.roi_desc': 'How much GoGoJap earns for you',
  'sidebar.market_intel': 'Market Intel',
  'sidebar.ai_assistant': 'AI Assistant',
  'sidebar.market_response': 'Market Response',
  'sidebar.competitor_monitor': 'Competitors',
  'sidebar.price_trends': 'Price Trends',
  'sidebar.seo_ranking': 'SEO Ranking',
  'sidebar.product_mgmt': 'Products',
  'sidebar.pricing_approval': 'Price Approval',
  'sidebar.pricing_approval_desc': 'Human-in-the-Loop AI pricing review',
  'sidebar.product_library': 'Product Library',
  'sidebar.categories': 'Categories',
  'sidebar.ai_image': 'AI Image Gen',
  'sidebar.content_pipeline': 'Content Pipeline',
  'sidebar.content_history': 'Content History',
  'sidebar.ai_analysis': 'AI Analysis',
  'sidebar.notifications': 'Alerts',
  'sidebar.alert_center': 'Alert Center',
  'sidebar.system': 'System',
  'sidebar.agent_team': 'Agent Team',
  'sidebar.agent_team_desc': 'Agent team status & control',
  'sidebar.ai_settings': 'AI Settings',
  'sidebar.data_export': 'Data Export',
  'sidebar.settings': 'Settings',
  'mobile.home': 'Home',
  'mobile.alerts': 'Alerts',
  'mobile.ai': 'AI',
  'mobile.competitor_monitor': 'Competitors',
  'mobile.product_library': 'Products',
  'mobile.ai_content': 'Content',
  'mobile.price_trends': 'Trends',
  'mobile.settings': 'Settings',
  // 帶插值的 key
  'test.greeting': 'Hello, {name}!',
  'test.count': '{n} items selected',
  'test.range': 'Page {current} of {total}',
  'test.no_params': 'No parameters here',
} as TranslationDict

// =============================================
// createTranslator 測試
// =============================================

describe('createTranslator', () => {
  const t = createTranslator(testDict)

  // ---- 基本查詢 ----

  it('應該返回已有 key 的翻譯文字', () => {
    expect(t('common.loading')).toBe('Loading...')
    expect(t('common.save')).toBe('Save')
  })

  it('應該對未知 key 返回 key 本身作為 fallback', () => {
    expect(t('nonexistent.key')).toBe('nonexistent.key')
  })

  // ---- 插值 ----

  it('應該替換單個 {variable} 佔位符', () => {
    expect(t('test.greeting', { name: 'Alice' })).toBe('Hello, Alice!')
  })

  it('應該替換數字佔位符', () => {
    expect(t('test.count', { n: 5 })).toBe('5 items selected')
  })

  it('應該替換多個佔位符', () => {
    expect(t('test.range', { current: 3, total: 10 })).toBe('Page 3 of 10')
  })

  it('無佔位符但傳入 params 應不受影響', () => {
    expect(t('test.no_params', { foo: 'bar' })).toBe('No parameters here')
  })

  it('有佔位符但未傳入對應 param 應保留原始佔位符', () => {
    expect(t('test.greeting')).toBe('Hello, {name}!')
  })

  it('param 值為 0 應正確顯示', () => {
    expect(t('test.count', { n: 0 })).toBe('0 items selected')
  })

  it('param 值為空字串應正確顯示', () => {
    expect(t('test.greeting', { name: '' })).toBe('Hello, !')
  })
})

// =============================================
// localeName 測試
// =============================================

describe('localeName', () => {
  it('英文 locale 時返回 name_en（有值）', () => {
    const product = { name: '日本和牛', name_en: 'Japanese Wagyu' }
    expect(localeName(product, 'en')).toBe('Japanese Wagyu')
  })

  it('英文 locale 但 name_en 為 null 時回退到 name', () => {
    const product = { name: '日本和牛', name_en: null }
    expect(localeName(product, 'en')).toBe('日本和牛')
  })

  it('中文 locale 時返回 name_zh（有值）', () => {
    const product = { name: 'default', name_zh: '日本和牛' }
    expect(localeName(product, 'zh-HK')).toBe('日本和牛')
  })

  it('中文 locale 但 name_zh 為 null 時回退到 name', () => {
    const product = { name: '日本和牛', name_zh: null }
    expect(localeName(product, 'zh-HK')).toBe('日本和牛')
  })

  it('競品商品只有 name + name_en（無 name_zh）在中文 locale 回退到 name', () => {
    const product = { name: '澳洲和牛 M9', name_en: 'Australian Wagyu M9' }
    expect(localeName(product, 'zh-HK')).toBe('澳洲和牛 M9')
  })

  it('所有欄位齊全時各 locale 正確選取', () => {
    const product = { name: 'default', name_en: 'English Name', name_zh: '中文名', name_ja: '日本語名' }
    expect(localeName(product, 'en')).toBe('English Name')
    expect(localeName(product, 'zh-HK')).toBe('中文名')
  })
})
