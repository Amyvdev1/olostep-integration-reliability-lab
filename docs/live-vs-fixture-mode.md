# Know what you are looking at

| Surface | Executes | Evidence |
|---|---|---|
| Browser console | Python runner + synthetic transport + virtual clock | Fixture logic, not API latency |
| Offline CLI | Python runner + synthetic transport + real local clock | Local behavior and elapsed duration |
| Optional live CLI | Same runner + fixed-origin HTTPS adapter | Provider responses if actually executed |
| Unit tests | Runner, transport mocks, SQLite restart test | Explicit local assertions |
| Recorded video | Actual browser operations against loopback server | Visual demonstration of fixture behavior |

One live compatibility run was completed on October 14, 2026 using a privately
configured key: one batch, two public URLs, two retrieved Markdown documents.
The browser console and video remain synthetic demonstrations. See
[live compatibility](live-compatibility.md) for the exact evidence and limits.
Any new live run still requires a key and explicit CLI opt-in for creation.
No credentials are requested by the console or embedded in examples.

To repeat compatibility testing deliberately: choose permitted public URLs, review current costs,
run the live command in the README, preserve a sanitized report, and compare actual
response shapes with the documented adapter. If the response differs, add a fixture
and regression test before changing the mapping. Do not change the report's mode
label to make an offline result look live.

Hosted content is intentionally not automatically fetched. `size_exceeded` becomes
`hosted_content_requires_review`: a future downloader needs separate origin, size
and credential rules rather than forwarding the provider bearer token to an arbitrary URL.
