// =============================================
// i18n 工具函數
// =============================================
//
// createTranslator: 將 TranslationDict 包裝成可調用函數
//   - t('key') → 查詢翻譯
//   - t('key', { n: 5 }) → 查詢 + 插值
//
// localeName: 根據 locale 選取多語言產品名稱
// =============================================

import type { Locale, TranslationDict } from './types'

/**
 * 翻譯函數類型。
 *
 * 支持兩種調用方式：
 *   t('key')            → 直接查詢
 *   t('key', { n: 5 })  → 查詢 + 插值 {n} → 5
 */
export type TranslateFunction = (
  key: string,
  params?: Record<string, string | number>,
) => string

/**
 * 將平面翻譯字典包裝成可調用的翻譯函數。
 *
 * - 已有 key → 返回翻譯文字
 * - 未知 key → 返回 key 本身（開發環境可 console.warn）
 * - 支持 {variable} 佔位符插值
 */
export function createTranslator(dict: TranslationDict): TranslateFunction {
  return (key: string, params?: Record<string, string | number>): string => {
    const template = dict[key]

    // 未知 key → fallback 到 key 本身
    if (template === undefined) {
      if (typeof window !== 'undefined' && process.env.NODE_ENV === 'development') {
        console.warn(`[i18n] Missing key: "${key}"`)
      }
      return key
    }

    // 無需插值 → 直接返回
    if (!params) return template

    // 替換所有 {variable} 佔位符
    return template.replace(/\{(\w+)\}/g, (match, name) => {
      const value = params[name]
      return value !== undefined ? String(value) : match
    })
  }
}

/**
 * 根據當前 locale 選取最合適的產品名稱。
 *
 * 競品商品：name（中文原始）、name_en
 * 自家商品：name（預設）、name_zh、name_ja、name_en
 *
 * Fallback 策略：若目標語言欄位為空，回退到 name。
 */
export function localeName(
  product: { name: string; name_en?: string | null; name_zh?: string | null; name_ja?: string | null },
  locale: Locale,
): string {
  switch (locale) {
    case 'en':
      return product.name_en || product.name
    case 'zh-HK':
      return product.name_zh || product.name
    default:
      return product.name
  }
}
