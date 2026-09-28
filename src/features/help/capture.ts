/* ============================================================
   Feedback context capture — what the reader is looking at when
   they open the Help Center, so a report points at the exact spot.
   ============================================================ */

import { domToCanvas } from 'modern-screenshot'

export interface CapturedContext {
  page: string
  pageTitle: string
  /** e.g. "LC 104 · Maximum Depth of Binary Tree › Optimized code" */
  section: string
  selection: string
  device: string
  theme: string
  /** element the screenshot is taken of */
  target: HTMLElement | null
}

/** Must run *before* the Help Center opens (it reads the screen center). */
export function captureContext(): CapturedContext {
  const main = document.querySelector('.ws-main')?.getBoundingClientRect()
  const x = main ? main.left + main.width / 2 : window.innerWidth / 2
  const hit = document.elementFromPoint(x, window.innerHeight * 0.45) as HTMLElement | null
  const target = hit?.closest<HTMLElement>('.problem-card, .block, .pc-box, .card-grid, .ws-content') ?? null

  const parts: string[] = []
  const card = hit?.closest('.problem-card')
  if (card) {
    parts.push(`${card.querySelector('.pc-eyebrow')?.textContent?.split('·').pop()?.trim() ?? card.id} · ${card.querySelector('h2')?.textContent ?? ''}`)
    const box = hit?.closest('.pc-box')?.querySelector('.pc-box-title')?.textContent
    if (box) parts.push(box)
  } else {
    const heading = hit?.closest('.block')?.querySelector('h3')?.textContent
    const title = document.querySelector('.topic-head .page-title')?.textContent
    if (title) parts.push(title)
    if (heading) parts.push(heading)
  }

  return {
    page: location.pathname + location.hash,
    pageTitle: document.title,
    section: parts.join(' › '),
    selection: window.getSelection()?.toString().trim().slice(0, 500) ?? '',
    device: `${window.innerWidth}×${window.innerHeight} · ${navigator.userAgent.match(/(iPhone|iPad|Android|Mac OS X|Windows NT|Linux)/)?.[0] ?? 'Unknown'}`,
    theme: document.documentElement.getAttribute('data-theme') ?? 'light',
    target,
  }
}

/** JPEG data URL of the part of `target` that is currently visible. */
export async function screenshotVisible(target: HTMLElement): Promise<string> {
  const rect = target.getBoundingClientRect()
  const headerBottom = document.querySelector('.header')?.getBoundingClientRect().bottom ?? 0
  const top = Math.max(0, headerBottom - rect.top)
  const bottom = Math.min(rect.height, window.innerHeight - rect.top)
  const height = Math.max(1, bottom - top)

  const full = await domToCanvas(target, {
    scale: 1,
    backgroundColor: getComputedStyle(document.body).backgroundColor,
    // Skip fetching web fonts: much faster, and the text stays readable.
    font: false,
  })
  const ratio = full.width / rect.width
  const out = document.createElement('canvas')
  const maxWidth = 1200
  const scale = Math.min(1, maxWidth / (rect.width * ratio))
  out.width = Math.round(rect.width * ratio * scale)
  out.height = Math.round(height * ratio * scale)
  out.getContext('2d')!.drawImage(full, 0, top * ratio, rect.width * ratio, height * ratio, 0, 0, out.width, out.height)
  return out.toDataURL('image/jpeg', 0.72)
}
