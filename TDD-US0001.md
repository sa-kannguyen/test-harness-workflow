# TDD-US0001

Related PRD: [PRD-US0001.md](https://github.com/sa-kannguyen/test-harness-workflow/issues/4)

## Test Plan
1. Unit: task service creates task with valid title.
2. Unit: empty title returns validation error.
3. API: authenticated create returns 201 and task payload.
4. API: unauthenticated create returns 401.
5. Regression: new task prepends in dashboard list.
