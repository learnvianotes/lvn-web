import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

const tones = {
  info: 'border-accent/30 bg-accent-soft text-fg',
  success: 'border-good/30 bg-good/10 text-fg',
  error: 'border-bad/30 bg-bad/10 text-fg',
}

export function Alert({ tone = 'info', children, className }: { tone?: keyof typeof tones; children: ReactNode; className?: string }) {
  return (
    <div role={tone === 'error' ? 'alert' : 'status'} className={cn('rounded-xl border px-4 py-3 text-sm', tones[tone], className)}>
      {children}
    </div>
  )
}
