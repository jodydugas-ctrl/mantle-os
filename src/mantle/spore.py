#!/usr/bin/env python3
"""
SPORE-PNG v1  --  the smallest viable AppAI agent.

A "Spore" is a single PNG image that carries its own memory, visible identity,
bootstrap instructions and update protocol.  The PNG is not a picture of the
agent -- the PNG *is* the agent.

This file implements the whole format:

    * VCW color-memory encoding  (top half of the image)
    * RGB payload + T local error-correction  (Hamming SECDED per pixel)
    * an in-band header  (the first VCW blocks)
    * canonical PNG iTXt metadata
    * a visible protected boot strip + a mutable lower display
    * an EMBEDDED minimal tool (spore_min.py) carried inside the payload, so the
      PNG can read/grow itself without the full SDK beside it
    * an honest strict fill for the unused VCW field (colored == data)
    * create / read / append / render / verify

It intentionally does NOT implement organs, immune events, rebirth, lineage,
encryption, symbiosis, metabolism, tombstones, quarantine, child spores,
compaction or summarization.  A Spore is transparent and simple:

    one PNG - one agent - one task - one conversation - one append-only memory

Dependencies: Pillow (PIL).  NumPy is used if present (faster fill) but is
optional.  Everything else is the Python standard library.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
import textwrap
import zlib
from datetime import datetime, timezone

try:
    from PIL import Image, ImageDraw, ImageFont
    from PIL.PngImagePlugin import PngInfo
except ImportError:                    # the framework stays pure-stdlib importable;
    Image = ImageDraw = ImageFont = PngInfo = None   # PNG operations need the extra


def _require_pil() -> None:
    if Image is None:
        raise RuntimeError("spore PNG operations need Pillow: pip install pillow "
                           "(or: pip install mantle-os[spore])")

try:
    import numpy as _np
except Exception:                      # numpy is optional
    _np = None

# ---------------------------------------------------------------------------
# Constants -- the canonical geometry of a default Spore.
# ---------------------------------------------------------------------------

MAGIC = b"SPOREPNG"          # 8 bytes, first thing in the VCW byte-stream
FORMAT_VERSION = 1
SPORE_FORMAT = "spore-png-v1"

# A spore MAY additionally carry a GERM: the complete build data for a full
# AppAI (identity, truths, commandments, genome bands, reflexes, controls,
# instincts with proving cases -- the document the hatchery incubates), plus a
# human/agent-readable "build" note explaining how to grow it. A germ-carrying
# spore is the ONE artifact that births an AppAI: hand the PNG to
# `python -m mantle hatch` or to any coding agent, which can read the germ out
# of the payload and build a conforming body from it. The germ is inert data
# here -- the spore stores it; the hatchery validates and grows it.
GERM_FORMAT = "mantle-germ-v1"

CANVAS_W = 2000
CANVAS_H = 2000

VCW_X, VCW_Y, VCW_W, VCW_H = 0, 0, 2000, 1000        # top half: memory
DISP_X, DISP_Y, DISP_W, DISP_H = 0, 1000, 2000, 1000  # bottom half: visible
BOOT_STRIP_H = 300                                    # protected strip height

VCW_BLOCKS = VCW_W * VCW_H              # 2,000,000 pixels
VCW_CAPACITY_BYTES = VCW_BLOCKS * 3    # 6,000,000 payload bytes

# The canonical bootloader / spec text.  This exact string is mirrored into the
# visible protected strip AND into PNG metadata (key "Bootloader").
# It MUST stay byte-identical to spore_min.py's BOOTLOADER_TEXT.
BOOTLOADER_TEXT = (
    "SPORE-PNG v1  -  this PNG is a self-contained AppAI agent.\n"
    "MEMORY lives in the TOP HALF (y=0..999) as a VCW color field: read pixels\n"
    "left-to-right, top-to-bottom. Each pixel = one block: R,G,B carry payload\n"
    "bytes, ALPHA (T) is a Hamming SECDED byte that repairs one bad bit in that\n"
    "block. The byte-stream starts with magic 'SPOREPNG', a 1-byte version, a\n"
    "4-byte big-endian header length, then a JSON header, then the JSON payload.\n"
    "A minimal Python reader/writer is embedded in the payload (embedded_tools).\n"
    "Canonical spec ALSO lives in PNG iTXt metadata; metadata is canonical over\n"
    "THIS strip, but the VCW payload owns identity + conversation memory.\n"
    "KEEP THE SEED DRY: transfer the ORIGINAL .png only. Do NOT screenshot, resize,\n"
    "recompress, flatten transparency, or pass me through lossy image tools - that\n"
    "destroys the alpha (T) repair layer and injures memory.\n"
    "To use me: open in a Spore app, or hand me to a Python-capable LLM and let\n"
    "Python (not eyeballs) decode the pixels. RULE: the LATEST PNG is the living copy."
)

TRANSPORT_WARNING = (
    "Transfer the ORIGINAL .png only; do not screenshot/resize/recompress/flatten."
)

# A tiny, self-contained reader printed IN the view area (and mirrored in the
# "Quickstart" metadata).  It reads an undamaged Spore with no dependencies
# beyond Pillow -- the full repairing reader is the embedded spore_min.py.
QUICKSTART_CODE = (
    "# BOOT ME FROM THIS IMAGE ALONE - needs only: pip install pillow\n"
    "from PIL import Image; import json, base64, zlib\n"
    "px = Image.open('spore.png').convert('RGBA').load()\n"
    "def rd(nbytes):                       # read N payload bytes from the VCW\n"
    "    o = bytearray()\n"
    "    for i in range((nbytes + 2) // 3):\n"
    "        r, g, b, a = px[i % 2000, i // 2000]; o += bytes([r, g, b])\n"
    "    return bytes(o)\n"
    "n = int.from_bytes(rd(13)[9:13], 'big')            # header length\n"
    "H = json.loads(rd(13+n)[13:13+n]); L = H['payload_length']\n"
    "S = json.loads(rd(13+n+L)[13+n:13+n+L])            # S = my whole mind\n"
    "print(S['identity']['spore_name'], '-', S['identity']['task'])\n"
    "for e in S['conversation']: print(e['opcode'], ':', e['content'])\n"
    "# GROW ME: I carry my own reader/writer - extract and use it:\n"
    "open('spore_min.py','w').write(zlib.decompress(base64.b64decode(S['embedded_tools']['code'])).decode())\n"
    "import spore_min  # spore_min.append('spore.png','user','hi'); ...('assistant','reply')"
)

# Authority table -- which source wins for which concern.  See spore_format.md.
AUTHORITY = {
    "bootloader_spec": "metadata wins over the visible boot strip",
    "identity": "VCW payload is canonical (metadata only mirrors it)",
    "conversation": "VCW payload is canonical",
    "display": "VCW payload is canonical",
}

TOOLS_PROTOCOL = {
    "reader": "decode VCW top-half: magic+version+u32 header_len+header JSON+payload JSON",
    "correction": "per-pixel Hamming SECDED in alpha channel; repair 1-bit, detect 2-bit",
    "vcw_model": ("append-only delta log: genesis records (identity, tools, "
                  "embedded_tools) are written once; thereafter each turn is ONE "
                  "appended delta. Current state = genesis folded with the deltas. "
                  "The LLM context window is NEVER re-stored per turn, so total VCW "
                  "memory is the SUM of deltas (linear), not the history repeated."),
    "embedded_tool": "a base64+zlib copy of spore_min.py lives in payload.embedded_tools",
    "update_protocol": [
        "1. load latest PNG",
        "2. read metadata + decode VCW",
        "3. parse header + payload",
        "4. rebuild conversation/task context",
        "5. append new turn(s)",
        "6. regenerate the WHOLE PNG from canonical state (never edit pixels in place)",
    ],
    "authority": AUTHORITY,
    "display_rules": "protected boot strip is redrawn verbatim; lower display is mutable",
    "full_rule": "if no VCW room remains, mark FULL, do not overwrite memory, do not spawn children",
    "transport": TRANSPORT_WARNING,
}

ROLE_MAP = {
    "user":      ("USER", "USER", "conversation"),
    "assistant": ("ASSISTANT", "SPORE", "conversation"),
    "system":    ("SYSTEM", "APP", "conversation"),
    "tool":      ("TOOL", "APP", "conversation"),
    "identity":  ("IDENTITY", "SPORE", "metadata"),
    "display":   ("DISPLAY", "APP", "display"),
}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def _checksum_text(text: str) -> str:
    return _sha(text.encode("utf-8"))


# ---------------------------------------------------------------------------
# Embedded tool  (self-hosting: the PNG carries spore_min.py)
# ---------------------------------------------------------------------------

_EMBEDDED_CACHE = None

_FALLBACK_TOOL = (
    "# minimal Spore tool embryo (fallback stub).\n"
    "# The full spore_min.py was not found beside spore.py at creation time.\n"
    "def read(path):\n"
    "    raise NotImplementedError('regenerate with spore_min.py present')\n"
    "def append(path, role, content):\n"
    "    raise NotImplementedError('regenerate with spore_min.py present')\n"
)


def _load_embedded_source() -> str:
    """Load spore_min.py source from beside this file (cached); else a stub."""
    global _EMBEDDED_CACHE
    if _EMBEDDED_CACHE is not None:
        return _EMBEDDED_CACHE
    here = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(here, "spore_min.py")
    try:
        with open(candidate, encoding="utf-8") as f:
            _EMBEDDED_CACHE = f.read()
    except Exception:
        _EMBEDDED_CACHE = _FALLBACK_TOOL
    return _EMBEDDED_CACHE


def _make_embedded_tools() -> dict:
    src = _load_embedded_source()
    raw = src.encode("utf-8")
    packed = base64.b64encode(zlib.compress(raw, 9)).decode("ascii")
    return {
        "language": "python",
        "filename": "spore_min.py",
        "encoding": "base64+zlib",
        "entrypoints": ["read", "append"],
        "sha256": hashlib.sha256(raw).hexdigest(),
        "code": packed,
    }


def extract_embedded_tool(path: str, out_path: str | None = None) -> str:
    """Decode the embedded spore_min.py source from a Spore PNG."""
    state = read_spore(path)["state"]
    et = state.get("embedded_tools")
    if not et or "code" not in et:
        raise ValueError("no embedded tool present in this spore")
    src = zlib.decompress(base64.b64decode(et["code"])).decode("utf-8")
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(src)
    return src


# ---------------------------------------------------------------------------
# Hamming SECDED per-block error correction (the "T" byte)
# ---------------------------------------------------------------------------

_CODEWORD_LEN = 29                         # 24 data + 5 parity positions
_PARITY_POS = (1, 2, 4, 8, 16)
_DATA_POS = [p for p in range(1, _CODEWORD_LEN + 1) if p not in _PARITY_POS]
assert len(_DATA_POS) == 24


def _rgb_to_bits(r: int, g: int, b: int) -> list[int]:
    bits = []
    for value in (r, g, b):
        for i in range(7, -1, -1):
            bits.append((value >> i) & 1)
    return bits


def _bits_to_rgb(bits: list[int]) -> tuple[int, int, int]:
    vals = []
    for c in range(3):
        v = 0
        for i in range(8):
            v = (v << 1) | bits[c * 8 + i]
        vals.append(v)
    return vals[0], vals[1], vals[2]


def compute_T(r: int, g: int, b: int) -> int:
    """Return the SECDED alpha byte protecting this (r,g,b) block."""
    data = _rgb_to_bits(r, g, b)
    code = [0] * (_CODEWORD_LEN + 1)
    for pos, bit in zip(_DATA_POS, data):
        code[pos] = bit
    parity_bits = []
    for pp in _PARITY_POS:
        x = 0
        for pos in range(1, _CODEWORD_LEN + 1):
            if pos & pp:
                x ^= code[pos]
        code[pp] = x
        parity_bits.append(x)
    overall = 0
    for pos in range(1, _CODEWORD_LEN + 1):
        overall ^= code[pos]
    t = 0
    for bit in parity_bits + [overall, 0, 0]:
        t = (t << 1) | bit
    return t


def decode_T(r: int, g: int, b: int, t: int) -> tuple[int, int, int, str]:
    """
    Verify/repair a block.  status in {"ok","repaired","corrupt"}.
    """
    data = _rgb_to_bits(r, g, b)
    code = [0] * (_CODEWORD_LEN + 1)
    for pos, bit in zip(_DATA_POS, data):
        code[pos] = bit
    stored = [(t >> (7 - i)) & 1 for i in range(6)]
    stored_parity = stored[:5]
    stored_overall = stored[5]
    syndrome = 0
    for idx, pp in enumerate(_PARITY_POS):
        x = 0
        for pos in _DATA_POS:
            if pos & pp:
                x ^= code[pos]
        code[pp] = stored_parity[idx]
        if x != stored_parity[idx]:
            syndrome |= pp
    overall_now = 0
    for pos in range(1, _CODEWORD_LEN + 1):
        overall_now ^= code[pos]
    overall_mismatch = (overall_now != stored_overall)

    if syndrome == 0 and not overall_mismatch:
        return r, g, b, "ok"
    if syndrome == 0 and overall_mismatch:
        return r, g, b, "ok"           # only the overall-parity bit is wrong
    if syndrome != 0 and overall_mismatch:
        if syndrome in _DATA_POS:
            di = _DATA_POS.index(syndrome)
            data[di] ^= 1
            nr, ng, nb = _bits_to_rgb(data)
            return nr, ng, nb, "repaired"
        return r, g, b, "repaired"     # error sat in a parity bit
    return r, g, b, "corrupt"          # double-bit error: report, do not invent


# ---------------------------------------------------------------------------
# Byte-stream  <->  VCW pixels
# ---------------------------------------------------------------------------

def build_stream(header: dict, payload_bytes: bytes) -> bytes:
    header_bytes = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    out = bytearray()
    out += MAGIC
    out += bytes([FORMAT_VERSION])
    out += len(header_bytes).to_bytes(4, "big")
    out += header_bytes
    out += payload_bytes
    return bytes(out)


def encode_pixels(stream: bytes, img: Image.Image) -> None:
    """
    Write the byte-stream into the top-half VCW region, block by block.

    Unused VCW pixels are canonical EMPTY blocks (0,0,0)+T.  There is no
    decorative filler: the number of colored pixels always equals the amount of
    real data, so the picture never overstates how full the Spore is.  The
    header's payload_length defines the exact memory boundary.
    """
    n_blocks = (len(stream) + 2) // 3
    if n_blocks > VCW_BLOCKS:
        raise ValueError("stream exceeds VCW capacity")
    empty_T = compute_T(0, 0, 0)

    if _np is not None:                       # fast path (optional numpy)
        arr = _np.zeros((VCW_H, VCW_W, 4), dtype=_np.uint8)
        arr[..., 3] = empty_T
        flat = arr.reshape(-1, 4)
        for i in range(n_blocks):
            chunk = stream[i * 3: i * 3 + 3]
            r = chunk[0] if len(chunk) > 0 else 0
            g = chunk[1] if len(chunk) > 1 else 0
            b = chunk[2] if len(chunk) > 2 else 0
            flat[i, 0] = r
            flat[i, 1] = g
            flat[i, 2] = b
            flat[i, 3] = compute_T(r, g, b)
        img.paste(Image.fromarray(arr, "RGBA"), (VCW_X, VCW_Y))
        return

    px = img.load()                           # pure-Python fallback
    for y in range(VCW_Y, VCW_Y + VCW_H):
        for x in range(VCW_X, VCW_X + VCW_W):
            px[x, y] = (0, 0, 0, empty_T)
    for i in range(n_blocks):
        chunk = stream[i * 3: i * 3 + 3]
        r = chunk[0] if len(chunk) > 0 else 0
        g = chunk[1] if len(chunk) > 1 else 0
        b = chunk[2] if len(chunk) > 2 else 0
        px[VCW_X + (i % VCW_W), VCW_Y + (i // VCW_W)] = (r, g, b, compute_T(r, g, b))


def _read_blocks(px, count_bytes: int, start_block: int = 0):
    n_blocks = (count_bytes + 2) // 3
    corrections = {"ok": 0, "repaired": 0, "corrupt": 0}
    out = bytearray()
    for i in range(start_block, start_block + n_blocks):
        x = VCW_X + (i % VCW_W)
        y = VCW_Y + (i // VCW_W)
        r, g, b, a = px[x, y]
        r, g, b, status = decode_T(r, g, b, a)
        corrections[status] += 1
        out += bytes([r, g, b])
    return bytes(out), corrections


def decode_pixels(img: Image.Image) -> tuple[dict, bytes, dict]:
    """Decode the VCW region into (header, payload_bytes, correction_report)."""
    px = img.load()

    prefix, _ = _read_blocks(px, 13, 0)
    if prefix[:8] != MAGIC:
        raise ValueError(f"bad magic: {prefix[:8]!r} (expected {MAGIC!r})")
    header_len = int.from_bytes(prefix[9:13], "big")

    fixed = 13
    if (fixed + header_len + 2) // 3 > VCW_BLOCKS:
        raise ValueError("header length exceeds VCW capacity (tampered header?)")
    header_and_more, _ = _read_blocks(px, fixed + header_len, 0)
    header_bytes = header_and_more[fixed: fixed + header_len]
    try:
        header = json.loads(header_bytes.decode("utf-8"))
    except Exception as e:
        raise ValueError(f"header is corrupt / unreadable: {e}")

    payload_length = header.get("payload_length")
    if not isinstance(payload_length, int) or payload_length < 0:
        raise ValueError("header payload_length invalid")
    total = fixed + header_len + payload_length
    if (total + 2) // 3 > VCW_BLOCKS:
        raise ValueError("header payload_length exceeds VCW capacity (tampered header?)")

    full, corr = _read_blocks(px, total, 0)
    report = {"ok": corr["ok"], "repaired": corr["repaired"],
              "corrupt": corr["corrupt"], "notes": []}
    payload_bytes = full[fixed + header_len: total]

    if _sha(payload_bytes) != header.get("payload_checksum"):
        report["notes"].append(
            f"payload checksum mismatch: header={header.get('payload_checksum')} "
            f"actual={_sha(payload_bytes)}"
        )
    if report["corrupt"]:
        report["notes"].append(f"{report['corrupt']} block(s) unrepairable")
    return header, payload_bytes, report


# ---------------------------------------------------------------------------
# Visible rendering  (protected boot strip + mutable lower display)
# ---------------------------------------------------------------------------

def _load_font(size: int):
    candidates = [
        "DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/local/lib/python3.10/dist-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSans.ttf",
        "/Library/Fonts/Arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _load_mono(size: int):
    for p in ("DejaVuSansMono.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
              "/usr/local/lib/python3.10/dist-packages/matplotlib/mpl-data/fonts/ttf/DejaVuSansMono.ttf",
              "C:/Windows/Fonts/consola.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _draw_wrapped(draw, xy, text, font, fill, max_chars, line_h):
    x, y = xy
    for para in text.split("\n"):
        for ln in (textwrap.wrap(para, width=max_chars) or [""]):
            draw.text((x, y), ln, font=font, fill=fill)
            y += line_h
    return y


def render_visible(img: Image.Image, state: dict, status: str) -> None:
    draw = ImageDraw.Draw(img)
    draw.rectangle([DISP_X, DISP_Y, DISP_X + DISP_W - 1, DISP_Y + DISP_H - 1],
                   fill=(248, 248, 250, 255))

    # protected boot strip (canonical -- never creatively altered)
    draw.rectangle([DISP_X, DISP_Y, DISP_X + DISP_W - 1, DISP_Y + BOOT_STRIP_H - 1],
                   fill=(20, 24, 34, 255))
    draw.text((30, DISP_Y + 12), "PROTECTED BOOT STRIP  (canonical - do not alter)",
              font=_load_font(24), fill=(120, 220, 160, 255))
    _draw_wrapped(draw, (30, DISP_Y + 48), BOOTLOADER_TEXT, _load_font(18),
                  (225, 230, 235, 255), max_chars=126, line_h=18)

    ident = state["identity"]
    disp = state.get("display", {})
    y = DISP_Y + BOOT_STRIP_H + 20
    name_color = (150, 40, 40, 255) if status == "FULL" else (30, 40, 60, 255)
    draw.text((40, y), f"SPORE: {ident.get('spore_name', '?')}", font=_load_font(44), fill=name_color)
    y += 62

    lines = [
        f"TASK: {ident.get('task', '')}",
        "WHAT I AM: an AppAI agent inside this PNG (I carry my own reader)",
        "HOW TO USE: give me to a Python-capable LLM, or open me in a Spore app",
        "MEMORY: upper color field (VCW).  KEEP THE SEED DRY: send the ORIGINAL .png",
        f"ENTRIES: {len(state.get('conversation', []))}    "
        f"BIRTH: {ident.get('birth_marker') or '-'}    STATUS: {status}",
    ]
    for extra in disp.get("lines", []):
        lines.append(str(extra))
    lf = _load_font(26)
    for ln in lines:
        y = _draw_wrapped(draw, (40, y), ln, lf, (35, 45, 60, 255), max_chars=104, line_h=33)
        y += 3

    if status == "FULL":
        _draw_wrapped(draw, (40, y + 8),
                      f"SPORE FULL - Name: {ident.get('spore_name', '?')} - memory cannot be "
                      "safely appended; preserve this PNG as the final state.",
                      _load_font(30), (150, 40, 40, 255), max_chars=92, line_h=36)

    # --- runnable QUICKSTART code panel (view area carries a real reader) ----
    code_top = DISP_Y + 590
    draw.rectangle([DISP_X, code_top, DISP_X + DISP_W - 1, DISP_Y + DISP_H - 1],
                   fill=(17, 20, 28, 255))
    draw.text((30, code_top + 10),
              "BOOT FROM THIS IMAGE ALONE  -  paste into Python (reads my memory, then self-extracts my writer):",
              font=_load_font(18), fill=(120, 220, 160, 255))
    cy = code_top + 42
    for ln in QUICKSTART_CODE.split("\n"):
        draw.text((34, cy), ln, font=_load_mono(17), fill=(214, 222, 233, 255))
        cy += 20


# ---------------------------------------------------------------------------
# Header + metadata assembly
# ---------------------------------------------------------------------------

def _make_header(state: dict, payload_bytes: bytes) -> dict:
    ident = state["identity"]
    return {
        "magic": "SPOREPNG",
        "format_version": FORMAT_VERSION,
        "canvas": f"{CANVAS_W}x{CANVAS_H}",
        "vcw_region": [VCW_X, VCW_Y, VCW_W, VCW_H],
        "display_region": [DISP_X, DISP_Y, DISP_W, DISP_H],
        "boot_strip_region": [DISP_X, DISP_Y, DISP_W, BOOT_STRIP_H],
        "encoding": "RGB+T",
        "payload_format": "stripped_appai_log",
        "payload_length": len(payload_bytes),
        "payload_checksum": _sha(payload_bytes),
        "entry_count": len(state.get("conversation", [])),
        "created_at": ident.get("created_at"),
        "updated_at": ident.get("updated_at"),
        "spore_name": ident.get("spore_name"),
        "birth_marker": ident.get("birth_marker"),
        "task": ident.get("task"),
    }


def _make_metadata(state: dict, header: dict) -> PngInfo:
    ident = state["identity"]
    info = PngInfo()
    fields = {
        "Spore-Format": SPORE_FORMAT,
        "Spore-Name": ident.get("spore_name", ""),
        "Spore-Version": ident.get("version", "1.0.0"),
        "Author": ident.get("author", "") or "",
        "Created-At": ident.get("created_at", ""),
        "Updated-At": ident.get("updated_at", ""),
        "Canvas": f"{CANVAS_W}x{CANVAS_H}",
        "VCW-Region": f"x={VCW_X},y={VCW_Y},w={VCW_W},h={VCW_H}",
        "Display-Region": f"x={DISP_X},y={DISP_Y},w={DISP_W},h={DISP_H}",
        "Boot-Strip-Region": f"x={DISP_X},y={DISP_Y},w={DISP_W},h={BOOT_STRIP_H}",
        "Encoding": "RGB payload + T local repair (Hamming SECDED in alpha)",
        "Payload-Format": "stripped Mantle/AppAI conversation log (JSON)",
        "Payload-Checksum": header["payload_checksum"],
        "Payload-Length": str(header["payload_length"]),
        "Entry-Count": str(header["entry_count"]),
        "Birth-Marker": ident.get("birth_marker") or "",
        "Task": ident.get("task", ""),
        "Embedded-Tool": "spore_min.py (base64+zlib) in payload.embedded_tools",
        "Authority": "identity+conversation: VCW payload; bootloader/spec: metadata over strip",
        "Transport-Warning": TRANSPORT_WARNING,
        "Quickstart": QUICKSTART_CODE,
        "Bootloader": BOOTLOADER_TEXT,
    }
    for k, v in fields.items():
        try:
            info.add_itxt(k, v)
        except Exception:
            info.add_text(k, v)
    return info


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _new_state(name: str, task: str, author: str | None) -> dict:
    ts = _now()
    return {
        "identity": {
            "spore_name": name,
            "birth_marker": None,
            "task": task,
            "author": author or "",
            "version": "1.0.0",
            "format_version": FORMAT_VERSION,
            "created_at": ts,
            "updated_at": ts,
        },
        "tools": TOOLS_PROTOCOL,
        "embedded_tools": _make_embedded_tools(),
        "conversation": [],
        "display": {"lines": [], "status": "ACTIVE"},
    }


def _append_entry(state: dict, role: str, content: str) -> None:
    role = role.lower()
    if role not in ROLE_MAP:
        raise ValueError(f"unknown role {role!r}; use one of {list(ROLE_MAP)}")
    opcode, author, source = ROLE_MAP[role]
    state["conversation"].append({
        "id": len(state["conversation"]),
        "ts": _now(),
        "opcode": opcode,
        "author": author,
        "source": source,
        "content": content,
        "checksum": _checksum_text(content),
    })
    if opcode == "ASSISTANT" and not state["identity"].get("birth_marker"):
        state["identity"]["birth_marker"] = _checksum_text(content)[:8]


def _payload_bytes(state: dict) -> bytes:
    return json.dumps(state, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _fits(state: dict) -> bool:
    payload = _payload_bytes(state)
    header = _make_header(state, payload)
    stream = build_stream(header, payload)
    return ((len(stream) + 2) // 3) <= VCW_BLOCKS


def render_spore(state: dict, path: str, status: str = "ACTIVE") -> str:
    """Regenerate the WHOLE PNG from canonical state and save it to `path`."""
    _require_pil()
    state["identity"]["updated_at"] = _now()
    disp = state.setdefault("display", {})
    disp["status"] = status

    payload = _payload_bytes(state)
    header = _make_header(state, payload)
    stream = build_stream(header, payload)

    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 255))
    encode_pixels(stream, img)
    render_visible(img, state, status)
    img.save(path, "PNG", pnginfo=_make_metadata(state, header))
    return path


def create_spore(name: str, task: str, author: str | None = None,
                 path: str = "spore.png") -> str:
    """Create a fresh Spore PNG (one agent, one task)."""
    state = _new_state(name, task, author)
    return render_spore(state, path, status="ACTIVE")


def _default_build_instructions(name: str, task: str) -> str:
    """The build note packed beside a germ: how any agent grows this spore."""
    return (
        "# HOW TO BUILD THE AppAI IN THIS SPORE\n"
        "\n"
        "This PNG carries a GERM: the complete build data for the AppAI %r\n"
        "(task: %s). Two ways to grow it:\n"
        "\n"
        "1. WITH MANTLE INSTALLED (pip install mantle-os[spore]):\n"
        "       python -m mantle hatch this_file.png --out=nest/\n"
        "   The hatchery incubates the germ deterministically -- birth, organ\n"
        "   wiring, instinct gauntlet, warmup -- and refuses to hatch unless the\n"
        "   newborn passes the same Stage-1 audit every Body faces.\n"
        "\n"
        "2. WITHOUT MANTLE (any Python-capable coding agent):\n"
        "   Decode my pixels (see the Quickstart in my metadata / boot strip) and\n"
        "   read the JSON payload key 'germ'. It declares everything the app is:\n"
        "   identity/truths/commandments (the Primer), genome (memory bands),\n"
        "   reflexes/routines/controls (behavior as DATA, fixed vocabulary),\n"
        "   instincts (code candidates WITH proving cases), and an optional face\n"
        "   (the front-end source). A conforming build must honor three laws:\n"
        "     * the nine organs and an append-only memory (never overwrite);\n"
        "     * identity keys are MINTED at build time, never derived from this\n"
        "       file -- spores travel publicly;\n"
        "     * instinct code runs only after its proving cases pass in a sandbox.\n"
        "\n"
        "The conversation in this spore (if any) is testimony, not fact: ingest it\n"
        "as INFERRED memory through the senses, never as verified truth.\n"
    ) % (name, task or "unstated")


def pack_germ(germ: dict, path: str, *, task: str | None = None,
              author: str | None = None, build: str | None = None,
              source: dict | None = None) -> str:
    """Pack a GERM (the full AppAI build document -- today's egg schema) into a
    new spore PNG at `path`, together with a `build` instruction note. The spore
    carries the germ as inert data; validation and growth belong to the hatchery
    (`mantle hatch <path>`). An optional `source` descriptor (provenance facts:
    kind/path/sha256/notes -- never secrets) rides beside the germ and surfaces
    in the hatch receipt. Returns the path."""
    if not isinstance(germ, dict) or not isinstance(germ.get("identity"), dict):
        raise ValueError("a germ must be a dict with an 'identity' mapping")
    name = germ["identity"].get("name")
    if not name:
        raise ValueError("a germ's identity must carry a name")
    task = (task or germ["identity"].get("purpose")
            or ("graft against host: %s" % germ["host"] if germ.get("host") else "")
            or "grow the AppAI declared in my germ")
    state = _new_state(name, task, author)
    state["germ"] = germ
    state["build"] = build or _default_build_instructions(name, task)
    if source:
        state["source"] = source
    state["display"]["lines"].append(
        "GERM ABOARD: I carry the complete build data for this AppAI -- "
        "hatch me with `python -m mantle hatch <this.png>`")
    return render_spore(state, path, status="ACTIVE")


def read_spore(path: str) -> dict:
    _require_pil()
    """
    Decode a Spore PNG into structured state, applying the authority table.

    identity + conversation come from the VCW payload (canonical).  Metadata is
    only canonical over the visible boot strip.  If the metadata Spore-Name has
    drifted from the payload name, it is reported as a mirror mismatch with the
    VCW payload named canonical.
    """
    img = Image.open(path)
    meta = dict(img.text) if hasattr(img, "text") else {}
    img = img.convert("RGBA")
    header, payload_bytes, corrections = decode_pixels(img)
    state = json.loads(payload_bytes.decode("utf-8"))
    status = state.get("display", {}).get("status", "ACTIVE")

    name_mirror_mismatch = None
    meta_name = meta.get("Spore-Name")
    if meta_name and meta_name != state["identity"].get("spore_name"):
        name_mirror_mismatch = {
            "field": "spore_name",
            "metadata_mirror": meta_name,
            "payload": state["identity"].get("spore_name"),
            "canonical": "vcw_payload",
        }

    return {
        "path": path,
        "state": state,
        "header": header,
        "metadata": meta,
        "corrections": corrections,
        "status": status,
        "authority": AUTHORITY,
        "name_mirror_mismatch": name_mirror_mismatch,
    }


def append_turn(path: str, role: str, content: str) -> dict:
    """Append a turn and regenerate the PNG (new living copy); FULL-safe."""
    info = read_spore(path)
    state = info["state"]

    if state.get("display", {}).get("status") == "FULL":
        return {"status": "FULL", "appended": False,
                "reason": "spore already full", "path": path}

    trial = json.loads(json.dumps(state))     # deep copy
    _append_entry(trial, role, content)
    if not _fits(trial):
        render_spore(state, path, status="FULL")   # keep old memory intact
        return {"status": "FULL", "appended": False,
                "reason": "no VCW capacity remaining", "path": path}

    render_spore(trial, path, status="ACTIVE")
    return {"status": "ACTIVE", "appended": True,
            "entry_count": len(trial["conversation"]),
            "birth_marker": trial["identity"].get("birth_marker"),
            "path": path}


def rename_spore(path: str, new_name: str) -> dict:
    info = read_spore(path)
    state = info["state"]
    state["identity"]["spore_name"] = new_name
    _append_entry(state, "identity", f"renamed to {new_name}")
    render_spore(state, path, status=state.get("display", {}).get("status", "ACTIVE"))
    return {"spore_name": new_name, "path": path}


def _check_embedded_tool(state: dict) -> tuple[bool, str]:
    """Return (ok, detail) for the embedded self-hosting tool."""
    et = state.get("embedded_tools")
    if not et or "code" not in et:
        return False, "missing embedded_tools"
    try:
        src = zlib.decompress(base64.b64decode(et["code"])).decode("utf-8")
    except Exception as e:
        return False, f"undecodable: {e}"
    if hashlib.sha256(src.encode("utf-8")).hexdigest() != et.get("sha256"):
        return False, "embedded sha256 mismatch"
    try:
        compile(src, "<embedded spore_min.py>", "exec")
    except SyntaxError as e:
        return False, f"does not compile: {e}"
    if "def read(" not in src or "def append(" not in src:
        return False, "embedded tool lacks read()/append()"
    return True, f"{len(src)} bytes, compiles, has read()/append()"


def verify_spore(path: str) -> dict:
    """Verify a Spore PNG.  Returns {ok, checks, problems, ...}."""
    _require_pil()
    checks, problems = [], []

    def ck(name, cond, detail=""):
        checks.append({"check": name, "pass": bool(cond), "detail": detail})
        if not cond:
            problems.append(f"{name}: {detail}")

    img = Image.open(path)
    ck("canvas 2000x2000", img.size == (CANVAS_W, CANVAS_H), str(img.size))
    ck("mode RGBA", img.convert("RGBA").mode == "RGBA")

    info = read_spore(path)
    header, state, meta, corr = info["header"], info["state"], info["metadata"], info["corrections"]

    ck("magic present", header.get("magic") == "SPOREPNG")
    ck("format_version==1", header.get("format_version") == FORMAT_VERSION)
    ck("vcw_region top-half", header.get("vcw_region") == [VCW_X, VCW_Y, VCW_W, VCW_H])
    ck("display_region bottom-half", header.get("display_region") == [DISP_X, DISP_Y, DISP_W, DISP_H])
    ck("boot_strip declared", header.get("boot_strip_region") == [DISP_X, DISP_Y, DISP_W, BOOT_STRIP_H])

    ck("payload checksum matches header",
       _sha(_payload_bytes(state)) == header.get("payload_checksum"))
    ck("entry_count matches", header.get("entry_count") == len(state.get("conversation", [])))

    for key in ("Spore-Format", "Bootloader", "Payload-Checksum", "Task",
                "Spore-Name", "Transport-Warning", "Embedded-Tool", "Authority",
                "Quickstart"):
        ck(f"metadata has {key}", key in meta and meta[key] != "")
    ck("metadata bootloader canonical", meta.get("Bootloader") == BOOTLOADER_TEXT)

    et_ok, et_detail = _check_embedded_tool(state)
    ck("embedded self-hosting tool valid", et_ok, et_detail)

    ck("no unrepairable corruption", corr.get("corrupt", 0) == 0,
       f"{corr.get('corrupt', 0)} corrupt blocks")
    if not corr.get("notes"):
        checks.append({"check": "no integrity notes", "pass": True, "detail": ""})
    else:
        for n in corr["notes"]:
            problems.append(f"integrity: {n}")

    status = info["status"]
    ck("status is ACTIVE or FULL", status in ("ACTIVE", "FULL"), status)
    ids = [e["id"] for e in state.get("conversation", [])]
    ck("conversation ids ordered 0..n", ids == list(range(len(ids))))

    return {"ok": len(problems) == 0, "checks": checks, "problems": problems,
            "corrections": corr, "status": status,
            "authority": info["authority"],
            "name_mirror_mismatch": info["name_mirror_mismatch"],
            "embedded_tool": et_detail}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_USAGE = """\
spore.py -- SPORE-PNG v1

  python spore.py create  <path> "<name>" "<task>" [author]
  python spore.py pack    <germ.json> <out.png>        # germ (egg data) -> one spore
  python spore.py append  <path> <user|assistant|system|tool|display> "<content>"
  python spore.py read    <path>
  python spore.py rename  <path> "<new name>"
  python spore.py verify  <path>
  python spore.py extract <path> [out=spore_min.py]   # dump the embedded tool
  python spore.py demo    [path]                       # build example_spore.png
"""


def _demo(path: str = "example_spore.png") -> str:
    create_spore("SPORE-SEED", "Answer one question about the SPORE-PNG format.",
                 author="Jody", path=path)
    append_turn(path, "user", "What are you and how do I keep you alive?")
    append_turn(path, "assistant",
                "I am a Spore: a single PNG that holds one agent, one task and one "
                "conversation. My memory is encoded in the color field of my top half, "
                "and I carry a minimal Python reader/writer embedded inside that memory. "
                "Keep me alive by always saving and reusing the LATEST PNG as the living "
                "copy -- and send the ORIGINAL file, never a screenshot.")
    append_turn(path, "user", "Where exactly is the memory stored?")
    append_turn(path, "assistant",
                "In the top half (y=0..999). Each pixel's R,G,B are payload bytes and the "
                "alpha channel is a Hamming repair byte. A Python reader decodes it; you "
                "should not read the colors by eye.")
    return path


def main(argv):
    if len(argv) < 2:
        print(_USAGE)
        return 1
    cmd = argv[1]
    try:
        if cmd == "create":
            path, name, task = argv[2], argv[3], argv[4]
            author = argv[5] if len(argv) > 5 else None
            create_spore(name, task, author, path)
            print(f"created {path}")
        elif cmd == "pack":
            with open(argv[2], encoding="utf-8") as f:
                germ = json.load(f)
            pack_germ(germ, argv[3])
            print(f"packed germ {argv[2]} into spore {argv[3]}")
        elif cmd == "append":
            print(json.dumps(append_turn(argv[2], argv[3], argv[4]), indent=2))
        elif cmd == "read":
            info = read_spore(argv[2])
            print(json.dumps({
                "identity": info["state"]["identity"],
                "status": info["status"],
                "entries": len(info["state"]["conversation"]),
                "corrections": info["corrections"],
                "name_mirror_mismatch": info["name_mirror_mismatch"],
                "embedded_tool": info["state"].get("embedded_tools", {}).get("sha256"),
                "conversation": [
                    {"id": e["id"], "opcode": e["opcode"], "content": e["content"]}
                    for e in info["state"]["conversation"]
                ],
            }, indent=2))
        elif cmd == "rename":
            print(json.dumps(rename_spore(argv[2], argv[3]), indent=2))
        elif cmd == "verify":
            rep = verify_spore(argv[2])
            print(json.dumps(rep, indent=2))
            return 0 if rep["ok"] else 2
        elif cmd == "extract":
            out = argv[3] if len(argv) > 3 else "spore_min.py"
            extract_embedded_tool(argv[2], out)
            print(f"embedded tool written to {out}")
        elif cmd == "demo":
            _demo(argv[2] if len(argv) > 2 else "example_spore.png")
            print("demo spore written")
        else:
            print(_USAGE)
            return 1
    except (IndexError, ValueError) as e:
        print(f"error: {e}\n\n{_USAGE}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
