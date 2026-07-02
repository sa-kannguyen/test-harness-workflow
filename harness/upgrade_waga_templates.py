#!/usr/bin/env python3
from pathlib import Path
import subprocess

REPO = "sa-kannguyen/test-harness-workflow"
US = "US0402"
ISSUES = {
    "story": 13,
    "prd": 14,
    "tdd": 15,
    "task1": 16,
    "task2": 17,
    "task3": 18,
    "task4": 19,
    "plan": 20,
    "e2e1": 21,
    "e2e2": 22,
}


def run(cmd):
    return subprocess.run(cmd, text=True, capture_output=True, check=True)


def write(path, content):
    Path(path).write_text(content.strip() + "\n", encoding="utf-8")


def issue_url(n):
    return f"https://github.com/{REPO}/issues/{n}"


def update_issue(n, title, label, md_file):
    run([
        "gh", "issue", "edit", str(n),
        "--repo", REPO,
        "--title", title,
        "--add-label", label,
        "--body-file", md_file,
    ])


def main():
    story = f"""
# {US} - 求人情報一覧（Recruitment List）Replace Story

## 1) Scope Summary
- **Source spec**: `/Users/dong.nguyen.02/projects/wagasha-de-domo/案件相談/04-02_画面仕様書.md`
- **Target**: Legacy `/admin/recruitment/` flow replacement baseline
- **Primary users**: 企業担当者 with recruitment permission

## 2) User Story
As an authenticated enterprise operator, I want to search and manage recruitment rows from one screen so I can complete daily operations (search, bulk updates, export) safely and quickly.

## 3) Business Value
- Reduce operation error from legacy mixed behavior
- Keep migration traceability by explicit parity checklist
- Create a safe baseline for future async bulk-job architecture

## 4) Acceptance Criteria (AC)
- [ ] AC-01 Authenticated + authorized users can access; unauthorized are redirected/blocked.
- [ ] AC-02 Search + paging + sort return expected records and stable response schema.
- [ ] AC-03 `kind` variant (`error/force/haishi`) switches list mode and UI action constraints.
- [ ] AC-04 Bulk operations support defined operation types with per-row success/skip/fail results.
- [ ] AC-05 CSV export reflects active search condition.
- [ ] AC-06 Ajax unauthenticated path returns controlled payload and UI guidance.

## 5) Out of Scope
- New UI redesign
- Cross-screen feature expansion
- Deep refactor of all legacy downstream modules

## 6) Flow Diagram
```mermaid
flowchart LR
A[Read Screen Spec] --> B[Define Story + AC]
B --> C[PRD]
C --> D[TDD]
D --> E[Task Breakdown]
E --> F[Implementation]
F --> G[E2E Validation]
```

## 7) Links
- PRD: {issue_url(ISSUES['prd'])}
- TDD: {issue_url(ISSUES['tdd'])}
- Plan: {issue_url(ISSUES['plan'])}
"""

    prd = f"""
# PRD-{US} - Recruitment List Replacement

Related Story: {issue_url(ISSUES['story'])}

## 1) Architecture Scope

```mermaid
flowchart TD
UI[AdminRecruitmentListPage] --> API1[GET /api/admin/recruitments]
UI --> API2[POST /api/admin/recruitments/bulk]
UI --> API3[GET /api/admin/recruitments/bulk/{{jobId}}]
UI --> API4[POST /api/admin/recruitments/csv]
API1 --> SVC[RecruitmentService]
API2 --> SVC
API3 --> JOB[BulkJobService]
SVC --> DB[(Recruitment DB)]
JOB --> DB
API2 --> EXT[DOMONET API Adapter]
```

## 2) Data Design (Prisma Draft)
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
  operationType   String
  totalCount      Int
  successCount    Int      @default(0)
  skippedCount    Int      @default(0)
  failedCount     Int      @default(0)
  status          String   @default("queued")
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
}}
```

## 3) API Contracts

### 3.1 GET /api/admin/recruitments
- Query: `page,size,sortBy,sortOrder,kind,keyword,status[]`
- 200 Response:
```json
{{
  "result": true,
  "allCount": 120,
  "page": 1,
  "size": 20,
  "rows": [{{"id":"r1","title":"...","status":1,"updatedAt":"..."}}]
}}
```

### 3.2 POST /api/admin/recruitments/bulk
- Request:
```json
{{"operationType":"public_all","targetIds":["r1","r2"],"csrfToken":"..."}}
```
- Response:
```json
{{"result":true,"jobId":"bj_001","accepted":2}}
```

### 3.3 GET /api/admin/recruitments/bulk/{{jobId}}
- Response includes `successCount/skippedCount/failedCount` and per-row errors.

### 3.4 POST /api/admin/recruitments/csv
- Uses same search payload; returns download token/stream.

## 4) Auth & Permission
- Require admin session
- Require recruitment permission
- Page path: redirect policy
- API path: 401/403 JSON policy

## 5) Frontend Spec
- Components:
  - `RecruitmentSearchForm`
  - `RecruitmentTable`
  - `BulkOperationPanel`
  - `BulkResultSummary`
- Behavior:
  - Keep search state after paging
  - Disable invalid actions by list variant

## 6) NFR
- P95 search response < 800ms (20 rows)
- Bulk start response < 500ms
- Error observability with correlation id

## 7) Traceability
- TDD: {issue_url(ISSUES['tdd'])}
- Plan: {issue_url(ISSUES['plan'])}
"""

    tdd = f"""
# TDD-{US} - Test Design Document

Related PRD: {issue_url(ISSUES['prd'])}

## 1) Test Pyramid
```mermaid
flowchart BT
E2E[E2E: search + bulk happy/edge]
INT[Integration: API contracts + auth + status rules]
UNIT[Unit: validators, permission checks, mapping]
E2E --> INT --> UNIT
```

## 2) Coverage Matrix
| Area | Case ID | Scenario | Expected |
|---|---|---|---|
| Auth | AUTH-01 | API call without session | 401 JSON |
| Permission | AUTH-02 | Session without recruitment permission | 403 JSON |
| Search | SRCH-01 | keyword + status filter | matching rows |
| Paging | SRCH-02 | page/size boundary | stable allCount + page rows |
| Variant | SRCH-03 | `kind=error` | disallowed actions hidden |
| Bulk | BULK-01 | valid `public_all` | success increments |
| Bulk | BULK-02 | lock conflict | errorcode 970/980 |
| Bulk | BULK-03 | csrf mismatch | errorcode 990 |
| CSV | CSV-01 | export with active filters | output matches filter |

## 3) Mandatory Automation
- API integration: AUTH-01/02, SRCH-01/02, BULK-01/02/03
- E2E smoke: search flow + bulk flow + summary rendering

## 4) Exit Criteria
- All P1 test cases pass
- No critical regression on legacy parity checkpoints
- CI green for API + E2E smoke suite
"""

    plan = f"""
# PLAN-{US} - Execution Plan

Related Story: {issue_url(ISSUES['story'])}
Related PRD: {issue_url(ISSUES['prd'])}
Related TDD: {issue_url(ISSUES['tdd'])}

## 1) Delivery Sequence
```mermaid
gantt
  title US0402 Implementation Plan
  dateFormat  YYYY-MM-DD
  section Backend
  Task-01 API List         :a1, 2026-07-03, 2d
  Task-02 Bulk API         :a2, after a1, 2d
  section Frontend
  Task-03 List/Bulk UI     :a3, after a2, 2d
  section QA
  Task-04 Test Automation  :a4, after a3, 2d
```

## 2) Task Links
1. TASK-US0402-01: {issue_url(ISSUES['task1'])}
2. TASK-US0402-02: {issue_url(ISSUES['task2'])}
3. TASK-US0402-03: {issue_url(ISSUES['task3'])}
4. TASK-US0402-04: {issue_url(ISSUES['task4'])}

## 3) Risk Watch
- Legacy parity ambiguity around status transition exceptions
- External DOMONET coupling and retry behavior
- Permission rule drift in migration
"""

    task1 = f"""
# TASK-US0402-01 - Implement Recruitment List API

## Goal
Build `GET /api/admin/recruitments` with filter/paging/sort/variant behavior aligned to PRD.

## Scope In
- Query validation (`page,size,sortBy,sortOrder,kind,keyword,status[]`)
- Auth + permission checks
- Response mapping (`result,allCount,page,size,rows`)

## Scope Out
- Bulk operations
- CSV endpoint

## Implementation Hints
- Add module: `backend/recruitments/list.controller.ts`
- Service: `backend/recruitments/list.service.ts`
- DTO validation: zod/class-validator

## Acceptance Criteria
- [ ] Returns 200 with stable schema for valid requests
- [ ] Returns 401 when unauthenticated
- [ ] Returns 403 when no recruitment permission
- [ ] Supports `kind=error/force/haishi` filtering contract

## Test Cases
- SRCH-01, SRCH-02, SRCH-03, AUTH-01, AUTH-02

## Done Definition
- API integration tests pass
- PR links Story/PRD/TDD/Task ticket
"""

    task2 = f"""
# TASK-US0402-02 - Implement Bulk Operation APIs

## Goal
Implement `POST /api/admin/recruitments/bulk` and `GET /api/admin/recruitments/bulk/{{jobId}}`.

## Scope In
- Operation type handling: public/nonpublic/draft/waiting/reserve/delete
- Row-level result aggregation: success/skipped/failed
- CSRF/token validation and lock handling (970/980/990 mapping)

## Scope Out
- Full async distributed job system (MVP can be synchronous with job-like response)

## Acceptance Criteria
- [ ] Valid request returns jobId + accepted count
- [ ] Per-row execution result is queryable by jobId
- [ ] Token mismatch returns mapped error behavior
- [ ] Lock conflicts are captured and surfaced

## Test Cases
- BULK-01, BULK-02, BULK-03

## Done Definition
- Integration tests green
- Error mapping documented in endpoint spec comments
"""

    task3 = f"""
# TASK-US0402-03 - Implement Frontend List + Bulk UI

## Goal
Deliver list/search/paging/sort UI and bulk operation panel integrated with new APIs.

## Scope In
- Search form state + query sync
- Table rendering with variant constraints (`kind`)
- Bulk operation dialog + result summary

## Scope Out
- Visual redesign beyond migration baseline

## UI Behavior Rules
- Disable unsupported actions in variant modes
- Preserve current search state after operations
- Show clear partial-failure summary

## Acceptance Criteria
- [ ] User can search and paginate without full page reload
- [ ] Bulk operations trigger API and show result summary
- [ ] Variant mode hides prohibited actions

## Test Cases
- E2E-US0402-01, E2E-US0402-02

## Done Definition
- E2E smoke passes
- No console errors on main flow
"""

    task4 = f"""
# TASK-US0402-04 - Implement Automated Test Suite

## Goal
Convert TDD matrix into executable API integration + Playwright smoke coverage.

## Scope In
- API test suite for auth/search/bulk contracts
- Playwright cases for search flow and bulk flow summary
- CI job wiring for required checks

## Acceptance Criteria
- [ ] Mandatory cases in TDD marked automated
- [ ] CI pipeline fails on contract regression
- [ ] Test reports include failing case IDs

## Done Definition
- Test docs updated with run command and coverage note
- Green pipeline in PR
"""

    e2e1 = f"""
# E2E-{US}-01 - Search and Paging Flow

## Objective
Validate that authorized user can search recruitment rows and paginate with consistent results.

## Preconditions
- Test account with recruitment permission
- Seeded data includes keyword-hit rows and non-hit rows

## Steps
1. Login as authorized user
2. Open recruitment list page
3. Enter keyword and submit
4. Move to page 2
5. Change sort order

## Expected
- Filtered results match keyword
- `allCount` remains consistent across paging
- Rows update correctly on sort

## Trace
- Task: {issue_url(ISSUES['task3'])}
- TDD Case: SRCH-01, SRCH-02
"""

    e2e2 = f"""
# E2E-{US}-02 - Bulk Publish with Mixed Eligibility

## Objective
Validate bulk operation summary when selected rows include valid and invalid targets.

## Preconditions
- Selection includes rows with different status/lock states

## Steps
1. Login and open list page
2. Select mixed rows
3. Execute `public_all`
4. Open operation result summary

## Expected
- Success/skipped/failed counts are displayed
- Row-level errors are visible for skipped/failed records
- UI remains usable for next operation

## Trace
- Task: {issue_url(ISSUES['task3'])}, {issue_url(ISSUES['task4'])}
- TDD Case: BULK-01, BULK-02
"""

    write(f"{US}.md", story)
    write(f"PRD-{US}.md", prd)
    write(f"TDD-{US}.md", tdd)
    write(f"PLAN-{US}.md", plan)
    write("TASK-US0402-01.md", task1)
    write("TASK-US0402-02.md", task2)
    write("TASK-US0402-03.md", task3)
    write("TASK-US0402-04.md", task4)
    write(f"E2E-{US}-01.md", e2e1)
    write(f"E2E-{US}-02.md", e2e2)

    update_issue(ISSUES["story"], f"Story: {US} Recruitment List Replace", "story", f"{US}.md")
    update_issue(ISSUES["prd"], f"PRD: {US}", "prd", f"PRD-{US}.md")
    update_issue(ISSUES["tdd"], f"TDD Plan: {US}", "tdd", f"TDD-{US}.md")
    update_issue(ISSUES["plan"], f"Plan: {US}", "plan", f"PLAN-{US}.md")
    update_issue(ISSUES["task1"], "Task Impl: US0402-01", "task-impl", "TASK-US0402-01.md")
    update_issue(ISSUES["task2"], "Task Impl: US0402-02", "task-impl", "TASK-US0402-02.md")
    update_issue(ISSUES["task3"], "Task Impl: US0402-03", "task-impl", "TASK-US0402-03.md")
    update_issue(ISSUES["task4"], "Task TDD: US0402-04", "task-tdd", "TASK-US0402-04.md")
    update_issue(ISSUES["e2e1"], f"E2E: {US}-01", "e2e", f"E2E-{US}-01.md")
    update_issue(ISSUES["e2e2"], f"E2E: {US}-02", "e2e", f"E2E-{US}-02.md")

    print("✅ Upgraded markdown templates and updated issues")


if __name__ == "__main__":
    main()
