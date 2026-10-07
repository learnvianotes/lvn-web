#!/usr/bin/env node
/**
 * Renders the LearnViaNotes logo (branding/logo-paths.json) into public/icons: SVG favicon, PNG favicons, the
 * Apple touch icon, PWA icons and the maskable PWA icon. Needs `rsvg-convert` (librsvg).
 *
 *   node branding/render-icons.mjs
 */
import { execFileSync } from 'node:child_process'
import { readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'

const root = path.resolve(import.meta.dirname, '..')
const icons = path.join(root, 'public/icons')
const p = JSON.parse(readFileSync(path.join(root, 'branding/logo-paths.json'), 'utf8'))
const c = p.colors

const defs = `<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${c.gradient[0]}"/><stop offset="0.55" stop-color="${c.gradient[1]}"/><stop offset="1" stop-color="${c.gradient[2]}"/></linearGradient><radialGradient id="glow" cx="0.22" cy="0.18" r="0.75"><stop offset="0" stop-color="#FFFFFF" stop-opacity="0.22"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient></defs>`
const mark =
  `<path d="${p.leftPage}" fill="${c.page}"/><path d="${p.rightPage}" fill="${c.pageShade}"/>` +
  p.lines.map((d) => `<path d="${d}" fill="none" stroke="${c.line}" stroke-width="18" stroke-linecap="round"/>`).join('') +
  `<path d="${p.check}" fill="none" stroke="${c.check}" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>` +
  `<path d="${p.spark}" fill="${c.spark}"/>`
const tile = (rx) => `<rect width="1024" height="1024" rx="${rx}" fill="url(#bg)"/><rect width="1024" height="1024" rx="${rx}" fill="url(#glow)"/>`
const svg = (body) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">${defs}${body}</svg>\n`

// Rounded tile for favicons and the header; full-bleed for Apple (it rounds the corners) and maskable PWA icons
// (the mark already sits inside the maskable safe zone, the central 80 %).
writeFileSync(path.join(icons, 'logo.svg'), svg(tile(p.tileRadius) + mark))
const square = path.join(root, 'branding/.logo-square.svg')
writeFileSync(square, svg(tile(0) + mark))

const render = (source, target, size) =>
  execFileSync('rsvg-convert', ['-w', String(size), '-h', String(size), source, '-o', path.join(icons, target)])
for (const size of [16, 32, 48, 192, 512]) render(path.join(icons, 'logo.svg'), `icon-${size}.png`, size)
render(square, 'apple-touch-icon.png', 180)
render(square, 'maskable-512.png', 512)
console.log('icons rendered into public/icons')
