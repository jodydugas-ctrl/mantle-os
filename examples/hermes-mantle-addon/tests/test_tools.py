import json
import importlib.util
from pathlib import Path
import sys
from types import ModuleType
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOLS_PATH = PROJECT_ROOT / "tools.py"
PLUGIN_PATH = PROJECT_ROOT / "__init__.py"


def load_module(name: str, path: Path):
    assert path.exists(), f"{path.name} production module does not exist yet"
    package_locations = [str(path.parent)] if path.name == "__init__.py" else None
    spec = importlib.util.spec_from_file_location(
        name, path, submodule_search_locations=package_locations
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class RecordingContext:
    def __init__(self):
        self.tools = []
        self.hooks = []
        self.profile_name = "default"

    def register_tool(self, **registration):
        self.tools.append(registration)

    def register_hook(self, hook_name, callback):
        self.hooks.append((hook_name, callback))


class MantleStatusTests(unittest.TestCase):
    def test_status_reports_vendored_mantle_capabilities(self):
        tools = load_module("hermes_mantle_tools", TOOLS_PATH)

        result = json.loads(tools.mantle_status({}))

        self.assertTrue(result["success"])
        self.assertEqual("1.2.0", result["mantle_version"])
        self.assertEqual("true", result["mantle_scope"])
        self.assertEqual("vendored", result["source"])
        self.assertTrue({"audit", "prove", "check", "assimilate"}.issubset(result["commands"]))

    def test_status_ignores_preloaded_nonvendored_mantle_modules(self):
        tools = load_module("hermes_mantle_tools_isolation", TOOLS_PATH)
        sentinel_mantle = ModuleType("mantle")
        setattr(sentinel_mantle, "__version__", "999.0-fake")
        sentinel_cli = ModuleType("mantle.cli")
        setattr(sentinel_cli, "known_commands", lambda: ["fake-command"])
        originals = {
            name: sys.modules.get(name)
            for name in ("mantle", "mantle.cli")
        }
        sys.modules["mantle"] = sentinel_mantle
        sys.modules["mantle.cli"] = sentinel_cli
        try:
            result = json.loads(tools.mantle_status({}))
        finally:
            for name, original in originals.items():
                if original is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = original

        self.assertTrue(result["success"])
        self.assertEqual("1.2.0", result["mantle_version"])
        self.assertNotIn("fake-command", result["commands"])
        self.assertIn("audit", result["commands"])


class PluginRegistrationTests(unittest.TestCase):
    def test_register_exposes_mantle_status_tool(self):
        sys.path.insert(0, str(PROJECT_ROOT))
        try:
            plugin = load_module("hermes_mantle_addon", PLUGIN_PATH)
        finally:
            sys.path.remove(str(PROJECT_ROOT))
        context = RecordingContext()

        plugin.register(context)

        self.assertEqual(1, len(context.tools))
        registration = context.tools[0]
        self.assertEqual("mantle_status", registration["name"])
        self.assertEqual("mantle", registration["toolset"])
        self.assertEqual("mantle_status", registration["schema"]["name"])
        self.assertIs(registration["handler"], plugin.mantle_status)
        self.assertEqual(
            {
                "on_session_start",
                "on_session_end",
                "on_session_finalize",
                "pre_llm_call",
                "post_llm_call",
                "pre_tool_call",
                "post_tool_call",
            },
            {name for name, _callback in context.hooks},
        )
        runtime_ids = {id(callback.__self__) for _name, callback in context.hooks}
        self.assertEqual(1, len(runtime_ids))


if __name__ == "__main__":
    unittest.main()
