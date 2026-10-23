# Alpha.26 source/notice amendment — not native evidence

Reviewed 2026-10-22. This is a bounded source-content comparison. It neither
publishes alpha.26 nor relabels an old Windows execution as a new one.

## Inputs and method

The candidate base is merged main
`e2e23ce1e954fd34ea6dd90a102a17ca0a7d3f4b`, tree
`1ea5182a0ca7ea9883ea6a5b18ba4db9ad032cda`, with a separately byte-bound
alpha.25 → alpha.26 version amendment. The base is **not a published HUD
release**. Five Git-exact witnesses and the new migration bind that provenance.

Rust 1.93.0 was installed from the official distribution in an isolated Linux
workspace. Before changing versions, fresh `cargo metadata --locked
--format-version 1 --filter-platform x86_64-pc-windows-msvc` and `cargo tree
--locked --target x86_64-pc-windows-msvc -p flightsim-app --edges normal,build
--prefix none --format '{p} features=[{f}]'` were retained. The same commands
were repeated offline after the version edit in the **same checkout**, followed
by the unchanged `collect-dependency-notices.py` on each metadata capture.
No native executable was produced or observed by this comparison.

Bindings (SHA-256):

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| Compiler identity | 196 | `83e4eefd5e010a92d9f63328bf8219e23fe5e4cf5e5d17ce53d0263cfa4218a6` |
| Baseline metadata | 2444318 | `6e2e61ec386329fcc2a19ee022b18361e4e3336c83b264980df94a4a8d74e834` |
| Alpha.26 metadata | 2444318 | `9e823157fc1beb54dd9214538063303a7a30f0a4c3174547cdda27603c9df8c7` |
| Baseline full tree | 79718 | `7644c2802697f59383832cd0287334b3839cf3db1c59969541f69547dd97f35f` |
| Alpha.26 full tree | 79718 | `48eb1199a0f1b9d5d3c48f01cd76e5806d607d6c263dfa496abf2294c0e4edb1` |
| Baseline raw inventory | 407610 | `8eb409ca1ca95cf68f28f0a9300de50438ba3180cbd09ad2152d8925e99e3a88` |
| Alpha.26 raw inventory | 407610 | `ef7f6590c9682450858436b19b3b8f7ff2a919e40f436f3407c9b7888e512388` |
| Cargo.toml | 5018 | `10d186ef64ce442c6815319ce4258129a57d6a2025942e969af6c658b2cb7929` |
| Cargo.lock | 154591 | `a4be7f2a769d9c0d5b33369334fe8dafb5c356f052208d4cb739700616c9fcda` |

Metadata was compared as complete JSON after only the exact project version
substitution; graph text was compared byte-for-byte after that substitution.
The baseline fresh inventory was also compared against the retained alpha.25
inventory: only the newly observed metadata digest differs. The successor
inventory then differs only by the project version identities, their notice
paths and the observed metadata/Cargo-lock digest. No feature, checksum,
external package, resolution-order or notice-order difference was accepted.

## Substantive source/notice results

- 359 conservative package records remain the same after eleven runtime-closure
  project identities change. The manifest changes one version field; lockfile
  changes exactly thirteen local workspace package versions.
- All 735 original notice files retain exact bytes. Eleven project licence
  directories (22 MIT/Apache file paths) receive only the version-name change.
  The raw collector assembly has 737 files, including its inventory and index.
- All 557 supplemental files are preserved byte-for-byte and all evidence paths
  and hashes in all 363 reviewed resolution records resolve to the exact files.
- All 510 pinned source-header records were rechecked against freshly collected
  package sources: both whole-file and exact excerpt hashes match. No new source
  or header was substituted under an old assertion.
- Since the published alpha.25 source, only four existing `flightsim-ui` source
  files changed: `lib.rs`, `pause.rs`, `traffic.rs`, and regression-only
  `top_layout_tests.rs`. Their authored layout, state eligibility and text
  presentation logic introduces no external source or asset. Aircraft, vendor,
  dependency, cloud and asset trees are unchanged. The new preparation itself
  changes no runtime source.
- Existing package licence routes, vendor modification/provenance obligations,
  original licence texts, supplemental notices and component-terms policy are
  preserved. No new agreement or recipient assent is inferred.

The collector's two original findings (`constgebra@0.1.4` and
`hexf-parse@0.2.1`) and `review_status: not_reviewed` remain **unmodified** in the
raw inventory. Their existing exact reviewed resolutions are separate evidence;
the collector was not changed to hide them or treat a cached verdict as a new
native review. The current dependency review is source-amended with the actual
new inventory hash. Its old source amendment is appended intact to history.

## Limits and remaining gates

The old `source_sha`, `source_tree`, native/build/runtime/supplier facts,
`component_conditions`, environment observations and supplemental assembly
binding remain original historical records, not facts about a new alpha.26
binary. `appearance_accepted`, `runtime_accepted`, `distribution_qualified`
and `release_authorized` remain false. Historical source amendments are retained
without retelling their observations as current.

This source/notice amendment initially left the alpha.25 publication receipt and
native applicability untouched. A subsequent separate alpha.26 permission-only
receipt records publication authority; native applicability remains historical
and insufficient for this changed-source successor. Final-source
Windows capture and all eleven native-content comparisons, actual publication
authority, same-build archive/extraction and both aircraft smokes are still
required. Linux source metadata, passing tests and an MSVC compile do not satisfy
those obligations. The independent cloud-rendering candidate is not included.
