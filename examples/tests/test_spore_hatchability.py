from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from mantle import spore
from mantle.audits import stage1
from mantle.hatchery import hatch, validate_germ


ROOT = Path(__file__).resolve().parents[2]
SPORES = ROOT / "examples" / "spores"
SRC = ROOT / "src"


def _independent_seed_spores() -> list[Path]:
    seeds = []
    for path in sorted(SPORES.glob("*.png")):
        state = spore.read_spore(str(path))["state"]
        germ = state.get("germ")
        if isinstance(germ, dict) and germ.get("germ_format") == "mantle-germ-v1":
            seeds.append(path)
    return seeds


def test_advertised_seed_spores_decode_verify_and_stage1_hatch():
    seeds = _independent_seed_spores()
    assert seeds, "no independent SEED spores discovered in examples/spores"

    for path in seeds:
        report = spore.verify_spore(str(path))
        assert report["ok"], "%s failed structural verification: %s" % (
            path.name, report["problems"])
        state = spore.read_spore(str(path))["state"]
        germ = validate_germ(dict(state.get("germ") or {}))
        assert germ["identity"]["name"].endswith(".AppAI")

        with tempfile.TemporaryDirectory(prefix="mantle-seed-hatch-") as out_dir:
            result = hatch(str(path), out_dir=out_dir, warmup_beats=0)
            org = result["organism"]
            passed, evidence = stage1.run(org, include_invariants=False)
            assert result["report"]["certified"] is True
            assert org.stage1_certified is True
            assert passed, "%s failed Stage-1: %s" % (path.name, evidence["fails"])


def test_doctor_refuses_missing_and_malformed_organisms_without_traceback(tmp_path):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC)

    missing = subprocess.run(
        [sys.executable, "-m", "mantle", "doctor", "path-that-does-not-exist"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert missing.returncode != 0
    assert "DOCTOR REFUSED: no saved Mantle organism found at path-that-does-not-exist" in (
        missing.stdout)
    assert "Traceback" not in missing.stdout + missing.stderr

    malformed = tmp_path / "broken-nest"
    malformed.mkdir()
    (malformed / "organism.json").write_text("{bad json", encoding="utf-8")
    bad = subprocess.run(
        [sys.executable, "-m", "mantle", "doctor", str(malformed)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert bad.returncode != 0
    assert "DOCTOR REFUSED: saved Mantle organism at" in bad.stdout
    assert "could not be loaded" in bad.stdout
    assert "Traceback" not in bad.stdout + bad.stderr
