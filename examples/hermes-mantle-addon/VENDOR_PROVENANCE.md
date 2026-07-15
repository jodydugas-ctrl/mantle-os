# Vendored Mantle OS provenance

- Source repository: `https://github.com/jodydugas-ctrl/mantle-os`
- Base repository commit: `59dfe35e13e09fe87e14595fc68a46c16417b3ff` (`main`)
- Snapshot state: Mantle OS `1.3.0` Step-10 working tree, including the reviewed alignment changes not yet represented by the base commit.
- Import method: `python scripts/sync_vendor.py --sync`; the addon itself is excluded to prevent recursive vendoring.
- Snapshot scope: 146 non-addon files covering package metadata, workflows, documents, examples, and `src/mantle`.
- Integrity manifest SHA-256: `1a91f7ca3b89adb12b8c1faeb0a059e7a4d46f6e674aa097791aa74a079bbe17`.
- Reproducible drift check: `python scripts/sync_vendor.py --check`.
- Framework certification: 20/20 Stage-1 rows and 111/111 security invariants.
- Private namespace certification: APPLET-5 and the complete addon Stage-1 path execute under `_hermes_mantle_vendor`.

The base commit and working-tree snapshot are stated separately so uncommitted alignment changes are
not misrepresented as content already present in Git history. Generated caches and local runtime
artifacts are ignored and excluded from the provenance claim.
