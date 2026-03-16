'use client'

// =============================================
// 語言切換 Context — localStorage 記住偏好
// =============================================

import { createContext, useContext, useState, useCallback, useMemo } from 'react'
import type { Locale } from '@/i18n/types'
import { zhHK } from '@/i18n/zh-HK'
import { en } from '@/i18n/en'
import { createTranslator, type TranslateFunction } from '@/i18n/utils'
export { localeName } from '@/i18n/utils'

const dictionaries = { 'zh-HK': zhHK, en } as const

interface LocaleContextType {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: TranslateFunction
}

const STORAGE_KEY = 'gogojap-locale'

function getInitialLocale(): Locale {
  if (typeof window === 'undefined') return 'zh-HK'
  return (localStorage.getItem(STORAGE_KEY) as Locale) || 'zh-HK'
}

const defaultT = createTranslator(zhHK)

const LocaleContext = createContext<LocaleContextType>({
  locale: 'zh-HK',
  setLocale: () => {},
  t: defaultT,
})

export function LocaleProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(getInitialLocale)

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next)
    localStorage.setItem(STORAGE_KEY, next)
    document.documentElement.lang = next
  }, [])

  const t = useMemo(() => createTranslator(dictionaries[locale]), [locale])

  return (
    <LocaleContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </LocaleContext.Provider>
  )
}

export function useLocale() {
  return useContext(LocaleContext)
}
