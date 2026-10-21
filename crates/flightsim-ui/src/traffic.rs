//! App-fed traffic presentation. No network or input sibling dependency.

use bevy::{ecs::system::SystemParam, prelude::*};

use crate::InputDiagnosticsPanel;

/// App supplies source, callsign, relative bearing/range/height and stale status.
#[derive(Resource, Debug, Clone, Default)]
pub struct TrafficPanel {
    pub visible: bool,
    pub text: String,
}

/// Includes the source/header lines. Longer lists show an explicit overflow
/// summary rather than silently rendering offscreen; publish nearest traffic first.
pub const TRAFFIC_PANEL_MAX_LINES: usize = 14;

#[derive(Component, Debug)]
pub struct TrafficDisplay;

#[derive(Component, Debug)]
pub struct TrafficRoot;

/// Shared read-only eligibility for compact traffic, help and pause reference.
/// Missing host state is not proof that Esc can open a complete reference.
#[derive(SystemParam)]
#[doc(hidden)]
pub struct TrafficLayoutContext<'w, 's> {
    state: Option<Res<'w, crate::HudState>>,
    replay: Option<Res<'w, crate::ReplayStatus>>,
    crash: Option<Res<'w, crate::CrashNotice>>,
    paused: Option<Res<'w, crate::Paused>>,
    traffic: Option<Res<'w, TrafficPanel>>,
    diagnostics: Option<Res<'w, InputDiagnosticsPanel>>,
    scale: Option<Res<'w, bevy::ui::UiScale>>,
    cameras: Query<'w, 's, &'static Camera>,
    references: Query<'w, 's, Entity, With<crate::HudReference>>,
    help: Query<'w, 's, Entity, With<crate::HudHelp>>,
    pause_reference: Query<'w, 's, Entity, With<crate::pause::PauseReference>>,
    inline_roots: Query<'w, 's, &'static ChildOf, With<TrafficRoot>>,
}

impl std::fmt::Debug for TrafficLayoutContext<'_, '_> {
    fn fmt(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        formatter
            .debug_struct("TrafficLayoutContext")
            .finish_non_exhaustive()
    }
}

impl TrafficLayoutContext<'_, '_> {
    fn eligible(&self) -> bool {
        self.references.single().ok().is_some_and(|reference| {
            self.inline_roots
                .iter()
                .any(|parent| parent.parent() == reference)
        }) && self.help.single().is_ok()
            && self.pause_reference.single().is_ok()
            && self.paused.is_some()
            && self
                .state
                .as_ref()
                .is_some_and(|state| state.view_mode == "CHASE")
            && self.replay.as_ref().is_some_and(|status| !status.active)
            && self
                .crash
                .as_ref()
                .is_some_and(|notice| !notice.is_crashed())
    }

    fn presented(&self) -> bool {
        self.traffic
            .as_ref()
            .is_some_and(|state| state.visible && !state.text.is_empty())
            && !self.diagnostics.as_ref().is_some_and(|panel| panel.visible)
    }

    pub(crate) fn active(&self) -> bool {
        self.eligible() && self.presented()
    }

    fn compact(&self) -> bool {
        self.cameras
            .iter()
            .filter(|camera| camera.is_active)
            .filter_map(Camera::logical_viewport_size)
            .map(|size| size / self.scale.as_ref().map_or(1.0, |scale| scale.0))
            .any(|size| size.x < 1000.0 || size.y < 720.0)
    }

    pub(crate) fn full_reference(&self) -> Option<String> {
        self.active().then(|| {
            // The live panel is deliberately summarized; Esc must retain every
            // supplied line and trailing error, not apply the old 14-row cap.
            self.traffic
                .as_ref()
                .expect("active traffic")
                .text
                .chars()
                .map(|character| {
                    if character == '\n' || (character.is_ascii() && !character.is_control()) {
                        character
                    } else {
                        '?'
                    }
                })
                .collect()
        })
    }
}

pub fn spawn_traffic_panel(
    mut commands: Commands,
    references: Query<Entity, With<crate::HudReference>>,
) {
    // Fixed roots avoid reparenting a laid-out Taffy node on a view transition.
    for parent in references.single().ok().map(Some).into_iter().chain([None]) {
        let inline = parent.is_some();
        let root = commands
            .spawn((
                BackgroundColor(Color::srgba(0.025, 0.045, 0.06, 0.87)),
                Node {
                    display: Display::None,
                    position_type: if inline {
                        PositionType::Relative
                    } else {
                        PositionType::Absolute
                    },
                    top: if inline { Val::Auto } else { px(190.0) },
                    right: if inline { Val::Auto } else { px(12.0) },
                    width: px(420.0),
                    max_width: if inline { percent(100.0) } else { Val::Auto },
                    min_width: if inline { px(0.0) } else { Val::Auto },
                    flex_direction: if inline {
                        FlexDirection::Column
                    } else {
                        FlexDirection::Row
                    },
                    flex_shrink: if inline { 0.0 } else { 1.0 },
                    padding: UiRect::all(px(10.0)),
                    ..default()
                },
                GlobalZIndex(5),
                Visibility::Hidden,
                TrafficRoot,
                Name::new("traffic panel"),
            ))
            .with_children(|panel| {
                panel.spawn((
                    Text::new(""),
                    TextFont {
                        font_size: 13.0,
                        ..default()
                    },
                    TextColor(Color::srgb(0.80, 0.94, 1.0)),
                    if inline {
                        TextLayout::default().with_linebreak(bevy::text::LineBreak::WordOrCharacter)
                    } else {
                        TextLayout::default()
                    },
                    Node {
                        width: if inline { Val::Auto } else { percent(100.0) },
                        min_width: if inline { px(0.0) } else { Val::Auto },
                        flex_shrink: if inline { 0.0 } else { 1.0 },
                        align_self: if inline {
                            AlignSelf::Stretch
                        } else {
                            AlignSelf::Auto
                        },
                        ..default()
                    },
                    TrafficDisplay,
                ));
            })
            .id();
        if let Some(parent) = parent {
            commands.entity(parent).insert_children(0, &[root]);
        }
    }
}

/// Keep externally supplied callsigns compatible with the bundled UI font and
/// bound the panel's footprint. The app retains the full underlying information.
#[must_use]
pub fn traffic_display_text(text: &str) -> String {
    let lines: Vec<_> = text.lines().collect();
    let visible = if lines.len() > TRAFFIC_PANEL_MAX_LINES {
        TRAFFIC_PANEL_MAX_LINES - 1
    } else {
        lines.len()
    };
    let mut output = Vec::with_capacity(TRAFFIC_PANEL_MAX_LINES);
    for line in lines.iter().take(visible) {
        let mut line: String = line
            .chars()
            .map(|character| {
                if character.is_ascii() && !character.is_control() {
                    character
                } else {
                    '?'
                }
            })
            .collect();
        if line.len() > 56 {
            line.truncate(53);
            line.push_str("...");
        }
        output.push(line);
    }
    if lines.len() > visible {
        output.push(format!("... {} more lines", lines.len() - visible));
    }
    output.join("\n")
}

fn ascii_line(line: &str) -> String {
    let mut line: String = line
        .chars()
        .take(57)
        .map(|character| {
            if character.is_ascii() && !character.is_control() {
                character
            } else {
                '?'
            }
        })
        .collect();
    if line.len() > 56 {
        line.truncate(53);
        line.push_str("...");
    }
    line
}

fn bounded_live_traffic_text(text: &str, budget: usize) -> String {
    let lines: Vec<_> = text.lines().collect();
    if lines.len() <= budget {
        return lines
            .into_iter()
            .map(ascii_line)
            .collect::<Vec<_>>()
            .join("\n");
    }
    let error = lines.last().filter(|line| line.starts_with("ERROR"));
    if budget == 1 {
        let header = ascii_line(lines[0]);
        let mut source = header
            .split_whitespace()
            .next()
            .unwrap_or("TRAFFIC")
            .to_owned();
        if source.len() > 9 {
            source.truncate(6);
            source.push_str("...");
        }
        return format!(
            "{source} | {}+{} lines (Esc)",
            if error.is_some() { "ERROR; " } else { "" },
            lines.len() - 1
        );
    }
    let visible = budget - 1 - usize::from(error.is_some());
    let mut output: Vec<_> = lines
        .iter()
        .take(visible)
        .map(|line| ascii_line(line))
        .collect();
    output.push(format!(
        "... {} more lines (Esc)",
        lines.len() - visible - usize::from(error.is_some())
    ));
    if let Some(error) = error {
        output.push(ascii_line(error));
    }
    output.join("\n")
}

pub fn update_traffic_panel(
    context: TrafficLayoutContext,
    mut roots: Query<(&mut Visibility, &mut Node, Option<&ChildOf>), With<TrafficRoot>>,
    mut displays: Query<&mut Text, With<TrafficDisplay>>,
) {
    let inline = context.eligible();
    let compact = inline && context.compact();
    for (mut visibility, mut node, parent) in &mut roots {
        let visible = context.presented() && (parent.is_some() == inline);
        *visibility = if visible {
            Visibility::Inherited
        } else {
            Visibility::Hidden
        };
        node.display = if visible {
            Display::Flex
        } else {
            Display::None
        };
        node.padding = UiRect::axes(
            px(10.0),
            px(if compact && parent.is_some() {
                0.0
            } else {
                10.0
            }),
        );
        node.margin.bottom = px(if parent.is_some() && !compact {
            8.0
        } else {
            0.0
        });
    }
    if let Some(state) = context.traffic.as_ref().filter(|_| context.presented()) {
        let desired = if inline {
            bounded_live_traffic_text(&state.text, if compact { 1 } else { 8 })
        } else {
            traffic_display_text(&state.text)
        };
        for mut text in &mut displays {
            if text.as_str() != desired {
                **text = desired.clone();
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn traffic_is_hidden_by_default() {
        assert!(!TrafficPanel::default().visible);
    }

    #[test]
    fn traffic_stays_ascii_and_reports_overflow() {
        let text = format!("SYNTHETIC 日本\n{}", "A".repeat(90));
        let output = traffic_display_text(&text);
        assert!(output.is_ascii());
        assert!(output.lines().all(|line| line.len() <= 56));
        let output = traffic_display_text(&["aircraft"; 30].join("\n"));
        assert_eq!(output.lines().count(), TRAFFIC_PANEL_MAX_LINES);
        assert!(output.ends_with("17 more lines"));
    }

    #[test]
    fn live_summary_preserves_error_and_accounts_for_hidden_lines() {
        let text = format!(
            "SYNTHETIC\n{}\nERROR connection unavailable",
            (1..=20)
                .map(|index| format!("TRAFFIC{index:02} 090deg 2nm +500ft"))
                .collect::<Vec<_>>()
                .join("\n")
        );
        let short = bounded_live_traffic_text(&text, 1);
        assert_eq!(short, "SYNTHETIC | ERROR; +21 lines (Esc)");
        let full = bounded_live_traffic_text(&text, 8);
        assert_eq!(full.lines().count(), 8);
        assert!(full.contains("... 15 more lines (Esc)"));
        assert!(full.ends_with("ERROR connection unavailable"));
    }

    #[test]
    fn live_summary_budget_and_ascii_bounds_hold_at_boundary() {
        for count in [1, 8, 9, 14, 30] {
            let text = (0..count)
                .map(|_| format!("{}日本\t", "A".repeat(90)))
                .collect::<Vec<_>>()
                .join("\n");
            for budget in [1, 8] {
                let output = bounded_live_traffic_text(&text, budget);
                assert!(output.is_ascii());
                assert!(output.lines().count() <= budget);
                assert!(output.lines().all(|line| line.len() <= 56));
                if count > budget {
                    assert!(output.contains("(Esc)"));
                }
            }
        }
    }

    #[test]
    fn controller_diagnostics_take_priority_without_erasing_traffic() {
        let mut app = App::new();
        app.init_resource::<TrafficPanel>()
            .init_resource::<InputDiagnosticsPanel>()
            .add_systems(Update, update_traffic_panel);
        let root = app
            .world_mut()
            .spawn((Visibility::Hidden, Node::default(), TrafficRoot))
            .id();
        let entity = app.world_mut().spawn((Text::new(""), TrafficDisplay)).id();
        *app.world_mut().resource_mut::<TrafficPanel>() = TrafficPanel {
            visible: true,
            text: "SYNTHETIC\nTEST01 090deg 2nm +500ft".into(),
        };
        app.update();
        assert_eq!(
            app.world().get::<Visibility>(root),
            Some(&Visibility::Inherited)
        );
        app.world_mut()
            .resource_mut::<InputDiagnosticsPanel>()
            .visible = true;
        app.update();
        assert_eq!(
            app.world().get::<Visibility>(root),
            Some(&Visibility::Hidden)
        );
        app.world_mut()
            .resource_mut::<InputDiagnosticsPanel>()
            .visible = false;
        app.update();
        assert_eq!(
            app.world().get::<Visibility>(root),
            Some(&Visibility::Inherited)
        );
        assert!(
            app.world()
                .get::<Text>(entity)
                .expect("text")
                .contains("TEST01")
        );
    }
}
