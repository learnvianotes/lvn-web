/* About / documentation page. Wording comes from the project owner. */

import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { APP_NAME } from '@/config'
import { useCatalog } from '@/content/hooks'

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
        <p><strong>Nothing is required.</strong> No sign-up, no login, no setup. Just learn.</p>
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
