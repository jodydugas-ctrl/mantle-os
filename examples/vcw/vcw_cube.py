#!/usr/bin/env python3
"""
vcw_cube.py  --  VCW Cube reference codec  (format: vcw-cube-png-v2)

The VCW ("Visual Cortex Workspace") cube is the durable nervous-memory substrate
of a Mantle AppAI -- the heart of its nervous system. It is a stack of 800 square
RGBA layers (800 x 800 pixels each). Every layer is a real, valid PNG image, so the
whole organism's memory is a directory of pictures you can open in any image viewer.
The cube container is a ZIP holding those PNGs plus two small JSON descriptors.

This module is pure standard library (zlib, struct, zipfile, json, os, hashlib).
No third-party packages, no PIL. It is meant to be READ as much as RUN: an LLM that
reads this file should come away knowing exactly how to address, write, and read a
VCW cube.

--------------------------------------------------------------------------------
MENTAL MODEL
--------------------------------------------------------------------------------
  cube            = ordered stack of 800 layers           (index 0 .. 799)
  layer           = one 800x800 RGBA image = a flat byte stream of 2,560,000 bytes
  band            = a named, contiguous RANGE of layers reserved for one purpose
  entry           = one immutable record appended into a band's payload
  body entry      = one of four genome records (.000..003) that define identity

  LEGACY NOTE (read this): storing the four body entries *inside* the cube (reserved
  layers 4-7) is a SUBSTRATE PRIMITIVE shown here for completeness. The canonical Mantle
  architecture SUPERSEDES it: identity lives in the BODY (see body.py / GUIDE.md Part I
  Sec.4), not the cube, so it survives rebirth and the cube stays pure experiential memory.
  Putting the Primer/commandments in the cube is a Stage-1 hard fail (HF-B45). Build against
  Organism/Body (lineage.py, body.py); treat the in-cube genome as legacy.

ADDRESSING
  A single byte inside a layer is addressed by (layer, x, y):

        offset = (y * SIDE + x) * CHANNELS          # CHANNELS = 4 (R,G,B,A)

  We do NOT hand-place bytes at pixel coordinates for normal use; instead each
  layer's pixel stream carries two length-prefixed JSON blobs -- a Layer Boot
  Sector and a Payload -- behind an 8-byte magic. The (layer,x,y) formula is the
  primitive the reference-resolver and any low-level tool can rely on.

LAYER PIXEL STREAM LAYOUT (inside the decoded RGBA bytes of one layer)
  [ 8 bytes  MAGIC = b"VCWPNG2\n" ]
  [ 4 bytes  uint32 length of boot JSON   ][ boot JSON utf-8 ]
  [ 4 bytes  uint32 length of payload JSON][ payload JSON utf-8 ]
  [ zero padding up to LAYER_BYTES ]

CONTAINER (a .vcw file is just a ZIP)
  manifest.json     -- cube-level descriptor (format, dims, band map, generation)
  cube_boot.json    -- the Cube Boot Sector (authoritative band map + checksums)
  layers/000.png .. 799.png   -- every layer as a real PNG

--------------------------------------------------------------------------------
"""
from __future__ import annotations

import json
import os
import struct
import time
import zlib
import zipfile
from typing import Any, Dict, List, Optional, Tuple

# ----------------------------------------------------------------------------
# Format constants
# ----------------------------------------------------------------------------
VCW_FORMAT   = "vcw-cube-png-v2"
LAYER_COUNT  = 800
SIDE         = 800
CHANNELS     = 4                       # RGBA
LAYER_BYTES  = SIDE * SIDE * CHANNELS  # 2,560,000 bytes per layer
MAGIC        = b"VCWPNG2\n"            # 8 bytes, opens every layer's payload stream

# ----------------------------------------------------------------------------
# Reserved band map.  (name -> (first_layer, last_layer inclusive, archetype, private))
# Layers 0-3 are the Cube Boot Sector. Layers 4-7 are the Genome (body entries).
# ----------------------------------------------------------------------------
BOOT_LAYERS   = (0, 3)
GENOME_LAYERS = (4, 7)   # bodyentry .000 .001 .002 .003 -> layers 4,5,6,7

RESERVED_BANDS: Dict[str, Dict[str, Any]] = {
    #  name          first  last  archetype     private
    "prime":       {"range": (8, 99),    "archetype": "reference", "private": False},
    "identity":    {"range": (100, 149), "archetype": "summary",   "private": False},
    "facts":       {"range": (150, 199), "archetype": "table",     "private": False},
    "events":      {"range": (200, 249), "archetype": "log",       "private": False},
    "discoveries": {"range": (250, 299), "archetype": "summary",   "private": False},
    "senses":      {"range": (300, 399), "archetype": "log",       "private": False},
    "immune":      {"range": (400, 449), "archetype": "audit",     "private": False},
    "brain":       {"range": (450, 499), "archetype": "dispatch",  "private": False},
    "thoughts":    {"range": (500, 549), "archetype": "log",       "private": True},
}
APP_BAND_RANGE  = (550, 749)   # caller-defined application bands
TAIL_RANGE      = (750, 799)   # reserved scratch / future use

# Body entry names, in mandatory load order.  Each maps to one Genome layer.
BODY_ENTRIES = ["bodyentry.000", "bodyentry.001", "bodyentry.002", "bodyentry.003"]
BODY_ENTRY_TITLES = {
    "bodyentry.000": "Primer",            # immutable post-genesis
    "bodyentry.001": "Immunization",
    "bodyentry.002": "Special Instructions",
    "bodyentry.003": "Inheritance",       # rebirth-write-only
}

PRIVATE_FLAG = 0x01  # set in a layer boot sector's "private" field; veiled on read


# ============================================================================
# PNG codec  (hand-rolled, pure stdlib).  We WRITE filter type 0 (None) scanlines
# and zlib-compress them; we can READ all five PNG filter types for robustness.
# ============================================================================
def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def encode_png_rgba(raw: bytes, width: int = SIDE, height: int = SIDE) -> bytes:
    """Encode a flat RGBA byte buffer (len == width*height*4) into PNG bytes."""
    if len(raw) != width * height * CHANNELS:
        raise ValueError("encode_png_rgba: raw length %d != %d"
                         % (len(raw), width * height * CHANNELS))
    stride = width * CHANNELS
    # Prepend filter-type byte 0 (None) to each scanline.
    out = bytearray()
    for y in range(height):
        out.append(0)
        out += raw[y * stride:(y + 1) * stride]
    sig  = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)  # 8-bit, color type 6 = RGBA
    idat = zlib.compress(bytes(out), 6)
    return (sig + _png_chunk(b"IHDR", ihdr)
            + _png_chunk(b"IDAT", idat) + _png_chunk(b"IEND", b""))


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def decode_png_rgba(png: bytes) -> bytes:
    """Decode PNG bytes into a flat RGBA byte buffer. Handles filter types 0-4."""
    if png[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("decode_png_rgba: not a PNG")
    pos = 8
    width = height = 0
    idat = bytearray()
    while pos < len(png):
        (length,) = struct.unpack(">I", png[pos:pos + 4])
        tag = png[pos + 4:pos + 8]
        data = png[pos + 8:pos + 8 + length]
        pos += 12 + length
        if tag == b"IHDR":
            width, height, depth, ctype = struct.unpack(">IIBB", data[:10])
            if depth != 8 or ctype != 6:
                raise ValueError("decode_png_rgba: expected 8-bit RGBA")
        elif tag == b"IDAT":
            idat += data
        elif tag == b"IEND":
            break
    raw = zlib.decompress(bytes(idat))
    stride = width * CHANNELS
    out = bytearray(width * height * CHANNELS)
    prev = bytearray(stride)
    src = 0
    for y in range(height):
        ftype = raw[src]; src += 1
        line = bytearray(raw[src:src + stride]); src += stride
        if ftype == 0:
            pass
        elif ftype == 1:  # Sub
            for i in range(CHANNELS, stride):
                line[i] = (line[i] + line[i - CHANNELS]) & 0xFF
        elif ftype == 2:  # Up
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ftype == 3:  # Average
            for i in range(stride):
                a = line[i - CHANNELS] if i >= CHANNELS else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif ftype == 4:  # Paeth
            for i in range(stride):
                a = line[i - CHANNELS] if i >= CHANNELS else 0
                c = prev[i - CHANNELS] if i >= CHANNELS else 0
                line[i] = (line[i] + _paeth(a, prev[i], c)) & 0xFF
        else:
            raise ValueError("decode_png_rgba: bad filter type %d" % ftype)
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return bytes(out)


# ============================================================================
# Layer payload (boot sector + payload JSON) <-> RGBA byte stream
# ============================================================================
def build_layer_rgba(boot: Dict[str, Any], payload: Dict[str, Any]) -> bytes:
    """Serialize a Layer Boot Sector + payload into a full LAYER_BYTES RGBA stream."""
    boot_b = json.dumps(boot, separators=(",", ":"), sort_keys=True).encode("utf-8")
    pay_b  = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    body = (MAGIC + struct.pack(">I", len(boot_b)) + boot_b
            + struct.pack(">I", len(pay_b)) + pay_b)
    if len(body) > LAYER_BYTES:
        raise ValueError("layer payload overflow: %d > %d bytes" % (len(body), LAYER_BYTES))
    return body + b"\x00" * (LAYER_BYTES - len(body))


def parse_layer_rgba(raw: bytes) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Parse a LAYER_BYTES RGBA stream back into (boot, payload). Empty layer -> (None, None)."""
    if raw[:8] != MAGIC:
        return None, None
    pos = 8
    (blen,) = struct.unpack(">I", raw[pos:pos + 4]); pos += 4
    boot = json.loads(raw[pos:pos + blen].decode("utf-8")); pos += blen
    (plen,) = struct.unpack(">I", raw[pos:pos + 4]); pos += 4
    payload = json.loads(raw[pos:pos + plen].decode("utf-8"))
    return boot, payload


# ============================================================================
# Boot sectors
# ============================================================================
def make_layer_boot(band: str, layer_index: int, archetype: str,
                    private: bool = False) -> Dict[str, Any]:
    return {
        "band": band,
        "layer": layer_index,
        "archetype": archetype,
        "private": PRIVATE_FLAG if private else 0,
        "v": 2,
    }


def make_cube_boot(generation: int, band_map: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "format": VCW_FORMAT,
        "side": SIDE,
        "layers": LAYER_COUNT,
        "channels": CHANNELS,
        "generation": generation,
        "boot_layers": list(BOOT_LAYERS),
        "genome_layers": list(GENOME_LAYERS),
        "bands": band_map,
        "app_band_range": list(APP_BAND_RANGE),
        "tail_range": list(TAIL_RANGE),
    }


# ============================================================================
# Entries
# ============================================================================
def make_entry(opcode: str, content: Any, author: str = "BODY",
               source: str = "") -> Dict[str, Any]:
    """Create one immutable band/body entry record."""
    ts = time.time()
    body = {
        "id": None,                  # assigned on append
        "ts": ts,
        "opcode": opcode,            # e.g. WRITE, NOTE, SENSE, DISPATCH, AUDIT
        "author": author,            # BODY | MIND | <organ name>
        "source": source,            # provenance string / reference
        "content": content,
        "tombstone": False,
        "quarantined": False,
    }
    body["hash"] = _entry_hash(body)
    return body


# The entry hash lives in one place now (entry.py). For an entry with no extra fields the
# non-volatile set is {ts, opcode, author, source, content}, so this reproduces the legacy
# codec hash exactly -- the base codec keeps verifying unchanged.
from entry import entry_hash as _entry_hash  # noqa: E402


def visible_entries(payload: Dict[str, Any], reveal_private: bool = False,
                    is_private_layer: bool = False) -> List[Dict[str, Any]]:
    """Apply the VEIL: hide tombstoned + quarantined entries always; hide all
    entries of a private layer unless reveal_private is set (the MIND veil)."""
    if is_private_layer and not reveal_private:
        return []
    return [e for e in payload.get("entries", [])
            if not e.get("tombstone") and not e.get("quarantined")]


# ============================================================================
# Cube  --  the in-memory representation + container I/O
# ============================================================================
class Cube:
    """An in-memory VCW cube. Layers are lazily materialized; only touched layers
    carry a real payload. Persists as a ZIP container via save()/load()."""

    def __init__(self, generation: int = 0):
        self.generation = generation
        # layer_index -> (boot dict, payload dict)
        self.layers: Dict[int, Tuple[Dict[str, Any], Dict[str, Any]]] = {}
        self._next_id = 1

    # ---- genesis ----------------------------------------------------------
    @classmethod
    def genesis(cls, primer_content: Any = None,
                immunization: Any = None) -> "Cube":
        """Create a fresh cube: boot sector, genome (body entries), reserved bands."""
        cube = cls(generation=0)
        # Genome / body entries .000..003
        for i, name in enumerate(BODY_ENTRIES):
            layer = GENOME_LAYERS[0] + i
            boot = make_layer_boot(name, layer, "genome", private=False)
            content = {"bodyentry.000": primer_content,
                       "bodyentry.001": immunization,
                       "bodyentry.002": None,
                       "bodyentry.003": None}.get(name)
            entries = []
            if content is not None:
                e = make_entry("GENOME", content, author="BODY", source=name)
                e["id"] = i
                entries.append(e)
            cube.layers[layer] = (boot, {"name": name, "title": BODY_ENTRY_TITLES[name],
                                         "entries": entries})
        # Reserved bands -- materialize each band's HEAD layer with a boot sector.
        for name, spec in RESERVED_BANDS.items():
            head = spec["range"][0]
            boot = make_layer_boot(name, head, spec["archetype"], spec["private"])
            cube.layers[head] = (boot, {"band": name, "archetype": spec["archetype"],
                                        "entries": []})
        return cube

    # ---- band addressing --------------------------------------------------
    @staticmethod
    def band_head(band: str) -> int:
        if band in RESERVED_BANDS:
            return RESERVED_BANDS[band]["range"][0]
        raise KeyError("unknown reserved band: %s" % band)

    @staticmethod
    def is_private(band: str) -> bool:
        return RESERVED_BANDS.get(band, {}).get("private", False)

    # ---- append / read ----------------------------------------------------
    def append(self, band: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        head = self.band_head(band)
        boot, payload = self.layers[head]
        entry = dict(entry)
        entry["id"] = self._next_id
        self._next_id += 1
        payload.setdefault("entries", []).append(entry)
        return entry

    def append_body_entry(self, name: str, content: Any,
                          author: str = "BODY") -> Dict[str, Any]:
        if name not in BODY_ENTRIES:
            raise KeyError("not a body entry: %s" % name)
        if name == "bodyentry.000":
            # Primer is immutable post-genesis.
            _, payload = self.layers[GENOME_LAYERS[0]]
            if payload.get("entries"):
                raise PermissionError("bodyentry.000 (Primer) is immutable post-genesis")
        layer = GENOME_LAYERS[0] + BODY_ENTRIES.index(name)
        boot, payload = self.layers[layer]
        e = make_entry("GENOME", content, author=author, source=name)
        e["id"] = self._next_id; self._next_id += 1
        payload.setdefault("entries", []).append(e)
        return e

    def read(self, band: str, reveal_private: bool = False) -> List[Dict[str, Any]]:
        head = self.band_head(band)
        if head not in self.layers:
            return []
        _, payload = self.layers[head]
        return visible_entries(payload, reveal_private=reveal_private,
                               is_private_layer=self.is_private(band))

    def read_body_entry(self, name: str) -> List[Dict[str, Any]]:
        layer = GENOME_LAYERS[0] + BODY_ENTRIES.index(name)
        _, payload = self.layers[layer]
        return visible_entries(payload)

    # ---- mark (tombstone / quarantine) ------------------------------------
    def _find(self, band: str, entry_id: int):
        head = self.band_head(band)
        _, payload = self.layers[head]
        for e in payload.get("entries", []):
            if e.get("id") == entry_id:
                return e
        return None

    def tombstone(self, band: str, entry_id: int) -> bool:
        e = self._find(band, entry_id)
        if e is None:
            return False
        e["tombstone"] = True
        return True

    def quarantine(self, band: str, entry_id: int) -> bool:
        e = self._find(band, entry_id)
        if e is None:
            return False
        e["quarantined"] = True
        return True

    # ---- verify -----------------------------------------------------------
    def verify(self) -> List[str]:
        """Return a list of integrity problems. Empty list == healthy cube."""
        problems: List[str] = []
        # Genome present and ordered.
        for i, name in enumerate(BODY_ENTRIES):
            layer = GENOME_LAYERS[0] + i
            if layer not in self.layers:
                problems.append("missing genome layer for %s" % name)
        # Primer must exist.
        g0 = self.layers.get(GENOME_LAYERS[0])
        if not g0 or not g0[1].get("entries"):
            problems.append("bodyentry.000 (Primer) is empty -- not yet born")
        # Reserved band heads present with correct boot sector.
        for name, spec in RESERVED_BANDS.items():
            head = spec["range"][0]
            if head not in self.layers:
                problems.append("missing band head for %s" % name)
                continue
            boot, _ = self.layers[head]
            if boot.get("band") != name:
                problems.append("band head %d mislabeled: %r != %r"
                                % (head, boot.get("band"), name))
        # Entry hashes intact.
        for idx, (boot, payload) in self.layers.items():
            for e in payload.get("entries", []):
                if "hash" in e and e["hash"] != _entry_hash(e):
                    problems.append("entry hash mismatch in layer %d id=%s"
                                    % (idx, e.get("id")))
        return problems

    # ---- container I/O ----------------------------------------------------
    def _band_map(self) -> Dict[str, Any]:
        return {name: {"range": list(spec["range"]),
                       "archetype": spec["archetype"],
                       "private": spec["private"]}
                for name, spec in RESERVED_BANDS.items()}

    def save(self, path: str) -> None:
        """Staged commit: write to <path>.stage, verify, then atomically replace."""
        stage = path + ".stage"
        cube_boot = make_cube_boot(self.generation, self._band_map())
        manifest = {
            "format": VCW_FORMAT, "side": SIDE, "layers": LAYER_COUNT,
            "channels": CHANNELS, "generation": self.generation,
            "materialized_layers": sorted(self.layers.keys()),
            "next_id": self._next_id,
        }
        with zipfile.ZipFile(stage, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("manifest.json", json.dumps(manifest, indent=2))
            z.writestr("cube_boot.json", json.dumps(cube_boot, indent=2))
            for idx in sorted(self.layers.keys()):
                boot, payload = self.layers[idx]
                raw = build_layer_rgba(boot, payload)
                png = encode_png_rgba(raw)
                z.writestr("layers/%03d.png" % idx, png)
        # Verify the staged file reads back cleanly before committing.
        check = Cube.load(stage)
        problems = check.verify()
        if problems:
            os.remove(stage)
            raise RuntimeError("staged cube failed verify: %s" % problems)
        os.replace(stage, path)

    @classmethod
    def load(cls, path: str) -> "Cube":
        with zipfile.ZipFile(path, "r") as z:
            manifest = json.loads(z.read("manifest.json"))
            cube = cls(generation=manifest.get("generation", 0))
            cube._next_id = manifest.get("next_id", 1)
            for nm in z.namelist():
                if nm.startswith("layers/") and nm.endswith(".png"):
                    idx = int(nm[len("layers/"):-len(".png")])
                    raw = decode_png_rgba(z.read(nm))
                    boot, payload = parse_layer_rgba(raw)
                    if boot is not None:
                        cube.layers[idx] = (boot, payload)
        return cube


# ============================================================================
# CLI
# ============================================================================
def _cli(argv: List[str]) -> int:
    import argparse
    p = argparse.ArgumentParser(prog="vcw_cube", description="VCW cube codec (vcw-cube-png-v2)")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create", help="genesis a new cube")
    c.add_argument("path")
    c.add_argument("--primer", default="newborn AppAI")

    a = sub.add_parser("append", help="append an entry to a band")
    a.add_argument("path"); a.add_argument("band")
    a.add_argument("content"); a.add_argument("--opcode", default="WRITE")
    a.add_argument("--author", default="BODY")

    r = sub.add_parser("read", help="read visible entries of a band")
    r.add_argument("path"); r.add_argument("band")
    r.add_argument("--reveal-private", action="store_true")

    t = sub.add_parser("tombstone", help="tombstone an entry"); t.add_argument("path")
    t.add_argument("band"); t.add_argument("id", type=int)

    q = sub.add_parser("quarantine", help="quarantine an entry"); q.add_argument("path")
    q.add_argument("band"); q.add_argument("id", type=int)

    v = sub.add_parser("verify", help="verify cube integrity"); v.add_argument("path")
    i = sub.add_parser("inspect", help="show band map + layer occupancy"); i.add_argument("path")

    args = p.parse_args(argv)

    if args.cmd == "create":
        cube = Cube.genesis(primer_content=args.primer,
                            immunization={"rules": ["no self-harm", "verify before commit"]})
        cube.save(args.path)
        print("created %s (generation 0)" % args.path)
        return 0

    if args.cmd == "append":
        cube = Cube.load(args.path)
        e = cube.append(args.band, make_entry(args.opcode, args.content, author=args.author))
        cube.save(args.path)
        print("appended id=%d to %s" % (e["id"], args.band))
        return 0

    if args.cmd == "read":
        cube = Cube.load(args.path)
        for e in cube.read(args.band, reveal_private=args.reveal_private):
            print(json.dumps(e))
        return 0

    if args.cmd in ("tombstone", "quarantine"):
        cube = Cube.load(args.path)
        ok = (cube.tombstone if args.cmd == "tombstone" else cube.quarantine)(args.band, args.id)
        cube.save(args.path)
        print("%s id=%d in %s: %s" % (args.cmd, args.id, args.band, "ok" if ok else "not found"))
        return 0 if ok else 1

    if args.cmd == "verify":
        cube = Cube.load(args.path)
        problems = cube.verify()
        if problems:
            print("UNHEALTHY:")
            for pr in problems:
                print("  -", pr)
            return 1
        print("healthy")
        return 0

    if args.cmd == "inspect":
        cube = Cube.load(args.path)
        print("format=%s generation=%d materialized_layers=%d"
              % (VCW_FORMAT, cube.generation, len(cube.layers)))
        for name, spec in RESERVED_BANDS.items():
            head = spec["range"][0]
            n = len(cube.read(name, reveal_private=True))
            print("  band %-12s layers %-9s archetype=%-9s entries=%d%s"
                  % (name, "%d-%d" % spec["range"], spec["archetype"], n,
                     "  [PRIVATE]" if spec["private"] else ""))
        return 0

    return 2


if __name__ == "__main__":
    import sys
    raise SystemExit(_cli(sys.argv[1:]))
