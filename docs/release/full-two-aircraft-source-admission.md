# Full two-aircraft alpha.25 version source admission, version 1

The current source-only identity is `full-two-aircraft-alpha25-version-source-v1`.
It admits only the alpha.24 to alpha.25 workspace/local-package version change
over published Swift visibility source `754bad886cbac8f564c6c46ebdb265c54bda275c`.
The current contracts bind **987 replay files, 63 analytical inputs and four
capture inputs**. All prior validators, exact historical witnesses, 499 current
crate members, 497 original runtime identities and 102 independent replay anchors
remain enforced. No source-admission pass qualifies native execution or release.
See the [current alpha.25 boundary](#alpha25-version-only-source-amendment) below.

The intervening sections record earlier admission stages. Their identities,
counts and observations describe those historical stages, not the current
alpha.25 contract or new Windows evidence.

## Historical alpha.24 overview and inherited boundaries

At this stage the source-only identity was `full-two-aircraft-alpha24-version-source-v1`.
That version-only migration extends the published aircraft-specific
cockpit source and every preserved alpha.23 version, cockpit, alpha.22 version,
terrain-stitch, terrain-centroid and component-terms migration. None supplies
native or publication evidence for alpha.24. Each previous admission identity
and complete validator is retained below as explicit history.
The `base_reviewed_source` and `base_reviewed_runtime_tree` fields identify the
previous runtime composition `960c3126e6a4bc22b8d4acc6e6737f8f2b473bef`, tree
`b3bbd57bc3819b1b1eda35ce4f8b476c52d1b24e`, as historical base provenance only.
They do not identify the changed component-terms, terrain-centroid, terrain-stitch,
state-coupled cockpit or aircraft-specific cockpit runtime. The separately pinned
`scripts/component-terms-source-migration.json` binds the exact startup change,
two new runtime inputs, three component documents and two unchanged embedded
project-license texts. Every execution still requires its actual final clean commit, complete tree and canonical input bytes.
Prior `55094fa` builds, graphs and native observations remain reference evidence;
none are qualified evidence for the changed runtime.

That stage's replay source contract named 974 exact files. Its literal path sets
include the previous 404-file boundary, every one of the 55 local core-pipeline
files, complete original-highwing inputs and provenance, and the frozen 497
runtime identities. The frozen map itself is unchanged. Its earlier changed
app `main.rs` remains retained byte-for-byte at
`scripts/history/4d40f9a-flightsim-app-main.rs`. Previous terrain material bytes
are additionally retained at `scripts/history/42a7dde-terrain_detail.rs`.
`scripts/terrain-centroid-source-migration.json` binds the exact new terrain
specialization, forward shader IO, vendor descriptions/current provenance and
single render-test addition. The subsequent stitch migration preserves old
`seams.rs` and `terrain_seam_geometry.rs` bytes at
`scripts/history/5eaaff3-seams.rs` and
`scripts/history/5eaaff3-terrain_seam_geometry.rs`. Its exact two-file replacement
also retains the complete previous 930-member replay contract at
`scripts/history/5eaaff3-replay-candidate-contract.json`; every other prior pin
must remain unchanged. The later cockpit migration additionally preserves four replaced runtime files at
separate published-base witness paths, as described below. The aircraft-specific
layer additionally preserves six pre-variant source files and all three
alpha.23 contracts under `scripts/history/alpha23-cockpit-variant-base-*`.
Original-map comparisons retain oldest-witness precedence: `main.rs` still uses
the component-terms witness, and `aircraft_scene.rs` and `cockpit.rs` still use
their pre-cockpit witnesses. The original `aircraft_picker_tests.rs` identity now
uses its alpha.23 witness. No old digest is overwritten or relabeled.

The stitch migration base `5eaaff379f19cc986fa5600619f1491213e9da0d`, tree
`a469ee76cd0d7aabf3dd2c07114d44c0bbdf5d37`, is an unpublished local centroid
checkpoint, derived from public `42a7ddeae36f3022c2c77e54d5dce33f71b11bca`, tree
`625c39f9b182b16a0dada2dc4131434d178a0831`. No verifier must fetch or possess
the unpublished object: checked-in historical witnesses and exact manifests
provide the complete verification inputs. Actual run identity remains its own
clean final commit and tree regardless of publication ancestry.
Before this migration, the frozen hashes were independently compared to both base `d918943a70d01644b5a6bebb8a903a5bbc89139f` and the canonical runtime Git
blobs. All 102 independent replay anchors retain their previous hashes. No
unrelated runtime/profile byte is refreshed to satisfy a test. Clean Git state,
regular files, canonical blob hashes, checkout hashes, case-sensitive exact path sets,
and rejection of ignored local vendor/witness inputs remain required. The 492
preserved crate paths, two literal component-terms inputs, one terrain test and
two literal state-coupled cockpit helpers and two aircraft-layout modules form a
closed 499-member current set. The two newest modules are excluded from the
original 492-path preserved set. Committed, ignored or untracked Cargo-discovered
build scripts, binaries, examples and benchmarks cannot expand either boundary. The three component
documents also form an exact closed directory boundary. Root-case aliases and
reparse/symlink paths remain rejected.

`scripts/history/d918943-*.json` stores byte-exact prior replay, analytical and
capture source contracts. Their historical identities, reviewed sources and
hashes are not relabeled. The current source contracts have new source admission
identities. Analytical Swift runtime features and the ordinary default-feature
control retain their original semantics; compiled source selection is separately
and explicitly `bevy-0.18.1-tony-filmic-source-v1`. The current analytical source
contract binds all relevant admission/audit tools, tests, workflow and source
manifest. Capture has a separate source contract and exact inherited hashes.

Current capture and audit require a checksum-verified original Bevy crate held
outside shipped source. They retain its hash/size privately and in bounded
metadata. The original AgX bytes are a negative reference, never distributed.
The selected core-pipeline source must match all 55 declared local files. Ordinary compilation must
contain exact Tony and Filmic payloads and omit AgX; analytical regression must
omit all three payloads. Both branches use the same verified negative reference.
Historical three-LUT fixtures explicitly select the upstream recipe. Historical
export schemas without a source recipe remain three-LUT records; they cannot
be rebound to current source or counted as a new two-LUT run.

Current asset tests select original Light model identity and Tony/Filmic records.
Historical Meshy/AgX records retain unresolved decisions and content-hash denial.
Current source archives select `original-highwing-v1`; historical default archive
fixtures retain their previous policy. The preparation map
`docs/release/full-two-aircraft-source-inputs.json` remains historical preparation
data, with no source-admission authority.

See [the bounded component-terms migration](../qa/component-terms-source-bindings-2026-10-09.md)
for its historical preservation boundary, and [the terrain-centroid migration](../qa/terrain-centroid-source-bindings-2026-10-09.md)
for its preserved shading-only source boundary. The [three-source stitch
migration](../qa/terrain-stitch-source-bindings-2026-10-09.md) binds the current
geometry change, its historical witnesses and source mutation-test boundary.

## Alpha.22 version-only boundary

**Historical stage; superseded by the current alpha.25 outer boundary.**

`scripts/alpha22-version-source-migration.json` permits exactly the workspace
version in `Cargo.toml` and the versions of the thirteen named local flightsim
packages in `Cargo.lock` to move from `0.6.0-alpha.21` to `0.6.0-alpha.22`.
The exact historical Cargo witnesses are `scripts/history/0bc4a49-Cargo.toml`
and `scripts/history/0bc4a49-Cargo.lock`. TOML checks constrain the changed
fields and local package membership; an exact byte-substitution check additionally
forbids comment, whitespace, ordering or other incidental changes. Each file is
bounded to one MiB. Dependency versions, sources, checksums, features, profiles,
workspace membership and lockfile metadata remain unchanged.

The base is local checkpoint `0bc4a4961c677a5173350630bf2641a2c1b40b94`, tree
`7ac0cedd0963ac4133fa8c5251f57f26037324d7`. The same candidate tree is published
as `3574bf175c66851df51ae89903e04a13f4a172e6`; the local checkpoint is not
relabeled as a published commit. Checked-in witnesses suffice without either Git
object. The previous three source contracts remain byte-exact at
`scripts/history/0bc4a49-{replay-candidate,analytical-swift-source,analytical-swift-capture}-contract.json`.
All 934 previous replay pins survive, with only the two Cargo entries relocated
to their historical paths. The original 497 runtime identities, all three prior
migration manifests, 102 independent replay anchors, CRT terms/startup UI and
runtime source bytes remain unchanged.

The alpha.22 analytical contract bound 53 exact inputs, including the new version
mutation tests. Its separate, bounded dependency-notice collector change makes
relative POSIX path ordering host-independent and fixes generated README/inventory
newlines to LF; see [the collector ordering evidence](../qa/dependency-notice-ordering-2026-10-10.md).
That tooling change does not widen the version migration or alter original
dependency notice bytes. The capture contract retains four inputs and explicit inherited
contract hashes. Historical alpha.21 reports, inventory review and authorization
never become alpha.22 approvals. Fresh inventory-bound review and authorization,
exact-final-source CI, Windows build and extracted-archive smoke remain separate.

## State-coupled cockpit boundary

**Historical stage; superseded by the current alpha.25 outer boundary.**

`scripts/cockpit-source-migration.json` binds exactly four replacements:
`crates/flightsim-app/src/main.rs`, `crates/flightsim-app/src/aircraft_scene.rs`,
`crates/flightsim-render/src/cockpit.rs` and
`crates/flightsim-ui/src/instruments.rs`. The two exact additions are
`crates/flightsim-app/src/cockpit_runtime.rs` and
`crates/flightsim-render/src/cockpit/texture.rs`; no filesystem discovery can
admit another runtime member.

The published base is `be5873840dc86eb551971bad6e7290840eaf9cd2`, tree
`49479664f838700cf52ed7621a727db7732752e2`. Seven byte-exact witnesses under
`scripts/history/be587384-*` retain its four replaced source files and three
source contracts. The existing component-terms main.rs witness is preserved
separately. The complete historical alpha.22 validator still checks its own
940-pin contract; the outer cockpit layer preserves every prior pin, relocating
only the declared four replacements, and adds exactly ten source members.
All prior migration descriptors, 497 original runtime identities and 102
independent replay anchors remain unchanged. No historical commit fetch is
required to validate the checked-in witnesses.

The historical cockpit analytical contract bound 54 exact inputs, including the
cockpit mutation tests; its capture retained four inputs and exact inherited hashes. Dedicated
negative tests reject omissions, extra or aliased members, changed digests,
canonical-versus-checkout drift and source/native/publication scope escalation.
The existing native, licensing, source-archive and stager gates remain separate.
The [cockpit guide](../3d-cockpit.md) lists real instrument values, controls and
unimplemented aircraft systems. Its [development QA](../qa/functional-cockpit-2026-10-10.md)
distinguishes automated/source checks and software captures from native-window,
physical hardware or pilot usability acceptance.

## Historical alpha.23 version-only boundary

`scripts/alpha23-version-source-migration.json` permits only the workspace version
in `Cargo.toml` and the versions of the thirteen literal local flightsim packages
in `Cargo.lock` to move from `0.6.0-alpha.22` to `0.6.0-alpha.23`. The published
cockpit base is `81bb3ea9c19c0016521a610dbeafb5029caa8713`, tree
`dde21933b02c962108916c6a5efeef20d8f32a6f`. It is a published commit, not a
relabeled local checkpoint. Every execution still binds its own final clean
commit, tree and canonical source bytes.

Five byte-exact witnesses under `scripts/history/81bb3ea-*` preserve its three
source contracts, `Cargo.toml` and `Cargo.lock`. The complete 950-member cockpit
validator and path boundary were frozen as a historical layer. That version-only
layer added exactly these five witnesses and its migration descriptor, preserving
every previous pin and relocating only the two Cargo identities. Its historical
replay contract therefore has 956 members. No historical Git object or fetch is needed.
The alpha.22 historical validator still reconstructs alpha.22 from its original
alpha.21 witnesses; neither its old descriptor nor any old witness is rewritten.

TOML validation checks exactly one workspace version, all thirteen named local
lock package versions and unchanged complete parsed documents after reversing
those fields. Exact byte substitution separately rejects changed comments,
whitespace, package ordering or other incidental bytes; each input remains
bounded to one MiB. Runtime files, dependencies, features, profiles, workspace
membership, checksums, the then-current 497-member crate boundary and all 102
independent replay anchors remained unchanged. All five previous migration
descriptors, the 497 original runtime identities, licensing terms and startup UI
remain byte-exact.

The historical alpha.23 analytical source contract bound 55 exact inputs, including
the alpha.23 version mutation tests; its capture retained four inputs and exact
inherited hashes. Both received explicit source-admission identities. Prior alpha.22
source, CI, inventory, Windows and authorization evidence stays historical.
Fresh exact-final-source CI, target inventory review, Windows build and
extracted-archive smoke, source-hosting verification and inventory-bound
publication authorization remain separate gates.

## Historical aircraft-specific cockpit boundary

`scripts/cockpit-variant-source-migration.json` binds the true released alpha.23
parent `130de6f2872cab4932a4b2e61c6828a7dccc883b`, tree
`26b935ac8c60cf0b87a8367f93a45ebc6a4fc2a8`. Its base kind is `published-commit`
and its status is `released-alpha23-parent`. This identifies actual published
provenance; it does not grant this successor native acceptance, rights review or
release authority. The descriptor and historical source contracts remain source-only,
with `release_authorized=false` wherever that field exists. The released parent's
Cargo, applicability record and authorization receipt remained unchanged in that
source-only change; the release gate rejected the stale receipt for the successor.

Exactly six current Rust pins are replaced:

- `crates/flightsim-app/src/aircraft_picker_tests.rs`
- `crates/flightsim-app/src/aircraft_scene.rs`
- `crates/flightsim-app/src/cockpit_runtime.rs`
- `crates/flightsim-app/src/main.rs`
- `crates/flightsim-render/src/cockpit.rs`
- `crates/flightsim-render/src/cockpit/texture.rs`

Exactly two runtime modules are added: `crates/flightsim-app/src/cockpit_layout.rs`
and `crates/flightsim-render/src/cockpit/variants.rs`. Nine immutable witnesses
under `scripts/history/alpha23-cockpit-variant-base-*` preserve the released
parent's six replaced source files and three complete replay/analytical/capture
contracts. Their exact bytes were rechecked against the final released parent;
stable filenames do not relabel the provisional parent as a released one.

The alpha.23 validator and its 956-path snapshot remain a complete historical
layer. The aircraft-specific layer preserves every prior pin through only the six declared
relocations, then adds precisely twelve members: nine witnesses, one descriptor
and two modules. Thus its historical replay boundary is 968, and the current crate
closure is 499. The original runtime map retains all 497 identities and its
original 492 crate paths. All six earlier migration descriptors, all older
witnesses, 102 independent replay anchors, 55 core-pipeline files and the original
404-path historical boundary remain unchanged. Verification requires no historical
Git object or fetch; canonical and checkout bytes still bind each actual run.

The historical aircraft-specific analytical contract binds 56 exact inputs, including
the aircraft-cockpit mutation suite. This existing admission document remains
one of those inputs; updating it does not add a contract member. The capture
contract retains its four literal members and refreshed inherited hashes. The
new identities are `analytical-swift-cockpit-variant-source-admission-v1` and
`analytical-swift-cockpit-variant-capture-source-admission-v1`. Mutation tests retain
exact-delta, omission/extra/alias, canonical/checkout, concealed-dirty, exported
hash, closure, symlink/reparse and authority-escalation checks. Earlier alpha.23
and provisional-draft test results remain tied to their original commits, never
relabelled as final-successor results.

This presentation change does not change FDM, profile/replay bytes, dependencies,
features, distribution allowlists, terms or licenses. The ordinary bundle remains
Light Single plus Swift Sport; Meadow and Kestrel remain optional/development-source
choices, and commercial staging remains Swift-only. Fresh exact-final-source CI,
native build/capture, inventory/applicability and rights/terms review, same-archive
smoke, source/archive verification and inventory-bound publication authorization
remain independent gates.

## Alpha.24 version-only outer boundary

**Historical stage; superseded by the current alpha.25 outer boundary.**

`scripts/alpha24-version-source-migration.json` permits only the workspace version
in `Cargo.toml` and the thirteen literal local package versions in `Cargo.lock`
to advance from `0.6.0-alpha.23` to `0.6.0-alpha.24`. Its published base is
`fbb53429bcae8a94078ea96f528b0b2ad216fdfe`, tree
`f7a2c9e7081c16d7efac552d7b8e7de0de54a192`. Published source provenance is not
native or publication acceptance. Actual runs still bind their own clean final
commit, tree, canonical blobs and checkout bytes.

Five byte-exact witnesses under `scripts/history/fbb5342-*` preserve both Cargo
files and the three source contracts. The complete aircraft-specific validator
and its 968-path boundary are frozen as a historical layer. The outer layer adds
only those five witnesses and one migration descriptor, reaching 974 replay pins.
Every prior pin remains exact; only the two Cargo identities are relocated.
The literal 499-member current crate boundary, 497 original runtime identities,
all seven earlier migration descriptors, 102 independent replay anchors and
component terms/startup UI remain unchanged. No old Git object or fetch is needed.

TOML checks require exactly one workspace version and all thirteen local lock
package versions. Complete parsed documents must otherwise remain equal. Exact
byte substitution separately rejects incidental comments, whitespace, ordering,
dependency or feature changes, with the existing one-MiB per-file bounds.
The analytical contract binds 57 exact inputs, adding the alpha.24 version
mutation suite. The capture contract retains four literal members and exact
inherited hashes. Their identities are
`analytical-swift-alpha24-version-source-admission-v1` and
`analytical-swift-alpha24-version-capture-source-admission-v1`.

Earlier alpha.23 captures, native packets, applicability reviews and publication
receipts retain their original source identities. This migration cannot reassign
them to alpha.24. Fresh genuine changed-source Windows evidence must support a
separate exact content-applicability review. Rebound final-source authorization,
final exact-source CI, a fresh same-build Windows run, unchanged extracted
Light Single/Swift smoke and remote source/tag/archive/asset verification remain
independent publication gates.

A source pass establishes neither native execution, appearance, whole-target
rights, source-hosting verification nor publication authority. The final full
runtime recipe remains release MSVC/Rust 1.93.0 with default features and no
additional features, Light Single default plus Swift, and ordinary Tony. Actual
full recipe qualification and inventory-bound authorization remain separate.

## CI source-tool budget amendment

**Historical stage; superseded by the current alpha.25 outer boundary.**

[PR #52 CI run 39201495425, job 117895225581](https://github.com/Xenoah/flightsim-rust/actions/runs/39201495425/job/117895225581)
was cancelled at `2026-10-19T05:20:48Z` by the 30-minute job ceiling, with no
preceding assertion failure and the suite still incomplete.
The same-source local suite completed 781 tests in 1952.594 seconds with one
Windows-only skip.

The alpha.24 runtime/version admission above is unchanged. The separate
`scripts/ci-timeout-source-migration.json` tooling layer uses published source
`c84b8aa97d38250ddb1c5495e2d65e3917be8b4c`, tree
`c9d792a5f0fc1641a6a050ce41a56f2a5b8afb2b`, as provenance. Two immutable
`scripts/history/c84b8aa-*` witnesses preserve its complete CI workflow and
57-input analytical source contract.

The only workflow change is `world_source_tools.timeout-minutes: 30` to `45`.
Complete byte comparison against the fixed historical workflow rejects every
other job, command, dependency, permission, test selection, whitespace or ordering
change. All tests and required gates continue to run. This is a CI job ceiling;
it changes no native capture, process, smoke or publication deadline.

The analytical source boundary is now 61 inputs: the previous 57 plus the two
witnesses, fixed closed migration descriptor and exact-delta mutation tests.
Only the workflow, auditor, this explanation and existing source-count/identity
assertions are rebound. The current identities are
`analytical-swift-alpha24-ci-timeout-source-admission-v1` and
`analytical-swift-alpha24-ci-timeout-capture-source-admission-v1`. The capture
boundary retains four inputs and exact inherited hashes. The 974-pin replay
contract, alpha.24 version-only validator, all historical migrations, runtime,
rights review and publication gates remain unchanged. Neither successful CI nor
this tooling amendment supplies fresh Windows evidence or release authority.

## Swift Sport forward-visibility source amendment

**Historical stage; superseded by the current alpha.25 outer boundary.**

The successor `scripts/swift-forward-visibility-source-migration.json` is based on
published alpha.24 source `4f385e121addc036c2103d634e2bb46e6392172b`, tree
`47aed13ca164afcadf3c1201c411fecd00e77cd4`. It admits only the reviewed complete
bytes of `crates/flightsim-render/src/cockpit.rs`,
`crates/flightsim-render/src/cockpit/variants.rs` and
`crates/flightsim-app/src/cockpit_runtime.rs`. Swift's initial look pitch changes
from 24 to 15 degrees; its stick, animation pivot and interaction bounds move
0.10 m forward together. The app-file changes are regression tests. No new runtime
file, package version, dependency, physics, replay, aircraft asset or workflow
change is admitted.

Six byte-exact `scripts/history/4f385e1-*` witnesses retain all three previous
contracts and all three replaced runtime files. The complete alpha.24 validator
remains a frozen 974-pin historical layer. The outer contract adds those witnesses
and the fixed descriptor, reaching 981 pins; its identity is
`full-two-aircraft-swift-forward-visibility-source-v1`. Every previous pin is
preserved, relocating only the three replaced runtime identities. The literal
499-member crate boundary, 497 original runtime identities, all earlier migration
descriptors and 102 independent replay anchors are unchanged. Fixed descriptor
and replacement hashes reject jointly resealed runtime/manifest/contract attacks.

The analytical successor preserves the exact published 61-input CI-only contract
and runs its unchanged bounded 30-to-45-minute validator before the new layer.
Only the source auditors, replay contract, this guide and affected test assertions
are rebound. One new mutation-test input brings its boundary to 62; capture keeps
four inputs and exact inherited hashes. Current identities are
`analytical-swift-forward-visibility-source-admission-v1` and
`analytical-swift-forward-visibility-capture-source-admission-v1`.

This source-only amendment cannot reuse alpha.24 native captures, applicability
or publication receipts as evidence for the changed source. The genuine Linux
software-rendered visual comparison is recorded in
[`docs/qa/swift-forward-view-2026-10-19.md`](../qa/swift-forward-view-2026-10-19.md).
Its original 78 source-pin rejections remain a historical failed proposal check;
the successor must pass its own fresh committed-source validation. Native,
whole-target rights, exact-inventory authorization and publication gates remain
separate and unqualified by this migration.

## Alpha.25 version-only source amendment

**Historical stage; superseded by the current chase-HUD outer boundary.**

`scripts/alpha25-version-source-migration.json` is a closed, version-only
successor to published Swift forward-visibility source
`754bad886cbac8f564c6c46ebdb265c54bda275c`, tree
`ae0558fe04c5fe700b47a5116b9977561f57b1c3`. Its sole runtime-input delta is
`0.6.0-alpha.24` to `0.6.0-alpha.25`: one workspace version in `Cargo.toml` and
thirteen local-package versions in `Cargo.lock`. Complete parsed TOML documents
must otherwise remain identical, and exact whole-file substitution rejects
extra comments, whitespace, reordered packages, dependencies, features or paths.
The existing one-MiB input bounds remain enforced.

Five exact `scripts/history/754bad8-*` witnesses preserve both Cargo inputs and
all three source contracts. The complete 981-pin Swift visibility validator
remains a historical layer, including its three fixed presentation-file hashes
and all previous version, cockpit and CI-only proofs. Only those five witnesses
and the descriptor are added, reaching 987 replay pins. The 499-member crate
boundary, 497 original runtime identities and 102 independent replay anchors
remain exact. No new runtime implementation, asset, physics, replay, dependency
or workflow change is admitted by this version migration.

The analytical successor first validates the frozen 62-input Swift contract,
which still validates the complete published CI-only layer. Only the Cargo pair,
source auditors, replay contract, this guide and affected test assertions are
rebound. One new alpha.25 adversarial suite brings its boundary to 63 inputs.
Capture keeps four exact inputs and inherited contract hashes. Current identities
are `full-two-aircraft-alpha25-version-source-v1`,
`analytical-swift-alpha25-version-source-admission-v1` and
`analytical-swift-alpha25-version-capture-source-admission-v1`.

No alpha.24 Windows observation or publication receipt becomes evidence for
alpha.25 through a version substitution. Fresh ordinary target-filtered notice
collection, substantive source/notice review, genuine changed-source Windows
capture, complete native-content applicability review and final inventory-bound
authorization remain separate. The final source still requires its own CI,
fresh same-build release MSVC capture, exact archive/extraction checks and the
unchanged Light Single cockpit plus Swift Sport chase smoke. A Swift cockpit
visual comparison is separately identified; the chase smoke does not establish
that view's appearance. The approved component terms and all publication gates
remain unchanged. See [alpha.25 preparation](../qa/alpha25-release-preparation-2026-10-19.md).


## Chase traffic and flight-guide source amendment

The source-only `scripts/chase-hud-source-migration.json` successor is based on
published alpha.25 commit `5082b772c6f2d220377c1031aaa91a0e96c5aec1`, tree
`3ae086914700566031427f45be0f4d17acc619c1`. It admits exactly four complete files
under `crates/flightsim-ui/src`: `lib.rs`, `pause.rs`, `top_layout_tests.rs` and
`traffic.rs`. The change shares measured space between ordinary live CHASE
traffic and flight guidance, with the complete traffic reference retained in the
paused view. No cloud, physics, replay, dependency, aircraft asset, package
version, workflow or release gate is admitted by this amendment.

Seven byte-exact `scripts/history/5082b772-*` witnesses preserve the three
previous contracts and four previous UI files. The complete 987-pin alpha.25
validator remains a frozen historical layer. Adding only the witnesses and the
fixed descriptor reaches 995 replay pins. Every previous pin is preserved,
relocating only the four replaced file identities. The 499-member crate boundary,
497 original runtime identities and 102 independent replay anchors remain exact.
Fixed descriptor and replacement hashes reject jointly resealed UI, migration
and contract attacks; source checks compare canonical Git and checkout bytes.

The analytical successor first validates the frozen 63-input alpha.25 contract
and its complete earlier migration chain. Only the source auditors, replay
contract, this guide and affected historical/current test assertions are rebound.
One new mutation-test input brings the analytical boundary to 64. Capture retains
four inputs and exact inherited contract hashes. Current identities are
`full-two-aircraft-chase-hud-source-v1`,
`analytical-swift-chase-hud-source-admission-v1` and
`analytical-swift-chase-hud-capture-source-admission-v1`.

The earlier unvalidated preservation branch and unavailable local validation
receipts are not acceptance evidence for this reconstruction. Its final source
requires fresh compilation, layout/image checks and CI. Existing alpha.25
Windows, applicability and publication receipts remain evidence only for their
original source. Native, whole-target rights, exact-inventory authorization and
publication remain independent gates; no source migration creates approval.

## Alpha.26 HUD version preparation

The source-only `scripts/alpha26-version-source-migration.json` successor is
based on merged main `e2e23ce1e954fd34ea6dd90a102a17ca0a7d3f4b`, tree
`1ea5182a0ca7ea9883ea6a5b18ba4db9ad032cda`. That base has successful source CI
and separate MSVC build-only evidence; it is not a published HUD binary or a
native/runtime qualification. The migration therefore calls it
`merged-main-commit`, not `published-commit`.

Only `0.6.0-alpha.25` to `0.6.0-alpha.26` changes are admitted: one workspace
manifest field and thirteen local lockfile package versions. Every other Cargo
byte, dependency, feature, crate and asset remains unchanged. Five byte-exact
`e2e23ce-*` witnesses preserve both Cargo files and all three complete contracts.
Together with the migration descriptor they extend the frozen 995-pin HUD proof
to 1001 pins; all earlier validators and independent physics/replay anchors
remain mandatory. Exact semantic and byte checks reject unrelated manifest,
lock-order, dependency and jointly resealed descriptor changes.

The analytical wrapper preserves the complete frozen 64-input HUD proof, adds
one alpha.26 mutation-test input, and limits rebindings to its explicit source
auditors/contracts/guide/test assertions plus the Cargo pair. Its boundary is
65 inputs; capture still has four. The current identities are
`full-two-aircraft-alpha26-version-source-v1`,
`analytical-swift-alpha26-version-source-admission-v1` and
`analytical-swift-alpha26-version-capture-source-admission-v1`.

No cloud rendering change is part of this preparation. This source migration
does not rebind historical native applicability. A separately recorded alpha.26
publication-permission receipt does not establish native qualification.
Fresh final-source Windows capture, substantive native-content applicability,
exact-inventory publication authority, same-build archive/extraction and both
existing aircraft smokes remain required. The new source/notice comparison is
not native evidence and does not accept a new agreement or recipient assent.
See [alpha.26 preparation](../qa/alpha26-release-preparation-2026-10-22.md).

## Alpha.26 source-tool CI budget successor

PR #58 CI run [39944623925](https://github.com/Xenoah/flightsim-rust/actions/runs/39944623925)
exhausted the source-tool job's 45-minute budget before the complete suite could
finish. The retained log contains 751 successful test results and no assertion
failure; the cancelled run is not a passing full-suite result.

The source-only `scripts/ci60-source-migration.json` successor retains public
preparation commit `2eb36242cde4ccd3492b0079d4de226ee26db15e`, tree
`f56e97232728aed82b66edb82beb7417e946c929`, as exact Git-blob witnesses for the
complete 45-minute workflow and its 65-input analytical contract. This base is
a PR preparation commit, not a released or native-qualified binary.

Only `world_source_tools.timeout-minutes` changes from 45 to 60. The entire
workflow must equal that single literal replacement: all tests, commands,
dependency versions, runners, triggers, permissions and other job budgets remain
byte-exact. The older 30-to-45 descriptor and validator remain intact and consume
the frozen 45-minute witness. The new outer layer independently validates the
actual 60-minute workflow and rejects unrelated or jointly resealed changes.

The replay contract remains the exact 1001-pin alpha.26 runtime contract. The
analytical boundary grows from 65 to 69 only for the two witnesses, fixed
descriptor and dedicated mutation tests; capture retains four inputs. Active
analytical/capture identities are
`analytical-swift-alpha26-ci60-source-admission-v1` and
`analytical-swift-alpha26-ci60-capture-source-admission-v1`. All original
historical pin, canonical-checkout and commit/export rejection checks remain.

This budget change is not a test waiver, native observation, applicability
review or release approval. Publication permission is rebound to exact changed
source separately; genuine Windows capture, all eleven native-content sections,
same-build archive/extraction and both aircraft smokes remain mandatory. The
ordinary release workflow and its `windows-latest` runner are unchanged.

## Offline urban scenery source-only successor

The successor preserves published alpha.26 `fc2ca797` and all three complete
contracts as exact checked-in witnesses. Its 1,001 replay pins remain mandatory
through the unchanged alpha.26 validator. Nine replaced inputs keep their prior
bytes at explicit historical paths; eight reviewed additions, those witnesses,
the three contracts and a closed descriptor extend the boundary to 1,022 pins.
The live crate boundary grows from 499 to 503 only for the urban generator, its
tests, index and provenance. The original 497 runtime identities and 102 independent
replay/physics anchors are preserved. See the
[substantive bounded review](../qa/urban-source-admission-2026-10-24.md).

The analytical successor retains the complete 69-input CI60 proof, adds one
adversarial urban-source suite and permits only explicitly listed source-tool,
contract, guide and historical/current test rebindings. Capture retains four
inputs and its native commands are unchanged. New source identities describe
offline urban source admission only; `release_authorized` remains false.
Ordinary code checks, genuine Linux visual evidence and source admission do not
create Windows assent, native qualification, rights applicability, same-build
archive acceptance or exact-inventory publication authority. Existing release
receipts and all release/consent gates remain byte-exact and independently required.
