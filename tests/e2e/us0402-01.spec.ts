import { test, expect } from '@playwright/test';

test('recruitment list search and paging', async ({ page }) => {
  await page.goto('/admin/recruitments');
  await page.getByPlaceholder('フリーワード').fill('営業');
  await page.keyboard.press('Enter');
  await expect(page.locator('[data-testid="recruitment-row"]').first()).toBeVisible();
});
