# Building-surface source boundary

This source-only successor is based on public commit
`729a72d205d3cdee4c2b18779b5d8a14e24672a2` and tree
`3747783385d9f5cab4163dde6dc2b930ae441a07`.

The runtime change adds explicit wall/roof metadata and building-local metre
coordinates, registers one shared opaque PBR extension, removes separate window
pane geometry, and applies derivative-filtered windows, floor bands and roof
joints. Surface classification keeps these patterns off roads, vegetation and
other ordinary surfaces. Source-ID seeds and local coordinates keep the detail
stable across floating-origin updates and revisits.

Selection policy, LOD thresholds and vertex caps remain unchanged. Removing
pane geometry can let more complete features fit within the same vertex cap.
Building footprints, roof heights, flight dynamics, controls and replay are
outside this runtime delta. Regional scenery priority, allocation/cancellation,
and water/airport exclusions remain in place. No new external textures, lights,
emission or online services are introduced.

The bounded source migration retains the complete prior 1,028-input replay,
71-input analytical and four-input capture proofs. Ten exact public-base blob
witnesses preserve three prior contracts, six changed runtime source files and
the prior scenery-budget regression. The oldest historical witness wins on
overlap; each positive result still evaluates the complete prior proof. The
successor explicitly enumerates its replaced and added inputs, with a current
boundary of 1,044 replay, 72 analytical and four capture inputs. No wildcard
admits additional crate members.

The scenery-budget regression checks exact counts below, at and above the
complete 64-building budget, with detail enabled and disabled. Surface tests
cover wall/roof classification, sloped foundations, reversed winding, stable
coordinates and reversible quality changes. Source-admission negative tests
reject omissions, aliases, repins, joint descriptor reseals and additional
acceptance claims. Historical validators, hashes and witnesses are retained.

Natural Earth urban extents are real geographic data; fallback buildings and
streets remain procedural approximations. This material change does not provide
precise worldwide terrain or surveyed building coverage. Source admission does
not establish native Windows qualification, recipient assent, release authority
or physical-GPU performance; those remain separate evidence and release gates.
