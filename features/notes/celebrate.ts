'use client'

/**
 * A short burst of confetti in the desk colours (ink, highlighter, teal, moss, clay), for moments worth it (first publish). Nothing when the person asked
 * for reduced motion; the canvas removes itself.
 */
export function celebrate(origin?: { x: number; y: number }): void {
  if (typeof window === 'undefined' || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  const canvas = document.createElement('canvas')
  const dpr = window.devicePixelRatio || 1
  Object.assign(canvas.style, { position: 'fixed', inset: '0', width: '100vw', height: '100vh', pointerEvents: 'none', zIndex: '100' })
  canvas.width = window.innerWidth * dpr
  canvas.height = window.innerHeight * dpr
  canvas.setAttribute('aria-hidden', 'true')
  document.body.appendChild(canvas)
  const ctx = canvas.getContext('2d')!
  ctx.scale(dpr, dpr)
  const colours = ['#1e40af', '#f2c230', '#0c5c66', '#3d6b2c', '#9a4a2b']
  const x0 = origin?.x ?? window.innerWidth / 2
  const y0 = origin?.y ?? window.innerHeight / 3
  const parts = Array.from({ length: 90 }, () => {
    const angle = Math.random() * Math.PI * 2
    const speed = 4 + Math.random() * 7
    return { x: x0, y: y0, vx: Math.cos(angle) * speed, vy: Math.sin(angle) * speed - 4, size: 4 + Math.random() * 5, rot: Math.random() * Math.PI, spin: (Math.random() - 0.5) * 0.3, colour: colours[Math.floor(Math.random() * colours.length)]! }
  })
  const start = performance.now()
  const frame = (now: number) => {
    const t = now - start
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight)
    for (const p of parts) {
      p.vy += 0.25
      p.vx *= 0.99
      p.x += p.vx
      p.y += p.vy
      p.rot += p.spin
      ctx.save()
      ctx.globalAlpha = Math.max(0, 1 - t / 1400)
      ctx.translate(p.x, p.y)
      ctx.rotate(p.rot)
      ctx.fillStyle = p.colour
      ctx.fillRect(-p.size / 2, -p.size / 4, p.size, p.size / 2)
      ctx.restore()
    }
    if (t < 1400) requestAnimationFrame(frame)
    else canvas.remove()
  }
  requestAnimationFrame(frame)
}
