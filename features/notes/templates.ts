import { positionsBetween } from '@/lib/contracts/validation'
import { newCardId, type CardType } from './model/doc'

/**
 * Ready-made starts for a note: the cards a student usually wants for a lecture, a revision sheet, a set of flashcards
 * or a practice quiz. Each card gets a new id and position, exactly as if the student had added it.
 */

const p = (text = '') => (text ? { type: 'paragraph', content: [{ type: 'text', text }] } : { type: 'paragraph' })
const doc = (...texts: string[]) => ({ type: 'doc', content: texts.length ? texts.map(p) : [p()] })
const inline = (text: string) => (text ? [{ type: 'text', text }] : [])

export type TemplateKey = 'lecture' | 'revision' | 'flashcards' | 'quiz'

const TEMPLATES: Record<TemplateKey, { type: CardType; content: unknown }[]> = {
  lecture: [
    { type: 'heading', content: { level: 2, content: inline('Key ideas') } },
    { type: 'text', content: { doc: doc() } },
    { type: 'heading', content: { level: 2, content: inline('Examples') } },
    { type: 'text', content: { doc: doc() } },
    { type: 'callout', content: { variant: 'tip', title: 'Remember', doc: doc() } },
    { type: 'question', content: { prompt: doc(), answer: doc() } },
  ],
  revision: [
    { type: 'heading', content: { level: 2, content: inline('Summary') } },
    { type: 'text', content: { doc: doc() } },
    { type: 'checklist', content: { items: [{ id: 'a', checked: false, content: [] }, { id: 'b', checked: false, content: [] }, { id: 'c', checked: false, content: [] }] } },
    { type: 'heading', content: { level: 2, content: inline('Test yourself') } },
    { type: 'question', content: { prompt: doc(), answer: doc() } },
    { type: 'question', content: { prompt: doc(), answer: doc() } },
  ],
  flashcards: [
    { type: 'flashcard', content: { front: doc(), back: doc() } },
    { type: 'flashcard', content: { front: doc(), back: doc() } },
    { type: 'flashcard', content: { front: doc(), back: doc() } },
  ],
  quiz: [
    { type: 'quiz', content: { question: doc(), choices: [{ id: 'a', content: [] }, { id: 'b', content: [] }, { id: 'c', content: [] }], correct: ['a'], multiple: false } },
    { type: 'quiz', content: { question: doc(), choices: [{ id: 'a', content: [] }, { id: 'b', content: [] }, { id: 'c', content: [] }], correct: ['a'], multiple: false } },
  ],
}

export const TEMPLATE_KEYS = Object.keys(TEMPLATES) as TemplateKey[]

/** The cards of a template, ready for createNote. */
export function templateCards(key: TemplateKey) {
  const cards = TEMPLATES[key]
  const positions = positionsBetween(null, null, cards.length)
  return cards.map((c, i) => ({ id: newCardId(), type: c.type, position: positions[i]!, content: c.content }))
}
