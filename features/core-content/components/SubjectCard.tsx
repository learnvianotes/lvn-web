import {
  Binary,
  BookOpen,
  Bot,
  Braces,
  Brain,
  BrainCircuit,
  ChartColumn,
  Code,
  Coffee,
  Cpu,
  Database,
  FileCode,
  GitMerge,
  Layers,
  ListChecks,
  Network,
  Plug,
  ShieldCheck,
  TextQuote,
  SquareCode,
  Table,
  Terminal,
  Workflow,
  type LucideIcon,
} from 'lucide-react'
import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import type { Subject } from '../schema'

/**
 * Catalog icon names (Lucide's names) → icons, rendered on the server as SVG: no icon font for the home page to load.
 * An unknown name shows a book.
 */
const ICONS: Record<string, LucideIcon> = {
  binary: Binary,
  bot: Bot,
  braces: Braces,
  brain: Brain,
  'brain-circuit': BrainCircuit,
  chart: ChartColumn,
  code: Code,
  coffee: Coffee,
  cpu: Cpu,
  database: Database,
  'file-code': FileCode,
  'git-merge': GitMerge,
  layers: Layers,
  'list-checks': ListChecks,
  network: Network,
  plug: Plug,
  'shield-check': ShieldCheck,
  sparkles: TextQuote,
  'square-code': SquareCode,
  table: Table,
  terminal: Terminal,
  workflow: Workflow,
}
export const subjectIcon = (icon: string): LucideIcon => ICONS[icon] ?? BookOpen

export async function SubjectCard({ subject }: { subject: Subject }) {
  const t = await getTranslations('core')
  const Icon = subjectIcon(subject.icon)
  return (
    <Link
      href={`/core/${subject.id}`}
      className="group flex h-full flex-col gap-3 rounded-2xl border border-border bg-surface p-5 transition-colors hover:border-accent"
    >
      <span className="flex size-10 items-center justify-center rounded-xl bg-accent-soft text-accent">
        <Icon className="size-5" aria-hidden />
      </span>
      <span className="font-semibold group-hover:text-accent">{subject.title}</span>
      <span className="line-clamp-3 text-sm text-muted">{subject.description}</span>
      <span className="mt-auto text-xs font-medium text-muted">
        {subject.kind === 'problems' ? t('problems', { count: subject.itemCount }) : t('topics', { count: subject.itemCount })}
      </span>
    </Link>
  )
}
