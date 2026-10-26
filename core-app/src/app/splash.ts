/* ============================================================
   Launch splash (markup + styles inline in index.html so it
   paints before any JS). Hidden as soon as the app shell mounts,
   and after 8 s at the latest if that script never runs. The page
   underneath shows its own loading and error states.
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
