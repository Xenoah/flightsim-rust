"""Exact version-only migration; no native, rights or publication acceptance."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    'alpha26_source_fixture', ROOT / 'scripts/tests/test_component_terms_source_admission.py')
fixture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture_module)
capture = fixture_module.capture
candidate = capture.check.candidate
CHANGED = {'Cargo.toml', 'Cargo.lock'}
RELOCATIONS = {
    'Cargo.toml': 'scripts/history/e2e23ce-Cargo.toml',
    'Cargo.lock': 'scripts/history/e2e23ce-Cargo.lock',
}
ADDED = {
    'scripts/alpha26-version-source-migration.json',
    'scripts/history/e2e23ce-replay-candidate-contract.json',
    'scripts/history/e2e23ce-analytical-swift-source-contract.json',
    'scripts/history/e2e23ce-analytical-swift-capture-contract.json',
    *RELOCATIONS.values(),
}


def retained_alpha26_path(relative):
    prior = candidate.URBAN_HISTORICAL_RELOCATIONS.get(relative, relative)
    return ROOT / candidate.ALPHA27_HISTORICAL_RELOCATIONS.get(prior, prior)


class Alpha26VersionSourceAdmissionTests(unittest.TestCase):
    fixture = fixture_module.ComponentTermsSourceAdmissionTests.fixture
    commit = staticmethod(fixture_module.ComponentTermsSourceAdmissionTests.commit)

    def version_bytes(self):
        return ({path: (ROOT / historical).read_bytes() for path, historical in RELOCATIONS.items()},
                {path: (ROOT / candidate.ALPHA27_HISTORICAL_RELOCATIONS.get(path, path)).read_bytes() for path in CHANGED})

    def test_exact_two_file_transition_preserves_all_995_prior_pins(self):
        contract = json.loads((ROOT / candidate.URBAN_BASE_CONTRACT_PATH).read_text())
        candidate.validate_alpha26_replay_contract(contract)
        base = json.loads((ROOT / candidate.ALPHA26_BASE_CONTRACT_PATH).read_text())
        migration = json.loads((ROOT / candidate.ALPHA26_MIGRATION_PATH).read_text())
        self.assertEqual(candidate.ALPHA26_SOURCE_PATHS, ADDED)
        self.assertEqual(candidate.ALPHA26_HISTORICAL_RELOCATIONS, RELOCATIONS)
        self.assertEqual(set(migration['replaced_source_sha256']), CHANGED)
        self.assertEqual(migration['historical_relocations'], RELOCATIONS)
        self.assertEqual(migration['added_source_sha256'], {})
        self.assertEqual(migration['base_source'], 'e2e23ce1e954fd34ea6dd90a102a17ca0a7d3f4b')
        self.assertEqual(migration['base_tree'], '1ea5182a0ca7ea9883ea6a5b18ba4db9ad032cda')
        self.assertEqual(migration['base_source_kind'], 'merged-main-commit')
        self.assertEqual(migration['previous_source_migration_sha256'], candidate.CHASE_HUD_MIGRATION_SHA256)
        candidate.validate_chase_hud_replay_contract(base)
        self.assertEqual(len(base['source_sha256']), 995)
        self.assertEqual(len(contract['source_sha256']), 1001)
        self.assertEqual(set(contract['source_sha256']) - set(base['source_sha256']), ADDED)
        self.assertEqual({path for path, expected in base['source_sha256'].items()
                          if contract['source_sha256'][path] != expected}, CHANGED)
        for path, expected in base['source_sha256'].items():
            historical = RELOCATIONS.get(path, path)
            self.assertEqual(contract['source_sha256'][historical], expected, path)
            self.assertEqual(candidate.digest(retained_alpha26_path(historical)), expected, path)
        for path, expected in candidate.ALPHA26_BASE_CONTRACT_HASHES.items():
            self.assertEqual(candidate.digest(retained_alpha26_path(path)), expected)
        for path in CHANGED:
            self.assertEqual(migration['replaced_source_sha256'][path], {
                'previous_sha256': base['source_sha256'][path],
                'sha256': candidate.digest(retained_alpha26_path(path)),
            })
        candidate.validate_alpha26_version_delta(*self.version_bytes())
        self.assertEqual(len(candidate.CHASE_HUD_REPLAY_CONTRACT_PATHS), 995)
        self.assertEqual(len(candidate.ALPHA26_SOURCE_PATHS), 6)
        self.assertEqual(len(candidate.ALPHA26_WORKSPACE_PACKAGES), 13)
        self.assertEqual(candidate.ALPHA26_WORKSPACE_PACKAGES, candidate.ALPHA25_WORKSPACE_PACKAGES)
        self.assertEqual(len(capture.check.SOURCE_PATHS), 71)
        self.assertEqual(len(capture.BOUND_FILES), 4)
        self.assertEqual(len(candidate.CURRENT_CRATE_SOURCE_PATHS), 503)
        self.assertEqual(len(candidate.INDEPENDENT_REPLAY_HASHES), 102)
        self.assertEqual(len(json.loads((ROOT / candidate.PRESERVED_RUNTIME_PATH).read_text())['source_sha256']), 497)
        self.assertIs(contract['release_authorized'], False)

    def test_merged_source_provenance_does_not_create_publication_authority(self):
        migration = json.loads((ROOT / candidate.ALPHA26_MIGRATION_PATH).read_text())
        self.assertEqual(migration['base_source_kind'], 'merged-main-commit')
        self.assertEqual(migration['base_source'], 'e2e23ce1e954fd34ea6dd90a102a17ca0a7d3f4b')
        self.assertEqual(migration['base_tree'], '1ea5182a0ca7ea9883ea6a5b18ba4db9ad032cda')
        self.assertEqual(migration['previous_version'], '0.6.0-alpha.25')
        self.assertEqual(migration['version'], '0.6.0-alpha.26')
        self.assertNotIn('native_runtime_qualified', migration)
        self.assertNotIn('distribution_qualified', migration)
        positive = candidate.load_replay_contract(ROOT)
        self.assertEqual(positive['scope'], candidate.SOURCE_ADMISSION_SCOPE)
        self.assertIs(positive['release_authorized'], False)
        for key, value in (
                ('schema_version', True),
                ('contract', candidate.CHASE_HUD_REPLAY_CONTRACT_ID),
                ('base_reviewed_source', migration['base_source']),
                ('base_reviewed_runtime_tree', migration['base_tree']),
                ('source_migration_sha256', candidate.CHASE_HUD_MIGRATION_SHA256),
                ('scope', 'native and distribution approved'),
                ('release_authorized', True)):
            with self.subTest(key=key), self.assertRaises(ValueError):
                candidate.validate_replay_contract({**positive, key: value})
        for key in positive:
            changed = copy.deepcopy(positive)
            del changed[key]
            with self.subTest(missing=key), self.assertRaises(ValueError):
                candidate.validate_replay_contract(changed)
        with self.assertRaises(ValueError):
            candidate.validate_replay_contract({**positive, 'native_runtime_qualified': True})

    def test_version_semantics_reject_unrelated_manifest_and_lock_changes(self):
        previous, current = self.version_bytes()
        manifest_mutations = [
            (b'0.6.0-alpha.26', b'0.6.0-alpha.27'),
            (b'edition = "2024"', b'edition = "2021"'),
            (b'rust-version = "1.85"', b'rust-version = "1.86"'),
            (b'"crates/flightsim-net",', b'"crates/unreviewed",'),
            (b'glam = "0.30"', b'glam = "0.31"'),
            (b'"x11",', b'"wayland",'),
            (b'vendor/bevy_pbr', b'vendor/unreviewed_pbr'),
        ]
        lock_mutations = [
            (b'0.6.0-alpha.26', b'0.6.0-alpha.25'),
            (b'name = "flightsim-app"', b'name = "unreviewed-app"'),
            (b'name = "flightsim-app"', b'name = "flightsim-core"'),
            (b'name = "flightsim-app"', b'name = "flightsim-app"\nsource = "registry+https://example.invalid"'),
            (b'version = 4', b'version = 3'),
            (b'version = "0.21.1"', b'version = "0.21.2"'),
            (b'cf203f9d3bd8f29f', b'df203f9d3bd8f29f'),
            (b'crates.io-index', b'unreviewed-index'),
        ]
        for path, mutations in [('Cargo.toml', manifest_mutations), ('Cargo.lock', lock_mutations)]:
            for old, new in mutations:
                self.assertIn(old, current[path])
                changed = {**current, path: current[path].replace(old, new, 1)}
                with self.subTest(path=path, old=old), self.assertRaises(ValueError):
                    candidate.validate_alpha26_version_delta(previous, changed)
            for suffix in (b'\n', b'\n# unreviewed comment\n'):
                with self.subTest(path=path, suffix=suffix), self.assertRaises(ValueError):
                    candidate.validate_alpha26_version_delta(previous, {**current, path: current[path] + suffix})
        for changed in (current | {'extra.toml': b''}, {'Cargo.toml': current['Cargo.toml']},
                        current | {'Cargo.lock': b' ' * (1024 * 1024 + 1)}):
            with self.assertRaises(ValueError):
                candidate.validate_alpha26_version_delta(previous, changed)
        # These additional changes must fail even if both sides are edited alike.
        for path, old, new in [('Cargo.toml', b'"crates/flightsim-net",', b'"crates/extra",'),
                               ('Cargo.lock', b'name = "flightsim-net"', b'name = "extra"')]:
            with self.subTest(previous=path), self.assertRaises(ValueError):
                candidate.validate_alpha26_version_delta(
                    {**previous, path: previous[path].replace(old, new)},
                    {**current, path: current[path].replace(old, new)})

    def test_reordered_added_or_removed_lock_packages_are_rejected(self):
        previous, current = self.version_bytes()
        sections = current['Cargo.lock'].split(b'[[package]]')
        for sections_changed in (sections[:1] + [sections[2], sections[1]] + sections[3:],
                                 sections + [sections[-1]], sections[:-1]):
            with self.assertRaises(ValueError):
                candidate.validate_alpha26_version_delta(
                    previous, {**current, 'Cargo.lock': b'[[package]]'.join(sections_changed)})

    def test_contract_cannot_repin_omit_or_alias_version_inputs(self):
        positive = candidate.load_replay_contract(ROOT)
        for path in CHANGED | ADDED:
            for attack in ('repin', 'omit', 'alias'):
                changed = copy.deepcopy(positive)
                if attack == 'repin':
                    changed['source_sha256'][path] = '0' * 64
                elif attack == 'omit':
                    del changed['source_sha256'][path]
                else:
                    changed['source_sha256'][path.upper()] = changed['source_sha256'].pop(path)
                with self.subTest(path=path, attack=attack), self.assertRaises(ValueError):
                    candidate.validate_replay_contract(changed)
        for identity in (candidate.CHASE_HUD_REPLAY_CONTRACT_ID, candidate.ALPHA25_REPLAY_CONTRACT_ID,
                         candidate.SWIFT_FORWARD_REPLAY_CONTRACT_ID, candidate.ALPHA24_REPLAY_CONTRACT_ID,
                         candidate.COCKPIT_VARIANT_REPLAY_CONTRACT_ID, candidate.ALPHA23_REPLAY_CONTRACT_ID,
                         candidate.COCKPIT_REPLAY_CONTRACT_ID, candidate.ALPHA22_REPLAY_CONTRACT_ID,
                         'full-two-aircraft-terrain-stitch-source-v1',
                         'full-two-aircraft-terrain-centroid-source-v1'):
            with self.assertRaises(ValueError):
                candidate.validate_replay_contract({**positive, 'contract': identity})
        with self.assertRaises(ValueError):
            candidate.validate_replay_contract({**positive,
                'source_migration_sha256': candidate.TERRAIN_STITCH_MIGRATION_SHA256})

    def test_actual_capture_chain_requires_exact_bytes_without_public_base_objects(self):
        repo, _ = self.fixture()
        result = subprocess.run(['git', 'cat-file', '-e',
            'e2e23ce1e954fd34ea6dd90a102a17ca0a7d3f4b^{commit}'], cwd=repo, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        for relative in sorted(CHANGED | ADDED):
            path = repo / relative
            original = path.read_bytes()
            path.write_bytes(original + b'\n')
            with self.subTest(path=relative), self.assertRaises(ValueError):
                capture.source_evidence(repo, self.commit(repo))
            path.write_bytes(original)
            capture.source_evidence(repo, self.commit(repo))

    def test_export_cannot_omit_substitute_or_reseal_version_inputs(self):
        _, source = self.fixture()
        report = {'source_sha': source['source_sha'], 'replay_contract': candidate.REPLAY_CONTRACT_ID,
                  'replay_contract_sha256': source['replay_contract_sha256']}
        candidate.validate_source_evidence(source, report)
        for relative in sorted(CHANGED | ADDED):
            for attack in ('omit-file', 'omit-evidence', 'canonical', 'checkout', 'reseal-contract'):
                changed = copy.deepcopy(source)
                changed_report = dict(report)
                if attack == 'omit-file':
                    changed['files'] = [row for row in changed['files'] if row['path'] != relative]
                elif attack == 'omit-evidence':
                    del changed['reviewed_replay_source_evidence'][relative]
                elif attack == 'canonical':
                    changed['reviewed_replay_source_evidence'][relative]['canonical_sha256'] = '0' * 64
                elif attack == 'checkout':
                    next(row for row in changed['files'] if row['path'] == relative)['checkout_sha256'] = '0' * 64
                    changed['reviewed_replay_source_evidence'][relative]['checkout_sha256'] = '0' * 64
                else:
                    changed['replay_contract']['source_sha256'][relative] = '0' * 64
                    changed['replay_contract_text'] = json.dumps(changed['replay_contract'])
                    digest = candidate.hashlib.sha256(changed['replay_contract_text'].encode()).hexdigest()
                    changed['replay_contract_sha256'] = digest
                    changed_report['replay_contract_sha256'] = digest
                with self.subTest(path=relative, attack=attack), self.assertRaises(ValueError):
                    candidate.validate_source_evidence(changed, changed_report)


    def test_analytical_successor_preserves_frozen_64_input_proof(self):
        check = capture.check
        previous = json.loads((ROOT / check.ALPHA26_BASE_CONTRACT_PATH).read_text())
        current = json.loads((ROOT / check.CI60_BASE_CONTRACT_PATH).read_text())
        check.validate_chase_hud_admission(ROOT, previous['source_sha256'])
        check.validate_alpha26_admission(ROOT, current['source_sha256'])
        self.assertEqual(len(previous['source_sha256']), 64)
        self.assertEqual(set(current['source_sha256']) - set(previous['source_sha256']),
                         check.ALPHA26_SOURCE_PATHS)
        self.assertEqual({p for p, h in previous['source_sha256'].items()
                          if current['source_sha256'][p] != h}, check.ALPHA26_REBOUND_PATHS)
        for path in set(previous['source_sha256']) - check.ALPHA26_REBOUND_PATHS:
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'unrelated analytical'):
                check.validate_alpha26_admission(ROOT, {**current['source_sha256'], path: '0' * 64})
        for path in check.ALPHA26_SOURCE_PATHS:
            for attack in ('omit', 'alias', 'extra'):
                changed = dict(current['source_sha256'])
                if attack == 'omit':
                    del changed[path]
                elif attack == 'alias':
                    changed[path.upper()] = changed.pop(path)
                else:
                    changed[path + '.extra'] = '0' * 64
                with self.subTest(path=path, attack=attack), self.assertRaises(ValueError):
                    check.validate_alpha26_admission(ROOT, changed)

    def test_resealed_cargo_and_descriptor_cannot_authorize_themselves(self):
        repo, _ = self.fixture()
        path = repo / 'Cargo.toml'
        path.write_bytes(path.read_bytes().replace(b'0.6.0-alpha.26', b'0.6.0-alpha.27'))
        migration = json.loads((repo / candidate.ALPHA26_MIGRATION_PATH).read_text())
        migration['replaced_source_sha256']['Cargo.toml']['sha256'] = candidate.digest(path)
        capture.write_json(repo / candidate.ALPHA26_MIGRATION_PATH, migration)
        contract = json.loads((repo / candidate.REPLAY_CONTRACT_PATH).read_text())
        contract['source_sha256']['Cargo.toml'] = candidate.digest(path)
        contract['source_sha256'][candidate.ALPHA26_MIGRATION_PATH] = candidate.digest(repo / candidate.ALPHA26_MIGRATION_PATH)
        contract['source_migration_sha256'] = candidate.digest(repo / candidate.ALPHA26_MIGRATION_PATH)
        capture.write_json(repo / candidate.REPLAY_CONTRACT_PATH, contract)
        with self.assertRaisesRegex(ValueError, 'identity or scope changed'):
            capture.source_evidence(repo, self.commit(repo))

if __name__ == '__main__':
    unittest.main()
