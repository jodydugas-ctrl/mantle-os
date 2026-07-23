# VCW Anatomical Atlas v1

This atlas defines how existing VCW images should be read as measurements. It
does not add a renderer, a new storage format, a calibration grid, or a colour
ontology. Live code remains the source of behavioural truth; this document names
the anatomy in one place so diagrams, spores, faces, and audits use the same
measurement vocabulary.

The machine-readable companion is `mantle.vcw.atlas`.

## Coordinate Ownership

The cube body plan is `vcw-cube-png-v2`: 800 layers, each an 800 by 800
non-interlaced 8-bit RGBA PNG. A byte inside a layer is addressed as:

```text
offset = (y * SIDE + x) * CHANNELS
```

Layer ownership is band ownership. A band owns the half-open layer range
`[head, head + span)` declared by its boot sector. The standard genome owns
identity, facts, events, discoveries, senses, immune, brain, and private
thoughts bands. App bands live in 550-749, with framework-reserved ranges
declared by `APP_BAND_ATLAS`; caller bands must be allocated only from gaps.
Layers 750-799 are tail space.

The spore body plan is `spore-png-v1`: a 2000 by 2000 RGBA PNG. Its top half is
the canonical VCW region, and its bottom half is display. The protected boot
strip is inside the display region. These regions must remain disjoint.

## Colour And Transparency Semantics

Content colour is payload. In a cube spatial layer, RGBA stores the spatial
state directly; alpha 0 means free and alpha 255 means occupied. In a spore,
RGB stores payload bytes and alpha is the T repair byte for Hamming SECDED.

Activity colour is status. The face/self-portrait uses colours for pressure,
organ state, lineage, and immune ticks. Those colours are diagnostic display
signals, not canonical payload.

Private or veiled tissue may be marked in an activity view, but its content must
not be exposed through a public measurement surface. A private band still owns
coordinates; the veil controls what crosses the boundary.

## Measurement Rules

Measurement views must be deterministic: the same canonical state produces the
same measurement image or atlas data.

Inspection scaling must use nearest-neighbor sampling. Interpolation invents
colours between pixels and is not valid for measuring VCW coordinates or repair
bytes.

Display regions and content regions are separate. A visible display may explain
the substrate, but it is not the canonical memory unless the body plan explicitly
declares it as such.

The atlas is intentionally small. It standardizes coordinate ownership, content
versus activity colour, transparency meaning, private tissue boundaries, and
deterministic inspection. It deliberately excludes complex colour ontology,
calibration grids, version negotiation, and renderer rewrites.
