import Link from 'next/link'

export function Breadcrumbs({ items }: { items: { href: string; label: string }[] }) {
  return (
    <nav aria-label="Breadcrumb">
      <ol className="flex flex-wrap items-center gap-1 text-sm text-muted">
        {items.map((item, i) => (
          <li key={item.href} className="flex items-center gap-1">
            {i > 0 && <i className="ti ti-chevron-right text-xs" aria-hidden />}
            <Link href={item.href} className="hover:text-fg">{i === 0 && <i className="ti ti-arrow-left mr-1" aria-hidden />}{item.label}</Link>
          </li>
        ))}
      </ol>
    </nav>
  )
}
