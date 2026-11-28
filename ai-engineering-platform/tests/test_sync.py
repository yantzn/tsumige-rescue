import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "aep_sync", ROOT / "ai-engineering-platform/scripts/sync.py"
)
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


class SyncTest(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in ("ai-engineering-platform", ".aep", "project-config"):
            shutil.copytree(ROOT / name, self.root / name)
        for name, value in (("ROOT", self.root), ("PLATFORM", self.root / "ai-engineering-platform")):
            override = patch.object(SYNC, name, value)
            override.start()
            self.addCleanup(override.stop)

    def test_reproducible_and_detects_drift(self):
        with self.assertRaises(ValueError):
            SYNC.sync(check=True)
        SYNC.sync(check=False)
        generated = self.root / ".agents/skills/orchestrator/SKILL.md"
        before = (generated.read_bytes(), generated.stat().st_mtime_ns)
        SYNC.sync(check=False)
        self.assertEqual(before, (generated.read_bytes(), generated.stat().st_mtime_ns))
        SYNC.sync(check=True)
        generated.write_text("手動変更", encoding="utf-8")
        with self.assertRaises(ValueError):
            SYNC.sync(check=True)
        SYNC.sync(check=False)
        self.assertEqual(before[0], generated.read_bytes())

    def test_rejects_gate_relaxation(self):
        overrides = self.root / "project-config/quality-overrides.json"
        overrides.write_text('{"additional_required": [], "disabled": ["flutter-test"]}')
        with self.assertRaisesRegex(ValueError, "必須ゲート"):
            SYNC.sync(check=False)
        self.assertFalse((self.root / ".agents").exists())
