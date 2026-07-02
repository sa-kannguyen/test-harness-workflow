#!/usr/bin/env python3
from pathlib import Path
import subprocess
from textwrap import dedent

REPO = "sa-kannguyen/test-harness-workflow"
ISSUES = {
    "story": 33,
    "prd": 34,
    "tdd": 35,
    "task1": 36,
    "task2": 37,
    "task3": 38,
    "task4": 39,
    "plan": 40,
    "e2e1": 41,
    "e2e2": 42,
}
US = "US0502"


def run(cmd):
    return subprocess.run(cmd, text=True, capture_output=True, check=True)


def write(path: str, content: str):
    Path(path).write_text(content.strip() + "\n", encoding="utf-8")


def issue_url(n: int) -> str:
    return f"https://github.com/{REPO}/issues/{n}"


def sync_issue(no: int, title: str, label: str, body_file: str):
    run([
        "gh", "issue", "edit", str(no),
        "--repo", REPO,
        "--title", title,
        "--add-label", label,
        "--body-file", body_file,
    ])


def main():
    story = dedent(f"""
    # {US} - リプレイス: アカウント検索・一覧（Bản tiếng Việt cho DEV)

    ## 1) Tóm tắt spec JP cho DEV
    - Màn hình gốc: `/at-manage/account.php`
    - Mục tiêu: tìm kiếm account/company, phân trang/sort, export CSV, chuyển màn hình liên quan.
    - Quyền: chỉ user AT có function ID=2 mới vào được.

    ## 2) User Story
    Là nhân sự nội bộ có quyền tra cứu account, tôi muốn lọc danh sách account theo nhiều điều kiện và xuất CSV đúng ngữ cảnh tìm kiếm để xử lý vận hành nhanh và chính xác.

    ## 3) Acceptance Criteria
    - [ ] AC-01: chưa login => redirect `/at-manage/index.php`.
    - [ ] AC-02: không có quyền function 2 => redirect `/at-manage/menu.php`.
    - [ ] AC-03: search trả đúng dữ liệu theo bộ filter đã submit.
    - [ ] AC-04: paging/sort ajax dùng `searchkey` snapshot của lần bấm search gần nhất.
    - [ ] AC-05: CSV thường/report/order xuất đúng theo filter + sort hiện tại.
    - [ ] AC-06: lỗi ajax hiển thị dòng `検索結果エラー`.

    ## 4) Approval Gates
    - Gate A (PM+BRSE): chốt hành vi business và AC.
    - Gate B (BRSE+DEV): chốt mapping filter -> query.
    - Gate C (DEV+TEST): chốt test matrix + task sẵn sàng triển khai.
    """)

    prd = dedent(f"""
    # PRD-{US} (VI) - Account Search/List Replace

    Related Story: {issue_url(ISSUES['story'])}

    ## 1) Kiến trúc xử lý
    ```mermaid
    flowchart TD
      A[UI: AccountSearchForm] --> B[POST search]
      B --> C[Search Service]
      C --> D[(company/login_user)]
      A --> E[Ajax paging/sort]
      E --> C
      A --> F[CSV button]
      F --> G[CSV service normal/report/order]
    ```

    ## 2) Backend contracts (để DEV code thẳng)

    ### 2.1 POST `/at-manage/account.php` (search full page)
    **Input chính:** `kensaku=1`, filter fields (`date_from`, `date_to`, `status`, `plan`, `kind[]`, `accountName`, ...)
    **Output:** HTML full page + list rows.

    ### 2.2 POST `/at-manage/account.php` (ajax)
    **Input:** `output_type=json`, `p,c,s,d,searchkey`
    **Output JSON:**
    ```json
    {{
      "result": true,
      "html": "<tr>...</tr>",
      "allcount": 123,
      "pngerrmsg": ""
    }}
    ```

    ### 2.3 POST `/at-manage/account.php` (csv)
    **Input:** `output_type=csv`, `csv_type` (`""|"_report"|"_order"`), filter hidden, sort params.
    **Output:** file download Shift_JIS + cookie `downloaded`.

    ### 2.4 GET `/at-manage/getbusho.php`
    **Input:** `busho`, `token`
    **Output:** member list JSON (403 nếu token sai/chưa login).

    ## 3) Mapping rule quan trọng
    - `status=3` (指定なし) => không add điều kiện status vào SQL.
    - `sub` unchecked => chỉ `is_superuser=1`.
    - Form chỉnh tay nhưng chưa bấm search: ajax vẫn dùng `searchkey` cũ.

    ## 4) NFR
    - Ajax list update < 1s với page size 20 trong dữ liệu thường.
    - CSV không double-submit (button disable + restore theo cookie).
    """)

    tdd = dedent(f"""
    # TDD-{US} (VI)

    Related PRD: {issue_url(ISSUES['prd'])}

    ## Test matrix (dev/test nhìn phát làm được)
    | ID | Loại | Case | Kết quả mong đợi |
    |---|---|---|---|
    | AUTH-01 | Integration | chưa login vào account.php | 302 -> index |
    | AUTH-02 | Integration | có login nhưng thiếu quyền function 2 | 302 -> menu |
    | SRCH-01 | Integration | filter date/status/plan/accountName | row đúng điều kiện |
    | SRCH-02 | Integration | status=3 | query không filter status |
    | AJAX-01 | Integration | output_type=json + sort/paging | trả `result/html/allcount` đúng |
    | AJAX-02 | UI | ajax fail | hiển thị `検索結果エラー` |
    | CSV-01 | Integration | csv normal | file tải về đúng cột |
    | CSV-02 | Integration | csv report | file report đúng |
    | CSV-03 | Integration | csv order (env bật) | file order đúng |
    | BUSHO-01 | Integration | token sai getbusho | 403 |

    ## Exit criteria
    - Tất cả case P1 pass (AUTH/SRCH/AJAX/CSV).
    - PR có evidence: ảnh/gif ajax + file csv mẫu.
    """)

    task1 = dedent(f"""
    # TASK-{US}-01 (Implement-ready)
    ## Mục tiêu
    Implement auth/permission + parser filter search cho account list.

    ## Scope in
    - Check session `atid > 0`
    - Check quyền function ID=2
    - Parse + sanitize filter: date/status/plan/kind/accountName/billingName/mode/flags
    - Rule `status=3` => no status where clause

    ## Scope out
    - Ajax rendering
    - CSV export

    ## Gợi ý file
    - `source/_base/at-manage/account.php`
    - `source/_base/at-manage/class/search/searchCompanyExec.php`

    ## AC
    - [ ] AUTH-01 pass
    - [ ] AUTH-02 pass
    - [ ] SRCH-01 pass
    - [ ] SRCH-02 pass

    ## DoD
    - Unit/integration tests green
    - PR mô tả rõ mapping field -> SQL condition
    """)

    task2 = dedent(f"""
    # TASK-{US}-02 (Implement-ready)
    ## Mục tiêu
    Implement ajax paging/sort endpoint contract `output_type=json`.

    ## Scope in
    - Nhận `p,c,s,d,searchkey`
    - Trả JSON chuẩn `result/html/allcount/pngerrmsg`
    - Xử lý fail path để client hiển thị `検索結果エラー`

    ## Scope out
    - CSV

    ## AC
    - [ ] AJAX-01 pass
    - [ ] AJAX-02 pass
    - [ ] `searchkey` cũ được giữ đúng hành vi legacy

    ## DoD
    - Có snapshot JSON contract
    - Có video/gif ngắn demo sort + paging
    """)

    task3 = dedent(f"""
    # TASK-{US}-03 (Implement-ready)
    ## Mục tiêu
    Implement CSV flows: normal/report/order theo filter hiện tại.

    ## Scope in
    - Branch `csv_type` = normal / _report / _order
    - Pass đúng hidden filter + sort
    - Cookie `downloaded` để restore button state

    ## Scope out
    - Refactor format CSV cũ

    ## AC
    - [ ] CSV-01 pass
    - [ ] CSV-02 pass
    - [ ] CSV-03 pass (khi env bật)

    ## DoD
    - Đính kèm file output mẫu cho 3 loại CSV
    - Không còn double-submit
    """)

    task4 = dedent(f"""
    # TASK-{US}-04 (Implement-ready)
    ## Mục tiêu
    Hoàn thiện automation + regression checklist cho account list flow.

    ## Scope in
    - Viết integration tests cho AUTH/SRCH/AJAX/CSV/BUSHO
    - Tạo smoke E2E search + csv action
    - Gắn test vào CI

    ## AC
    - [ ] Case BUSHO-01 pass
    - [ ] PR fail nếu vỡ ajax/csv contract

    ## DoD
    - Pipeline xanh
    - Báo cáo case-id pass/fail trong artifact CI
    """)

    plan = dedent(f"""
    # PLAN-{US} (VI)

    Related: Story {issue_url(ISSUES['story'])} | PRD {issue_url(ISSUES['prd'])} | TDD {issue_url(ISSUES['tdd'])}

    ## Execution order
    1. TASK-01 (auth + filter parser)
    2. TASK-02 (ajax json contract)
    3. TASK-03 (csv flows)
    4. TASK-04 (automation + CI)

    ## Governance
    ```mermaid
    flowchart TD
      A[Story] --> GA{{Gate A}}
      GA --> B[PRD]
      B --> GB{{Gate B}}
      GB --> C[TDD + Tasks]
      C --> GC{{Gate C}}
      GC --> D[Implement]
      D --> E[Review + CI]
      E --> F[E2E]
      F --> R[Release]
    ```
    """)

    e2e1 = dedent(f"""
    # E2E-{US}-01
    ## Kịch bản
    User có quyền search account bằng nhiều filter, sau đó sort/paging.

    ## Expected
    - allcount đúng
    - rows đổi theo sort/paging
    - không mất ngữ cảnh filter đã search
    """)

    e2e2 = dedent(f"""
    # E2E-{US}-02
    ## Kịch bản
    User export CSV từ kết quả đã search.

    ## Expected
    - file được tải về
    - loại CSV đúng theo button
    - UI button được restore sau download
    """)

    write(f"{US}.md", story)
    write(f"PRD-{US}.md", prd)
    write(f"TDD-{US}.md", tdd)
    write(f"TASK-{US}-01.md", task1)
    write(f"TASK-{US}-02.md", task2)
    write(f"TASK-{US}-03.md", task3)
    write(f"TASK-{US}-04.md", task4)
    write(f"PLAN-{US}.md", plan)
    write(f"E2E-{US}-01.md", e2e1)
    write(f"E2E-{US}-02.md", e2e2)

    sync_issue(ISSUES["story"], f"Story: {US} Account Search/List Screen", "story", f"{US}.md")
    sync_issue(ISSUES["prd"], f"PRD: {US}", "prd", f"PRD-{US}.md")
    sync_issue(ISSUES["tdd"], f"TDD Plan: {US}", "tdd", f"TDD-{US}.md")
    sync_issue(ISSUES["task1"], f"Task Impl: {US}-01", "task-impl", f"TASK-{US}-01.md")
    sync_issue(ISSUES["task2"], f"Task Impl: {US}-02", "task-impl", f"TASK-{US}-02.md")
    sync_issue(ISSUES["task3"], f"Task Impl: {US}-03", "task-impl", f"TASK-{US}-03.md")
    sync_issue(ISSUES["task4"], f"Task TDD: {US}-04", "task-tdd", f"TASK-{US}-04.md")
    sync_issue(ISSUES["plan"], f"Plan: {US}", "plan", f"PLAN-{US}.md")
    sync_issue(ISSUES["e2e1"], f"E2E: {US}-01", "e2e", f"E2E-{US}-01.md")
    sync_issue(ISSUES["e2e2"], f"E2E: {US}-02", "e2e", f"E2E-{US}-02.md")

    print("✅ Hardened US0502 into Vietnamese implement-ready docs and synced issues")


if __name__ == "__main__":
    main()
