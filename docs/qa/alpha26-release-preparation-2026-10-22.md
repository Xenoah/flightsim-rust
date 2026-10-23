# Alpha.26 HUD successor: local source preparation

Date: 2026-10-22. Base: merged main
`e2e23ce1e954fd34ea6dd90a102a17ca0a7d3f4b`, tree
`1ea5182a0ca7ea9883ea6a5b18ba4db9ad032cda` (HUD PR #57).
This is preparation, not a published alpha.26 or native runtime acceptance.

## Bounded source

The merged HUD change shares measured space between live CHASE traffic and
flight guidance and retains the full traffic reference while paused. This
preparation adds no runtime change: only one workspace and thirteen local
lockfile version fields change from alpha.25 to alpha.26. Crate, aircraft,
asset, dependency, feature, cloud, replay and component-terms bytes are exact.
README/CHANGELOG and this guide describe the successor without claiming release.

Five exact Git-blob witnesses retain both Cargo inputs and all three current
source contracts. The new outer validator preserves the complete 995-pin HUD
proof and earlier migration chain, adding six witnesses/descriptor inputs to
reach 1001. Analytical and capture boundaries are 65 and four inputs. The base
is explicitly a merged main commit, not a released binary.

## Evidence separation

Main CI run [39615600851](https://github.com/Xenoah/flightsim-rust/actions/runs/39615600851)
passed all 12 jobs on the HUD base. MSVC engineering run
[39615600801](https://github.com/Xenoah/flightsim-rust/actions/runs/39615600801)
completed its dual build audit, but its original artifact explicitly records
`native_runtime_qualified=false`, `distribution_qualified=false` and
`release_authorized=false`. Those facts remain about that exact base only.

The latest published alpha.25 tag points to
`5082b772c6f2d220377c1031aaa91a0e96c5aec1`, before the HUD change.
Its native applicability remains historical and is not rebound by this source
preparation. A separate inventory-bound alpha.26 receipt records publication
permission only; it does not establish native runtime or distribution success.
Final-source applicability, same-build archive verification and both aircraft
smokes must still pass independently. No conversation content or simulated
native result is added to the repository.

Fresh Linux-hosted, Windows-target Cargo metadata and dependency notices were
collected before and after the version edit in the same checkout using Rust
1.93.0. Complete metadata and graph comparison shows version substitution only;
notice text is unchanged. See the separate
[source/notice amendment](alpha26-dependency-notice-review-2026-10-22.md).
This does not establish a Windows binary, DLL closure or execution result.

## Required next stages

1. Complete clean-source tests and independent review for the final prepared tree.
2. Obtain genuine final-source Windows capture with retained original metadata,
   graph, compiler/link observations, executable and private logs.
3. Substantively compare all eleven native-content sections with the historical
   applicability basis; resolve actual differences without normalizing unknowns.
4. Bind genuine publication authority to the final version/source/release
   inventory only when that action is authorized; update applicability only from
   actually reviewed evidence.
5. Run final CI and the existing same-build archive/extraction and Light Single
   cockpit plus Swift Sport chase smoke chain. Inspect the actual images.
6. Only after authorized publication, verify exact remote source/tag and all five
   assets. Physical GPU/input/audio acceptance remains separate from software smoke.

No Windows capture or release execution was initiated by this local preparation.

## Local source verification

The new alpha.26 admission suite passed all nine tests. Independent review
reproduced the version-only metadata/graph comparison, all original/supplemental
notice bytes, all 510 header spans and all 347 exact-feature sets (plus twelve
conservative-only null sets), without changing historical native facts.

Canonical production capture-source verification passed on local preparation
commit `357789351237f38b7b4e69753020479f35f194f7`, tree
`75c1632eea9f17799d8f56ef40254d961cbedafa`, covering 3577 tracked files and the
1001/65/4 admission boundaries. The final committed source must be rechecked
again; this source proof does not claim a Windows build or execution.

The full Python suite includes a real-HEAD committed-archive test. Before the
preparation commit it correctly rejected the six uncommitted successor inputs
missing from the old HEAD archive. No test or guard was weakened: its prerequisite
is the committed current source, and the unchanged test is rerun against that
source. Complete clean-head CI remains required before merge.
