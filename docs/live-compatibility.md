# Live compatibility — one bounded batch verified

Executed **October 14, 2026, 13:55:17 UTC** against revision
`dc366be3bf7639cab58d4b5d13362db15903524d` using the existing REST adapter.

**Result: complete.** One creation attempt, two public URLs, two successful
Markdown retrievals, zero failed/unresolved items, zero retries. No adapter
changes were needed for this observed lifecycle.

## Scope and results

| Check | Observed result | Boundary |
|---|---|---|
| Creation | One POST accepted; batch ID checkpoint saved before polling | No automatic creation retry or second batch |
| Polling | Four reads; in_progress followed by completed | Other lifecycle/failure states remain fixture-tested |
| Pagination | limit=1 returned one item and integer cursor; next page returned one item without cursor | Real cursor traversal verified for two completed items |
| Failed inventory | Empty list | Does not validate a real failed-item response |
| Identity | page-2 arrived before page-1; both matched original manifest; provider total=2 | Ordering is not assumed |
| Retrieval | Two nonempty Markdown strings: 1,076 and 974 characters | Availability and basic content inspection, not general extraction accuracy |
| Usage | credits_consumed=null and cost_usd=null in Batch Info | Unknown, not zero; no billing amount inferred |
| Duration | 11.1576 seconds local elapsed; ten total HTTP calls | One observation, not a service benchmark |

Submitted URLs were `https://example.com` and
`https://www.iana.org/help/example-domains`. The first returned URL normalized to
`https://example.com/`; reconciliation uses the original custom IDs rather than
raw URL string equality. Retrieved content was inspected for the expected example
domain material. Example domains are documentation examples, not dependable load-test
or monitoring targets; this was a single compatibility check.

The dashboard showed 500 unused credits before execution. No purchase, card entry,
subscription or top-up was performed. A post-run account balance has not been
verified, and the batch response did not provide a usage measurement.

## Contract observations

- Creation returned string `id` and `status`, integer totals, and additional fields
  safely ignored by the adapter.
- Batch Info returned integer `total_urls`/`completed_urls`, and `completed_at`
  changed from null to an integer. Usage fields remained null.
- Item records contained string `custom_id`, `retrieve_id` and `url`.
- Retrieval returned string `markdown_content`, boolean `success` and
  `size_exceeded`, plus optional hosted-content fields. No hosted URL was followed.
- Terminal pagination omitted `cursor`, which the existing adapter accepts.

See [sanitized summary](../reports/live-compatibility/summary.json) and
[response field/type observations](../reports/live-compatibility/response-shapes.json).
Operational IDs, credentials, raw content, checkpoint locations and hosted-content
URLs are excluded from public evidence. Raw local reports remain Git-ignored.

## What this does not prove

The nine failure scenarios are still offline simulations. This run does not
establish production adoption, general reliability, concurrency behavior, credit
pricing, extraction accuracy, public webhook authentication/delivery or exactly-once
side effects. The browser walkthrough intentionally remains in fixture mode.

Sources: [Batch information](https://docs.olostep.com/api-reference/batches/info),
[Batch items](https://docs.olostep.com/api-reference/batches/items),
[Retrieval](https://docs.olostep.com/api-reference/retrieve).
