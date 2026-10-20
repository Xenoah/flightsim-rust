# Alpha.25 source-only dependency and notice amendment

Date: 2026-10-19. Published Swift visibility source: `754bad886cbac8f564c6c46ebdb265c54bda275c`.
The separately hashed local alpha.25 version preparation is uncommitted at this
review. This source assessment does not relabel any earlier Windows observation,
accept an agreement, or grant runtime, appearance or publication approval.

## Bounded authored change

The [Swift forward-visibility migration](../../scripts/swift-forward-visibility-source-migration.json)
binds three changed crate source files against published alpha.24 source
`4f385e121addc036c2103d634e2bb46e6392172b`:

- `crates/flightsim-render/src/cockpit.rs`: Sport's centered downward angle
  changes from 24 to 15 degrees; the other layouts retain their existing angles.
- `crates/flightsim-render/src/cockpit/variants.rs`: both Sport stick assemblies,
  including animation pivots and attached hit surfaces, move 0.10 m forward.
- `crates/flightsim-app/src/cockpit_runtime.rs`: regression tests only.

All three current file hashes and all three retained predecessor hashes match
the exact migration. The complete `crates/`, `vendor/` and `assets/` diff from
that released base contains only these three paths. These are changes to existing
project-authored camera framing and procedural geometry, plus four regression
tests. No new source dependency, external cockpit mesh, photograph, texture,
font, audio, asset, aircraft profile, physics, replay rule or component term is
introduced. The [dated development report](swift-forward-view-2026-10-19.md)
retains its image/runtime limits and historical failed pre-admission result;
this notice review does not turn those into new Windows acceptance.

The additional alpha.25 preparation changes one workspace version field and
13 local lockfile package versions. The complete Cargo files are otherwise
byte-identical to the published Swift source. Only 11 local packages belong to
the ordinary application's normal/build closure; the two offline tools remain
outside that closure. Exactly 22 original project license destinations change
from alpha.24 to alpha.25 directory names, with unchanged bytes.

## Fresh collection and complete comparison

Rust 1.93.0 on `x86_64-unknown-linux-gnu` collected an alpha.24 baseline before
the version edit, then fresh alpha.25 Windows-target metadata and normal/build
tree output in the same checkout. Missing Windows-target crates were fetched
from the official Cargo registry; the lockfile remained exact. Both captures
verified Cargo hashes before and after collection. The existing collector wrote
to a new empty directory, and its output was compared before any reviewed notice
path or inventory was replaced.

```sh
rustc +1.93.0 -vV
cargo +1.93.0 metadata --locked --offline --format-version 1 \
  --filter-platform x86_64-pc-windows-msvc > metadata.json
cargo +1.93.0 tree --locked --offline --target x86_64-pc-windows-msvc \
  -p flightsim-app --edges normal,build --prefix none \
  --format '{p} features=[{f}]' > graph.txt
python3 -B scripts/collect-dependency-notices.py --metadata metadata.json \
  --repo . --target x86_64-pc-windows-msvc --output fresh-original-notices
```

The complete fresh metadata structures differ only by the local project version
substitution. Every fresh inventory package equals its reviewed alpha.24 record
after those project identity/path substitutions. The only other inventory
changes are the actual metadata and Cargo.lock digests. This is cross-target
source metadata, not a native Windows build.

Verified scope:

- 359 complete conservative package records, including ordered notices, source,
  checksum, revision, license expression, feature lists and unresolved fields
- 1,264 ordered normal/build edges, including kind and target condition; these
  also equal the genuine final alpha.24 native graph after project-version
  substitution alone
- 347 exact normal/build feature sets; 12 conservative-only package records
  retain null exact graph membership
- 737 original assembly files: 735 exact notice texts, collector README and
  the fresh unmodified inventory; no notice order or notice text changed
- All 557 pre-existing supplemental evidence files and their complete path set
- 510 source-header records, checking whole source bytes and each exact span
- Three unchanged embedded dependency assets and their original notices
- Complete modified vendor trees with exact path sets and hashes:
  bevy_core_pipeline 55 files, bevy_pbr 149, zune-jpeg 58

The raw collector inventory retains `not_reviewed` and both original
constgebra/hexf missing-primary-notice findings. Their existing exact evidence
and reviewed resolutions remain separate. The previous alpha.24 source amendment
is appended unchanged to history. Historical source SHA/tree, native/environment
facts, Microsoft supplier conditions and runtime observations remain unchanged.

## Exact collection bindings

Metadata/tree text can include local paths. These records bind actual original
bytes; they do not prescribe a normalizer or infer a native metadata-difference
cause. The inventory retains the fresh metadata's exact digest.

| Evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| Historical alpha.24 inventory | 407610 | `59d3385ecd3912e87a3eff21362acf870afc37483437fee5b2db1299d0a0c573` |
| Fresh alpha.25 inventory | 407610 | `f5d6ddd9ef0827544135912ae46d3a6901d8de3911039f7cfb835947c9eec735` |
| Historical dependency review | 1122191 | `fb29e32699f2956b46f92255c94f7402ffa8817ade72c5936f62d79d29acafdd` |
| Fresh alpha.24 comparison metadata | 2460027 | `e4996b016d8601e0fd10ae2568532bc4cbb86d6f568928cec39d813fe22c363e` |
| Fresh alpha.25 metadata | 2460027 | `8fbc9a2952e57830c09671ca22e32c6cdd0e11c5bc8d44ffcd6e95fd3b9deb0e` |
| Alpha.25 normal/build tree | 79193 | `e5c6980c8635754ea6f3bbc78f977aec72868c7c9b1c33bd9b3633fcb1843453` |
| Compiler identity | 196 | `83e4eefd5e010a92d9f63328bf8219e23fe5e4cf5e5d17ce53d0263cfa4218a6` |
| Cargo.toml | 5018 | `d73e043a71ed4bccaae07dbbd0e7b4573392e70b05ef09a4a04a6e5f3e4b71ab` |
| Cargo.lock | 154591 | `f2d1cb82a6a292afa0f6289fbcf235f492ab1579a50246ed99323e9994cfcab1` |
| Unmodified collector | 13342 | `5f2ea6860e414ae91dd9672dd1fc75060d0cecce3ba2ae7837afae5cb1fa02f9` |
| Swift visibility migration | 2167 | `6bf34c0ddc0e9bf76f8a9717092e51c16d7f168379682dcfef6b40364a5d401d` |
| Preserved final alpha.24 native packet | 2915397 | `9ca0ca2a8e906a2c71ab9a611c78026dd4cf857731ce1fadaddc0a5dfadd4c64` |

The genuine final alpha.24 native packet is from ordinary Release run
[39249808180](https://github.com/Xenoah/flightsim-rust/actions/runs/39249808180),
source `4f385e121addc036c2103d634e2bb46e6392172b`, tree
`47aed13ca164afcadf3c1201c411fecd00e77cd4`. It is retained unchanged as the next
native comparison baseline. Reading it and comparing its dependency graph does
not make it an alpha.25 build. The earlier alpha.24 bootstrap is also retained.

## Validation and remaining gates

- Notice ordering regression tests: 5 passed
- Commercial-readiness/collector regression tests: 39 passed
- Complete source/notice comparison: all assertions passed
- Real source readiness: only `BUNDLE_NOT_CHECKED` remains; inventory,
  original notices and review evidence pass their exact checks
- `git diff --check`: passed

These mechanical/source results do not qualify the final executable or bundle.
Fresh changed-source Windows capture and supplier/native applicability review,
separately bound publication authority, archive integrity and extracted
Light Single/Swift runtime checks remain required. No Microsoft agreement or
recipient assent was accepted or collected by this amendment.
