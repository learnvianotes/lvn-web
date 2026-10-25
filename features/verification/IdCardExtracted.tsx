'use client'

import { useTranslations } from 'next-intl'
import type { IdCardFieldsView } from '@/lib/platform-api'
import { fieldsAgree, type FieldMatch } from './proof'

/** Name, institution, validity and ID number read from the card, next to the profile. */
export function IdCardExtracted({ extracted, profileName, profileInstitution }: { extracted: IdCardFieldsView; profileName: string | null; profileInstitution: string | null }) {
  const t = useTranslations('verification.review')
  const rows: { label: string; extracted: string | null; profile: string | null }[] = [
    { label: t('extractedName'), extracted: extracted.name, profile: profileName },
    { label: t('extractedInstitution'), extracted: extracted.institution, profile: profileInstitution },
  ]
  return (
    <ul className="flex flex-col gap-1 text-sm">
      {rows.map((row) => (
        <li key={row.label}>
          <span className="font-medium">{row.label}:</span> {row.extracted ?? '—'}
          <span className="text-muted"> · {matchLabel(t, fieldsAgree(row.extracted, row.profile), row.profile)}</span>
        </li>
      ))}
      {extracted.validUntil ? <li>{t('validUntil', { when: extracted.validUntil })}</li> : null}
      <li>{extracted.idNumber ? t('idNumber', { value: extracted.idNumber }) : t('idMissing')}</li>
    </ul>
  )
}

function matchLabel(t: ReturnType<typeof useTranslations<'verification.review'>>, match: FieldMatch, profile: string | null): string {
  if (match === 'same') return t('matches')
  if (match === 'different') return t('differs')
  if (!profile) return t('noProfile')
  return t('noProfile')
}
