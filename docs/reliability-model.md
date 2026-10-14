# Reliability is a policy, not a retry loop

## States

`create → accepted → poll → list completed + failed → retrieve → evidence`

The runner reports `complete` only when all enumerated content is usable and the
known submitted item count agrees. `partial` means enumeration finished but some
items failed or have missing content. `incomplete` means the workflow could not
finish determining its result; already retrieved items remain in the report.

## Retry policy

- POST creation: one attempt. A network failure or server 5xx leaves acceptance
  uncertain. Return `creation_unknown_do_not_resubmit` rather than replaying it.
- GET reads: at most three attempts for network failures and 429/500/502/503/504.
- Backoff: 1 then 2 seconds, within a shared deadline. This deterministic sample
  does not implement jitter or parse Retry-After; add both before fleet deployment.
- Authentication errors: stop. Changing nothing and retrying an invalid key is not recovery.
- Polling: one-second intervals, sharing the same deadline as retrieval. Live
  request timeout is capped at ten seconds and remaining budget.
- Pagination: at most 100 pages per category; repeat cursors and duplicate item
  identifiers stop the run. A missing/null cursor terminates pagination.

Time budgets are best-effort client bounds: DNS and operating-system networking
can exceed socket timeouts. This is not a hard real-time scheduler.

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
| unknown | Not observed or not reliably attributable, including credits |

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
