/* ============================================================
   SUBJECT ICONS
   Maps subject IDs to Lucide icon components.
   Tree-shaking: only imports the icons that are actually used.
   ============================================================ */

import type { LucideIcon } from 'lucide-react'
import {
  ListChecks,
  Network,
  Cpu,
  Database,
  Layers,
  ShieldCheck,
  Workflow,
  GitMerge,
  Plug,
  Code2,
  Braces,
  BrainCircuit,
  Sparkles,
  BookOpen,
} from 'lucide-react'

export const SUBJECT_ICON_MAP: Record<string, LucideIcon> = {
  'sheet-150':        ListChecks,
  'computer-networks': Network,
  'operating-systems': Cpu,
  'dbms':             Database,
  'oops':             Layers,
  'cryptography':     ShieldCheck,
  'system-design':    Workflow,
  'git-github':       GitMerge,
  'api-design':       Plug,
  'dsa-basics':       Code2,
  'dsa-advanced':     Braces,
  'ml-ai':            BrainCircuit,
  'genai-fluency':    Sparkles,
}

/** Get the icon component for a subject. Falls back to BookOpen. */
export function getSubjectIcon(subjectId: string): LucideIcon {
  return SUBJECT_ICON_MAP[subjectId] ?? BookOpen
}
