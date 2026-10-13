'use client'

import { useQuery } from '@apollo/client/react'
import { ArrowRight, BookOpen } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { ExamsDocument, RecommendationsDocument, RhythmDocument, ViewerDocument } from '@/graphql/generated/graphql'
import { ExamCard } from './Exams'
import { Recommendations } from './Recommendations'
import { Today, Week } from './Rhythm'

/**
 * Home for a signed-in learner (P6h; lvn-backend ADR-0069–0071): a greeting, today's ring and this week's Rhythm, the
 * note to continue, the next exam's Readiness, and recommendations, each saying why.
 */
export function Home() {
  const t = useTranslations('homeDashboard')
  const viewer = useQuery(ViewerDocument).data?.viewer
  const rhythm = useQuery(RhythmDocument, { fetchPolicy: 'cache-and-network' }).data?.rhythm
  const exams = useQuery(ExamsDocument, { fetchPolicy: 'cache-and-network' }).data?.exams
  const recs = useQuery(RecommendationsDocument, { variables: { limit: 6 }, fetchPolicy: 'cache-and-network' }).data?.recommendations
  const firstName = viewer?.displayName.trim().split(/\s+/)[0]
  const next = exams?.find((e) => !e.past)
  const continueNote = recs?.find((r) => r.kind === 'CONTINUE_NOTE' && r.note)
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-extrabold tracking-tight">{firstName ? t('greeting', { name: firstName }) : t('greetingAnon')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      {rhythm ? (
        <>
          <Today r={rhythm} />
          <Week r={rhythm} />
          <Link href="/rhythm" className="-mt-3 inline-flex items-center gap-1 self-end text-sm font-semibold text-accent hover:underline">
            {t('openRhythm')} <ArrowRight aria-hidden className="size-4" />
          </Link>
        </>
      ) : null}
      {continueNote?.note ? (
        <section aria-labelledby="continue" className="flex flex-col gap-3">
          <h2 id="continue" className="text-lg font-bold">
            {t('continue')}
          </h2>
          <Link href={`/notes/${continueNote.note.id}`} className="flex items-center gap-4 rounded-2xl border border-border bg-surface p-4 hover:border-accent">
            <BookOpen aria-hidden className="size-6 shrink-0 text-accent" />
            <span className="flex min-w-0 flex-1 flex-col">
              <span className="truncate font-semibold">{continueNote.noteTitle || t('untitled')}</span>
              <span className="text-sm text-muted">{continueNote.reason}</span>
            </span>
          </Link>
        </section>
      ) : null}
      {exams ? (
        <section aria-labelledby="next-exam" className="flex flex-col gap-3">
          <div className="flex items-baseline justify-between">
            <h2 id="next-exam" className="text-lg font-bold">
              {t('nextExam')}
            </h2>
            <Link href="/exams" className="text-sm font-semibold text-accent hover:underline">
              {next ? t('allExams') : t('addExam')}
            </Link>
          </div>
          {next ? <ExamCard exam={next} /> : <p className="rounded-2xl border border-dashed border-border px-4 py-6 text-center text-sm text-muted">{t('noExam')}</p>}
        </section>
      ) : null}
      <Recommendations limit={6} />
    </div>
  )
}
