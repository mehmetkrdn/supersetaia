import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'

import tr from './tr.json'
import en from './en.json'
import fr from './fr.json'
import ar from './ar.json'

const SUPPORTED = ['tr', 'en', 'fr', 'ar']

function getInitialLanguage() {
  const saved = localStorage.getItem('app_ui_locale')
  if (SUPPORTED.includes(saved)) return saved

  const nav = (navigator.language || '').toLowerCase()
  if (nav.startsWith('tr')) return 'tr'
  if (nav.startsWith('fr')) return 'fr'
  if (nav.startsWith('ar')) return 'ar'
  return 'en'
}

i18n.use(initReactI18next).init({
  resources: {
    tr: { translation: tr },
    en: { translation: en },
    fr: { translation: fr },
    ar: { translation: ar },
  },
  lng: getInitialLanguage(),
  fallbackLng: 'tr',
  interpolation: { escapeValue: false },
})

export const supportedLanguages = SUPPORTED

export function applyDocumentDirection(lang) {
  const dir = lang === 'ar' ? 'rtl' : 'ltr'
  document.documentElement.setAttribute('dir', dir)
  document.documentElement.setAttribute('lang', lang)
}

applyDocumentDirection(i18n.language)

i18n.on('languageChanged', (lng) => {
  localStorage.setItem('app_ui_locale', lng)
  applyDocumentDirection(lng)
})

export default i18n
