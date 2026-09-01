/**
 * UX2-P0 accessibility harness — axe-core over mounted primitives (jsdom).
 *
 * Component-level structural axe run (P0 harness). Full-page axe over
 * authorized production surfaces is the UX2-P6 verification scope.
 */
import { afterEach, describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import axe from 'axe-core'
import DHObjectLayout from '../components/primitives/DHObjectLayout.vue'
import BibliographicRecord from '../components/primitives/BibliographicRecord.vue'

/** Component-level rules; page-level rules (document-title, meta-viewport,
 *  page-has-heading-one, landmark-unique) belong to full-page verification. */
const RUN_ONLY = {
  type: 'rule' as const,
  values: [
    'heading-order',
    'aria-allowed-attr',
    'aria-required-attr',
    'aria-valid-attr-value',
    'aria-valid-attr',
    'button-name',
    'definition-list',
    'duplicate-id',
    'label',
    'link-name',
    'list',
    'nested-interactive',
    'region',
    'select-name',
  ],
}

async function axeViolations(el: HTMLElement): Promise<string[]> {
  const results = await axe.run(el, { runOnly: RUN_ONLY })
  return results.violations.map((v) => v.id)
}

let host: HTMLElement | null = null

afterEach(() => {
  if (host && host.parentNode) host.parentNode.removeChild(host)
  host = null
})

function withMainHost(): HTMLElement {
  host = document.createElement('main')
  document.body.appendChild(host)
  return host
}

describe('UX2-P0 accessibility — axe = 0', () => {
  it('DHObjectLayout (full PRESENT + incomplete evidence + relations) is axe-clean', async () => {
    const main = withMainHost()
    mount(DHObjectLayout, {
      attachTo: main,
      props: {
        title: '皇甫谧',
        titleTag: 1,
        meta: [{ label: '生卒年', value: '215—282' }, { value: '人物档案' }],
        slots: {
          header: { state: 'PRESENT' },
          context: { state: 'PRESENT' },
          evidence: {
            state: 'INCOMPLETE_WITH_EVIDENCE_STATE',
            status: 'METADATA_ONLY',
            statusLabel: '仅题录',
            note: '原典全文未收录；整理说明已可读',
          },
          relations: { state: 'PRESENT' },
        },
        relations: [
          { label: '作品《针灸甲乙经》', href: '/jiayi', sem: 'EXPLICIT_RELATION' },
          { label: '非遗传承', sem: 'ASSOCIATED_CONTEXT' },
        ],
      },
      slots: {
        context: '<p>其传 · 后论 已整理为 Reader 全文（2 篇 FULL_TEXT）。</p>',
      },
    })
    expect(await axeViolations(main)).toEqual([])
  })

  it('BibliographicRecord (full record) is axe-clean', async () => {
    const main = withMainHost()
    mount(BibliographicRecord, {
      attachTo: main,
      props: {
        title: '《针灸甲乙经》医统正脉全书本',
        author: '皇甫谧',
        year: '明万历 29 年（1601）',
        kind: '古代版本',
        source: '客户提供：甲乙经论著资料',
        status: 'METADATA_ONLY',
        statusLabel: '存目',
        description: '医统正脉全书所收版本。',
        locator: '引用定位：文档级',
        href: '/jiayi#editions',
      },
    })
    expect(await axeViolations(main)).toEqual([])
  })
})
