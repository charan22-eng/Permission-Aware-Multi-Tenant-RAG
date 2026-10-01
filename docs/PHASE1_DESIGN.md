# Phase 1: Multi-Tenancy & Access Control Design

## 1. ACL Schema (Source of Truth)
A new SQLite table `documents_acl`:
- `document_id` (PK, TEXT)
- `tenant_id` (TEXT)
- `classification` (TEXT: public, internal, confidential)
- `allowed_roles` (TEXT: JSON array/keywords, lowercase exact match)
- `allowed_users` (TEXT: JSON array/keywords, lowercase exact match)
- `acl_version` (INTEGER)

*Every Qdrant chunk payload will contain a copy of this schema (plus `document_id`), refusing ingestion without a `tenant_id`.*

## 2. JWT Identity & Claims
- **Validation:** Uses `PyJWT` with `HS256` only, secret from `.env`. Must contain `exp`, `iat`, `user_id`, `tenant_id`. `roles` as a list of strings.
- **Constraints:** Known tenants only, 15-minute expiry. A dev token script will generate these.
- **Enforcement:** The request body/query params will have zero effect. Identity is derived *exclusively* from the token.

## 3. Dual-Layer Retrieval Defense
- **Layer 1 (Pre-Filter):** Qdrant query filter built from JWT. 
  Payload indexes on `tenant_id`, `allowed_roles`, `allowed_users`.
  Filter: `tenant_id` must match AND (`allowed_roles` intersects `token.roles` OR `allowed_users` contains `token.user_id`). The roles-OR-users condition is nested inside the MUST clause. (Testing will prove that "tenant matches, no role/user match" returns nothing).
- **Layer 2 (Post-Retrieval Guard - `acl_guard.py`):** An independent module. After retrieval but BEFORE prompt construction, we do a batch lookup against `documents_acl` by `document_id`. 
  - **Fails Closed:** Missing document, tenant mismatch, or `acl_version` mismatch means drop + alert. We decide purely by the source of truth, ignoring the payload copy to prevent stale-data leaks. (Tradeoff: ACL updates are not atomic between SQLite and Qdrant. A lag in Qdrant means new access grants may briefly fail-closed until Qdrant is updated, which is a safe failure mode.)
  - *Failure:* Drop the chunk, write an alert-level audit row, and continue processing remaining chunks.

## 4. API Contract & Refusal Behavior
- **Single Entry Point:** `retrieve_authorized()` will be the only retrieval entry point. Tests will assert nothing else imports the Qdrant client.
- **Admin Access:** No blanket admin bypass. Board minutes (allowed_users only) cannot be retrieved by admins. Other admin access is granted via explicit ACL entries.
- `/query` returns citations *only* for chunks that passed Layer 2 and reached the prompt. Eval fields (`eval_chunk_ids`, `k`) exist only when `EVAL_MODE=true` AND the caller has the admin role, with `k` capped at 10; normal responses never contain chunk IDs beyond the authorized citations.
- If all chunks are forbidden (or none exist), the system emits a generic "I don't know" abstention, never confirming a restricted document's existence.
- **Evaluation:** Report leak count and correct-refusal rate separately.

## 5. Audit Log (SQLite)
- Table `audit_log`: `request_id`, `user_id`, `tenant_id`, `query`, `returned_chunk_ids`, `returned_document_ids`, `dropped_chunk_ids`, `dropped_document_ids`, `dropped_roles`, `alert_level`, `acl_version`, `model`, `timestamp`.
- Made append-only via SQLite triggers that `ABORT` on `UPDATE` or `DELETE`.
- An admin endpoint will query "who retrieved document X in the last N days" (restricted to their own tenant). It will return identical empty results for nonexistent and other-tenant documents.

## 6. Deterministic Chunk IDs
Chunk IDs will be generated deterministically using `uuid5(document_id + chunk_index)`. We will migrate `questions.jsonl`, re-ingest `apex` at `corpus_version` 2, and prove the Phase 0 numbers reproduce (same two misses) *before* adding `northwind` and `helix`.

## 7. Threat Model (OWASP Top 10 for LLM Applications [EDITION TBD])
- **Role-change lag until token expiry:** 15 min max window where a revoked role remains valid.
- **Writable ACL table & droppable triggers:** The app DB is a trust boundary.
- **Prompt Injection (LLM01):** Will be tested via indirect injection documents.
- **Sensitive Information Disclosure (LLM02):** Mitigated by Layer 1 + Layer 2 + audit log + canary-string tests.
- **Excessive Agency (LLM03):** We mandate that `retrieve_authorized()` is the centralized hook for data access. Every future tool/retrieval path will be hardcoded to pass through this guard.
- **Hidden Context / Data Leakage (LLM08):** Mitigated by Layer 2's source-of-truth check before the LLM prompt is populated, preventing payload lag exploitation.
- **Vector / Embedding Weaknesses (LLM09):** Defeated by Layer 1 pre-filtering. The vector DB structurally refuses to return semantically proximate chunks if the tenant/roles don't match.

*Note: The Phase 2 cache key includes tenant_id and is invalidated on acl_version change.*
