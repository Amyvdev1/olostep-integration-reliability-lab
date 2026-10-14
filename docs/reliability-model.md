# Reliability is a policy, not a retry loop

## States

`create → accepted → poll → list completed + failed → retrieve → evidence`

The runner reports `complete` only when all enumerated content is usable and the
submitted identities and provider count agree when available. Without a saved
manifest, a resumed run verifies the provider count only, explicitly labeled in
the report. Without either an expected count or a manifest, completeness is unknown. `partial` means enumeration finished but some
items failed or have missing content. `incomplete` means the workflow could not
finish determining its result; already retrieved items remain in the report.

## Retry policy

- POST creation: one attempt. A network failure or server 5xx leaves acceptance
  uncertain. Return `creation_unknown_do_not_resubmit` rather than replaying it.
- GET reads: at most three attempts for network failures and 429/500/502/503/504.
- Backoff: the larger of exponential delay (1 then 2 seconds) and a valid
  Retry-After value, plus up to 250 ms jitter in live mode. Numeric seconds and
  HTTP-date values are supported. Fixtures use zero jitter unless a test injects it.
  The shared deadline may stop waiting before another request is permitted.
- Authentication errors: stop. Changing nothing and retrying an invalid key is not recovery.
- Polling: one-second intervals, sharing the same deadline as retrieval. Live
  request timeout is capped at ten seconds and remaining budget.
- Pagination: at most 100 pages per category; repeat cursors and duplicate item
  identifiers stop the run. A missing/null cursor terminates pagination.

Time budgets are best-effort client bounds: DNS and operating-system networking
can exceed socket timeouts. This is not a hard real-time scheduler.

## Resume and reconciliation

The CLI writes a minimal checkpoint using a temporary file, flush/fsync and atomic
replacement before its first poll. Resume preserves the original custom IDs and
never creates work. Count equality alone cannot prove identity: three unexpected
IDs cannot substitute for the three submitted IDs. Reports include missing and
unexpected identities, provider total, observed count, and the verification basis.

A crash after provider acceptance but before checkpoint persistence still leaves a
reconciliation gap. If checkpoint writing fails, the incomplete report retains the
batch ID; recover it before proceeding. This is not distributed exactly-once execution
or a concurrent multi-process checkpoint store.

## Duplicate notification handling

SQLite stores an event ID and digest of its semantic payload. The database unique
constraint arbitrates inserts. A matching re-delivery is ignored even after a
restart; the same ID with a different payload is rejected. Delivery-attempt metadata
is excluded from the digest because it can change on retry.

This is event deduplication, not exactly-once side effects. A production consumer
needs an outbox or transactional work queue, authentication, payload limits,
retention policies and reconciliation after crashes. The inbox demo is deliberately
separate from the runner and never treats a webhook as authoritative API evidence.

## Evidence vocabulary

| Label | Meaning here |
|---|---|
| fixture | Local synthetic response under a controlled scenario |
| live | A response returned by the opt-in provider adapter |
| documented | Public documentation describes a behavior; see source map |
| provider_reported | Valid nonnegative usage returned by a live batch-info response; not an invoice audit |
| unknown | Absent, invalid or not reliably attributable usage; never silently converted to zero |

No cost is inferred from page counts. Console elapsed values are simulated. CLI
elapsed values measure local execution, not a provider benchmark. This sample has
no measured adoption, support-volume reduction or production reliability results.

## Security boundaries

Only the fixed HTTPS Olostep API origin receives the bearer token. Redirects are
rejected. Error bodies and headers are not persisted. No API-key input exists in
the browser. The local server binds to loopback and serves only three named assets
and fixture output. Content is rendered with textContent, never as HTML.

Live retrieved content may itself be sensitive even when the key is safe. Review
reports before sharing. The output directory is ignored by Git. User-supplied URL
permission is a prerequisite; this tool is not an access-control bypass.
