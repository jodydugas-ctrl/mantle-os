#!/usr/bin/env python3
"""
lineage.py  --  The boot-driven Cube, and the Organism as a chain of cubes (Mantle v2.1/v2.2)

Because the VCW is append-only, a cube's genome (its band layout, declared in the cube boot
sector) is fixed for that cube's whole life. The ONLY way to a re-fitted genome is a NEW cube.
So REBIRTH = REFORMAT: distill the current Prime, author a new genome, declare a new Prime, and
keep the old cube as read-only ANCESTRAL memory. Generation-pinned references still resolve
against the ancestor, so rebirth loses nothing.

    Organism = BODY (holds the Primer + lineage index)
             + PRIME cube (one, hot, takes all experiential writes)
             + ANCESTRAL cubes (sealed, read-only to experience)

v2.2 -- LAYERS ON DEMAND + SAFE REUSE
  A band reserves a RANGE of layers ([head, head+span-1]) but allocates physical layers only as
  it fills, and reclaims emptied layers into a per-band FREE LIST for reuse. "Every layer has a
  purpose; be efficient." Safe-reuse rule: only entry-addressed (log-json/keyvalue) layers are
  reclaimable; spatial (calendar) and exec layers are never recycled while referenced. Logical
  entry references (<facts.11>) address the band's concatenated VISIBLE stream, so physical reuse
  never breaks them.
"""
from __future__ import annotations

import json
import os
import zipfile
from typing import Any, Dict, List, Optional

from vcw_cube import encode_png_rgba, decode_png_rgba, LAYER_BYTES
from boot import make_band_boot, make_cube_boot, get_driver, code_hash
import drivers  # noqa: F401 -- registers the drivers on import
from drivers import ExecDriver, make_entry, trial
from body import Body
from redact import redact

_EXEC = ExecDriver()
_ENTRY_ENCODINGS = ("log-json", "keyvalue")   # the reclaimable, entry-addressed encodings


class CapacityError(Exception):
    """Raised when a band has used every layer in its reserved range (overflow reflex)."""


# ----------------------------------------------------------------------------
# Standard genome (the default band layout; rebirth can author a different one)
# ----------------------------------------------------------------------------
def standard_genome() -> List[Dict[str, Any]]:
    """The reserved experiential bands. NOTE: no Primer/Genome here -- identity is in the Body.
    Spans are sized to each band's reserved range so Memory's metabolism can grow/reclaim layers."""
    return [
        make_band_boot("identity",    100, "log-json", span=50,  purpose="experiential self-state"),
        make_band_boot("facts",       150, "log-json", span=50,  purpose="durable truths"),
        make_band_boot("events",      200, "log-json", span=50,  purpose="event history"),
        make_band_boot("discoveries", 250, "log-json", span=50,  purpose="learned knowledge"),
        make_band_boot("senses",      300, "log-json", span=100, purpose="sensor intake"),
        make_band_boot("immune",      400, "log-json", span=50,  purpose="audit/defense"),
        make_band_boot("brain",       450, "log-json", span=50,  purpose="dispatch log"),
        make_band_boot("thoughts",    500, "log-json", span=50,  purpose="private reflection",
                       private=True),
    ]


class Cube:
    def __init__(self, generation: int = 0, identity_in_body: bool = True) -> None:
        self.generation = generation
        self.identity_in_body = identity_in_body
        self.sealed = False
        self.bands: Dict[str, Dict[str, Any]] = {}        # name -> boot sector
        self.band_layers: Dict[str, List[int]] = {}        # name -> active physical layer indices
        self.band_free: Dict[str, List[int]] = {}          # name -> reclaimed indices (reuse pool)
        self.layers: Dict[int, Any] = {}                   # physical idx -> driver-native content

    # ---- genesis ----------------------------------------------------------
    @classmethod
    def genesis(cls, genome: List[Dict[str, Any]], generation: int = 0) -> "Cube":
        c = cls(generation=generation)
        for boot in genome:
            name = boot["band"]
            c.bands[name] = boot
            c.band_layers[name] = [boot["head"]]
            c.band_free[name] = []
            c.layers[boot["head"]] = get_driver(boot["encoding"]).empty(boot["params"])
        return c

    # ---- band helpers -----------------------------------------------------
    def _boot(self, band: str) -> Dict[str, Any]:
        if band not in self.bands:
            raise KeyError("no band %r in generation %d" % (band, self.generation))
        return self.bands[band]

    def _driver(self, band: str):
        return get_driver(self._boot(band)["encoding"])

    def encoding(self, band: str) -> str:
        return self._boot(band)["encoding"]

    def primary_layer(self, band: str) -> int:
        """The band's single-layer home (for calendar/exec bands and boot location)."""
        return self.band_layers[band][0]

    def layer_count(self, band: str) -> int:
        return len(self.band_layers[band])

    def free_count(self, band: str) -> int:
        return len(self.band_free[band])

    # ---- on-demand layer allocation within the band's range ---------------
    def _allocate(self, band: str) -> int:
        """Allocate one physical layer for the band: reuse a freed slot if available, else take
        the next unused index in [head, head+span-1]; raise CapacityError if the range is full."""
        boot = self._boot(band)
        if self.band_free[band]:                          # prefer reuse (efficiency)
            idx = self.band_free[band].pop(0)
        else:
            head, span = boot["head"], boot["span"]
            used = set(self.band_layers[band]) | set(self.band_free[band])
            free_slots = [i for i in range(head, head + span) if i not in used]
            if not free_slots:
                raise CapacityError("band %r exhausted its %d reserved layers (overflow reflex: "
                                    "compact, tier, or motivate a rebirth-reformat)"
                                    % (band, span))
            idx = free_slots[0]
        self.layers[idx] = get_driver(boot["encoding"]).empty(boot["params"])
        self.band_layers[band].append(idx)
        return idx

    # ---- the three verbs (dispatch through the band's driver) -------------
    def append(self, band: str, value: Any) -> Any:
        if self.sealed:
            raise PermissionError(
                "generation %d is ANCESTRAL (read-only); experiential writes go to PRIME only"
                % self.generation)
        boot = self._boot(band)
        drv = self._driver(band)
        tail = self.band_layers[band][-1]
        # on-demand allocation: roll to a new layer when the tail reaches its capacity
        cap = boot["params"].get("max_entries_per_layer")
        if cap and boot["encoding"] in _ENTRY_ENCODINGS and len(self.layers[tail]) >= cap:
            tail = self._allocate(band)
        self.layers[tail] = drv.append(self.layers[tail], boot["params"], value)
        return value

    def read(self, band: str, reveal_private: bool = False) -> Any:
        boot = self._boot(band)
        if boot["private"] and not reveal_private:
            return []                                     # the veil (a Body reflex)
        drv = self._driver(band)
        if boot["encoding"] == "log-json":                # concatenate the visible stream
            out: List[Any] = []
            for idx in self.band_layers[band]:
                out.extend(drv.read(self.layers[idx], boot["params"], reveal_private))
            return out
        if boot["encoding"] == "keyvalue":
            merged: Dict[str, Any] = {}
            for idx in self.band_layers[band]:
                merged.update(drv.read(self.layers[idx], boot["params"]))
            return merged
        return drv.read(self.layers[self.primary_layer(band)], boot["params"], reveal_private)

    def retrieve(self, band: str, address: Any) -> Any:
        boot = self._boot(band)
        if boot["private"]:
            return None
        drv = self._driver(band)
        if boot["encoding"] == "log-json":
            vis = self.read(band)
            i = int(address)
            return vis[i] if 0 <= i < len(vis) else None
        if boot["encoding"] == "keyvalue":
            for idx in self.band_layers[band]:
                v = drv.retrieve(self.layers[idx], boot["params"], address)
                if v is not None:
                    return v
            return None
        return drv.retrieve(self.layers[self.primary_layer(band)], boot["params"], address)

    # ---- metabolism: compaction reclaims emptied layers (safe reuse) ------
    def compact(self, band: str) -> Dict[str, Any]:
        """Drop tombstoned/quarantined entries; reclaim any non-tail layer that becomes empty
        into the free list. Only entry-addressed bands are reclaimable (safe-reuse rule)."""
        boot = self._boot(band)
        if boot["encoding"] not in _ENTRY_ENCODINGS:
            return {"band": band, "reclaimed": 0, "note": "spatial/exec layers are not reclaimed"}
        reclaimed = 0
        keep: List[int] = []
        for pos, idx in enumerate(self.band_layers[band]):
            live = [e for e in self.layers[idx]
                    if not e.get("tombstone") and not e.get("quarantined")]
            self.layers[idx] = live
            is_last_remaining = (len(self.band_layers[band]) - reclaimed) <= 1
            if not live and not is_last_remaining:
                del self.layers[idx]
                self.band_free[band].append(idx)          # return to the reuse pool
                reclaimed += 1
            else:
                keep.append(idx)
        self.band_layers[band] = keep or [self.band_layers[band][0]]
        return {"band": band, "reclaimed": reclaimed,
                "active": len(self.band_layers[band]), "free": len(self.band_free[band])}

    def tombstone_all(self, band: str) -> int:
        """Mark every visible entry in a band tombstoned (test/demo helper for compaction)."""
        n = 0
        for idx in self.band_layers[band]:
            for e in self.layers[idx]:
                if not e.get("tombstone"):
                    e["tombstone"] = True
                    n += 1
        return n

    # ---- calendar convenience --------------------------------------------
    def calendar_set(self, band: str, iso: str, meaning: str) -> None:
        boot = self._boot(band)
        if self.sealed:
            raise PermissionError("generation %d is ANCESTRAL (read-only)" % self.generation)
        layer = self.primary_layer(band)
        self.layers[layer] = self._driver(band).append(self.layers[layer], boot["params"],
                                                       (iso, meaning))

    def calendar_get(self, band: str, iso: str) -> str:
        boot = self._boot(band)
        return self._driver(band).get_date(self.layers[self.primary_layer(band)],
                                           boot["params"], iso)

    # ---- reflex layers (calcify + invoke) --------------------------------
    def calcify(self, band: str, code: str, entry: str, signature: Dict[str, Any],
                capabilities: Dict[str, Any], provenance: Dict[str, Any],
                limits: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Promote proven code into an exec (reflex) layer. PRIME only; hashed + capability-bound."""
        if self.sealed:
            raise PermissionError("cannot calcify into an ancestral cube")
        if self.encoding(band) != "exec":
            raise ValueError("band %r is not an exec band" % band)
        content = {"code": code, "code_hash": code_hash(code), "entry": entry,
                   "language": "python", "signature": signature,
                   "capabilities": capabilities, "limits": limits or {"ms": 200},
                   "provenance": provenance}
        self.layers[self.primary_layer(band)] = content
        return content

    def invoke(self, band: str, args: Dict[str, Any],
               granted: Optional[Dict[str, Any]] = None) -> Any:
        """Run a calcified reflex. Works with NO MIND -- this is a zombie-state capability."""
        content = self.layers[self.primary_layer(band)]
        if not content:
            raise ValueError("reflex band %r is empty (no skill calcified)" % band)
        return _EXEC.execute(content, args, granted)

    # ---- persistence ------------------------------------------------------
    def save(self, path: str) -> None:
        meta = {"generation": self.generation, "identity_in_body": self.identity_in_body,
                "sealed": self.sealed, "bands": self.bands,
                "band_layers": self.band_layers, "band_free": self.band_free, "content": {}}
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for band, boot in self.bands.items():
                for idx in self.band_layers[band]:
                    content = self.layers[idx]
                    if boot["encoding"] == "calendar-spatial":
                        z.writestr("layers/%03d.png" % idx, encode_png_rgba(bytes(content)))
                        meta["content"][str(idx)] = {"__png__": "layers/%03d.png" % idx}
                    else:
                        meta["content"][str(idx)] = content
            z.writestr("cube.json", json.dumps(meta, indent=2))

    @classmethod
    def load(cls, path: str) -> "Cube":
        with zipfile.ZipFile(path, "r") as z:
            meta = json.loads(z.read("cube.json"))
            c = cls(generation=meta["generation"],
                    identity_in_body=meta.get("identity_in_body", True))
            c.sealed = meta.get("sealed", False)
            c.bands = meta["bands"]
            c.band_layers = {k: list(v) for k, v in meta["band_layers"].items()}
            c.band_free = {k: list(v) for k, v in meta.get("band_free", {}).items()}
            for band, boot in c.bands.items():
                for idx in c.band_layers[band]:
                    stored = meta["content"][str(idx)]
                    if boot["encoding"] == "calendar-spatial":
                        c.layers[idx] = bytearray(decode_png_rgba(z.read(stored["__png__"])))
                    else:
                        c.layers[idx] = stored
        return c

    def verify(self) -> List[str]:
        problems = []
        for band, boot in self.bands.items():
            if not self.band_layers.get(band):
                problems.append("band %s has no active layer" % band)
            try:
                get_driver(boot["encoding"])
            except KeyError:
                problems.append("band %s names unknown driver %s" % (band, boot["encoding"]))
            # active and free layer sets must not overlap (reuse integrity)
            if set(self.band_layers.get(band, [])) & set(self.band_free.get(band, [])):
                problems.append("band %s has a layer both active and free" % band)
        return problems


# ============================================================================
# Organism : Body + Prime cube + ancestral chain
# ============================================================================
class Organism:
    def __init__(self, body: Body, prime: Cube) -> None:
        self.body = body
        self.prime = prime
        self.ancestral: List[Cube] = []
        self.immune_log: List[Dict[str, Any]] = []
        self._sync_lineage()

    @classmethod
    def birth(cls, identity: Dict[str, Any], truths: List[str], commandments: List[str],
              genome: Optional[List[Dict[str, Any]]] = None) -> "Organism":
        body = Body()
        body.birth(identity, truths, commandments)
        prime = Cube.genesis(genome or standard_genome(), generation=0)
        return cls(body, prime)

    # ---- lineage bookkeeping ---------------------------------------------
    def _sync_lineage(self) -> None:
        self.body.prime_generation = self.prime.generation
        self.body.lineage_index[self.prime.generation] = {"role": "prime", "location": "prime"}
        for c in self.ancestral:
            self.body.lineage_index[c.generation] = {"role": "ancestral",
                                                     "location": "gen%03d" % c.generation}

    def cube_for_generation(self, gen: int) -> Optional[Cube]:
        if gen == self.prime.generation:
            return self.prime
        for c in self.ancestral:
            if c.generation == gen:
                return c
        return None

    # ---- senses: the inbound boundary (redact before anything is remembered) ----
    def sense(self, signal: Any, opcode: str = "SENSE") -> Dict[str, Any]:
        """The sense boundary. Redact secrets BEFORE the signal becomes permanent VCW memory
        (B-20 / HF-B20), then append to the senses band. Deterministic, no MIND."""
        entry = make_entry(redact(signal), opcode=opcode, author="BODY")
        self.prime.append("senses", entry)
        return entry

    # ---- immune ----------------------------------------------------------
    def immune_event(self, kind: str, detail: Any) -> None:
        # redact at the boundary: a secret must never be burned into the immune log
        evt = {"kind": kind, "detail": redact(detail)}
        self.immune_log.append(evt)
        try:
            self.prime.append("immune", make_entry(evt, opcode="IMMUNE", author="BODY"))
        except Exception:
            pass  # fail-open: immune logging must never crash the organism

    # ---- rebirth = reformat ----------------------------------------------
    def rebirth(self, new_genome: Optional[List[Dict[str, Any]]] = None,
                reason: str = "reformat") -> "Organism":
        """MIND-chosen. Distill Prime -> seal it as ancestral -> new Prime with a (possibly new)
        genome. The Body keeps the Primer; nothing identity-bearing is copied between cubes."""
        distillation = {"from_generation": self.prime.generation, "reason": reason,
                        "fact_count": len(self.prime.read("facts"))}
        self.prime.sealed = True
        self.ancestral.append(self.prime)
        new_gen = self.prime.generation + 1
        self.prime = Cube.genesis(new_genome or standard_genome(), generation=new_gen)
        self.prime.append("discoveries", make_entry(
            {"inheritance": distillation}, opcode="INHERIT", author="BODY",
            source="<gen%d:facts>" % distillation["from_generation"]))
        self._sync_lineage()
        return self

    # ---- reference resolution (delegated to refs.py) ---------------------
    def resolve(self, ref: str) -> Any:
        import refs
        return refs.resolve(self, ref)

    # ---- persistence ------------------------------------------------------
    def save(self, directory: str) -> None:
        os.makedirs(directory, exist_ok=True)
        self.prime.save(os.path.join(directory, "gen%03d.vcw" % self.prime.generation))
        for c in self.ancestral:
            c.save(os.path.join(directory, "gen%03d.vcw" % c.generation))
        with open(os.path.join(directory, "body.json"), "w") as f:
            json.dump(self.body.to_dict(), f, indent=2)
        with open(os.path.join(directory, "organism.json"), "w") as f:
            json.dump({"prime_generation": self.prime.generation,
                       "ancestral_generations": [c.generation for c in self.ancestral]},
                      f, indent=2)

    @classmethod
    def load(cls, directory: str) -> "Organism":
        with open(os.path.join(directory, "organism.json")) as f:
            org = json.load(f)
        with open(os.path.join(directory, "body.json")) as f:
            body = Body.from_dict(json.load(f))
        prime = Cube.load(os.path.join(directory, "gen%03d.vcw" % org["prime_generation"]))
        o = cls(body, prime)
        o.ancestral = [Cube.load(os.path.join(directory, "gen%03d.vcw" % g))
                       for g in org["ancestral_generations"]]
        o._sync_lineage()
        return o


__all__ = ["Cube", "Organism", "standard_genome", "make_band_boot",
           "make_entry", "trial", "code_hash", "CapacityError"]
