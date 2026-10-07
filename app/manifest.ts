import type { MetadataRoute } from 'next'

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'LearnViaNotes',
    short_name: 'LearnViaNotes',
    start_url: '/',
    display: 'standalone',
    background_color: '#f7f7fb',
    theme_color: '#4f46e5',
    icons: [
      { src: '/icons/logo.svg', sizes: 'any', type: 'image/svg+xml' },
      { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
      { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
      { src: '/icons/maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
    ],
  }
}
