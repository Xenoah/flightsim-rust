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

## Verification in progress

- Initial world tests passed at six city locations, plus deterministic revisits,
  invalid/polar/date-line queries, LOD overlap and spatial exclusions.
- Coastal Sydney centre (-33.87, 151.21) was completely suppressed by the existing
  coarse water mask. The positive Sydney case is inland (-33.87, 151.05).
- Runtime CPU/ECS tests, aggregate Rust checks and Linux software Vulkan screenshots
  are pending completion. Do not interpret this checkpoint as a passing report.
- Development toolchain: official Rust 1.93.0, crates.io locked dependencies;
  Debian-signed packages extracted locally under `/workspace/flightsim-deps`.
  No system authentication, security setting or package policy was changed.
- Logs are retained under `/workspace/flightsim-evidence`. Reproducible local env:
  `/workspace/flightsim-env.sh`. These paths are workspace evidence, not release assets.

## Consent and remaining acceptance boundaries

Windows normal capture remains pending the user's own choice on the Microsoft
component supplement (`2026-10-09-2`, English SHA-256
`052656e63c7f2df77a7cfffb7d78fcbb64d8525f9d0ca69d39e5475e5bce9d20`).
The concrete action is to run `flightsim-app.exe --component-terms` on Windows,
read the complete terms, and choose Agree/Decline personally. No receipt, consent
click, smoke-mode substitute or bypass was made. This is a pending user choice,
not an auto-review denial. Linux's existing non-Windows admission branch requires
no such receipt; Linux testing does not establish Windows/physical-GPU acceptance.

This is development work only. Release source admissions and historical exact-byte
allowlists must not be rewritten to borrow an earlier PR's approval. Any PR remains
draft; no merge, Ready conversion, release, paid service or API key is authorized.
