# Recover without hiding the failure

| Evidence | Meaning | Next action |
|---|---|---|
| `missing_api_key` | No environment variable in this process | Set it privately and restart the command |
| HTTP 401/403 | Credentials or permissions rejected | Verify the account/key; do not retry unchanged |
| `creation_unknown_do_not_resubmit` | The POST may have reached the service | Reconcile through provider tooling; recover its ID before resuming |
| `deadline_exceeded` with batch ID | Local waiting budget expired | Resume the same batch with a suitable larger budget |
| `partial` + failed item | Operation ended, some source work failed | Inspect failed sources before explicitly choosing another submission |
| `missing_content` | Retrieval did not return usable Markdown | Inspect requested format and provider result; retain unresolved status |
| `repeated_cursor` | Pagination is not advancing | Stop and preserve evidence; review provider response schema |
| `item_count_mismatch` | Enumerated items differ from submitted count | Investigate omissions or duplicates before claiming completion |
| `item_identity_mismatch` | Counts match but identities differ | Compare missing/unexpected IDs; do not claim a complete dataset |
| `provider_total_mismatch` | Provider total disagrees with manifest | Reconcile the original submission with provider response |
| `completeness_unknown` | Resume lacks both manifest and valid total | Recover the checkpoint; do not interpret empty results as success |
| `checkpoint_write_failed` / `checkpoint_conflict` | Local resume state was not safely saved | Preserve the returned batch ID; repair storage or reconcile the conflicting manifest; do not recreate |
| `unexpected_batch_state` | Unsupported lifecycle status | Check current documentation and update a tested adapter mapping |
| Port 8765 occupied | Another local server uses the port | Stop that server or change the explicit port in `lab/server.py` |

The application intentionally stops on schema surprises. Silent fallback would
make a smooth demo while concealing an unreliable integration.
