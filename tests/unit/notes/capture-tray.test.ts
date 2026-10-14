import { describe, expect, it } from 'vitest'
import { addToTray, fitWithin, sizeLabel, type TrayItem } from '@/features/notes/capture/tray'

const item = (n: number, kind: 'image' | 'pdf' = 'image', size = 300_000): TrayItem => ({ key: `k${n}`, file: { name: kind === 'pdf' ? `doc${n}.pdf` : `p${n}.jpg`, size } as File, kind, preview: null })

/** The tray's limits (lvn-backend ADR-0084): ten photos or PDFs, no PDF over 20 MB, pictures drawn to fit 2,048. */
describe('the photo tray', () => {
  it('keeps up to ten and says how many were left out', () => {
    const eight = Array.from({ length: 8 }, (_, i) => item(i))
    const { tray, refused } = addToTray(eight, [item(8), item(9), item(10), item(11)])
    expect(tray.map((i) => i.key)).toEqual([...eight.map((i) => i.key), 'k8', 'k9'])
    expect(refused).toEqual([{ reason: 'tooMany', left: 2 }])
  })

  it('turns away a PDF over 20 MB with its size, and keeps the rest', () => {
    const { tray, refused } = addToTray([], [item(1, 'pdf', 25 * 1024 ** 2), item(2, 'pdf', 2 * 1024 ** 2), item(3)])
    expect(tray.map((i) => i.key)).toEqual(['k2', 'k3'])
    expect(refused).toEqual([{ reason: 'pdfTooLarge', name: 'doc1.pdf', size: '25.0 MB' }])
  })

  it('draws a large picture at 2,048 on its longer side, and a small one as it is', () => {
    expect(fitWithin(4000, 3000, 2048)).toEqual({ width: 2048, height: 1536 })
    expect(fitWithin(3000, 4000, 2048)).toEqual({ width: 1536, height: 2048 })
    expect(fitWithin(1600, 1200, 2048)).toEqual({ width: 1600, height: 1200 })
    expect([sizeLabel(640 * 1024), sizeLabel(3.2 * 1024 ** 2)]).toEqual(['640 KB', '3.2 MB'])
  })
})
