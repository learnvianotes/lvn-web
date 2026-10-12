'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation, useQuery } from '@apollo/client/react'
import { ArrowDown, ArrowUp, Plus, Trash2 } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { MyTeacherProfileDocument, UpdateTeacherProfileDocument, type TeacherSkillKind } from '@/graphql/generated/graphql'

type Item = { key: number; kind: TeacherSkillKind; name: string; detail: string }
const KINDS: TeacherSkillKind[] = ['QUALIFICATION', 'EXPERIENCE', 'SKILL']
let next = 0

/** A teacher's Skills tab, by hand (lvn-backend ADR-0012, ADR-0044): headline, bio and items, saved in one go. */
export function SkillsEditor() {
  const t = useTranslations('people.skills')
  const { data, loading } = useQuery(MyTeacherProfileDocument, { fetchPolicy: 'cache-and-network' })
  const [save, saving] = useMutation(UpdateTeacherProfileDocument)
  const [headline, setHeadline] = useState('')
  const [bio, setBio] = useState('')
  const [items, setItems] = useState<Item[]>([])
  const [loaded, setLoaded] = useState(false)
  const [message, setMessage] = useState<{ ok: boolean; text: string } | null>(null)
  const viewer = data?.viewer

  useEffect(() => {
    const p = viewer?.teacherProfile
    if (loaded || !viewer) return
    setHeadline(p?.headline ?? '')
    setBio(p?.bio ?? '')
    setItems((p?.skills ?? []).map((s) => ({ key: next++, kind: s.kind, name: s.name, detail: s.detail ?? '' })))
    setLoaded(true)
  }, [viewer, loaded])

  if (loading && !viewer) return <p role="status" className="text-sm text-muted">{t('loading')}</p>
  if (viewer && viewer.globalRole !== 'TEACHER') return <p className="text-muted">{t('teachersOnly')}</p>

  const update = (key: number, change: Partial<Item>) => setItems((list) => list.map((i) => (i.key === key ? { ...i, ...change } : i)))
  const move = (index: number, by: -1 | 1) =>
    setItems((list) => {
      const copy = [...list]
      const [item] = copy.splice(index, 1)
      copy.splice(index + by, 0, item!)
      return copy
    })

  const submit = async () => {
    setMessage(null)
    try {
      const res = await save({ variables: { input: { headline: headline || null, bio: bio || null, skills: items.map((i) => ({ kind: i.kind, name: i.name, detail: i.detail || null })) } } })
      const problem = res.data?.updateTeacherProfile.userErrors[0]?.message
      setMessage(problem ? { ok: false, text: problem } : { ok: true, text: t('saved') })
    } catch (e) {
      setMessage({ ok: false, text: CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed') })
    }
  }

  return (
    <form
      className="mx-auto flex max-w-2xl flex-col gap-5"
      onSubmit={(e) => {
        e.preventDefault()
        void submit()
      }}
    >
      <header className="flex items-center justify-between gap-3">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('editTitle')}</h1>
        {viewer ? (
          <Link href={`/u/${viewer.handle}`} className="text-sm font-medium text-accent hover:underline">
            {t('seeProfile')}
          </Link>
        ) : null}
      </header>
      <p className="text-sm text-muted">{t('lead')}</p>
      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-semibold">{t('headline')}</span>
        <input value={headline} maxLength={120} onChange={(e) => setHeadline(e.target.value)} className="h-11 rounded-xl border border-border bg-surface px-3" placeholder={t('headlineHint')} />
      </label>
      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-semibold">{t('bio')}</span>
        <textarea value={bio} maxLength={2000} rows={4} onChange={(e) => setBio(e.target.value)} className="rounded-xl border border-border bg-surface px-3 py-2" />
      </label>
      <section aria-labelledby="skills-items" className="flex flex-col gap-3">
        <h2 id="skills-items" className="text-sm font-semibold">
          {t('items')}
        </h2>
        {items.map((item, i) => (
          <fieldset key={item.key} className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-3">
            <legend className="sr-only">{t('item', { n: i + 1 })}</legend>
            <div className="flex gap-2">
              <label className="shrink-0">
                <span className="sr-only">{t('kindLabel')}</span>
                <select value={item.kind} onChange={(e) => update(item.key, { kind: e.target.value as TeacherSkillKind })} className="h-10 rounded-lg border border-border bg-bg px-2 text-sm">
                  {KINDS.map((k) => (
                    <option key={k} value={k}>
                      {t(`kind.${k}`)}
                    </option>
                  ))}
                </select>
              </label>
              <label className="min-w-0 flex-1">
                <span className="sr-only">{t('name')}</span>
                <input value={item.name} maxLength={120} required onChange={(e) => update(item.key, { name: e.target.value })} placeholder={t('name')} className="h-10 w-full rounded-lg border border-border bg-bg px-3 text-sm" />
              </label>
            </div>
            <div className="flex gap-2">
              <label className="min-w-0 flex-1">
                <span className="sr-only">{t('detail')}</span>
                <input value={item.detail} maxLength={500} onChange={(e) => update(item.key, { detail: e.target.value })} placeholder={t('detail')} className="h-10 w-full rounded-lg border border-border bg-bg px-3 text-sm" />
              </label>
              <Button type="button" variant="ghost" size="icon" aria-label={t('up')} disabled={i === 0} onClick={() => move(i, -1)}>
                <ArrowUp className="size-4" aria-hidden />
              </Button>
              <Button type="button" variant="ghost" size="icon" aria-label={t('down')} disabled={i === items.length - 1} onClick={() => move(i, 1)}>
                <ArrowDown className="size-4" aria-hidden />
              </Button>
              <Button type="button" variant="ghost" size="icon" aria-label={t('remove', { name: item.name || t('item', { n: i + 1 }) })} onClick={() => setItems((list) => list.filter((x) => x.key !== item.key))}>
                <Trash2 className="size-4" aria-hidden />
              </Button>
            </div>
          </fieldset>
        ))}
        <Button type="button" variant="secondary" className="w-fit gap-1.5" disabled={items.length >= 60} onClick={() => setItems((list) => [...list, { key: next++, kind: 'SKILL', name: '', detail: '' }])}>
          <Plus className="size-4" aria-hidden />
          {t('add')}
        </Button>
      </section>
      {message ? (
        <p role={message.ok ? 'status' : 'alert'} className={message.ok ? 'text-sm text-accent' : 'text-sm text-red-600 dark:text-red-400'}>
          {message.text}
        </p>
      ) : null}
      <Button type="submit" className="w-fit" disabled={saving.loading}>
        {t('save')}
      </Button>
    </form>
  )
}
