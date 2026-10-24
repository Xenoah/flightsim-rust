# Offline urban scenery fallback

With the global terrain enabled (the default), nearby mapped urban areas now
receive invented buildings and short residential street segments even without
`--scenery`. F2 / `--draw-distance short|standard|long` controls the existing
selection radius. No network, API key, purchase or regional download is needed.
A loaded `.fsscenery` database takes priority throughout its conservative bounds.
The HUD attribution explicitly identifies fictional buildings, streets and heights.

This is **not a worldwide precise building map**. Natural Earth's historical
urban extent is real source geography; every generated footprint, street, facade
and height is a deterministic visual approximation. There is no scenery collision,
address, actual street network, landmark identification or real building tile service.
The downloaded region catalogue still supplies terrain, not building tiles.

## Source and reproducibility

The bundled `crates/flightsim-world/data/natural-earth-urban.fsua` is 925,730 bytes.
It derives from 11,878 Natural Earth urban polygons, rasterized to 1/120-degree
cell centres and compressed into sorted half-open row spans. Polygon holes use
even/odd filling. The index contains 1,590,358 occupied cells, not that many buildings.
A cell is about 0.93 km north/south, with longitude spacing shrinking poleward.
An occupied centre does not establish the boundary of an individual urban block.

Natural Earth identifies this layer as derived from MODIS 2002–2003 imagery at
1 km resolution. The official vector release used is v5.1.2. The data are public
domain under [Natural Earth's terms](https://www.naturalearthdata.com/about/terms-of-use/).
See the [layer description](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-urban-area/)
and the adjacent machine-readable provenance file for input/output SHA-256 values.

```sh
curl -fL https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/10m_cultural/ne_10m_urban_areas.shp -o /tmp/ne_10m_urban_areas.shp
python3 scripts/bake_urban.py /tmp/ne_10m_urban_areas.shp crates/flightsim-world/data/natural-earth-urban.fsua
```

The standard-library baker refuses an input whose hash differs from the pinned
source. Runtime has no shapefile parser. It validates header, limits, checksum,
interval ordering and bundled identity before sharing the immutable index.
Generated FSSC source kind 3 identifies procedural urban geometry; older readers
reject this new kind rather than mislabel it as OSM. Kinds 1 and 2 are unchanged.

## Bounds, priority and clearance

Each background request examines at most 32,768 candidate urban cells, retains
at most 2,048 nearby cells, and tests at most 32,768 building parcels. Output is
at most 2,048 buildings and 256 short streets. Far parcels use stable subsets
beyond 2 km and 4 km; generated window/facade detail is limited to 350 m
(regional facade detail retains 2.4 km). Existing scenery vertex/batch/upload caps
still apply. Overflow is reported as `truncated` and does not expand budgets.
Geometry is anchored to global parcel IDs; surviving features keep the same
shape and height during movement, distance changes and revisits.

A single cancellable scenery worker creates optional meshes. Map relocation
cancels its generation, drains owned old assets and refreshes terrain/airport
configuration. A cancelled worker is retained until completion, preventing
rapid relocations from accumulating jobs. Scenery never changes physics or replay.

The existing global independent land/water mask must classify the centre and
all building corners as dry, with land fraction at least 0.6. Street endpoints
and centre must also pass. This is deliberately conservative: Sydney's harbour
and central-city test location are omitted by the coarse atlas, while the inland
Sydney test has buildings. The mask is approximately 20 km resolution. Small
rivers, harbours, islands and true shorelines remain unresolved; this is not a
surveyed water-clearance guarantee.

The active runway, nearby loaded taxiways/aprons and all runways in a supplied
`.fsairports` database exclude generated geometry. Features receive a conservative
200 m centre clearance covering their full extent. Missing/over-budget airport
exclusions suppress generation. No global airport footprint database is bundled;
unknown real airport land cannot be guaranteed clear. Actual regional source
coverage suppresses fallback wholesale, even where that source has missing features.

## Acceptance and platform boundary

See [the dated cloud checkpoint](qa/global-urban-cloud-2026-10-24.md) for the actual
test and screenshot results, including limitations. This change does not authorize
an alpha release or modify historical release approvals/allowlists.

Windows ordinary execution requires the user's own Microsoft component supplement
choice (version `2026-10-09-2`). Review it with `flightsim-app.exe --component-terms`
and personally choose Agree or Decline. No agreement record has been created for
the user. Existing Linux execution contains no Microsoft component route and does
not read/write Windows assent. Software Vulkan images are Linux evidence only.
