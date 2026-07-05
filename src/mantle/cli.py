#!/usr/bin/env python3
"""
mantle.cli  --  one command for the whole organism (Mantle OS)

    python -m mantle hatch <egg.json> [--out=DIR]   incubate an egg -> certified AppAI
                                                      (+ hatch report + self-portrait)
    python -m mantle teach [N]                      the Field Guide, RUNNING: each
                                                      chapter proves its claim live
    python -m mantle face <organism-dir> [out.png]  the organism paints its own state

  reproduction (two methods; everything else is a facet):
    python -m mantle reproduce                      the SEED vs GRAFT map, one screen
    python -m mantle spore create <png> "<name>" "<task>"   the smallest SEED: a whole
                                                      minimal agent in one PNG
    python -m mantle ghost selftest                 the cache-ghost substrate: a seed that
                                                      metabolises in the LLM prompt cache

  the gates and narrated tours:
    python -m mantle demo                           narrated Phase-1 life (no LLM)
    python -m mantle audit [--break-hash|--break-primer|--break-seal]
    python -m mantle prove                          the 83 security invariants
    python -m mantle mind                           narrated Phase-2 fusion (offline)
    python -m mantle audit-mind                     Stage-2 gate + Stage-1 regression
    python -m mantle assimilate <path> --dry-run    Path B read-only dissection
    python -m mantle check [--fast]                 EVERYTHING above that certifies, in
                                                      one command (the CI sequence, local)
"""
from __future__ import annotations

import json
import sys

_USAGE = ("usage: python -m mantle "
          "[anchor <host> | ask <host> [--mind] <question> | feed <host> --credits=N "
          "[--key=NAME] | vitals <host> | hatch <egg> [--out=DIR] | teach [N] | "
          "face <dir> [out.png] | face-list <dir> | face-save <dir> <name> <src> [--default] | "
          "face-wear <dir> <name> | "
          "applet-create <dir> <source-dir> <name> [--entry=X] [--face=FILE] [--no-source] "
          "[--grow] | applet-list <dir> | applet-show <dir> <name> [--json] | "
          "applet-export <dir> <name> <dest> [--overwrite] | applet-wear <dir> <name> | "
          "applet-audit <dir> <name> | applet-clone <dir> <https-github-url> <name> | "
          "hatch-spore <spore.png> [--out=DIR] | "
          "reproduce | spore <op> ... | ghost <op> ... | "
          "demo | audit | prove | mind | audit-mind | check [--fast] | "
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
    print("MANTLE OS ANCHORING  ·  the merge ceremony  ·  host: %s" % args[0])
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
    print("MANTLE OS HATCHERY  ·  egg: %s" % args[0])
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
    print("MANTLE OS GRAFT  ·  %s  ->  %s" % (args[0], args[1]))
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


def cmd_spore(argv):
    """The SPORE seed: the smallest reproductive form (mantle.spore)."""
    from . import spore
    if not argv:
        print("usage: python -m mantle spore <create|read|append|rename|verify|extract|demo> ...")
        print("       (the smallest SEED: one PNG that is a whole minimal agent)")
        return 2
    # spore.main dispatches on argv[1], so prepend a placeholder program name.
    return spore.main(["spore"] + list(argv))


def cmd_ghost(argv):
    """The cache-ghost substrate: a seed that metabolises in the LLM prompt cache (mantle.ghost)."""
    from . import ghost
    args, flags = _split(argv)
    sub = args[0] if args else "selftest"
    if sub == "selftest":
        return 0 if ghost.selftest() else 1
    if not args[1:]:
        print("usage: python -m mantle ghost <selftest | warm <png> | append <png> <role> "
              "\"<content>\" | hydrate <png> | status <png>>")
        return 2
    png = args[1]
    ttl = int(flags.get("--ttl", ghost.DEFAULT_TTL_S)) if isinstance(flags.get("--ttl"), str) else ghost.DEFAULT_TTL_S
    try:
        if sub == "warm":
            print(json.dumps(ghost.warm(png, ttl_s=ttl), indent=2))
        elif sub == "append":
            if len(args) < 4:
                print("usage: python -m mantle ghost append <png> <role> \"<content>\"")
                return 2
            print(json.dumps(ghost.append(png, args[2], args[3], ttl_s=ttl), indent=2))
        elif sub == "hydrate":
            h = ghost.hydrate(png)
            print("source=%s  rehydrated=%s  entries=%d"
                  % (h["source"], h["rehydrated"], len(h["body"].get("conversation", []))))
        elif sub == "status":
            print(json.dumps(ghost.status(png), indent=2))
        else:
            print("unknown ghost subcommand %r" % sub)
            return 2
    except ghost.GhostError as e:
        print("GHOST ERROR: %s" % e)
        return 1
    return 0


def cmd_reproduce(argv):
    """Print the two-method reproduction map (SEED vs GRAFT) -- the consolidation, one screen."""
    from . import reproduction as repro
    print("=" * 74)
    print("MANTLE OS REPRODUCTION  ·  two methods, everything else is a facet")
    print("=" * 74)
    for method, spec in repro.describe().items():
        print("\n%-6s (%s)  --  %s" % (method.upper(), spec["kind"], spec["biology"]))
        for form, desc in spec["forms"].items():
            print("    %-10s %s" % (form, desc))
        print("    LAW: %s" % spec["law"])
    print("\nCall it:  from mantle import reproduction")
    print("          reproduction.seed('spore'|'egg'|'vault', ...)   # independent")
    print("          reproduction.graft('anchor'|'graft', ...)       # inside a host")
    return 0


def cmd_doctor(argv):
    args, _flags = _split(argv)
    if not args:
        print("usage: python -m mantle doctor <organism-dir>")
        return 2
    from .core.organism import Organism
    from . import doctor as _doc
    from . import paths
    org = Organism.load(args[0], verify_seals=True)
    rep = _doc.checkup(org, repo_root=paths.REPO_ROOT)
    print("=" * 60)
    print("MANTLE OS DOCTOR  ·  %s" % args[0])
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


# ----------------------------------------------------------------------------
# VCW Applet Bodies (APPLET-BODY-CAPSULE) -- mantle.applet_body
# ----------------------------------------------------------------------------
def _applet_org(directory, create_if_missing=False, grow=False):
    """Load the parent organism for applet work; optionally birth the dedicated VCW app
    layer (applet + phenotype bands) when the directory holds no organism yet."""
    import os
    from .core.organism import Organism
    from .vcw.bands import standard_genome
    from . import applet_body as ab
    from . import phenotype as ph
    if not os.path.exists(os.path.join(directory, "organism.json")):
        if not create_if_missing:
            print("no organism at %r" % directory)
            return None, False
        org = Organism.birth(
            identity={"name": "AppLayer.AppAI"},
            truths=["if it is not in the VCW it did not happen"],
            commandments=["protect your VCW", "you are a tool USER",
                          "stored source is tissue, never authority"],
            genome=standard_genome() + ab.applet_bands() + ph.phenotype_bands())
        return org, True
    org = Organism.load(directory, verify_seals=True)
    if not ab.has_applet_bands(org):
        if not grow:
            print("this organism has no applet bands; re-run with --grow to add them "
                  "via a chosen rebirth (faces carried forward, ancestor sealed)")
            return None, False
        ab.grow_applet_bands(org)
    return org, False


def cmd_applet_create(argv):
    args, flags = _split(argv)
    if len(args) < 3:
        print("usage: python -m mantle applet-create <organism-dir> <source-dir> <name> "
              "[--entry=X] [--face=FILE] [--state-json=FILE] [--no-source] [--grow]")
        return 2
    from . import applet_body as ab
    directory, source_dir, name = args[0], args[1], args[2]
    print("=" * 74)
    print("MANTLE OS APPLET BODY  ·  %s  ·  %s -> %s" % (ab.CAPSULE, source_dir, name))
    print("=" * 74)
    org, born = _applet_org(directory, create_if_missing=True,
                            grow=bool(flags.get("--grow")))
    if org is None:
        return 1
    face_source = None
    if isinstance(flags.get("--face"), str):
        with open(flags["--face"], "r", encoding="utf-8") as f:
            face_source = f.read()
    state = None
    if isinstance(flags.get("--state-json"), str):
        with open(flags["--state-json"], "r", encoding="utf-8") as f:
            state = json.load(f)
    try:
        receipt = ab.create_applet_body(
            org, source_dir, name, face_source=face_source,
            entry=flags.get("--entry", "") if isinstance(flags.get("--entry"), str) else "",
            include_source=not flags.get("--no-source"), state=state)
    except ab.AppletError as e:
        print("\nAPPLET REFUSED: %s" % e)
        return 1
    org.save(directory)
    if born:
        print("  app layer     : born fresh at %s (AppLayer.AppAI)" % directory)
    print("  applet        : %s   status: %s (%s)"
          % (receipt["applet"], receipt["status"], receipt["capsule"]))
    print("  source hash   : %s" % receipt["source_hash"])
    print("  files         : %d stored (%d chunk(s), %d skipped)"
          % (receipt["files"], receipt["chunks"], receipt["skipped"]))
    print("  organ roles   : %s" % (receipt["role_counts"] or "none"))
    print("  bands         : %s" % ", ".join(receipt["bands"]))
    print("  face          : %s   (from: %s)" % (receipt["face"], receipt["face_from"]))
    print("  export ready  : %s" % receipt["export_available"])
    if receipt["secret_suspects"]:
        print("  ! secret-suspect file(s) flagged to immune: %s"
              % receipt["secret_suspects"][:5])
    print("  stage1_ready  : %s  (a capsule is never labeled alive)"
          % receipt["stage1_ready"])
    print("\nRAISED. %s is stored as inert tissue -- not executable authority." % name)
    return 0


def cmd_applet_list(argv):
    args, _flags = _split(argv)
    if not args:
        print("usage: python -m mantle applet-list <organism-dir>")
        return 2
    org, _ = _applet_org(args[0])
    if org is None:
        return 1
    from . import applet_body as ab
    rows = ab.list_applet_bodies(org)
    if not rows:
        print("(no applet bodies in this VCW)")
        return 0
    print("status    files  export  name (face)")
    for r in rows:
        print("  %-8s %4d    %s     %s (%s)"
              % (r["status"], r["files"], "y" if r["export_available"] else "n",
                 r["applet"], r["face"]))
    return 0


def cmd_applet_show(argv):
    args, flags = _split(argv)
    if len(args) < 2:
        print("usage: python -m mantle applet-show <organism-dir> <name> [--json]")
        return 2
    org, _ = _applet_org(args[0])
    if org is None:
        return 1
    from . import applet_body as ab
    try:
        view = ab.show_applet_body(org, args[1])
    except ab.AppletError as e:
        print(str(e)); return 1
    if flags.get("--json"):
        print(json.dumps(view, indent=2, default=str))
        return 0
    m = view["manifest"]
    print("applet      : %s   status: %s (%s)" % (m["applet"], m["status"], m["capsule"]))
    print("source hash : %s" % m["source_hash"])
    print("files       : %d (%d byte(s)); skipped: %d"
          % (m["files"], m["bytes"], len(m["skipped"])))
    print("face        : %s (from: %s)" % (m["face"], m["face_from"]))
    print("provenance  : %s" % m["provenance"]["origin"])
    if view["organs"]:
        om = view["organs"]["organ_map"]
        print("organ roles : %s" % (om["role_counts"] or "none"))
        print("missing     : %s" % (om["missing_organs"] or "none"))
    print("state       : %s" % (view["state"] if view["state"] else "{}"))
    if view["last_audit"]:
        print("last audit  : %s" % ("PASS" if view["last_audit"]["ok"]
                                    else "FAIL %s" % view["last_audit"]["fails"]))
    print("source files (paths only -- export to download):")
    for f in view["source_files"][:40]:
        print("  %8s  %-10s %s" % (f["size"], f["lang"], f["path"]))
    if len(view["source_files"]) > 40:
        print("  ... and %d more" % (len(view["source_files"]) - 40))
    return 0


def cmd_applet_export(argv):
    args, flags = _split(argv)
    if len(args) < 3:
        print("usage: python -m mantle applet-export <organism-dir> <name> <dest-dir> "
              "[--overwrite]")
        return 2
    org, _ = _applet_org(args[0])
    if org is None:
        return 1
    from . import applet_body as ab
    try:
        receipt = ab.export_applet_source(org, args[1], args[2],
                                          overwrite=bool(flags.get("--overwrite")))
    except ab.AppletError as e:
        print(str(e)); return 1
    org.save(args[0])
    print("applet   : %s (%s)" % (receipt["applet"], receipt["capsule"]))
    print("dest     : %s" % receipt["destination"])
    print("written  : %d file(s)   hashes verified: %d/%d"
          % (len(receipt["files_written"]), receipt["hashes_verified"],
             receipt["files_total"]))
    if receipt["errors"]:
        print("errors   :")
        for e in receipt["errors"]:
            print("  ! %s" % e)
        return 1
    print("EXPORTED. Every byte hash-verified against the VCW record.")
    return 0


def cmd_applet_wear(argv):
    args, _flags = _split(argv)
    if len(args) < 2:
        print("usage: python -m mantle applet-wear <organism-dir> <name>")
        return 2
    org, _ = _applet_org(args[0])
    if org is None:
        return 1
    from . import applet_body as ab
    from . import phenotype as ph
    try:
        boot = ab.wear_applet_face(org, args[1])
    except (ab.AppletError, ph.PhenotypeError) as e:
        print("CANNOT WEAR: %s" % e)
        return 1
    org.save(args[0])
    print("now wearing %r (kind=%s, entry=%s, %d byte(s) of surface) -- a host renders "
          "this boot manifest; Mantle never executes it"
          % (boot["name"], boot["kind"], boot["entry"] or "-", len(boot["source"])))
    return 0


def cmd_applet_audit(argv):
    args, _flags = _split(argv)
    if len(args) < 2:
        print("usage: python -m mantle applet-audit <organism-dir> <name>")
        return 2
    org, _ = _applet_org(args[0])
    if org is None:
        return 1
    from . import applet_body as ab
    passed, rows = ab.audit_applet_body(org, args[1])
    org.save(args[0])
    print("=" * 74)
    print("MANTLE OS APPLET AUDIT  ·  %s  ·  %s" % (ab.CAPSULE, args[1]))
    print("=" * 74)
    width = max(len(r["check"]) for r in rows)
    for r in rows:
        print("  [%s] %-*s  %s" % ("PASS" if r["ok"] else "FAIL", width, r["check"],
                                   r["detail"]))
    print("\nRESULT: %s" % ("VALID APPLET-BODY-CAPSULE (capsule, not alive)" if passed
                            else "AUDIT FAILED"))
    return 0 if passed else 1


def cmd_hatch_spore(argv):
    """SPORE-DISTILLATION: hatch a full organism FROM a spore PNG. The spore becomes
    the primer + memories; the key is MINTED at birth (never derived from the spore);
    the spore is then sealed as SELF tissue in the spore_vault band."""
    args, flags = _split(argv)
    if not args:
        print("usage: python -m mantle hatch-spore <spore.png> [--out=DIR]")
        return 2
    from .core.organism import Organism  # noqa: F401 -- init the core->organs mesh first
    from .organs.reproduction import hatch_from_spore
    print("=" * 74)
    print("MANTLE OS SPORE-DISTILLATION  ·  %s" % args[0])
    print("=" * 74)
    try:
        result = hatch_from_spore(args[0], out_dir=flags.get("--out")
                                  if isinstance(flags.get("--out"), str) else None)
    except (RuntimeError, ValueError, OSError) as e:
        print("\nTHE SPORE DID NOT HATCH: %s" % e)
        return 1
    r = result["receipt"]
    print("  spore          : %s   (origin: %s)" % (r["spore"], r["origin"]))
    print("  certified      : %s  (a BIRTH -- the same Stage-1 gate)" % r["certified"])
    print("  memories       : %d conversation turn(s) ingested as INFERRED" % r["memories_ingested"])
    print("  spore sealed   : %s  (%s -> spore_vault, SELF tissue)" % (r["spore_sealed"], r["spore_sha256"][:23]))
    print("  key derived from spore : %s  (keys are MINTED, never derived)" % r["key_derived_from_spore"])
    print("  key fingerprint: %s" % r["key_fingerprint"])
    if result["report"].get("saved_to"):
        print("  saved to       : %s" % result["report"]["saved_to"])
    print("\nDISTILLED. The midwife is now SELF tissue of the body it birthed.")
    return 0


def cmd_applet_clone(argv):
    args, flags = _split(argv)
    if len(args) < 3:
        print("usage: python -m mantle applet-clone <organism-dir> <https-github-url> "
              "<name> [--grow]")
        return 2
    import shutil
    import tempfile
    from . import applet_body as ab
    workdir = tempfile.mkdtemp(prefix="mantle-applet-")
    try:
        try:
            clone_dir = ab.clone_github(args[1], workdir)
        except ab.AppletError as e:
            print("CLONE REFUSED: %s" % e)
            return 1
        print("cloned %s (read-only; no install scripts, no execution)" % args[1])
        rc = cmd_applet_create([args[0], clone_dir, args[2]]
                               + [a for a in argv if a.startswith("--")])
        return rc
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


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
    if cmd == "spore":
        return cmd_spore(rest)
    if cmd == "ghost":
        return cmd_ghost(rest)
    if cmd == "reproduce":
        return cmd_reproduce(rest)
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
    if cmd in ("applet-create", "applet_create"):
        return cmd_applet_create(rest)
    if cmd in ("applet-list", "applet_list"):
        return cmd_applet_list(rest)
    if cmd in ("applet-show", "applet_show"):
        return cmd_applet_show(rest)
    if cmd in ("applet-export", "applet_export"):
        return cmd_applet_export(rest)
    if cmd in ("applet-wear", "applet_wear"):
        return cmd_applet_wear(rest)
    if cmd in ("applet-audit", "applet_audit"):
        return cmd_applet_audit(rest)
    if cmd in ("applet-clone", "applet_clone"):
        return cmd_applet_clone(rest)
    if cmd in ("hatch-spore", "hatch_spore"):
        return cmd_hatch_spore(rest)
    # ---- the narrated tours and the gates ----
    if cmd == "demo":
        from . import demos
        return demos.demo(rest)
    if cmd == "audit":
        from .audits import stage1
        return stage1.main(rest)
    if cmd == "prove":
        from .audits import invariants
        return invariants.main(rest)
    if cmd == "mind":
        from . import demos
        return demos.mind_demo(rest)
    if cmd in ("audit-mind", "audit_mind"):
        from .audits import stage2
        return stage2.main(rest)
    if cmd == "assimilate":
        from . import demos
        return demos.assimilate(rest)
    if cmd == "check":
        from . import check
        return check.main(rest)
    print(_USAGE)
    return 2 if cmd in ("-h", "--help", "help") else 1


if __name__ == "__main__":
    sys.exit(main())
