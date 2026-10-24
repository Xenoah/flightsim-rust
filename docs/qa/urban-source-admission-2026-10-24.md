# Offline urban scenery: bounded source review

This source-only successor reviews application commit
`c2b177d32a209b4d4a43044b53ea6d39d2ade308` against published alpha.26 main
`fc2ca797a1e13b36f208fbcbbab5fce647b172e7` (tree
`999bf0474859647c139d9fed3b281aa1d2f80107`). The desktop's unavailable uncommitted
work is not evidence. This review does not grant publication permission, record
recipient assent, qualify a native build, or reinterpret the earlier failed CI.

## Reviewed implementation boundary

The nine replaced inputs have these specific effects:

- `.gitattributes` adds only `*.fsua binary`, preserving baked bytes on Windows.
- `ATTRIBUTION.md` appends Natural Earth provenance, the invented-geometry
  distinction and an explicit statement that the notice is not release approval.
- `scenery_runtime.rs` enables the bounded fallback for ordinary global terrain,
  keeps regional source priority and existing resource budgets, shares the global
  land mask, excludes whole features near known runways and loaded airport ground,
  and reduces generated facade detail to 350 m. It neither mutates flight physics
  nor fetches network data. Unreadable or overflowing airport exclusions fail closed.
- `scenery_runtime_tests.rs` adds default-start, six-region mesh-budget, full
  runway-footprint/relocation and regional-priority regressions.
- `world_runtime.rs` refreshes scenery configuration after map relocation while
  retaining the cancelled worker until completion; old geometry is cleared first.
- World `lib.rs` exports `urban`; `scenery.rs` and `scenery/io.rs` add source kind
  3 and its explicit fictional attribution. Existing kinds 1/2 are unchanged.
  Older readers reject the new kind instead of silently misidentifying its source.
- World `benches/scenery.rs` adds one CPU generation benchmark without changing
  the existing benchmark or treating its timing as a frame-rate guarantee.

Four new crate inputs are admitted explicitly: the urban generator, its tests,
the 925,730-byte index and its provenance JSON. The generator validates the index,
uses stable globally anchored parcel identities and the existing core coordinate
conversion, limits cells/candidates/buildings/streets, checks cancellation, and
requires land/water and airport/regional exclusion checks. Independent tests cover
six cities, repeatability, LOD overlap, bounds, source roundtrip and exclusions.
No dependency, package version, flight dynamics, replay codec, aircraft asset,
cloud implementation, HUD layout or consent-code change is admitted.

The two baker files and urban explanation are also pinned. The standard-library
baker's CLI accepts only the fixed official Natural Earth v5.1.2 shapefile hash;
even/odd scanlines preserve holes. Its binary output/provenance hash and known
cell counts are checked. Natural Earth's public-domain urban extent is historical
and coarse; individual buildings, roads and heights are invented. Small waterways
and unknown airports remain unresolved, and central Sydney is conservatively
omitted. This is not surveyed worldwide building coverage or collision geometry.

## Preservation and adversarial verification

All 1,001 alpha.26 replay pins remain evidence for their original bytes. Nine
changed files are retained as exact `fc2ca797-*` Git-blob witnesses, alongside
all three original source contracts. The original alpha.26 validator and complete
earlier migration chain remain mandatory. An outer closed descriptor admits only
the listed replacements/additions, with fixed hashes independent of the mutable
descriptor and contract. The original 497 runtime identities and 102 independent
physics/replay anchors remain unchanged; the live crate boundary grows by exactly
four members. No on-disk glob selects admitted additions.

The analytical wrapper preserves its complete 69-input predecessor and the
unchanged CI60 workflow proof. Only source auditors/contracts, this source guide
and affected historical/current test assertions are rebound; a dedicated urban
adversarial test is added. The capture boundary retains four inputs. Capture
commands, native gates, target selection, notice collection and publication
authorization logic remain unchanged. Historical/current assertions are moved
to the appropriate frozen witness rather than deleted.

Tests must reject omitted/aliased/extra inputs, altered prior witnesses, mutated
urban code/data/provenance, jointly resealed descriptors/contracts, hidden
checkout edits and forged exported source evidence. They must also reject
release/native/assent claims. Genuine native runtime, whole-target applicability,
same-build packaging and exact-inventory publication authority remain separate.

Application validation before this source-only amendment: 2,770 ordinary Rust
tests, 6 doctests, workspace Clippy and build passed; optional region-download
configuration passed 570 tests and Clippy. Nine Linux software-Vulkan screenshots
were inspected. Three ordinary and one overlapping optional fixture/manual tests
were ignored as documented. Neither this review nor those Linux results supplies
Windows assent or physical-GPU/audio qualification. See the separate cloud QA
record for original failures, commands and screenshots; fresh source-admission
tests and CI are required for the amended source.
