import { getTranslations } from 'next-intl/server'

/** Shown when the catalogue could not be asked for. A missing subject is a 404 instead. */
export async function SubjectsDown() {
  const t = await getTranslations('subjects')
  return (
    <div className="mx-auto flex min-h-[40dvh] max-w-xl flex-col justify-center gap-3 px-4 py-16">
      <h1 className="text-2xl font-bold tracking-tight">{t('title')}</h1>
      <p className="text-muted">{t('unavailable')}</p>
    </div>
  )
}
