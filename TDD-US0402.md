# TDD-US0402

Related PRD ticket: https://github.com/sa-kannguyen/test-harness-workflow/issues/14

## Test Plan
1. Auth/permission tests (page + ajax endpoints)
2. Search filter + paging + sorting tests
3. List variant tests (`kind=error/force/haishi`)
4. Bulk operation tests:
   - valid status transitions
   - token mismatch (`990`)
   - lock error (`970/980`)
   - partial failure reporting
5. CSV export with selected conditions
6. Regression: legacy key actions (preview/duplicate links availability by variant)

## Automation Target
- API integration tests for search and bulk endpoints
- UI E2E for search -> bulk -> result flow
