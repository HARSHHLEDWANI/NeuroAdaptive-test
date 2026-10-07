# Architecture entrypoint

SYSTEM_ARCHITECTURE.md is the current implementation/target architecture. frozen-scope.md is the revised v1 scope accepted 2026-10-06. AGENTS.md governs engineering invariants. docs/BASELINE_REPORT.md records actual verification, not provider/deployment assumptions.

The former broad architecture (Neo4j, Judge0, OCR and extra formats) is deferred by this scope revision. Retain the monorepo and domain modules, PostgreSQL/pgvector, private storage seam, Gemini gateways and Celery/Redis. Do not introduce duplicate services or change provider/runtime versions as incidental cleanup.
