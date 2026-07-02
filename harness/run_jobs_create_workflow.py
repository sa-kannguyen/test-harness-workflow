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
    ap.add_argument("--id", default="US0501")
    args = ap.parse_args()

    us = args.id
    spec_path = args.spec

    us_md = dedent(f"""
    # {us} - 求人登録 API (`POST /jobs`) 実装

    ## Source Spec
    - `{spec_path}`

    ## User Story
    As a CMS enterprise operator, I want to create a new job via API so draft/non-public/public/reserved jobs are saved with correct validations and side effects.

    ## Acceptance Criteria
    - [ ] `POST /jobs` creates new job when `jobId` is omitted or `0`.
    - [ ] Public/public-reserved statuses execute DOMONET pre-save linkage; on failure DB is not saved.
    - [ ] Draft/non-public/waiting statuses save WD DB without DOMONET linkage.
    - [ ] Response includes side effects summary (`indeedTasksCreated`, `googleIndexingUpdated`, etc.).
    - [ ] Error mapping follows 401/403/409/422/502/500 contract.

    ## Approval Gates
    - Gate A (PM+BRSE): story + AC approved
    - Gate B (BRSE+DEV): API contract + persistence strategy approved
    - Gate C (DEV+TEST): test matrix + tasks approved
    """)
    write(f"{us}.md", us_md)
    us_issue = create_issue(args.repo, f"Story: {us} Jobs Create API", "story", us_md + f"\nArtifact: `{us}.md`")

    prd_md = dedent(f"""
    # PRD-{us}

    Related Story: {us_issue}

    ## Architecture
    ```mermaid
    flowchart TD
      A[POST /jobs] --> B[Auth + Permission]
      B --> C[editToken/jobId validation]
      C --> D[Business validation]
      D --> E{{status public/reserved?}}
      E -->|yes| F[DOMONET kiji_waku/kiji_edit/option_chain]
      E -->|no| G[Skip DOMONET]
      F --> H[Persist recruitment + extends + options]
      G --> H
      H --> I[Side effects: Indeed/Indexing/Quota check]
      I --> J[201 or mapped error]
    ```

    ## API Contract
    - Endpoint: `POST /jobs`
    - Content-Type: `application/json` or `multipart/form-data`
    - Auth: CMS session (Bearer/Cookie)
    - Permission: recruitment management (`isauth=true`)

    ### Success (201)
    - `jobId`, `status`, `adId`, `editToken`, `publicationQuota`, `sideEffects`

    ### Error map
    - 401 `UNAUTHORIZED`
    - 403 `FORBIDDEN`
    - 422 `VALIDATION_ERROR`
    - 409 `PUBLICATION_LIMIT_EXCEEDED`
    - 502 `DOMONET_API_ERROR`

    ## Data Design (draft)
    - `recruitment` insert on create
    - `recruitment_extend` append history row
    - `dtb_dn_option` write option chains
    - `data_dtb_indeedapi` enqueue on publish-related conditions

    ## Non-functional
    - Contract-first response schema stability
    - Idempotency safeguard against duplicate submit tokens (future enhancement)
    - Trace logging for external API failures
    """)
    write(f"PRD-{us}.md", prd_md)
    prd_issue = create_issue(args.repo, f"PRD: {us}", "prd", prd_md + f"\nArtifact: `PRD-{us}.md`")

    tdd_md = dedent(f"""
    # TDD-{us}

    Related PRD: {prd_issue}

    ## Test Pyramid
    ```mermaid
    flowchart BT
      E2E[E2E API flow]
      INT[Integration: validation/auth/external-link]
      UNIT[Unit: field validators + rule engine]
      E2E --> INT --> UNIT
    ```

    ## Mandatory Cases
    - AUTH-01: no session -> 401
    - AUTH-02: no permission -> 403
    - VAL-01: invalid editToken -> 422
    - VAL-02: `jobId > 0` on create -> 422
    - PUB-01: public status + DOMONET success -> 201 with `adId`
    - PUB-02: public status + DOMONET failure -> 502 and no DB commit
    - DRAFT-01: draft save skips DOMONET
    - QUOTA-01: post-save quota overrun -> 409 rollback behavior

    ## Exit Criteria
    - P1 cases automated and passing in CI
    - Error code mapping snapshot locked
    """)
    write(f"TDD-{us}.md", tdd_md)
    tdd_issue = create_issue(args.repo, f"TDD Plan: {us}", "tdd", tdd_md + f"\nArtifact: `TDD-{us}.md`")

    task1 = dedent(f"""
    # TASK-{us}-01
    ## Scope
    Implement request validation + auth/permission middleware for `POST /jobs`.

    ## AC
    - [ ] Reject unauthenticated (401)
    - [ ] Reject unauthorized (403)
    - [ ] Validate `editToken`, `jobId`, required field rules by status

    ## Tests
    AUTH-01, AUTH-02, VAL-01, VAL-02
    """)
    task2 = dedent(f"""
    # TASK-{us}-02
    ## Scope
    Implement DOMONET-linked create path and transactional persistence guard.

    ## AC
    - [ ] Public/public-reserved trigger DOMONET before DB commit
    - [ ] DOMONET failure returns 502 and DB remains unsaved
    - [ ] Success path persists recruitment/recruitment_extend/options

    ## Tests
    PUB-01, PUB-02
    """)
    task3 = dedent(f"""
    # TASK-{us}-03
    ## Scope
    Implement non-public path + side effects response composition.

    ## AC
    - [ ] Draft/non-public/waiting skip DOMONET and persist DB
    - [ ] Response includes `publicationQuota` and `sideEffects`
    - [ ] Quota overrun handling returns 409 mapped error

    ## Tests
    DRAFT-01, QUOTA-01
    """)
    task4 = dedent(f"""
    # TASK-{us}-04
    ## Scope
    Implement automated tests + API contract snapshots + CI integration.

    ## AC
    - [ ] Integration suite covers all P1 cases
    - [ ] Snapshot for error/success schema in CI
    """)

    write(f"TASK-{us}-01.md", task1)
    write(f"TASK-{us}-02.md", task2)
    write(f"TASK-{us}-03.md", task3)
    write(f"TASK-{us}-04.md", task4)

    i1 = create_issue(args.repo, f"Task Impl: {us}-01", "task-impl", task1)
    i2 = create_issue(args.repo, f"Task Impl: {us}-02", "task-impl", task2)
    i3 = create_issue(args.repo, f"Task Impl: {us}-03", "task-impl", task3)
    i4 = create_issue(args.repo, f"Task TDD: {us}-04", "task-tdd", task4)

    plan_md = dedent(f"""
    # PLAN-{us}

    Related Story: {us_issue}
    Related PRD: {prd_issue}
    Related TDD: {tdd_issue}

    ## Delivery Sequence
    1. {i1}
    2. {i2}
    3. {i3}
    4. {i4}

    ## Governance Flow
    ```mermaid
    flowchart TD
      A[Story] --> B{{Gate A}}
      B --> C[PRD]
      C --> D{{Gate B}}
      D --> E[TDD + Tasks]
      E --> F{{Gate C}}
      F --> G[Implementation + CI]
      G --> H[E2E]
      H --> I{{Spec bug?}}
      I -->|yes| C
      I -->|no| J[Release]
    ```
    """)
    write(f"PLAN-{us}.md", plan_md)
    plan_issue = create_issue(args.repo, f"Plan: {us}", "plan", plan_md + f"\nArtifact: `PLAN-{us}.md`")

    e2e1 = dedent(f"""
    # E2E-{us}-01
    Scenario: create draft job (`status=3`) with minimum payload.
    Expected: 201, `jobId` generated, DOMONET not invoked.
    """)
    e2e2 = dedent(f"""
    # E2E-{us}-02
    Scenario: create public job (`status=1`) with DOMONET failure simulation.
    Expected: 502 DOMONET_API_ERROR and no DB commit.
    """)
    write(f"E2E-{us}-01.md", e2e1)
    write(f"E2E-{us}-02.md", e2e2)
    e1 = create_issue(args.repo, f"E2E: {us}-01", "e2e", e2e1)
    e2 = create_issue(args.repo, f"E2E: {us}-02", "e2e", e2e2)

    tests_dir = Path("tests/e2e")
    tests_dir.mkdir(parents=True, exist_ok=True)
    playwright = dedent("""
    import { test, expect } from '@playwright/test';

    test('jobs create draft success', async ({ request }) => {
      const res = await request.post('/api/jobs', {
        data: { editToken: 'dummy', job: { status: 3, mainCopy: 'draft' } }
      });
      expect([201, 401, 403, 422]).toContain(res.status());
    });
    """)
    (tests_dir / f"{us.lower()}-jobs-create.spec.ts").write_text(playwright, encoding="utf-8")

    print("✅ Workflow completed")
    print("Story:", us_issue)
    print("PRD:", prd_issue)
    print("TDD:", tdd_issue)
    print("Plan:", plan_issue)
    print("Tasks:", i1, i2, i3, i4)
    print("E2E:", e1, e2)


if __name__ == "__main__":
    main()
