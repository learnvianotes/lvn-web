/* About / documentation page. Wording comes from the project owner. */

import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { APP_NAME, LEGAL } from '@/config'
import { useCatalog } from '@/features/catalog/hooks'

export function AboutPage() {
  const { data } = useCatalog()
  return (
    <div className="page page-narrow">
      <Link to="/" className="back-link"><ArrowLeft size={14} aria-hidden /> All subjects</Link>
      <article className="prose about">
        <h1 className="page-title">About {APP_NAME}</h1>
        <p className="lead">
          {APP_NAME} is an interview sheet — a quick sheet for understanding and a quick learning platform.
          It is purely focused on study and the important points to understand.
        </p>
        <h3>What do you need?</h3>
        <p><strong>Nothing is required.</strong> No sign-up, no setup. Just learn.</p>
        <p>
          Signing in is optional: it keeps your study streak, history (what you studied, when and for how long),
          review queue and personal notes in sync across your devices.
        </p>
        <h3>Study tools</h3>
        <ul>
          <li><strong>Listen</strong> — any topic or problem can be read aloud, with the current paragraph highlighted.</li>
          <li><strong>Smart study kit</strong> — quick notes, side headings and key points to remember, generated from every topic.</li>
          <li><strong>Focus timer</strong> — timed focus sessions that count toward your streak.</li>
          <li><strong>Review queue</strong> — completed topics come back after 1, 3, 7, 14 and 30 days so they stick.</li>
        </ul>
        <h3>Who runs it</h3>
        <p>
          {APP_NAME} is run by {LEGAL.operator || 'its founders'}. Read how we handle your data in the{' '}
          <Link to="/privacy">Privacy Policy</Link>, the rules in the <Link to="/terms">Terms of Use</Link>, and how
          to raise a complaint on the <Link to="/grievance">Grievance Redressal</Link> page.
        </p>
        {data && (
          <>
            <h3>Subjects</h3>
            <ul>
              {data.subjects.map((s) => (
                <li key={s.id}><Link to={`/${s.id}`}>{s.title}</Link></li>
              ))}
            </ul>
          </>
        )}
      </article>
    </div>
  )
}
