import type { NoteTab } from './NoteTabs'

/** What feeds each study tab: the note's own cards, its public aids (ADR-0061) and the viewer's AI results (ADR-0059). */
export const TAB_CARDS: Record<'flashcards' | 'quiz', readonly string[]> = { flashcards: ['flashcard'], quiz: ['quiz', 'question'] }
export const TAB_TASKS: Record<'summary' | 'flashcards' | 'quiz', readonly string[]> = {
  summary: ['SUMMARIZE', 'KEY_CONCEPTS', 'PRACTICE_QUESTIONS', 'REVISION_SHEET', 'EXPLAIN_SIMPLY'],
  flashcards: ['FLASHCARDS'],
  quiz: ['QUIZ'],
}

export interface TabInputs {
  /** The viewer may edit the note (they can add a card) */
  canEdit: boolean
  /** The viewer reads it (not its owner or an editor) */
  reader: boolean
  /** It has a published version (its discussion is open) */
  published: boolean
  /** AI answers now (unknown counts as off) */
  ai: boolean
  /** Card types in the note */
  cardTypes: readonly string[]
  /** Tasks of its public aids and of the viewer's results */
  tasks: readonly string[]
}

/**
 * The tabs a note offers (lvn-backend ADR-0076): a tab is shown only when it has something, or a way to make
 * something — never an empty tab with nothing to do.
 */
export function offeredTabs(x: TabInputs): NoteTab[] {
  const has = (tab: 'summary' | 'flashcards' | 'quiz') => x.tasks.some((task) => TAB_TASKS[tab].includes(task)) || (tab !== 'summary' && x.cardTypes.some((type) => TAB_CARDS[tab].includes(type)))
  const tabs: NoteTab[] = ['content']
  if (has('summary') || x.ai) tabs.push('summary')
  if (has('flashcards') || x.ai || x.canEdit) tabs.push('flashcards')
  if (has('quiz') || x.ai || x.canEdit) tabs.push('quiz')
  if (x.reader || x.published) tabs.push('discussions')
  return tabs
}
