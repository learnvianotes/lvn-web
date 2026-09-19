/* ============================================================
   Breadcrumbs — navigational context indicator
   ============================================================ */

import { Link } from 'react-router-dom'
import { ChevronRight } from 'lucide-react'

export interface BreadcrumbItem {
  label: string
  to?: string
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[]
}

export function Breadcrumbs({ items }: BreadcrumbsProps) {
  if (items.length === 0) return null

  return (
    <nav className="breadcrumbs" aria-label="Breadcrumb">
      <ol style={{ display: 'contents', listStyle: 'none' }}>
        {items.map((item, index) => {
          const isLast = index === items.length - 1
          return (
            <li key={`${item.label}-${index}`} className="breadcrumbs__item">
              {isLast || !item.to ? (
                <span
                  className="breadcrumbs__current"
                  aria-current={isLast ? 'page' : undefined}
                >
                  {item.label}
                </span>
              ) : (
                <Link to={item.to} className="breadcrumbs__link">
                  {item.label}
                </Link>
              )}
              {!isLast && (
                <span className="breadcrumbs__separator" aria-hidden="true">
                  <ChevronRight size={12} />
                </span>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
