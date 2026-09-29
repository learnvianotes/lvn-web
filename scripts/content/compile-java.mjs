/* ============================================================
   CONTENT PIPELINE — compile every Java snippet (needs a JDK)
   Usage: JAVAC=/path/to/javac node scripts/content/compile-java.mjs
   Each snippet gets its own package (so every `class Solution`
   can coexist) plus LeetCode's helper types; one javac run
   compiles them all and failures are mapped back to problems.
   ============================================================ */

import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { spawnSync } from 'node:child_process'

const javac = process.env.JAVAC || 'javac'
const HELPERS = {
  ListNode: 'class ListNode { int val; ListNode next; ListNode() {} ListNode(int val) { this.val = val; } ListNode(int val, ListNode next) { this.val = val; this.next = next; } }',
  TreeNode: 'class TreeNode { int val; TreeNode left, right; TreeNode() {} TreeNode(int val) { this.val = val; } TreeNode(int val, TreeNode left, TreeNode right) { this.val = val; this.left = left; this.right = right; } }',
  Node: 'class Node { public int val; public Node next, random; public List<Node> neighbors = new ArrayList<>(); public Node() {} public Node(int val) { this.val = val; } public Node(int val, ArrayList<Node> neighbors) { this.val = val; this.neighbors = neighbors; } }',
  Interval: 'class Interval { public int start, end; public Interval(int start, int end) { this.start = start; this.end = end; } }',
}

const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'cnote-java-'))
const files = []
const owner = new Map()
let n = 0
for (const f of fs.readdirSync('content-build/problems')) {
  for (const p of JSON.parse(fs.readFileSync(`content-build/problems/${f}`, 'utf8')).problems) {
    for (const kind of ['naive', 'optimal']) {
      const code = p[kind]?.code?.java
      if (!code) continue
      const pkg = `p${n++}`
      const helpers = Object.entries(HELPERS).filter(([name]) => !new RegExp(`\\bclass\\s+${name}\\b`).test(code)).map(([, d]) => d)
      // Top-level `public class X` would force the file name; drop the modifier.
      const body = code.replace(/^public\s+(class|interface)\s/gm, '$1 ')
      const file = path.join(dir, pkg, 'Snippet.java')
      fs.mkdirSync(path.dirname(file))
      fs.writeFileSync(file, `package ${pkg};\nimport java.util.*;\n${helpers.join('\n')}\n${body}\n`)
      files.push(file)
      owner.set(file, `${p.id} ${kind}`)
    }
  }
}

const r = spawnSync(javac, ['-nowarn', '-Xmaxerrs', '10000', '-d', path.join(dir, 'out'), ...files], { encoding: 'utf8' })
if (r.error) { console.error(`Could not run ${javac}: ${r.error.message}`); process.exit(2) }
const failed = new Map()
for (const line of r.stderr.split('\n')) {
  const m = line.match(/^(.*Snippet\.java):(\d+): error: (.*)$/)
  if (m) {
    const key = owner.get(m[1])
    if (!failed.has(key)) failed.set(key, [])
    failed.get(key).push(`line ${m[2] - 2 - 0}: ${m[3]}`)
  }
}
for (const [key, errs] of failed) console.log(`FAIL ${key}\n  ${errs.slice(0, 3).join('\n  ')}`)
console.log(`\nCompiled ${files.length} Java snippets: ${files.length - failed.size} ok, ${failed.size} failed.`)
fs.rmSync(dir, { recursive: true, force: true })
process.exit(failed.size ? 1 : 0)
