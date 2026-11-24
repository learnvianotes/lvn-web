// Copied from lvn-backend contracts/src/validation/drawing.ts by scripts/contracts-sync.mjs — do not edit here.
import { z } from 'zod'

/** Bounds for a page's ink and the images placed on it. */
export const DRAWING_LIMITS = {
  strokes: 5_000,
  points: 8_000,
  pages: 200,
  imagesPerPage: 30,
} as const

export const StrokeTool = { PEN: 'pen', MARKER: 'marker', ERASER: 'eraser', RULER: 'ruler' } as const
export type StrokeTool = (typeof StrokeTool)[keyof typeof StrokeTool]

const point = z.object({ x: z.number().finite(), y: z.number().finite() })

/**
 * One ink stroke. Pen and marker carry a colour. A ruler is the straight line between two points.
 * An eraser removes ink; it has no colour.
 */
export const strokeSchema = z
  .object({
    id: z.string().min(1).max(64),
    tool: z.enum(['pen', 'marker', 'eraser', 'ruler']),
    color: z.string().regex(/^#[0-9a-fA-F]{6}$/).optional(),
    width: z.number().positive().max(200),
    points: z.array(point).min(1).max(DRAWING_LIMITS.points),
  })
  .superRefine((stroke, ctx) => {
    if ((stroke.tool === 'pen' || stroke.tool === 'marker') && !stroke.color) {
      ctx.addIssue({ code: 'custom', message: 'Pen and marker strokes need a colour.', path: ['color'] })
    }
    if (stroke.tool === 'ruler' && stroke.points.length !== 2) {
      ctx.addIssue({ code: 'custom', message: 'A ruler line is two points.', path: ['points'] })
    }
  })

/** The drawing layer of one page: vector strokes, nothing rasterised. */
export const drawingSchema = z.object({
  strokes: z.array(strokeSchema).max(DRAWING_LIMITS.strokes),
})

export type Drawing = z.infer<typeof drawingSchema>

export const pageImagePlacementSchema = z.object({
  x: z.number().finite(),
  y: z.number().finite(),
  width: z.number().positive().max(20_000),
  height: z.number().positive().max(20_000),
  rotation: z.number().finite().min(-360).max(360),
})

export type PageImagePlacement = z.infer<typeof pageImagePlacementSchema>

export function parseDrawing(value: unknown): { ok: true; drawing: Drawing } | { ok: false; message: string } {
  const parsed = drawingSchema.safeParse(value)
  if (parsed.success) return { ok: true, drawing: parsed.data }
  const issue = parsed.error.issues[0]
  return { ok: false, message: issue ? `${issue.path.join('.') || 'drawing'}: ${issue.message}` : 'That drawing is not valid.' }
}

export function parsePageImagePlacement(value: unknown): { ok: true; placement: PageImagePlacement } | { ok: false; message: string } {
  const parsed = pageImagePlacementSchema.safeParse(value)
  if (parsed.success) return { ok: true, placement: parsed.data }
  const issue = parsed.error.issues[0]
  return { ok: false, message: issue ? `${issue.path.join('.') || 'placement'}: ${issue.message}` : 'That placement is not valid.' }
}
