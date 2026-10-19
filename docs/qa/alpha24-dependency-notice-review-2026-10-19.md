# Alpha.24 source-only dependency and notice amendment

Date: 2026-10-19. Published runtime base: `fbb53429bcae8a94078ea96f528b0b2ad216fdfe`.
This review binds the local alpha.24 manifest/lockfile bytes separately. It is not a native-build,
runtime, recipient-assent, legal-agreement acceptance or publication record.

## Reviewed change

The existing [aircraft-specific cockpit source migration](../../scripts/cockpit-variant-source-migration.json)
preserves the released alpha.23 runtime witnesses and binds six replacement
files plus two added modules. All eight current files and all six retained
predecessors were rehashed against that migration. The changed runtime is
project-authored procedural geometry, bitmap lettering/display artwork and
presentation/input wiring. The [layout provenance](../aircraft-cockpit-layouts.md),
[source decision](../adr/0034-aircraft-specific-cockpit-layouts.md), actual source
and [dated development QA](aircraft-cockpits-2026-10-10.md) were inspected.
No reference photograph, copied third-party cockpit model/texture/font,
new dependency or altered component terms was found in this bounded delta.
The aircraft-profile/model admission and ordinary two-aircraft payload remain
separate existing boundaries; supporting an external layout does not add that
external aircraft to the distributable payload.

The additional alpha.24 change substitutes the project version in one workspace
manifest field and 13 local lockfile package entries. Only 11 project packages
belong to the ordinary application normal/build closure. The two offline tools
remain outside that closure. Both Cargo files match their published parent
byte-for-byte after this exact version substitution, with no dependency update.

## Fresh collection and comparison

Rust 1.93.0 on `x86_64-unknown-linux-gnu` ran the ordinary/default-feature
Windows-target metadata and normal/build tree commands. Metadata is a
cross-target source observation; no Windows executable was built or run here.
The existing unmodified collector wrote into a new empty output directory.
Its output was compared before replacing the source inventory or project
notice directories. The raw inventory continues to say `not_reviewed` and
retains its two original missing-primary-notice findings.

Reproduction uses these ordinary recipe commands, with separate fresh paths:

```sh
rustc +1.93.0 -vV
cargo +1.93.0 metadata --locked --format-version 1 \
  --filter-platform x86_64-pc-windows-msvc > metadata.json
cargo +1.93.0 tree --locked --offline --target x86_64-pc-windows-msvc \
  -p flightsim-app --edges normal,build --prefix none \
  --format '{p} features=[{f}]' > graph.txt
python3 scripts/collect-dependency-notices.py --metadata metadata.json \
  --repo . --target x86_64-pc-windows-msvc --output fresh-original-notices
```

Two comparisons were made independently:

1. Fresh alpha.23 and alpha.24 metadata from the same checkout/toolchain are
   structurally identical after only the local project-version substitution.
   The alpha.23 baseline was collected before the version change. Its manifest
   and lockfile identities match the published parent and retained source review.
2. Every fresh alpha.24 inventory package is identical to the committed,
   reviewed alpha.23 package record after only those project identity/path
   substitutions. Top-level changes are the actual metadata and Cargo.lock
   digests. Asset/supplement manifests, raw collector scope/status/findings and
   embedded records are unchanged. Host-local metadata paths explain a different
   raw metadata digest; no normalized inventory replaces the raw collection.

Verified coverage:

- 359 complete conservative package records, including features, source/checksum,
  revision, license expression, ordered notices and unresolved fields
- 1,264 ordered normal/build edges, including dependency kind and target condition
- 347 exact `cargo tree` package feature sets identical to the prior review;
  12 conservative-only package records retain null exact graph membership
- 737 original assembly files: 735 exact notice texts, the unchanged collector
  README, and the fresh unmodified inventory; 22 project license destinations
  change version directory while their bytes remain exact
- 510 source-header records, rechecking both the complete original source file
  hash and each exact byte-range hash
- Three unchanged embedded dependency assets and their notice records
- Three complete modified vendor trees, including exact path membership and
  every byte hash: bevy_core_pipeline 55 files, bevy_pbr 149, zune-jpeg 58
- All 557 pre-existing supplemental evidence files rehashed unchanged
- Every previous package license route remains the same. The constgebra/hexf
  collector findings retain their existing exact evidence-backed resolutions

The current source amendment appends the previous alpha.23 amendment unchanged
to history. Historical source SHA/tree, native and environment observations,
Microsoft supplier/component review, failed runtime observation and supplemental
binding remain unchanged. No old executable, native toolset/SDK, final-link
membership, runtime image, rendering result or recipient assent is relabeled.

## Exact collection bindings

The hashes below bind observed bytes; metadata and graph output include local
source paths, so another host can reproduce the content without reproducing
those raw path-dependent hashes. The inventory's metadata hash remains exact.

| Evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| Historical alpha.23 inventory | 407610 | `3038e9253ce86edbf8f566ab3653ada7d03ff951a4d6942affecf8b72b69de6e` |
| Fresh alpha.24 inventory | 407610 | `59d3385ecd3912e87a3eff21362acf870afc37483437fee5b2db1299d0a0c573` |
| Historical dependency review | 1112649 | `67424e20473e63c921b9ce9a67e48f4e93fca927cf6859b1180589d576568d9c` |
| Alpha.23 comparison metadata | 2392709 | `f16ff976dc0a78490bcaf8f15984fcd610b3032cc68113dec809ec88083ad9a3` |
| Alpha.24 metadata | 2392709 | `64b63da56455bdaed5a3d6e040d13ec9dfc096f6fc479ee00b935b73473c0d65` |
| Alpha.24 normal/build tree | 79193 | `0f172c10c8fb70ec2caac7e6263572ef2b431245f6b6d29703936e3c5b70a227` |
| Compiler identity text | 196 | `83e4eefd5e010a92d9f63328bf8219e23fe5e4cf5e5d17ce53d0263cfa4218a6` |
| Cargo.toml | 5018 | `dab096b8af04872a32fe59c2875b791790ed947ab38fd4ddee763dc071417172` |
| Cargo.lock | 154591 | `020ffeba85f07d14d69bbaad8bba2a8e6be943fde97dd559524ca72937a54359` |
| Unmodified collector | 13342 | `5f2ea6860e414ae91dd9672dd1fc75060d0cecce3ba2ae7837afae5cb1fa02f9` |
| Cockpit variant source migration | 3582 | `df88b6a7740626cb14c43a3421253d96336b66d4524e37fd2964e57c82b44bfd` |

## Mechanical validation

- Notice ordering tests: 5 passed
- Commercial-readiness/collector regression tests: 39 passed
- Real source readiness check: only `BUNDLE_NOT_CHECKED` remains; all exact
  dependency inventory, notice and review-evidence checks pass
- `git diff --check`: passed

No synthetic test or source-only pass is treated as bundle/native approval.

## Remaining gates

This source-only assessment does not approve distribution or widen the historical
supplier conditions. A genuine changed-source Windows capture, fresh exact
supplier/native applicability assessment, separately inventory-bound publication
authority, and final same-build bundle/archive/runtime checks remain required.
The previously approved Microsoft component policy is unchanged; no agreement
was accepted and no recipient assent was collected in this review.
