/* Thin progress bar at the top while a page's code is loading (Suspense fallback). */

export function RouteProgress() {
  return <div className="route-progress" role="progressbar" aria-label="Loading page" />
}
