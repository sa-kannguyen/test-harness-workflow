#!/usr/bin/env python3
import argparse
import re
import subprocess
from pathlib import Path


def run(cmd, check=True):
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def ensure_label(repo: str, label: str):
    cp = run(["gh", "label", "list", "--repo", repo, "--limit", "200", "--json", "name"], check=False)
    if cp.returncode != 0:
        return
    names = {x.strip().strip('"') for x in []}
    import json
    names = {x["name"] for x in json.loads(cp.stdout or "[]")}
    if label in names:
        return
    run(["gh", "label", "create", label, "--repo", repo, "--color", "1D76DB"], check=False)


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


def write(path: Path, content: str):
    path.write_text(content, encoding="utf-8")


def to_num(url: str) -> str:
    m = re.search(r"/issues/(\d+)", url)
    return m.group(1) if m else "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--spec", default="sample-spec.md")
    ap.add_argument("--id", default="US0001")
    args = ap.parse_args()

    root = Path.cwd()
    spec_text = Path(args.spec).read_text(encoding="utf-8")
    us_id = args.id

    # 1) Story
    us_file = root / f"{us_id}.md"
    us_body = f"""# {us_id} - Quick Add Task on Dashboard

## User Story
As an authenticated user, I want to quickly add a task from dashboard so I can capture work instantly.

## Acceptance Criteria
- Quick-add input is visible on dashboard header.
- Enter valid title + Enter creates a new task.
- New task appears at top of list after success.
- Empty title shows inline validation error.
- Unauthenticated requests are rejected.

## Source
- `sample-spec.md`
"""
    write(us_file, us_body)
    us_issue = create_issue(args.repo, f"Story: {us_id} Quick Add Task", "story", us_body + f"\n\nArtifact: `{us_file.name}`")

    # 2) PRD
    prd_file = root / f"PRD-{us_id}.md"
    prd_body = f"""# PRD-{us_id}

Related Story: [{us_id}]({us_issue})

## Database Design (Prisma)
```prisma
model Task {{
  id        String   @id @default(cuid())
  title     String
  status    String   @default("todo")
  userId    String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}}
```

## Backend API Design
- **Controller**: `POST /api/tasks/quick-add`
- **Service**: validate title, persist task, return created task
- **Authentication**: require valid session/JWT

## Frontend Design
- **Page**: Dashboard
- **Component**: `QuickAddTaskInput`
- **Behavior**: submit on Enter, optimistic loading, prepend result

## Middleware Integration
- Auth middleware on API route
- Request validation middleware for title length
"""
    write(prd_file, prd_body)
    prd_issue = create_issue(args.repo, f"PRD: {us_id}", "prd", prd_body + f"\n\nArtifact: `{prd_file.name}`\nStory ticket: {us_issue}")

    # 3) TDD
    tdd_file = root / f"TDD-{us_id}.md"
    tdd_body = f"""# TDD-{us_id}

Related PRD: [{prd_file.name}]({prd_issue})

## Test Plan
1. Unit: task service creates task with valid title.
2. Unit: empty title returns validation error.
3. API: authenticated create returns 201 and task payload.
4. API: unauthenticated create returns 401.
5. Regression: new task prepends in dashboard list.
"""
    write(tdd_file, tdd_body)
    tdd_issue = create_issue(args.repo, f"TDD Plan: {us_id}", "tdd", tdd_body + f"\n\nArtifact: `{tdd_file.name}`\nPRD ticket: {prd_issue}")

    # 4) Task plan + tasks
    plan_file = root / f"PLAN-{us_id}.md"
    task1 = root / f"TASK-{us_id}-01.md"
    task2 = root / f"TASK-{us_id}-02.md"
    task3 = root / f"TASK-{us_id}-03.md"

    task1_body = f"# TASK-{us_id}-01\nImplement backend endpoint `POST /api/tasks/quick-add` with auth + validation.\n"
    task2_body = f"# TASK-{us_id}-02\nImplement `QuickAddTaskInput` on dashboard and prepend created task.\n"
    task3_body = f"# TASK-{us_id}-03\nImplement unit/API tests per `TDD-{us_id}.md`.\n"
    write(task1, task1_body)
    write(task2, task2_body)
    write(task3, task3_body)

    task1_issue = create_issue(args.repo, f"Task Impl: {us_id}-01", "task-impl", task1_body)
    task2_issue = create_issue(args.repo, f"Task Impl: {us_id}-02", "task-impl", task2_body)
    task3_issue = create_issue(args.repo, f"Task TDD: {us_id}-03", "task-tdd", task3_body)

    plan_body = f"""# PLAN-{us_id}

Related PRD: {prd_issue}
Related TDD: {tdd_issue}

## Task Order
1. [TASK-{us_id}-01]({task1_issue})
2. [TASK-{us_id}-02]({task2_issue})
3. [TASK-{us_id}-03]({task3_issue})

## Artifact Links
- `{task1.name}`
- `{task2.name}`
- `{task3.name}`
"""
    write(plan_file, plan_body)
    plan_issue = create_issue(args.repo, f"Plan: {us_id}", "plan", plan_body + f"\n\nArtifact: `{plan_file.name}`")

    # 5) E2E
    e2e1 = root / f"E2E-{us_id}-01.md"
    e2e2 = root / f"E2E-{us_id}-02.md"
    e2e1_body = f"# E2E-{us_id}-01\nScenario: authenticated user quick-adds valid task and sees it at top.\n"
    e2e2_body = f"# E2E-{us_id}-02\nScenario: empty task title shows validation error and does not create task.\n"
    write(e2e1, e2e1_body)
    write(e2e2, e2e2_body)
    e2e1_issue = create_issue(args.repo, f"E2E: {us_id}-01", "e2e", e2e1_body + f"\nPRD ticket: {prd_issue}")
    e2e2_issue = create_issue(args.repo, f"E2E: {us_id}-02", "e2e", e2e2_body + f"\nPRD ticket: {prd_issue}")

    # 6) E2E generate
    tests_dir = root / "tests" / "e2e"
    tests_dir.mkdir(parents=True, exist_ok=True)
    spec_file = tests_dir / f"{us_id.lower()}-01.spec.ts"
    spec_file.write_text(
        """import { test, expect } from '@playwright/test';

test('quick add task success', async ({ page }) => {
  await page.goto('/dashboard');
  await page.getByPlaceholder('Add a task').fill('Buy milk');
  await page.keyboard.press('Enter');
  await expect(page.locator('[data-testid="task-item"]').first()).toContainText('Buy milk');
});
""",
        encoding="utf-8",
    )

    print("✅ Workflow completed")
    print(f"Story: {us_issue}")
    print(f"PRD: {prd_issue}")
    print(f"TDD: {tdd_issue}")
    print(f"Plan: {plan_issue}")
    print(f"Task 1: {task1_issue}")
    print(f"Task 2: {task2_issue}")
    print(f"Task 3: {task3_issue}")
    print(f"E2E 1: {e2e1_issue}")
    print(f"E2E 2: {e2e2_issue}")
    print(f"Generated test: {spec_file}")


if __name__ == "__main__":
    main()
