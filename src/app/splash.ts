/* ============================================================
   Launch splash (markup + styles inline in index.html so it
   paints before any JS). Hidden as soon as the first content is
   ready — there's no minimum display time — and after 8 s at the
   latest, so it can never block the app.
   ============================================================ */

let done = false

export function hideSplash() {
  if (done) return
  done = true
  const el = document.getElementById('splash')
  if (!el) return
  el.classList.add('is-done')
  window.setTimeout(() => el.remove(), 250)
}

window.setTimeout(hideSplash, 8000)
