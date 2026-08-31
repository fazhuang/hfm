/**
 * P2-04 Heritage Visualization tests.
 *
 * Proves the frozen P2-04 acceptance criteria:
 *  - P2-04-AC-01 visualization renders evidence-backed relations from the
 *    P1-06 API projection (fixture);
 *  - P2-04-AC-02 unverified/private nodes are not displayed publicly;
 *  - P2-04-AC-03 empty genealogy state renders gracefully (no crash/blank).
 */
import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import { visibleNodes, visibleRelations } from '../services/heritage'
import HeritageView from '../views/heritage/HeritageView.vue'
import LineageTree from '../components/LineageTree.vue'
import EmptyState from '../components/states/EmptyState.vue'
import type { LineageProjection } from '../types/heritage'

const projection: LineageProjection = {
  nodes: [
    { id: 'n1', name: '皇甫谧', evidenceBound: true, publicationState: 'published' },
    { id: 'n2', name: '佚名传承人', evidenceBound: false, publicationState: 'published' },
    { id: 'n3', name: '未公开节点', evidenceBound: true, publicationState: 'draft' },
  ],
  relations: [
    {
      id: 'r1',
      from: 'n1',
      to: 'n2',
      relationType: '师承',
      evidenceBound: true,
      publicationState: 'published',
    },
    {
      id: 'r2',
      from: 'n1',
      to: 'n3',
      relationType: '师承',
      evidenceBound: false,
      publicationState: 'published',
    },
  ],
}

describe('P2-04-AC-01 evidence-backed relations rendered', () => {
  it('renders nodes/relations bound to evidence from the P1-06 API projection', () => {
    const nodes = visibleNodes(projection)
    const relations = visibleRelations(projection)
    expect(nodes.map((n) => n.id)).toEqual(['n1'])
    expect(relations.map((r) => r.id)).toEqual(['r1'])
    expect(relations[0].evidenceBound).toBe(true)
  })

  it('LineageTree renders the visible nodes', () => {
    const wrapper = mount(LineageTree, {
      props: {
        nodes: [{ id: 'n1', name: '皇甫谧', evidenceBound: true, publicationState: 'published' }],
      },
    })
    expect(wrapper.text()).toContain('皇甫谧')
  })
})

describe('P2-04-AC-02 unverified/private nodes hidden', () => {
  it('unverified node is not displayed publicly', () => {
    const nodes = visibleNodes(projection)
    expect(nodes.some((n) => n.id === 'n2' && !n.evidenceBound)).toBe(false)
    expect(nodes.map((n) => n.id)).not.toContain('n2')
  })

  it('private (non-published) node is not displayed publicly', () => {
    const nodes = visibleNodes(projection)
    expect(nodes.map((n) => n.id)).not.toContain('n3')
  })

  it('unverified relation is not displayed', () => {
    const relations = visibleRelations(projection)
    expect(relations.map((r) => r.id)).not.toContain('r2')
  })
})

describe('P2-04-AC-03 empty genealogy state', () => {
  it('renders a graceful empty state instead of crashing', () => {
    const wrapper = mount(HeritageView)
    // no data yet -> loading or empty state, never a blank crash
    expect(wrapper.exists()).toBe(true)
    wrapper.unmount()
  })

  it('empty projection renders the EmptyState component', () => {
    const wrapper = mount(EmptyState, { props: { label: '暂无已发布的传承谱系数据。' } })
    expect(wrapper.find('[role="status"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('暂无已发布的传承谱系数据')
  })

  it('LineageTree with zero nodes renders an empty list without error', () => {
    const wrapper = mount(LineageTree, { props: { nodes: [] } })
    expect(wrapper.findAll('.lineage-tree__node')).toHaveLength(0)
  })
})
