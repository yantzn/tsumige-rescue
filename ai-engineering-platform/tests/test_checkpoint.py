import importlib.util
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/checkpoint.py"
SPEC = importlib.util.spec_from_file_location("checkpoint", SCRIPT)
CHECKPOINT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKPOINT)


class CheckpointTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = directory.name
        self.ticket = "TMGR-426"
        self.state = {
            "schemaVersion": 1, "ticket": self.ticket, "stage": "PLANNED",
            "targetSha": "1" * 40, "requirementsHash": "2" * 64,
        }

    def transaction(self, ticket=None):
        return CHECKPOINT.checkpoint_transaction(self.directory, ticket or self.ticket)

    def test_committed_state_can_be_reopened(self):
        with self.transaction() as checkpoint:
            self.assertIsNone(checkpoint.load())
            checkpoint.save(self.state)
        with self.transaction() as checkpoint:
            self.assertEqual(checkpoint.load(), self.state)

    def test_invalid_state_and_interrupted_update_preserve_last_commit(self):
        with self.transaction() as checkpoint:
            checkpoint.save(self.state)
        with self.assertRaises(ValueError), self.transaction() as checkpoint:
            checkpoint.save(dict(self.state, requirementsHash="invalid"))
        with self.assertRaises(RuntimeError), self.transaction() as checkpoint:
            checkpoint.save(dict(self.state, stage="DESIGNED"))
            raise RuntimeError("中断")
        with self.transaction() as checkpoint:
            self.assertEqual(checkpoint.load(), self.state)

    def test_same_ticket_is_locked_and_other_ticket_remains_available(self):
        with self.transaction():
            with self.assertRaisesRegex(sqlite3.OperationalError, "locked"):
                with self.transaction():
                    self.fail("二重にロックを取得しました。")
            with self.transaction("TMGR-427") as checkpoint:
                self.assertIsNone(checkpoint.load())
        with self.transaction() as checkpoint:
            self.assertIsNone(checkpoint.load())

    def test_resume_and_single_pr_reservation(self):
        sha, digest = self.state["targetSha"], self.state["requirementsHash"]
        with self.transaction() as checkpoint:
            checkpoint.save(dict(self.state, stage="PR_READY"))
        with self.transaction() as checkpoint:
            self.assertEqual(checkpoint.resume(sha, digest)["stage"], "PR_READY")
            for wrong_sha, wrong_digest in (("3" * 40, digest), (sha, "4" * 64)):
                with self.assertRaises(ValueError):
                    checkpoint.resume(wrong_sha, wrong_digest)
            checkpoint.reserve_pr(sha, digest)
        with self.transaction() as checkpoint:
            with self.assertRaisesRegex(ValueError, "予約済み"):
                checkpoint.reserve_pr(sha, digest)

    def test_forced_process_exit_recovers_last_commit(self):
        with self.transaction() as checkpoint:
            checkpoint.save(self.state)
        child = """
import os
import sys
import checkpoint
with checkpoint.checkpoint_transaction(sys.argv[1], sys.argv[2]) as state:
    state.save(dict(state.load(), stage='DESIGNED'))
    os._exit(42)
"""
        result = subprocess.run(
            [sys.executable, "-c", child, self.directory, self.ticket],
            cwd=SCRIPT.parent, capture_output=True, timeout=10,
        )
        self.assertEqual(result.returncode, 42, result.stderr.decode(errors="replace"))
        with self.transaction() as checkpoint:
            self.assertEqual(checkpoint.load(), self.state)
