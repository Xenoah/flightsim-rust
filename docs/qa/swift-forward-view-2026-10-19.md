# Swift Sport initial forward view

2026-10-19. Local source proposal based on
`de2e4d35ef21cd35c4445d7c6eb8a12bed48fed7`. This report does not grant source
admission, native acceptance, distribution rights or publication approval.

## Bounded change

- Only Sport's centered look angle changes, from 24 to 15 degrees down.
  Trainer/Meadow remain at 15 degrees and JetTrainer remains at 24 degrees.
- Both Sport stick assemblies move 0.10 m forward relative to the eye. The
  shafts, grips, ribs, gaiters, animation pivots and attached hit surfaces move
  together. A camera-only change would put the previous neutral grips below the
  default viewport; the existing viewport requirement is retained.
- The 60-degree vertical FOV, eye/profile data, PFD/stack geometry and artwork,
  materials, lighting, input arbitration, control bindings, flight dynamics and replay
  are unchanged.
  The panel's trim wheel/pedals still require looking down.
- No assets, aircraft selection, licenses, distribution lists, source-admission
  checks or CI/release budgets are changed.

## Actual image comparison

The evidence bundle contains six original application PNGs: `before-day.png`,
`before-night.png`, `before-approach.png` and the matching `candidate-*` images.
All six were completely decoded at 1280 x 720, exited with status 0, and were
visually inspected. They were not regenerated, retouched, resized or composited.

The baseline executable is built from
`fbb53429bcae8a94078ea96f528b0b2ad216fdfe`, SHA-256
`9514a96a8ebc133b2d1b8a4ed12ae5ffced8aa2b1dcf42ad449f2fefca961849`.
Its runtime `crates/`, `vendor/` and `assets/` files are identical to the base
commit above; the package version differs. Both executables were run again for
this comparison using the same unchanged Swift assets.

The candidate executable SHA-256 is
`2c5845c750da119b9d84e632aecd1efab190f2d07405c9a94f2402b6ce273a52`.
Its compiled source hashes are retained with the build log and dep-info. App and
render artifacts were explicitly invalidated before building; the verbose Rust
commands and dep-info identify the independent candidate checkout, avoiding a
previously observed stale-binary reuse across checkouts.

Both use Rust 1.93.0, ordinary/default features, dev opt-level 1, dependency
opt-level 1, no debug info/incremental build, and Mesa 25.0.7 llvmpipe
(LLVM 19.1.7) CPU Vulkan. The command is:

```sh
cargo +1.93.0 build --locked -j 1 \
  --config 'profile.dev.package."*".opt-level=1' -p flightsim-app -vv
```

Both use cockpit view, beginner, clear seed 0, traffic off, wind 0/0,
turbulence calm, date 2026-06-21, time-rate 0, light graphics/water/cloud quality,
standard draw distance and screenshot-delay 5. Day uses 12:00, night 22:00,
and approach 12:00 with `--approach 1.5`. Each capture JSON contains the entire
command, environment, source/binary identity, elapsed time, dimensions, exit
status and PNG/log hashes. These are matching launch conditions, not an exact
same-simulation-tick pixel comparison or a performance benchmark.

Observed results:

- Day ground horizon moves from y=83 to y=194. This is confirmed by the largest
  blue-channel drop across the terrain/sky boundary at x=20..199, as well as
  inspection of the originals. The forward scene above the panel gains room.
- The approach's diffuse horizon moves from approximately y=5 to y=125 and
  the distant runway from approximately y=35 to y=150. It is now below the
  cockpit hint instead of pressed against the top edge.
- PFD and flight/control-state screens remain wholly visible. Approach images
  show EAS 69 kt, ellipsoid altitude 585 ft, GS 71 kt, throttle 26%, flaps 100%
  and trim +14%. V/S differs slightly around -498 ft/min because live capture
  does not lock the two launches to the same simulation tick.
- Both neutral grips are recognizable. No new visible intersection with the
  panel/PFD, throttle or flap paddle was found. The left grip's lowest portion
  overlaps the unchanged attribution strip; this limitation remains visible.
- Night retains readable PFD/stack and the relocated runway lights. Physical
  controls remain dark. The largest night blue-channel drop identifies a bright
  runway-light edge, so it is not used as a numerical horizon measurement.

All six logs contain the capture-complete marker and no ERROR/panic/asset-load
failure. Software-adapter, absent-audio-device and terrain precision warnings
remain; these are not warning-free or hardware-qualified runs.

## Regression validation

Completed local results (Rust 1.93.0, Linux):

- All 13 crates' default-feature all-targets tests: **2,723 passed, 0 failed,
  3 ignored** (1,363 pure-side and 1,360 render/app/input/UI/audio-side).
- The baseline's pure run also enabled `flightsim-content/downloads`. Its 24
  library tests were explicitly run and passed, bringing the comparable total
  to **2,747 passed**. Exact test-name multiset comparison against the retained
  alpha24 logs finds all 2,743 baseline tests plus only the four new tests below;
  none is missing. Doctests are separate: **6 passed**, no failure.
- Workspace/all-targets clippy and downloads-feature clippy with `-D warnings`,
  workspace rustdoc with `-D warnings`, fmt and architecture checks passed.
- Nine Python packaging/schema/reference/asset-validation commands passed.
- Full Python source-tools discovery on a clean source checkpoint ran 787
  tests: **708 passed, 3 failures, 75 errors, 1 Windows-only skip**, exit 1.
  All 78 non-passing cases reject the old cockpit source pin. This suite is
  **failed**, not source-admitted. An earlier uncommitted run additionally
  failed the committed-archive equality test; the clean rerun resolved that
  one failure without changing a test or gate. Both logs are retained.

The three pre-existing Rust ignores need optional regional scenery fixtures,
external Haneda terrain, or a dedicated planning-latency measurement window.
No ignore was added. Optional application `region-downloads` and analytical
feature matrices, release-profile benchmark compilation, Windows and hosted
CI were not run here; the results above are not a full CI/release qualification.

Validation results are recorded in the accompanying evidence logs. The added
tests use the production perspective and Swift profile eye, retain the existing
all-layout center/Home/picking tests, and add:

- Level and six-degree nose-down horizon bounds, including a 4:3 viewport and
  high-DPI viewport. This is a view fixture, not a flight-dynamics guarantee.
- Every PFD/flight/control screen vertex and every neutral grip mesh vertex
  inside 16:9 viewports, with display clearance above the attribution region.
- Explicit unchanged angles for the other layouts, and consistent translation
  of the entire Sport stick assemblies and their pivots/hit surfaces.
- Every moving stick mesh vertex at 25 pitch/roll combinations, including all
  extrema, remains at least 25 mm on the pilot side of the PFD front plane. Existing control
  rays and extreme-deflection re-grabbing tests remain intact.

This does not qualify native mouse/window interaction, all viewport aspect
ratios, physical GPUs, HOTAS, speakers, Windows or a release archive. The
neutral PNGs do not visually prove every animated control pose.

## Historical pre-admission result

The current admission test rejects the changed source hashes. No old admission
failure is counted as success and no historical pin was overwritten. A later
bounded migration must retain the current historical evidence and account for:

1. `crates/flightsim-render/src/cockpit.rs`
2. `crates/flightsim-render/src/cockpit/variants.rs`
3. `crates/flightsim-app/src/cockpit_runtime.rs` (test-only change)

The current replay/source contract, migration validators and corresponding
analytical/capture contract bindings must be advanced through their normal
reviewed successor mechanism; documentation/QA inputs must be included where
required. Current physical/replay source and asset pins stay unchanged.
Exact final-source CI, Windows/extracted two-aircraft captures, archive/notice
checks and publication approval remain separate subsequent gates.

## Source-admission successor

The proposal was safely rebased onto published alpha.24 source
`4f385e121addc036c2103d634e2bb46e6392172b` without changing its three runtime files.
The bounded successor preserves all previous contracts and runtime witnesses;
see [the source-admission guide](../release/full-two-aircraft-source-admission.md#swift-sport-forward-visibility-source-amendment).
The original 78 Python source-pin rejections above remain the result of that
pre-admission run, not a successful or waived check. Fresh successor validation
must be recorded separately. The Linux image comparison does not qualify native
Windows behavior or authorize publication.

Successor implementation checks: the eight new bounded-migration tests passed in
86.784 seconds, including committed-byte, hidden-checkout, exported-evidence and
joint runtime/descriptor self-reseal rejection. Twenty focused historical and
current-boundary tests passed in 59.013 seconds. These fixture-based checks are
separate from the original failed proposal run; the complete clean-commit source
suite and CI remain pending at this checkpoint. All six new historical witnesses
were compared byte-for-byte with published `4f385e1` Git blobs, and all three
runtime files still match the pre-rebase `ad1afa7` proposal exactly.
