# Know what you are looking at

| Surface | Executes | Evidence |
|---|---|---|
| Browser console | Python runner + synthetic transport + virtual clock | Fixture logic, not API latency |
| Offline CLI | Python runner + synthetic transport + real local clock | Local behavior and elapsed duration |
| Optional live CLI | Same runner + fixed-origin HTTPS adapter | Provider responses if actually executed |
| Unit tests | Runner, transport mocks, SQLite restart test | Explicit local assertions |
| Recorded video | Actual browser operations against loopback server | Visual demonstration of fixture behavior |

No live provider calls were made during this build. No real key was used. A live
run requires your privately configured key and explicit CLI opt-in for creation.
No credentials are requested by the console or embedded in examples.

To validate the next stage: choose one permitted public URL, review current costs,
run the live command in the README, preserve a sanitized report, and compare actual
response shapes with the documented adapter. If the response differs, add a fixture
and regression test before changing the mapping. Do not change the report's mode
label to make an offline result look live.

Hosted content is intentionally not automatically fetched. `size_exceeded` becomes
`hosted_content_requires_review`: a future downloader needs separate origin, size
and credential rules rather than forwarding the provider bearer token to an arbitrary URL.
