# PRD-US0402

Related Story: https://github.com/sa-kannguyen/test-harness-workflow/issues/13

## 1) Database Design (Prisma draft)
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
  operationType   String   // public_all/nonpublic_all/.../delete_all
  totalCount      Int
  successCount    Int      @default(0)
  skippedCount    Int      @default(0)
  failedCount     Int      @default(0)
  status          String   @default("queued")
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt
}
```

## 2) Backend API Design
- `GET /api/admin/recruitments` : search/paging/sort/list variant (`kind`)
- `POST /api/admin/recruitments/bulk` : start bulk operation (or sync processing for MVP)
- `GET /api/admin/recruitments/bulk/{jobId}` : operation result summary
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
- Story artifact: `US0402.md`
- Story ticket: https://github.com/sa-kannguyen/test-harness-workflow/issues/13
