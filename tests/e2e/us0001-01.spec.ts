import { test, expect } from '@playwright/test';

test('quick add task success', async ({ page }) => {
  await page.goto('/dashboard');
  await page.getByPlaceholder('Add a task').fill('Buy milk');
  await page.keyboard.press('Enter');
  await expect(page.locator('[data-testid="task-item"]').first()).toContainText('Buy milk');
});
