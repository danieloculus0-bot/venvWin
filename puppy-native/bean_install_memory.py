#!/usr/bin/env python3
"""BEAN installer evidence journal. An attested Ubuntu pass is NEVER Puppy proof.

Persistent SQLite can be restored from CI cache/artifacts or used on BEAN's PC.
Real BEAN EvidenceRankLedger is mandatory when recording, no mock fallback.
Never infer releases from a score; hash-chain integrity != external authenticity.
"""
import argparse
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "venvwin.bean.installer.v1"
MARKER = b"REAL_WINDOWS_APPLICATION_LAUNCHED"
CASES = {"nsis-exe", "wix-msi"}
SCOPES = {"ubuntu-wine", "puppy-guest"}

def digest(value):
    return hashlib.sha256(value).hexdigest()

def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

def file_hash(file):
    h = hashlib.sha256()
    with Path(file).open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def evidence_file(folder, name):
    if not re.fullmatch(r"[a-zA-Z0-9_.-]{1,96}", str(name)):
        raise ValueError("unsafe evidence path")
    p = folder / name
    if not p.is_file() or p.is_symlink():
        raise ValueError("missing evidence: " + name)
    return p

def verified_file(folder, name, expected):
    if not isinstance(expected, str) or not re.fullmatch("[0-9a-f]{64}", expected):
        raise ValueError("invalid evidence checksum")
    p = evidence_file(folder, name)
    if file_hash(p) != expected:
        raise ValueError("evidence content changed: " + name)
    return p

def fingerprint(scope, files, runtime):
    if scope not in SCOPES or not runtime or not files:
        raise ValueError("unbound test fingerprint")
    return digest(canonical({"scope": scope, "runtime": runtime,
                             "sources": [{"name": Path(p).name, "hash": file_hash(p)} for p in files]}))

def verify_receipt(path):
    p = Path(path)
    r = json.loads(p.read_text())
    if r.get("schema") != SCHEMA or r.get("scope") not in SCOPES or r.get("case") not in CASES:
        raise ValueError("unknown receipt/test scope")
    if not re.fullmatch("[0-9a-f]{64}", r.get("fingerprint", "")):
        raise ValueError("invalid fingerprint")
    if not re.fullmatch("[0-9a-f]{40}", r.get("source_sha", "")):
        raise ValueError("missing source commit")
    if not re.fullmatch("[1-9][0-9]{4,18}", str(r.get("run_id", ""))):
        raise ValueError("no GitHub Actions run identity")
    instant = datetime.fromisoformat(r["observed_at"].replace("Z", "+00:00"))
    if instant.utcoffset() is None or instant.astimezone(timezone.utc) > datetime.now(timezone.utc):
        raise ValueError("invalid evidence time")
    folder = p.parent
    state = "blocked"
    blocker = None
    outcome_ref = None
    if r.get("error_sha"):
        error = verified_file(folder, "error.txt", r["error_sha"])
        blocker = "harness:" + error.read_text()[:100]
    else:
        log = verified_file(folder, "install.json", r["install_sha"])
        install = json.loads(log.read_text())
        if install.get("action") != "install" or install.get("runner_available") is not True:
            raise ValueError("no real Wine-backed installation receipt")
        if type(install.get("exit_code")) is not int:
            raise ValueError("installer did not return exit code")
        state, blocker = "failed", "installer_exit_nonzero"
        outcome_ref = "sha256:install-log:" + r["install_sha"]
        if install["exit_code"] == 0:
            if not r.get("launch_sha"):
                state, blocker = "blocked", "installed_executable_not_located"
                outcome_ref = None
            else:
                launch = json.loads(verified_file(folder, "launch.json", r["launch_sha"]).read_text())
                if launch.get("exit_code") != 0:
                    blocker = "windows_application_launch_failed"
                    outcome_ref = "sha256:launch-log:" + r["launch_sha"]
                elif not (folder / "marker.txt").is_file():
                    blocker = "windows_application_marker_missing"
                    outcome_ref = "sha256:launch-log:" + r["launch_sha"]
                else:
                    marker = verified_file(folder, "marker.txt", r["marker_sha"])
                    if marker.read_bytes() != MARKER:
                        raise ValueError("incorrect Windows-generated marker")
                    outcome_ref = "sha256:windows-marker:" + r["marker_sha"]
                    if r["scope"] == "puppy-guest":
                        serial = verified_file(folder, "guest-serial.log", r.get("serial_sha")).read_bytes()
                        expected = ("VENVWIN_GUEST_WINDOWS_APP_PASS=" + r["case"] + ":" + r["fingerprint"]).encode()
                        if expected not in serial.splitlines() or b"PUPPY_GUEST_BOOT_PROVEN" not in serial.splitlines():
                            raise ValueError("no true Puppy serial witness")
                        screenshot = evidence_file(folder, "guest-desktop.png")
                        if screenshot.stat().st_size < 1024 or screenshot.open("rb").read(8) != b"\x89PNG\r\n\x1a\n":
                            raise ValueError("no actual guest screenshot")
                        outcome_ref = "sha256:guest-serial:" + r["serial_sha"]
                    state, blocker = "passed", None
    return {"id": f"venvwin:{r['run_id']}:{r['scope']}:{r['case']}:{r['fingerprint'][:16]}",
            "scope": r["scope"], "case": r["case"], "fingerprint": r["fingerprint"],
            "state": state, "blocker": blocker, "run_id": str(r["run_id"]),
            "source_sha": r["source_sha"], "observed_at": instant.astimezone(timezone.utc).isoformat(),
            "payload_sha": file_hash(p), "verification_ref": "sha256:receipt:" + file_hash(p),
            "outcome_ref": outcome_ref}

class Memory:
    def __init__(self, db):
        Path(db).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(db))
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
          CREATE TABLE IF NOT EXISTS venvwin_install_observations(
            seq INTEGER PRIMARY KEY AUTOINCREMENT, id TEXT NOT NULL UNIQUE,
            scope TEXT NOT NULL, test_case TEXT NOT NULL, fingerprint TEXT NOT NULL,
            state TEXT NOT NULL, blocker TEXT, run_id TEXT NOT NULL,
            source_sha TEXT NOT NULL, payload_sha TEXT NOT NULL,
            observed_at TEXT NOT NULL, prior_hash TEXT NOT NULL, entry_hash TEXT NOT NULL);
          CREATE INDEX IF NOT EXISTS venvwin_install_latest
            ON venvwin_install_observations(scope,test_case,fingerprint,seq);
        """)
        self.db.commit()
        self.check()
    def __enter__(self):
        return self
    def __exit__(self, *_):
        self.db.close()
    def check(self):
        prior = "GENESIS"
        for r in self.db.execute("SELECT * FROM venvwin_install_observations ORDER BY seq"):
            fields = ("id", "scope", "test_case", "fingerprint", "state", "blocker",
                      "run_id", "source_sha", "payload_sha", "observed_at", "prior_hash")
            payload = {k:r[k] for k in fields}
            if r["prior_hash"] != prior or digest(canonical(payload)) != r["entry_hash"]:
                raise ValueError("BEAN install history chain invalid")
            prior = r["entry_hash"]
    def plan(self, scope, case, identity, force=False):
        self.check()
        if scope not in SCOPES or case not in CASES or not re.fullmatch("[0-9a-f]{64}", identity):
            raise ValueError("invalid test/fingerprint")
        r = self.db.execute(
            "SELECT * FROM venvwin_install_observations WHERE scope=? AND test_case=? "
            "AND fingerprint=? ORDER BY seq DESC LIMIT 1", (scope,case,identity)).fetchone()
        if r is None:
            return {"decision":"run", "why":"new fingerprint or missing result"}
        if r["state"] == "passed":
            return {"decision":"reuse_scope_only", "run_id":r["run_id"], "entry_hash":r["entry_hash"]}
        return {"decision":"run" if force else "blocked_unchanged", "blocker":r["blocker"],
                "run_id":r["run_id"], "entry_hash":r["entry_hash"]}
    def record(self, receipt_path):
        e = verify_receipt(receipt_path)
        self.check()
        from bean.evaluation.evidence_rank import Evidence, EvidenceRankLedger
        ranked = EvidenceRankLedger(self.db)
        r = self.db.execute("SELECT payload_sha,entry_hash,state FROM venvwin_install_observations WHERE id=?",
                            (e["id"],)).fetchone()
        if r:
            if r["payload_sha"] != e["payload_sha"]:
                raise ValueError("receipt identity collision")
            return {"new":False, "state":r["state"], "hash":r["entry_hash"]}
        last = self.db.execute("SELECT entry_hash FROM venvwin_install_observations ORDER BY seq DESC LIMIT 1").fetchone()
        row = {"id":e["id"], "scope":e["scope"], "test_case":e["case"],
               "fingerprint":e["fingerprint"], "state":e["state"], "blocker":e["blocker"],
               "run_id":e["run_id"], "source_sha":e["source_sha"],
               "payload_sha":e["payload_sha"], "observed_at":e["observed_at"],
               "prior_hash":last[0] if last else "GENESIS"}
        row["entry_hash"] = digest(canonical(row))
        topic = f"venvwin.{e['scope']}.{e['case']}.{e['fingerprint'][:12]}"
        ranked.observe(Evidence(evidence_id=e["id"], domain="software_install",
             topic=topic, value=e["state"], origin="github-actions-" + e["run_id"],
             source_ref="https://github.com/danieloculus0-bot/venvWin/actions/runs/" + e["run_id"],
             observed_at=e["observed_at"], verified=True,
             verification_ref=e["verification_ref"],
             outcome=("unmeasured" if e["state"] == "blocked" else
                      "pass" if e["state"] == "passed" else "fail"),
             outcome_ref=e["outcome_ref"]))
        self.db.execute("INSERT INTO venvwin_install_observations"
            "(id,scope,test_case,fingerprint,state,blocker,run_id,source_sha,payload_sha,observed_at,prior_hash,entry_hash)"
            "VALUES(:id,:scope,:test_case,:fingerprint,:state,:blocker,:run_id,:source_sha,"
            ":payload_sha,:observed_at,:prior_hash,:entry_hash)",row)
        self.db.commit()
        self.check()
        return {"new":True, "state":e["state"], "blocker":e["blocker"],
                "hash":row["entry_hash"], "scope":e["scope"], "run_id":e["run_id"]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, required=True)
    sub = ap.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan")
    plan.add_argument("--scope", choices=sorted(SCOPES), required=True)
    plan.add_argument("--case", choices=sorted(CASES), required=True)
    plan.add_argument("--fingerprint", required=True)
    plan.add_argument("--force", action="store_true")
    record = sub.add_parser("record")
    record.add_argument("receipt", type=Path)
    sub.add_parser("verify")
    args = ap.parse_args()
    with Memory(args.db) as ledger:
        if args.command == "plan":
            result = ledger.plan(args.scope, args.case, args.fingerprint, args.force)
        elif args.command == "record":
            result = ledger.record(args.receipt)
        else:
            from bean.evaluation.evidence_rank import EvidenceRankLedger
            EvidenceRankLedger(ledger.db).verify_chain()
            result = {"BEAN_CHAIN_VERIFIED":True}
    print(json.dumps(result, sort_keys=True))
    if result.get("state") in {"failed","blocked"}:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
