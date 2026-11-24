#!/usr/bin/env node
/**
 * Renders the LearnViaNotes logo (branding/logo-paths.json) into public/icons: SVG favicon, PNG favicons, the
 * Apple touch icon, PWA icons and the maskable PWA icon. Uses sharp (installed with Next.js).
 *
 *   node branding/render-icons.mjs
 */
import { createRequire } from 'node:module'
import { readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'

const root = path.resolve(import.meta.dirname, '..')
const sharp = createRequire(createRequire(import.meta.url).resolve('next/package.json'))('sharp')
const icons = path.join(root, 'public/icons')
const p = JSON.parse(readFileSync(path.join(root, 'branding/logo-paths.json'), 'utf8'))
const c = p.colors

const mark = p.letters.map((d) => `<path d="${d}" fill="${c.letter}"/>`).join('') + `<path d="${p.marker}" fill="${c.marker}"/>`
const tile = (rx) => `<rect width="1024" height="1024" rx="${rx}" fill="${c.tile}"/>`
const svg = (body) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">${body}</svg>\n`

// Rounded tile for favicons and the header; full-bleed for Apple (it rounds the corners) and maskable PWA icons
// (the mark already sits inside the maskable safe zone, the central 80 %).
const rounded = svg(tile(p.tileRadius) + mark)
const square = svg(tile(0) + mark)
writeFileSync(path.join(icons, 'logo.svg'), rounded)

const render = (source, target, size) => sharp(Buffer.from(source), { density: 72 * (size / 1024) * 4 }).resize(size, size).png().toFile(path.join(icons, target))
await Promise.all([
  ...[16, 32, 48, 192, 512].map((size) => render(rounded, `icon-${size}.png`, size)),
  render(square, 'apple-touch-icon.png', 180),
  render(square, 'maskable-512.png', 512),
])
console.log('icons rendered into public/icons')
