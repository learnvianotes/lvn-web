#!/usr/bin/env node
/**
 * Copies what pdf.js loads at run time — its worker, character maps, standard fonts, image decoders and colour
 * profiles — from node_modules/pdfjs-dist into public/pdfjs/<version>/, where the PDF reader (lvn-backend ADR-0040)
 * finds them. Run by `pnpm dev` and `pnpm build`; the output is not committed.
 */
import { cpSync, existsSync, readFileSync, rmSync } from 'node:fs'
import path from 'node:path'

const root = path.resolve(import.meta.dirname, '..')
const source = path.join(root, 'node_modules/pdfjs-dist')
const { version } = JSON.parse(readFileSync(path.join(source, 'package.json'), 'utf8'))
const target = path.join(root, 'public/pdfjs', version)

if (!existsSync(path.join(target, 'pdf.worker.min.mjs'))) {
  // One version at a time: older copies go.
  rmSync(path.join(root, 'public/pdfjs'), { recursive: true, force: true })
  cpSync(path.join(source, 'build/pdf.worker.min.mjs'), path.join(target, 'pdf.worker.min.mjs'))
  for (const dir of ['cmaps', 'standard_fonts', 'wasm', 'iccs']) cpSync(path.join(source, dir), path.join(target, dir), { recursive: true })
  console.log(`pdf.js ${version} assets → public/pdfjs/${version}`)
}
