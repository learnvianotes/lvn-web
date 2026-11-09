'use client'

import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { Button } from '@/components/ui/button'
import { ViewerDocument } from '@/graphql/generated/graphql'
import { dismissWalkthrough, setTourMenu, shouldAutoShowWalkthrough, tourKeyAction, WALKTHROUGH_EVENT } from '@/lib/walkthrough'

/** One spotlight per area. `drawer` opens the phone menu so the item can be seen. */
const STEPS = [
  { id: 'notes', target: 'notes', drawer: true },
  { id: 'search', target: 'explore', drawer: true },
  { id: 'groups', target: 'groups', drawer: true },
  { id: 'classes', target: 'classes', drawer: true },
  { id: 'guide', target: 'guide', drawer: true },
  { id: 'account', target: 'account', drawer: false },
  { id: 'done', target: null, drawer: false },
] as const

type StepId = (typeof STEPS)[number]['id']

const phoneQuery = '(max-width: 1023px)'

function focusable(root: HTMLElement): HTMLElement[] {
  return [...root.querySelectorAll<HTMLElement>('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])')].filter((el) => !el.hasAttribute('disabled') && el.getAttribute('aria-hidden') !== 'true')
}

/** The visible element for this step. Hidden copies (the desktop sidebar on a phone, or the reverse) are skipped. */
function targetElement(name: string | null): HTMLElement | null {
  if (!name) return null
  for (const el of document.querySelectorAll<HTMLElement>(`[data-tour="${name}"]`)) {
    const r = el.getBoundingClientRect()
    if (r.width >= 8 && r.height >= 8) return el
  }
  return null
}

function holeFor(el: HTMLElement): DOMRect {
  const r = el.getBoundingClientRect()
  const pad = 6
  const left = Math.max(4, r.left - pad)
  const top = Math.max(4, r.top - pad)
  const right = Math.min(window.innerWidth - 4, r.right + pad)
  const bottom = Math.min(window.innerHeight - 4, r.bottom + pad)
  return new DOMRect(left, top, Math.max(8, right - left), Math.max(8, bottom - top))
}

function place(hole: DOMRect | null, panelWidth: number, panelHeight: number): { top: number; left: number } {
  const margin = 12
  const gap = 12
  const vw = window.innerWidth
  const vh = window.innerHeight
  if (!hole) return { top: Math.max(margin, (vh - panelHeight) / 2), left: Math.max(margin, (vw - panelWidth) / 2) }
  // On a phone the drawer fills the left side. The card sits at the bottom, or at the top when the item is low in the list.
  if (window.matchMedia(phoneQuery).matches) {
    const bottom = Math.max(margin, vh - panelHeight - margin)
    return { top: hole.top > bottom - 8 ? margin : bottom, left: margin }
  }
  // A sidebar item gets the card in the page, beside that item, not over the middle of the content.
  if (hole.left < 280) {
    const left = Math.min(Math.max(hole.right + gap, 280), vw - margin - panelWidth)
    const top = Math.max(margin, Math.min(hole.top, vh - margin - panelHeight))
    return { top, left }
  }
  let top = hole.bottom + gap
  if (top + panelHeight > vh - margin) top = Math.max(margin, hole.top - gap - panelHeight)
  let left = hole.left
  if (left + panelWidth > vw - margin) left = vw - margin - panelWidth
  if (left < margin) left = margin
  return { top, left }
}

/**
 * A short tour of the signed-in shell. It runs once after the profile is created, and again from the guide.
 * On a phone it opens the navigation drawer and spotlights each item. Skip, Back and Next are on every step.
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
    setTourMenu(false)
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
    if (!open) {
      setTourMenu(false)
      return
    }
    const current = STEPS[step]!
    const phone = window.matchMedia(phoneQuery).matches
    setTourMenu(phone && current.drawer)
  }, [open, step])

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
    let cancelled = false
    let frame = 0
    let tries = 0
    const measure = () => {
      if (cancelled) return
      const current = STEPS[step]!
      const phone = window.matchMedia(phoneQuery).matches
      const el = targetElement(current.target)
      // The phone drawer mounts a frame after the tour asks for it.
      if (phone && current.drawer && !el && tries < 20) {
        tries += 1
        frame = requestAnimationFrame(measure)
        return
      }
      if (el) el.scrollIntoView({ block: phone ? 'start' : 'center', inline: 'nearest', behavior: 'auto' })
      // Read the box on the next frame, after the sidebar or drawer has scrolled.
      frame = requestAnimationFrame(() => {
        if (cancelled) return
        const now = targetElement(current.target)
        const hole = now ? holeFor(now) : null
        const panel = dialogRef.current
        const width = panel?.offsetWidth ?? Math.min(360, window.innerWidth - 24)
        const height = panel?.offsetHeight ?? 280
        const pos = place(hole, width, height)
        setBox({ top: pos.top, left: pos.left, hole: hole ? { x: hole.x, y: hole.y, w: hole.width, h: hole.height } : null })
      })
    }
    frame = requestAnimationFrame(measure)
    window.addEventListener('resize', measure)
    return () => {
      cancelled = true
      cancelAnimationFrame(frame)
      window.removeEventListener('resize', measure)
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
        event.stopPropagation()
        close()
        return
      }
      if (action === 'next') {
        event.preventDefault()
        if (step >= STEPS.length - 1) close()
        else setStep((n) => n + 1)
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
      const lastItem = items[items.length - 1]!
      const active = document.activeElement
      const inside = active instanceof Node && root.contains(active)
      if (action === 'tab-prev' && (active === first || !inside)) {
        event.preventDefault()
        lastItem.focus()
      } else if (action === 'tab-next' && (active === lastItem || !inside)) {
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
  const bodyKey = `${current.id}Body` as `${StepId}Body`
  const titleKey = `${current.id}Title` as `${StepId}Title`

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
          className="pointer-events-none absolute rounded-xl ring-2 ring-accent motion-reduce:transition-none"
          style={{ top: box.hole.y, left: box.hole.x, width: box.hole.w, height: box.hole.h }}
        />
      ) : null}
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={bodyId}
        className="absolute rounded-2xl border border-border bg-bg p-4 text-fg shadow-2xl outline-none motion-reduce:transition-none"
        style={{ top: box?.top ?? 0, left: box?.left ?? 12, width: 'min(22.5rem,calc(100vw-1.5rem))', visibility: box ? 'visible' : 'hidden' }}
      >
        <p className="text-xs font-medium text-muted">{t('progress', { step: step + 1, total: STEPS.length })}</p>
        <h2 id={titleId} ref={titleRef} tabIndex={-1} className="mt-1 text-lg font-bold tracking-tight outline-none">
          {t(titleKey)}
        </h2>
        <p id={bodyId} className="mt-2 text-sm leading-6 text-muted">
          {t(bodyKey)}
        </p>
        {current.id === 'done' ? (
          <p className="mt-3">
            <Link href="/guide" className="text-sm font-medium text-accent hover:underline" onClick={() => close()}>
              {t('openGuide')}
            </Link>
          </p>
        ) : null}
        <p className="mt-2 text-xs text-muted">{t('keys')}</p>
        <div className="mt-4 flex flex-col gap-2">
          <div className="flex gap-2">
            <Button type="button" variant="secondary" className="min-w-0 flex-1" disabled={step === 0} onClick={() => setStep((n) => Math.max(0, n - 1))}>
              {t('back')}
            </Button>
            <Button type="button" className="min-w-0 flex-1" onClick={() => (last ? close() : setStep((n) => n + 1))}>
              {last ? t('done') : t('next')}
            </Button>
          </div>
          <Button type="button" variant="secondary" className="w-full border-2" onClick={() => close()}>
            {t('skip')}
          </Button>
        </div>
      </div>
    </div>,
    document.body,
  )
}
