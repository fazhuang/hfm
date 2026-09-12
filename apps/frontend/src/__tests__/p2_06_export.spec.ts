/**
 * P2-06 Export/Print UI tests.
 *
 * Proves the frozen P2-06 frontend acceptance criteria:
 *  - P2-06-AC-01 export output preserves the disclaimer;
 *  - P2-06-AC-02 withdrawn content export is blocked;
 *  - P2-06-AC-03 export output is deterministic on fixture.
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { EXPORT_DISCLAIMER, ExportError, exportMarkdown, exportPrint } from '../services/export'
import ExportPanel from '../components/ExportPanel.vue'

const record = { title: '校勘笔记', body: '正文内容。', publicationState: 'published' as const }

describe('P2-06-AC-01 disclaimer retained', () => {
  it('markdown export contains the disclaimer', () => {
    expect(exportMarkdown(record)).toContain(EXPORT_DISCLAIMER)
  })

  it('print export contains the disclaimer', () => {
    expect(exportPrint(record)).toContain(EXPORT_DISCLAIMER)
  })

  it('export panel renders the disclaimer in its output', async () => {
    const wrapper = mount(ExportPanel)
    const buttons = wrapper.findAll('button')
    await buttons[0].trigger('click')
    expect(wrapper.find('[data-testid="export-output"]').text()).toContain(EXPORT_DISCLAIMER)
  })
})

describe('P2-06-AC-02 withdrawn export blocked', () => {
  it('markdown export of withdrawn content throws ExportError', () => {
    expect(() => exportMarkdown({ ...record, publicationState: 'withdrawn' })).toThrow(ExportError)
  })

  it('print export of withdrawn content throws ExportError', () => {
    expect(() => exportPrint({ ...record, publicationState: 'withdrawn' })).toThrow(ExportError)
  })

  it('draft export is also blocked', () => {
    expect(() => exportMarkdown({ ...record, publicationState: 'draft' })).toThrow(ExportError)
  })
})

describe('P2-06-AC-03 deterministic output', () => {
  it('identical input produces identical bytes', () => {
    expect(exportMarkdown(record)).toBe(exportMarkdown(record))
    expect(exportMarkdown(record)).toBe(exportMarkdown({ ...record }))
    expect(exportPrint(record)).toBe(exportPrint(record))
  })
})
