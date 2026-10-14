import type { DocumentInitParameters } from 'pdfjs-dist/types/src/display/api'

type PdfJs = typeof import('pdfjs-dist')

/** The first piece fetched: enough for most PDFs' first pages and their cross-reference table. */
const FIRST_BYTES = 256 * 1024

/**
 * A PDF read in ranges from a pre-signed URL that lives 15 minutes (lvn-backend ADR-0090): when storage refuses an
 * expired URL, `refresh` asks the API for a new one and the read goes on, so a long reading session never breaks. A
 * file small enough to arrive whole in the first piece is given to pdf.js as data.
 */
export async function pdfSource(pdfjs: PdfJs, firstUrl: string, refresh: () => Promise<string | null>): Promise<DocumentInitParameters> {
  let url = firstUrl
  const get = async (begin: number, end: number): Promise<{ status: number; total: number | null; bytes: Uint8Array }> => {
    for (let attempt = 0; ; attempt++) {
      const res = await fetch(url, { headers: { range: `bytes=${begin}-${end - 1}` } })
      if (res.ok) {
        const total = Number(res.headers.get('content-range')?.split('/')[1])
        return { status: res.status, total: Number.isFinite(total) ? total : null, bytes: new Uint8Array(await res.arrayBuffer()) }
      }
      // An expired URL: S3 and RustFS answer 403 (AccessDenied, "Request has expired").
      const next = attempt === 0 && (res.status === 403 || res.status === 400) ? await refresh() : null
      if (!next) throw new Error(`the PDF could not be read (${res.status})`)
      url = next
    }
  }
  const first = await get(0, FIRST_BYTES)
  if (first.status === 200 || first.total === null || first.bytes.length >= first.total) return { data: first.bytes }
  const transport = new pdfjs.PDFDataRangeTransport(first.total, first.bytes)
  transport.requestDataRange = (begin: number, end: number) => {
    get(begin, end).then(
      ({ bytes }) => transport.onDataRange(begin, bytes),
      () => transport.abort(),
    )
  }
  return { range: transport }
}
