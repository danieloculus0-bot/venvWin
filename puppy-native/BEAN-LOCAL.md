# BEAN Local on venvWin Puppy

This is **the existing BEAN Core** bundled into the small native Puppy addon. The source snapshot is from danieloculus0-bot/BEAN at the audited October 11, 2026 main tree (hash daefb52e3a18e6b63440b2c15f714aca680af413), not a newly invented copycat agent.

Included code: BEAN's authentic SQLite memory schema, identity, session continuity, event logger/audit mirror, original runtime bootstrap, and epistemic guard. The mascot `art/bean-official.webp` is byte-identical to `BEAN/docs/bean-official.webp` at blob 40387e82366a146e3904fb770d75cb9f19d816f3. It appears in the local BEAN page and desktop icon, not in the venvWin logo.

**Startup:** `/root/Startup/venvwin-session` runs `venvwin-bean --serve` after the guest graphical session exists. Its runtime is Python stdlib, SQLite, and a small loopback-only HTTP interface at `127.0.0.1:8788`, with no model download, microphones, cloud transport, code writing, robot actuation, or trading. `venvwin-bean --status` reports actual reachability and never returns simulated success. The operator's claim and optional user-supplied source label are recorded as unverified, reviewed with BEAN's actual epistemic guard, and returned with event/audit IDs. The local page makes it clear no text-generation model is loaded.

This is a **tiny offline BEAN intelligence substrate**, not a generative chatbot. Future opt-in tiny GGUF inference may be layered onto compatible RAM/storage hardware, but no model weights are included and no LLM inference has been proven.

Storage: uses `$VENVWIN_HOME/bean/bean_memory.db` when the home source is defined, falling back to `$HOME/venvWin-Capsules/bean/bean_memory.db`. That location is **not proof of persistence across USB reboot**. Live Puppy currently remains unverified for Python3, 64-bit Wine, SFS loading and BEAN startup. No release until real guest evidence.

Local development gate: `python -m pytest -q tests/test_puppy_bean_local.py`. This is host-side source/runtime verification; real Puppy must be tested separately.
