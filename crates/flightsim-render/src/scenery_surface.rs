//! Original building surface artwork, evaluated on the existing opaque mesh.
//! Per-face metre coordinates and stable source-ID styles survive rebasing and
//! revisits. No textures, extra lights, geometry, network or simulation state.

use bevy::{
    asset::{load_internal_asset, uuid_handle},
    pbr::{ExtendedMaterial, MaterialExtension},
    prelude::*,
    render::render_resource::AsBindGroup,
    shader::ShaderRef,
};

const SHADER: Handle<Shader> = uuid_handle!("9440a02d-b25e-4eac-a372-517c7a79482b");

/// Shared opaque scenery material. Unmarked surfaces retain ordinary PBR.
pub type SceneryMaterial = ExtendedMaterial<StandardMaterial, ScenerySurface>;

/// Embedded artwork, with no dependency on external image assets.
#[derive(Asset, AsBindGroup, Reflect, Debug, Clone, PartialEq)]
pub struct ScenerySurface {
    #[uniform(100)]
    strength: Vec4,
}

impl Default for ScenerySurface {
    fn default() -> Self {
        Self {
            strength: Vec4::ONE,
        }
    }
}

impl MaterialExtension for ScenerySurface {
    fn fragment_shader() -> ShaderRef {
        SHADER.into()
    }

    fn deferred_fragment_shader() -> ShaderRef {
        SHADER.into()
    }
}

/// Register after Bevy rendering, before scenery materials are created.
#[derive(Debug, Default)]
pub struct ScenerySurfacePlugin;

impl Plugin for ScenerySurfacePlugin {
    fn build(&self, app: &mut App) {
        load_internal_asset!(app, SHADER, "scenery_surface.wgsl", Shader::from_wgsl);
        app.add_plugins(MaterialPlugin::<SceneryMaterial>::default());
    }
}

#[cfg(test)]
mod tests {
    #[test]
    fn actual_surface_math_is_valid_wgsl() {
        let source = include_str!("scenery_surface.wgsl");
        let start = source.find("// Pure surface functions").unwrap();
        let end = source.find("@fragment").unwrap();
        let module = naga::front::wgsl::parse_str(&source[start..end]).unwrap();
        naga::valid::Validator::new(
            naga::valid::ValidationFlags::all(),
            naga::valid::Capabilities::all(),
        )
        .validate(&module)
        .unwrap();
    }
}
