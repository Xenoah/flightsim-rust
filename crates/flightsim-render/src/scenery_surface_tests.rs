use super::*;
use bevy::mesh::VertexAttributeValues;
use flightsim_world::scenery::BuildingHeightSource;

fn source(at: Geodetic, id: i64) -> SceneryBuilding {
    let frame = LocalFrame::new(at);
    SceneryBuilding {
        source_id: id,
        height: Meters(21.0),
        height_source: BuildingHeightSource::Default,
        footprint: [(0.0, 0.0), (0.0, 20.0), (16.0, 20.0), (16.0, 0.0)]
            .map(|(n, e)| {
                let p = frame
                    .ned_to_ecef_position(Ned::new(n, e, 0.0))
                    .to_geodetic();
                Geodetic::new(p.latitude, p.longitude, Meters::ZERO)
            })
            .to_vec(),
        triangles: vec![[0, 1, 2], [0, 2, 3]],
    }
}

fn pairs(mesh: &Mesh, attribute: bevy::mesh::MeshVertexAttribute) -> &[[f32; 2]] {
    let Some(VertexAttributeValues::Float32x2(values)) = mesh.attribute(attribute) else {
        panic!("missing surface coordinates");
    };
    values
}

fn build(building: &SceneryBuilding, origin: Ecef) -> Mesh {
    let mut builder = Builder::new(origin, MAX_BATCH_VERTICES, None);
    assert!(build_building(&mut builder, building, true, &mut |_| Some(
        Meters(80.0)
    )));
    builder.finish()
}

#[test]
fn roofs_walls_and_vegetation_have_disjoint_explicit_surface_kinds() {
    let at = Geodetic::from_degrees(35.68, 139.76, 0.0);
    let building = source(at, -991);
    let mut builder = Builder::new(at.to_ecef(), MAX_BATCH_VERTICES, None);
    assert!(build_building(
        &mut builder,
        &building,
        true,
        &mut |_| Some(Meters(80.0))
    ));
    assert_eq!(builder.len(), 30, "no separate window polygons");
    assert!(tree_with_roots(
        &mut builder,
        at,
        Meters(9.0),
        17,
        FOUNDATION_DEPTH
    ));
    let mesh = builder.finish();
    let kinds = pairs(&mesh, Mesh::ATTRIBUTE_UV_1);
    assert!(
        kinds[..6]
            .iter()
            .all(|k| k[0] <= -1.0 && k[1].to_bits() == 21.0_f32.to_bits())
    );
    assert!(
        kinds[6..30]
            .iter()
            .all(|k| k[0] >= 1.0 && k[1].to_bits() == 21.0_f32.to_bits())
    );
    assert!(kinds[30..].iter().all(|k| k.map(f32::to_bits) == [0; 2]));
    assert!(
        pairs(&mesh, Mesh::ATTRIBUTE_UV_0)
            .iter()
            .flatten()
            .all(|v| v.is_finite())
    );

    let mut ground = Builder::new(at.to_ecef(), MAX_BATCH_VERTICES, None);
    let road = SceneryRoad {
        source_id: 2,
        class: RoadClass::Residential,
        width: Meters(6.0),
        width_inferred: false,
        points: building.footprint[..2].to_vec(),
    };
    assert!(build_road(&mut ground, &road, &mut |_| Some(Meters(80.0))));
    let mesh = ground.finish();
    assert!(
        pairs(&mesh, Mesh::ATTRIBUTE_UV_1)
            .iter()
            .all(|k| k.map(f32::to_bits) == [0; 2])
    );
}

#[test]
fn surface_coordinates_and_style_survive_rebase_revisit_and_geographic_seams() {
    for (lat, lon) in [
        (35.68, 139.76),
        (51.51, -0.12),
        (0.0, 179.9999),
        (89.9, 40.0),
    ] {
        let at = Geodetic::from_degrees(lat, lon, 0.0);
        let building = source(at, i64::MIN);
        let before = building.clone();
        let first = build(&building, at.to_ecef());
        let shifted = LocalFrame::new(at).ned_to_ecef_position(Ned::new(1250.0, -2100.0, 0.0));
        let rebased = build(&building, shifted);
        let revisit = build(&building, at.to_ecef());
        for attribute in [
            Mesh::ATTRIBUTE_UV_0,
            Mesh::ATTRIBUTE_UV_1,
            Mesh::ATTRIBUTE_COLOR,
        ] {
            assert_eq!(first.attribute(attribute), rebased.attribute(attribute));
            assert_eq!(first.attribute(attribute), revisit.attribute(attribute));
        }
        assert_eq!(
            first.attribute(Mesh::ATTRIBUTE_POSITION),
            revisit.attribute(Mesh::ATTRIBUTE_POSITION)
        );
        assert_eq!(
            building, before,
            "rendering never rewrites source geography"
        );
    }
}

#[test]
fn surface_metadata_rolls_back_with_failed_feature_and_keeps_dense_blocks() {
    let at = Geodetic::from_degrees(51.51, -0.12, 0.0);
    let buildings: Vec<_> = (0..64).map(|id| source(at, id)).collect();
    let refs: Vec<_> = buildings.iter().map(SceneryFeatureRef::Building).collect();
    let mesh = scenery_mesh(
        &refs,
        at,
        SceneryMeshOptions::near(at),
        &mut |_| Some(Meters(80.0)),
        &|_| false,
    )
    .unwrap();
    assert_eq!(mesh.statistics.buildings, 64);
    assert_eq!(mesh.statistics.vertices, 64 * 30);
    assert_eq!(mesh.statistics.skipped_features, 0);
    assert_ne!(
        pairs(&mesh.mesh, Mesh::ATTRIBUTE_UV_1)[6].map(f32::to_bits),
        pairs(&mesh.mesh, Mesh::ATTRIBUTE_UV_1)[36].map(f32::to_bits)
    );

    let mut options = SceneryMeshOptions::near(at);
    options.max_vertices = 45;
    let bounded = scenery_mesh(
        &refs[..2],
        at,
        options,
        &mut |_| Some(Meters(80.0)),
        &|_| false,
    )
    .unwrap();
    assert_eq!(bounded.statistics.buildings, 1);
    assert_eq!(bounded.statistics.skipped_features, 1);
    assert_eq!(bounded.mesh.count_vertices(), 30);
    for attribute in [Mesh::ATTRIBUTE_UV_0, Mesh::ATTRIBUTE_UV_1] {
        assert_eq!(
            pairs(&bounded.mesh, attribute).len(),
            bounded.mesh.count_vertices()
        );
    }
}

#[test]
fn reversed_winding_and_sloped_foundations_keep_surface_coordinates_attached() {
    let at = Geodetic::from_degrees(51.51, -0.12, 0.0);
    for reverse in [false, true] {
        let mut building = source(at, 100);
        if reverse {
            building.footprint.reverse();
        }
        let terrain_frame = LocalFrame::new(at);
        let elevation = |p: Geodetic| {
            Meters(80.0 + terrain_frame.ecef_to_ned_position(p.to_ecef()).north() * 0.2)
        };
        let highest = building
            .footprint
            .iter()
            .copied()
            .map(elevation)
            .map(Meters::get)
            .fold(f64::NEG_INFINITY, f64::max);
        let mut builder = Builder::new(at.to_ecef(), MAX_BATCH_VERTICES, None);
        assert!(build_building(
            &mut builder,
            &building,
            true,
            &mut |p| Some(elevation(p))
        ));
        let mesh = builder.finish();
        let Some(VertexAttributeValues::Float32x3(positions)) =
            mesh.attribute(Mesh::ATTRIBUTE_POSITION)
        else {
            panic!("missing positions");
        };
        let Some(VertexAttributeValues::Float32x3(normals)) =
            mesh.attribute(Mesh::ATTRIBUTE_NORMAL)
        else {
            panic!("missing normals");
        };
        let uv = pairs(&mesh, Mesh::ATTRIBUTE_UV_0);
        let local = LocalFrame::new(building.footprint[0]);
        for (index, position) in positions.iter().enumerate() {
            let world = Ecef::from_vec(
                at.to_ecef().as_vec() + glam::Vec3::from_array(*position).as_dvec3(),
            );
            let geo = world.to_geodetic();
            if index < 6 {
                let projected = local.ecef_to_ned_position(
                    Geodetic::new(geo.latitude, geo.longitude, Meters::ZERO).to_ecef(),
                );
                assert!((f64::from(uv[index][0]) - projected.east()).abs() < 0.001);
                assert!((f64::from(uv[index][1]) - projected.north()).abs() < 0.001);
                assert!(
                    glam::Vec3::from_array(normals[index])
                        .as_dvec3()
                        .dot(world.as_vec())
                        > 0.0,
                    "roof must face outwards for both input windings"
                );
            } else {
                assert!(
                    (f64::from(uv[index][1]) - (geo.altitude.get() - highest)).abs() < 0.001,
                    "wall coordinates must follow the same physical vertex after reversal"
                );
            }
        }
    }
}
