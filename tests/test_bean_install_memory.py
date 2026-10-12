"""Synthetic contract tests only: they never count as real installer/guest evidence."""
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "puppy-native"))
from bean_install_memory import Memory, SCHEMA, MARKER, file_hash, verify_receipt

class InstallMemoryContracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.db = self.dir / "bean-install.sqlite"
        self.fingerprint = "a" * 64

    def fixture(self, scope="ubuntu-wine", case="nsis-exe"):
        folder = self.dir / (scope + case)
        folder.mkdir()
        (folder / "install.json").write_text(json.dumps({
            "action": "install", "runner_available": True, "exit_code": 0}))
        (folder / "launch.json").write_text(json.dumps({"exit_code": 0}))
        (folder / "marker.txt").write_bytes(MARKER)
        receipt = {
            "schema": SCHEMA, "scope": scope, "case": case,
            "fingerprint": self.fingerprint, "source_sha": "b" * 40,
            "run_id": "98765432100", "observed_at": datetime.now(timezone.utc).isoformat(),
            "install_sha": file_hash(folder / "install.json"),
            "launch_sha": file_hash(folder / "launch.json"),
            "marker_sha": file_hash(folder / "marker.txt"),
        }
        target = folder / "receipt.json"
        target.write_text(json.dumps(receipt))
        return target

    def test_fresh_case_is_run(self):
        with Memory(self.db) as m:
            self.assertEqual(m.plan("ubuntu-wine", "nsis-exe", self.fingerprint)["decision"], "run")

    def test_parser_checks_separate_wine_install_and_launch_receipts(self):
        self.assertEqual(verify_receipt(self.fixture())["state"], "passed")

    def test_tampered_application_marker_fails(self):
        receipt = self.fixture()
        (receipt.parent / "marker.txt").write_bytes(b"NOT_ACTUALLY_EXECUTED")
        with self.assertRaisesRegex(ValueError, "evidence content changed"):
            verify_receipt(receipt)

    def test_host_receipt_never_counts_as_guest(self):
        host = self.fixture()
        with Memory(self.db) as m:
            self.assertEqual(m.plan("puppy-guest", "nsis-exe", self.fingerprint)["decision"], "run")
        self.assertEqual(verify_receipt(host)["scope"], "ubuntu-wine")

    def test_fake_guest_without_serial_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing evidence"):
            verify_receipt(self.fixture(scope="puppy-guest"))

    def test_real_bean_store_idempotence_and_scope_separation(self):
        try:
            from bean.evaluation.evidence_rank import EvidenceRankLedger
        except ModuleNotFoundError:
            self.skipTest("Real BEAN Core not installed in general source-only CI")
        receipt = self.fixture()
        with Memory(self.db) as m:
            first = m.record(receipt)
            second = m.record(receipt)
            self.assertTrue(first["new"])
            self.assertFalse(second["new"])
            self.assertEqual(m.plan("ubuntu-wine", "nsis-exe", self.fingerprint)["decision"], "reuse_scope_only")
            self.assertEqual(m.plan("puppy-guest", "nsis-exe", self.fingerprint)["decision"], "run")
            from bean.evaluation.evidence_rank import EvidenceRankLedger
            self.assertTrue(EvidenceRankLedger(m.db).verify_chain())

    def test_hash_chain_tampering_blocks_reuse(self):
        try:
            from bean.evaluation.evidence_rank import EvidenceRankLedger
        except ModuleNotFoundError:
            self.skipTest("Real BEAN Core not installed in general source-only CI")
        receipt = self.fixture()
        with Memory(self.db) as m:
            m.record(receipt)
            m.db.execute("UPDATE venvwin_install_observations SET state='failed'")
            m.db.commit()
            with self.assertRaisesRegex(ValueError, "chain invalid"):
                m.plan("ubuntu-wine", "nsis-exe", self.fingerprint)

    def test_same_failed_fingerprint_not_blindly_retried(self):
        with Memory(self.db) as m:
            row = {
                "id": "synthetic-failed", "scope":"ubuntu-wine", "test_case":"nsis-exe",
                "fingerprint":self.fingerprint, "state":"failed", "blocker":"installer_exit_nonzero",
                "run_id":"98765432100", "source_sha":"b"*40, "payload_sha":"c"*64,
                "observed_at":datetime.now(timezone.utc).isoformat(), "prior_hash":"GENESIS",
            }
            from bean_install_memory import digest, canonical
            row["entry_hash"] = digest(canonical(row))
            m.db.execute("INSERT INTO venvwin_install_observations "
                "(id,scope,test_case,fingerprint,state,blocker,run_id,source_sha,payload_sha,observed_at,prior_hash,entry_hash) "
                "VALUES (:id,:scope,:test_case,:fingerprint,:state,:blocker,:run_id,:source_sha,:payload_sha,:observed_at,:prior_hash,:entry_hash)",row)
            m.db.commit()
            self.assertEqual(m.plan("ubuntu-wine","nsis-exe",self.fingerprint)["decision"],"blocked_unchanged")
            self.assertEqual(m.plan("ubuntu-wine","nsis-exe",self.fingerprint,True)["decision"],"run")

if __name__ == "__main__":
    unittest.main()
