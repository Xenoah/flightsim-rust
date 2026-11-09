// Original illustrative architecture. These are not surveyed facades.
#import bevy_pbr::{
    pbr_fragment::pbr_input_from_standard_material,
    pbr_functions::alpha_discard,
    decal::clustered::apply_decals,
}
#ifdef PREPASS_PIPELINE
#import bevy_pbr::{
    prepass_io::{VertexOutput, FragmentOutput},
    pbr_deferred_functions::deferred_output,
}
#else
#import bevy_pbr::{
    forward_io::{VertexOutput, FragmentOutput},
    pbr_functions::{apply_pbr_lighting, main_pass_post_lighting_processing},
    pbr_types::STANDARD_MATERIAL_FLAGS_UNLIT_BIT,
}
#endif
@group(#{MATERIAL_BIND_GROUP}) @binding(100)
var<uniform> strength: vec4<f32>;

// Pure surface functions. No clock, origin, scene allocation or variable loops.
struct Surface {
    color: vec3<f32>,
    roughness: f32,
}

fn coverage(p: vec2<f32>, lo: vec2<f32>, hi: vec2<f32>, aa: vec2<f32>) -> f32 {
    let a = smoothstep(lo - aa, lo + aa, p);
    let b = 1.0 - smoothstep(hi - aa, hi + aa, p);
    return a.x * a.y * b.x * b.y;
}

fn cell_hash(cell: vec2<i32>, seed: u32) -> f32 {
    var h = u32(cell.x) * 1597334677u + u32(cell.y) * 3812015801u + seed * 2798796415u;
    h = (h ^ (h >> 16u)) * 2246822519u;
    return f32(h & 65535u) / 65535.0;
}

fn building_surface(uv: vec2<f32>, descriptor: vec2<f32>, base: vec3<f32>,
                    dx: vec2<f32>, dy: vec2<f32>) -> Surface {
    // A conservative pixel footprint, including diagonal/grazing directions.
    let footprint = sqrt(dot(dx, dx) + dot(dy, dy));
    let resolved = 1.0 - smoothstep(0.25, 1.25, footprint);
    let kind = floor(abs(descriptor.x));
    let seed = u32(round(fract(abs(descriptor.x)) * 256.0));
    let height = max(descriptor.y, 1.0);
    var surface = Surface(base, 0.94);
    if descriptor.x > 0.0 {
        let floor_height = height / max(floor(height / 3.2), 1.0);
        let pitch = vec2<f32>(select(3.4, 4.2, kind == 3.0), floor_height);
        let grid = uv / pitch;
        let cell = floor(grid);
        let p = fract(grid);
        let aa = max((abs(dx) + abs(dy)) / pitch, vec2<f32>(0.001));
        let ribbon = kind == 3.0;
        let pane = coverage(p, vec2<f32>(select(0.19, 0.06, ribbon), 0.29),
                              vec2<f32>(select(0.81, 0.94, ribbon), 0.79), aa);
        let variation = cell_hash(vec2<i32>(cell), seed);
        let glass = mix(vec3<f32>(0.035, 0.073, 0.095), vec3<f32>(0.14, 0.20, 0.23), variation);
        let in_wall = smoothstep(0.1, 0.4, uv.y) * (1.0 - smoothstep(height - 0.45, height - 0.15, uv.y));
        let panes = pane * in_wall;
        // Fade toward the area average, not a bright blank wall. No subpixel
        // checkerboards remain at altitude. Close mullions fade earlier.
        let mean_glass = vec3<f32>(0.0875, 0.1365, 0.1625);
        let average = mix(base, mean_glass, select(0.31, 0.44, ribbon));
        var detailed = mix(base, glass, panes);
        let mullion = coverage(p, vec2<f32>(0.48, 0.29), vec2<f32>(0.52, 0.79), aa);
        let fine = 1.0 - smoothstep(0.04, 0.18, footprint);
        detailed = mix(detailed, base * 0.72, mullion * in_wall * fine);
        let floor_band = 1.0 - smoothstep(0.018, 0.018 + aa.y, min(p.y, 1.0 - p.y));
        detailed *= 1.0 - 0.15 * floor_band;
        // A light cornice and darker plinth clarify roof and ground boundaries;
        // these only shade existing walls and never extend their silhouette.
        let cornice = smoothstep(height - 0.42, height - 0.20, uv.y);
        detailed = mix(detailed, base * 1.14, cornice);
        detailed *= mix(0.72, 1.0, smoothstep(0.0, 0.6, uv.y));
        surface.color = mix(average, detailed, resolved);
        surface.roughness = mix(0.78, mix(0.94, 0.36, panes), resolved);
    } else if descriptor.x < 0.0 {
        // Roof-only joints: tile/slate, standing seams or broad felt panels.
        let pitch = select(vec2<f32>(0.65, 0.36), vec2<f32>(1.1, 5.0), kind == 2.0);
        let scale = select(pitch, vec2<f32>(3.0, 4.0), kind == 3.0);
        let grid = uv / scale;
        let aa = max((abs(dx) + abs(dy)) / scale, vec2<f32>(0.001));
        let p = fract(grid);
        let joint = 1.0 - coverage(p, vec2<f32>(0.04), vec2<f32>(0.96), aa);
        let tile = cell_hash(vec2<i32>(floor(grid)), seed);
        // Broad roof panels stay legible longer than individual slate joints.
        // Filter in their own cell units, still using the full projected pixel.
        let cell_dx = dx / scale;
        let cell_dy = dy / scale;
        let cell_footprint = sqrt(dot(cell_dx, cell_dx) + dot(cell_dy, cell_dy));
        let fine = 1.0 - smoothstep(0.12, 0.48, cell_footprint);
        surface.color = base * (1.0 + fine * (0.12 * (tile - 0.5) - 0.22 * joint));
    }
    return surface;
}

@fragment
fn fragment(in: VertexOutput, @builtin(front_facing) is_front: bool) -> FragmentOutput {
    var pbr_input = pbr_input_from_standard_material(in, is_front);
#ifdef VERTEX_UVS_A
#ifdef VERTEX_UVS_B
    // Derivatives must be evaluated before surface-dependent branching. Zero
    // descriptors (vegetation/roads/land) retain the original PBR material.
    let dx = dpdx(in.uv);
    let dy = dpdy(in.uv);
    let surface = building_surface(in.uv, in.uv_b, pbr_input.material.base_color.rgb, dx, dy);
    pbr_input.material.base_color = vec4<f32>(mix(pbr_input.material.base_color.rgb, surface.color, strength.x), pbr_input.material.base_color.a);
    pbr_input.material.perceptual_roughness = mix(pbr_input.material.perceptual_roughness, surface.roughness, strength.x);
#endif
#endif
    pbr_input.material.base_color = alpha_discard(pbr_input.material, pbr_input.material.base_color);
    apply_decals(&pbr_input);
#ifdef PREPASS_PIPELINE
    let out = deferred_output(in, pbr_input);
#else
    var out: FragmentOutput;
    if (pbr_input.material.flags & STANDARD_MATERIAL_FLAGS_UNLIT_BIT) == 0u {
        out.color = apply_pbr_lighting(pbr_input);
    } else {
        out.color = pbr_input.material.base_color;
    }
    out.color = main_pass_post_lighting_processing(pbr_input, out.color);
#endif
    return out;
}
