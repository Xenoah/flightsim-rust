# Cloud urban scenery checkpoint — 2026-10-24

Worktree: `/workspace/flightsim-rust`, branch `agent/cloud-offline-urban-fallback`.
Base: `fc2ca797a1e13b36f208fbcbbab5fce647b172e7` (published alpha.26 main).
The unrelated `/workspace/meshcopia` repository was not modified.

The offline desktop branch `agent/offline-urban-fallback` was not published in
GitHub's branch list. Its uncommitted files could not be recovered into this
workspace. No direct desktop access was attempted. This implementation is an
independent reconstruction from main and the reported design; it is not a saved
copy of the desktop changes, and desktop test claims are not used as evidence.
No unpublished cloud-rendering candidate was imported. Existing HUD layout source
is unchanged. No AGENTS.md or .agents/skills files were present in the target
checkout; CLAUDE.md, HANDOFF, architecture and relevant ADRs supplied local guidance.

## Current implementation

See [offline urban scenery](../global-urban-scenery.md). The official Natural Earth
input was fetched from its upstream GitHub release after the official website/S3
ZIP URLs failed. Its hash and reproducible rasterization are recorded alongside
the bundled 925,730-byte index. The prior desktop's reported 4.42 MB artifact was
not reused. Source locations are approximate historical mapped urban extent;
individual buildings/streets/heights are invented. Precise world building tiles
remain unimplemented.

## Final application validation

Application source tested/captured: `c2b177d32a209b4d4a43044b53ea6d39d2ade308`.
The subsequent evidence commit changes documentation and captured artifacts only.
Draft PR: <https://github.com/Xenoah/flightsim-rust/pull/60>.

- Pure-Rust aggregate: 1,395 tests passed (105 test binaries; `--all-targets`,
  core/fdm/world/sim/tilegen/assetgen/net/content with content downloads). Zero failures.
- Render/input/UI/audio/app aggregate: 1,375 passed, zero failures, 3 existing
  ignored tests (optional real regional fixture, external Haneda terrain fixture,
  and manual quiet-window mesh latency benchmark). Combined Rust aggregates:
  2,770 passed. Pure-library doctests: 6 passed.
- Full workspace Clippy `--workspace --all-targets -- -D warnings`, normal app
  build, `cargo fmt --all -- --check`, dependency architecture check and diff
  whitespace check passed. The pure-library Clippy group also passed separately.
- World urban tests: 8 passed, including six cities, deterministic revisits,
  invalid/polar/date-line queries, LOD overlap, spatial exclusions, coastal
  suppression and source-kind roundtrip. Baker hole/hash/interval tests: 2 passed.
- Criterion (`--profile dev`, Rust 1.93.0, shared cloud runner): London 4.5 km,
  cap 2,048 buildings, 6.198–6.429 ms (quick estimate). This is CPU source generation,
  not mesh preparation, GPU time or a general frame-time guarantee.
- Coastal Sydney centre (-33.87, 151.21) was completely suppressed by the existing
  coarse water mask. The positive Sydney case is inland (-33.87, 151.05).
- First Linux software Vulkan capture pass completed in all six regions (exit 0).
  It exposed excessive generated facade detail: London used 599,982 vertices for
  only 572 buildings, leaving most surrounding city blocks omitted. A development
  follow-up limits generated facades to 350 m while retaining regional 2.4 km detail.
  The final CPU test requires >1,500 rendered buildings in each positive region.
  The rebuilt final screenshots and render aggregate now pass. London prepares
  all 2,048 buildings in 90,648 vertices; this is still a bounded, nearby view,
  not an uninterrupted city extending to the horizon.
- Python source/release aggregate completed: 829 tests, 15 failures, 92 errors,
  1 skipped (721 passed). Failures are exact reviewed-source hashes/closure admissions.
  Isolated reproduction: `test_alpha22_version_source_admission` rejects changed
  `.gitattributes` canonical SHA-256; the same test PASSES on pristine fc2ca797.
  Existing admission pins and approvals are deliberately unchanged. These failures
  are release/source-admission blockers, not a claim that all CI has passed.
- Independent checks normally following that failing Python aggregate were run
  separately and passed: terrain packer (5), aircraft profile schemas (2 + 1),
  replay identity/v3/v4, subsonic and jet identity references, and the Meadow
  Trainer asset validator. No Blender execution or external data download was
  needed for the validator.
- Development toolchain: official Rust 1.93.0, crates.io locked dependencies;
  Debian-signed packages extracted locally under `/workspace/flightsim-deps`.
  No system authentication, security setting or package policy was changed.
- Logs are retained under `/workspace/flightsim-evidence`. Reproducible local env:
  `/workspace/flightsim-env.sh`. These paths are workspace evidence, not release assets.

Reproduction (ordinary offline execution, default features):

```sh
cargo test --locked -j 2 -p flightsim-core -p flightsim-fdm -p flightsim-world -p flightsim-sim -p flightsim-tilegen -p flightsim-assetgen -p flightsim-net -p flightsim-content --features flightsim-content/downloads --all-targets
cargo test --locked -j 2 -p flightsim-render -p flightsim-input -p flightsim-ui -p flightsim-audio -p flightsim-app --all-targets
cargo clippy --locked -j 2 --workspace --all-targets -- -D warnings
cargo build --locked -j 2 -p flightsim-app
python3 -m unittest scripts.tests.test_bake_urban -v
bash scripts/check-architecture.sh
```

## Final screenshots

All nine original 1280 × 720 PNGs were opened and visually inspected. All
processes exited 0. The adapter was **llvmpipe LLVM 19.1.7 / Mesa 25.0.7, CPU
software Vulkan** on Debian 13. These are actual application captures, not a
browser mockup. Physical GPU, Windows application runtime and audio playback
are not qualified by these images. HUD layout source was not modified.

| Capture | Buildings prepared | Vertices | Observation |
| --- | ---: | ---: | --- |
| [Tokyo](global-urban-2026-10-24/tokyo.png) | 2,048 | 66,930 | Fictional urban blocks visible |
| [London](global-urban-2026-10-24/london.png) | 2,048 | 90,648 | Surrounding blocks survive facade LOD |
| [New York](global-urban-2026-10-24/new-york.png) | 1,791 | 77,640 | Bounded generated coverage |
| [Sydney inland](global-urban-2026-10-24/sydney-inland.png) | 2,044 | 190,416 | Positive inland case; 4 features omitted by existing mesh rules |
| [São Paulo](global-urban-2026-10-24/sao-paulo.png) | 2,048 | 73,224 | Fictional urban blocks visible |
| [Cairo](global-urban-2026-10-24/cairo.png) | 2,045 | 138,078 | 3 features omitted by existing mesh rules |
| [Sydney coast](global-urban-2026-10-24/sydney-coast.png) | 0 | 0 | Coarse water mask excludes 2,275 candidate features |
| [Default synthetic airfield](global-urban-2026-10-24/default-synthetic-airfield.png) | 1,786 | 59,160 | Clear runway corridor; 105 exclusions; not surveyed Haneda geometry |
| [London at 900 m](global-urban-2026-10-24/london-900m.png) | 2,048 | 90,648 | Higher view shows the deliberate coverage limit |

[Capture metadata](global-urban-2026-10-24/capture-summary.json) includes exact
coordinates, commands, PNG hashes and the common application binary SHA-256.
Adjacent `.log` files retain adapter, scenery statistics and successful capture
lines. Environment selected Vulkan and the installed software ICD with
`WGPU_BACKEND=vulkan`, `LIBGL_ALWAYS_SOFTWARE=1`,
`VK_ICD_FILENAMES=/workspace/flightsim-deps/usr/share/vulkan/icd.d/lvp_icd.json`.
The common binary SHA-256 is
`00a54f98b042bed13dc001ed86e4e5fc8585d93b2681405963f2209f8df51a37`.
`--cloud-cover 0` is the existing clear-weather option; no separate cloud-rendering
candidate was used. Complete local validation logs are summarized and hashed in
[validation metadata](global-urban-2026-10-24/validation-summary.json).

## CI state and source-admission blocker

At the evidence checkpoint, [CI run 40053956184](https://github.com/Xenoah/flightsim-rust/actions/runs/40053956184)
for application commit `c2b177d` passed Linux core, Rust 1.85 pure-library MSRV,
architecture, documentation, both OS public synthetic download checks and the
ordinary software-Vulkan app smoke. Both OS render groups, Windows core benchmark
compilation, analytical-tonemapping source/build and world source-tool boundaries
were still running. This is a timestamped checkpoint, not their final result;
the PR carries the latest status. In particular, the source/release aggregate
failure above remains unresolved and this change is not merge/release ready.

## Consent and remaining acceptance boundaries

Windows normal capture remains pending the user's own choice on the Microsoft
component supplement (`2026-10-09-2`, English SHA-256
`052656e63c7f2df77a7cfffb7d78fcbb64d8525f9d0ca69d39e5475e5bce9d20`).
The concrete action is to run `flightsim-app.exe --component-terms` on Windows,
read the complete terms, and choose Agree/Decline personally. No receipt, consent
click, smoke-mode substitute or bypass was made. This is a pending user choice,
not an auto-review denial. The unmodified
`crates/flightsim-app/src/component_terms.rs::enforce` calls the consent flow only
inside `#[cfg(windows)]`; its existing `#[cfg(not(windows))]` normal-startup branch
returns `Ok(Admission::Continue)`. The nine captures used this ordinary Linux
path, not `--internal-release-smoke`. No Microsoft component assent was recorded
or inferred. Linux testing does not establish Windows/physical-GPU acceptance.

This is development work only. Release source admissions and historical exact-byte
allowlists must not be rewritten to borrow an earlier PR's approval. Any PR remains
draft; no merge, Ready conversion, release, paid service or API key is authorized.
