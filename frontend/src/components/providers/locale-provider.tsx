'use client'

// =============================================
// 語言切換 Context — localStorage 記住偏好
// =============================================

import { createContext, useContext, useState, useCallback } from 'react'
import type { Locale, TranslationDict } from '@/i18n/types'
import { zhHK } from '@/i18n/zh-HK'
import { en } from '@/i18n/en'

const dictionaries: Record<Locale, TranslationDict> = { 'zh-HK': zhHK, en }

interface LocaleContextType {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: TranslationDict
}

const STORAGE_KEY = 'gogojap-locale'

function getInitialLocale(): Locale {
  if (typeof window === 'undefined') return 'zh-HK'
  return (localStorage.getItem(STORAGE_KEY) as Locale) || 'zh-HK'
}

const LocaleContext = createContext<LocaleContextType>({
  locale: 'zh-HK',
  setLocale: () => {},
  t: zhHK,
})

export function LocaleProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(getInitialLocale)

  const setLocale = useCallback((next: Locale) => {
    setLocaleState(next)
    localStorage.setItem(STORAGE_KEY, next)
    document.documentElement.lang = next
  }, [])

  const t = dictionaries[locale]

  return (
    <LocaleContext.Provider value={{ locale, setLocale, t }}>
      {children}
    </LocaleContext.Provider>
  )
}

export function useLocale() {
  return useContext(LocaleContext)
}
