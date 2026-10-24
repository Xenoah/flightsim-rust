use super::*;

const CITIES: [(&str, f64, f64); 6] = [
    ("Tokyo", 35.68, 139.76),
    ("London", 51.51, -0.12),
    ("New York", 40.75, -73.98),
    ("Sydney (inland)", -33.87, 151.05),
    ("Sao Paulo", -23.55, -46.63),
    ("Cairo", 30.04, 31.24),
];

#[test]
fn known_cities_are_mapped_and_remote_locations_are_empty() {
    let atlas = UrbanAtlas::bundled().unwrap();
    for (name, lat, lon) in CITIES {
        assert!(
            atlas.contains(Geodetic::from_degrees(lat, lon, 0.0)),
            "{name}"
        );
    }
    for (lat, lon) in [(0.0, -140.0), (85.0, 0.0), (-85.0, 0.0), (23.0, 15.0)] {
        assert!(!atlas.contains(Geodetic::from_degrees(lat, lon, 0.0)));
    }
}

#[test]
fn six_regions_are_bounded_repeatable_and_masked() {
    let atlas = UrbanAtlas::bundled().unwrap();
    let land = GlobalTerrain::bundled().unwrap();
    let cancel = AtomicBool::new(false);
    for (name, lat, lon) in CITIES {
        let p = Geodetic::from_degrees(lat, lon, 0.0);
        let a = atlas
            .generate(p, Meters(4_500.0), &land, &|_, _| false, &cancel)
            .unwrap();
        let b = atlas
            .generate(p, Meters(4_500.0), &land, &|_, _| false, &cancel)
            .unwrap();
        let db = a.database.unwrap_or_else(|| panic!("{name} no scene"));
        eprintln!(
            "{name}: {} buildings, {} streets, {} candidates, {} excluded, truncated={}",
            db.buildings().len(),
            db.roads().len(),
            a.statistics.candidates,
            a.statistics.excluded,
            a.statistics.truncated
        );
        assert!(!db.buildings().is_empty(), "{name}");
        assert!(db.buildings().len() <= MAX_URBAN_BUILDINGS);
        assert!(db.roads().len() <= MAX_URBAN_ROADS);
        assert!(a.statistics.candidates <= MAX_URBAN_CANDIDATES);
        assert_eq!(db.buildings(), b.database.unwrap().buildings(), "{name}");
        for building in db.buildings() {
            assert!(building.footprint.iter().all(|&p| dry(&land, p)), "{name}");
            assert!(building.height.get().is_finite());
        }
    }
}

#[test]
fn airport_radius_and_regional_coverage_exclusions_cover_whole_buildings() {
    let atlas = UrbanAtlas::bundled().unwrap();
    let land = GlobalTerrain::bundled().unwrap();
    let p = Geodetic::from_degrees(51.51, -0.12, 0.0);
    let cancel = AtomicBool::new(false);
    let result = atlas
        .generate(
            p,
            Meters(2_250.0),
            &land,
            &|q, padding| q.great_circle_distance(p).get() < 1_000.0 + padding.get(),
            &cancel,
        )
        .unwrap();
    for building in result.database.unwrap().buildings() {
        assert!(
            building
                .footprint
                .iter()
                .all(|q| q.great_circle_distance(p).get() >= 1_000.0)
        );
    }
    let result = atlas
        .generate(p, Meters(9_000.0), &land, &|_, _| true, &cancel)
        .unwrap();
    assert!(result.database.is_none());
    assert!(result.statistics.candidates <= MAX_URBAN_CANDIDATES);
}

#[test]
fn cancelled_invalid_polar_and_date_line_queries_are_safe() {
    let atlas = UrbanAtlas::bundled().unwrap();
    let land = GlobalTerrain::bundled().unwrap();
    let p = Geodetic::from_degrees(51.51, -0.12, 0.0);
    let cancel = AtomicBool::new(true);
    let result = atlas
        .generate(p, Meters(4_500.0), &land, &|_, _| false, &cancel)
        .unwrap();
    assert!(result.database.is_none() && result.statistics.cancelled);
    cancel.store(false, Ordering::Relaxed);
    for (lat, lon) in [(90.0, 180.0), (-90.0, -180.0), (0.0, 180.0), (0.0, -180.0)] {
        assert!(
            atlas
                .generate(
                    Geodetic::from_degrees(lat, lon, 0.0),
                    Meters(9_000.0),
                    &land,
                    &|_, _| false,
                    &cancel
                )
                .unwrap()
                .database
                .is_none()
        );
    }
    assert!(
        atlas
            .generate(p, Meters(f64::NAN), &land, &|_, _| false, &cancel)
            .is_err()
    );
    assert!(!atlas.contains(Geodetic::from_degrees(f64::NAN, 0.0, 0.0)));
}

#[test]
fn lod_and_moving_observer_preserve_surviving_parcels() {
    let atlas = UrbanAtlas::bundled().unwrap();
    let land = GlobalTerrain::bundled().unwrap();
    let p = Geodetic::from_degrees(51.51, -0.12, 0.0);
    let cancel = AtomicBool::new(false);
    let a = atlas
        .generate(p, Meters(2_250.0), &land, &|_, _| false, &cancel)
        .unwrap()
        .database
        .unwrap();
    let b = atlas
        .generate(
            p.offset_by(Meters(600.0), Meters::ZERO),
            Meters(9_000.0),
            &land,
            &|_, _| false,
            &cancel,
        )
        .unwrap()
        .database
        .unwrap();
    let mut shared = 0;
    for building in a.buildings() {
        if let Ok(i) = b
            .buildings()
            .binary_search_by_key(&building.source_id, |b| b.source_id)
        {
            assert_eq!(building, &b.buildings()[i]);
            shared += 1;
        }
    }
    assert!(shared > 500);
}

#[test]
fn malformed_atlas_never_becomes_empty_valid_geography() {
    for bytes in [&BYTES[..0], &BYTES[..19], &BYTES[..BYTES.len() - 1]] {
        assert!(UrbanAtlas::decode(bytes).is_err());
    }
    for index in [0, 4, 6, 8, 12, 21] {
        let mut bytes = BYTES.to_vec();
        bytes[index] ^= 1;
        assert!(UrbanAtlas::decode(&bytes).is_err());
    }
}

#[test]
fn coastal_urban_cells_classified_as_water_are_omitted() {
    let atlas = UrbanAtlas::bundled().unwrap();
    let land = GlobalTerrain::bundled().unwrap();
    let sydney_harbour = Geodetic::from_degrees(-33.87, 151.21, 0.0);
    assert!(atlas.contains(sydney_harbour));
    let result = atlas
        .generate(
            sydney_harbour,
            Meters(4_500.0),
            &land,
            &|_, _| false,
            &AtomicBool::new(false),
        )
        .unwrap();
    assert!(result.database.is_none());
    assert!(result.statistics.excluded > 0);
}

#[test]
fn generated_provenance_round_trips_without_claiming_osm() {
    let atlas = UrbanAtlas::bundled().unwrap();
    let land = GlobalTerrain::bundled().unwrap();
    let db = atlas
        .generate(
            Geodetic::from_degrees(51.51, -0.12, 0.0),
            Meters(1_000.0),
            &land,
            &|_, _| false,
            &AtomicBool::new(false),
        )
        .unwrap()
        .database
        .unwrap();
    let mut bytes = Vec::new();
    db.write(&mut bytes).unwrap();
    let restored = SceneryDatabase::read(bytes.as_slice()).unwrap();
    assert_eq!(restored.source().kind, ScenerySourceKind::ProceduralUrban);
    assert_eq!(restored.buildings(), db.buildings());
}
