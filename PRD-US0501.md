# PRD-US0501

Related Story: https://github.com/sa-kannguyen/test-harness-workflow/issues/23

## Architecture
```mermaid
flowchart TD
  A[POST /jobs] --> B[Auth + Permission]
  B --> C[editToken/jobId validation]
  C --> D[Business validation]
  D --> E{status public/reserved?}
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
