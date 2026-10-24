#!/usr/bin/env python3
"""Read-only, separately selected analytical Swift build-evidence auditor.

This tool never builds, stages, runs an executable, approves rights or publishes.
A passing audit is a build-evidence result; all native/bundle/release gates remain
required and unexecuted. See docs/release/analytical-swift-recipe.md.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import tomllib
from pathlib import Path
import re
import sys
import tempfile


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


tone = load('analytical_swift_tone', 'check-tonemapping-build.py')
candidate = load('analytical_swift_ordinary', 'check-swift-windows-candidate.py')
collector = load('analytical_swift_notices', 'collect-dependency-notices.py')
readiness = load('analytical_swift_readiness', 'check-commercial-readiness.py')
require, digest = tone.require, tone.digest
IDENTITY = tone.ANALYTICAL_SWIFT_RECIPE
TARGET, TOOLCHAIN = candidate.TARGET, candidate.TOOLCHAIN
FEATURES = ['analytic-tonemapping', 'commercial-staging']
CONTRACT = 'scripts/analytical-swift-source-contract.json'
SOURCE_ADMISSION = 'analytical-swift-alpha27-version-source-admission-v1'
SOURCE_RECIPE = tone.TWO_LUT_SOURCE
SOURCE_PATHS = {
    'Cargo.toml', 'Cargo.lock', 'crates/flightsim-app/Cargo.toml',
    'crates/flightsim-render/Cargo.toml', 'crates/flightsim-app/src/main.rs',
    'crates/flightsim-app/src/distribution.rs', 'crates/flightsim-render/src/lib.rs',
    'crates/flightsim-render/src/tonemapping.rs',
    'crates/flightsim-render/tests/tonemapping_modes.rs',
    'scripts/check-analytical-swift-recipe.py', 'scripts/check-tonemapping-build.py',
    'scripts/collect-dependency-notices.py', 'scripts/check-commercial-readiness.py',
    # Native toolchain/linker observations rely on this bounded collector and
    # its exact-output, ambiguity, origin and closed-schema witnesses.
    'scripts/collect-analytical-runtime-facts.py',
    'scripts/tests/test_analytical_runtime_facts.py',
    'scripts/check-swift-windows-candidate.py', 'scripts/stage-commercial-candidate.py',
    'scripts/check-release-authorization.py', 'scripts/replay-candidate-contract.json',
    'scripts/tests/test_analytical_swift_recipe.py', 'scripts/tests/test_tonemapping_build.py',
    'docs/release/asset-rights-manifest.json', 'docs/release/dependency-notice-supplements.json',
    'docs/release/analytical-swift-recipe.md',
    'scripts/tonemapping-two-lut-source.json', 'docs/two-lut-build-audit.md',
    'scripts/ci-tonemapping.py', 'scripts/tests/test_ci_tonemapping.py',
    'scripts/tests/test_full_source_admission.py',
    'scripts/tests/test_swift_windows_candidate.py',
    'scripts/tests/test_filmic_asset_integration.py',
    'scripts/tests/test_release_authorization.py',
    'scripts/tests/test_historical_release_copy_plan.py',
    '.github/workflows/ci.yml',
    'docs/release/full-two-aircraft-source-admission.md',
    'scripts/tests/test_component_terms_source_admission.py',
    'scripts/tests/test-component-terms-dialog.ps1',
    'docs/qa/component-terms-source-bindings-2026-10-09.md',
    'scripts/tests/test_terrain_centroid_source_admission.py',
    'docs/qa/terrain-centroid-source-bindings-2026-10-09.md',
    'scripts/tests/test_terrain_stitch_source_admission.py',
    'scripts/tests/test_alpha22_version_source_admission.py',
    'scripts/tests/test_cockpit_source_admission.py',
    'scripts/tests/test_alpha23_version_source_admission.py',
    'scripts/tests/test_alpha24_version_source_admission.py',
    'scripts/tests/test_cockpit_variant_source_admission.py',
    'scripts/tests/test_dependency_notice_ordering.py',
    'docs/qa/dependency-notice-ordering-2026-10-10.md',
    'docs/qa/terrain-stitch-source-bindings-2026-10-09.md',
    'docs/adr/0032-terrain-three-source-corners.md',
} | candidate.COMPONENT_TERMS_SOURCE_PATHS
# A separate tooling-only layer preserves the exact alpha.24 runtime migration.
# The historical workflow is complete: only this job's 30 -> 45 minute budget
# may change. All tests, commands, permissions and other jobs remain byte-exact.
CI_TIMEOUT_MIGRATION_PATH = 'scripts/ci-timeout-source-migration.json'
CI_TIMEOUT_MIGRATION_SHA256 = '33375880cd5a90b934914464d2ed415421378698879d3993193f2931ba93bebc'
CI_TIMEOUT_WORKFLOW_PATH = '.github/workflows/ci.yml'
CI_TIMEOUT_HISTORY_PATH = 'scripts/history/c84b8aa-ci.yml'
CI_TIMEOUT_PREVIOUS_SHA256 = '9018bf9b4a64d7a68d007a2000a7cdf45439ebe92fb16c42c4d0aab9f670d6dd'
CI_TIMEOUT_CURRENT_SHA256 = '19ff459cddeb90a060d3bb254f5346bb46b9c070d578f0e5973735304a35dd91'
CI_TIMEOUT_BASE_CONTRACT_PATH = 'scripts/history/c84b8aa-analytical-swift-source-contract.json'
CI_TIMEOUT_BASE_CONTRACT_SHA256 = '94291d136bd71ac239f3e7e453f32f4870dd3421ed636c8f77800b4f4f7bdadb'
CI_TIMEOUT_BASE_SOURCE_PATHS = frozenset(SOURCE_PATHS)
CI_TIMEOUT_SOURCE_PATHS = frozenset({
    CI_TIMEOUT_MIGRATION_PATH, CI_TIMEOUT_HISTORY_PATH, CI_TIMEOUT_BASE_CONTRACT_PATH,
    'scripts/tests/test_ci_timeout_source_admission.py',
})
# Only the auditor, its bound documentation, and current count/identity assertions
# are rebound alongside the sole workflow field. Runtime and release gates do not move.
CI_TIMEOUT_REBOUND_PATHS = frozenset({
    CI_TIMEOUT_WORKFLOW_PATH, 'scripts/check-analytical-swift-recipe.py',
    'docs/release/full-two-aircraft-source-admission.md',
    'scripts/tests/test_alpha23_version_source_admission.py',
    'scripts/tests/test_alpha24_version_source_admission.py',
    'scripts/tests/test_analytical_swift_recipe.py',
    'scripts/tests/test_cockpit_source_admission.py',
    'scripts/tests/test_cockpit_variant_source_admission.py',
    'scripts/tests/test_component_terms_source_admission.py',
    'scripts/tests/test_terrain_stitch_source_admission.py',
})
SOURCE_PATHS |= CI_TIMEOUT_SOURCE_PATHS

# Keep the published CI-only proof intact under the runtime successor.
SWIFT_FORWARD_BASE_CONTRACT_PATH = 'scripts/history/4f385e1-analytical-swift-source-contract.json'
SWIFT_FORWARD_BASE_SOURCE_PATHS = frozenset(SOURCE_PATHS)
SWIFT_FORWARD_SOURCE_PATHS = frozenset({'scripts/tests/test_swift_forward_visibility_source_admission.py'})
SWIFT_FORWARD_REBOUND_PATHS = frozenset({
    'scripts/replay-candidate-contract.json', 'scripts/check-swift-windows-candidate.py',
    'scripts/check-analytical-swift-recipe.py',
    'docs/release/full-two-aircraft-source-admission.md',
    'scripts/tests/test_swift_windows_candidate.py', 'scripts/tests/test_full_source_admission.py',
    'scripts/tests/test_analytical_swift_recipe.py',
    'scripts/tests/test_alpha23_version_source_admission.py',
    'scripts/tests/test_alpha24_version_source_admission.py',
    'scripts/tests/test_cockpit_source_admission.py',
    'scripts/tests/test_cockpit_variant_source_admission.py',
    'scripts/tests/test_component_terms_source_admission.py',
    'scripts/tests/test_terrain_stitch_source_admission.py',
    'scripts/tests/test_ci_timeout_source_admission.py',
})
SOURCE_PATHS |= SWIFT_FORWARD_SOURCE_PATHS
SWIFT_FORWARD_ADMISSION_SOURCE_PATHS = frozenset(SOURCE_PATHS)
ALPHA25_BASE_CONTRACT_PATH = 'scripts/history/754bad8-analytical-swift-source-contract.json'
ALPHA25_SOURCE_PATHS = frozenset({'scripts/tests/test_alpha25_version_source_admission.py'})
ALPHA25_REBOUND_PATHS = frozenset({
    'Cargo.toml', 'Cargo.lock', 'scripts/replay-candidate-contract.json',
    'scripts/check-swift-windows-candidate.py', 'scripts/check-analytical-swift-recipe.py',
    'docs/release/full-two-aircraft-source-admission.md',
    'scripts/tests/test_swift_windows_candidate.py', 'scripts/tests/test_full_source_admission.py',
    'scripts/tests/test_analytical_swift_recipe.py',
    'scripts/tests/test_alpha23_version_source_admission.py',
    'scripts/tests/test_alpha24_version_source_admission.py',
    'scripts/tests/test_cockpit_source_admission.py',
    'scripts/tests/test_cockpit_variant_source_admission.py',
    'scripts/tests/test_component_terms_source_admission.py',
    'scripts/tests/test_terrain_stitch_source_admission.py',
    'scripts/tests/test_swift_forward_visibility_source_admission.py',
})
SOURCE_PATHS |= ALPHA25_SOURCE_PATHS
ALPHA25_ADMISSION_SOURCE_PATHS = frozenset(SOURCE_PATHS)
CHASE_HUD_BASE_CONTRACT_PATH = 'scripts/history/5082b772-analytical-swift-source-contract.json'
CHASE_HUD_SOURCE_PATHS = frozenset({'scripts/tests/test_chase_hud_source_admission.py'})
CHASE_HUD_REBOUND_PATHS = frozenset({'docs/release/full-two-aircraft-source-admission.md',
 'scripts/check-analytical-swift-recipe.py',
 'scripts/check-swift-windows-candidate.py',
 'scripts/replay-candidate-contract.json',
 'scripts/tests/test_alpha22_version_source_admission.py',
 'scripts/tests/test_alpha23_version_source_admission.py',
 'scripts/tests/test_alpha24_version_source_admission.py',
 'scripts/tests/test_alpha25_version_source_admission.py',
 'scripts/tests/test_analytical_swift_recipe.py',
 'scripts/tests/test_cockpit_source_admission.py',
 'scripts/tests/test_cockpit_variant_source_admission.py',
 'scripts/tests/test_component_terms_source_admission.py',
 'scripts/tests/test_full_source_admission.py',
 'scripts/tests/test_swift_forward_visibility_source_admission.py',
 'scripts/tests/test_swift_windows_candidate.py',
 'scripts/tests/test_terrain_stitch_source_admission.py'})
SOURCE_PATHS |= CHASE_HUD_SOURCE_PATHS
CHASE_HUD_ADMISSION_SOURCE_PATHS = frozenset(SOURCE_PATHS)

# Keep the merged HUD proof intact. This successor changes only the workspace
# version and the bounded source-auditor/documentation/test bindings below.
ALPHA26_BASE_CONTRACT_PATH = 'scripts/history/e2e23ce-analytical-swift-source-contract.json'
ALPHA26_SOURCE_PATHS = frozenset({'scripts/tests/test_alpha26_version_source_admission.py'})
ALPHA26_REBOUND_PATHS = frozenset({
    'Cargo.toml', 'Cargo.lock',
    'docs/release/full-two-aircraft-source-admission.md',
    'scripts/check-analytical-swift-recipe.py',
    'scripts/check-swift-windows-candidate.py',
    'scripts/replay-candidate-contract.json',
    'scripts/tests/test_alpha23_version_source_admission.py',
    'scripts/tests/test_alpha24_version_source_admission.py',
    'scripts/tests/test_alpha25_version_source_admission.py',
    'scripts/tests/test_analytical_swift_recipe.py',
    'scripts/tests/test_chase_hud_source_admission.py',
    'scripts/tests/test_cockpit_source_admission.py',
    'scripts/tests/test_cockpit_variant_source_admission.py',
    'scripts/tests/test_component_terms_source_admission.py',
    'scripts/tests/test_full_source_admission.py',
    'scripts/tests/test_swift_forward_visibility_source_admission.py',
    'scripts/tests/test_swift_windows_candidate.py',
    'scripts/tests/test_terrain_stitch_source_admission.py',
})
SOURCE_PATHS |= ALPHA26_SOURCE_PATHS
ALPHA26_ADMISSION_SOURCE_PATHS = frozenset(SOURCE_PATHS)

# Preserve the complete 65-input public alpha.26 proof. This outer tooling-only
# layer changes one CI ceiling; it grants no runtime or publication acceptance.
CI60_MIGRATION_PATH = 'scripts/ci60-source-migration.json'
CI60_MIGRATION_SHA256 = '5b663e654ef105f768fbf96c5ff8f93281cc943a87f6d0367c484b557bfa9ab2'
CI60_HISTORY_PATH = 'scripts/history/2eb36242-ci.yml'
CI60_PREVIOUS_SHA256 = '19ff459cddeb90a060d3bb254f5346bb46b9c070d578f0e5973735304a35dd91'
CI60_CURRENT_SHA256 = 'b99cc0a5a1fb8a102bd676c0638a37483ee0aab0511ab551133c2d7d4632587c'
CI60_BASE_CONTRACT_PATH = 'scripts/history/2eb36242-analytical-swift-source-contract.json'
CI60_BASE_CONTRACT_SHA256 = '35b23ccd283b86051ef84c9fc38ff6d448465e699b06d8f6bb5810bf01503ace'
CI60_SOURCE_PATHS = frozenset({
    CI60_MIGRATION_PATH, CI60_HISTORY_PATH, CI60_BASE_CONTRACT_PATH,
    'scripts/tests/test_ci60_source_admission.py',
})
CI60_REBOUND_PATHS = frozenset({
    CI_TIMEOUT_WORKFLOW_PATH, 'scripts/check-analytical-swift-recipe.py',
    'docs/release/full-two-aircraft-source-admission.md',
    'scripts/tests/test_alpha23_version_source_admission.py',
    'scripts/tests/test_alpha24_version_source_admission.py',
    'scripts/tests/test_alpha25_version_source_admission.py',
    'scripts/tests/test_alpha26_version_source_admission.py',
    'scripts/tests/test_analytical_swift_recipe.py',
    'scripts/tests/test_chase_hud_source_admission.py',
    'scripts/tests/test_ci_timeout_source_admission.py',
    'scripts/tests/test_cockpit_source_admission.py',
    'scripts/tests/test_cockpit_variant_source_admission.py',
    'scripts/tests/test_component_terms_source_admission.py',
    'scripts/tests/test_swift_forward_visibility_source_admission.py',
    'scripts/tests/test_terrain_stitch_source_admission.py',
})
SOURCE_PATHS |= CI60_SOURCE_PATHS
CI60_ADMISSION_SOURCE_PATHS = frozenset(SOURCE_PATHS)
URBAN_BASE_CONTRACT_PATH = 'scripts/history/fc2ca797-scripts-analytical-swift-source-contract.json'
URBAN_SOURCE_PATHS = frozenset({'scripts/tests/test_urban_source_admission.py'})
URBAN_REBOUND_PATHS = frozenset(['docs/release/full-two-aircraft-source-admission.md',
 'scripts/check-analytical-swift-recipe.py',
 'scripts/check-swift-windows-candidate.py',
 'scripts/replay-candidate-contract.json',
 'scripts/tests/test_alpha22_version_source_admission.py',
 'scripts/tests/test_alpha23_version_source_admission.py',
 'scripts/tests/test_alpha24_version_source_admission.py',
 'scripts/tests/test_alpha25_version_source_admission.py',
 'scripts/tests/test_alpha26_version_source_admission.py',
 'scripts/tests/test_analytical_swift_recipe.py',
 'scripts/tests/test_chase_hud_source_admission.py',
 'scripts/tests/test_ci60_source_admission.py',
 'scripts/tests/test_cockpit_source_admission.py',
 'scripts/tests/test_cockpit_variant_source_admission.py',
 'scripts/tests/test_component_terms_source_admission.py',
 'scripts/tests/test_full_source_admission.py',
 'scripts/tests/test_swift_forward_visibility_source_admission.py',
 'scripts/tests/test_swift_windows_candidate.py',
 'scripts/tests/test_terrain_centroid_source_admission.py',
 'scripts/tests/test_terrain_stitch_source_admission.py'])
SOURCE_PATHS |= URBAN_SOURCE_PATHS
URBAN_ADMISSION_SOURCE_PATHS = frozenset(SOURCE_PATHS)
ALPHA27_BASE_CONTRACT_PATH = 'scripts/history/de5d43ab-analytical-swift-source-contract.json'
ALPHA27_SOURCE_PATHS = frozenset({'scripts/tests/test_alpha27_version_source_admission.py'})
ALPHA27_REBOUND_PATHS = frozenset(['Cargo.lock',
 'Cargo.toml',
 'docs/release/full-two-aircraft-source-admission.md',
 'scripts/check-analytical-swift-recipe.py',
 'scripts/check-swift-windows-candidate.py',
 'scripts/replay-candidate-contract.json',
 'scripts/tests/test_alpha23_version_source_admission.py',
 'scripts/tests/test_alpha24_version_source_admission.py',
 'scripts/tests/test_alpha25_version_source_admission.py',
 'scripts/tests/test_alpha26_version_source_admission.py',
 'scripts/tests/test_analytical_swift_recipe.py',
 'scripts/tests/test_chase_hud_source_admission.py',
 'scripts/tests/test_ci60_source_admission.py',
 'scripts/tests/test_cockpit_source_admission.py',
 'scripts/tests/test_cockpit_variant_source_admission.py',
 'scripts/tests/test_component_terms_source_admission.py',
 'scripts/tests/test_swift_forward_visibility_source_admission.py',
 'scripts/tests/test_swift_windows_candidate.py',
 'scripts/tests/test_terrain_stitch_source_admission.py',
 'scripts/tests/test_urban_source_admission.py'])
SOURCE_PATHS |= ALPHA27_SOURCE_PATHS

GATES = {
    'combined_feature_regressions': 'Combined release/MSVC app/render tests and Clippy; real render tonemapping_modes; ordinary controls and mixed/neither rejection',
    'exact_identity_and_legacy_tests': 'Existing fingerprint and three exact legacy tests, one executed passing test each under combined release/MSVC features',
    'extracted_bundle_isolation': 'Sole unchanged stager; Swift-only complete allowlist, hashes/archive/extraction, unrelated CWD and poisoned asset environment; no renamed unapproved bytes',
    'extracted_runtime_acceptance': 'Actual Swift model/7.12 m fit, decoded PNG/exit 0; absent Light exit 2; legacy mismatch exit 2; explicit no-model legacy PNG/exit 0 and partial-identity notice',
    'analytical_windows_appearance': 'Day/low sun/night, atmosphere/fog/clouds/water, cockpit/HUD, camera/map/lifecycle; accept darker Reinhard appearance',
    'dependency_and_platform_review': 'Genuine exact-inventory dependency/runtime review; constgebra/hexf unresolved; Fira, shaders, MSVC/native imports and other obligations retained',
    'publication_receipt': 'Genuine exact-inventory publication receipt; standing user publication permission is separate and is not withheld',
}


def commands(mode):
    require(mode in ('analytic', 'ordinary'), 'unknown capture mode')
    select = ['-p', 'flightsim-app']
    features = ['--no-default-features', '--features', ','.join(FEATURES)] if mode == 'analytic' else []
    metadata_features = ['--no-default-features', '--features', ','.join('flightsim-app/' + f for f in FEATURES)] if mode == 'analytic' else []
    return {
        'rustc': ['rustc', '+' + TOOLCHAIN, '-vV'],
        'graph': ['cargo', '+' + TOOLCHAIN, 'tree', '--locked', '--offline', '--target', TARGET,
                  *select, *features, '--edges', 'normal,build', '--prefix', 'none', '--format', '{p} features=[{f}]'],
        'build': ['cargo', '+' + TOOLCHAIN, 'build', '--locked', '--offline', '--release', '-j', '2',
                  '--target', TARGET, *select, *features, '--message-format=json'],
        'metadata': ['cargo', '+' + TOOLCHAIN, 'metadata', '--locked', '--offline', '--format-version', '1',
                     '--filter-platform', TARGET, *metadata_features],
    }


def recipe(source_recipe=SOURCE_RECIPE):
    return {'schema_version': 1, 'recipe': IDENTITY, 'source_recipe': source_recipe, 'status': 'prepared_unexecuted',
            'target': TARGET, 'toolchain': TOOLCHAIN, 'default_features': False,
            'features': FEATURES, 'region_downloads': False, 'release_authorized': False,
            'commands': {mode: commands(mode) for mode in ('analytic', 'ordinary')},
            'required_unexecuted_gates': GATES}


def validate_header(value, source_sha):
    expected = {key: recipe()[key] for key in ('schema_version', 'recipe', 'target', 'toolchain',
                                              'default_features', 'features', 'region_downloads', 'release_authorized')}
    require(all(value.get(k) == v for k, v in expected.items())
            and type(value.get('schema_version')) is int
            and value.get('default_features') is False and value.get('region_downloads') is False
            and value.get('release_authorized') is False,
            'wrong analytical Swift capture identity')
    require(re.fullmatch('[0-9a-f]{40}', source_sha) is not None and value.get('source_sha') == source_sha,
            'capture source differs from exact source')
    require(value.get('source_recipe') in (tone.UPSTREAM_THREE_LUT_SOURCE, SOURCE_RECIPE),
            'explicit source recipe is required')
    require(set(value.get('modes', {})) == {'analytic', 'ordinary'}, 'both isolated build captures are required')


def validate_ci_timeout_delta(previous, current):
    """Accept the complete known workflow with exactly one job-budget replacement."""
    require(isinstance(previous, bytes) and isinstance(current, bytes)
            and 0 < len(previous) <= 1024 * 1024 and 0 < len(current) <= 1024 * 1024,
            'CI timeout workflow exceeds byte boundary')
    import hashlib
    require(hashlib.sha256(previous).hexdigest() == CI_TIMEOUT_PREVIOUS_SHA256,
            'CI timeout historical workflow changed')
    before = (b'  world_source_tools:\n'
              b'    name: world source-tool boundaries\n'
              b'    runs-on: ubuntu-latest\n'
              b'    # Allow the full canonical-source mutation sweep and all schema/reference\n'
              b'    # checks to finish despite hosted-runner variability.\n'
              b'    timeout-minutes: 30\n')
    after = before.replace(b'timeout-minutes: 30', b'timeout-minutes: 45')
    require(previous.count(before) == 1 and current == previous.replace(before, after)
            and hashlib.sha256(current).hexdigest() == CI_TIMEOUT_CURRENT_SHA256,
            'CI workflow changed outside exact world_source_tools 30-to-45 budget')


def validate_ci_timeout_admission(repo, pins):
    """Keep the exact historical 30-to-45 proof; the outer layer checks live CI."""
    require(digest(repo / CI_TIMEOUT_MIGRATION_PATH) == CI_TIMEOUT_MIGRATION_SHA256
            and pins.get(CI_TIMEOUT_MIGRATION_PATH) == CI_TIMEOUT_MIGRATION_SHA256,
            'CI timeout migration changed')
    migration = json.loads((repo / CI_TIMEOUT_MIGRATION_PATH).read_text(encoding='utf-8'))
    expected = {
        'schema_version': 1, 'identity': 'analytical-swift-ci-timeout-source-migration-v1',
        'base_source': 'c84b8aa97d38250ddb1c5495e2d65e3917be8b4c',
        'base_tree': 'c9d792a5f0fc1641a6a050ce41a56f2a5b8afb2b',
        'base_source_kind': 'published-commit',
        'scope': 'source-only CI job budget; no test, native, runtime, rights or publication gate change',
        'release_authorized': False,
        'runtime_source_migration_sha256': candidate.ALPHA24_MIGRATION_SHA256,
        'base_analytical_contract': {'path': CI_TIMEOUT_BASE_CONTRACT_PATH,
                                     'sha256': CI_TIMEOUT_BASE_CONTRACT_SHA256},
        'workflow': {'path': CI_TIMEOUT_WORKFLOW_PATH, 'historical_path': CI_TIMEOUT_HISTORY_PATH,
                     'previous_sha256': CI_TIMEOUT_PREVIOUS_SHA256,
                     'sha256': CI_TIMEOUT_CURRENT_SHA256, 'job': 'world_source_tools',
                     'previous_timeout_minutes': 30, 'timeout_minutes': 45},
    }
    require(type(migration.get('schema_version')) is int
            and migration.get('release_authorized') is False and migration == expected,
            'invalid CI-only timeout migration identity or scope')
    require(digest(repo / CI_TIMEOUT_BASE_CONTRACT_PATH) == CI_TIMEOUT_BASE_CONTRACT_SHA256
            and pins.get(CI_TIMEOUT_BASE_CONTRACT_PATH) == CI_TIMEOUT_BASE_CONTRACT_SHA256,
            'CI timeout historical analytical contract changed')
    previous = json.loads((repo / CI_TIMEOUT_BASE_CONTRACT_PATH).read_text(encoding='utf-8'))
    require(previous['source_admission'] == 'analytical-swift-alpha24-version-source-admission-v1'
            and previous['source_migration_sha256'] == candidate.ALPHA24_MIGRATION_SHA256
            and previous['release_authorized'] is False
            and set(previous['source_sha256']) == CI_TIMEOUT_BASE_SOURCE_PATHS,
            'CI timeout previous analytical boundary changed')
    require(set(pins) == CI_TIMEOUT_BASE_SOURCE_PATHS | CI_TIMEOUT_SOURCE_PATHS,
            'CI timeout analytical boundary changed')
    for path, expected in previous['source_sha256'].items():
        if path not in CI_TIMEOUT_REBOUND_PATHS:
            require(pins.get(path) == expected, 'CI timeout unrelated analytical source changed: ' + path)
    validate_ci_timeout_delta((repo / CI_TIMEOUT_HISTORY_PATH).read_bytes(),
                              (repo / CI60_HISTORY_PATH).read_bytes())
    require(pins.get(CI_TIMEOUT_HISTORY_PATH) == CI_TIMEOUT_PREVIOUS_SHA256
            and pins.get(CI_TIMEOUT_WORKFLOW_PATH) == CI_TIMEOUT_CURRENT_SHA256,
            'CI timeout workflow pins changed')


def validate_swift_forward_admission(repo, pins):
    """Retain the exact published 61-input CI-only proof beneath this successor."""
    path = SWIFT_FORWARD_BASE_CONTRACT_PATH
    require(digest(repo / path) == candidate.SWIFT_FORWARD_BASE_CONTRACT_HASHES[path],
            'Swift forward visibility historical analytical contract changed')
    previous = json.loads((repo / path).read_text(encoding='utf-8'))
    require(set(previous) == {'schema_version', 'recipe', 'source_admission', 'source_recipe',
            'base_reviewed_source', 'base_reviewed_runtime_tree', 'source_migration_sha256',
            'release_authorized', 'source_sha256'}
            and type(previous['schema_version']) is int and previous['schema_version'] == 1
            and previous['recipe'] == IDENTITY and previous['source_recipe'] == SOURCE_RECIPE
            and previous['source_admission'] == 'analytical-swift-alpha24-ci-timeout-source-admission-v1'
            and previous['base_reviewed_source'] == candidate.REVIEWED_RUNTIME_SOURCE
            and previous['base_reviewed_runtime_tree'] == candidate.REVIEWED_RUNTIME_TREE
            and previous['source_migration_sha256'] == candidate.ALPHA24_MIGRATION_SHA256
            and previous['release_authorized'] is False
            and set(previous['source_sha256']) == SWIFT_FORWARD_BASE_SOURCE_PATHS,
            'invalid Swift forward visibility historical analytical contract')
    validate_ci_timeout_admission(repo, previous['source_sha256'])
    require(isinstance(pins, dict) and set(pins) == SWIFT_FORWARD_ADMISSION_SOURCE_PATHS,
            'Swift forward visibility analytical boundary changed')
    for path, expected in previous['source_sha256'].items():
        if path not in SWIFT_FORWARD_REBOUND_PATHS:
            require(pins.get(path) == expected, 'unrelated analytical input changed: ' + path)


def validate_alpha25_admission(repo, pins):
    """Retain the exact published 62-input Swift visibility proof beneath this successor."""
    path = ALPHA25_BASE_CONTRACT_PATH
    require(digest(repo / path) == candidate.ALPHA25_BASE_CONTRACT_HASHES[path],
            'alpha25 version historical analytical contract changed')
    previous = json.loads((repo / path).read_text(encoding='utf-8'))
    require(set(previous) == {'schema_version', 'recipe', 'source_admission', 'source_recipe',
            'base_reviewed_source', 'base_reviewed_runtime_tree', 'source_migration_sha256',
            'release_authorized', 'source_sha256'}
            and type(previous['schema_version']) is int and previous['schema_version'] == 1
            and previous['recipe'] == IDENTITY and previous['source_recipe'] == SOURCE_RECIPE
            and previous['source_admission'] == 'analytical-swift-forward-visibility-source-admission-v1'
            and previous['base_reviewed_source'] == candidate.REVIEWED_RUNTIME_SOURCE
            and previous['base_reviewed_runtime_tree'] == candidate.REVIEWED_RUNTIME_TREE
            and previous['source_migration_sha256'] == candidate.SWIFT_FORWARD_MIGRATION_SHA256
            and previous['release_authorized'] is False
            and set(previous['source_sha256']) == SWIFT_FORWARD_ADMISSION_SOURCE_PATHS,
            'invalid alpha25 version historical analytical contract')
    validate_swift_forward_admission(repo, previous['source_sha256'])
    require(isinstance(pins, dict) and set(pins) == ALPHA25_ADMISSION_SOURCE_PATHS,
            'alpha25 version analytical boundary changed')
    for path, expected in previous['source_sha256'].items():
        if path not in ALPHA25_REBOUND_PATHS:
            require(pins.get(path) == expected, 'unrelated analytical input changed: ' + path)


def validate_chase_hud_admission(repo, pins):
    """Retain the exact published 63-input alpha.25 proof beneath this successor."""
    path = CHASE_HUD_BASE_CONTRACT_PATH
    require(digest(repo / path) == candidate.CHASE_HUD_BASE_CONTRACT_HASHES[path],
            'chase HUD historical analytical contract changed')
    previous = json.loads((repo / path).read_text(encoding='utf-8'))
    require(set(previous) == {'schema_version', 'recipe', 'source_admission', 'source_recipe',
            'base_reviewed_source', 'base_reviewed_runtime_tree', 'source_migration_sha256',
            'release_authorized', 'source_sha256'}
            and type(previous['schema_version']) is int and previous['schema_version'] == 1
            and previous['recipe'] == IDENTITY and previous['source_recipe'] == SOURCE_RECIPE
            and previous['source_admission'] == 'analytical-swift-alpha25-version-source-admission-v1'
            and previous['base_reviewed_source'] == candidate.REVIEWED_RUNTIME_SOURCE
            and previous['base_reviewed_runtime_tree'] == candidate.REVIEWED_RUNTIME_TREE
            and previous['source_migration_sha256'] == candidate.ALPHA25_MIGRATION_SHA256
            and previous['release_authorized'] is False
            and set(previous['source_sha256']) == ALPHA25_ADMISSION_SOURCE_PATHS,
            'invalid chase HUD historical analytical contract')
    validate_alpha25_admission(repo, previous['source_sha256'])
    require(isinstance(pins, dict) and set(pins) == CHASE_HUD_ADMISSION_SOURCE_PATHS,
            'chase HUD analytical boundary changed')
    for path, expected in previous['source_sha256'].items():
        if path not in CHASE_HUD_REBOUND_PATHS:
            require(pins.get(path) == expected, 'unrelated analytical input changed: ' + path)


def validate_alpha26_admission(repo, pins):
    """Retain the exact merged 64-input HUD proof beneath the version successor."""
    path = ALPHA26_BASE_CONTRACT_PATH
    require(digest(repo / path) == candidate.ALPHA26_BASE_CONTRACT_HASHES[path],
            'alpha26 version historical analytical contract changed')
    previous = json.loads((repo / path).read_text(encoding='utf-8'))
    require(set(previous) == {'schema_version', 'recipe', 'source_admission', 'source_recipe',
            'base_reviewed_source', 'base_reviewed_runtime_tree', 'source_migration_sha256',
            'release_authorized', 'source_sha256'}
            and type(previous['schema_version']) is int and previous['schema_version'] == 1
            and previous['recipe'] == IDENTITY and previous['source_recipe'] == SOURCE_RECIPE
            and previous['source_admission'] == 'analytical-swift-chase-hud-source-admission-v1'
            and previous['base_reviewed_source'] == candidate.REVIEWED_RUNTIME_SOURCE
            and previous['base_reviewed_runtime_tree'] == candidate.REVIEWED_RUNTIME_TREE
            and previous['source_migration_sha256'] == candidate.CHASE_HUD_MIGRATION_SHA256
            and previous['release_authorized'] is False
            and set(previous['source_sha256']) == CHASE_HUD_ADMISSION_SOURCE_PATHS,
            'invalid alpha26 version historical analytical contract')
    validate_chase_hud_admission(repo, previous['source_sha256'])
    require(isinstance(pins, dict) and set(pins) == ALPHA26_ADMISSION_SOURCE_PATHS,
            'alpha26 version analytical boundary changed')
    for path, expected in previous['source_sha256'].items():
        if path not in ALPHA26_REBOUND_PATHS:
            require(pins.get(path) == expected, 'unrelated analytical input changed: ' + path)


def validate_ci60_delta(previous, current):
    """Accept only the complete public workflow's single 45-to-60 job ceiling."""
    require(isinstance(previous, bytes) and isinstance(current, bytes)
            and 0 < len(previous) <= 1024 * 1024 and 0 < len(current) <= 1024 * 1024,
            'CI60 workflow exceeds byte boundary')
    import hashlib
    require(hashlib.sha256(previous).hexdigest() == CI60_PREVIOUS_SHA256,
            'CI60 historical workflow changed')
    before = (b'  world_source_tools:\n'
              b'    name: world source-tool boundaries\n'
              b'    runs-on: ubuntu-latest\n'
              b'    # Allow the full canonical-source mutation sweep and all schema/reference\n'
              b'    # checks to finish despite hosted-runner variability.\n'
              b'    timeout-minutes: 45\n')
    after = before.replace(b'timeout-minutes: 45', b'timeout-minutes: 60')
    require(previous.count(before) == 1 and current == previous.replace(before, after)
            and hashlib.sha256(current).hexdigest() == CI60_CURRENT_SHA256,
            'CI workflow changed outside exact world_source_tools 45-to-60 budget')


def validate_ci60_admission(repo, pins):
    """Preserve all 65 prior inputs and independently bind the complete live CI."""
    require(isinstance(pins, dict) and set(pins) == CI60_ADMISSION_SOURCE_PATHS,
            'CI60 analytical boundary changed')
    require(digest(repo / CI60_MIGRATION_PATH) == CI60_MIGRATION_SHA256
            and pins[CI60_MIGRATION_PATH] == CI60_MIGRATION_SHA256,
            'CI60 migration changed')
    migration = json.loads((repo / CI60_MIGRATION_PATH).read_text(encoding='utf-8'))
    expected = {
        'schema_version': 1, 'identity': 'analytical-swift-alpha26-ci60-source-migration-v1',
        'base_source': '2eb36242cde4ccd3492b0079d4de226ee26db15e',
        'base_tree': 'f56e97232728aed82b66edb82beb7417e946c929',
        'base_source_kind': 'public-pull-request-commit',
        'scope': 'source-only CI job budget; no test, native, runtime, rights or publication gate change',
        'release_authorized': False,
        'runtime_source_migration_sha256': candidate.ALPHA26_MIGRATION_SHA256,
        'previous_ci_migration_sha256': CI_TIMEOUT_MIGRATION_SHA256,
        'base_analytical_contract': {'path': CI60_BASE_CONTRACT_PATH,
                                     'sha256': CI60_BASE_CONTRACT_SHA256},
        'workflow': {'path': CI_TIMEOUT_WORKFLOW_PATH, 'historical_path': CI60_HISTORY_PATH,
                     'previous_sha256': CI60_PREVIOUS_SHA256,
                     'sha256': CI60_CURRENT_SHA256, 'job': 'world_source_tools',
                     'previous_timeout_minutes': 45, 'timeout_minutes': 60},
    }
    require(type(migration.get('schema_version')) is int
            and migration.get('release_authorized') is False and migration == expected,
            'invalid CI60 migration identity or scope')
    require(digest(repo / CI60_BASE_CONTRACT_PATH) == CI60_BASE_CONTRACT_SHA256
            and pins[CI60_BASE_CONTRACT_PATH] == CI60_BASE_CONTRACT_SHA256,
            'CI60 historical analytical contract changed')
    previous = json.loads((repo / CI60_BASE_CONTRACT_PATH).read_text(encoding='utf-8'))
    require(set(previous) == {'schema_version', 'recipe', 'source_admission', 'source_recipe',
            'base_reviewed_source', 'base_reviewed_runtime_tree', 'source_migration_sha256',
            'release_authorized', 'source_sha256'}
            and type(previous['schema_version']) is int and previous['schema_version'] == 1
            and previous['recipe'] == IDENTITY and previous['source_recipe'] == SOURCE_RECIPE
            and previous['source_admission'] == 'analytical-swift-alpha26-version-source-admission-v1'
            and previous['base_reviewed_source'] == candidate.REVIEWED_RUNTIME_SOURCE
            and previous['base_reviewed_runtime_tree'] == candidate.REVIEWED_RUNTIME_TREE
            and previous['source_migration_sha256'] == candidate.ALPHA26_MIGRATION_SHA256
            and previous['release_authorized'] is False
            and set(previous['source_sha256']) == ALPHA26_ADMISSION_SOURCE_PATHS,
            'invalid CI60 historical analytical contract')
    validate_alpha26_admission(repo, previous['source_sha256'])
    for path, prior in previous['source_sha256'].items():
        if path not in CI60_REBOUND_PATHS:
            require(pins[path] == prior, 'CI60 unrelated analytical source changed: ' + path)
    require(pins[CI60_HISTORY_PATH] == CI60_PREVIOUS_SHA256
            and pins[CI_TIMEOUT_WORKFLOW_PATH] == CI60_CURRENT_SHA256,
            'CI60 workflow pins changed')
    validate_ci60_delta((repo / CI60_HISTORY_PATH).read_bytes(),
                       (repo / CI_TIMEOUT_WORKFLOW_PATH).read_bytes())


def validate_urban_admission(repo, pins):
    """Keep the whole CI60 proof and every unrelated analytical input exact."""
    require(isinstance(pins, dict) and set(pins) == URBAN_ADMISSION_SOURCE_PATHS,
            'urban analytical boundary changed')
    require(digest(repo / URBAN_BASE_CONTRACT_PATH)
            == candidate.URBAN_BASE_CONTRACT_HASHES[URBAN_BASE_CONTRACT_PATH],
            'urban historical analytical contract changed')
    previous = json.loads((repo / URBAN_BASE_CONTRACT_PATH).read_text(encoding='utf-8'))
    require(set(previous) == {'schema_version', 'recipe', 'source_admission', 'source_recipe',
            'base_reviewed_source', 'base_reviewed_runtime_tree', 'source_migration_sha256',
            'release_authorized', 'source_sha256'}
            and type(previous['schema_version']) is int and previous['schema_version'] == 1
            and previous['recipe'] == IDENTITY and previous['source_recipe'] == SOURCE_RECIPE
            and previous['source_admission'] == 'analytical-swift-alpha26-ci60-source-admission-v1'
            and previous['base_reviewed_source'] == candidate.REVIEWED_RUNTIME_SOURCE
            and previous['base_reviewed_runtime_tree'] == candidate.REVIEWED_RUNTIME_TREE
            and previous['source_migration_sha256'] == candidate.ALPHA26_MIGRATION_SHA256
            and previous['release_authorized'] is False
            and len(previous['source_sha256']) == 69
            and set(previous['source_sha256']) == CI60_ADMISSION_SOURCE_PATHS,
            'invalid urban historical analytical contract')
    validate_ci60_admission(repo, previous['source_sha256'])
    for path, prior in previous['source_sha256'].items():
        if path not in URBAN_REBOUND_PATHS:
            require(pins[path] == prior, 'urban unrelated analytical source changed: ' + path)


def validate_alpha27_admission(repo, pins):
    """Retain the entire 70-input urban proof and unrelated analytical bytes."""
    path = ALPHA27_BASE_CONTRACT_PATH
    require(digest(repo / path) == candidate.ALPHA27_BASE_CONTRACT_HASHES[path],
            'alpha27 historical analytical contract changed')
    previous = json.loads((repo / path).read_text(encoding='utf-8'))
    require(set(previous) == {'schema_version', 'recipe', 'source_admission', 'source_recipe',
            'base_reviewed_source', 'base_reviewed_runtime_tree', 'source_migration_sha256',
            'release_authorized', 'source_sha256'}
            and type(previous['schema_version']) is int and previous['schema_version'] == 1
            and previous['recipe'] == IDENTITY and previous['source_recipe'] == SOURCE_RECIPE
            and previous['source_admission'] == 'analytical-swift-offline-urban-source-admission-v1'
            and previous['base_reviewed_source'] == candidate.REVIEWED_RUNTIME_SOURCE
            and previous['base_reviewed_runtime_tree'] == candidate.REVIEWED_RUNTIME_TREE
            and previous['source_migration_sha256'] == candidate.URBAN_MIGRATION_SHA256
            and previous['release_authorized'] is False
            and len(previous['source_sha256']) == 70
            and set(previous['source_sha256']) == URBAN_ADMISSION_SOURCE_PATHS,
            'invalid alpha27 historical analytical contract')
    require(isinstance(pins, dict) and set(pins) == SOURCE_PATHS, 'alpha27 analytical boundary changed')
    for path, prior in previous['source_sha256'].items():
        if path not in ALPHA27_REBOUND_PATHS:
            require(pins[path] == prior, 'alpha27 unrelated analytical source changed: ' + path)
    validate_urban_admission(repo, previous['source_sha256'])


def source_evidence(repo, expected):
    # Versioned source admission retains the historical 404 pins and all 102 independent anchors.
    source = candidate.source_inputs(repo, expected)
    contract = json.loads((repo / CONTRACT).read_text())
    require(set(contract) == {'schema_version', 'recipe', 'source_admission', 'source_recipe',
            'base_reviewed_source', 'base_reviewed_runtime_tree', 'source_migration_sha256',
            'release_authorized', 'source_sha256'}
            and type(contract.get('schema_version')) is int
            and contract.get('schema_version') == 1 and contract.get('recipe') == IDENTITY
            and contract.get('base_reviewed_source') == candidate.REVIEWED_RUNTIME_SOURCE
            and contract.get('base_reviewed_runtime_tree') == candidate.REVIEWED_RUNTIME_TREE
            and contract.get('source_migration_sha256') == candidate.ALPHA27_MIGRATION_SHA256
            and contract.get('source_admission') == SOURCE_ADMISSION
            and contract.get('source_recipe') == SOURCE_RECIPE
            and contract.get('release_authorized') is False,
            'invalid analytical source contract')
    pins = contract.get('source_sha256')
    require(isinstance(pins, dict) and set(pins) == SOURCE_PATHS, 'analytical source boundary changed')
    validate_alpha27_admission(repo, pins)
    files = {entry['path']: entry for entry in source['files']}
    require(CONTRACT in files, 'analytical source contract must be tracked')
    for relative in SOURCE_PATHS | {CONTRACT}:
        entry = files.get(relative)
        require(entry is not None, 'missing analytical source: ' + relative)
        # Hash canonical blob bytes as well as the LF checkout used by Cargo.
        import subprocess
        import hashlib
        blob = subprocess.check_output(['git', 'cat-file', 'blob', entry['canonical_git_blob']], cwd=repo)
        require(hashlib.sha256(blob).hexdigest() == entry['checkout_sha256'],
                'analytical checkout differs from Git: ' + relative)
        if relative != CONTRACT:
            require(pins[relative] == entry['checkout_sha256'], 'analytical source pin changed: ' + relative)
    return {**source, 'source_recipe': SOURCE_RECIPE, 'analytical_contract': contract, 'analytical_contract_sha256': digest(repo / CONTRACT)}


def graph_identity(name, value):
    return (name.rsplit('@', 1)[0], value['version'])


def reconcile(metadata, graph, repo, mode):
    require(Path(metadata['workspace_root']).resolve() == repo.resolve(), 'foreign metadata workspace')
    packages, nodes, ids = collector.closure(metadata, 'flightsim-app')
    lock = tomllib.loads((repo / 'Cargo.lock').read_text())
    locked = {(p['name'], p['version'], p.get('source')): p for p in lock['package']}
    for i in ids:
        package = packages[i]
        identity = (package['name'], package['version'], package.get('source'))
        require(identity in locked, 'metadata package is absent from exact lock: ' + package['name'])
        if (package.get('source') or '').startswith('registry+'):
            require(re.fullmatch('[0-9a-f]{64}', locked[identity].get('checksum', '')) is not None,
                    'registry checksum missing from pinned lock')
    identities = {(packages[i]['name'], packages[i]['version']): i for i in ids}
    require(len(identities) == len(ids), 'ambiguous source for package/version')
    exact = {graph_identity(name, value): value for name, value in graph.items()}
    require(len(exact) == len(graph) and set(exact) <= set(identities),
            'package graph is outside conservative metadata closure')
    if mode == 'analytic':
        require(not any('tonemapping_luts' in nodes[i]['features'] for i in ids),
                'metadata reactivates LUTs; stop and resolve collection design without editing evidence')
    differences = []
    for identity, i in identities.items():
        package, node = packages[i], nodes[i]
        require(Path(package['manifest_path']).is_file(), 'missing metadata package source')
        features = set(node['features'])
        if identity in exact:
            required = exact[identity]['features']
            require(required <= features, 'metadata omits exact graph features: ' + package['name'])
            if package['name'] == 'flightsim-app':
                require(features == required, 'metadata app selection differs from exact recipe')
            if features != required:
                differences.append({'package': package['name'], 'version': package['version'],
                                    'exact_features': sorted(required), 'metadata_features': sorted(features)})
    extra = [{'package': name, 'version': version} for name, version in sorted(set(identities) - set(exact))]
    return {'exact_graph_packages': len(exact), 'conservative_packages': len(ids),
            'extra_conservative_packages': extra, 'conservative_feature_differences': differences,
            'scope': 'Raw metadata retained unchanged; conservative extras retained in inventory; exact graph is separate compiled-scope evidence'}


def validate_inventory(metadata_path, inventory_path, graph, repo, mode, *, source_recipe=tone.UPSTREAM_THREE_LUT_SOURCE):
    require(source_recipe in (tone.UPSTREAM_THREE_LUT_SOURCE, SOURCE_RECIPE), "unknown inventory source recipe")
    metadata = json.loads(metadata_path.read_text())
    difference = reconcile(metadata, graph, repo, mode)
    inventory = json.loads(inventory_path.read_text())
    # Recollect exact sources rather than trust mutable package/notice summaries.
    # The isolated temporary result never replaces the original inventory.
    with tempfile.TemporaryDirectory(prefix='analytical-swift-notices-') as temporary:
        fresh = collector.collect(metadata_path, repo, Path(temporary) / 'notices', TARGET, 'flightsim-app')
    require(inventory == fresh, 'inventory differs from fresh conservative collection')
    require(inventory.get('review_status') == 'not_reviewed', 'collection is not review approval')
    expected_assets = {'bevy-fira-mono'}
    if mode == 'ordinary':
        expected_assets |= {'bevy-tony-mc-mapface', 'bevy-blender-filmic-lut'}
        if source_recipe == tone.UPSTREAM_THREE_LUT_SOURCE:
            expected_assets.add('bevy-agx-lut')
    require({a['id'] for a in inventory['embedded_assets']} == expected_assets,
            'embedded asset applicability differs from exact mode')
    identities = {p['id'] for p in inventory['packages']}
    require({'constgebra@0.1.4', 'hexf-parse@0.2.1'} <= identities, 'remaining dependency obligations disappeared')
    report = readiness.check(repo, None, inventory_path)
    candidate.validate_readiness(report, 2)
    require(any(b['code'] == 'DEPENDENCY_REVIEW_REQUIRED' for b in report['blockers']),
            'missing genuine dependency review must remain blocked')
    return {'inventory_sha256': digest(inventory_path), 'metadata_sha256': digest(metadata_path),
            'reconciliation': difference, 'readiness': report}


def file_record(path):
    require(path.is_absolute() and path.is_file() and not path.is_symlink(), 'expected absolute regular artifact path')
    require(not any(p.is_symlink() for p in path.parents), 'artifact path traverses a symlink')
    return {'sha256': digest(path), 'bytes': path.stat().st_size}


def recapture(repo, target, mode):
    """Authoritative read-only Cargo collection; never compile or alter metadata.

    A receipt/hash supplied by a caller cannot establish metadata completeness.
    Re-run the exact locked/offline read commands in the same source/target.
    """
    overrides = ('RUSTC', 'RUSTC_WRAPPER', 'RUSTC_WORKSPACE_WRAPPER', 'CARGO_ENCODED_RUSTFLAGS',
                 'CARGO_BUILD_RUSTC', 'CARGO_BUILD_RUSTC_WRAPPER', 'CARGO_BUILD_RUSTC_WORKSPACE_WRAPPER')
    require(not any(os.environ.get(key) for key in overrides), 'unapproved compiler override in audit environment')
    env = {**os.environ, 'RUSTFLAGS': '-D warnings', 'CARGO_TARGET_DIR': str(target), 'CARGO_INCREMENTAL': '0'}
    return {name: subprocess.check_output(commands(mode)[name], cwd=repo, env=env, timeout=180)
            for name in ('rustc', 'graph', 'metadata')}


def release_profile(artifact):
    profile = artifact.get('profile', {})
    require(profile.get('opt_level') == '3' and type(profile.get('debuginfo')) is int
            and profile['debuginfo'] == 0 and profile.get('debug_assertions') is False
            and profile.get('overflow_checks') is False and profile.get('test') is False,
            'selected artifact is not the strict release profile')


def validate_capture(record, directory, repo, mode, source):
    require(record.get('cwd') == str(repo.resolve()) and record.get('source_sha') == source['source_sha']
            and record.get('source_tree') == source['source_tree'], 'command source/CWD mismatch')
    target = Path(record['target_dir'])
    require(target.is_absolute() and target.resolve() == target and not target.is_symlink(), 'invalid target directory')
    require(record.get('environment') == {'RUSTFLAGS': '-D warnings', 'CARGO_TARGET_DIR': str(target),
                                         'CARGO_INCREMENTAL': '0'}, 'unexpected captured compiler environment')
    require(record.get('commands') == commands(mode), 'build/graph/metadata command differs from recipe')
    outputs = {'rustc': 'rustc.txt', 'graph': 'graph.txt', 'build': 'messages.jsonl', 'metadata': 'metadata.json'}
    require(set(record.get('results', {})) == set(outputs), 'incomplete command results')
    for key, filename in outputs.items():
        status = record['results'][key]
        require(type(status.get('exit_code')) is int and status['exit_code'] == 0, 'capture command failed: ' + key)
        require(status.get('stdout') == file_record(directory / filename)
                and status.get('stderr') == file_record(directory / (key + '.stderr')), 'captured command output changed: ' + key)
    fresh = recapture(repo, target, mode)
    for name in ('rustc', 'graph', 'metadata'):
        require((directory / outputs[name]).read_bytes() == fresh[name],
                'captured ' + name + ' differs from authoritative locked/offline recapture')
    compiler = (directory / 'rustc.txt').read_text()
    require(compiler.startswith('rustc 1.93.0 ') and '\nhost: ' + TARGET + '\n' in compiler,
            'capture is not the pinned native Windows MSVC compiler')
    graph_path, messages_path = directory / 'graph.txt', directory / 'messages.jsonl'
    graph = tone.parse_graph(graph_path.read_text())
    selected_recipe = IDENTITY if mode == 'analytic' else None
    tone.validate_graph(graph, mode, 'app', recipe=selected_recipe)
    require(graph_path.read_text().splitlines()[0].startswith('flightsim-app v'), 'graph root is not the app')
    require('downloads' not in graph.get('flightsim-content', {}).get('features', set()), 'network content features are forbidden')
    messages = [json.loads(line) for line in messages_path.read_text().splitlines()]
    require([m for m in messages if m.get('reason') == 'build-finished'] == [{'reason': 'build-finished', 'success': True}],
            'contradictory or incomplete build completion')
    require(not any(m.get('reason') == 'compiler-message' and m.get('message', {}).get('level') in ('error', 'failure-note', 'warning')
                    for m in messages), 'build contains rejected compiler diagnostics')
    artifacts = [m for m in messages if m.get('reason') == 'compiler-artifact']
    require(len([m for m in artifacts if m.get('executable')]) == 1, 'unexpected executable roots')
    source_recipe = source['source_recipe']
    modern = source_recipe == SOURCE_RECIPE
    root, libraries = tone.select_artifacts(messages, graph, 'app', source_recipe=source_recipe,
                                             source_root=repo if modern else None)
    render = [a for a in artifacts if a['target']['name'] == 'flightsim_render' and a['target']['kind'] == ['lib']]
    require(len(render) == 1 and set(render[0]['features']) == graph['flightsim-render']['features'],
            'missing or mismatched compiled render routing')
    executable = target / TARGET / 'release/flightsim-app.exe'
    require(Path(root['executable']) == executable, 'wrong target/profile/executable path')
    for artifact in [root, *libraries.values(), render[0]]:
        release_profile(artifact)
    require(Path(root['target']['src_path']).resolve() == repo / 'crates/flightsim-app/src/main.rs', 'foreign app source')
    metadata = json.loads((directory / 'metadata.json').read_text())
    require(Path(metadata['target_directory']) == target, 'metadata target directory differs from captured build')
    packages, nodes, ids = collector.closure(metadata, 'flightsim-app')
    exact_identities = {graph_identity(name, item): item['features'] for name, item in graph.items()}
    for artifact in artifacts:
        package_id = artifact['package_id']
        require(package_id in packages and (packages[package_id]['name'], packages[package_id]['version']) in exact_identities,
                'compiled package is absent from exact app graph')
        require(set(artifact['features']) <= exact_identities[(packages[package_id]['name'], packages[package_id]['version'])],
                'compiled features are outside exact app graph')
        require(package_id in ids and set(artifact['features']) <= set(nodes[package_id]['features']),
                'compiled package/features outside conservative metadata')
        require(any(t['name'] == artifact['target']['name'] and t['kind'] == artifact['target']['kind']
                    and t['src_path'] == artifact['target']['src_path'] for t in packages[package_id]['targets']),
                'compiled source target differs from metadata')
    result = tone.audit(graph_path, messages_path, mode, 'app', recipe=selected_recipe,
                        source_recipe=source_recipe, source_root=repo if modern else None,
                        upstream_archive=source.get('upstream_archive') if modern else None,
                        target=TARGET if modern else None)
    paths = [executable, Path(result['core_pipeline_depinfo']['path'])]
    for item in result['compiled']:
        paths.extend([Path(item['rlib']), Path(item['fingerprint'])])
    # Freeze the render routing library too, in addition to the six dependency libraries.
    render_libraries = [Path(p) for p in render[0]['filenames'] if p.endswith('.rlib')]
    require(len(render_libraries) == 1 and render_libraries[0].parent == executable.parent / 'deps',
            'render library is outside the exact target')
    paths.extend(render_libraries)
    render_suffix = render_libraries[0].stem.removeprefix('libflightsim_render-')
    require(render_suffix != render_libraries[0].stem, 'unrecognized render library name')
    render_fingerprint = executable.parent / '.fingerprint' / ('flightsim-render-' + render_suffix) / 'lib-flightsim_render.json'
    app_fingerprints = list((executable.parent / '.fingerprint').glob('flightsim-app-*/bin-flightsim-app.json'))
    require(len(app_fingerprints) == 1, 'expected one app fingerprint in the fresh target tree')
    for fingerprint, artifact in ((render_fingerprint, render[0]), (app_fingerprints[0], root)):
        value = json.loads(fingerprint.read_text())
        require(set(json.loads(value['features'])) == set(artifact['features']) and value.get('rustflags') == ['-D', 'warnings'],
                'app/render fingerprint differs from selected features or flags')
        paths.append(fingerprint)
    observed = {str(path): file_record(path) for path in paths}
    require(record.get('frozen_artifacts') == observed, 'frozen artifact hashes/bytes changed or incomplete')
    inventory = validate_inventory(directory / 'metadata.json', directory / 'notices/dependency-inventory.json',
                                   graph, repo, mode, source_recipe=source_recipe)
    require(record.get('inventory') == file_record(directory / 'notices/dependency-inventory.json'), 'inventory capture changed')
    return {'artifact': result, **inventory}


def audit(repo, expected, capture, *, upstream_archive=None):
    repo, capture = repo.resolve(), capture.resolve()
    original_capture = (capture / 'capture.json').read_bytes()
    value = json.loads(original_capture)
    validate_header(value, expected)
    source = source_evidence(repo, expected)
    require(value.get('source_tree') == source['source_tree'], 'capture source tree changed')
    require(value['source_recipe'] == source['source_recipe'], 'capture source recipe differs from admitted source')
    capture_source = dict(source)
    if source['source_recipe'] == SOURCE_RECIPE:
        require(upstream_archive is not None, 'two-LUT audit requires private upstream archive')
        upstream_archive = Path(upstream_archive)
        require(upstream_archive.is_absolute() and upstream_archive.resolve() == upstream_archive,
                'private upstream reference must be absolute and unaliased')
        file_record(upstream_archive)
        tone.validate_source(repo, upstream_archive)
        require(value.get('upstream_archive') == file_record(upstream_archive), 'private upstream reference changed')
        capture_source['upstream_archive'] = upstream_archive
    else:
        require(upstream_archive is None and 'upstream_archive' not in value,
                'historical source recipe cannot accept a two-LUT reference')
    directories = [Path(value['modes'][mode]['target_dir']).resolve() for mode in ('analytic', 'ordinary')]
    require(not directories[0].is_relative_to(directories[1]) and not directories[1].is_relative_to(directories[0]),
            'ordinary control requires a disjoint target directory')
    results = {mode: validate_capture(value['modes'][mode], capture / mode, repo, mode, capture_source)
               for mode in ('analytic', 'ordinary')}
    analytic, ordinary = (results[mode]['artifact'] for mode in ('analytic', 'ordinary'))
    require(analytic['executable_sha256'] != ordinary['executable_sha256'], 'ordinary control was substituted')
    require([(p['name'], p['source_sha256'], p['bytes']) for p in analytic['payloads']]
            == [(p['name'], p['source_sha256'], p['bytes']) for p in ordinary['payloads']], 'ordinary LUT source control changed')
    # Rehash every supplied input at the end; neither evidence nor source may drift.
    require((capture / 'capture.json').read_bytes() == original_capture, 'capture changed during audit')
    require(source_evidence(repo, expected) == source, 'source changed during audit')
    for mode in ('analytic', 'ordinary'):
        directory = capture / mode
        for name, filename in {'rustc': 'rustc.txt', 'graph': 'graph.txt', 'build': 'messages.jsonl', 'metadata': 'metadata.json'}.items():
            status = value['modes'][mode]['results'][name]
            require(file_record(directory / filename) == status['stdout']
                    and file_record(directory / (name + '.stderr')) == status['stderr'], 'input changed during audit')
        require(file_record(directory / 'notices/dependency-inventory.json') == value['modes'][mode]['inventory'],
                'inventory changed during audit')
        final_readiness = readiness.check(repo, None, directory / 'notices/dependency-inventory.json')
        candidate.validate_readiness(final_readiness, 2)
        require(final_readiness == results[mode]['readiness'], 'notice integrity/readiness changed during audit')
        for path, frozen in value['modes'][mode]['frozen_artifacts'].items():
            require(file_record(Path(path)) == frozen, 'artifact changed during audit')
    if upstream_archive is not None:
        require(file_record(upstream_archive) == value['upstream_archive'], 'private upstream reference changed during audit')
    return {**recipe(source['source_recipe']), 'status': 'build_evidence_checked_native_and_distribution_unqualified',
            'source_sha': expected, 'source_tree': source['source_tree'],
            'analytical_contract_sha256': source['analytical_contract_sha256'],
            'replay_contract_sha256': source['replay_contract_sha256'],
            'capture_sha256': digest(capture / 'capture.json'), 'builds': results,
            **({'upstream_archive': value['upstream_archive']} if upstream_archive is not None else {}),
            'tone_attestation': 'Exact pinned source/command/graph/compiled features/fingerprints/dep-info/executable payloads; distribution-info has no tone field'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--describe', action='store_true')
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--source-sha')
    parser.add_argument('--capture', type=Path)
    parser.add_argument('--upstream-archive', type=Path)
    args = parser.parse_args()
    try:
        if args.describe:
            require(args.source_sha is None and args.capture is None, 'describe cannot attest a capture')
            result = recipe()
        else:
            require(args.source_sha is not None and args.capture is not None, 'audit requires source SHA and complete capture')
            result = audit(args.repo, args.source_sha, args.capture, upstream_archive=args.upstream_archive)
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print('analytical Swift build-evidence audit failed: ' + str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
