/* ============================================================
   CONTENT PIPELINE — check hand-written solutions
   Usage: node scripts/content/check-code.mjs [problemId ...]
   Compiles C++ (clang++), parses Java, syntax-checks JS for every
   file in content-src/code/<problemId>/ and reports what is still
   missing per problem (compared to the Python in content-build).
   ============================================================ */

import fs from 'node:fs'
import path from 'node:path'
import { cppErrors, javaErrors, jsErrors, saveCache } from './validate-code.mjs'

const CODE_DIR = 'content-src/code'
const CHECK = { cpp: cppErrors, java: javaErrors, js: jsErrors }
const ids = process.argv.slice(2)
const problems = new Map()
for (const f of fs.readdirSync('content-build/problems')) {
  for (const p of JSON.parse(fs.readFileSync(`content-build/problems/${f}`, 'utf8')).problems) problems.set(p.id, p)
}

let failures = 0
for (const id of ids.length ? ids : [...problems.keys()]) {
  const p = problems.get(id)
  if (!p) { console.log(`${id}: unknown problem`); failures++; continue }
  const dir = path.join(CODE_DIR, id)
  const missing = []
  for (const kind of ['naive', 'optimal']) {
    if (!p[kind]) continue
    for (const lang of ['cpp', 'java', 'js']) {
      const file = path.join(dir, `${kind}.${lang}`)
      if (fs.existsSync(file)) {
        const err = CHECK[lang](fs.readFileSync(file, 'utf8'))
        if (err) { failures++; console.log(`FAIL ${file}\n  ${err.replace(/\n/g, '\n  ')}`) }
      } else if (!p[kind].code?.[lang]) missing.push(`${kind}.${lang}`)
    }
  }
  if (missing.length && ids.length) console.log(`${id}: missing ${missing.join(', ')}`)
}
saveCache()
console.log(failures ? `\n${failures} file(s) failed.` : '\nAll checked files are valid.')
process.exit(failures ? 1 : 0)
