/**
 * UI-08 《针灸甲乙经》核心学术界面 — browser E2E.
 *
 *  - /jiayi renders the flagship page with heading + lineage PNG;
 *  - enlarge dialog is keyboard-operable (Enter open, Escape close,
 *    focus returns to the trigger);
 *  - mobile (375px) renders without horizontal overflow;
 *  - dark mode keeps the (light) PNG readable inside a surface frame.
 */
import { expect, test } from '@playwright/test'

test.describe('UI-08 Jiayi Jing page', () => {
  test('renders the flagship heading and the lineage PNG', async ({ page }) => {
    await page.goto('/jiayi')
    await expect(page.getByRole('heading', { name: '《针灸甲乙经》' })).toBeVisible()
    const img = page.getByAltText(/版本及各版本之间脉络联系/)
    await expect(img).toBeVisible()
    await expect(page.getByRole('button', { name: '查看大图' })).toBeVisible()
  })

  test('keyboard: Enter opens enlarge dialog, Escape closes, focus returns', async ({ page }) => {
    await page.goto('/jiayi')
    const enlarge = page.getByRole('button', { name: '查看大图' })
    await enlarge.focus()
    await page.keyboard.press('Enter')
    await expect(page.getByRole('dialog')).toBeVisible()
    await expect(page.getByRole('dialog').getByRole('heading')).toBeVisible()
    await page.keyboard.press('Escape')
    await expect(page.getByRole('dialog')).toBeHidden()
    await expect(enlarge).toBeFocused()
  })

  test('375px renders without horizontal overflow (editions degrade to list)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    await page.goto('/jiayi')
    await expect(page.getByRole('heading', { name: '《针灸甲乙经》' })).toBeVisible()
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow).toBeLessThanOrEqual(0)
  })

  test('dark mode keeps the light lineage PNG readable', async ({ page }) => {
    await page.goto('/jiayi')
    await page.evaluate(() => document.documentElement.classList.add('dark'))
    const img = page.getByAltText(/版本及各版本之间脉络联系/)
    await expect(img).toBeVisible()
    // PNG is NOT inverted via filter in dark mode.
    const filter = await img.evaluate((el) => getComputedStyle(el).filter)
    expect(filter).toBe('none')
  })
})
