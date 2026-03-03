'use client'

// =============================================
// 語言切換按鈕 — 放在側欄底部
// =============================================

import { useLocale } from '@/components/providers/locale-provider'
import { Languages } from 'lucide-react'

export function LocaleToggle() {
  const { locale, setLocale } = useLocale()

  return (
    <button
      type="button"
      onClick={() => setLocale(locale === 'zh-HK' ? 'en' : 'zh-HK')}
      className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm
                 text-gray-500 hover:text-gray-700 hover:bg-white/50
                 rounded-lg transition-all border border-transparent
                 hover:border-purple-200/30"
    >
      <Languages className="w-4 h-4" />
      <span className="font-medium">
        {locale === 'zh-HK' ? 'English' : '中文'}
      </span>
    </button>
  )
}
