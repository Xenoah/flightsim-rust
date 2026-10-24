//! Offline, visual-only invented buildings inside coarse Natural Earth urban cells.
//! No building footprint, street or height here is surveyed. Water and airport
//! exclusions are mandatory, including all footprint corners and their centre.
use crate::{
    BuildingHeightSource, RoadClass, SceneryBuilding, SceneryDatabase, SceneryError, SceneryRoad,
    ScenerySource, ScenerySourceKind, global::GlobalTerrain,
};
use flightsim_core::{Geodetic, LocalFrame, Meters, Ned};
use std::sync::{
    Arc, OnceLock,
    atomic::{AtomicBool, Ordering},
};

const BYTES: &[u8] = include_bytes!("../data/natural-earth-urban.fsua");
const SCALE: u16 = 120;
const ROWS: u16 = 180 * SCALE;
const COLS: u16 = 360 * SCALE;
const MAX_SPANS: usize = 200_000;
const MAX_CELLS: usize = 2_048;
const MAX_CELL_CANDIDATES: usize = 32_768;
const BUNDLED_FINGERPRINT: u64 = 2814579682465643733;
pub const MAX_URBAN_BUILDINGS: usize = 2_048;
pub const MAX_URBAN_ROADS: usize = 256;
pub const MAX_URBAN_CANDIDATES: usize = 32_768;
pub const URBAN_ATTRIBUTION: &str =
    "Natural Earth urban areas (public domain); fictional buildings/streets/heights";

#[derive(Debug, Clone)]
pub struct UrbanAtlas {
    spans: Arc<[[u16; 3]]>,
}

#[derive(Debug, Default, Clone, Copy)]
pub struct UrbanStatistics {
    pub candidates: usize,
    pub excluded: usize,
    pub truncated: bool,
    pub cancelled: bool,
}

#[derive(Debug)]
pub struct UrbanScene {
    pub database: Option<SceneryDatabase>,
    pub statistics: UrbanStatistics,
}

impl UrbanAtlas {
    pub fn bundled() -> Result<Self, SceneryError> {
        static ATLAS: OnceLock<Result<UrbanAtlas, &'static str>> = OnceLock::new();
        ATLAS
            .get_or_init(|| {
                if u64::from_le_bytes(BYTES[12..20].try_into().unwrap()) != BUNDLED_FINGERPRINT {
                    return Err("bundled urban atlas identity");
                }
                Self::decode(BYTES)
            })
            .clone()
            .map_err(SceneryError::Invalid)
    }

    fn decode(bytes: &[u8]) -> Result<Self, &'static str> {
        if bytes.len() < 20
            || bytes.len() > 20 + MAX_SPANS * 6
            || &bytes[..4] != b"FSUA"
            || bytes[4..8] != [1, 0, 120, 0]
        {
            return Err("urban atlas header/length");
        }
        let count = u32::from_le_bytes(bytes[8..12].try_into().unwrap()) as usize;
        if count == 0 || count > MAX_SPANS || bytes.len() != 20 + count * 6 {
            return Err("urban atlas span count");
        }
        let hash = bytes[20..].iter().fold(0xcbf2_9ce4_8422_2325_u64, |h, b| {
            (h ^ u64::from(*b)).wrapping_mul(0x100_0000_01b3)
        });
        if hash != u64::from_le_bytes(bytes[12..20].try_into().unwrap()) {
            return Err("urban atlas checksum");
        }
        let mut spans = Vec::with_capacity(count);
        let mut previous = None;
        for chunk in bytes[20..].chunks_exact(6) {
            let s = [0, 2, 4].map(|i| u16::from_le_bytes([chunk[i], chunk[i + 1]]));
            if s[0] >= ROWS
                || s[1] >= s[2]
                || s[2] > COLS
                || previous.is_some_and(|p: [u16; 3]| p[0] > s[0] || (p[0] == s[0] && p[2] >= s[1]))
            {
                return Err("urban atlas span ordering/bounds");
            }
            spans.push(s);
            previous = Some(s);
        }
        Ok(Self {
            spans: spans.into(),
        })
    }

    /// Cell-centre coverage only; coarse cells may extend beyond source polygons.
    #[must_use]
    pub fn contains(&self, point: Geodetic) -> bool {
        if !valid(point) {
            return false;
        }
        let (row, col) = cell(point);
        let i = self
            .spans
            .partition_point(|s| s[0] < row || (s[0] == row && s[2] <= col));
        self.spans
            .get(i)
            .is_some_and(|s| s[0] == row && s[1] <= col && col < s[2])
    }

    /// Bounded selection and stable, globally anchored parcels. The callback must
    /// conservatively reject known airport/regional coverage, with `padding`
    /// covering the complete feature, not just its sampled centre. True = exclude.
    /// The global mask is intentionally conservative; its ~20 km resolution can
    /// omit coastal cities and cannot guarantee surveyed shoreline clearance.
    pub fn generate(
        &self,
        observer: Geodetic,
        radius: Meters,
        land: &GlobalTerrain,
        excluded: &dyn Fn(Geodetic, Meters) -> bool,
        cancel: &AtomicBool,
    ) -> Result<UrbanScene, SceneryError> {
        let mut stats = UrbanStatistics::default();
        let empty = |statistics| UrbanScene {
            database: None,
            statistics,
        };
        if !valid(observer) || !radius.is_finite() || !(0.0..=9_000.0).contains(&radius.get()) {
            return Err(SceneryError::Invalid("urban query"));
        }
        // There is no bundled urban coverage at the poles. Avoid singular bbox
        // expansion there without inventing settlements or a second conversion.
        if observer.latitude.to_degrees().get().abs() > 85.0 {
            return Ok(empty(stats));
        }
        let pad = Meters(radius.get() + 1_500.0);
        let south = observer.offset_by(Meters(-pad.get()), Meters::ZERO);
        let north = observer.offset_by(pad, Meters::ZERO);
        let low = cell(south).0;
        let high = cell(north).0;
        let edge = if north.latitude.get().abs() > south.latitude.get().abs() {
            north
        } else {
            south
        };
        let lon_delta =
            (edge.offset_by(Meters::ZERO, pad).longitude.get() - edge.longitude.get()).abs();
        let center_col = (observer.longitude.to_degrees().get() + 180.0) * f64::from(SCALE);
        let col_delta = lon_delta.to_degrees() * f64::from(SCALE) + 1.0;
        let first = self.spans.partition_point(|s| s[0] < low);
        let last = self.spans.partition_point(|s| s[0] <= high);
        let mut cells = Vec::new();
        'selection: for &[row, a, b] in &self.spans[first..last] {
            if cancel.load(Ordering::Relaxed) {
                stats.cancelled = true;
                return Ok(empty(stats));
            }
            // Three shifted intervals implement longitude wrap without a global scan.
            for shift in [-f64::from(COLS), 0.0, f64::from(COLS)] {
                let start = (center_col - col_delta + shift).floor().max(f64::from(a));
                let end = (center_col + col_delta + shift).ceil().min(f64::from(b));
                #[allow(
                    clippy::cast_possible_truncation,
                    reason = "clipped to validated u16 row spans"
                )]
                for col in (start.max(0.0) as u16)..(end.max(0.0) as u16) {
                    let p = position(row, col, 0.5, 0.5);
                    let distance = p.great_circle_distance(observer).get();
                    if distance <= pad.get() {
                        if cells.len() == MAX_CELL_CANDIDATES {
                            stats.truncated = true;
                            break 'selection;
                        }
                        cells.push((distance, row, col));
                    }
                }
            }
        }
        cells.sort_by(|a, b| {
            a.0.total_cmp(&b.0)
                .then_with(|| (a.1, a.2).cmp(&(b.1, b.2)))
        });
        stats.truncated |= cells.len() > MAX_CELLS;
        let mut buildings = Vec::new();
        let mut roads = Vec::new();
        'cells: for (_, row, col) in cells.into_iter().take(MAX_CELLS) {
            for slot in 0..64_u32 {
                if cancel.load(Ordering::Relaxed) {
                    stats.cancelled = true;
                    return Ok(empty(stats));
                }
                if stats.candidates == MAX_URBAN_CANDIDATES
                    || buildings.len() == MAX_URBAN_BUILDINGS
                {
                    stats.truncated = true;
                    break 'cells;
                }
                stats.candidates += 1;
                let id =
                    (u64::from(row) * u64::from(COLS) + u64::from(col)) * 64 + u64::from(slot) + 1;
                let hash = mix(id);
                let p = position(
                    row,
                    col,
                    (f64::from(slot / 8) + 0.5) / 8.0,
                    (f64::from(slot % 8) + 0.5) / 8.0,
                );
                let distance = p.great_circle_distance(observer).get();
                // Stable subset per LOD; surviving parcels never change geometry.
                if distance > radius.get()
                    || (distance > 4_000.0 && hash % 8 != 0)
                    || (distance > 2_000.0 && hash % 3 != 0)
                {
                    continue;
                }
                let east_spacing = p
                    .to_ecef()
                    .distance_to(
                        position(
                            row,
                            col,
                            (f64::from(slot / 8) + 0.5) / 8.0,
                            (f64::from(slot % 8) + 1.5) / 8.0,
                        )
                        .to_ecef(),
                    )
                    .get();
                let half_east = (10.0 + f64::from((hash & 15) as u8)).min(east_spacing * 0.25);
                let half_north = 10.0 + f64::from(((hash >> 4) & 15) as u8);
                if half_east < 3.0 {
                    continue;
                }
                let padding = Meters(half_east.hypot(half_north) + 4.0);
                if excluded(p, padding) || !dry(land, p) {
                    stats.excluded += 1;
                    continue;
                }
                let frame = LocalFrame::new(p);
                let footprint: Vec<_> = [
                    (-half_north, -half_east),
                    (-half_north, half_east),
                    (half_north, half_east),
                    (half_north, -half_east),
                ]
                .into_iter()
                .map(|(n, e)| {
                    let p = frame
                        .ned_to_ecef_position(Ned::new(n, e, 0.0))
                        .to_geodetic();
                    Geodetic {
                        altitude: Meters::ZERO,
                        ..p
                    }
                })
                .collect();
                if footprint.iter().any(|&p| !dry(land, p)) {
                    stats.excluded += 1;
                    continue;
                }
                buildings.push(SceneryBuilding {
                    source_id: i64::try_from(id).expect("bounded global parcel ID"),
                    height: Meters(if hash % 29 == 0 {
                        45.0 + f64::from((hash % 80) as u8)
                    } else {
                        6.0 + f64::from((hash % 9) as u8) * 3.0
                    }),
                    height_source: BuildingHeightSource::Default,
                    footprint,
                    triangles: vec![[0, 1, 2], [0, 2, 3]],
                });
            }
            // Short invented street segments stay between parcel rows. Conservative
            // centre+radius exclusion covers the whole segment and road width.
            if roads.len() < MAX_URBAN_ROADS {
                let center = position(row, col, 0.5, 0.5);
                let a = center.offset_by(Meters::ZERO, Meters(-180.0));
                let b = center.offset_by(Meters::ZERO, Meters(180.0));
                if center.great_circle_distance(observer).get() < radius.get()
                    && [a, center, b]
                        .into_iter()
                        .all(|p| valid(p) && dry(land, p) && self.contains(p))
                    && !excluded(center, Meters(185.0))
                {
                    roads.push(SceneryRoad {
                        source_id: i64::from(row) * i64::from(COLS) + i64::from(col) + 1,
                        class: RoadClass::Residential,
                        width: Meters(6.0),
                        width_inferred: true,
                        points: vec![a, b],
                    });
                }
            } else {
                stats.truncated = true;
            }
        }
        if buildings.is_empty() && roads.is_empty() {
            return Ok(empty(stats));
        }
        let database = SceneryDatabase::new(ScenerySource {
            kind: ScenerySourceKind::ProceduralUrban, name: URBAN_ATTRIBUTION.into(),
            url: "https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-urban-area/".into(),
            input_fingerprint: u64::from_le_bytes(BYTES[12..20].try_into().unwrap()),
        }, roads, buildings, vec![])?;
        Ok(UrbanScene {
            database: Some(database),
            statistics: stats,
        })
    }
}

fn dry(land: &GlobalTerrain, p: Geodetic) -> bool {
    land.sample(p)
        .is_some_and(|s| s.is_land && !s.is_inland_water && s.land_fraction >= 0.6)
}
fn mix(mut x: u64) -> u64 {
    x ^= x >> 30;
    x = x.wrapping_mul(0xbf58_476d_1ce4_e5b9);
    x ^= x >> 27;
    x = x.wrapping_mul(0x94d0_49bb_1331_11eb);
    x ^ (x >> 31)
}
fn valid(p: Geodetic) -> bool {
    p.latitude.is_finite()
        && p.longitude.is_finite()
        && p.altitude.is_finite()
        && p.latitude.to_degrees().get().abs() <= 90.0
        && p.longitude.to_degrees().get().abs() <= 180.0
}
#[allow(
    clippy::cast_possible_truncation,
    reason = "clamped atlas grid coordinates"
)]
fn cell(p: Geodetic) -> (u16, u16) {
    (
        ((p.latitude.to_degrees().get() + 90.0) * f64::from(SCALE))
            .floor()
            .clamp(0.0, f64::from(ROWS - 1)) as u16,
        (((p.longitude.to_degrees().get() + 180.0) * f64::from(SCALE)).floor() as i32)
            .rem_euclid(i32::from(COLS)) as u16,
    )
}
fn position(row: u16, col: u16, north: f64, east: f64) -> Geodetic {
    Geodetic::from_degrees(
        (f64::from(row) + north) / f64::from(SCALE) - 90.0,
        ((f64::from(col) + east) / f64::from(SCALE)).rem_euclid(360.0) - 180.0,
        0.0,
    )
}

#[cfg(test)]
#[path = "urban_tests.rs"]
mod tests;
