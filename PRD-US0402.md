# PRD-US0402 - Recruitment List Replacement

Related Story: https://github.com/sa-kannguyen/test-harness-workflow/issues/13

## 1) Architecture Scope

```mermaid
flowchart TD
UI[AdminRecruitmentListPage] --> API1[GET /api/admin/recruitments]
UI --> API2[POST /api/admin/recruitments/bulk]
UI --> API3[GET /api/admin/recruitments/bulk/{jobId}]
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
model Recruitment {
  id              String   @id @default(cuid())
  companyId       String
  title           String
  status          Int      // 1,2,3,4,5,7
  updatedAt       DateTime @updatedAt
  createdAt       DateTime @default(now())
}

model RecruitmentBulkJob {
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
}
```

## 3) API Contracts

### 3.1 GET /api/admin/recruitments
- Query: `page,size,sortBy,sortOrder,kind,keyword,status[]`
- 200 Response:
```json
{
  "result": true,
  "allCount": 120,
  "page": 1,
  "size": 20,
  "rows": [{"id":"r1","title":"...","status":1,"updatedAt":"..."}]
}
```

### 3.2 POST /api/admin/recruitments/bulk
- Request:
```json
{"operationType":"public_all","targetIds":["r1","r2"],"csrfToken":"..."}
```
- Response:
```json
{"result":true,"jobId":"bj_001","accepted":2}
```

### 3.3 GET /api/admin/recruitments/bulk/{jobId}
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
- TDD: https://github.com/sa-kannguyen/test-harness-workflow/issues/15
- Plan: https://github.com/sa-kannguyen/test-harness-workflow/issues/20
