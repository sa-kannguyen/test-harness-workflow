# TDD-US0502 (VI)

Related PRD: https://github.com/sa-kannguyen/test-harness-workflow/issues/34

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
