# Alpha.26 source-tool CI budget correction

Date: 2026-10-23. This is a source/CI correction, not Windows execution or
distribution acceptance.

PR #58 head `2eb36242cde4ccd3492b0079d4de226ee26db15e` has the exact locally
verified preparation tree `f56e97232728aed82b66edb82beb7417e946c929`.
The earlier clean local full suite completed 820 tests: 819 passed and one
Windows-only junction test skipped, in 2615.550 seconds. Those results remain
about that source, not this subsequent correction.

In hosted CI run [39944623925](https://github.com/Xenoah/flightsim-rust/actions/runs/39944623925),
source-tool job [120384115530](https://github.com/Xenoah/flightsim-rust/actions/runs/39944623925/job/120384115530)
started at 11:13:55 UTC and was cancelled at 11:59:10 UTC. Its log contains 751
completed successful test results, no assertion failure and no completed suite
summary. The last completed test was the terrain-stitch committed-drift check;
the exhaustive pin-mutation sweep had not reported completion. No passing result
is inferred from cancellation.

The correction increases only the `world_source_tools` budget from 45 to 60
minutes. It does not omit, select away, weaken or parallelize any test. Every
other workflow byte is preserved. Exact predecessor witnesses and a bounded
analytical source-admission successor preserve the older 30-to-45 proof and
reject changes to commands, permissions, triggers, runners or other job limits.
The replay/runtime/Cargo/asset/dependency/native facts remain unchanged.

The permission-only receipt must cover this exact source. Historical native
applicability remains fail-closed; unchanged `release.yml` still uses
`windows-latest`. The corrected PR and main require complete normal CI, followed
by genuine same-build Windows evidence and every existing publication gate.
