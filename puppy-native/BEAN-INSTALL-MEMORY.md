# BEAN Bridge: persistent Windows install memory (experimental)

The repeatable fixtures are one **real Windows x64 application**, wrapped in a simple NSIS `.exe` installer and a WiX `.msi` installer. The host-runner compiles the fixtures, uses venvWin's actual Wine capsule entry points, tests the installed executable, and checks an exact marker written by Windows code into the capsule's Wine C: drive.

**Critical separation:** `ubuntu-wine` and `puppy-guest` are different evidence scopes. Successful Ubuntu Wine results NEVER prove native Puppy Windows compatibility. Host source tests and mock fixture tests are labeled separately. BEAN's evidence rank scores evidence strength, not truth probability or permission to release.

## Mechanism

- `puppy-native/bean_install_memory.py` uses the actual pinned BEAN Core `bean.evaluation.evidence_rank.EvidenceRankLedger`, not a recreated ranking engine. It stores the installer observation in its own SQLite hash-chained table and the shared BEAN ranking ledger.
- Its stable fingerprint is based on **source inputs and runtime identity**, not generated EXE/MSI bytes that may vary by build timestamp, and excludes the independent verifier's implementation.
- A matching passed fingerprint is eligible for reuse **within the exact same scope only**. An unchanged failed/blocked fingerprint refuses blind automatic retry. A changed fingerprint is a new test candidate. Explicit `--force` is a manual override.
- The full source SHA and GitHub Actions run are saved with each observation. Raw stdout, stderr, execution receipts and application markers are uploaded separately. The journal rejects changed reused IDs and verifies its internal hash chain.
- The guest gate requires a real QEMU serial log with a case-specific marker emitted inside Puppy, a completed live-guest boot marker and a genuine guest screenshot. A host assertion alone does not meet this gate.
- Missing or corrupted raw evidence is **not** a pass. A harness failure is `blocked`, not an application failure or a success.

## Where memory lives

GitHub runners are disposable, so the workflow restores the most recent BEAN installer SQLite database from a GitHub Actions cache, records the new observation and saves a fresh run-keyed cache. It also uploads the evidence and database with 30-day retention. Cache expiry, deletion, parallel isolated histories or missing cache are disclosed: **the GitHub cache is best-effort continuity, not permanent archival storage.** The matching branch uses job concurrency to avoid overlapping redundant test runs.

For truly durable local history, use the same module with BEAN's owner-controlled local SQLite path, such as `D:\BEAN\data\bean_memory.db` on a configured BEAN machine, with real pinned BEAN Core available on `PYTHONPATH`. This code does not secretly connect to the BEAN PC or claim to have imported its database. A later authorized synchronization can import GitHub artifact receipts; artifact retention must be considered.

## Current findings

- The original Ubuntu-hosted real Wine smoke previously passed a simple x64 executable; it does **not** establish NSIS setup or MSI compatibility or a Puppy guest runtime.
- In Actions run [38253521716](https://github.com/danieloculus0-bot/venvWin/actions/runs/38253521716) a real Windows NSIS setup was built but failed under 64-bit-only Wine 9.0. The retained stderr references missing `syswow64\ntdll.dll`, diagnostic for an absent 32-bit Wine runtime. The verifier originally could not ingest stdout diagnostic prelude as JSON, now repaired; BEAN must record the actual failure rather than hallucinate success.
- The simple x64 MSI and all Windows execution inside the actual Puppy guest remain subject to independent runtime results.

No Debian monolithic build, no ISO release, no merge. A six-gate or end-to-end product readiness claim remains forbidden without the genuine Puppy-specific evidence.
