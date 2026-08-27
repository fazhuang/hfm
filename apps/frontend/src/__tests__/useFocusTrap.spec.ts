import { afterEach, describe, expect, it } from 'vitest'
import { enableAutoUnmount, mount } from '@vue/test-utils'
import { defineComponent, h, nextTick } from 'vue'
import { useFocusTrap } from '../composables/useFocusTrap'

enableAutoUnmount(afterEach)

type TrapVm = { containerRef: HTMLElement | null; activate: () => void; deactivate: () => void }

function mountTrap() {
  const Comp = defineComponent({
    setup() {
      const { containerRef, activate, deactivate } = useFocusTrap()
      return { containerRef, activate, deactivate }
    },
    render() {
      return h('div', { ref: 'containerRef' }, [
        h('button', { id: 'first' }, 'one'),
        h('button', { id: 'last' }, 'two'),
      ])
    },
  })
  // attachTo: document.body is required so jsdom's focus() works on connected nodes
  return mount(Comp, { attachTo: document.body })
}

describe('useFocusTrap (migrated Batch 2 asset)', () => {
  it('focuses the first focusable element on activate', async () => {
    const wrapper = mountTrap()
    const vm = wrapper.vm as unknown as TrapVm
    vm.activate()
    await nextTick()
    expect(document.activeElement?.id).toBe('first')
    vm.deactivate()
  })

  it('wraps focus from last to first on Tab', async () => {
    const wrapper = mountTrap()
    const vm = wrapper.vm as unknown as TrapVm
    vm.activate()
    await nextTick()

    const lastButton = wrapper.find('#last').element as HTMLElement
    lastButton.focus()
    expect(document.activeElement?.id).toBe('last')

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', bubbles: true }))
    expect(document.activeElement?.id).toBe('first')

    vm.deactivate()
  })

  it('wraps focus from first to last on Shift+Tab', async () => {
    const wrapper = mountTrap()
    const vm = wrapper.vm as unknown as TrapVm
    vm.activate()
    await nextTick()

    const firstButton = wrapper.find('#first').element as HTMLElement
    firstButton.focus()

    document.dispatchEvent(
      new KeyboardEvent('keydown', { key: 'Tab', shiftKey: true, bubbles: true }),
    )
    expect(document.activeElement?.id).toBe('last')

    vm.deactivate()
  })

  it('deactivate removes the keydown listener', async () => {
    const wrapper = mountTrap()
    const vm = wrapper.vm as unknown as TrapVm
    vm.activate()
    vm.deactivate()
    await nextTick()

    const lastButton = wrapper.find('#last').element as HTMLElement
    lastButton.focus()
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Tab', bubbles: true }))
    // no listener → focus stays on the last button
    expect(document.activeElement?.id).toBe('last')
  })
})
