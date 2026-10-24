"""Exact version-only successor preserves urban source and all acceptance gates."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    'alpha27_fixture', ROOT / 'scripts/tests/test_component_terms_source_admission.py')
fixture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture_module)
capture = fixture_module.capture
candidate = capture.check.candidate
check = capture.check


class Alpha27VersionSourceAdmissionTests(unittest.TestCase):
    fixture = fixture_module.ComponentTermsSourceAdmissionTests.fixture
    commit = staticmethod(fixture_module.ComponentTermsSourceAdmissionTests.commit)

    def version_bytes(self):
        paths = candidate.ALPHA27_HISTORICAL_RELOCATIONS
        return ({p: (ROOT / h).read_bytes() for p, h in paths.items()},
                {p: (ROOT / p).read_bytes() for p in paths})

    def test_exact_version_delta_retains_complete_urban_history(self):
        current = candidate.load_replay_contract(ROOT)
        prior = json.loads((ROOT / candidate.ALPHA27_BASE_CONTRACT_PATH).read_text())
        candidate.validate_urban_replay_contract(prior)
        self.assertEqual(len(prior['source_sha256']), 1022)
        self.assertEqual(len(current['source_sha256']), 1028)
        self.assertEqual(set(current['source_sha256']) - set(prior['source_sha256']),
                         candidate.ALPHA27_SOURCE_PATHS)
        changed = {p for p, h in prior['source_sha256'].items() if current['source_sha256'][p] != h}
        self.assertEqual(changed, {'Cargo.toml', 'Cargo.lock'})
        for p, h in prior['source_sha256'].items():
            historical = candidate.ALPHA27_HISTORICAL_RELOCATIONS.get(p, p)
            self.assertEqual(current['source_sha256'][historical], h, p)
            self.assertEqual(candidate.digest(ROOT / historical), h, p)
        candidate.validate_alpha27_version_delta(*self.version_bytes())
        self.assertEqual(len(candidate.CURRENT_CRATE_SOURCE_PATHS), 503)
        self.assertEqual(len(candidate.INDEPENDENT_REPLAY_HASHES), 102)
        self.assertEqual(len(check.SOURCE_PATHS), 71)
        self.assertEqual(len(capture.BOUND_FILES), 4)
        self.assertIs(current['release_authorized'], False)

    def test_version_semantics_reject_more_than_exact_substitution(self):
        before, after = self.version_bytes()
        for path in before:
            for suffix in (b'\n', b'\n# unreviewed\n'):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    candidate.validate_alpha27_version_delta(before, {**after, path: after[path] + suffix})
        for path, old, new in [('Cargo.toml', b'"crates/flightsim-net",', b'"crates/extra",'),
                               ('Cargo.lock', b'name = "flightsim-net"', b'name = "extra"')]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                candidate.validate_alpha27_version_delta(
                    {**before, path: before[path].replace(old, new)},
                    {**after, path: after[path].replace(old, new)})
        sections = after['Cargo.lock'].split(b'[[package]]')
        for chunks in (sections[:1] + [sections[2], sections[1]] + sections[3:],
                       sections + [sections[-1]], sections[:-1]):
            with self.assertRaises(ValueError):
                candidate.validate_alpha27_version_delta(before, {**after, 'Cargo.lock': b'[[package]]'.join(chunks)})

    def test_current_pins_reject_omission_alias_and_repin(self):
        current = candidate.load_replay_contract(ROOT)
        for path in candidate.ALPHA27_SOURCE_PATHS | {'Cargo.toml', 'Cargo.lock'}:
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

    def test_source_admission_cannot_supply_native_assent_or_publication(self):
        current = candidate.load_replay_contract(ROOT)
        for key, value in [('release_authorized', True), ('native_runtime_qualified', True),
                           ('recipient_agreed', True), ('base_reviewed_source', candidate.ALPHA27_BASE_SOURCE),
                           ('scope', 'approved for release'), ('source_migration_sha256', candidate.URBAN_MIGRATION_SHA256)]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                candidate.validate_replay_contract({**current, key: value})

    def test_historical_analytical_proof_and_unrelated_checks_remain_required(self):
        current = json.loads((ROOT / check.CONTRACT).read_text())
        prior = json.loads((ROOT / check.ALPHA27_BASE_CONTRACT_PATH).read_text())
        check.validate_alpha27_admission(ROOT, current['source_sha256'])
        check.validate_urban_admission(ROOT, prior['source_sha256'])
        self.assertEqual(len(prior['source_sha256']), 70)
        for path in check.URBAN_ADMISSION_SOURCE_PATHS - check.ALPHA27_REBOUND_PATHS:
            with self.subTest(path=path), self.assertRaises(ValueError):
                check.validate_alpha27_admission(ROOT, {**current['source_sha256'], path: '0' * 64})

    def test_actual_version_and_descriptor_drift_are_rejected(self):
        repo, _ = self.fixture()
        for relative in candidate.ALPHA27_SOURCE_PATHS | {'Cargo.toml', 'Cargo.lock'}:
            path = repo / relative
            before = path.read_bytes()
            path.write_bytes(before + b'\n')
            with self.subTest(path=relative), self.assertRaises(ValueError):
                capture.source_evidence(repo, self.commit(repo))
            path.write_bytes(before)
        capture.source_evidence(repo, self.commit(repo))

    def test_joint_descriptor_reseal_does_not_admit_changed_code(self):
        repo, _ = self.fixture()
        path = repo / 'Cargo.toml'
        path.write_bytes(path.read_bytes() + b'\n')
        migration = json.loads((repo / candidate.ALPHA27_MIGRATION_PATH).read_text())
        migration['replaced_source_sha256']['Cargo.toml']['sha256'] = candidate.digest(path)
        capture.write_json(repo / candidate.ALPHA27_MIGRATION_PATH, migration)
        contract = json.loads((repo / candidate.REPLAY_CONTRACT_PATH).read_text())
        contract['source_sha256']['Cargo.toml'] = candidate.digest(path)
        contract['source_sha256'][candidate.ALPHA27_MIGRATION_PATH] = candidate.digest(repo / candidate.ALPHA27_MIGRATION_PATH)
        contract['source_migration_sha256'] = candidate.digest(repo / candidate.ALPHA27_MIGRATION_PATH)
        capture.write_json(repo / candidate.REPLAY_CONTRACT_PATH, contract)
        with self.assertRaises(ValueError):
            capture.source_evidence(repo, self.commit(repo))

    def test_exported_current_version_evidence_cannot_be_removed_or_resealed(self):
        _, source = self.fixture()
        report = {'source_sha': source['source_sha'], 'replay_contract': candidate.REPLAY_CONTRACT_ID,
                  'replay_contract_sha256': source['replay_contract_sha256']}
        candidate.validate_source_evidence(source, report)
        for path in ('Cargo.toml', 'Cargo.lock', candidate.ALPHA27_MIGRATION_PATH):
            changed = copy.deepcopy(source)
            del changed['reviewed_replay_source_evidence'][path]
            with self.subTest(path=path), self.assertRaises(ValueError):
                candidate.validate_source_evidence(changed, report)


if __name__ == '__main__':
    unittest.main()
