import { describe, expect, it } from 'vitest'
import { confidencePercent, fieldsAgree, proofKind, verdictTone } from '@/features/verification/proof'

describe('proof preview', () => {
  it('treats images and pdfs as previewable', () => {
    expect(proofKind('image/png', 'card.png')).toBe('image')
    expect(proofKind('image/jpeg', 'card.jpg')).toBe('image')
    expect(proofKind('application/pdf', 'card.pdf')).toBe('pdf')
    expect(proofKind('application/octet-stream', 'card.PDF')).toBe('pdf')
    expect(proofKind('text/plain', 'notes.txt')).toBe('file')
  })

  it('reads confidence as a fraction or a percent', () => {
    expect(confidencePercent(0.82)).toBe(82)
    expect(confidencePercent(82)).toBe(82)
    expect(confidencePercent(null)).toBeNull()
    expect(confidencePercent(Number.NaN)).toBeNull()
  })

  it('compares the card with the profile without caring about case or punctuation', () => {
    expect(fieldsAgree('Ravi Kumar', 'ravi kumar')).toBe('same')
    expect(fieldsAgree('IIT Hyderabad', 'Hyderabad')).toBe('same')
    expect(fieldsAgree('Other College', 'IIT Hyderabad')).toBe('different')
    expect(fieldsAgree('Ravi', null)).toBe('unknown')
  })

  it('colours a verdict by its words', () => {
    expect(verdictTone('APPROVE')).toBe('good')
    expect(verdictTone('high_confidence_match')).toBe('good')
    expect(verdictTone('MISMATCH')).toBe('bad')
    expect(verdictTone('REVIEW')).toBe('pending')
  })
})
