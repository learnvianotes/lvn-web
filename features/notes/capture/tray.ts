import { QuickNoteLimits } from '@/lib/contracts/domain/enums'

/** A photo or PDF waiting in the tray; `fileId` once it is uploaded (a retry skips it). */
export type TrayItem = { key: string; file: File; kind: 'image' | 'pdf'; preview: string | null; fileId?: string }

/** "640 KB", "3.2 MB". */
export function sizeLabel(bytes: number): string {
  return bytes < 1024 ** 2 ? `${Math.max(1, Math.round(bytes / 1024))} KB` : `${(bytes / 1024 ** 2).toFixed(1)} MB`
}

/** The size a picture is drawn at so that its longer side is at most `side`. */
export function fitWithin(width: number, height: number, side: number): { width: number; height: number } {
  const scale = Math.min(1, side / Math.max(width, height))
  return { width: Math.round(width * scale), height: Math.round(height * scale) }
}

export type Refusal = { reason: 'pdfTooLarge'; name: string; size: string } | { reason: 'tooMany'; left: number }

/**
 * What adding these keeps (lvn-backend ADR-0084): up to QuickNoteLimits.files in all and no PDF over pdfBytes;
 * `refused` says what was left out and why.
 */
export function addToTray(tray: TrayItem[], added: TrayItem[]): { tray: TrayItem[]; refused: Refusal[] } {
  const refused: Refusal[] = []
  const fitting = added.filter((item) => {
    if (item.kind === 'pdf' && item.file.size > QuickNoteLimits.pdfBytes) {
      refused.push({ reason: 'pdfTooLarge', name: item.file.name, size: sizeLabel(item.file.size) })
      return false
    }
    return true
  })
  const room = Math.max(0, QuickNoteLimits.files - tray.length)
  if (fitting.length > room) refused.push({ reason: 'tooMany', left: fitting.length - room })
  return { tray: [...tray, ...fitting.slice(0, room)], refused }
}
