/* ============================================================
   CONTENT PIPELINE — code validation
   Several legacy Sheet 150 modules contain C++/Java that was
   machine-translated from Python and does not compile. Rather
   than guess, we check it:
     C++  → clang++ -fsyntax-only with LeetCode's helper types
     Java → java-parser (syntax only; no JDK needed)
   Results are cached by content hash so re-runs are fast.
   ============================================================ */

import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import crypto from 'node:crypto'
import { spawnSync } from 'node:child_process'
import vm from 'node:vm'
import { parse as parseJava } from 'java-parser'

const CACHE_FILE = 'content-src/.code-check-cache.json'
let cache = {}
try { cache = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8')) } catch { /* missing or mid-write: start empty */ }
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'cnote-cpp-'))

const HEADERS = ['algorithm', 'array', 'bitset', 'climits', 'cmath', 'cstring', 'deque', 'functional',
  'iostream', 'map', 'numeric', 'queue', 'set', 'sstream', 'stack', 'string', 'tuple',
  'unordered_map', 'unordered_set', 'utility', 'vector']

const HELPERS = {
  ListNode: 'struct ListNode { int val; ListNode *next; ListNode(): val(0), next(nullptr) {} ListNode(int x): val(x), next(nullptr) {} ListNode(int x, ListNode *n): val(x), next(n) {} };',
  TreeNode: 'struct TreeNode { int val; TreeNode *left, *right; TreeNode(): val(0), left(nullptr), right(nullptr) {} TreeNode(int x): val(x), left(nullptr), right(nullptr) {} TreeNode(int x, TreeNode *l, TreeNode *r): val(x), left(l), right(r) {} };',
  Node: 'class Node { public: int val; Node *next = nullptr, *random = nullptr; vector<Node*> neighbors; Node() {} Node(int v): val(v) {} Node(int v, vector<Node*> n): val(v), neighbors(n) {} };',
  Interval: 'struct Interval { int start, end; Interval(int s, int e): start(s), end(e) {} };',
}

const hash = (s) => crypto.createHash('sha1').update(s).digest('hex')

export function cppCompiles(code) {
  const key = `cpp:${hash(code)}`
  if (key in cache) return cache[key]
  const helpers = Object.entries(HELPERS)
    .filter(([name]) => !new RegExp(`\\b(struct|class)\\s+${name}\\b`).test(code))
    .map(([, def]) => def)
  const src = HEADERS.map((h) => `#include <${h}>`).join('\n') + '\nusing namespace std;\n' + helpers.join('\n') + '\n' + code + '\n'
  const file = path.join(tmp, 'check.cpp')
  fs.writeFileSync(file, src)
  const r = spawnSync('clang++', ['-std=c++17', '-fsyntax-only', '-w', file], { encoding: 'utf8' })
  cache[key] = r.status === 0
  return cache[key]
}

export function javaParses(code) {
  const key = `java:${hash(code)}`
  if (key in cache) return cache[key]
  try { parseJava(code); cache[key] = true } catch { cache[key] = false }
  return cache[key]
}

/** C++ compile errors (first lines) or '' when it compiles. Not cached — used by check-code. */
export function cppErrors(code) {
  const helpers = Object.entries(HELPERS)
    .filter(([name]) => !new RegExp(`\\b(struct|class)\\s+${name}\\b`).test(code))
    .map(([, def]) => def)
  const src = HEADERS.map((h) => `#include <${h}>`).join('\n') + '\nusing namespace std;\n' + helpers.join('\n') + '\n' + code + '\n'
  const file = path.join(tmp, 'errors.cpp')
  fs.writeFileSync(file, src)
  const r = spawnSync('clang++', ['-std=c++17', '-fsyntax-only', '-w', file], { encoding: 'utf8' })
  return r.status === 0 ? '' : r.stderr.split('\n').filter((l) => l.includes('error')).slice(0, 4).join('\n')
}

export function javaErrors(code) {
  try { parseJava(code); return '' } catch (e) { return String(e.message).split('\n').slice(0, 3).join(' ') }
}

export function jsErrors(code) {
  try { new vm.Script(code); return '' } catch (e) { return String(e.message) }
}

export function saveCache() {
  // Atomic write: several checks may run at once.
  const tmpFile = `${CACHE_FILE}.${process.pid}`
  fs.writeFileSync(tmpFile, JSON.stringify(cache))
  fs.renameSync(tmpFile, CACHE_FILE)
  fs.rmSync(tmp, { recursive: true, force: true })
}
