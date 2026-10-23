# LearnViaNotes web UI audit

Audited against the Next.js app (`app/`, `components/`, `features/`) and the kept `/core` reader (`core-app/`). Severity is what a learner hits, not how large the diff is.

Palette rule already in the product (ADR-0094): no purple, violet, indigo, or lavender. This audit also treats pink gradients, sparkle marks, and rainbow feature tiles as off-brief for a study tool. No dummy testimonials or invented statistics were added. Counts on `/core` are the real catalogue.

## Critical

1. **Signed-in routes could sit on a blank line while the API hung.** `RequireSession` rendered a single ellipsis for every status other than `signed-in`. `refreshSession` had no deadline, so a stalled gateway left `/home` and the rest of the app looking empty. The `/core` splash covered the whole viewport until the catalogue loaded, and for 8 seconds even when that request never finished (`core-app/src/app/splash.ts`).
2. **An API failure on a subject or topic was shown as a 404.** `getSubject` throws when the request fails. The pages caught that and called `notFound()`, so an outage and a missing slug looked the same. Real missing slugs must stay 404s (the e2e suite checks them).

## High

3. **The public wordmark always went to `/`.** `SiteHeader` linked the logo to `/` even after this tab knew the person was signed in (the landing page keeps that header). The app sidebar already went to `/home`.
4. **A resource page was an empty box while it loaded.** `ResourceView` returned a blank `div` for loading and for an unknown session. Ask AI's answer list returned `null` while the first query was in flight.
5. **No route error screen.** There was no `error.tsx`. A thrown server render fell through to the framework fallback instead of "This could not be loaded" and Try again.
6. **Phone public header hid the way around the site.** Features, Subjects, Community, and Get Started were `display: none` below 768px, and Get Started also below 640px. A 390px-wide landing showed the logo tile, a subjects icon, Sign in, and the theme control, with a large empty gap where the wordmark was hidden (`min-width: 400px`). There was no menu to replace those links. The phone control is named Browse, so it does not collide with the signed-in Menu drawer.
7. **The app drawer did not move focus or lock scroll.** It was labelled as a dialog and closed on Escape, but focus stayed on the page behind it and the page could still scroll.

## Medium

8. **The marketing surface read as a generic gradient template.** Full-bleed blue wash, a pink blob, a sparkle eyebrow (`✦`), rainbow feature tiles (orange, pink, emerald), and an illustration with pink cards and "Explain simply ✨". The same pink (`#DB2777`, `#F9A8D4`, `#FBCFE8`) showed up on recommendation art, community cards, and the `/core` AI category. Code titles in the reader used purple (`#8250df` / `#d2a8ff`).
9. **Loading states were a short muted sentence**, so the page jumped when the real content arrived. The hero entrance also translated the heading down by 12px (layout shift).
10. **Muted text `#5b6475` was tight** on tinted surfaces and for 12px type. Icon buttons were 36px. The dialog close control was a raw "✕" with a hardcoded label and a small hit area.
11. **Two palettes.** The product and `/core` did not share ink, paper, or brand blue, so a person moving from notes to the reader (when `/core` is on) changed colour.
12. **The in-app 404 was an unframed page** with no header, and "Go home" always went to `/`.
13. **Group picture in the editor had an empty `alt`** even though the same screen already has "The picture of {name}" for the public view. Resource covers stay empty on purpose: the title is in the same link.

## Low

14. **Search hint always says "Ctrl K"**, including on a phone where the hint is hidden and on a Mac where the shortcut is different. The button's accessible name is still "Search".
15. **Theme icon is a moon until hydration**, so the first paint does not flash the wrong theme colour (the theme itself is set before paint) but the glyph can swap once.
16. **Page titles use a mix of `text-2xl` and `text-3xl`.** The hierarchy is readable; it is not one scale yet. New work should use the type ramp in `tokens.json`.
17. **Footer copy** ("Your own notes, groups and classrooms are on the way.") is behind the product. Left as written; it is product copy, not a layout bug.

## Needs backend

Nothing in this revamp needs a backend or contract change.

- Session refresh already returns a session or it does not. A transport failure is handled in the client (timeout, then an on-page error). A real "no cookie" answer still signs the person out.
- Subject pages tell "missing" from "request failed" with the existing GraphQL result (`null` versus a thrown HTTP or timeout). No new field.
- Serving HTTP 503 for an outage, instead of a 200 page that says the catalogue could not load, would be a hosting concern. It is not required for the learner to see an honest error, and it was not added.

## Deferred

- Note editor, PDF reader marks, and study-card chrome keep their behaviour. Reader colours now use the same ink and brand; highlight colours (including the API value `PURPLE`, drawn orange per ADR-0094) are unchanged.
- Beta allowlist sign-in, the admin allowlist screen, and admin plans/limits are not in this tree. Sign-in logic and admin navigation structure were not rewritten. Shared button, field, alert, and token changes apply if those screens use them.
- Per-page empty dashes were not all replaced with one component. New loading uses the shared skeleton. Empty copy already on each screen stays.
- Shortcut labelling for Mac, and a single page-title component on every route.
