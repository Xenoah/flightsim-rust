# Alpha.27 source and notice review — no new native observation

Reviewed 2026-10-24 by the development assistant. Candidate base is merged urban
main `de5d43ab5af2dcfb3f1fcda3c50478c0029af642`, tree
`83dd2788a021081537033f3d74416b37e724c7be`. This identifies a source merge,
not a published alpha.27 or a new Windows execution.

The source implementation is reviewed in
[the bounded urban review](urban-source-admission-2026-10-24.md). Nine existing
inputs change and four new crate inputs add the generator, regressions, pinned
925,730-byte Natural Earth index and provenance. The official v5.1.2 urban extent
is public-domain data; retained ATTRIBUTION identifies its provenance and the
fictional building/street/height distinction. No third-party building mesh,
texture, photograph, dependency or executable was imported. The embedded index
adds data to the application binary, not a new dependency package or SDK grant.
Coarse water and known-airport exclusions do not establish precision mapping.
HUD layout, cloud candidate, physics, aircraft and component terms are unchanged.

Fresh Rust 1.93.0 metadata (`--locked --filter-platform x86_64-pc-windows-msvc`)
and the full ordered normal/build graph were captured before and after the version
edit in the same Linux checkout. Complete metadata JSON and graph text compare
equal after only alpha.26 -> alpha.27 substitution. Cargo inputs differ by one
workspace field and thirteen local lockfile version fields only.

Both fresh collections use the unchanged notice collector. All 359 package
records, their features and ordering, embedded dependency assets and original
findings remain unchanged modulo eleven runtime-closure project identities.
The baseline fresh inventory differs from the retained alpha.26 inventory only
by its actual observed metadata digest. The successor additionally changes
project versions/notice paths and the actual Cargo lock digest; no other field
is normalized. Raw `review_status: not_reviewed` and both collector findings stay
unchanged. Full metadata, trees and raw collector outputs remain in the cloud
evidence checkpoint.

All 735 original licence text files were compared byte-for-byte across the old
assembly, fresh baseline and successor. Only 22 project licence destinations
change version names. All 557 supplemental files remain byte-exact. All 363
reviewed resolutions point to verified original/supplemental bytes, and all 510
source-header records were checked against fresh package source, including both
whole-file and exact excerpt hashes. Existing package licence routes, upstream
notices, vendor provenance and component presentation obligations remain intact.

The old review's source/tree, native, supplier, environment, runtime and component
facts are retained as historical records. Its prior amendment is appended intact
to history. This amendment records only observed source/notice facts; it does not
record a new agreement, recipient assent, Windows build, runtime acceptance,
distribution qualification or publication authority. Genuine current-source
Windows observations, all eleven applicability sections, same-build archive
verification, both extracted-aircraft smokes and remote release verification
remain mandatory separate stages.
