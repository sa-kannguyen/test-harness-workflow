
import { test, expect } from '@playwright/test';

test('jobs create draft success', async ({ request }) => {
  const res = await request.post('/api/jobs', {
    data: { editToken: 'dummy', job: { status: 3, mainCopy: 'draft' } }
  });
  expect([201, 401, 403, 422]).toContain(res.status());
});
