"""Bounded urban source successor; never native, assent or publication evidence."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    'urban_source_fixture', ROOT / 'scripts/tests/test_component_terms_source_admission.py')
fixture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture_module)
capture = fixture_module.capture
check = capture.check
candidate = check.candidate


class UrbanSourceAdmissionTests(unittest.TestCase):
    fixture = fixture_module.ComponentTermsSourceAdmissionTests.fixture
    commit = staticmethod(fixture_module.ComponentTermsSourceAdmissionTests.commit)

    def previous(self):
        return json.loads((ROOT / candidate.URBAN_BASE_CONTRACT_PATH).read_text())

    def test_exact_boundary_retains_all_prior_bytes_and_unrelated_authorities(self):
        current = candidate.load_replay_contract(ROOT)
        previous = self.previous()
        candidate.validate_alpha26_replay_contract(previous)
        self.assertEqual(len(previous['source_sha256']), 1001)
        self.assertEqual(len(current['source_sha256']), 1022)
        self.assertEqual(len(candidate.URBAN_PREVIOUS_SHA256), 9)
        self.assertEqual(len(candidate.URBAN_ADDED_SHA256), 8)
        self.assertEqual(len(candidate.CURRENT_CRATE_SOURCE_PATHS), 503)
        self.assertEqual(len(candidate.INDEPENDENT_REPLAY_HASHES), 102)
        self.assertEqual(set(current['source_sha256']) - set(previous['source_sha256']),
                         candidate.URBAN_SOURCE_PATHS)
        self.assertEqual({p for p, h in previous['source_sha256'].items()
                          if current['source_sha256'][p] != h}, set(candidate.URBAN_PREVIOUS_SHA256))
        for path, expected in previous['source_sha256'].items():
            historical = candidate.URBAN_HISTORICAL_RELOCATIONS.get(path, path)
            self.assertEqual(current['source_sha256'][historical], expected, path)
            self.assertEqual(candidate.digest(ROOT / historical), expected, path)
        for path in ('scripts/check-release-authorization.py', 'scripts/stage-commercial-candidate.py',
                     'crates/flightsim-app/src/component_terms.rs',
                     'crates/flightsim-app/src/component_terms_dialog.ps1', '.github/workflows/ci.yml'):
            prior = json.loads((ROOT / check.URBAN_BASE_CONTRACT_PATH).read_text())['source_sha256']
            self.assertEqual(candidate.digest(ROOT / path), prior[path], path)
        self.assertIs(current['release_authorized'], False)
        self.assertEqual(current['scope'], candidate.SOURCE_ADMISSION_SCOPE)
        before = (ROOT / candidate.URBAN_HISTORICAL_RELOCATIONS['.gitattributes']).read_bytes()
        self.assertEqual((ROOT / '.gitattributes').read_bytes(),
                         before.replace(b'*.fsclim binary\n', b'*.fsclim binary\n*.fsua binary\n'))

    def test_descriptor_and_contract_cannot_jointly_reseal_or_claim_acceptance(self):
        current = candidate.load_replay_contract(ROOT)
        previous = self.previous()['source_sha256']
        original = json.loads((ROOT / candidate.URBAN_MIGRATION_PATH).read_text())
        def validate(value, pins=None):
            candidate.validate_urban_migration(value, pins or current['source_sha256'], previous, ROOT)
        validate(original)
        for key, value in {'schema_version': True, 'base_source': '0' * 40,
                           'base_tree': '0' * 40, 'release_authorized': True,
                           'scope': 'native and distribution approved',
                           'historical_relocations': {}, 'base_contract_sha256': {},
                           'previous_source_migration_sha256': '0' * 64}.items():
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate({**original, key: value})
        for key in original:
            changed = copy.deepcopy(original); del changed[key]
            with self.subTest(missing=key), self.assertRaises(ValueError):
                validate(changed)
        for claim in ('native_runtime_qualified', 'recipient_agreed', 'publication_authorized'):
            with self.subTest(claim=claim), self.assertRaises(ValueError):
                validate({**original, claim: True})
        for path in {*candidate.URBAN_PREVIOUS_SHA256, *candidate.URBAN_ADDED_SHA256}:
            changed = copy.deepcopy(original)
            if path in changed['replaced_source_sha256']:
                changed['replaced_source_sha256'][path]['sha256'] = '0' * 64
            else:
                changed['added_source_sha256'][path] = '0' * 64
            with self.subTest(resealed=path), self.assertRaises(ValueError):
                validate(changed, {**current['source_sha256'], path: '0' * 64})
        for path in candidate.URBAN_SOURCE_PATHS | set(candidate.URBAN_PREVIOUS_SHA256):
            for attack in ('omit', 'alias', 'repin'):
                changed = copy.deepcopy(current)
                if attack == 'omit':
                    del changed['source_sha256'][path]
                elif attack == 'alias':
                    changed['source_sha256'][path.upper()] = changed['source_sha256'].pop(path)
                else:
                    changed['source_sha256'][path] = '0' * 64
                with self.subTest(path=path, attack=attack), self.assertRaises(ValueError):
                    candidate.validate_replay_contract(changed)

    def test_analytical_historical_ci_and_release_checks_remain_mandatory(self):
        previous = json.loads((ROOT / check.URBAN_BASE_CONTRACT_PATH).read_text())
        current = json.loads((ROOT / check.CONTRACT).read_text())
        check.validate_ci60_admission(ROOT, previous['source_sha256'])
        check.validate_urban_admission(ROOT, current['source_sha256'])
        self.assertEqual(len(previous['source_sha256']), 69)
        self.assertEqual(len(current['source_sha256']), 70)
        self.assertEqual(len(capture.BOUND_FILES), 4)
        for path in check.CI60_ADMISSION_SOURCE_PATHS - check.URBAN_REBOUND_PATHS:
            with self.subTest(unrelated=path), self.assertRaisesRegex(ValueError, 'unrelated analytical'):
                check.validate_urban_admission(ROOT, {**current['source_sha256'], path: '0' * 64})
        for path in check.URBAN_SOURCE_PATHS:
            changed = dict(current['source_sha256']); del changed[path]
            with self.assertRaises(ValueError):
                check.validate_urban_admission(ROOT, changed)

    def test_actual_source_rejects_code_data_and_history_drift_without_base_objects(self):
        repo, _ = self.fixture()
        result = subprocess.run(['git', 'cat-file', '-e', candidate.URBAN_BASE_SOURCE + '^{commit}'],
                                cwd=repo, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        paths = set(candidate.URBAN_PREVIOUS_SHA256) | candidate.URBAN_SOURCE_PATHS
        for relative in sorted(paths):
            path = repo / relative; original = path.read_bytes()
            path.write_bytes(original + b'\n')
            with self.subTest(path=relative), self.assertRaises(ValueError):
                capture.source_evidence(repo, self.commit(repo))
            path.write_bytes(original)
        capture.source_evidence(repo, self.commit(repo))

    def test_hidden_checkout_and_resealed_source_bundle_are_rejected(self):
        repo, _ = self.fixture()
        relative = 'crates/flightsim-world/data/natural-earth-urban.fsua'
        path = repo / relative; original = path.read_bytes()
        subprocess.run(['git', 'update-index', '--assume-unchanged', relative], cwd=repo, check=True)
        try:
            path.write_bytes(original + b'\0')
            self.assertEqual(candidate.git(repo, 'status', '--porcelain'), '')
            with self.assertRaisesRegex(ValueError, 'checkout differs'):
                capture.source_evidence(repo, candidate.git(repo, 'rev-parse', 'HEAD'))
        finally:
            path.write_bytes(original)
            subprocess.run(['git', 'update-index', '--no-assume-unchanged', relative], cwd=repo, check=True)
        path.write_bytes(original + b'\0')
        migration = json.loads((repo / candidate.URBAN_MIGRATION_PATH).read_text())
        migration['added_source_sha256'][relative] = candidate.digest(path)
        capture.write_json(repo / candidate.URBAN_MIGRATION_PATH, migration)
        contract = json.loads((repo / candidate.REPLAY_CONTRACT_PATH).read_text())
        contract['source_sha256'][relative] = candidate.digest(path)
        contract['source_sha256'][candidate.URBAN_MIGRATION_PATH] = candidate.digest(repo / candidate.URBAN_MIGRATION_PATH)
        contract['source_migration_sha256'] = candidate.digest(repo / candidate.URBAN_MIGRATION_PATH)
        capture.write_json(repo / candidate.REPLAY_CONTRACT_PATH, contract)
        with self.assertRaisesRegex(ValueError, 'identity or scope changed'):
            capture.source_evidence(repo, self.commit(repo))

    def test_export_cannot_omit_forge_or_reseal_current_geometry_evidence(self):
        _, source = self.fixture()
        report = {'source_sha': source['source_sha'], 'replay_contract': candidate.REPLAY_CONTRACT_ID,
                  'replay_contract_sha256': source['replay_contract_sha256']}
        candidate.validate_source_evidence(source, report)
        for relative in candidate.URBAN_RUNTIME_PATHS | {'crates/flightsim-app/src/scenery_runtime.rs'}:
            for attack in ('omit', 'canonical', 'reseal'):
                changed = copy.deepcopy(source); changed_report = dict(report)
                if attack == 'omit':
                    del changed['reviewed_replay_source_evidence'][relative]
                elif attack == 'canonical':
                    changed['reviewed_replay_source_evidence'][relative]['canonical_sha256'] = '0' * 64
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
