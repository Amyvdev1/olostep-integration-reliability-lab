# Live compatibility — pending

**Status: not executed.** The private API key was not available in the process or
Windows user environment at the last check on October 14, 2026. No batch was created.
Offline success must not be read as provider compatibility.

## Approved bounded protocol

- One batch, at most two permitted public URLs, existing credits only.
- No credit purchase, automatic second submission or retry of batch creation.
- Use `https://example.com` and `https://www.iana.org/help/example-domains`.
- Save the minimal checkpoint immediately after acceptance. Keep raw reports local
  in the ignored output directory; never publish the key or unreviewed payloads.
- Request page size 1 to exercise actual cursor pagination if the API honors it.
- Bound polling/retrieval to 600 seconds. If waiting expires, resume the saved
  batch, never create a replacement automatically.
- Compare accepted batch ID, lifecycle status, totals, item identities, cursors,
  retrieve IDs and nonempty Markdown with the documented contract.
- Record returned credits/cost as provider-reported only when present and valid.
  Do not estimate missing usage or infer it from the number of pages.

## Report after execution

Record UTC execution time, sanitized response-field/type observations, requested
and observed item counts, whether pagination actually occurred, content checks,
usage-field presence, any contract differences, and explicit pass/fail/unknown for
each check. Redact operational IDs and sensitive fields from public evidence.
A two-page compatibility check cannot establish load, reliability, production
adoption, extraction accuracy, webhook delivery or general billing behavior.

Sources: [Batch information](https://docs.olostep.com/api-reference/batches/info),
[Batch items](https://docs.olostep.com/api-reference/batches/items),
[Retrieval](https://docs.olostep.com/api-reference/retrieve).
