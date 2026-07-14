from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
