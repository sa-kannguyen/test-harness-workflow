#!/usr/bin/env python3
import argparse
import subprocess
from pathlib import Path
from textwrap import dedent


def run(cmd):
    return subprocess.run(cmd, text=True, capture_output=True, check=True)


def ensure_label(repo: str, label: str):
    subprocess.run([
        "gh", "label", "create", label,
        "--repo", repo,
        "--color", "1D76DB",
        "--description", f"Auto label: {label}",
    ], text=True, capture_output=True)


def create_issue(repo: str, title: str, label: str, body: str) -> str:
    ensure_label(repo, label)
    cp = run([
        "gh", "issue", "create",
        "--repo", repo,
        "--title", title,
        "--label", label,
        "--body", body,
    ])
    return cp.stdout.strip()


def write(path: str, content: str):
    Path(path).write_text(content.strip() + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--spec", required=True)
    ap.add_argument("--id", default="US0502")
    args = ap.parse_args()

    us = args.id
    spec = args.spec

    us_md = dedent(f"""
    # {us} - アカウント検索・一覧 画面リプレイス

    ## Source Spec
    - `{spec}`

    ## User Story
    As an AT internal operator with account-search permission, I want to search and view account list with filters, paging/sort, and CSV export so I can quickly inspect and operate account status.

    ## Acceptance Criteria
    - [ ] Auth + permission control matches legacy behavior.
    - [ ] Search criteria, paging, and sorting return expected results consistently.
    - [ ] CSV export types (`normal`, `_report`, `_order`) work with current search context.
    - [ ] Ajax error and session-expired handling follow defined UI behavior.
    - [ ] Sub-account include/exclude rules are preserved.

    ## Approval Gates
    - Gate A: PM+BRSE approve business behavior and AC
    - Gate B: BRSE+DEV approve API/Query/data mapping strategy
    - Gate C: DEV+TEST approve test matrix and task readiness
    """)
    write(f"{us}.md", us_md)
    us_issue = create_issue(args.repo, f"Story: {us} Account Search/List Screen", "story", us_md)

    prd_md = dedent(f"""
    # PRD-{us}

    Related Story: {us_issue}

    ## Architecture Flow
    ```mermaid
    flowchart TD
      A[Account List Page] --> B[Search Query Build]
      B --> C[Account Search API]
      C --> D[(Company/LoginUser DB)]
      A --> E[Ajax Paging/Sorting]
      A --> F[CSV Export Trigger]
      F --> G[CSV Service normal/report/order]
    ```

    ## Backend Design
    - Endpoint 1: `GET /at-manage/accounts` (initial render or API mode)
    - Endpoint 2: `POST /at-manage/accounts/search` (`output_type=json`) for ajax list updates
    - Endpoint 3: `POST /at-manage/accounts/export` (`csv_type: normal|_report|_order`)
    - Endpoint 4: `GET /at-manage/getbusho` for department-member linkage

    ## Auth/Permission
    - Require `atid > 0`
    - Require account-search permission (function id 2)
    - Unauthorized redirect/403 behavior by endpoint type

    ## Frontend Design
    - Components:
      - `AccountSearchForm`
      - `AccountTable`
      - `PagerControl`
      - `CsvActionPanel`
    - Preserve `searchkey` behavior for ajax paging/sort

    ## Data/Rule Notes
    - Keep status='指定なし(3)' logic as no-status-filter
    - Keep sub-account inclusion toggle (`sub=1`)
    - Keep manager-only page size option (all records)
    """)
    write(f"PRD-{us}.md", prd_md)
    prd_issue = create_issue(args.repo, f"PRD: {us}", "prd", prd_md)

    tdd_md = dedent(f"""
    # TDD-{us}

    Related PRD: {prd_issue}

    ## Test Pyramid
    ```mermaid
    flowchart BT
      E2E[E2E: list + csv + ajax behavior]
      INT[Integration: search filter + permission + export]
      UNIT[Unit: query parser + mapper + validator]
      E2E --> INT --> UNIT
    ```

    ## Mandatory Cases
    - AUTH-01: unauthenticated -> redirect/login behavior
    - AUTH-02: no permission -> menu redirect/forbidden behavior
    - SRCH-01: multi-condition filter returns expected rows
    - SRCH-02: paging + sort with `searchkey` consistency
    - CSV-01: normal CSV export success
    - CSV-02: report CSV export success
    - CSV-03: order CSV export gated by environment flag
    - AJAX-01: ajax failure shows "検索結果エラー"

    ## Exit Criteria
    - P1 cases automated or scriptable and pass
    - CSV download behavior verified with cookie/download restore flow
    """)
    write(f"TDD-{us}.md", tdd_md)
    tdd_issue = create_issue(args.repo, f"TDD Plan: {us}", "tdd", tdd_md)

    task1_md = dedent(f"""
    # TASK-{us}-01
    Implement auth/permission + search query handling for account list.

    ## AC
    - [ ] Auth and permission behavior aligned with spec
    - [ ] Search filters mapped correctly (date/status/plan/flags/etc.)
    - [ ] `searchkey` serialization is stable
    """)
    task2_md = dedent(f"""
    # TASK-{us}-02
    Implement ajax paging/sorting endpoint and response contract (`result/html/allcount`).

    ## AC
    - [ ] Ajax search updates rows and pager correctly
    - [ ] Session-expired/error paths return controlled behavior
    - [ ] Sort/paging stable across repeated operations
    """)
    task3_md = dedent(f"""
    # TASK-{us}-03
    Implement CSV export paths (normal/report/order) and front-end trigger flow.

    ## AC
    - [ ] CSV exports include current search conditions
    - [ ] `_report` and `_order` branch behavior correct
    - [ ] Download completion restores button state
    """)
    task4_md = dedent(f"""
    # TASK-{us}-04
    Implement test automation/integration checks for search, ajax, and csv contracts.

    ## AC
    - [ ] Core TDD cases covered in CI or regression scripts
    - [ ] Contract snapshots for ajax and csv request params
    """)

    write(f"TASK-{us}-01.md", task1_md)
    write(f"TASK-{us}-02.md", task2_md)
    write(f"TASK-{us}-03.md", task3_md)
    write(f"TASK-{us}-04.md", task4_md)

    i1 = create_issue(args.repo, f"Task Impl: {us}-01", "task-impl", task1_md)
    i2 = create_issue(args.repo, f"Task Impl: {us}-02", "task-impl", task2_md)
    i3 = create_issue(args.repo, f"Task Impl: {us}-03", "task-impl", task3_md)
    i4 = create_issue(args.repo, f"Task TDD: {us}-04", "task-tdd", task4_md)

    plan_md = dedent(f"""
    # PLAN-{us}

    Related Story: {us_issue}
    Related PRD: {prd_issue}
    Related TDD: {tdd_issue}

    ## Task Sequence
    1. {i1}
    2. {i2}
    3. {i3}
    4. {i4}

    ## Governance
    ```mermaid
    flowchart TD
      A[Story] --> GA{{Gate A}}
      GA --> B[PRD]
      B --> GB{{Gate B}}
      GB --> C[TDD + Tasks]
      C --> GC{{Gate C}}
      GC --> D[Implementation]
      D --> E[Review + CI]
      E --> F[E2E]
      F --> G[Release]
    ```
    """)
    write(f"PLAN-{us}.md", plan_md)
    plan_issue = create_issue(args.repo, f"Plan: {us}", "plan", plan_md)

    e2e1_md = dedent(f"""
    # E2E-{us}-01
    Scenario: user runs account search with multiple filters and paginates/sorts.
    Expected: result rows + allcount + pager remain consistent.
    """)
    e2e2_md = dedent(f"""
    # E2E-{us}-02
    Scenario: user exports CSV from current filtered results.
    Expected: correct CSV type generated and download flow completes.
    """)
    write(f"E2E-{us}-01.md", e2e1_md)
    write(f"E2E-{us}-02.md", e2e2_md)
    e1 = create_issue(args.repo, f"E2E: {us}-01", "e2e", e2e1_md)
    e2 = create_issue(args.repo, f"E2E: {us}-02", "e2e", e2e2_md)

    tests_dir = Path("tests/e2e")
    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / f"{us.lower()}-account-list.spec.ts").write_text(
        dedent("""
        import { test, expect } from '@playwright/test';

        test('account list search smoke', async ({ page }) => {
          await page.goto('/at-manage/account.php');
          await page.getByRole('button', { name: '上記条件で検索' }).click();
          await expect(page.locator('#results')).toBeVisible();
        });
        """),
        encoding="utf-8",
    )

    print("✅ Workflow completed")
    print("Story:", us_issue)
    print("PRD:", prd_issue)
    print("TDD:", tdd_issue)
    print("Plan:", plan_issue)
    print("Tasks:", i1, i2, i3, i4)
    print("E2E:", e1, e2)


if __name__ == "__main__":
    main()
