"""Reproducible real-Hermes PluginManager verification.

Run with the Python interpreter from a Hermes Agent environment, for example:
    ~/.hermes/hermes-agent/venv/bin/python tests/verify_real_plugin.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


OBSERVER_HOOKS = {
    "on_session_start",
    "on_session_end",
    "on_session_finalize",
    "pre_llm_call",
    "post_llm_call",
    "pre_tool_call",
    "post_tool_call",
}


def _worker(mode: str) -> dict[str, object]:
    from hermes_cli.plugins import PluginManager  # pyright: ignore[reportMissingImports]
    from tools.registry import registry  # pyright: ignore[reportMissingImports]

    manager = PluginManager()
    manager.discover_and_load()
    row = next(
        item for item in manager.list_plugins() if item.get("name") == "mantle-os"
    )
    if mode == "disabled":
        assert row["enabled"] is False
        assert "not enabled" in str(row["error"])
        assert registry.get_entry("mantle_status") is None
        assert not (OBSERVER_HOOKS & set(manager._hooks))
        return {"mode": mode, "enabled": False, "hooks": 0}

    assert row["enabled"] is True and row["error"] is None, row
    assert OBSERVER_HOOKS <= set(manager._hooks)
    status_entry = registry.get_entry("mantle_status")
    assert status_entry is not None
    status = json.loads(status_entry.handler({}))
    assert status["mantle_version"] == "1.2.0"

    sensitive = [
        "sk-integration-user",
        "sk-integration-history",
        "sk-integration-assistant",
        "sk-integration-command",
        "sk-integration-result",
        "call-integration-ok",
        "call-integration-blocked",
    ]
    invoke = manager.invoke_hook
    invoke("on_session_start", session_id="session-integration")
    invoke(
        "pre_llm_call",
        session_id="session-integration",
        user_message=sensitive[0],
        conversation_history=[{"role": "user", "content": sensitive[1]}],
        is_first_turn=False,
        model="provider/model",
    )
    invoke(
        "post_llm_call",
        session_id="session-integration",
        user_message=sensitive[0],
        assistant_response=sensitive[2],
        conversation_history=[],
        model="provider/model",
    )
    invoke(
        "pre_tool_call",
        tool_name="terminal",
        args={"command": sensitive[3], sensitive[3]: "value"},
        tool_call_id=sensitive[5],
        session_id="session-integration",
    )
    invoke(
        "post_tool_call",
        tool_name="terminal",
        args={"command": sensitive[3]},
        result=sensitive[4],
        tool_call_id=sensitive[5],
        session_id="session-integration",
        status="error",
        error_type="PermissionError",
        error_message="private",
        duration_ms=3,
    )
    invoke(
        "post_tool_call",
        tool_name="write_file",
        args={"path": "/tmp/x"},
        result="blocked",
        tool_call_id=sensitive[6],
        session_id="session-integration",
        status="blocked",
        error_type="plugin_block",
    )
    invoke("on_session_end", session_id="session-integration")

    runtime = manager._hooks["pre_llm_call"][0].__self__
    organism = runtime.organism
    senses = organism.prime.read("senses")
    brain = organism.prime.read("brain")
    serialized = json.dumps(
        {"senses": senses, "brain": brain, "immune": organism.immune.log},
        sort_keys=True,
    )
    for value in sensitive:
        assert value not in serialized, value

    signals = [
        item["content"]["signal"]
        for item in senses
        if isinstance(item.get("content", {}).get("signal"), dict)
    ]
    pre = next(item for item in signals if item.get("event_type") == "pre_llm_call")
    post = next(item for item in signals if item.get("event_type") == "post_llm_call")
    assert pre["metadata"]["user_message"]["chars"] == len(sensitive[0])
    assert pre["metadata"]["conversation_history"]["items"] == 1
    assert post["metadata"]["assistant_response"]["chars"] == len(sensitive[2])

    proofs = [
        item["content"]["action_proof"]
        for item in brain
        if isinstance(item.get("content", {}).get("action_proof"), dict)
    ]
    assert any(
        proof["attempted"] is True
        and proof["ok"] is False
        and proof["method"] == "Hermes dispatch"
        for proof in proofs
    )
    assert any(
        proof["attempted"] is False
        and proof["ok"] is False
        and proof["method"] is None
        and proof["evidence"][0]["status"] == "blocked"
        for proof in proofs
    )

    resident = Path(runtime._handle.path)
    assert json.loads((resident / "organism.json").read_text(encoding="utf-8"))[
        "stage1_certified"
    ] is False
    for node in [resident, *resident.rglob("*")]:
        assert node.lstat().st_mode & 0o077 == 0, (node, oct(node.lstat().st_mode))
    return {
        "mode": mode,
        "enabled": True,
        "hooks": len(OBSERVER_HOOKS),
        "proofs": len(proofs),
        "stage1_certified": False,
        "raw_exclusion": True,
        "owner_only": True,
    }


def _coordinator() -> None:
    project = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="hermes-mantle-integration-") as temp:
        sandbox = Path(temp)
        workspace = sandbox / "workspace"
        plugin = workspace / ".hermes" / "plugins" / "mantle-os"
        shutil.copytree(
            project,
            plugin,
            ignore=shutil.ignore_patterns(".git", ".runtime", "__pycache__", "*.pyc"),
        )
        results: dict[str, object] = {}
        for mode in ("enabled", "disabled"):
            hermes_home = sandbox / f"home-{mode}"
            hermes_home.mkdir()
            enabled = ["mantle-os"] if mode == "enabled" else []
            (hermes_home / "config.yaml").write_text(
                "plugins:\n  enabled: " + json.dumps(enabled) + "\n",
                encoding="utf-8",
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "HERMES_HOME": str(hermes_home),
                    "HERMES_ENABLE_PROJECT_PLUGINS": "1",
                }
            )
            completed = subprocess.run(
                [sys.executable, __file__, "--worker", mode],
                cwd=workspace,
                env=environment,
                text=True,
                capture_output=True,
                check=False,
                timeout=180,
            )
            if completed.returncode != 0:
                raise RuntimeError(
                    f"{mode} PluginManager verification failed:\n"
                    + completed.stdout
                    + completed.stderr
                )
            results[mode] = json.loads(completed.stdout)
        print(json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--worker":
        print(json.dumps(_worker(sys.argv[2]), sort_keys=True))
    else:
        _coordinator()
