import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  isPresentationState,
  PRESENTATION_STATES,
  presentationLabel,
  presentationStatusLabel,
  resolvePresentationState,
  resolveTitleTag,
} from '../presentation/stateMapping'

describe('resolvePresentationState — G1-C matrix', () => {
  it('row 1: AVAILABLE + FULL_TEXT → RESOURCE_READY', () => {
    expect(resolvePresentationState({ contentStatus: 'AVAILABLE', readingAvailability: 'FULL_TEXT' })).toBe(
      'RESOURCE_READY',
    )
  })

  it('row 2: AVAILABLE + EXCERPT → RESOURCE_READY', () => {
    expect(resolvePresentationState({ contentStatus: 'AVAILABLE', readingAvailability: 'EXCERPT' })).toBe(
      'RESOURCE_READY',
    )
  })

  it('rows 12/13: AVAILABLE (no reading availability) → RESOURCE_READY', () => {
    expect(resolvePresentationState({ contentStatus: 'AVAILABLE' })).toBe('RESOURCE_READY')
  })

  it('row 3: METADATA_ONLY + metadata present → METADATA_ONLY', () => {
    expect(
      resolvePresentationState({ contentStatus: 'METADATA_ONLY', hasMetadata: true }),
    ).toBe('METADATA_ONLY')
  })

  it('row 5: full text absent from corpus + collation description present → METADATA_ONLY (not 文献阙佚)', () => {
    expect(resolvePresentationState({ collationDescriptionPresent: true })).toBe('METADATA_ONLY')
  })

  it('row 6: verified text records loss → HISTORICAL_ABSENCE', () => {
    expect(
      resolvePresentationState({ contentStatus: 'METADATA_ONLY', historicalAbsence: true }),
    ).toBe('HISTORICAL_ABSENCE')
  })

  it('row 7: verified scholarly controversy → SCHOLARLY_UNCERTAIN', () => {
    expect(
      resolvePresentationState({ contentStatus: 'AVAILABLE', readingAvailability: 'FULL_TEXT', scholarlyUncertain: true }),
    ).toBe('SCHOLARLY_UNCERTAIN')
  })

  it('row 10: edition exists + digitized resource absent → METADATA_ONLY (存目)', () => {
    expect(
      resolvePresentationState({ contentStatus: 'AVAILABLE', digitizedResourceAbsent: true }),
    ).toBe('METADATA_ONLY')
  })

  it('row 4 / fail-closed: DATA_GAP without metadata or loss → UNSTRUCTURED_OR_INCOMPLETE', () => {
    expect(resolvePresentationState({ contentStatus: 'DATA_GAP' })).toBe('UNSTRUCTURED_OR_INCOMPLETE')
  })

  it('fail-closed: unknown/absent inputs → UNSTRUCTURED_OR_INCOMPLETE', () => {
    expect(resolvePresentationState({})).toBe('UNSTRUCTURED_OR_INCOMPLETE')
    expect(resolvePresentationState({ contentStatus: 'DATA_GAP', hasMetadata: false })).toBe(
      'UNSTRUCTURED_OR_INCOMPLETE',
    )
  })
})

describe('resolvePresentationState — conflict precedence (G1-C §3)', () => {
  it('SCHOLARLY_UNCERTAIN (7) outranks RESOURCE_READY (5)', () => {
    expect(
      resolvePresentationState({
        contentStatus: 'AVAILABLE',
        readingAvailability: 'FULL_TEXT',
        scholarlyUncertain: true,
      }),
    ).toBe('SCHOLARLY_UNCERTAIN')
  })

  it('HISTORICAL_ABSENCE (6) outranks unavailability', () => {
    expect(
      resolvePresentationState({ contentStatus: 'DATA_GAP', historicalAbsence: true }),
    ).toBe('HISTORICAL_ABSENCE')
  })

  it('METADATA_ONLY (4) beats fail-closed (3) when metadata present', () => {
    expect(resolvePresentationState({ contentStatus: 'METADATA_ONLY' })).toBe('METADATA_ONLY')
  })

  it('deterministic: identical inputs always produce the same state', () => {
    const inputs = { contentStatus: 'METADATA_ONLY', hasMetadata: true } as const
    expect(resolvePresentationState(inputs)).toBe(resolvePresentationState(inputs))
  })

  it('missing data is never treated as historical absence', () => {
    expect(resolvePresentationState({ contentStatus: 'DATA_GAP' })).not.toBe('HISTORICAL_ABSENCE')
  })
})

describe('presentationLabel / presentationStatusLabel — G1-C public labels', () => {
  it('canonical labels per state', () => {
    expect(presentationLabel('RESOURCE_READY')).toBe('数字资源可阅')
    expect(presentationLabel('METADATA_ONLY')).toBe('仅题录')
    expect(presentationLabel('SCHOLARLY_UNCERTAIN')).toBe('尚有争议')
    expect(presentationLabel('HISTORICAL_ABSENCE')).toBe('文献阙佚')
    expect(presentationLabel('UNSTRUCTURED_OR_INCOMPLETE')).toBe('资料整理中')
  })

  it('context variants', () => {
    expect(presentationLabel('RESOURCE_READY', { reader: true })).toBe('全文已整理')
    expect(presentationLabel('METADATA_ONLY', { excerpt: true })).toBe('存目')
    expect(presentationLabel('METADATA_ONLY', { searchable: true })).toBe('仅题录（可检索）')
  })

  it('explicit label wins over canonical', () => {
    expect(presentationStatusLabel('METADATA_ONLY', '存目')).toBe('存目')
    expect(presentationStatusLabel('RESOURCE_READY', '已展示')).toBe('已展示')
  })

  it('known state without explicit label → canonical label', () => {
    expect(presentationStatusLabel('SCHOLARLY_UNCERTAIN')).toBe('尚有争议')
  })

  it('unknown status → raw status; absent → fail-closed text', () => {
    expect(presentationStatusLabel('SOME_RAW_STATUS')).toBe('SOME_RAW_STATUS')
    expect(presentationStatusLabel(undefined)).toBe('资料整理中')
  })

  it('isPresentationState / vocabulary closed set', () => {
    expect(PRESENTATION_STATES).toHaveLength(5)
    for (const s of PRESENTATION_STATES) expect(isPresentationState(s)).toBe(true)
    expect(isPresentationState('AVAILABLE')).toBe(false)
    expect(isPresentationState(undefined)).toBe(false)
  })
})

describe('resolveTitleTag — frozen N-F-1 production contract', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('valid 1..6 → semantic h1..h6, no warning', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    expect(resolveTitleTag(1)).toBe('h1')
    expect(resolveTitleTag(2)).toBe('h2')
    expect(resolveTitleTag(3)).toBe('h3')
    expect(resolveTitleTag(4)).toBe('h4')
    expect(resolveTitleTag(5)).toBe('h5')
    expect(resolveTitleTag(6)).toBe('h6')
    expect(warn).not.toHaveBeenCalled()
  })

  it('null | undefined | "none" → non-heading <p>, no warning', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    expect(resolveTitleTag(null)).toBe('p')
    expect(resolveTitleTag(undefined)).toBe('p')
    expect(resolveTitleTag('none')).toBe('p')
    expect(warn).not.toHaveBeenCalled()
  })

  it.each([0, -1, 7, 1.5, NaN])('invalid numeric %s → fail-closed <p> + dev warning', (value) => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    expect(resolveTitleTag(value)).toBe('p')
    expect(warn).toHaveBeenCalledTimes(1)
  })

  it('invalid strings → fail-closed <p> + dev warning (0 NOT a valid production value)', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    expect(resolveTitleTag('h2' as unknown as number)).toBe('p')
    expect(resolveTitleTag('arbitrary' as unknown as number)).toBe('p')
    expect(warn).toHaveBeenCalledTimes(2)
    expect(warn.mock.calls[0][0]).toContain('0 is NOT a valid production titleTag value')
  })

  it('no truthiness-based branch: 0 is treated as invalid, not as absent', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    expect(resolveTitleTag(0)).toBe('p')
    expect(warn).toHaveBeenCalledTimes(1)
  })
})
