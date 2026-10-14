# Implementation contract

Independent reference workflow by Amy V; not an official Olostep product.

Approved scope: one batch lifecycle, partial results, bounded retries for reads,
resumption, cursor pagination, durable duplicate-event handling, JSON/Markdown
evidence, offline fixtures, opt-in live adapter, guide, article and walkthrough.

Architecture: Python standard-library transport and runner; SQLite inbox; local
read-only browser console. No account, dependency install, or key needed offline.
The live adapter is deliberately CLI-only. No automatic retries of batch creation.

Execution plan:
1. Implement transport and deterministic fixtures; test status/error boundaries.
2. Implement runner, pagination, retrieval and reports; test partial results,
   repeated cursors, deadlines, unknown cost and creation ambiguity.
3. Implement durable event inbox; test duplicate and conflicting deliveries.
4. Add a local console driven by real runner output, responsive styles and exports.
5. Write source map, quickstart, troubleshooting, article and teaching walkthrough.
6. Run tests, record a real local demonstration and report unrun live checks.

Acceptance: a fresh checkout runs using Python 3.11+; all offline tests pass;
unknown credits stay null; reports label fixtures; live tests never run in CI.
Only documentation-backed endpoints are called. Secrets are never logged.

Review focus: malformed responses, missing items, cursor loops, ambiguous POST
failures, and duplicate events across restarts. No claim of production readiness.
