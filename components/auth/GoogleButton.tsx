'use client'

import { useTranslations } from 'next-intl'
import { cn } from '@/lib/cn'
import { GoogleMark } from './GoogleMark'

/**
 * Google's own button styles (Sign in with Google branding guidelines): dark (#131314 / #8E918F / #E3E3E3) on light
 * surfaces, light (#FFFFFF / #747775 / #1F1F1F) on dark ones, with the unmodified G mark — never recoloured to our
 * brand. `auto` follows the site theme.
 */
const tones = {
  dark: 'border-[#8E918F] bg-[#131314] text-[#E3E3E3] hover:bg-[#2B2B2E]',
  light: 'border-[#747775] bg-white text-[#1F1F1F] hover:bg-[#F2F2F2]',
  auto: 'border-[#8E918F] bg-[#131314] text-[#E3E3E3] hover:bg-[#2B2B2E] dark:border-[#747775] dark:bg-white dark:text-[#1F1F1F] dark:hover:bg-[#F2F2F2]',
}

export function GoogleButton({ onClick, busy, disabled, tone = 'auto', className }: { onClick: () => void; busy?: boolean; disabled?: boolean; tone?: keyof typeof tones; className?: string }) {
  const t = useTranslations('auth.providers')
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled || busy}
      aria-busy={busy || undefined}
      className={cn(
        'inline-flex h-12 w-full items-center justify-center gap-3 rounded-full border px-6 text-[15px] font-semibold transition-[background-color,transform] active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-80',
        tones[tone],
        className,
      )}
    >
      {busy ? <span className="size-5 animate-spin rounded-full border-2 border-current border-t-transparent" aria-hidden /> : <GoogleMark />}
      {busy ? t('googleBusy') : t('google')}
    </button>
  )
}
