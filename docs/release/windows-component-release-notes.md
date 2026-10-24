## alpha.27 — offline world urban scenery

Default global terrain now includes bounded fictional buildings and short streets
inside bundled Natural Earth urban extents. Urban locations are coarse historical
source data; individual buildings, roads and heights are invented. The 925,730-byte
index works offline without an API key. Generation caps at 2,048 buildings and
256 streets, uses distance LOD and existing rendering budgets, prioritizes loaded
regional scenery and discards old generation on map relocation.

Coarse land/water checks and known-airport/runway exclusions suppress placement.
The roughly 20 km water mask cannot resolve small waterways and conservatively
omits central Sydney. Unknown real airports remain a limitation. Precise worldwide
building tiles are not implemented. Existing CHASE HUD spacing is retained; the
separate unpublished cloud-rendering candidate is not included.

See the [urban scenery guide](https://github.com/Xenoah/flightsim-rust/blob/@SOURCE_SHA@/docs/global-urban-scenery.md)
for provenance, controls and approximation limits. Source tests and software
rendering do not establish physical GPU performance, controller or audio acceptance.
The ordinary Windows bundle continues to contain Light Single and Swift Sport.

## Retained flight and cockpit behavior

Swift Sport retains its 15-degree centered look pitch,
keeping the horizon and approach runway in view. Both sticks, animation pivots
and interaction bounds move forward together by 0.10 m. Its original primary
flight display, dual center sticks and low canopy framing remain unchanged. Light Single retains its analog trainer panel and dual yokes.
The source also supports distinct Meadow and Kestrel interiors, but this ordinary
Windows bundle continues to contain only Light Single and Swift Sport.

Instruments and physical controls remain coupled to existing simulation state
and fixed-step input. Replay controls stay locked; recorded effective-axis
animation is labeled and separate trim is unavailable. The display labels remain
EAS, ellipsoid altitude, true heading, body yaw rate and throttle command, not
unmodeled pitot/static, magnetic, gyro or engine-speed measurements.

Fuel, mixture, starter/magnetos, electrical failures, radio tuning, transponder
and pressure/gyro dynamics remain unmodeled. Generated cockpit views hide the
whole exterior GLB, so external noses and wings are absent from those views;
external views restore the unchanged aircraft models. Unknown or unsupported
model/profile combinations keep their existing fallback. No reference photo,
third-party cockpit mesh, texture, font, dependency or physics change is added.

See the [cockpit guide](https://github.com/Xenoah/flightsim-rust/blob/754bad886cbac8f564c6c46ebdb265c54bda275c/docs/3d-cockpit.md)
and [layout inventory](https://github.com/Xenoah/flightsim-rust/blob/754bad886cbac8f564c6c46ebdb265c54bda275c/docs/aircraft-cockpit-layouts.md)
for operating instructions and limits at the frozen runtime source. Development QA and Linux software-rendered
captures remain separate from this release's own source-bound Windows build,
same-archive smoke and screenshots. Those checks do not establish physical GPU,
controller, native mouse usability, audio or pilot-handling acceptance. Terrain
issue #6 remains open with its earlier bounded residuals and precision limits.

## Windows component terms: review before download or redistribution

This Windows executable includes proprietary Microsoft native runtime/startup
code with separate [component terms, version 2026-10-09-2](https://github.com/Xenoah/flightsim-claude/blob/@SOURCE_SHA@/docs/release/components/MICROSOFT-COMPONENT-TERMS.txt).
Read the complete English terms, [Japanese reference translation](https://github.com/Xenoah/flightsim-claude/blob/@SOURCE_SHA@/docs/release/components/MICROSOFT-COMPONENT-TERMS.ja.txt)
and [component notice](https://github.com/Xenoah/flightsim-claude/blob/@SOURCE_SHA@/docs/release/components/MICROSOFT-COMPONENT-NOTICE.txt).
All three are included in the ZIP with the existing copyright and license notices.
The supplement covers only incorporated Microsoft code, including its protection,
Microsoft/supplier warranty and liability terms, and redistribution obligations.
FlightSim's MIT/Apache-2.0 source rights, separately licensed components and ordinary
FlightSim benchmarking are unchanged.

At first launch, review the full terms before entering the simulator, then choose
**Agree and continue / 同意して続行** or **Decline and exit / 同意せず終了**.
Agreement is not preselected. Declining exits without recording acceptance.
Only your explicit choice stores local acceptance bound to the exact terms
version/hash. Changed terms require a new choice. No account, telemetry or
server-side consent receipt is added. The screen also provides the component notice.

**Redistributors: before onward distribution, run `flightsim-app.exe --component-terms`,
review the same complete terms and explicitly agree.** This terms-only route exits
after your choice without starting the simulator and also lets you reopen the
terms later. Retain the terms/notices and require onward distributors and external
end users to agree to protective terms as the supplement requires. Downloading,
opening a notice or a successful build/smoke test is not recipient assent.

Windows, UCRT, graphics drivers and the **x64 Visual C++ v14 runtime** remain
external prerequisites. Obtain a current supported x64 v14 package from
[Microsoft's official runtime guidance](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170).
No Microsoft DLL, LIB or redistributable installer is separately bundled. Do not
download individual DLLs from unofficial sites. Visual Studio purchase or account
creation is not required by this component supplement.

日本語：初回起動前に英語正文と日本語参考訳を確認し、同意するか終了するかを選択してください。
再配布者は再配布前に `flightsim-app.exe --component-terms` で同じ規約への同意を明示し、
規約・表示を残して次の配布先にも必要な同意を求めてください。専用操作はシミュレーターを
起動せず終了し、同意記録は正確な版・ハッシュに対応して利用端末内だけに保存します。
ソースの MIT／Apache ライセンスと通常のベンチマークは変わりません。
