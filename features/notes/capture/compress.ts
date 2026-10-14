import { QuickNoteLimits } from '@/lib/contracts/domain/enums'
import { fitWithin } from './tray'

/** How much a picture is compressed: small enough to upload quickly, sharp enough to read handwriting. */
const QUALITY = 0.75
/** A JPEG this small and within the side is sent as it is. */
const SMALL = 1024 ** 2

/**
 * A picture made smaller in the browser before it is uploaded (lvn-backend ADR-0084): drawn at most
 * QuickNoteLimits.pictureSide on the longer side, upright, on white, as JPEG. Throws when the browser cannot read it
 * (a HEIC photo outside Safari).
 */
export async function compressPicture(file: File): Promise<File> {
  const bitmap = await createImageBitmap(file, { imageOrientation: 'from-image' })
  try {
    const { width, height } = fitWithin(bitmap.width, bitmap.height, QuickNoteLimits.pictureSide)
    if (width === bitmap.width && file.type === 'image/jpeg' && file.size <= SMALL) return file
    const canvas = document.createElement('canvas')
    canvas.width = width
    canvas.height = height
    const ctx = canvas.getContext('2d')
    if (!ctx) throw new Error('no canvas')
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, width, height)
    ctx.drawImage(bitmap, 0, 0, width, height)
    const blob = await new Promise<Blob | null>((resolve) => canvas.toBlob(resolve, 'image/jpeg', QUALITY))
    if (!blob) throw new Error('not encoded')
    return new File([blob], `${file.name.replace(/\.[a-z0-9]{1,5}$/i, '') || 'photo'}.jpg`, { type: 'image/jpeg' })
  } finally {
    bitmap.close()
  }
}
