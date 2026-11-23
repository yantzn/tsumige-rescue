# Architecture constraints
- Follow AGENTS.md and the current Jira TMGR acceptance criteria.
- Use feature-first Flutter structure: presentation / application / domain / data.
- Views never access SQLite or filesystem directly. Domain is framework-independent.
- UseCases are required for multi-resource operations (photos, restore, billing), not trivial CRUD.
- A filesystem operation and DB transaction are not atomic together; design staging, compensation and recovery.
- Preserve original photos; use separate thumbnails. Migrations need rollback/recovery test plans.
- Every architecture deviation requires an ADR or explicit approval.
