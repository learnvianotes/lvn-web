/* ============================================================
   CONTENT PIPELINE — seed Firestore
   Uploads public/content (produced by extract.mjs) to Firestore.

   Layout:
     catalog/current                               catalog.json
     subjects/{subjectId}/topics/{topicId}         topic (html chunked if > ~900 KB)
     subjects/{subjectId}/topics/{topicId}/chunks/{n}   { html } overflow chunks
     subjects/sheet-150/problems/{problemId}       one problem

   Requires a service account (Firebase console → Project settings →
   Service accounts → Generate new private key):

     GOOGLE_APPLICATION_CREDENTIALS=./service-account.json \
       node scripts/content/seed-firestore.mjs

   Writes bypass security rules (admin SDK), so the rules can stay
   read-only for everyone else.
   ============================================================ */

import fs from 'node:fs'
import path from 'node:path'
import { initializeApp, applicationDefault } from 'firebase-admin/app'
import { getFirestore } from 'firebase-admin/firestore'
import { OUT_DIR } from './config.mjs'

const CHUNK = 900_000 // characters; keeps each doc under Firestore's 1 MiB limit

if (!process.env.GOOGLE_APPLICATION_CREDENTIALS) {
  console.error('Set GOOGLE_APPLICATION_CREDENTIALS to a service-account JSON file. See the header of this script.')
  process.exit(1)
}

const read = (rel) => JSON.parse(fs.readFileSync(path.join(OUT_DIR, rel), 'utf8'))

initializeApp({ credential: applicationDefault() })
const db = getFirestore()
const writer = db.bulkWriter()
let writes = 0
const put = (ref, data) => { writes++; writer.set(ref, data) }

const catalog = read('catalog.json')
put(db.doc('catalog/current'), catalog)

for (const subject of catalog.subjects) {
  if (subject.kind === 'problems') {
    for (const cat of subject.topics) {
      const { problems } = read(`problems/${cat.id}.json`)
      for (const p of problems) put(db.doc(`subjects/${subject.id}/problems/${p.id}`), p)
    }
    continue
  }
  for (const t of subject.topics) {
    const topic = read(`topics/${subject.id}/${t.id}.json`)
    const chunks = []
    for (let i = 0; i < topic.html.length; i += CHUNK) chunks.push(topic.html.slice(i, i + CHUNK))
    const ref = db.doc(`subjects/${subject.id}/topics/${t.id}`)
    put(ref, { ...topic, html: chunks[0] ?? '', chunks: chunks.length })
    chunks.slice(1).forEach((html, i) => put(ref.collection('chunks').doc(String(i + 1)), { html }))
  }
}

await writer.close()
console.log(`Seeded ${writes} documents to project ${db.projectId ?? ''}.`)
