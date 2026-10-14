# Source map and verification boundaries

Public pages inspected October 14, 2026. Documentation can change. This is an
independent interpretation, not an audit endorsed by Olostep.

| Concept | Official source | Implementation |
|---|---|---|
| Create batch with items/custom IDs | https://docs.olostep.com/api-reference/batches/create | `Runner.run` |
| Async flow and new-account constraints | https://docs.olostep.com/features/batches | Bounded polling; local 10-URL cap |
| Completed/failed items, retrieval IDs | https://docs.olostep.com/api-reference/batches/items | `Runner.items` |
| Batch totals and reported usage | https://docs.olostep.com/api-reference/batches/info | Reconciliation and labeled usage fields |
| Retrieve stored content | https://docs.olostep.com/api-reference/retrieve | Markdown retrieval |
| Completion notifications and re-delivery | https://docs.olostep.com/api-reference/common/webhooks | Local `Inbox` simulation |
| Bearer credentials | https://docs.olostep.com/get-started/authentication | Environment variable; fixed-origin adapter |
| Product surface | https://docs.olostep.com/get-started/welcome | Workflow decision guide |
| Technical writing responsibilities | https://www.olostep.com/careers/technical_writer | Executable tutorial and evidence methodology |

The feature guide illustrates a cursor response; the reference example can omit it
on the final page. This implementation accepts an absent/null cursor as terminal
and rejects repeated cursors. One live two-item batch confirmed an integer cursor
on its first page and an omitted cursor on its terminal page. See the bounded
[live compatibility record](live-compatibility.md).

Response fixtures are original minimal examples, not copied production records.
The in_progress/completed lifecycle and top-level `markdown_content` response were
observed in that run; other states and failure responses remain fixture-tested. The sample fails visibly
rather than silently guessing alternate schemas.
