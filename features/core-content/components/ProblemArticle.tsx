import { getTranslations } from 'next-intl/server'
import { cn } from '@/lib/cn'
import { codeTabsHtml, renderContent } from '../render'
import type { Problem, Solution } from '../schema'
import { ContentHtml } from './ContentHtml'

const difficultyClass = {
  Easy: 'bg-[color-mix(in_srgb,var(--good)_14%,transparent)] text-[var(--good)]',
  Medium: 'bg-[color-mix(in_srgb,var(--warn)_14%,transparent)] text-[var(--warn)]',
  Hard: 'bg-[color-mix(in_srgb,var(--bad)_14%,transparent)] text-[var(--bad)]',
}

export async function ProblemArticle({ problem, index }: { problem: Problem; index: number }) {
  const t = await getTranslations('core.problem')
  const part = (html: string, key: string) => (html.trim() ? renderContent(html, `${problem.id}-${key}`).html : '')
  const sections = [
    ['statement', problem.statement],
    ['understanding', problem.understanding],
    ['intuition', problem.intuition],
    ['approach', problem.approach],
  ] as const

  return (
    <article id={problem.id} className="mb-8 scroll-mt-20 rounded-2xl border border-border bg-surface p-5 sm:p-6">
      <header className="flex flex-wrap items-center gap-x-3 gap-y-2">
        <span className="text-sm font-semibold text-muted">{index}.</span>
        <h2 className="text-xl font-semibold tracking-tight">{problem.title}</h2>
        <span className={cn('rounded-full px-2.5 py-0.5 text-xs font-semibold', difficultyClass[problem.difficulty])}>
          {t(`difficulty.${problem.difficulty}`)}
        </span>
        <span className="ml-auto flex gap-3 text-sm">
          <a href={problem.leetcodeUrl} target="_blank" rel="noopener nofollow" className="text-accent hover:underline">
            {t('leetcode')} <i className="ti ti-external-link" aria-hidden />
          </a>
          {problem.youtubeUrl && (
            <a href={problem.youtubeUrl} target="_blank" rel="noopener nofollow" className="text-accent hover:underline">
              {t('video')} <i className="ti ti-brand-youtube" aria-hidden />
            </a>
          )}
        </span>
      </header>
      {sections.map(([key, html]) => {
        const rendered = part(html, key)
        if (!rendered) return null
        return (
          <section key={key} className="mt-6">
            <h3 className="mb-2 text-sm font-semibold uppercase tracking-wider text-muted">{t(key)}</h3>
            <ContentHtml html={rendered} />
          </section>
        )
      })}
      {problem.naive && <SolutionBlock id={`${problem.id}-naive`} solution={problem.naive} />}
      {problem.optimal && <SolutionBlock id={`${problem.id}-optimal`} solution={problem.optimal} />}
      {problem.takeaway.trim() && (
        <section className="mt-6">
          <h3 className="mb-2 text-sm font-semibold uppercase tracking-wider text-muted">{t('takeaway')}</h3>
          <ContentHtml html={part(problem.takeaway, 'takeaway')} />
        </section>
      )}
      {problem.similar.length > 0 && (
        <section className="mt-6">
          <h3 className="mb-2 text-sm font-semibold uppercase tracking-wider text-muted">{t('similar')}</h3>
          <ul className="flex flex-wrap gap-2">
            {problem.similar.map((s) => (
              <li key={s.url}>
                <a href={s.url} target="_blank" rel="noopener nofollow" className="inline-block rounded-full border border-border px-3 py-1 text-sm hover:border-accent">
                  {s.title}
                </a>
              </li>
            ))}
          </ul>
        </section>
      )}
    </article>
  )
}

function SolutionBlock({ id, solution }: { id: string; solution: Solution }) {
  const html = renderContent(solution.html + codeTabsHtml(solution.code), id).html
  return (
    <section className="mt-6">
      <h3 className="mb-2 text-lg font-semibold tracking-tight">{solution.title}</h3>
      {solution.complexity.length > 0 && (
        <p className="mb-3 flex flex-wrap gap-2">
          {solution.complexity.map((c) => (
            <span key={c} className="rounded-full bg-surface-2 px-2.5 py-0.5 font-mono text-xs">{c}</span>
          ))}
        </p>
      )}
      <ContentHtml html={html} />
    </section>
  )
}
