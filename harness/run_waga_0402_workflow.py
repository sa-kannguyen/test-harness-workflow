#!/usr/bin/env python3
import subprocess
from pathlib import Path

REPO = "sa-kannguyen/test-harness-workflow"
US_ID = "US0402"


def run(cmd):
    return subprocess.run(cmd, text=True, capture_output=True, check=True)


def ensure_label(label):
    subprocess.run([
        "gh", "label", "create", label,
        "--repo", REPO,
        "--color", "1D76DB",
        "--description", f"Auto label: {label}",
    ], text=True, capture_output=True)


def issue(title, label, body):
    ensure_label(label)
    cp = run([
        "gh", "issue", "create",
        "--repo", REPO,
        "--title", title,
        "--label", label,
        "--body", body,
    ])
    return cp.stdout.strip()


def write(name, content):
    Path(name).write_text(content, encoding="utf-8")


def main():
    us = f"""# {US_ID} - Recruitments List Screen Replace Baseline

## Source Spec
- `/Users/dong.nguyen.02/projects/wagasha-de-domo/案件相談/04-02_画面仕様書.md`
- Scope: 求人情報一覧（旧 `/admin/recruitment/`）

## User Story
As a logged-in enterprise operator with recruitment permission, I want to search/browse/manage recruitment rows from one list screen so I can perform daily operation (filtering, bulk status updates, and CSV export) safely.

## Acceptance Criteria
- [ ] Only authenticated and authorized users can access list screen; unauthorized users are redirected.
- [ ] Search + paging + sorting work and return row HTML/data consistently.
- [ ] Bulk operations support public/nonpublic/draft/waiting/reservation/delete with per-row result handling.
- [ ] CSV export uses current search condition.
- [ ] Error/force/haishi list variants are switchable and hide disallowed actions.
- [ ] Ajax unauthenticated response is controlled (`result:false`) and UI shows guided handling.

## Out of Scope
- New UX redesign
- Legacy behavior parity beyond documented scope
- Other screens outside recruitment list flow
"""
    write(f"{US_ID}.md", us)
    us_issue = issue(f"Story: {US_ID} Recruitment List Replace", "story", us + f"\n\nArtifact: `{US_ID}.md`")

    prd = f"""# PRD-{US_ID}

Related Story: {us_issue}

## 1) Database Design (Prisma draft)
```prisma
model Recruitment {{
  id              String   @id @default(cuid())
  companyId       String
  title           String
  status          Int      // 1,2,3,4,5,7
  updatedAt       DateTime @updatedAt
  createdAt       DateTime @default(now())
}}

model RecruitmentBulkJob {{
  id              String   @id @default(cuid())
  companyId       String
  operationType   String   // public_all/nonpublic_all/.../delete_all
  totalCount      Int
  successCount    Int      @default(0)
  skippedCount    Int      @default(0)
  failedCount     Int      @default(0)
  status          String   @default("queued")
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
}}
```

## 2) Backend API Design
- `GET /api/admin/recruitments` : search/paging/sort/list variant (`kind`)
- `POST /api/admin/recruitments/bulk` : start bulk operation (or sync processing for MVP)
- `GET /api/admin/recruitments/bulk/{{jobId}}` : operation result summary
- `POST /api/admin/recruitments/csv` : export CSV from current condition

### Controller/Service
- Controller: validate params, auth context, dispatch service
- Service: search composition, bulk op eligibility checks, row-level result mapping
- Legacy parity points: status rules, token checks, lock checks, errorcode mapping

### Authentication/Authorization
- Require logged-in admin session
- Require recruitment permission (`person` feature id=1 equivalent)
- Return 401/403/redirect behavior aligned by endpoint type (page vs ajax)

## 3) Frontend API Design
- Page: `AdminRecruitmentListPage`
- Components:
  - `RecruitmentSearchForm`
  - `RecruitmentTable`
  - `BulkOperationPanel`
  - `BulkResultDialog/ResultPage`
- Client behavior:
  - Preserve search state
  - Async list update for paging/sort
  - Guarded dialogs for destructive actions

## 4) Middleware Integration
- Auth middleware
- Role permission middleware
- Request validation middleware
- CSRF/session protection for bulk operations

## 5) Trace
- Story artifact: `{US_ID}.md`
- Story ticket: {us_issue}
"""
    write(f"PRD-{US_ID}.md", prd)
    prd_issue = issue(f"PRD: {US_ID}", "prd", prd + f"\n\nArtifact: `PRD-{US_ID}.md`")

    tdd = f"""# TDD-{US_ID}

Related PRD ticket: {prd_issue}

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
"""
    write(f"TDD-{US_ID}.md", tdd)
    tdd_issue = issue(f"TDD Plan: {US_ID}", "tdd", tdd + f"\n\nArtifact: `TDD-{US_ID}.md`")

    task1 = """# TASK-US0402-01
Implement recruitment list query API (`GET /api/admin/recruitments`) with filter/paging/sort/kind.
Done when: endpoint returns stable schema and auth/permission checks pass.
"""
    task2 = """# TASK-US0402-02
Implement bulk operation API (`POST /api/admin/recruitments/bulk`) + result endpoint.
Done when: supports mapped operation types and row-level result summary.
"""
    task3 = """# TASK-US0402-03
Implement frontend list page and bulk operation panel integration.
Done when: search/paging/sort and bulk action UX works against new APIs.
"""
    task4 = """# TASK-US0402-04
Implement automated tests from TDD (API integration + E2E smoke).
Done when: CI passes selected coverage gates.
"""
    write("TASK-US0402-01.md", task1)
    write("TASK-US0402-02.md", task2)
    write("TASK-US0402-03.md", task3)
    write("TASK-US0402-04.md", task4)

    i1 = issue("Task Impl: US0402-01", "task-impl", task1)
    i2 = issue("Task Impl: US0402-02", "task-impl", task2)
    i3 = issue("Task Impl: US0402-03", "task-impl", task3)
    i4 = issue("Task TDD: US0402-04", "task-tdd", task4)

    plan = f"""# PLAN-{US_ID}

Related PRD: {prd_issue}
Related TDD: {tdd_issue}

## Task Order
1. [TASK-US0402-01]({i1})
2. [TASK-US0402-02]({i2})
3. [TASK-US0402-03]({i3})
4. [TASK-US0402-04]({i4})

## Artifacts
- `TASK-US0402-01.md`
- `TASK-US0402-02.md`
- `TASK-US0402-03.md`
- `TASK-US0402-04.md`
"""
    write(f"PLAN-{US_ID}.md", plan)
    plan_issue = issue(f"Plan: {US_ID}", "plan", plan + f"\n\nArtifact: `PLAN-{US_ID}.md`")

    e2e1 = f"""# E2E-{US_ID}-01
Scenario: authorized user filters recruitment list and sees expected rows with paging.
Precondition: user has recruitment permission.
Expected: search/paging/sort update list correctly.
Related PRD: {prd_issue}
"""
    e2e2 = f"""# E2E-{US_ID}-02
Scenario: bulk publish on selected rows with mixed eligibility.
Expected: success/skipped/failed counts are shown and traceable.
Related PRD: {prd_issue}
"""
    write(f"E2E-{US_ID}-01.md", e2e1)
    write(f"E2E-{US_ID}-02.md", e2e2)
    e1 = issue(f"E2E: {US_ID}-01", "e2e", e2e1)
    e2 = issue(f"E2E: {US_ID}-02", "e2e", e2e2)

    tests_dir = Path("tests/e2e")
    tests_dir.mkdir(parents=True, exist_ok=True)
    test_code = """import { test, expect } from '@playwright/test';

test('recruitment list search and paging', async ({ page }) => {
  await page.goto('/admin/recruitments');
  await page.getByPlaceholder('フリーワード').fill('営業');
  await page.keyboard.press('Enter');
  await expect(page.locator('[data-testid="recruitment-row"]').first()).toBeVisible();
});
"""
    (tests_dir / "us0402-01.spec.ts").write_text(test_code, encoding="utf-8")

    print("✅ Created workflow for 04-02_画面仕様書.md")
    print("Story:", us_issue)
    print("PRD:", prd_issue)
    print("TDD:", tdd_issue)
    print("Plan:", plan_issue)
    print("Tasks:", i1, i2, i3, i4)
    print("E2E:", e1, e2)


if __name__ == "__main__":
    main()
