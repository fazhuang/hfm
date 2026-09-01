/**
 * UX2-P0 token scan — negative boundary (NB-09 / G1-B): no hard-coded palette
 * in the new UX2 production files. Every visual value must resolve to a token.
 */
import { describe, expect, it } from 'vitest'
import dhObjectLayoutSource from '../components/primitives/DHObjectLayout.vue?raw'
import bibliographicRecordSource from '../components/primitives/BibliographicRecord.vue?raw'
import stateMappingSource from '../presentation/stateMapping.ts?raw'

const NEW_UX2_SOURCE_FILES: Array<[string, string]> = [
  ['components/primitives/DHObjectLayout.vue', dhObjectLayoutSource],
  ['components/primitives/BibliographicRecord.vue', bibliographicRecordSource],
  ['presentation/stateMapping.ts', stateMappingSource],
]

const HEX_PATTERN = /(?<!&)#[0-9a-fA-F]{3,8}\b/

describe('UX2-P0 token scan — NB-09 (no arbitrary hardcoded palette)', () => {
  for (const [name, source] of NEW_UX2_SOURCE_FILES) {
    it(`${name} contains no hard-coded hex color`, () => {
      const matches = source.match(HEX_PATTERN)
      expect(matches, `found hex in ${name}: ${matches?.join(', ')}`).toBeNull()
    })
  }
})
