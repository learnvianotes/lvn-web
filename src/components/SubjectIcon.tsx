import {
  BookOpen, Braces, Brain, Code2, Cpu, Database, GitMerge, Layers, ListChecks, Network, Plug,
  ShieldCheck, Sparkles, Workflow, type LucideIcon, type LucideProps,
} from 'lucide-react'

/** Icon names used by `Subject.icon` in the catalog. */
const ICONS: Record<string, LucideIcon> = {
  code: Code2, braces: Braces, 'list-checks': ListChecks, layers: Layers, network: Network,
  database: Database, cpu: Cpu, 'shield-check': ShieldCheck, workflow: Workflow,
  'git-merge': GitMerge, plug: Plug, sparkles: Sparkles, brain: Brain,
}

export function SubjectIcon({ name, ...props }: { name: string } & LucideProps) {
  const Icon = ICONS[name] ?? BookOpen
  return <Icon aria-hidden {...props} />
}
