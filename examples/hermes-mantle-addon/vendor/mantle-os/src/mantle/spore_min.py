#!/usr/bin/env python3
"""
spore_min.py -- the SPORE-PNG v1 "tool embryo".

This is a small, self-contained reader/writer for a Spore PNG.  A base64+zlib
copy of THIS file is embedded inside every Spore's own VCW payload (under
`embedded_tools`), so the PNG carries the minimal code needed to read and grow
itself -- it does not depend on the full `spore.py` SDK being present.

It is format-compatible with spore.py: a Spore written by one can be read and
appended by the other.  It keeps only the essentials (decode, append, render,
read) and always renders in STRICT fill mode.

Dependency: Pillow (PIL).  Standard library otherwise.
"""

from __future__ import annotations
import hashlib, json, sys, textwrap
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
from PIL.PngImagePlugin import PngInfo

MAGIC = b"SPOREPNG"
FORMAT_VERSION = 1
SPORE_FORMAT = "spore-png-v1"
CANVAS_W = CANVAS_H = 2000
VCW_X, VCW_Y, VCW_W, VCW_H = 0, 0, 2000, 1000
DISP_X, DISP_Y, DISP_W, DISP_H = 0, 1000, 2000, 1000
BOOT_STRIP_H = 300
VCW_BLOCKS = VCW_W * VCW_H
VCW_CAPACITY_BYTES = VCW_BLOCKS * 3

# NOTE: this string MUST be byte-identical to spore.py's BOOTLOADER_TEXT.
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

ROLE_MAP = {
    "user": ("USER", "USER", "conversation"),
    "assistant": ("ASSISTANT", "SPORE", "conversation"),
    "system": ("SYSTEM", "APP", "conversation"),
    "tool": ("TOOL", "APP", "conversation"),
    "identity": ("IDENTITY", "SPORE", "metadata"),
    "display": ("DISPLAY", "APP", "display"),
}

# --- Hamming SECDED per pixel (identical to spore.py) ----------------------
_CW = 29
_PARITY = (1, 2, 4, 8, 16)
_DATA = [p for p in range(1, _CW + 1) if p not in _PARITY]


def _bits(r, g, b):
    out = []
    for v in (r, g, b):
        for i in range(7, -1, -1):
            out.append((v >> i) & 1)
    return out


def _unbits(bits):
    vals = []
    for c in range(3):
        v = 0
        for i in range(8):
            v = (v << 1) | bits[c * 8 + i]
        vals.append(v)
    return vals[0], vals[1], vals[2]


def compute_T(r, g, b):
    data = _bits(r, g, b)
    code = [0] * (_CW + 1)
    for pos, bit in zip(_DATA, data):
        code[pos] = bit
    pb = []
    for pp in _PARITY:
        x = 0
        for pos in range(1, _CW + 1):
            if pos & pp:
                x ^= code[pos]
        code[pp] = x
        pb.append(x)
    overall = 0
    for pos in range(1, _CW + 1):
        overall ^= code[pos]
    t = 0
    for bit in pb + [overall, 0, 0]:
        t = (t << 1) | bit
    return t


def decode_T(r, g, b, t):
    data = _bits(r, g, b)
    code = [0] * (_CW + 1)
    for pos, bit in zip(_DATA, data):
        code[pos] = bit
    stored = [(t >> (7 - i)) & 1 for i in range(6)]
    syndrome = 0
    for idx, pp in enumerate(_PARITY):
        x = 0
        for pos in _DATA:
            if pos & pp:
                x ^= code[pos]
        code[pp] = stored[idx]
        if x != stored[idx]:
            syndrome |= pp
    now = 0
    for pos in range(1, _CW + 1):
        now ^= code[pos]
    mism = (now != stored[5])
    if syndrome == 0:
        return r, g, b, "ok"
    if mism:
        if syndrome in _DATA:
            data[_DATA.index(syndrome)] ^= 1
            nr, ng, nb = _unbits(data)
            return nr, ng, nb, "repaired"
        return r, g, b, "repaired"
    return r, g, b, "corrupt"


def _sha(data):
    return hashlib.sha256(data).hexdigest()[:16]


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# --- stream <-> pixels -----------------------------------------------------

def _read(px, count):
    n = (count + 2) // 3
    corr = {"ok": 0, "repaired": 0, "corrupt": 0}
    out = bytearray()
    for i in range(n):
        x = VCW_X + (i % VCW_W)
        y = VCW_Y + (i // VCW_W)
        r, g, b, a = px[x, y]
        r, g, b, st = decode_T(r, g, b, a)
        corr[st] += 1
        out += bytes([r, g, b])
    return bytes(out), corr


def decode_pixels(img):
    px = img.load()
    pre, _ = _read(px, 13)
    if pre[:8] != MAGIC:
        raise ValueError("bad magic")
    hlen = int.from_bytes(pre[9:13], "big")
    if (13 + hlen + 2) // 3 > VCW_BLOCKS:
        raise ValueError("header length exceeds VCW capacity (tampered header?)")
    hm, _ = _read(px, 13 + hlen)
    header = json.loads(hm[13:13 + hlen].decode("utf-8"))
    total = 13 + hlen + header["payload_length"]
    full, corr = _read(px, total)
    payload = full[13 + hlen:total]
    corr["notes"] = []
    if _sha(payload) != header.get("payload_checksum"):
        corr["notes"].append("payload checksum mismatch")
    if corr["corrupt"]:
        corr["notes"].append(f"{corr['corrupt']} block(s) unrepairable")
    return header, payload, corr


def _header(state, payload):
    i = state["identity"]
    return {
        "magic": "SPOREPNG", "format_version": FORMAT_VERSION,
        "canvas": f"{CANVAS_W}x{CANVAS_H}",
        "vcw_region": [VCW_X, VCW_Y, VCW_W, VCW_H],
        "display_region": [DISP_X, DISP_Y, DISP_W, DISP_H],
        "boot_strip_region": [DISP_X, DISP_Y, DISP_W, BOOT_STRIP_H],
        "encoding": "RGB+T", "payload_format": "stripped_appai_log",
        "payload_length": len(payload), "payload_checksum": _sha(payload),
        "entry_count": len(state.get("conversation", [])),
        "created_at": i.get("created_at"), "updated_at": i.get("updated_at"),
        "spore_name": i.get("spore_name"), "birth_marker": i.get("birth_marker"),
        "task": i.get("task"),
    }


def _metadata(state, header):
    i = state["identity"]
    info = PngInfo()
    f = {
        "Spore-Format": SPORE_FORMAT, "Spore-Name": i.get("spore_name", ""),
        "Spore-Version": i.get("version", "1.0.0"), "Author": i.get("author", "") or "",
        "Created-At": i.get("created_at", ""), "Updated-At": i.get("updated_at", ""),
        "Canvas": f"{CANVAS_W}x{CANVAS_H}",
        "VCW-Region": f"x={VCW_X},y={VCW_Y},w={VCW_W},h={VCW_H}",
        "Display-Region": f"x={DISP_X},y={DISP_Y},w={DISP_W},h={DISP_H}",
        "Boot-Strip-Region": f"x={DISP_X},y={DISP_Y},w={DISP_W},h={BOOT_STRIP_H}",
        "Encoding": "RGB payload + T local repair (Hamming SECDED in alpha)",
        "Payload-Format": "stripped Mantle/AppAI conversation log (JSON)",
        "Payload-Checksum": header["payload_checksum"],
        "Payload-Length": str(header["payload_length"]),
        "Entry-Count": str(header["entry_count"]),
        "Birth-Marker": i.get("birth_marker") or "", "Task": i.get("task", ""),
        "Embedded-Tool": "spore_min.py (base64+zlib) in payload.embedded_tools",
        "Authority": "identity+conversation: VCW payload; bootloader/spec: metadata over strip",
        "Transport-Warning": "Transfer the ORIGINAL .png only; do not screenshot/resize/recompress/flatten.",
        "Quickstart": QUICKSTART_CODE,
        "Bootloader": BOOTLOADER_TEXT,
    }
    for k, v in f.items():
        try:
            info.add_itxt(k, v)
        except Exception:
            info.add_text(k, v)
    return info


def _mono(sz):
    for p in ("DejaVuSansMono.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
              "C:/Windows/Fonts/consola.ttf"):
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def _font(sz):
    for p in ("DejaVuSans.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(p, sz)
        except Exception:
            pass
    return ImageFont.load_default()


def _render(state, path, status="ACTIVE"):
    state["identity"]["updated_at"] = _now()
    state.setdefault("display", {})["status"] = status
    payload = json.dumps(state, separators=(",", ":"), sort_keys=True).encode("utf-8")
    header = _header(state, payload)
    hb = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
    stream = MAGIC + bytes([FORMAT_VERSION]) + len(hb).to_bytes(4, "big") + hb + payload

    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 255))
    px = img.load()
    empty_T = compute_T(0, 0, 0)
    for y in range(VCW_Y, VCW_Y + VCW_H):          # strict fill
        for x in range(VCW_X, VCW_X + VCW_W):
            px[x, y] = (0, 0, 0, empty_T)
    n = (len(stream) + 2) // 3
    if n > VCW_BLOCKS:
        raise ValueError("stream exceeds VCW capacity")
    for k in range(n):
        c = stream[k * 3:k * 3 + 3]
        r = c[0] if len(c) > 0 else 0
        g = c[1] if len(c) > 1 else 0
        b = c[2] if len(c) > 2 else 0
        px[VCW_X + (k % VCW_W), VCW_Y + (k // VCW_W)] = (r, g, b, compute_T(r, g, b))

    d = ImageDraw.Draw(img)
    d.rectangle([DISP_X, DISP_Y, DISP_X + DISP_W - 1, DISP_Y + DISP_H - 1], fill=(248, 248, 250, 255))
    d.rectangle([DISP_X, DISP_Y, DISP_X + DISP_W - 1, DISP_Y + BOOT_STRIP_H - 1], fill=(20, 24, 34, 255))
    bf = _font(20)
    y = DISP_Y + 16
    for para in BOOTLOADER_TEXT.split("\n"):
        for ln in (textwrap.wrap(para, 118) or [""]):
            d.text((30, y), ln, font=bf, fill=(225, 230, 235, 255))
            y += 21
    i = state["identity"]
    d.text((40, DISP_Y + BOOT_STRIP_H + 30), f"SPORE: {i.get('spore_name','?')}", font=_font(46), fill=(30, 40, 60, 255))
    d.text((40, DISP_Y + BOOT_STRIP_H + 96), f"TASK: {i.get('task','')}", font=_font(28), fill=(35, 45, 60, 255))
    d.text((40, DISP_Y + BOOT_STRIP_H + 140), f"STATUS: {status}   ENTRIES: {len(state.get('conversation',[]))}   (grown by spore_min)", font=_font(28), fill=(35, 45, 60, 255))
    ct = DISP_Y + 590
    d.rectangle([DISP_X, ct, DISP_X + DISP_W - 1, DISP_Y + DISP_H - 1], fill=(17, 20, 28, 255))
    d.text((30, ct + 10), "BOOT FROM THIS IMAGE ALONE  -  paste into Python (reads memory, then self-extracts writer):", font=_font(18), fill=(120, 220, 160, 255))
    cy = ct + 42
    for ln in QUICKSTART_CODE.split("\n"):
        d.text((34, cy), ln, font=_mono(17), fill=(214, 222, 233, 255)); cy += 20
    img.save(path, "PNG", pnginfo=_metadata(state, header))
    return path


def read(path):
    img = Image.open(path)
    meta = dict(img.text) if hasattr(img, "text") else {}
    header, payload, corr = decode_pixels(img.convert("RGBA"))
    state = json.loads(payload.decode("utf-8"))
    return {"state": state, "header": header, "metadata": meta, "corrections": corr}


def append(path, role, content):
    info = read(path)
    state = info["state"]
    if state.get("display", {}).get("status") == "FULL":
        return {"status": "FULL", "appended": False}
    r = role.lower()
    op, au, src = ROLE_MAP[r]
    trial = json.loads(json.dumps(state))
    trial["conversation"].append({
        "id": len(trial["conversation"]), "ts": _now(), "opcode": op,
        "author": au, "source": src, "content": content,
        "checksum": _sha(content.encode("utf-8")),
    })
    if op == "ASSISTANT" and not trial["identity"].get("birth_marker"):
        trial["identity"]["birth_marker"] = _sha(content.encode("utf-8"))[:8]
    payload = json.dumps(trial, separators=(",", ":"), sort_keys=True).encode("utf-8")
    hb = json.dumps(_header(trial, payload), separators=(",", ":"), sort_keys=True).encode("utf-8")
    stream_blocks = (len(MAGIC) + 1 + 4 + len(hb) + len(payload) + 2) // 3
    if stream_blocks > VCW_BLOCKS:
        _render(state, path, status="FULL")
        return {"status": "FULL", "appended": False}
    _render(trial, path, status="ACTIVE")
    return {"status": "ACTIVE", "appended": True, "entry_count": len(trial["conversation"])}


_USAGE = "python spore_min.py read <path> | append <path> <role> <content>"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(_USAGE); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "read":
        info = read(sys.argv[2])
        print(json.dumps({"identity": info["state"]["identity"],
                          "entries": len(info["state"]["conversation"]),
                          "corrections": info["corrections"]}, indent=2))
    elif cmd == "append":
        print(json.dumps(append(sys.argv[2], sys.argv[3], sys.argv[4]), indent=2))
    else:
        print(_USAGE); sys.exit(1)
