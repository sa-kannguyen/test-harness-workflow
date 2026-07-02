#!/usr/bin/env python3
from pathlib import Path
import subprocess

REPO = "sa-kannguyen/test-harness-workflow"
MAP = {
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


def append_once(path: str, marker: str, block: str):
    p = Path(path)
    txt = p.read_text(encoding="utf-8")
    if marker in txt:
        return
    p.write_text(txt.rstrip() + "\n\n" + block.strip() + "\n", encoding="utf-8")


def issue_edit(no: int, title: str, label: str, file: str):
    run([
        "gh", "issue", "edit", str(no),
        "--repo", REPO,
        "--title", title,
        "--add-label", label,
        "--body-file", file,
    ])


def main():
    append_once(
        "US0402.md",
        "## 8) Approval Gates",
        """
## 8) Approval Gates
- **Gate A (PM + BRSE):** approve business intent and AC completeness before PRD elaboration.
- **Gate B (BRSE + DEV):** approve feasibility and API/DB/UI scope before task breakdown.
- **Gate C (DEV + TEST):** approve TDD coverage + task readiness before implementation.
""",
    )

    append_once(
        "PRD-US0402.md",
        "## 8) Release and Runtime Readiness",
        """
## 8) Release and Runtime Readiness
- PR review is mandatory with at least one reviewer.
- CI gate required: lint + unit/integration + selected E2E smoke.
- Staging sign-off required before production rollout.
- Post-release monitoring: error rate, failed bulk ops, API latency.
""",
    )

    append_once(
        "TDD-US0402.md",
        "## 5) Defect Triage Loop",
        """
## 5) Defect Triage Loop
When test fails, classify defect root first:
1. **Code defect** → fix in implementation task, keep spec unchanged.
2. **Spec/design defect** → update PRD/TDD/Task and then implement.
3. **Test defect** → fix flaky/incorrect test script and rerun.
""",
    )

    append_once(
        "PLAN-US0402.md",
        "## 4) Governance Flow",
        """
## 4) Governance Flow
```mermaid
flowchart TD
R[Requirement Input] --> S[Story + AC]
S --> GA{Gate A\nPM+BRSE}
GA -->|Pass| P[PRD Design]
GA -->|Fail| S
P --> GB{Gate B\nBRSE+DEV}
GB -->|Pass| T[TDD + Task Breakdown]
GB -->|Fail| P
T --> GC{Gate C\nDEV+TEST}
GC -->|Pass| I[Implementation + PR]
GC -->|Fail| T
I --> C[CI + Review]
C --> E[E2E + UAT]
E --> D{Defect?}
D -->|Code| I
D -->|Spec| P
D -->|No| REL[Release + Monitoring]
```
""",
    )

    append_once(
        "TASK-US0402-01.md",
        "## Estimation Rule",
        """
## Estimation Rule
Estimate only after API contract + validation rules are approved at Gate B.
""",
    )
    append_once(
        "TASK-US0402-02.md",
        "## Estimation Rule",
        """
## Estimation Rule
Estimate after error mapping and edge-case rules are reviewed with TEST.
""",
    )
    append_once(
        "TASK-US0402-03.md",
        "## Delivery Gate",
        """
## Delivery Gate
UI task is complete only after E2E smoke case references are attached in PR.
""",
    )
    append_once(
        "TASK-US0402-04.md",
        "## CI Gate",
        """
## CI Gate
Mark done only when mandatory suites are blocking checks in CI.
""",
    )

    append_once(
        "E2E-US0402-01.md",
        "## Failure Routing",
        """
## Failure Routing
- If mismatch due to API behavior, open defect against Task-01/02.
- If mismatch due to requirement ambiguity, raise spec defect and route to PRD update.
""",
    )
    append_once(
        "E2E-US0402-02.md",
        "## Failure Routing",
        """
## Failure Routing
- If summary counts mismatch, verify bulk result contract first.
- If UI state only is broken, route to Task-03.
""",
    )

    # Sync issue bodies
    issue_edit(MAP["story"], "Story: US0402 Recruitment List Replace", "story", "US0402.md")
    issue_edit(MAP["prd"], "PRD: US0402", "prd", "PRD-US0402.md")
    issue_edit(MAP["tdd"], "TDD Plan: US0402", "tdd", "TDD-US0402.md")
    issue_edit(MAP["plan"], "Plan: US0402", "plan", "PLAN-US0402.md")
    issue_edit(MAP["task1"], "Task Impl: US0402-01", "task-impl", "TASK-US0402-01.md")
    issue_edit(MAP["task2"], "Task Impl: US0402-02", "task-impl", "TASK-US0402-02.md")
    issue_edit(MAP["task3"], "Task Impl: US0402-03", "task-impl", "TASK-US0402-03.md")
    issue_edit(MAP["task4"], "Task TDD: US0402-04", "task-tdd", "TASK-US0402-04.md")
    issue_edit(MAP["e2e1"], "E2E: US0402-01", "e2e", "E2E-US0402-01.md")
    issue_edit(MAP["e2e2"], "E2E: US0402-02", "e2e", "E2E-US0402-02.md")

    print("✅ Patched flow gaps and synced issues")


if __name__ == "__main__":
    main()
