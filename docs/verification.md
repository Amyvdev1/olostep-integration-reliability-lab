# Verification record — October 14, 2026

## Executed

- Python 3.14 local suite: **28 tests passed; zero failures**.
- CLI partial scenario: 2 completed, 1 failed, overall partial; Markdown/JSON written.
- CLI transient scenario: recovered read; 3 completed, overall complete.
- Python source compilation succeeded.
- Node 24 TypeScript example executed its missing-key guard without a network call.
- Actual local browser at 1440×1080: partial flow, guided recovery chapters, complete
  flow and JSON export; **zero page errors**.
- Mobile browser at 390×844: partial flow; **no horizontal overflow**.
- Four-page article PDF rendered and all pages visually inspected.
- Real local browser walkthrough recorded. Synthetic fixture mode remains visible.

Evidence: `reports/test-results.txt`, `reports/sample/`, `reports/recovery/`,
`media/browser-verification.json`, `media/recorded-evidence.json`, screenshots,
and `media/walkthrough.mp4`.

## Not executed / not claimed

- No live Olostep API compatibility, performance or credit-usage run.
- No public webhook receiver, signature validation or production infrastructure.
- No search workflow or hosted-content downloader.
- No npm publication or production deployment.
- No measured onboarding improvement or customer/business outcome.

The initial build was verified on local Windows/Python 3.14. The included CI
configuration covers Windows/Linux and Python 3.11/3.14; check the repository's
Actions tab for subsequent hosted results. The Node example
is a small optional read, not a separately verified live TypeScript integration.

Windows sandbox networking initially blocked browser access to the local server.
The successful browser run used a loopback-only server outside that sandbox.
This was a local recording-environment issue, not an observed provider incident.
