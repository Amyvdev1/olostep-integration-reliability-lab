# Integration evidence

Mode: **fixture** | Outcome: **complete**

Batch: `batch_fixture`

Credits: **unknown** (unknown; not inferred from success counts).

Cost USD: **unknown** (unknown; not an invoice audit).

Read retries: 1

## Items

| Item | Status | Evidence |
|---|---|---|
| page-1 | completed | fixture |
| page-2 | completed | fixture |
| page-3 | completed | fixture |

## Reconciliation

Verification basis: `manifest`.
Expected: 3; observed: 3; provider total: 3.
Missing IDs: [].
Unexpected IDs: [].

## Decisions

- 1. create_batch: requested
- 2. create_batch: accepted
- 3. checkpoint: saved
- 4. retry_read: scheduled
- 5. poll: completed
- 6. list_items: received
- 7. retrieve: completed
- 8. retrieve: completed
- 9. list_items: received
- 10. retrieve: completed
- 11. list_items: received

## Limits

- Fixture responses are synthetic, not Olostep performance evidence.
- Credits are not inferred from successful item counts.
- Webhook inbox is a local simulation, not a public receiver.
