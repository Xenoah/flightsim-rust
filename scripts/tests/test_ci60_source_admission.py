"""Exact second CI ceiling amendment; no test removal or runtime qualification."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    'ci60_source_fixture', ROOT / 'scripts/tests/test_component_terms_source_admission.py')
fixture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture_module)
capture = fixture_module.capture
check = capture.check
candidate = check.candidate


class Ci60SourceAdmissionTests(unittest.TestCase):
    fixture = fixture_module.ComponentTermsSourceAdmissionTests.fixture
    commit = staticmethod(fixture_module.ComponentTermsSourceAdmissionTests.commit)

    def pins(self):
        return json.loads((ROOT / check.URBAN_BASE_CONTRACT_PATH).read_text())['source_sha256']

    def workflow_bytes(self):
        return ((ROOT / check.CI60_HISTORY_PATH).read_bytes(),
                (ROOT / check.CI_TIMEOUT_WORKFLOW_PATH).read_bytes())

    def test_exact_single_budget_change_retains_both_historical_layers(self):
        previous, current = self.workflow_bytes()
        check.validate_ci60_delta(previous, current)
        self.assertEqual(len(previous), len(current))
        self.assertEqual([(a, b) for a, b in zip(previous.splitlines(), current.splitlines()) if a != b],
                         [(b'    timeout-minutes: 45', b'    timeout-minutes: 60')])
        check.validate_ci_timeout_delta((ROOT / check.CI_TIMEOUT_HISTORY_PATH).read_bytes(), previous)
        historical = json.loads((ROOT / check.CI60_BASE_CONTRACT_PATH).read_text())
        check.validate_alpha26_admission(ROOT, historical['source_sha256'])
        current = self.pins()
        check.validate_ci60_admission(ROOT, current)
        self.assertEqual(len(historical['source_sha256']), 65)
        self.assertEqual(len(current), 69)
        self.assertEqual(set(current) - set(historical['source_sha256']), check.CI60_SOURCE_PATHS)
        self.assertEqual({p for p, h in historical['source_sha256'].items() if current[p] != h},
                         check.CI60_REBOUND_PATHS)
        for path in (candidate.REPLAY_CONTRACT_PATH, 'scripts/check-swift-windows-candidate.py',
                     'Cargo.toml', 'Cargo.lock', 'scripts/check-release-authorization.py'):
            self.assertEqual(current[path], historical['source_sha256'][path])
        self.assertEqual(len(candidate.ALPHA26_REPLAY_CONTRACT_PATHS), 1001)
        self.assertEqual(len(capture.BOUND_FILES), 4)
        self.assertIs(candidate.load_replay_contract(ROOT)['release_authorized'], False)

    def test_complete_workflow_mutations_are_rejected(self):
        previous, current = self.workflow_bytes()
        mutations = [
            (b'timeout-minutes: 60', b'timeout-minutes: 45'),
            (b'timeout-minutes: 60', b'timeout-minutes: 61'),
            (b'timeout-minutes: 60', b'timeout-minutes: 90'),
            (b'timeout-minutes: 10', b'timeout-minutes: 60'),
            (b'contents: read', b'contents: write'),
            (b'branches: [main]', b'branches: [unreviewed]'),
            (b'runs-on: ubuntu-latest', b'runs-on: windows-latest'),
            (b'-m unittest discover -s scripts/tests -v', b'-m unittest scripts.tests.test_ci60_source_admission -v'),
            (b'numpy==2.3.5', b'numpy==2.4.0'),
            (b'python3 -m venv', b'python3 -m skipped'),
            (b'    steps:\n', b'    if: false\n    steps:\n'),
        ]
        for old, new in mutations:
            self.assertIn(old, current)
            with self.subTest(old=old), self.assertRaisesRegex(ValueError, 'outside exact'):
                check.validate_ci60_delta(previous, current.replace(old, new, 1))
        for changed in (current + b'\n', current.replace(b'\n', b'\r\n'), current[:-1],
                        current.replace(b'    timeout-minutes: 60\n', b'')):
            with self.assertRaises(ValueError):
                check.validate_ci60_delta(previous, changed)

    def test_bad_previous_cannot_authorize_matching_unrelated_changes(self):
        previous, current = self.workflow_bytes()
        for before, after in [(previous + b'\n', current + b'\n'),
                              (previous.replace(b'contents: read', b'contents: write'),
                               current.replace(b'contents: read', b'contents: write'))]:
            with self.assertRaisesRegex(ValueError, 'historical workflow changed'):
                check.validate_ci60_delta(before, after)
        for before, after in [(None, current), (previous, current.decode()),
                              (b'', current), (previous, b' ' * (1024 * 1024 + 1))]:
            with self.assertRaisesRegex(ValueError, 'byte boundary'):
                check.validate_ci60_delta(before, after)

    def test_prior_pins_and_new_member_boundaries_cannot_be_resealed(self):
        pins = self.pins()
        for path in check.ALPHA26_ADMISSION_SOURCE_PATHS - check.CI60_REBOUND_PATHS:
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'unrelated analytical'):
                check.validate_ci60_admission(ROOT, {**pins, path: '0' * 64})
        for path in check.CI60_SOURCE_PATHS:
            for attack in ('omit', 'alias', 'extra'):
                changed = dict(pins)
                if attack == 'omit':
                    del changed[path]
                elif attack == 'alias':
                    changed[path.upper()] = changed.pop(path)
                else:
                    changed[path + '.extra'] = '0' * 64
                with self.subTest(path=path, attack=attack), self.assertRaises(ValueError):
                    check.validate_ci60_admission(ROOT, changed)
        for path in (check.CI60_MIGRATION_PATH, check.CI60_HISTORY_PATH,
                     check.CI60_BASE_CONTRACT_PATH, check.CI_TIMEOUT_WORKFLOW_PATH):
            with self.subTest(repin=path), self.assertRaises(ValueError):
                check.validate_ci60_admission(ROOT, {**pins, path: '0' * 64})

    def test_actual_capture_needs_no_base_object_and_rejects_committed_drift(self):
        repo, _ = self.fixture()
        result = subprocess.run(['git', 'cat-file', '-e',
            '2eb36242cde4ccd3492b0079d4de226ee26db15e^{commit}'], cwd=repo, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        for relative in sorted(check.CI60_SOURCE_PATHS | {check.CI_TIMEOUT_WORKFLOW_PATH}):
            path = repo / relative
            original = path.read_bytes()
            path.write_bytes(original + b'\n')
            with self.subTest(path=relative), self.assertRaises(ValueError):
                capture.source_evidence(repo, self.commit(repo))
            path.write_bytes(original)
            capture.source_evidence(repo, self.commit(repo))

    def test_resealed_workflow_and_descriptor_cannot_authorize_themselves(self):
        repo, _ = self.fixture()
        path = repo / check.CI_TIMEOUT_WORKFLOW_PATH
        path.write_bytes(path.read_bytes().replace(b'timeout-minutes: 60', b'timeout-minutes: 90'))
        migration = json.loads((repo / check.CI60_MIGRATION_PATH).read_text())
        migration['workflow']['timeout_minutes'] = 90
        migration['workflow']['sha256'] = candidate.digest(path)
        capture.write_json(repo / check.CI60_MIGRATION_PATH, migration)
        contract = json.loads((repo / check.CONTRACT).read_text())
        contract['source_sha256'][check.CI_TIMEOUT_WORKFLOW_PATH] = candidate.digest(path)
        contract['source_sha256'][check.CI60_MIGRATION_PATH] = candidate.digest(repo / check.CI60_MIGRATION_PATH)
        capture.write_json(repo / check.CONTRACT, contract)
        with self.assertRaisesRegex(ValueError, 'CI60 migration changed'):
            capture.source_evidence(repo, self.commit(repo))

    def test_descriptor_retains_source_only_scope_and_rejects_resealed_claims(self):
        repo, _ = self.fixture()
        path = repo / check.CI60_MIGRATION_PATH
        original = json.loads(path.read_text())
        self.assertIs(original['release_authorized'], False)
        self.assertEqual(original['base_source_kind'], 'public-pull-request-commit')
        self.assertEqual(original['runtime_source_migration_sha256'], candidate.ALPHA26_MIGRATION_SHA256)
        self.assertNotIn('runtime_accepted', original)
        self.assertNotIn('distribution_qualified', original)
        for key, value in [('schema_version', True), ('release_authorized', True),
                           ('base_source', '0' * 40), ('scope', 'native and distribution approved')]:
            changed = copy.deepcopy(original)
            changed[key] = value
            capture.write_json(path, changed)
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'CI60 migration changed'):
                check.validate_ci60_admission(repo, {**self.pins(),
                    check.CI60_MIGRATION_PATH: hashlib.sha256(path.read_bytes()).hexdigest()})


if __name__ == '__main__':
    unittest.main()
