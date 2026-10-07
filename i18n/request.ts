import { getRequestConfig } from 'next-intl/server'

/** English only ships (section 12.2); every string still comes from messages/<locale>.json. */
export default getRequestConfig(async () => {
  const locale = 'en'
  return { locale, messages: (await import(`../messages/${locale}.json`)).default }
})
