"""Recorded-evidence contracts with synthetic files, not real game-playing tests."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

MANIFEST = Path(__file__).resolve().parents[1]
ROOT = MANIFEST.parents[1]
SPEC = importlib.util.spec_from_file_location('game_test_evidence', MANIFEST / 'scripts/game_test_cli.py')
cli = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cli)


class RecordedGameTestingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.session = self.base / 'session.json'
        self.review = self.base / 'review.json'
        self.build = self.base / 'synthetic-build.bin'
        self.build.write_bytes(b'Synthetic protocol fixture; not a runnable game')
        self.log = self.base / 'synthetic-log.txt'
        self.log.write_text('Synthetic input result fixture, not actual game observations')
        self.data = {
            'schema_version': 1, 'run_id': 'protocol-fixture-001',
            'game': {'revision': 'fixture-r1', 'build': {'path': self.build.name, 'sha256': cli.digest(self.build)}},
            'execution': {'kind': 'real_game', 'channel': 'project-harness', 'tool': 'synthetic-test-protocol',
                          'environment': 'unit-test fixtures only', 'tester': 'qa-context', 'implementation_actor': 'implementer-context'},
            'cases': [{'id': 'FLOW-001', 'required': True, 'expected': 'Fixture expected observation', 'actual': 'Fixture actual observation',
                       'status': 'passed', 'normal_input': True, 'steps': ['Fixture launch', 'Fixture input and observed assertion'],
                       'input_events': [{'kind': 'key_down', 'code': 'Space', 't_ms': 0}, {'kind': 'key_up', 'code': 'Space', 't_ms': 50}],
                       'evidence': [{'path': self.log.name, 'sha256': cli.digest(self.log), 'kind': 'log'}]}]}
        self.write()

    def write(self):
        self.session.write_text(json.dumps(self.data))

    def review_record(self, verdict='passed'):
        value = {'schema_version': 1, 'review_status': 'completed', 'reviewer': 'independent-review-context',
                 'independent_context': True, 'reviewed_revision': 'fixture-r1', 'reviewed_session_sha256': cli.digest(self.session),
                 'verdict': verdict, 'approved_revision': 'fixture-r1' if verdict == 'passed' else None}
        self.review.write_text(json.dumps(value))
        return value

    def command(self, *args):
        return subprocess.run([sys.executable, '-B', str(MANIFEST / 'scripts/game_test_cli.py'), 'check', *map(str, args)],
                              capture_output=True, text=True, timeout=15, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})

    def test_synthetic_passing_record_and_independent_review_bind_exact_input(self):
        self.review_record()
        before = {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.base.iterdir()}
        record = cli.check(self.session, self.review, True)
        self.assertEqual(record['status'], 'passed')
        self.assertEqual(record['validation_status'], 'passed')
        self.assertEqual(record['review_verdict'], 'passed')
        self.assertEqual(record['counts']['passed'], 1)
        self.assertIn('not truth of observations', record['limitation'])
        self.assertEqual(before, {p.name: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.base.iterdir()})

    def test_pending_template_is_not_run_not_fake_success(self):
        run = self.command('--session', MANIFEST / 'templates/game-test-session.json')
        self.assertEqual(run.returncode, 2)
        self.assertEqual(json.loads(run.stdout)['status'], 'not_run')

    def test_failed_observation_stays_failed_even_if_review_blocked(self):
        self.data['cases'][0]['status'] = 'failed'
        self.write()
        self.review_record('blocked')
        record = cli.check(self.session, self.review, True)
        self.assertEqual(record['status'], 'failed')
        self.assertEqual(record['counts']['failed'], 1)

    def test_required_not_run_and_optional_not_run_are_separate(self):
        case = {'id': 'OTHER', 'required': False, 'expected': 'Future case', 'status': 'not_run', 'reason': 'No device'}
        self.data['cases'].append(case)
        self.write()
        self.assertEqual(cli.check(self.session)['status'], 'passed')
        case['required'] = True
        self.write()
        self.assertEqual(cli.check(self.session)['status'], 'not_run')

    def test_missing_review_and_changes_requested_do_not_pass_gate(self):
        self.assertEqual(cli.check(self.session, require_review=True)['status'], 'not_run')
        self.review_record('changes_requested')
        self.assertEqual(cli.check(self.session, self.review, True)['status'], 'failed')

    def test_stale_review_and_wrong_approved_revision_rejected(self):
        self.review_record()
        self.data['cases'][0]['actual'] = 'new observation'
        self.write()
        with self.assertRaisesRegex(ValueError, 'Stale review'):
            cli.check(self.session, self.review, True)
        value = self.review_record()
        value['approved_revision'] = 'old-revision'
        self.review.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'exact revision'):
            cli.check(self.session, self.review, True)

    def test_self_review_rejected_for_tester_and_implementation_actor(self):
        for actor in ('qa-context', 'implementer-context'):
            value = self.review_record()
            value['reviewer'] = actor
            self.review.write_text(json.dumps(value))
            with self.subTest(actor=actor), self.assertRaisesRegex(ValueError, 'independent context'):
                cli.check(self.session, self.review, True)

    def test_missing_tampered_and_escaped_evidence_rejected(self):
        for value in ('missing.txt', '../outside.txt'):
            self.data['cases'][0]['evidence'][0]['path'] = value
            self.write()
            with self.subTest(path=value), self.assertRaises(ValueError):
                cli.check(self.session)
        self.data['cases'][0]['evidence'][0]['path'] = self.log.name
        self.write()
        self.log.write_text('changed evidence')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            cli.check(self.session)

    def test_build_hash_is_required_for_actual_observations(self):
        self.build.write_bytes(b'changed build')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            cli.check(self.session)

    def test_unreleased_input_nonfinite_and_out_of_order_times_rejected(self):
        cases = [[{'kind': 'key_down', 'code': 'Space', 't_ms': 0}],
                 [{'kind': 'pointer_move', 't_ms': float('nan')}],
                 [{'kind': 'pointer_move', 't_ms': 1}, {'kind': 'pointer_move', 't_ms': 0}],
                 [{'kind': 'key_up', 'code': 'Space', 't_ms': 0}]]
        for events in cases:
            self.data['cases'][0]['input_events'] = events
            self.write()
            with self.subTest(events=events), self.assertRaises(ValueError):
                cli.check(self.session)

    def test_simulation_cannot_claim_real_game_coverage(self):
        self.data['execution']['kind'] = 'simulation'
        self.write()
        with self.assertRaisesRegex(ValueError, 'must stay not_run'):
            cli.check(self.session)
        self.data['cases'][0].update(status='not_run', reason='Simulated fixture, real game absent')
        self.write()
        self.assertEqual(cli.check(self.session)['status'], 'not_run')

    def test_injection_only_does_not_pass_normal_input_gameplay(self):
        self.data['cases'][0]['normal_input'] = False
        self.write()
        with self.assertRaisesRegex(ValueError, 'normal input'):
            cli.check(self.session)

    def test_startup_crash_can_be_recorded_without_fake_player_input(self):
        self.data['cases'][0].update(scope='startup', normal_input=False, status='failed', input_events=[])
        self.write()
        self.assertEqual(cli.check(self.session)['status'], 'failed')

    def test_duplicate_empty_or_no_required_cases_are_invalid(self):
        variations = [[], [copy.deepcopy(self.data['cases'][0]), copy.deepcopy(self.data['cases'][0])],
                      [dict(self.data['cases'][0], required=False)]]
        for cases in variations:
            self.data['cases'] = cases
            self.write()
            with self.subTest(cases=cases), self.assertRaises(ValueError):
                cli.check(self.session)

    def test_supplied_negative_review_is_respected_even_without_require_flag(self):
        for verdict, expected in (('changes_requested', 'failed'), ('blocked', 'not_run')):
            self.review_record(verdict)
            with self.subTest(verdict=verdict):
                self.assertEqual(cli.check(self.session, self.review)['status'], expected)

    def test_identity_whitespace_does_not_bypass_self_review(self):
        value = self.review_record()
        value['reviewer'] = '  qa-context  '
        self.review.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'independent context'):
            cli.check(self.session, self.review, True)

    def test_unknown_event_kind_and_nonzero_gamepad_axis_rejected(self):
        for events in ([{'kind': 'key_dwon', 'code': 'Space', 't_ms': 0}],
                       [{'kind': 'gamepad_axis', 'code': 'LX', 'value': 0.5, 't_ms': 0}]):
            with self.subTest(events=events), self.assertRaises(ValueError):
                cli.input_balance(events)
        cli.input_balance([{'kind': 'gamepad_axis', 'code': 'LX', 'value': 0.5, 't_ms': 0},
                           {'kind': 'gamepad_axis', 'code': 'LX', 'value': 0, 't_ms': 5}])

    def test_build_manifest_checks_actual_referenced_files(self):
        manifest = self.base / 'build-manifest.json'
        manifest.write_text(json.dumps({'schema_version': 1, 'files': [{'path': self.build.name, 'sha256': cli.digest(self.build)}]}))
        self.data['game']['build'] = {'kind': 'manifest', 'path': manifest.name, 'sha256': cli.digest(manifest)}
        self.write()
        self.assertEqual(len(cli.check(self.session)['build']['manifest_files']), 1)
        self.build.unlink()
        with self.assertRaisesRegex(ValueError, 'Missing/empty evidence'):
            cli.check(self.session)

    def test_public_install_includes_game_testing_skills_helper_and_templates(self):
        target = self.base / 'installed game'
        env = {**os.environ, 'VIBE_HOME': str(ROOT), 'PYTHONPATH': str(ROOT / 'tools/vibe_tool/src'), 'PYTHONDONTWRITEBYTECODE': '1'}
        run = subprocess.run([sys.executable, '-B', '-m', 'vibe_tool', 'init', 'unity-game', str(target)],
                             cwd=ROOT, env=env, text=True, capture_output=True, timeout=90)
        self.assertEqual(run.returncode, 0, run.stderr)
        branch = target / '.agents/skills/unity-game-development/unity-game-alpha/unity-game-testing'
        self.assertEqual(len(list(branch.rglob('SKILL.md'))), 8)
        for relative in ('scripts/game_test_cli.py', 'references/game-testing.md', 'templates/game-test-session.json',
                         'templates/game-test-session.md', 'templates/game-test-review.json', 'templates/bug-report.md'):
            self.assertEqual((target / '.unity-game' / relative).read_bytes(), (MANIFEST / relative).read_bytes())
        check = subprocess.run([sys.executable, '-B', str(target / '.unity-game/scripts/game_test_cli.py'), 'check',
                                '--session', str(target / '.unity-game/templates/game-test-session.json'),
                                '--review', str(target / '.unity-game/templates/game-test-review.json'), '--require-review'],
                               capture_output=True, text=True, timeout=20)
        self.assertEqual(check.returncode, 2, check.stderr)
        self.assertEqual(json.loads(check.stdout)['status'], 'not_run')

    def test_bad_json_cli_is_a_failed_check_not_a_pass(self):
        self.session.write_text('{invalid')
        run = self.command('--session', self.session)
        self.assertEqual(run.returncode, 1)
        self.assertEqual(json.loads(run.stdout)['validation_status'], 'failed')


if __name__ == '__main__':
    unittest.main()
