import type { Catalog } from '../schema'
import { SubjectCard } from './SubjectCard'

export function CategorySections({ catalog, headingLevel = 'h2' }: { catalog: Catalog; headingLevel?: 'h2' | 'h3' }) {
  const H = headingLevel
  return (
    <div className="space-y-10">
      {catalog.categories.map((category) => {
        const subjects = catalog.subjects.filter((s) => s.category === category.id)
        if (!subjects.length) return null
        return (
          <section key={category.id} aria-labelledby={`cat-${category.id}`}>
            <H id={`cat-${category.id}`} className="mb-4 text-lg font-semibold tracking-tight">{category.title}</H>
            <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {subjects.map((s) => (
                <li key={s.id}><SubjectCard subject={s} /></li>
              ))}
            </ul>
          </section>
        )
      })}
    </div>
  )
}
