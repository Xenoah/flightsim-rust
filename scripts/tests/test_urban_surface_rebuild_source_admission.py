"""Bounded building-surface source proof; no native, assent or release authority."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    'surface_fixture', ROOT / 'scripts/tests/test_component_terms_source_admission.py')
fixture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture_module)
capture = fixture_module.capture
check = capture.check
candidate = check.candidate


class SurfaceSourceAdmissionTests(unittest.TestCase):
    fixture = fixture_module.ComponentTermsSourceAdmissionTests.fixture
    commit = staticmethod(fixture_module.ComponentTermsSourceAdmissionTests.commit)

    def test_exact_closure_retains_complete_alpha27_and_all_historical_proofs(self):
        current = candidate.load_replay_contract(ROOT)
        prior = json.loads((ROOT / candidate.SURFACE_BASE_CONTRACT_PATH).read_text())
        candidate.validate_alpha27_replay_contract(prior)
        self.assertEqual(len(prior['source_sha256']), 1028)
        self.assertEqual(len(current['source_sha256']), 1044)
        self.assertEqual(set(current['source_sha256']) - set(prior['source_sha256']),
                         candidate.SURFACE_SOURCE_PATHS)
        changed = {p for p, h in prior['source_sha256'].items() if current['source_sha256'][p] != h}
        self.assertEqual(changed, set(candidate.SURFACE_PREVIOUS_SHA256))
        for p, h in prior['source_sha256'].items():
            old = candidate.SURFACE_HISTORICAL_RELOCATIONS.get(p, p)
            self.assertEqual(current['source_sha256'][old], h)
            self.assertEqual(candidate.digest(ROOT / old), h)
        self.assertEqual(len(candidate.ALPHA27_CRATE_SOURCE_PATHS), 503)
        self.assertEqual(len(candidate.CURRENT_CRATE_SOURCE_PATHS), 506)
        self.assertEqual(len(check.ALPHA27_ADMISSION_SOURCE_PATHS), 71)
        self.assertEqual(len(check.SOURCE_PATHS), 72)
        self.assertEqual(len(capture.BOUND_FILES), 4)
        self.assertIs(current['release_authorized'], False)

    def test_all_surface_pins_reject_omission_alias_and_repin(self):
        original = candidate.load_replay_contract(ROOT)
        for path in candidate.SURFACE_SOURCE_PATHS | set(candidate.SURFACE_PREVIOUS_SHA256):
            for attack in ('omit', 'alias', 'repin'):
                value = copy.deepcopy(original)
                if attack == 'omit':del value['source_sha256'][path]
                elif attack == 'alias':value['source_sha256'][path.upper()] = value['source_sha256'].pop(path)
                else:value['source_sha256'][path] = '0' * 64
                with self.subTest(path=path, attack=attack), self.assertRaises(ValueError):
                    candidate.validate_replay_contract(value)

    def test_descriptor_reseal_cannot_grant_unreviewed_code_or_other_authority(self):
        current = candidate.load_replay_contract(ROOT)
        prior = json.loads((ROOT / candidate.SURFACE_BASE_CONTRACT_PATH).read_text())['source_sha256']
        original = json.loads((ROOT / candidate.SURFACE_MIGRATION_PATH).read_text())
        candidate.validate_surface_migration(original, current['source_sha256'], prior)
        for key in original:
            value = copy.deepcopy(original);del value[key]
            with self.subTest(missing=key), self.assertRaises(ValueError):
                candidate.validate_surface_migration(value, current['source_sha256'], prior)
        for key, value in [('schema_version', True), ('release_authorized', True),
                           ('release_authorized', 0), ('release_authorized', 0.0),
                           ('native_runtime_qualified', True), ('recipient_agreed', True),
                           ('publication_authorized', True), ('scope', 'approved')]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                candidate.validate_surface_migration({**original, key:value}, current['source_sha256'], prior)
        for path in set(candidate.SURFACE_PREVIOUS_SHA256) | set(candidate.SURFACE_ADDED_SHA256):
            value = copy.deepcopy(original)
            if path in value['replaced_source_sha256']:value['replaced_source_sha256'][path]['sha256'] = '0' * 64
            else:value['added_source_sha256'][path] = '0' * 64
            with self.subTest(resealed=path), self.assertRaises(ValueError):
                candidate.validate_surface_migration(value, {**current['source_sha256'], path:'0' * 64}, prior)

    def test_analytical_proof_preserves_unrelated_inputs_and_rejects_new_claims(self):
        pins = json.loads((ROOT / check.CONTRACT).read_text())['source_sha256']
        check.validate_surface_admission(ROOT, pins)
        prior = json.loads((ROOT / check.SURFACE_BASE_CONTRACT_PATH).read_text())
        check.validate_alpha27_admission(ROOT, prior['source_sha256'])
        for path in check.ALPHA27_ADMISSION_SOURCE_PATHS - check.SURFACE_REBOUND_PATHS:
            with self.subTest(path=path), self.assertRaises(ValueError):
                check.validate_surface_admission(ROOT, {**pins, path:'0' * 64})
        for value in ({**pins, 'extra.py':'0' * 64}, {p:h for p,h in pins.items() if p != 'scripts/tests/test_urban_surface_rebuild_source_admission.py'}):
            with self.assertRaises(ValueError):check.validate_surface_admission(ROOT, value)

    def test_actual_runtime_witness_and_descriptor_changes_are_rejected(self):
        repo, _ = self.fixture()
        for path in ['crates/flightsim-render/src/scenery_surface.wgsl',
                     candidate.SURFACE_HISTORICAL_RELOCATIONS['crates/flightsim-render/src/scenery.rs'],
                     candidate.SURFACE_MIGRATION_PATH]:
            p = repo / path;before = p.read_bytes();p.write_bytes(before + b'\n')
            with self.subTest(path=path), self.assertRaises(ValueError):
                capture.source_evidence(repo, self.commit(repo))
            p.write_bytes(before)
        capture.source_evidence(repo, self.commit(repo))

    def test_export_cannot_omit_or_reseal_reviewed_surface_evidence(self):
        _, source = self.fixture()
        report = {'source_sha':source['source_sha'], 'replay_contract':candidate.REPLAY_CONTRACT_ID,
                  'replay_contract_sha256':source['replay_contract_sha256']}
        candidate.validate_source_evidence(source, report)
        for path in candidate.SURFACE_RUNTIME_PATHS | {candidate.SURFACE_MIGRATION_PATH}:
            value = copy.deepcopy(source);del value['reviewed_replay_source_evidence'][path]
            with self.subTest(path=path), self.assertRaises(ValueError):
                candidate.validate_source_evidence(value, report)


if __name__ == '__main__':
    unittest.main()
