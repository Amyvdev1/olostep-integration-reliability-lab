# Explain it with confidence

## Your opening, in plain English

“I built a small reference workflow around Olostep's batch API. It helps a developer
understand what happens after submission: how to wait, retrieve all the results,
handle missing content, and recover without accidentally creating the same work
again. The demonstration is offline and reproducible. The optional live adapter
still needs a provider compatibility run.”

## Five-minute code tour

| Time | Show | Explain |
|---|---|---|
| 0:00–0:40 | README and console | Who the example serves; fixture evidence boundary |
| 0:40–1:30 | Partial scenario | Batch status and usable content are different facts |
| 1:30–2:15 | `Runner.read` | Retry selected reads within an attempt and time budget |
| 2:15–3:00 | Timeout and checkpoint | Save the ID and original item identities; resume reads without recreating work |
| 3:00–3:40 | `Runner.items` and reconciliation | Follow cursors; compare identities, not just counts |
| 3:40–4:15 | `Inbox.accept` | SQLite uniqueness persists duplicate decisions |
| 4:15–5:00 | Tests and evidence export | Show what is verified and what remains unknown |

## 110-second recorded demonstration

The video records actual browser interactions with the local fixture application.
It is a demonstration of the finished workflow, not a time-lapse of development.
There is no invented provider footage, API latency or synthetic success claim.

- **00:00–00:12:** Establish the product and offline label. “This is an independent
  integration reference, focused on one reliable developer journey.”
- **00:12–00:32:** Partial results. “The batch finishes, but one source fails.
  The report keeps that failure visible instead of hiding it.”
- **00:32–00:49:** Transient read failure. “A bounded retry recovers the read.
  It does not create a second batch.”
- **00:49–01:06:** Deadline. “Waiting stops, but the batch identifier survives.
  A subsequent command can resume the same operation.”
- **01:06–01:23:** Ambiguous creation. “If the server may have accepted the request,
  resubmitting automatically is unsafe. The result is explicitly unknown.”
- **01:23–01:50:** Complete retrieval and export. “Pagination finishes, content is
  available to inspect, and duplicate events are illustrated separately. Credits
  remain unknown. The export preserves those boundaries.”

The supplied video is a clean silent screen recording; use these notes to explain
it in your own voice. No subtitle track or impersonated narration is included.

## Questions Hamza could reasonably ask

**Why Python instead of building another SDK?**
The small standard-library adapter makes the HTTP decisions visible and keeps the
offline quickstart dependency-free. This is not a replacement SDK. An SDK version
would need to account for any built-in retries to avoid accidentally multiplying attempts.

**Why not add search now?**
Known URLs isolate extraction reliability from discovery relevance. Search is a
separate stage with its own partial-content semantics; it can be added once this
workflow is verified live and understood.

**Why do you call a result partial?**
Enumeration completed, but some items failed or lacked usable Markdown. Incomplete
means the client could not finish determining the result at all.

**Does this guarantee exactly-once execution?**
No. The inbox deduplicates notification IDs durably. It does not atomically commit
downstream side effects. That would require a queue/outbox and crash recovery.

**Did you test Olostep's production API?**
Not in this delivery. The tests prove the local client behavior against fixtures.
The live adapter is implemented but requires a real compatibility run with a key.

**What would you improve next?**
Validate actual response shapes and usage fields, then conduct a
small onboarding study. Only after that add search, a public webhook receiver or
more languages. Improvements should follow observed friction.

**How do you know the documentation helps?**
It is executable and internally checked, but its effect on onboarding has not been
measured with new users. I would observe their first run and recovery attempts.

## Practice without memorizing

Run partial, transient, timeout and ambiguous-create yourself. Before opening the
report, predict its status and explain why. Then change the time budget and predict
which steps can finish. If you can explain the outcome without reading the script,
you understand the central design.
