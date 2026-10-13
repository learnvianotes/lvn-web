'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useApolloClient, useLazyQuery, useMutation } from '@apollo/client/react'
import { BookOpen, Link2 } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useEffect, useId, useMemo, useRef, useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { putToStorage, UploadError } from '@/features/notes/media'
import {
  CompleteNoteUploadDocument,
  CreateNoteUploadDocument,
  MyResourcesDocument,
  ResourcePreviewDocument,
  ResourceTopicOptionsDocument,
  SubmitResourceDocument,
  UpdateResourceDocument,
  type ResourceFieldsFragment,
  type ResourceType,
} from '@/graphql/generated/graphql'
import { RESOURCE_LIMITS } from '@/lib/contracts/validation'

export const RESOURCE_TYPES: ResourceType[] = ['BOOK', 'COURSE', 'TOOL', 'SOFTWARE', 'HARDWARE', 'OTHER']
type Topic = { id: string; title: string }
const input = 'h-11 rounded-xl border border-border bg-bg px-3 text-sm'

/**
 * Adding a resource (lvn-backend ADR-0074), or editing one's own before it is approved: a link or an ISBN fills the
 * form from the page or Open Library, the person checks every field, and it goes to moderators.
 */
export function ResourceForm({ resource }: { resource?: ResourceFieldsFragment }) {
  const t = useTranslations('resources.form')
  const types = useTranslations('resources.type')
  const router = useRouter()
  const client = useApolloClient()
  const fileInput = useRef<HTMLInputElement>(null)
  const [url, setUrl] = useState(resource?.url ?? '')
  const [isbn, setIsbn] = useState(resource?.isbn ?? '')
  const [type, setType] = useState<ResourceType | ''>(resource?.type ?? '')
  const [title, setTitle] = useState(resource?.title ?? '')
  const [author, setAuthor] = useState(resource?.author ?? '')
  const [description, setDescription] = useState(resource?.description ?? '')
  const [topics, setTopics] = useState<Topic[]>(resource?.topics.flatMap((x) => (x ? [{ id: x.id, title: x.title }] : [])) ?? [])
  const [foundImage, setFoundImage] = useState<string | null>(null)
  const [useFound, setUseFound] = useState(true)
  const [file, setFile] = useState<File | null>(null)
  const [removeCover, setRemoveCover] = useState(false)
  const [notice, setNotice] = useState<'notFound' | null>(null)
  const [existing, setExisting] = useState<{ id: string; title: string } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [preview, previewing] = useLazyQuery(ResourcePreviewDocument, { fetchPolicy: 'network-only' })
  const fileSrc = useMemo(() => (file ? URL.createObjectURL(file) : null), [file])
  useEffect(() => () => void (fileSrc && URL.revokeObjectURL(fileSrc)), [fileSrc])
  const [submit] = useMutation(SubmitResourceDocument)
  const [update] = useMutation(UpdateResourceDocument)

  const lookUp = async (by: 'url' | 'isbn') => {
    setError(null)
    setNotice(null)
    setExisting(null)
    try {
      const res = await preview({ variables: { input: by === 'url' ? { url } : { isbn } } })
      if (res.error) throw res.error
      const p = res.data?.resourcePreview
      if (!p) return
      if (p.url) setUrl(p.url)
      if (p.isbn) setIsbn(p.isbn)
      if (p.type) setType(p.type)
      if (p.title) setTitle(p.title)
      if (p.author) setAuthor(p.author)
      if (p.description) setDescription(p.description.slice(0, RESOURCE_LIMITS.description))
      setFoundImage(p.imageUrl ?? null)
      setUseFound(!!p.imageUrl)
      setExisting(p.existing ? { id: p.existing.id, title: p.existing.title } : null)
      if (!p.found) setNotice('notFound')
    } catch (e) {
      setError(CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
    }
  }

  const uploadCover = async (picked: File): Promise<string> => {
    const res = await client.mutate({ mutation: CreateNoteUploadDocument, variables: { input: { fileName: picked.name, mimeType: picked.type, sizeBytes: picked.size, purpose: 'COVER' } } })
    const intent = res.data?.createUploadIntent.intent
    if (!intent) throw new UploadError(res.data?.createUploadIntent.userErrors[0]?.message ?? t('failed'))
    await putToStorage(intent, picked, () => undefined)
    const done = await client.mutate({ mutation: CompleteNoteUploadDocument, variables: { fileId: intent.fileId } })
    if (!done.data?.completeUpload.ok) throw new UploadError(done.data?.completeUpload.userErrors[0]?.message ?? t('failed'))
    return intent.fileId
  }

  const send = async () => {
    if (!type) return
    setError(null)
    setBusy(true)
    try {
      const coverFileId = file ? await uploadCover(file) : null
      const fields = {
        type,
        title,
        url,
        isbn: type === 'BOOK' && isbn.trim() ? isbn.trim() : null,
        author: author.trim() || null,
        description: description.trim() || null,
        topicIds: topics.map((x) => x.id),
        coverFileId,
        imageUrl: !coverFileId && useFound && foundImage ? foundImage : null,
      }
      const payload = resource
        ? (await update({ variables: { input: { id: resource.id, ...fields, removeCover: removeCover && !coverFileId } } })).data?.updateResource
        : (await submit({ variables: { input: fields } })).data?.submitResource
      const problem = payload?.userErrors[0]?.message
      if (problem || !payload?.resource) throw new UploadError(problem ?? t('failed'))
      await client.refetchQueries({ include: [MyResourcesDocument] })
      router.push(`/resources/${payload.resource.id}`)
    } catch (e) {
      setError(e instanceof UploadError && !/^(network|storage answered)/.test(e.message) ? e.message : CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
    } finally {
      setBusy(false)
    }
  }

  const ready = !!type && title.trim().length >= RESOURCE_LIMITS.title.min && !!url.trim() && topics.length >= RESOURCE_LIMITS.topics.min && !busy
  const showsCover = !removeCover && (file || (useFound && foundImage) || (!foundImage && resource?.coverUrl))
  return (
    <form
      aria-label={resource ? t('editTitle') : t('title')}
      className="flex flex-col gap-5"
      onSubmit={(e) => {
        e.preventDefault()
        void send()
      }}
    >
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-extrabold tracking-tight">{resource ? t('editTitle') : t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>

      <section className="grid gap-3 rounded-2xl border border-border bg-surface p-4 sm:grid-cols-2">
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium">{t('link')}</span>
          <span className="flex gap-2">
            <input type="url" inputMode="url" required maxLength={RESOURCE_LIMITS.url} value={url} placeholder="https://" onChange={(e) => setUrl(e.target.value)} className={`${input} min-w-0 flex-1`} />
            <Button type="button" variant="secondary" disabled={!url.trim() || previewing.loading} onClick={() => void lookUp('url')} className="gap-1.5">
              <Link2 className="size-4" aria-hidden />
              {t('lookUp')}
            </Button>
          </span>
          <span className="text-xs text-muted">{t('linkHint')}</span>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium">{t('isbn')}</span>
          <span className="flex gap-2">
            <input inputMode="numeric" maxLength={20} value={isbn} onChange={(e) => setIsbn(e.target.value)} className={`${input} min-w-0 flex-1`} />
            <Button type="button" variant="secondary" disabled={!isbn.trim() || previewing.loading} onClick={() => void lookUp('isbn')} className="gap-1.5">
              <BookOpen className="size-4" aria-hidden />
              {t('lookUpIsbn')}
            </Button>
          </span>
          <span className="text-xs text-muted">{t('isbnHint')}</span>
        </label>
        {previewing.loading ? <p className="text-sm text-muted sm:col-span-2">{t('lookingUp')}</p> : null}
        {notice ? <p className="text-sm text-muted sm:col-span-2">{t(notice)}</p> : null}
        {existing ? (
          <p role="status" className="text-sm sm:col-span-2">
            {t('exists')}{' '}
            <Link href={`/resources/${existing.id}`} className="font-semibold text-accent hover:underline">
              {existing.title}
            </Link>
          </p>
        ) : null}
      </section>

      <fieldset className="flex flex-col gap-2">
        <legend className="mb-1 text-sm font-medium">{t('type')}</legend>
        <div className="flex flex-wrap gap-2">
          {RESOURCE_TYPES.map((v) => (
            <label key={v} className={`cursor-pointer rounded-full border px-3 py-1.5 text-sm ${type === v ? 'border-accent bg-accent-soft font-semibold text-accent' : 'border-border'}`}>
              <input type="radio" name="type" className="sr-only" checked={type === v} onChange={() => setType(v)} />
              {types(v)}
            </label>
          ))}
        </div>
      </fieldset>

      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium">{t('name')}</span>
        <input required minLength={RESOURCE_LIMITS.title.min} maxLength={RESOURCE_LIMITS.title.max} value={title} onChange={(e) => setTitle(e.target.value)} className={input} />
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium">{t('author')}</span>
        <input maxLength={RESOURCE_LIMITS.author} value={author} onChange={(e) => setAuthor(e.target.value)} className={input} />
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium">{t('description')}</span>
        <textarea maxLength={RESOURCE_LIMITS.description} rows={4} value={description} placeholder={t('descriptionHint')} onChange={(e) => setDescription(e.target.value)} className="rounded-xl border border-border bg-bg px-3 py-2" />
      </label>

      <TopicPicker picked={topics} onChange={setTopics} />

      <fieldset className="flex flex-col gap-2">
        <legend className="mb-1 text-sm font-medium">{t('cover')}</legend>
        {showsCover ? (
          // eslint-disable-next-line @next/next/no-img-element -- a picture on another site or in storage, shown once
          <img src={fileSrc ?? (useFound && foundImage ? foundImage : (resource?.coverUrl ?? ''))} alt="" referrerPolicy="no-referrer" className="h-40 w-auto self-start rounded-xl border border-border object-contain" />
        ) : null}
        {foundImage && !file ? (
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={useFound} onChange={(e) => setUseFound(e.target.checked)} />
            {t('useFound')}
          </label>
        ) : null}
        <input
          ref={fileInput}
          type="file"
          accept={RESOURCE_LIMITS.coverTypes.join(',')}
          className="sr-only"
          aria-label={t('upload')}
          onChange={(e) => {
            const picked = e.target.files?.[0]
            e.target.value = ''
            if (picked && (RESOURCE_LIMITS.coverTypes as readonly string[]).includes(picked.type) && picked.size <= RESOURCE_LIMITS.coverBytes) {
              setFile(picked)
              setRemoveCover(false)
            }
          }}
        />
        <div className="flex flex-wrap gap-2">
          <Button type="button" size="sm" variant="secondary" onClick={() => fileInput.current?.click()}>
            {t('upload')}
          </Button>
          {showsCover ? (
            <Button
              type="button"
              size="sm"
              variant="ghost"
              onClick={() => {
                setFile(null)
                setUseFound(false)
                setRemoveCover(true)
              }}
            >
              {t('removeCover')}
            </Button>
          ) : null}
        </div>
      </fieldset>

      {error ? <Alert tone="error">{error}</Alert> : null}
      <div className="flex flex-wrap gap-2">
        <Button type="submit" disabled={!ready}>
          {resource ? (resource.status === 'REJECTED' ? t('saveAgain') : t('save')) : t('send')}
        </Button>
        <Button type="button" variant="ghost" onClick={() => router.back()}>
          {t('cancel')}
        </Button>
      </div>
    </form>
  )
}

/** Curated topics only (lvn-backend ADR-0074): a person's own topics are private to them. */
function TopicPicker({ picked, onChange }: { picked: Topic[]; onChange: (topics: Topic[]) => void }) {
  const t = useTranslations('resources.form')
  const inputId = useId()
  const [query, setQuery] = useState('')
  const [find, found] = useLazyQuery(ResourceTopicOptionsDocument)
  useEffect(() => {
    if (query.trim().length < 2) return
    const timer = setTimeout(() => void find({ variables: { query: query.trim() } }), 250)
    return () => clearTimeout(timer)
  }, [query, find])
  const options = query.trim().length >= 2 ? (found.data?.resourceTopicOptions ?? []).filter((o) => !picked.some((p) => p.id === o.id)) : []
  return (
    <fieldset className="flex flex-col gap-2">
      <legend className="mb-1 text-sm font-medium">{t('topics')}</legend>
      {picked.length ? (
        <ul className="flex flex-wrap gap-2">
          {picked.map((p) => (
            <li key={p.id} className="flex items-center gap-1 rounded-full bg-accent-soft py-1 pl-3 pr-1 text-sm text-accent">
              {p.title}
              <button type="button" aria-label={t('removeTopic', { title: p.title })} className="rounded-full px-2 hover:bg-accent/10" onClick={() => onChange(picked.filter((x) => x.id !== p.id))}>
                ×
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      {picked.length < RESOURCE_LIMITS.topics.max ? (
        <>
          <label htmlFor={inputId} className="sr-only">
            {t('findTopic')}
          </label>
          <input id={inputId} type="search" value={query} placeholder={t('findTopic')} onChange={(e) => setQuery(e.target.value)} className={input} />
          <p className="text-xs text-muted">{t('findTopicHelp')}</p>
          {query.trim().length >= 2 && found.data && !options.length ? <p className="text-sm text-muted">{t('noTopicFound')}</p> : null}
          {options.length ? (
            <ul className="flex flex-col gap-1">
              {options.slice(0, 8).map((o) => (
                <li key={o.id}>
                  <button
                    type="button"
                    aria-label={t('addTopic', { title: o.title })}
                    className="flex w-full items-baseline justify-between gap-2 rounded-lg px-3 py-2 text-left text-sm hover:bg-surface-2"
                    onClick={() => {
                      onChange([...picked, { id: o.id, title: o.title }])
                      setQuery('')
                    }}
                  >
                    <span>{o.title}</span>
                    <span className="text-xs text-muted">{o.subjectTitle}</span>
                  </button>
                </li>
              ))}
            </ul>
          ) : null}
        </>
      ) : null}
    </fieldset>
  )
}
