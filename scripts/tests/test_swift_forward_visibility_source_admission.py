"""Three-file Swift presentation admission; historical/native gates stay independent."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    'swift_forward_source_fixture', ROOT / 'scripts/tests/test_component_terms_source_admission.py')
fixture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture_module)
capture = fixture_module.capture
check = capture.check
candidate = check.candidate
CHANGED = {
    'crates/flightsim-app/src/cockpit_runtime.rs',
    'crates/flightsim-render/src/cockpit.rs',
    'crates/flightsim-render/src/cockpit/variants.rs',
}
RELOCATIONS = {
    'crates/flightsim-app/src/cockpit_runtime.rs': 'scripts/history/4f385e1-cockpit_runtime.rs',
    'crates/flightsim-render/src/cockpit.rs': 'scripts/history/4f385e1-cockpit.rs',
    'crates/flightsim-render/src/cockpit/variants.rs': 'scripts/history/4f385e1-cockpit-variants.rs',
}
CONTRACTS = {f'scripts/history/4f385e1-{name}' for name in (
    'replay-candidate-contract.json', 'analytical-swift-source-contract.json',
    'analytical-swift-capture-contract.json')}
MIGRATION = 'scripts/swift-forward-visibility-source-migration.json'
ADDED = {MIGRATION, *CONTRACTS, *RELOCATIONS.values()}


class SwiftForwardVisibilitySourceAdmissionTests(unittest.TestCase):
    fixture = fixture_module.ComponentTermsSourceAdmissionTests.fixture
    commit = staticmethod(fixture_module.ComponentTermsSourceAdmissionTests.commit)

    def previous(self):
        return json.loads((ROOT / candidate.SWIFT_FORWARD_BASE_CONTRACT_PATH).read_text())

    def test_exact_three_replacements_preserve_all_974_prior_pins_and_physics(self):
        current = json.loads((ROOT / candidate.ALPHA25_BASE_CONTRACT_PATH).read_text())
        candidate.validate_swift_forward_replay_contract(current)
        previous = self.previous()
        candidate.validate_alpha24_replay_contract(previous)
        migration = json.loads((ROOT / MIGRATION).read_text())
        self.assertEqual(set(previous['source_sha256']), candidate.ALPHA24_REPLAY_CONTRACT_PATHS)
        self.assertEqual(len(previous['source_sha256']), 974)
        self.assertEqual(len(current['source_sha256']), 981)
        self.assertEqual(set(current['source_sha256']) - set(previous['source_sha256']), ADDED)
        self.assertEqual(candidate.SWIFT_FORWARD_SOURCE_PATHS, ADDED)
        self.assertEqual(candidate.SWIFT_FORWARD_HISTORICAL_RELOCATIONS, RELOCATIONS)
        self.assertEqual(set(migration['replaced_source_sha256']), CHANGED)
        self.assertEqual(migration['added_source_sha256'], {})
        self.assertEqual(migration['base_source'], '4f385e121addc036c2103d634e2bb46e6392172b')
        self.assertEqual(migration['base_tree'], '47aed13ca164afcadf3c1201c411fecd00e77cd4')
        self.assertEqual(migration['previous_source_migration_sha256'], candidate.ALPHA24_MIGRATION_SHA256)
        self.assertEqual({p for p, h in previous['source_sha256'].items()
                          if current['source_sha256'][p] != h}, CHANGED)
        for path, expected in previous['source_sha256'].items():
            historical = RELOCATIONS.get(path, path)
            self.assertEqual(current['source_sha256'][historical], expected, path)
            self.assertEqual(candidate.digest(ROOT / candidate.ALPHA25_HISTORICAL_RELOCATIONS.get(historical, historical)), expected, path)
        for path in CHANGED:
            self.assertEqual(candidate.SWIFT_FORWARD_CURRENT_SHA256[path], candidate.digest(ROOT / path))
        self.assertEqual(len(candidate.CURRENT_CRATE_SOURCE_PATHS), 499)
        self.assertEqual(len(candidate.INDEPENDENT_REPLAY_HASHES), 102)
        frozen = json.loads((ROOT / candidate.PRESERVED_RUNTIME_PATH).read_text())['source_sha256']
        self.assertEqual(len(frozen), 497)
        for path, expected in frozen.items():
            historical = candidate.CURRENT_HISTORICAL_RUNTIME_RELOCATIONS.get(path, path)
            self.assertEqual(current['source_sha256'][historical], expected)
        self.assertEqual(len(check.SOURCE_PATHS), 63)
        self.assertEqual(len(capture.BOUND_FILES), 4)
        self.assertIs(current['release_authorized'], False)

    def test_closed_descriptor_rejects_scope_identity_and_runtime_boundary_changes(self):
        current = candidate.load_replay_contract(ROOT)
        previous = self.previous()
        original = json.loads((ROOT / MIGRATION).read_text())
        def validate(value):
            candidate.validate_swift_forward_migration(
                value, current['source_sha256'], previous['source_sha256'], ROOT)
        validate(original)
        for key, value in {
            'schema_version': True, 'identity': 'arbitrary-source-admission',
            'base_source': '0' * 40, 'base_tree': '0' * 40,
            'base_source_kind': 'local-proposal', 'base_source_status': 'native-approved',
            'scope': 'native and release approved', 'release_authorized': True,
            'previous_source_migration_sha256': '0' * 64, 'preserved_runtime_sha256': '0' * 64,
            'base_contract_sha256': {}, 'historical_relocations': {},
            'added_source_sha256': {'crates/flightsim-fdm/src/unreviewed.rs': '0' * 64},
        }.items():
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate({**original, key: value})
        for key in original:
            changed = copy.deepcopy(original)
            del changed[key]
            with self.subTest(missing=key), self.assertRaises(ValueError):
                validate(changed)
        with self.assertRaises(ValueError):
            validate({**original, 'authorization': 'approved'})
        for path in CHANGED:
            for attack in ('omit', 'alias', 'old', 'reseal', 'extra-key'):
                changed = copy.deepcopy(original)
                row = changed['replaced_source_sha256'][path]
                if attack == 'omit':
                    del changed['replaced_source_sha256'][path]
                elif attack == 'alias':
                    changed['replaced_source_sha256'][path.upper()] = changed['replaced_source_sha256'].pop(path)
                elif attack == 'old':
                    row['previous_sha256'] = '0' * 64
                elif attack == 'reseal':
                    row['sha256'] = '0' * 64
                else:
                    row['native_pass'] = True
                with self.subTest(path=path, attack=attack), self.assertRaises(ValueError):
                    validate(changed)
        # Even a descriptor and its corresponding current pin cannot jointly self-reseal.
        for path in CHANGED:
            changed = copy.deepcopy(original)
            changed['replaced_source_sha256'][path]['sha256'] = '0' * 64
            with self.subTest(resealed=path), self.assertRaises(ValueError):
                candidate.validate_swift_forward_migration(changed,
                    {**current['source_sha256'], path: '0' * 64}, previous['source_sha256'], ROOT)

    def test_contract_rejects_repins_missing_aliases_and_old_authority(self):
        positive = candidate.load_replay_contract(ROOT)
        for path in CHANGED | ADDED | {'Cargo.toml', 'Cargo.lock',
                                      'crates/flightsim-fdm/src/aircraft.rs'}:
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
        for key, value in [('contract', candidate.ALPHA24_REPLAY_CONTRACT_ID),
                           ('source_migration_sha256', candidate.ALPHA24_MIGRATION_SHA256),
                           ('scope', 'publication approved'), ('release_authorized', True)]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                candidate.validate_replay_contract({**positive, key: value})

    def test_historical_ci_layer_and_unrelated_analytical_inputs_remain_fixed(self):
        previous = json.loads((ROOT / check.SWIFT_FORWARD_BASE_CONTRACT_PATH).read_text())
        current = json.loads((ROOT / check.ALPHA25_BASE_CONTRACT_PATH).read_text())
        check.validate_ci_timeout_admission(ROOT, previous['source_sha256'])
        check.validate_swift_forward_admission(ROOT, current['source_sha256'])
        self.assertEqual(len(previous['source_sha256']), 61)
        self.assertEqual(set(current['source_sha256']) - set(previous['source_sha256']),
                         check.SWIFT_FORWARD_SOURCE_PATHS)
        self.assertEqual({p for p, h in previous['source_sha256'].items()
                          if current['source_sha256'][p] != h}, check.SWIFT_FORWARD_REBOUND_PATHS)
        for path in set(previous['source_sha256']) - check.SWIFT_FORWARD_REBOUND_PATHS:
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'unrelated analytical'):
                check.validate_swift_forward_admission(ROOT, {**current['source_sha256'], path: '0' * 64})
        for path in check.SWIFT_FORWARD_SOURCE_PATHS:
            changed = dict(current['source_sha256'])
            del changed[path]
            with self.assertRaises(ValueError):
                check.validate_swift_forward_admission(ROOT, changed)

    def test_actual_capture_rejects_committed_drift_without_published_git_objects(self):
        repo, _ = self.fixture()
        result = subprocess.run(['git', 'cat-file', '-e', candidate.SWIFT_FORWARD_BASE_SOURCE + '^{commit}'],
                                cwd=repo, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        for relative in sorted(CHANGED | ADDED):
            path = repo / relative
            original = path.read_bytes()
            path.write_bytes(original + b'\n')
            with self.subTest(path=relative), self.assertRaises(ValueError):
                capture.source_evidence(repo, self.commit(repo))
            path.write_bytes(original)
            capture.source_evidence(repo, self.commit(repo))

    def test_hidden_checkout_edits_cannot_bypass_canonical_runtime_pins(self):
        repo, _ = self.fixture()
        for relative in sorted(CHANGED):
            path = repo / relative
            original = path.read_bytes()
            subprocess.run(['git', 'update-index', '--assume-unchanged', relative], cwd=repo, check=True)
            try:
                path.write_bytes(original + b'\n')
                self.assertEqual(candidate.git(repo, 'status', '--porcelain'), '')
                with self.subTest(path=relative), self.assertRaisesRegex(ValueError, 'checkout differs'):
                    capture.source_evidence(repo, candidate.git(repo, 'rev-parse', 'HEAD'))
            finally:
                path.write_bytes(original)
                subprocess.run(['git', 'update-index', '--no-assume-unchanged', relative], cwd=repo, check=True)

    def test_resealed_runtime_and_manifest_cannot_authorize_themselves(self):
        repo, _ = self.fixture()
        relative = 'crates/flightsim-render/src/cockpit.rs'
        path = repo / relative
        path.write_bytes(path.read_bytes() + b'\n// unreviewed view change\n')
        changed_hash = candidate.digest(path)
        migration = json.loads((repo / MIGRATION).read_text())
        migration['replaced_source_sha256'][relative]['sha256'] = changed_hash
        capture.write_json(repo / MIGRATION, migration)
        contract = json.loads((repo / candidate.REPLAY_CONTRACT_PATH).read_text())
        contract['source_sha256'][relative] = changed_hash
        contract['source_sha256'][MIGRATION] = candidate.digest(repo / MIGRATION)
        contract['source_migration_sha256'] = candidate.digest(repo / MIGRATION)
        capture.write_json(repo / candidate.REPLAY_CONTRACT_PATH, contract)
        with self.assertRaisesRegex(ValueError, 'identity or scope changed'):
            capture.source_evidence(repo, self.commit(repo))

    def test_export_rejects_missing_forged_and_resealed_runtime_evidence(self):
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
                    digest = hashlib.sha256(changed['replay_contract_text'].encode()).hexdigest()
                    changed['replay_contract_sha256'] = digest
                    changed_report['replay_contract_sha256'] = digest
                with self.subTest(path=relative, attack=attack), self.assertRaises(ValueError):
                    candidate.validate_source_evidence(changed, changed_report)


if __name__ == '__main__':
    unittest.main()
