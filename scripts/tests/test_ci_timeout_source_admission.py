"""Exact CI-budget-only admission; no test removal or runtime/release qualification."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    'ci_timeout_source_fixture', ROOT / 'scripts/tests/test_component_terms_source_admission.py')
fixture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture_module)
capture = fixture_module.capture
check = capture.check
candidate = check.candidate


class CiTimeoutSourceAdmissionTests(unittest.TestCase):
    fixture = fixture_module.ComponentTermsSourceAdmissionTests.fixture
    commit = staticmethod(fixture_module.ComponentTermsSourceAdmissionTests.commit)

    def pins(self):
        return json.loads((ROOT / check.SWIFT_FORWARD_BASE_CONTRACT_PATH).read_text())['source_sha256']

    def workflow_bytes(self):
        return ((ROOT / check.CI_TIMEOUT_HISTORY_PATH).read_bytes(),
                (ROOT / check.CI60_HISTORY_PATH).read_bytes())

    def test_exact_single_budget_change_preserves_all_tests_and_runtime_contracts(self):
        previous, current = self.workflow_bytes()
        check.validate_ci_timeout_delta(previous, current)
        before, after = previous.splitlines(), current.splitlines()
        self.assertEqual(len(before), len(after))
        self.assertEqual([(a, b) for a, b in zip(before, after) if a != b],
                         [(b'    timeout-minutes: 30', b'    timeout-minutes: 45')])
        pins = self.pins()
        check.validate_ci_timeout_admission(ROOT, pins)
        historical = json.loads((ROOT / check.CI_TIMEOUT_BASE_CONTRACT_PATH).read_text())
        self.assertEqual(len(historical['source_sha256']), 57)
        self.assertEqual(len(pins), 61)
        self.assertEqual(set(pins) - set(historical['source_sha256']), check.CI_TIMEOUT_SOURCE_PATHS)
        changed = {p for p, value in historical['source_sha256'].items() if pins[p] != value}
        self.assertEqual(changed, check.CI_TIMEOUT_REBOUND_PATHS)
        replay = json.loads((ROOT / candidate.SWIFT_FORWARD_BASE_CONTRACT_PATH).read_text())
        candidate.validate_alpha24_replay_contract(replay)
        self.assertEqual(len(replay['source_sha256']), 974)
        self.assertEqual(candidate.digest(ROOT / candidate.SWIFT_FORWARD_BASE_CONTRACT_PATH),
                         historical['source_sha256'][candidate.REPLAY_CONTRACT_PATH])
        self.assertEqual(pins['scripts/check-swift-windows-candidate.py'],
                         historical['source_sha256']['scripts/check-swift-windows-candidate.py'])
        self.assertIs(replay['release_authorized'], False)

    def test_whole_workflow_mutations_are_rejected(self):
        previous, current = self.workflow_bytes()
        mutations = [
            (b'timeout-minutes: 45', b'timeout-minutes: 30'),
            (b'timeout-minutes: 45', b'timeout-minutes: 46'),
            (b'timeout-minutes: 45', b'timeout-minutes: 90'),
            (b'timeout-minutes: 10', b'timeout-minutes: 45'),
            (b'timeout-minutes: 90', b'timeout-minutes: 45'),
            (b'contents: read', b'contents: write'),
            (b'branches: [main]', b'branches: [unreviewed]'),
            (b'runs-on: ubuntu-latest', b'runs-on: windows-latest'),
            (b'-m unittest discover -s scripts/tests -v', b'-m unittest scripts.tests.test_ci_timeout_source_admission -v'),
            (b'numpy==2.3.5', b'numpy==2.4.0'),
            (b'python3 -m venv', b'python3 -m skipped'),
            (b'    steps:\n', b'    if: false\n    steps:\n'),
        ]
        for old, new in mutations:
            self.assertIn(old, current)
            with self.subTest(old=old), self.assertRaisesRegex(ValueError, 'outside exact'):
                check.validate_ci_timeout_delta(previous, current.replace(old, new, 1))
        for changed in (current + b'\n', current.replace(b'\n', b'\r\n'), current[:-1],
                        current.replace(b'    timeout-minutes: 45\n', b'')):
            with self.assertRaises(ValueError):
                check.validate_ci_timeout_delta(previous, changed)

    def test_bad_previous_workflow_cannot_authorize_identical_unrelated_changes(self):
        previous, current = self.workflow_bytes()
        for before, after in [(previous + b'\n', current + b'\n'),
                              (previous.replace(b'contents: read', b'contents: write'),
                               current.replace(b'contents: read', b'contents: write'))]:
            with self.assertRaisesRegex(ValueError, 'historical workflow changed'):
                check.validate_ci_timeout_delta(before, after)
        for before, after in [(None, current), (previous, current.decode()),
                              (b'', current), (previous, b' ' * (1024 * 1024 + 1))]:
            with self.assertRaisesRegex(ValueError, 'byte boundary'):
                check.validate_ci_timeout_delta(before, after)

    def test_unrelated_prior_pins_and_new_member_boundaries_cannot_be_resealed(self):
        positive = self.pins()
        for path in ('scripts/check-release-authorization.py', 'Cargo.toml', 'Cargo.lock',
                     'scripts/check-swift-windows-candidate.py', candidate.REPLAY_CONTRACT_PATH):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'unrelated analytical'):
                check.validate_ci_timeout_admission(ROOT, {**positive, path: '0' * 64})
        for path in check.CI_TIMEOUT_SOURCE_PATHS:
            for attack in ('omit', 'alias', 'extra'):
                changed = dict(positive)
                if attack == 'omit':
                    del changed[path]
                elif attack == 'alias':
                    changed[path.upper()] = changed.pop(path)
                else:
                    changed[path + '.unreviewed'] = '0' * 64
                with self.subTest(path=path, attack=attack), self.assertRaises(ValueError):
                    check.validate_ci_timeout_admission(ROOT, changed)
        for path in (check.CI_TIMEOUT_HISTORY_PATH, check.CI_TIMEOUT_BASE_CONTRACT_PATH,
                     check.CI_TIMEOUT_MIGRATION_PATH, check.CI_TIMEOUT_WORKFLOW_PATH):
            with self.subTest(path=path), self.assertRaises(ValueError):
                check.validate_ci_timeout_admission(ROOT, {**positive, path: '0' * 64})

    def test_changed_workflow_or_manifest_cannot_self_authorize_with_resealed_hashes(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            paths = {check.CI_TIMEOUT_MIGRATION_PATH, check.CI_TIMEOUT_BASE_CONTRACT_PATH,
                     check.CI_TIMEOUT_HISTORY_PATH, check.CI60_HISTORY_PATH}
            for path in paths:
                destination = repo / path
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((ROOT / path).read_bytes())
            pins = self.pins()
            check.validate_ci_timeout_admission(repo, pins)
            for path in paths:
                original = (repo / path).read_bytes()
                changed = original + b'\n'
                (repo / path).write_bytes(changed)
                pin = check.CI_TIMEOUT_WORKFLOW_PATH if path == check.CI60_HISTORY_PATH else path
                with self.subTest(path=path), self.assertRaises(ValueError):
                    check.validate_ci_timeout_admission(repo, {**pins, pin: hashlib.sha256(changed).hexdigest()})
                (repo / path).write_bytes(original)
            original = json.loads((repo / check.CI_TIMEOUT_MIGRATION_PATH).read_text())
            for key, value in [('release_authorized', True), ('schema_version', True),
                               ('base_source', '0' * 40), ('scope', 'skip tests and authorize release')]:
                changed = {**original, key: value}
                data = (json.dumps(changed, indent=2, sort_keys=True) + '\n').encode()
                (repo / check.CI_TIMEOUT_MIGRATION_PATH).write_bytes(data)
                with self.subTest(field=key), self.assertRaises(ValueError):
                    check.validate_ci_timeout_admission(repo, {**pins,
                        check.CI_TIMEOUT_MIGRATION_PATH: hashlib.sha256(data).hexdigest()})

    def test_actual_capture_accepts_clean_fixture_and_rejects_committed_workflow_drift(self):
        repo, source = self.fixture()
        result = subprocess.run(['git', 'cat-file', '-e',
            'c84b8aa97d38250ddb1c5495e2d65e3917be8b4c^{commit}'], cwd=repo, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(source['analytical_contract']['source_admission'], check.SOURCE_ADMISSION)
        for relative in (check.CI_TIMEOUT_WORKFLOW_PATH, check.CI_TIMEOUT_MIGRATION_PATH,
                         check.CI_TIMEOUT_HISTORY_PATH, check.CI_TIMEOUT_BASE_CONTRACT_PATH,
                         check.CI60_HISTORY_PATH):
            path = repo / relative
            original = path.read_bytes()
            path.write_bytes(original + b'\n')
            with self.subTest(path=relative), self.assertRaises(ValueError):
                capture.source_evidence(repo, self.commit(repo))
            path.write_bytes(original)
            capture.source_evidence(repo, self.commit(repo))


if __name__ == '__main__':
    unittest.main()
