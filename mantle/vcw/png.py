#!/usr/bin/env python3
"""
mantle.vcw.png  --  the pure-stdlib PNG codec (Mantle v3)

Every VCW layer is a REAL, valid PNG image: the whole organism's memory is a directory of
pictures you can open in any image viewer. This module is the lowest substrate primitive --
flat RGBA bytes <-> PNG bytes, and the layer pixel-stream layout:

  [ 8 bytes  MAGIC = b"VCWPNG2\\n" ]
  [ 4 bytes  uint32 length of boot JSON   ][ boot JSON utf-8 ]
  [ 4 bytes  uint32 length of payload JSON][ payload JSON utf-8 ]
  [ zero padding up to LAYER_BYTES ]

A single byte inside a layer is addressed by (layer, x, y):
  offset = (y * SIDE + x) * CHANNELS          # CHANNELS = 4 (R,G,B,A)

We WRITE filter type 0 (None) scanlines at zlib level 1 (the payload is JSON + zero pad --
level 1 compresses it nearly as small as level 6 at a fraction of the CPU; the level is
invisible to the decoder). We READ all five PNG filter types for robustness.
"""
from __future__ import annotations

import json
import struct
import zlib
from typing import Any, Dict, Optional, Tuple

VCW_FORMAT  = "vcw-cube-png-v2"          # the on-disk format is unchanged from v2
LAYER_COUNT = 800
SIDE        = 800
CHANNELS    = 4                          # RGBA
LAYER_BYTES = SIDE * SIDE * CHANNELS     # 2,560,000 bytes per layer
MAGIC       = b"VCWPNG2\n"               # 8 bytes, opens every layer's payload stream


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return (struct.pack(">I", len(data)) + tag + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


def encode_png_rgba(raw: bytes, width: int = SIDE, height: int = SIDE) -> bytes:
    """Encode a flat RGBA byte buffer (len == width*height*4) into PNG bytes."""
    if len(raw) != width * height * CHANNELS:
        raise ValueError("encode_png_rgba: raw length %d != %d"
                         % (len(raw), width * height * CHANNELS))
    stride = width * CHANNELS
    out = bytearray(height * (stride + 1))      # filter bytes stay 0 from zero-init
    for y in range(height):
        dst = y * (stride + 1) + 1
        out[dst:dst + stride] = raw[y * stride:(y + 1) * stride]
    sig  = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)  # 8-bit RGBA
    idat = zlib.compress(bytes(out), 1)
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


# ---- layer pixel stream (boot sector + payload JSON) <-> RGBA bytes --------
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
