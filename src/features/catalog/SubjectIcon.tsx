import {
  Bot, BookOpen, Braces, Brain, BrainCircuit, ChartNoAxesCombined, Code2, MessagesSquare, Cpu, Database, GitMerge, Grid3x3, Layers, Lightbulb, ListChecks, Network, Plug, Sigma,
  ShieldCheck, Sparkles, Terminal, Workflow, type LucideIcon, type LucideProps,
} from 'lucide-react'

/** Icon names used by `Subject.icon` in the catalog. */
const ICONS: Record<string, LucideIcon> = {
  code: Code2, braces: Braces, 'list-checks': ListChecks, layers: Layers, network: Network,
  database: Database, cpu: Cpu, 'shield-check': ShieldCheck, workflow: Workflow,
  'git-merge': GitMerge, plug: Plug, sparkles: Sparkles, brain: Brain,
  bot: Bot, 'brain-circuit': BrainCircuit, chart: ChartNoAxesCombined, message: MessagesSquare,
  sigma: Sigma, grid: Grid3x3, lightbulb: Lightbulb, terminal: Terminal,
}

export function SubjectIcon({ name, ...props }: { name: string } & LucideProps) {
  const Icon = ICONS[name] ?? BookOpen
  return <Icon aria-hidden {...props} />
}
