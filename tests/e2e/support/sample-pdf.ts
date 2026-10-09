/**
 * A small real PDF for the reader's tests: two A4 pages of text in Helvetica and an outline with an entry per page.
 * Built here, with its cross-reference table, so no binary fixture is committed.
 */

export const PDF_TEXT = {
  page1: ['Photosynthesis', 'Plants turn light into chemical energy.', 'Chlorophyll absorbs red and blue light.'],
  page2: ['Respiration', 'Cells release energy from glucose.'],
}

function content(lines: string[]): string {
  return lines.map((line, i) => `BT /F1 ${i === 0 ? 24 : 14} Tf 72 ${760 - i * 40} Td (${line}) Tj ET`).join('\n')
}

export function samplePdf(): Buffer {
  const streams = [content(PDF_TEXT.page1), content(PDF_TEXT.page2)]
  const objects = [
    '<< /Type /Catalog /Pages 2 0 R /Outlines 8 0 R /PageMode /UseOutlines >>',
    '<< /Type /Pages /Kids [3 0 R 5 0 R] /Count 2 >>',
    '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 7 0 R >> >> /Contents 4 0 R >>',
    `<< /Length ${streams[0]!.length} >>\nstream\n${streams[0]}\nendstream`,
    '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 7 0 R >> >> /Contents 6 0 R >>',
    `<< /Length ${streams[1]!.length} >>\nstream\n${streams[1]}\nendstream`,
    '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>',
    '<< /Type /Outlines /First 9 0 R /Last 10 0 R /Count 2 >>',
    '<< /Title (Photosynthesis) /Parent 8 0 R /Next 10 0 R /Dest [3 0 R /XYZ 0 842 null] >>',
    '<< /Title (Respiration) /Parent 8 0 R /Prev 9 0 R /Dest [5 0 R /XYZ 0 842 null] >>',
  ]
  let out = '%PDF-1.7\n'
  const offsets: number[] = []
  objects.forEach((body, i) => {
    offsets.push(out.length)
    out += `${i + 1} 0 obj\n${body}\nendobj\n`
  })
  const xref = out.length
  out += `xref\n0 ${objects.length + 1}\n0000000000 65535 f \n${offsets.map((o) => `${String(o).padStart(10, '0')} 00000 n \n`).join('')}`
  out += `trailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF\n`
  return Buffer.from(out, 'latin1')
}
