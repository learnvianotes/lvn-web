// The retired learnvianotes app registered a service worker at this URL with scope "/".
// Browsers fetch this file to update it; this version clears its caches, unregisters itself
// and reloads open tabs so they get the current site from the network.
self.addEventListener('install', () => self.skipWaiting())
self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    for (const key of await caches.keys()) await caches.delete(key)
    await self.registration.unregister()
    for (const client of await self.clients.matchAll({ type: 'window' })) client.navigate(client.url)
  })())
})
