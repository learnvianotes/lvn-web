'use client'

import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { Button } from '@/components/ui/button'
import { ViewerDocument } from '@/graphql/generated/graphql'
import { dismissWalkthrough, shouldAutoShowWalkthrough, tourKeyAction, WALKTHROUGH_EVENT } from '@/lib/walkthrough'

const STEPS = [
  { id: 'notes', targets: ['nav', 'menu'] },
  { id: 'search', targets: ['search'] },
  { id: 'together', targets: ['nav', 'menu'] },
  { id: 'account', targets: ['account'] },
  { id: 'guide', targets: [] },
] as const

type StepId = (typeof STEPS)[number]['id']

function focusable(root: HTMLElement): HTMLElement[] {
  return [...root.querySelectorAll<HTMLElement>('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])')].filter((el) => !el.hasAttribute('disabled') && el.getAttribute('aria-hidden') !== 'true')
}

/** The first on-screen element marked for this step, clipped to the viewport. */
function targetBox(names: readonly string[]): DOMRect | null {
  for (const name of names) {
    for (const el of document.querySelectorAll<HTMLElement>(`[data-tour="${name}"]`)) {
      const r = el.getBoundingClientRect()
      const x = Math.max(0, r.left)
      const y = Math.max(0, r.top)
      const right = Math.min(window.innerWidth, r.right)
      const bottom = Math.min(window.innerHeight, r.bottom)
      if (right - x < 8 || bottom - y < 8) continue
      const pad = 6
      const left = Math.max(4, x - pad)
      const top = Math.max(4, y - pad)
      const holeRight = Math.min(window.innerWidth - 4, right + pad)
      const holeBottom = Math.min(window.innerHeight - 4, bottom + pad)
      return new DOMRect(left, top, holeRight - left, holeBottom - top)
    }
  }
  return null
}

function place(hole: DOMRect | null, panelWidth: number, panelHeight: number): { top: number; left: number } {
  const margin = 12
  const gap = 12
  const vw = window.innerWidth
  const vh = window.innerHeight
  if (!hole) return { top: Math.max(margin, (vh - panelHeight) / 2), left: Math.max(margin, (vw - panelWidth) / 2) }
  if (hole.height > vh * 0.45 && hole.left < 80 && hole.right + gap + panelWidth <= vw - margin) {
    return { top: Math.max(margin, Math.min(80, vh - margin - panelHeight)), left: hole.right + gap }
  }
  let top = hole.bottom + gap
  if (top + panelHeight > vh - margin) {
    const above = hole.top - gap - panelHeight
    top = above >= margin ? above : Math.max(margin, vh - margin - panelHeight)
  }
  let left = hole.left
  if (left + panelWidth > vw - margin) left = vw - margin - panelWidth
  if (left < margin) left = margin
  return { top, left }
}

/**
 * A short tour of the signed-in shell, shown once after a profile is created and again from the guide.
 * Tab stays in the dialog, arrows move steps, Escape skips. The spotlight does not animate when reduced motion is on.
 */
export function Walkthrough() {
  const t = useTranslations('guide.tour')
  const viewerId = useQuery(ViewerDocument).data?.viewer?.id
  const params = useSearchParams()
  const pathname = usePathname()
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const [step, setStep] = useState(0)
  const [box, setBox] = useState<{ top: number; left: number; hole: { x: number; y: number; w: number; h: number } | null } | null>(null)
  const dialogRef = useRef<HTMLDivElement>(null)
  const titleRef = useRef<HTMLHeadingElement>(null)
  const previousFocus = useRef<HTMLElement | null>(null)
  const maskId = useId().replace(/:/g, '')
  const titleId = useId()
  const bodyId = useId()

  const close = useCallback(() => {
    if (viewerId) dismissWalkthrough(viewerId)
    setOpen(false)
  }, [viewerId])

  useEffect(() => {
    if (viewerId && shouldAutoShowWalkthrough(viewerId)) {
      setStep(0)
      setOpen(true)
    }
  }, [viewerId])

  useEffect(() => {
    const onReplay = () => {
      setStep(0)
      setOpen(true)
    }
    window.addEventListener(WALKTHROUGH_EVENT, onReplay)
    return () => window.removeEventListener(WALKTHROUGH_EVENT, onReplay)
  }, [])

  useEffect(() => {
    if (params.get('tour') !== '1') return
    setStep(0)
    setOpen(true)
    const next = new URLSearchParams(params.toString())
    next.delete('tour')
    const search = next.size ? `?${next.toString()}` : ''
    router.replace(`${pathname}${search}`, { scroll: false })
  }, [params, pathname, router])

  useEffect(() => {
    if (!open) return
    previousFocus.current = document.activeElement instanceof HTMLElement ? document.activeElement : null
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = previousOverflow
      previousFocus.current?.focus()
    }
  }, [open])

  useEffect(() => {
    if (!open) return
    titleRef.current?.focus()
  }, [open, step])

  useLayoutEffect(() => {
    if (!open) return
    const measure = () => {
      const current = STEPS[step]!
      const hole = targetBox(current.targets)
      const panel = dialogRef.current
      const width = panel?.offsetWidth ?? Math.min(360, window.innerWidth - 24)
      const height = panel?.offsetHeight ?? 220
      const pos = place(hole, width, height)
      setBox({ top: pos.top, left: pos.left, hole: hole ? { x: hole.x, y: hole.y, w: hole.width, h: hole.height } : null })
    }
    measure()
    window.addEventListener('resize', measure)
    window.addEventListener('scroll', measure, true)
    return () => {
      window.removeEventListener('resize', measure)
      window.removeEventListener('scroll', measure, true)
    }
  }, [open, step])

  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent) => {
      const action = tourKeyAction(event.key, event.shiftKey)
      if (!action) return
      const root = dialogRef.current
      if (action === 'skip') {
        event.preventDefault()
        close()
        return
      }
      if (action === 'next') {
        event.preventDefault()
        setStep((n) => (n >= STEPS.length - 1 ? n : n + 1))
        if (step >= STEPS.length - 1) close()
        return
      }
      if (action === 'back') {
        event.preventDefault()
        setStep((n) => Math.max(0, n - 1))
        return
      }
      if (!root) return
      const items = focusable(root)
      if (!items.length) return
      const first = items[0]!
      const last = items[items.length - 1]!
      const active = document.activeElement
      const inside = active instanceof Node && root.contains(active)
      if (action === 'tab-prev' && (active === first || !inside)) {
        event.preventDefault()
        last.focus()
      } else if (action === 'tab-next' && (active === last || !inside)) {
        event.preventDefault()
        first.focus()
      }
    }
    window.addEventListener('keydown', onKey, true)
    return () => window.removeEventListener('keydown', onKey, true)
  }, [open, step, close])

  if (!open || typeof document === 'undefined') return null

  const current = STEPS[step]!
  const last = step === STEPS.length - 1
  const menu = (current.targets as readonly string[]).includes('menu') && !targetBox(['nav'])
  const bodyKey = menu && (current.id === 'notes' || current.id === 'together') ? (`${current.id}BodyMenu` as const) : (`${current.id}Body` as const)

  return createPortal(
    <div className="fixed inset-0 z-[80]">
      <svg className="absolute inset-0 h-full w-full" aria-hidden>
        <defs>
          <mask id={maskId}>
            <rect width="100%" height="100%" fill="white" />
            {box?.hole ? <rect x={box.hole.x} y={box.hole.y} width={box.hole.w} height={box.hole.h} rx="12" fill="black" /> : null}
          </mask>
        </defs>
        <rect width="100%" height="100%" fill="rgba(2,6,23,0.62)" mask={`url(#${maskId})`} />
      </svg>
      {box?.hole ? (
        <div
          aria-hidden
          className="pointer-events-none absolute rounded-xl ring-2 ring-accent motion-reduce:transition-none motion-safe:transition-all motion-safe:duration-200"
          style={{ top: box.hole.y, left: box.hole.x, width: box.hole.w, height: box.hole.h }}
        />
      ) : null}
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={bodyId}
        className="absolute rounded-2xl border border-border bg-bg p-4 text-fg shadow-2xl outline-none motion-reduce:transition-none motion-safe:transition-[top,left] motion-safe:duration-200"
        style={{ top: box?.top ?? 0, left: box?.left ?? 12, width: 'min(22.5rem,calc(100vw-1.5rem))', visibility: box ? 'visible' : 'hidden' }}
      >
        <p className="text-xs font-medium text-muted">{t('progress', { step: step + 1, total: STEPS.length })}</p>
        <h2 id={titleId} ref={titleRef} tabIndex={-1} className="mt-1 text-lg font-bold tracking-tight outline-none">
          {t(`${current.id}Title` as `${StepId}Title`)}
        </h2>
        <p id={bodyId} className="mt-2 text-sm leading-6 text-muted">
          {t(bodyKey)}
        </p>
        {current.id === 'guide' ? (
          <p className="mt-3">
            <Link href="/guide" className="text-sm font-medium text-accent hover:underline" onClick={() => close()}>
              {t('openGuide')}
            </Link>
          </p>
        ) : null}
        <p className="mt-2 text-xs text-muted">{t('keys')}</p>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-2">
          <Button type="button" variant="ghost" onClick={() => close()}>
            {t('skip')}
          </Button>
          <div className="flex gap-2">
            {step > 0 ? (
              <Button type="button" variant="secondary" onClick={() => setStep((n) => n - 1)}>
                {t('back')}
              </Button>
            ) : null}
            <Button type="button" onClick={() => (last ? close() : setStep((n) => n + 1))}>
              {last ? t('done') : t('next')}
            </Button>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  )
}
