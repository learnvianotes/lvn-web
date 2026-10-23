/** Which listed models a select may offer. A picker shows one use and leaves every other model out. */

import type { AiModelKind, AiModelUse } from '@/graphql/generated/graphql'

export type ListedModel = { id: string; kind: AiModelKind; supports: readonly AiModelUse[] }

export const KIND_ORDER: readonly AiModelKind[] = ['CHAT', 'EMBEDDING', 'IMAGE', 'AUDIO', 'REALTIME', 'TTS', 'MODERATION', 'OTHER']

/** Chat answers, and every task route except embeddings and transcription. */
export function routeModelUse(task: string): AiModelUse {
  if (task === 'EMBED') return 'EMBEDDING'
  if (task === 'TRANSCRIBE') return 'TRANSCRIBE'
  return 'CHAT'
}

export function modelsForUse(pickers: readonly { use: AiModelUse; models: readonly ListedModel[] }[], use: AiModelUse): ListedModel[] {
  const found = pickers.find((picker) => picker.use === use)
  return dedupe(found?.models ?? [])
}

/** A select is shown only when it has models. An empty picker is left out. */
export function pickerModels(models: readonly ListedModel[] | null): ListedModel[] | null {
  if (!models || models.length === 0) return null
  return [...models]
}

export function filterModels(models: readonly ListedModel[], query: string): ListedModel[] {
  const q = query.trim().toLowerCase()
  if (!q) return [...models]
  return models.filter((model) => model.id.toLowerCase().includes(q))
}

export function groupModels(models: readonly ListedModel[]): { kind: AiModelKind; models: ListedModel[] }[] {
  const buckets = new Map<AiModelKind, ListedModel[]>()
  for (const model of dedupe(models)) {
    const list = buckets.get(model.kind) ?? []
    list.push(model)
    buckets.set(model.kind, list)
  }
  return KIND_ORDER.filter((kind) => buckets.has(kind)).map((kind) => ({
    kind,
    models: buckets.get(kind)!.sort((a, b) => a.id.localeCompare(b.id)),
  }))
}

/** Preset names, before a saved connection has an account catalog. They are hints for that one use. */
export function presetsAsModels(ids: readonly string[], use: AiModelUse): ListedModel[] {
  const kind: AiModelKind = use === 'EMBEDDING' ? 'EMBEDDING' : use === 'IMAGE' ? 'IMAGE' : use === 'TTS' ? 'TTS' : use === 'AUDIO' || use === 'TRANSCRIBE' ? 'AUDIO' : 'CHAT'
  return dedupe(ids.filter(Boolean).map((id) => ({ id, kind, supports: [use] })))
}

function dedupe(models: readonly ListedModel[]): ListedModel[] {
  const seen = new Set<string>()
  const out: ListedModel[] = []
  for (const model of models) {
    if (seen.has(model.id)) continue
    seen.add(model.id)
    out.push(model)
  }
  return out
}
