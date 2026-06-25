#!/usr/bin/env python3
"""
mantle.cli  --  one command for the whole lineage (Mantle OS · Gen-4)

    python -m mantle hatch <egg.json> [--out=DIR]   incubate an egg -> certified AppAI
                                                      (+ hatch report + self-portrait)
    python -m mantle teach [N]                      the Field Guide, RUNNING: each
                                                      chapter proves its claim live
    python -m mantle face <organism-dir> [out.png]  the organism paints its own state

  inherited from the Mantle lineage (unchanged guarantees):
    python -m mantle demo                           narrated Phase-1 life (no LLM)
    python -m mantle audit [--break-hash|--break-primer|--break-seal]
    python -m mantle prove                          the 32 security invariants
    python -m mantle mind                           narrated Phase-2 fusion (offline)
    python -m mantle audit-mind                     Stage-2 gate + Stage-1 regression
    python -m mantle assimilate <path> --dry-run    Path B read-only dissection
"""
from __future__ import annotations

import sys

_USAGE = ("usage: python -m mantle "
          "[anchor <host> | ask <host> [--mind] <question> | feed <host> --credits=N "
          "[--key=NAME] | vitals <host> | hatch <egg> [--out=DIR] | teach [N] | "
          "face <dir> [out.png] | face-list <dir> | face-save <dir> <name> <src> [--default] | "
          "face-wear <dir> <name> | demo | audit | prove | mind | audit-mind | "
          "assimilate <path> [--dry-run] [--out=DIR]]")


def _split(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = {a.split("=")[0]: (a.split("=", 1)[1] if "=" in a else True)
             for a in argv if a.startswith("--")}
    return args, flags


def cmd_anchor(argv):
    args, flags = _split(argv)
    if not args:
        print("usage: python -m mantle anchor <host-dir> [--credits=N] [--name=X]")
        return 2
    from .anchor import anchor, AnchorError
    print("=" * 74)
    print("ARGONAUT ANCHORING  ·  the merge ceremony  ·  host: %s" % args[0])
    print("=" * 74)
    try:
        result = anchor(args[0],
                        name=flags.get("--name") if isinstance(flags.get("--name"), str) else None,
                        starter_credits=float(flags.get("--credits", 5)))
    except AnchorError as e:
        print("\nANCHORING REFUSED: %s" % e)
        return 1
    r = result["report"]
    print("  resident      : %s" % r["resident"])
    print("  organ map     : %s" % r["organ_map"])
    print("  host files    : %d  -- unchanged: %s  (census-verified, byte for byte)"
          % (r["host_files"], r["host_unchanged"]))
    print("  certified     : %s  (the same Stage-1 gate every Body faces)" % r["certified"])
    print("  starter energy: %.1f credits" % r["starter_credits"])
    print("  nest          : %s" % r["nest"])
    print("\nANCHORED. The app has a resident now. Ask it things:")
    print("  python -m mantle ask %s \"how do I ...?\"" % args[0])
    return 0


def cmd_ask(argv):
    args, flags = _split(argv)
    if len(args) < 2:
        print("usage: python -m mantle ask <host-dir> [--mind] \"question\"")
        return 2
    from .anchor import ask, AnchorError
    try:
        result = ask(args[0], " ".join(args[1:]), use_mind=bool(flags.get("--mind")))
    except AnchorError as e:
        print(str(e)); return 1
    print(result["answer"])
    if result["thought"]:
        print("\n[the MIND adds]  %s" % result["thought"])
    print("\n(energy: %.1f credits · %s)" % (result["balance"], result["state"]))
    return 0


def cmd_feed(argv):
    args, flags = _split(argv)
    if not args or "--credits" not in flags:
        print("usage: python -m mantle feed <host-dir> --credits=N [--key=NAME]")
        return 2
    from .anchor import feed, AnchorError
    try:
        result = feed(args[0], float(flags["--credits"]),
                      key_name=flags.get("--key") if isinstance(flags.get("--key"), str) else None)
    except AnchorError as e:
        print(str(e)); return 1
    led = result["ledger"]
    print("fed. balance=%.1f credits (%s) · lifetime granted=%.1f · value delivered: %d record(s)"
          % (result["balance"], result["state"], led["granted"], len(led["value_records"])))
    return 0


def cmd_vitals(argv):
    args, _flags = _split(argv)
    if not args:
        print("usage: python -m mantle vitals <host-dir>")
        return 2
    from .anchor import vitals, AnchorError
    try:
        v = vitals(args[0])
    except AnchorError as e:
        print(str(e)); return 1
    led = v["ledger"]
    print("resident   : %s   (generation %d)" % (v["resident"], v["generation"]))
    print("state      : %s   balance=%.1f / granted=%.1f credits   keys=%s"
          % (v["state"], led["balance"], led["granted"], led["keys"] or "none"))
    print("value      : %d record(s) of delivered work" % v["value_delivered"])
    print("immune log : %d event(s)" % v["immune_events"])
    print("portrait   : %s   (painted just now, by the resident)" % v["portrait"])
    return 0


def cmd_hatch(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = {a.split("=")[0]: (a.split("=", 1)[1] if "=" in a else True)
             for a in argv if a.startswith("--")}
    if not args:
        print("usage: python -m mantle hatch <egg.json> [--out=DIR]")
        return 2
    from .hatchery import hatch, HatchError
    from .egg import EggError
    print("=" * 74)
    print("ARGONAUT HATCHERY  ·  egg: %s" % args[0])
    print("=" * 74)
    try:
        result = hatch(args[0], out_dir=flags.get("--out")
                       if isinstance(flags.get("--out"), str) else None)
    except (EggError, HatchError) as e:
        print("\nTHE EGG DID NOT HATCH: %s" % e)
        return 1
    rep = result["report"]
    for stage in rep["stages"]:
        for k, v in stage.items():
            print("  %-9s %s" % (k.upper(), v))
    print("\n  certified : %s  (the same Stage-1 gate every Body faces)" % rep["certified"])
    if rep.get("saved_to"):
        print("  saved to  : %s" % rep["saved_to"])
        print("  portrait  : %s   (the organism painted it itself)" % rep["portrait"])
    print("\nHATCHED. %s is alive, certified, and dormant -- ready for a MIND." % rep["egg"])
    return 0


def cmd_graft(argv):
    args, flags = _split(argv)
    if len(args) < 2:
        print("usage: python -m mantle graft <graft-egg.json> <host-dir> [--allow-drift]")
        return 2
    from .graft import load_graft, apply, GraftError, GraftDrift
    print("=" * 74)
    print("ARGONAUT GRAFT  ·  %s  ->  %s" % (args[0], args[1]))
    print("=" * 74)
    try:
        result = apply(load_graft(args[0]), args[1],
                       allow_drift=bool(flags.get("--allow-drift")))
    except GraftDrift as e:
        print("\nGRAFT DRIFT (the host moved): %s" % e)
        return 1
    except GraftError as e:
        print("\nGRAFT REFUSED: %s" % e)
        return 1
    r = result["report"]
    print("  resident           : %s" % r["graft"])
    print("  workspace          : %s" % r["workspace"])
    print("  original unchanged : %s  (census-verified, byte for byte)" % r["original_unchanged"])
    print("  extra bands        : %s" % (r["extra_bands"] or "none"))
    print("  hooks declared     : %d  (woven live with `weave()`)" % r["hooks"])
    print("  certified          : %s  (the same Stage-1 gate every Body faces)" % r["certified"])
    print("\nGRAFTED. The resident grew in the workspace; the original host was never touched.")
    return 0


def cmd_doctor(argv):
    args, _flags = _split(argv)
    if not args:
        print("usage: python -m mantle doctor <organism-dir>")
        return 2
    import os
    from .core.organism import Organism
    from . import doctor as _doc
    org = Organism.load(args[0], verify_seals=True)
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rep = _doc.checkup(org, repo_root=repo)
    print("=" * 60)
    print("ARGONAUT DOCTOR  ·  %s" % args[0])
    print("=" * 60)
    for c in rep["checks"]:
        print("  [%s] %-16s %s" % ("OK" if c["ok"] else "XX", c["check"], c["detail"]))
    print("\n%s" % ("HEALTHY." if rep["ok"] else "PROBLEMS FOUND."))
    return 0 if rep["ok"] else 1


def cmd_face(argv):
    if not argv:
        print("usage: python -m mantle face <organism-dir> [out.png]")
        return 2
    from .core.organism import Organism
    from .face import render
    org = Organism.load(argv[0], verify_seals=True)
    out = argv[1] if len(argv) > 1 else "face.png"
    render(org, out)
    print("the organism painted its state: %s" % out)
    return 0


def cmd_face_list(argv):
    args, _flags = _split(argv)
    if not args:
        print("usage: python -m mantle face-list <organism-dir>")
        return 2
    from .core.organism import Organism
    from . import phenotype as ph
    org = Organism.load(args[0], verify_seals=True)
    faces = ph.list_faces(org)
    if not faces:
        print("(this organism carries no faces -- no phenotype band)")
        return 0
    print("worn  default  parts  name")
    for f in faces:
        print("  %s     %s       %3d   %s"
              % ("*" if f["worn"] else " ", "*" if f["default"] else " ",
                 f["parts"], f["name"]))
    return 0


def cmd_face_save(argv):
    args, flags = _split(argv)
    if len(args) < 3:
        print("usage: python -m mantle face-save <organism-dir> <name> <source-file> "
              "[--kind=html] [--entry=index.html] [--default]")
        return 2
    from .core.organism import Organism
    from . import phenotype as ph
    directory, name, source_file = args[0], args[1], args[2]
    with open(source_file, "r", encoding="utf-8") as f:
        source = f.read()
    org = Organism.load(directory, verify_seals=True)
    try:
        rec = ph.express(org, name, flags.get("--kind", "html"), source,
                         entry=flags.get("--entry", "") if isinstance(flags.get("--entry"), str) else "",
                         default=bool(flags.get("--default")))
    except ph.PhenotypeError as e:
        print("FACE NOT SAVED: %s" % e)
        return 1
    org.save(directory)
    print("sealed face %r (%d chunk(s), %s) into the VCW -- SELF-encrypted, append-only."
          % (rec["name"], rec["parts"], rec["source_hash"]))
    return 0


def cmd_face_wear(argv):
    args, _flags = _split(argv)
    if len(args) < 2:
        print("usage: python -m mantle face-wear <organism-dir> <name>")
        return 2
    from .core.organism import Organism
    from . import phenotype as ph
    org = Organism.load(args[0], verify_seals=True)
    try:
        boot = ph.wear(org, args[1])
    except ph.PhenotypeError as e:
        print("CANNOT WEAR: %s" % e)
        return 1
    org.save(args[0])
    print("now wearing %r (kind=%s, entry=%s, %d byte(s) of source, %d control(s))"
          % (boot["name"], boot["kind"], boot["entry"] or "-",
             len(boot["source"]), len(boot["controls"])))
    return 0


# ---- back-compat API surface (the v2.3 reference shims in examples/vcw/ call these
# directly: examples_boot.py -> cli.demo, examples_mind.py -> cli.mind_demo) ----------
def demo(argv=None):
    from . import lineage_cli
    return lineage_cli.demo(argv or [])


def mind_demo(argv=None):
    from . import lineage_cli
    return lineage_cli.mind_demo(argv or [])


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "teach"
    rest = argv[1:]
    if cmd == "anchor":
        return cmd_anchor(rest)
    if cmd == "ask":
        return cmd_ask(rest)
    if cmd == "feed":
        return cmd_feed(rest)
    if cmd == "vitals":
        return cmd_vitals(rest)
    if cmd == "hatch":
        return cmd_hatch(rest)
    if cmd == "graft":
        return cmd_graft(rest)
    if cmd == "doctor":
        return cmd_doctor(rest)
    if cmd == "teach":
        from . import teach
        return teach.main(rest)
    if cmd == "face":
        return cmd_face(rest)
    if cmd in ("face-list", "face_list"):
        return cmd_face_list(rest)
    if cmd in ("face-save", "face_save"):
        return cmd_face_save(rest)
    if cmd in ("face-wear", "face_wear"):
        return cmd_face_wear(rest)
    # ---- inherited lineage commands (the Mantle guarantees, unchanged) ----
    if cmd == "demo":
        from . import lineage_cli
        return lineage_cli.demo(rest)
    if cmd == "audit":
        from .audits import stage1
        return stage1.main(rest)
    if cmd == "prove":
        from .audits import invariants
        return invariants.main(rest)
    if cmd == "mind":
        from . import lineage_cli
        return lineage_cli.mind_demo(rest)
    if cmd in ("audit-mind", "audit_mind"):
        from .audits import stage2
        return stage2.main(rest)
    if cmd == "assimilate":
        from . import lineage_cli
        return lineage_cli.assimilate(rest)
    print(_USAGE)
    return 2 if cmd in ("-h", "--help", "help") else 1


if __name__ == "__main__":
    sys.exit(main())
