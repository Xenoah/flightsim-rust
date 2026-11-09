# ADR-0035: Building surface detail without pane geometry

- Date: 2026-11-02
- Status: development candidate; actual rendering and source admission tracked in QA

## Decision

Render original window, floor-band, cornice and roof-joint artwork on the existing
opaque scenery mesh using one shared `ExtendedMaterial<StandardMaterial, ...>`.
Remove the separate window quads. Keep footprint, height, roof elevation,
foundation, normals, roads, vegetation, selection, exclusion and upload budgets.
This applies to both the offline invented urban fallback and regional building
geometry. It does not imply surveyed facades or accurate landmarks.

Each face carries two `vec2` attributes. UV0 contains building-local metres;
UV1 carries an explicit wall/roof/other discriminator, one exact source-ID seed
byte and building height. Positive discriminators are walls, negative ones roofs,
zero means ordinary PBR. Each triangle has a constant discriminator. Winding
reversal also reverses UVs. Ground overlay remeshing may omit the attributes;
the shader then retains ordinary PBR. No normal or global-position inference is
used to guess whether a surface is a wall.

Coordinates are prepared through core's f64 ECEF/LocalFrame conversions before
conversion to local f32 attributes. Camera position, floating origin, batch
origin, visit order and clocks do not seed the artwork. Arbitrary regional
polygon corners can terminate a window bay; we do not infer a real facade plan.

The shader evaluates derivatives before varying branches and uses the Frobenius
norm of the two metre-coordinate derivatives to bound a pixel's footprint.
Window detail fades to its area-average colour from 0.25 to 1.25 m per pixel;
fine mullions fade earlier. Roof joints fade from 0.12 to 0.48 roof cells per
pixel, so broad panels remain legible longer than individual slate joints.
This includes grazing views without
increasing distance-based geometry density. The work has no variable loops,
texture allocation, per-building material or additional light. Window roughness
uses the existing PBR lighting. No emission is added; night lighting is a separate
future design. Light/High/Ultra retain the same material and geometry while the
existing sampling/lighting policy remains reversible.

## Alternatives and costs

More window quads would exhaust the scene vertex budget and omit surrounding
blocks, as found during the original urban QA. A large facade texture collection
would add download, rights and streaming obligations. This original procedural
surface adds only embedded shader/code bytes, at the cost of fragment work and
16 attribute bytes per mesh vertex (at the existing 600,000-vertex scene ceiling,
9.6 MB before any GPU/backend padding). No new entity or vertex allowance is
introduced. This is a bound, not a hardware performance claim.

The pattern is illustrative and repeated, with no interiors, geometry relief,
surveyed material classification or new building collision. Close inspection
will still reveal coarse urban placements and flat roofs. Global land/airport
masks retain their prior resolution and omissions.

## Acceptance boundary

Check source geometry invariance, classification, stable coordinates across
rebasing/revisits and geographic seams, rollback and dense-block budgets, actual
Bevy shader compilation, and matching close/far/day/low-light captures. Software
Vulkan screenshots do not qualify Windows runtime, physical GPU performance or
distribution. A new bounded source-only migration must retain the complete
alpha.27 proof and leave native, recipient-assent and publication gates closed.
