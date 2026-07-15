import json
from pathlib import Path
import subprocess
import sys
from types import ModuleType
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mantle_addon.vendor import vendored_symbol


class VendorIsolationTests(unittest.TestCase):
    def test_private_alias_and_submodule_preloads_cannot_spoof_runtime(self):
        alias = "_hermes_mantle_vendor"
        module_name = alias + ".core.organism"
        originals = {
            name: sys.modules.get(name)
            for name in (alias, alias + ".core", module_name)
        }
        sentinel = object()
        fake_package = ModuleType(alias)
        fake_package.__path__ = []
        fake_core = ModuleType(alias + ".core")
        fake_core.__path__ = []
        fake_organism = ModuleType(module_name)
        setattr(fake_organism, "Organism", sentinel)
        sys.modules[alias] = fake_package
        sys.modules[alias + ".core"] = fake_core
        sys.modules[module_name] = fake_organism
        try:
            resolved = vendored_symbol("core.organism", "Organism")
            resolved_module = sys.modules[resolved.__module__]
            origin = getattr(resolved_module, "__file__", None)
        finally:
            for name, original in originals.items():
                if original is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = original

        self.assertIsNot(sentinel, resolved)
        self.assertIsInstance(origin, str)
        self.assertTrue(
            Path(str(origin)).resolve().is_relative_to(
                PROJECT_ROOT / "vendor" / "mantle-os" / "src" / "mantle"
            )
        )

    def test_private_vendor_namespace_runs_applet5(self):
        """Vendoring must preserve relative imports in executable invariants."""
        check = vendored_symbol("audits.invariants", "t_applet_secret_boundary_and_bands")
        passed, note = check()
        self.assertTrue(passed, note)

    def test_stage1_language_separates_evidence_from_authority(self):
        stage1 = (PROJECT_ROOT.parents[1] / "src" / "mantle" / "audits" / "stage1.py")
        text = stage1.read_text(encoding="utf-8")
        self.assertNotIn("authorizes Phase 2", text)
        self.assertNotIn("Phase 2 authorized", text)
        self.assertIn("separate readiness and dual authorization", text)

    def test_complete_non_addon_vendor_snapshot_is_aligned(self):
        script = PROJECT_ROOT / "scripts" / "sync_vendor.py"
        completed = subprocess.run(
            [sys.executable, str(script), "--check"], cwd=PROJECT_ROOT,
            capture_output=True, text=True, check=False,
        )
        receipt = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, receipt)
        self.assertTrue(receipt["aligned"])
        self.assertEqual(receipt["snapshot_files"], receipt["vendor_files"])

    def test_repository_alignment_receipt_covers_every_practical_file(self):
        script = PROJECT_ROOT / "scripts" / "repository_alignment.py"
        completed = subprocess.run(
            [sys.executable, str(script), "--check"], cwd=PROJECT_ROOT,
            capture_output=True, text=True, check=False,
        )
        receipt = json.loads(completed.stdout)
        self.assertEqual(completed.returncode, 0, receipt)
        self.assertTrue(receipt["ok"])
        self.assertGreaterEqual(receipt["files_total"], 336)
        self.assertEqual([], receipt["failures"])

    def test_vendored_source_matches_repository_source(self):
        """The importable vendor tree must be byte-identical to authoritative core."""
        import hashlib

        source = PROJECT_ROOT.parents[1] / "src" / "mantle"
        vendor = PROJECT_ROOT / "vendor" / "mantle-os" / "src" / "mantle"

        def digests(root):
            return {
                str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in root.rglob("*.py")
                if "__pycache__" not in path.parts
            }

        self.assertEqual(digests(source), digests(vendor))


if __name__ == "__main__":
    unittest.main()
