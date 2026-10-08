import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

const tones = {
  info: 'border-accent/30 bg-accent-soft text-fg',
  success: 'border-green-600/30 bg-green-50 text-green-900 dark:bg-green-950/40 dark:text-green-200',
  error: 'border-red-600/30 bg-red-50 text-red-900 dark:bg-red-950/40 dark:text-red-200',
}

export function Alert({ tone = 'info', children, className }: { tone?: keyof typeof tones; children: ReactNode; className?: string }) {
  return (
    <div role={tone === 'error' ? 'alert' : 'status'} className={cn('rounded-xl border px-4 py-3 text-sm', tones[tone], className)}>
      {children}
    </div>
  )
}
