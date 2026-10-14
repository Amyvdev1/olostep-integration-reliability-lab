# Integration evidence

Mode: **fixture** | Outcome: **partial**

Batch: `batch_fixture`

Credits: **unknown** (not inferred from success counts).

Read retries: 0

## Items

| Item | Status | Evidence |
|---|---|---|
| page-1 | completed | fixture |
| page-2 | completed | fixture |
| page-3 | failed | fixture |

## Decisions

- 1. create_batch: requested
- 2. create_batch: accepted
- 3. poll: in_progress
- 4. poll: completed
- 5. list_items: received
- 6. retrieve: completed
- 7. retrieve: completed
- 8. list_items: received
- 9. list_items: received
- 10. failed_item: failed

## Limits

- Fixture responses are synthetic, not Olostep performance evidence.
- Credits are not inferred from successful item counts.
- Webhook inbox is a local simulation, not a public receiver.
