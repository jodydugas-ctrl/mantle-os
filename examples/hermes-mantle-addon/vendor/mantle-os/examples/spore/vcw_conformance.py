#!/usr/bin/env python3
"""
vcw_conformance.py -- prove a SPORE PNG is a conformant VCW SUBSTRATE.

The claim this script defends:

    VCW is not one file format. It is a MEMORY GRAMMAR -- a law about how state is stored,
    grown, proven, and exposed. The 800-layer cube (`vcw-cube-png-v2`) is one body plan that
    obeys that law. A SPORE PNG is ANOTHER: a single image that carries its whole memory in
    its top-half colour field. So the spore is not a toy Mantle; it is a demonstration that
    the VCW substrate can MOLT into different media.

        VCW is the law. The cube is one body plan; the PNG is another.

This audit states the law as nine properties (the memory grammar) and checks, live, that a
SPORE PNG exhibits every one -- each mapped to the concrete SPORE mechanism that provides it.
It also drives the PNG through VCW's own three verbs (read / retrieve / append) via a thin
adapter, proving the same read/write grammar the cube speaks works on the PNG medium.

    python examples/spore/vcw_conformance.py               # prove a fresh spore
    python examples/spore/vcw_conformance.py <a_spore.png> # prove a given PNG

Exit code 0 = CONFORMANT, non-zero = NOT CONFORMANT.
Dependency: Pillow (PIL). Standard library otherwise.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile

from PIL import Image
from PIL.PngImagePlugin import PngInfo

try:
    from mantle import spore
except ImportError:
    sys.path.insert(0, os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
    from mantle import spore


# ---------------------------------------------------------------------------
# The VCW memory grammar -- the law a substrate must obey to BE a VCW layer.
# ---------------------------------------------------------------------------
MEMORY_GRAMMAR = [
    ("addressable region",
     "a defined storage region you can index into by position"),
    ("canonical payload",
     "one checksummed source-of-truth state, distinct from any view of it"),
    ("append-only evolution",
     "state grows by appending immutable records; append before overwrite"),
    ("integrity checks",
     "tampering with the store is detectable, not silent"),
    ("repair signaling",
     "local damage is repaired where possible and reported otherwise -- never invented"),
    ("embedded boot instructions",
     "the substrate is self-describing: it carries how to read itself"),
    ("authority rules",
     "which source wins when copies disagree is stated, not assumed"),
    ("read/write protocol",
     "a fixed verb set to read the stream, retrieve one item, and append"),
    ("display separate from substrate",
     "a visible surface distinct from the canonical memory region"),
]


# ---------------------------------------------------------------------------
# The PNG spoken through VCW's three verbs -- proof the PNG IS a VCW layer.
# A spore is a single implicit band ("conversation"); the cube's log-json driver speaks the
# same read / retrieve(address) / append(value) grammar this adapter exposes.
# ---------------------------------------------------------------------------
class SporeAsVCWLayer:
    def __init__(self, path: str):
        self.path = path

    def read(self):                                   # cube: cube.read(band)
        return spore.read_spore(self.path)["state"]["conversation"]

    def retrieve(self, address):                      # cube: cube.retrieve(band, address)
        conv = self.read()
        i = int(address)
        return conv[i] if 0 <= i < len(conv) else None

    def append(self, value):                          # cube: cube.append(band, value)
        role, content = value
        return spore.append_turn(self.path, role, content)


def _resave(img, srcpath, dst):
    """Re-save `img` preserving the PNG text metadata found in `srcpath`."""
    meta = Image.open(srcpath).text
    pi = PngInfo()
    for k, v in meta.items():
        pi.add_itxt(k, v)
    img.save(dst, "PNG", pnginfo=pi)


class Conformance:
    def __init__(self):
        self.rows = []      # (property, ok, mechanism/evidence)

    def prove(self, prop, ok, mechanism):
        self.rows.append((prop, bool(ok), mechanism))
        return bool(ok)

    @property
    def ok(self):
        return all(ok for _, ok, _ in self.rows)


def audit(path: str) -> Conformance:
    c = Conformance()
    d = tempfile.mkdtemp(prefix="vcw_conf_")
    try:
        info = spore.read_spore(path)
        state, header, meta = info["state"], info["header"], info["metadata"]
        layer = SporeAsVCWLayer(path)

        # 1. addressable region -----------------------------------------------
        region = header.get("vcw_region")
        e0 = layer.retrieve(0)
        c.prove("addressable region",
                region == [spore.VCW_X, spore.VCW_Y, spore.VCW_W, spore.VCW_H]
                and (e0 is None or e0["id"] == 0),
                f"VCW region {region}; block index i -> (i%W, i//W); retrieve(0) O(1)")

        # 2. canonical payload -------------------------------------------------
        recomputed = spore._sha(spore._payload_bytes(state))
        c.prove("canonical payload",
                recomputed == header.get("payload_checksum"),
                f"header.payload_checksum {header.get('payload_checksum')} == sha(payload)")

        # 3. append-only evolution --------------------------------------------
        ids = [e["id"] for e in state.get("conversation", [])]
        before = len(ids)
        p = os.path.join(d, "grow.png")
        shutil.copyfile(path, p)
        SporeAsVCWLayer(p).append(("user", "conformance: one more turn"))
        grown = [e["id"] for e in spore.read_spore(p)["state"]["conversation"]]
        c.prove("append-only evolution",
                ids == list(range(before)) and grown == list(range(before + 1))
                and grown[:before] == ids,
                f"ids ordered 0..n ({before} -> {before + 1}); prefix preserved, never rewritten")

        # 4. integrity checks: broken magic must be refused -------------------
        q = os.path.join(d, "tamper.png")
        spore.create_spore("CONF", "integrity", path=q)
        img = Image.open(q).convert("RGBA"); px = img.load()
        px[0, 0] = (0, 0, 0, spore.compute_T(0, 0, 0))    # wipe the first magic bytes
        _resave(img, q, q)
        refused = False
        try:
            spore.read_spore(q)
        except ValueError:
            refused = True
        c.prove("integrity checks", refused,
                "magic + payload_checksum; a wiped header is REFUSED, not silently read")

        # 5. repair signaling: 1-bit repaired, 2-bit reported -----------------
        r = os.path.join(d, "repair.png")
        spore.create_spore("CONF", "repair", path=r)
        spore.append_turn(r, "user", "protect me")
        img = Image.open(r).convert("RGBA"); px = img.load()
        rr, gg, bb, aa = px[4, 0]
        px[4, 0] = (rr ^ 0b100, gg, bb, aa)               # single-bit flip
        _resave(img, r, r)
        one = spore.read_spore(r)["corrections"]
        spore.create_spore("CONF", "repair2", path=r)
        spore.append_turn(r, "user", "detect tampering")
        img = Image.open(r).convert("RGBA"); px = img.load()
        rr, gg, bb, aa = px[7, 0]
        px[7, 0] = (rr ^ 0b11, gg, bb, aa)                # two-bit flip
        _resave(img, r, r)
        two = spore.read_spore(r)["corrections"]
        c.prove("repair signaling",
                one["repaired"] >= 1 and one["corrupt"] == 0
                and (two["corrupt"] >= 1 or two["notes"]),
                "per-block Hamming SECDED in alpha: repair 1 bit, report 2 (never invent)")

        # 6. embedded boot instructions ---------------------------------------
        et_ok, et_detail = spore._check_embedded_tool(state)
        c.prove("embedded boot instructions",
                header.get("magic") == "SPOREPNG"
                and meta.get("Bootloader") == spore.BOOTLOADER_TEXT and et_ok,
                "magic+version+header, BOOTLOADER strip, and a runnable embedded reader/writer")

        # 7. authority rules ---------------------------------------------------
        a = os.path.join(d, "auth.png")
        spore.create_spore("CANON", "authority", path=a)
        img = Image.open(a); m = dict(img.text); m["Spore-Name"] = "META-TAMPER"
        pi = PngInfo()
        for k, v in m.items():
            pi.add_itxt(k, v)
        img.convert("RGBA").save(a, "PNG", pnginfo=pi)
        ai = spore.read_spore(a)
        mm = ai["name_mirror_mismatch"]
        c.prove("authority rules",
                bool(ai["authority"]) and mm and mm["canonical"] == "vcw_payload"
                and ai["state"]["identity"]["spore_name"] == "CANON",
                "AUTHORITY table: VCW payload is canonical; metadata is only a mirror")

        # 8. read/write protocol: the three verbs round-trip ------------------
        conv = layer.read()
        rendered = os.path.join(d, "rt.png")
        spore.render_spore(spore.read_spore(path)["state"], rendered)
        rt = SporeAsVCWLayer(rendered).read()
        c.prove("read/write protocol",
                isinstance(conv, list) and rt == conv
                and (layer.retrieve(0) == conv[0] if conv else True),
                "read()/retrieve(address)/append(value) -- the same grammar the cube speaks")

        # 9. display separate from substrate ----------------------------------
        disp = header.get("display_region")
        boot = header.get("boot_strip_region")
        vy0, vy1 = spore.VCW_Y, spore.VCW_Y + spore.VCW_H
        dy0 = spore.DISP_Y
        disjoint = dy0 >= vy1                              # display starts where the VCW ends
        boot_in_disp = (boot and boot[1] == spore.DISP_Y
                        and boot[3] <= spore.DISP_H)
        c.prove("display separate from substrate",
                disp == [spore.DISP_X, spore.DISP_Y, spore.DISP_W, spore.DISP_H]
                and disjoint and boot_in_disp,
                f"canonical VCW y=[{vy0},{vy1}) vs visible display y>={dy0}; regions disjoint")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return c


def main(argv):
    if len(argv) > 1:
        path = argv[1]
        created = None
    else:
        path = tempfile.mktemp(suffix="_spore.png")
        spore._demo(path)                                 # a small, populated spore
        created = path

    try:
        c = audit(path)
    finally:
        if created and os.path.exists(created):
            os.remove(created)

    print("=" * 74)
    print("VCW SUBSTRATE CONFORMANCE  --  is this PNG a valid VCW layer?")
    print("=" * 74)
    print("\nThe memory grammar (the law), and the SPORE mechanism that provides each:\n")
    width = max(len(p) for p, _, _ in c.rows)
    for prop, ok, mechanism in c.rows:
        print(f"  [{'OK' if ok else 'XX'}] {prop.ljust(width)}  {mechanism}")
    print("\n" + "-" * 74)
    verdict = "CONFORMANT" if c.ok else "NOT CONFORMANT"
    print(f"RESULT: {verdict}  --  VCW is the law; the cube is one body plan, this PNG is another.")
    print("=" * 74)
    return 0 if c.ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
