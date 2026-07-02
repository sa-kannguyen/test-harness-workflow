
import { test, expect } from '@playwright/test';

test('account list search smoke', async ({ page }) => {
  await page.goto('/at-manage/account.php');
  await page.getByRole('button', { name: '上記条件で検索' }).click();
  await expect(page.locator('#results')).toBeVisible();
});
