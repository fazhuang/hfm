/**
 * useTextDirection — 其言阅读页的横排 / 竖排偏好（P-8）。
 *
 * 照 useTheme 的模式（模块级 ref + localStorage），使偏好跨页面、跨会话保持。
 * 竖排是古籍的本来形态，但竖排对不熟悉的人反而更难读，所以默认**横排**，
 * 由读者自行切换 —— 不做「因为它是古籍所以必须竖排」的强制。
 *
 * 纯 CSS `writing-mode`，不引入任何排版库。
 */
import { ref, watchEffect } from 'vue'

export type TextDirection = 'horizontal' | 'vertical'

const STORAGE_KEY = 'hfm-yan-direction'

const direction = ref<TextDirection>(load())

function load(): TextDirection {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === 'horizontal' || stored === 'vertical') {
      return stored
    }
  } catch {
    // localStorage 不可用（隐私模式 / jsdom）
  }
  return 'horizontal'
}

export function useTextDirection() {
  watchEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.dataset.yanDirection = direction.value
    }
  })

  function setDirection(value: TextDirection): void {
    direction.value = value
    try {
      localStorage.setItem(STORAGE_KEY, value)
    } catch {
      // ignore
    }
  }

  function toggleDirection(): void {
    setDirection(direction.value === 'horizontal' ? 'vertical' : 'horizontal')
  }

  return { direction, setDirection, toggleDirection }
}
