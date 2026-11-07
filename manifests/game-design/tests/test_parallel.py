"""Black-box parallel state-machine fixtures; no LLM or game-runtime execution claims."""
from concurrent.futures import ThreadPoolExecutor
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

HOME = Path(__file__).resolve().parents[1]
ROOT = HOME.parents[1]
SCRIPT = HOME / 'scripts/parallel.py'
ROLE = 'game-design-designer'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def snapshot(root):
    return {p.relative_to(root).as_posix(): digest(p.read_bytes())
            for p in root.rglob('*') if p.is_file() and not p.is_symlink()}


class ParallelRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='game parallel fixture ')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / 'game project'
        self.project.mkdir()
        self.plan_file = self.base / 'plan.json'
        self.state_file = self.project / '.game-design/state/parallel.json'
        self.index = 0

    def task(self, identifier='a', **changes):
        task = {
            'id': identifier, 'custom_reason': 'Project-specific deterministic test fixture',
            'role': ROLE, 'depends_on': [],
            'writes': [f'Work/{identifier}.txt', f'Evidence/{identifier}'],
            'resources': [], 'inputs': [], 'outputs': [f'Work/{identifier}.txt'],
            'effect': 'design', 'gates': [],
        }
        task.update(changes)
        return task

    def plan(self, tasks=None, **changes):
        value = {'schema_version': 1, 'mode': 'design-only', 'max_parallel': 3,
                 'lease_seconds': 1800, 'gates': [], 'waivers': {},
                 'tasks': tasks if tasks is not None else [self.task()]}
        value.update(changes)
        return value

    def cli(self, *args, expected=0):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), '--project', str(self.project), *map(str, args)],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
        )
        self.assertEqual(result.returncode, expected,
                         f'command={args!r}\nstdout={result.stdout}\nstderr={result.stderr}')
        if expected:
            return result
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail(f'Expected JSON output: {result.stdout!r}; stderr={result.stderr!r}')

    def initialize(self, plan=None, expected=0, dry_run=False):
        self.plan_file.write_text(json.dumps(plan or self.plan()), encoding='utf-8')
        args = ['init', '--plan', self.plan_file]
        if dry_run:
            args.append('--dry-run')
        return self.cli(*args, expected=expected)

    def state(self):
        return json.loads(self.state_file.read_text(encoding='utf-8'))

    def claim(self, limit=1, worker='fixture-author'):
        return self.cli('claim', '--worker', worker, '--limit', limit)['claimed']

    def bind(self, claimed, run_id=None):
        identifier = claimed['id']
        self.cli('bind', '--id', identifier, '--token', claimed['claim_token'],
                 '--run-id', run_id or f'fixture-author-run-{identifier}')

    def put(self, relative, data='fixture evidence, not a game-runtime result\n', workspace=None):
        root = workspace or self.project
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data if isinstance(data, bytes) else data.encode())
        return path

    def result_file(self, claim, *, status='submitted', workspace=None, artifact=None, **changes):
        identifier = claim['id']
        root = workspace or self.project
        relative = artifact or f'Work/{identifier}.txt'
        output = self.put(relative, f'fixture output for {identifier}\n', root)
        evidence = f'Evidence/{identifier}/author.txt'
        self.put(evidence, workspace=root)
        value = {
            'task_id': identifier, 'claim_token': claim['claim_token'], 'status': status,
            'summary': 'Deterministic file fixture; no LLM or engine execution',
            'artifacts': [{'path': relative, 'sha256': digest(output.read_bytes())}],
            'evidence': [evidence],
            'tests': [{'name': 'fixture bytes', 'status': 'pass',
                       'command': 'fixture write/read check', 'exit_status': 0}],
        }
        value.update(changes)
        self.index += 1
        path = self.base / f'result-{identifier}-{self.index}.json'
        path.write_text(json.dumps(value), encoding='utf-8')
        return path

    def stage(self, operation, claim, *, actor=None, decision=None, expected=0):
        identifier = claim['id']
        evidence = f'Evidence/stages/{identifier}-{operation}.txt'
        self.put(evidence)
        args = [operation, '--id', identifier, '--actor', actor or f'fixture-{operation}-{identifier}',
                '--evidence', evidence]
        if decision is not None:
            args += ['--decision', decision]
        return self.cli(*args, expected=expected)

    def submitted(self, task=None):
        self.initialize(self.plan([task or self.task()]))
        claim = self.claim()[0]
        self.bind(claim)
        self.cli('submit', '--result', self.result_file(claim))
        return claim

    def finish(self, claim):
        self.stage('integrate', claim)
        self.stage('validate', claim, decision='pass')
        self.stage('review', claim, decision='pass')

    def test_init_dry_run_and_status_next_are_read_only(self):
        before = snapshot(self.project)
        self.initialize(dry_run=True)
        self.assertEqual(snapshot(self.project), before)
        self.initialize()
        before = snapshot(self.project)
        status = self.cli('status')
        self.assertEqual(status['tasks']['a']['status'], 'pending')
        self.assertEqual([t['id'] for t in self.cli('next')['ready']], ['a'])
        self.assertEqual(snapshot(self.project), before)

    def test_duplicate_init_preserves_state(self):
        self.initialize()
        before = snapshot(self.project)
        self.initialize(expected=2)
        self.assertEqual(snapshot(self.project), before)

    def test_end_to_end_only_reviewed_done_unlocks_successor(self):
        self.initialize(self.plan([self.task(), self.task('b', depends_on=['a'])]))
        self.assertEqual([t['id'] for t in self.cli('next')['ready']], ['a'])
        claim = self.claim()[0]
        self.bind(claim)
        self.assertEqual(self.state()['tasks']['a']['status'], 'running')
        self.cli('submit', '--result', self.result_file(claim))
        self.assertEqual(self.state()['tasks']['a']['status'], 'submitted')
        self.assertEqual(self.cli('next')['ready'], [])
        self.stage('integrate', claim)
        self.assertEqual(self.state()['tasks']['a']['status'], 'integrated')
        self.assertEqual(self.cli('next')['ready'], [])
        self.stage('validate', claim, decision='pass')
        self.assertEqual(self.state()['tasks']['a']['status'], 'validated')
        self.assertEqual(self.cli('next')['ready'], [])
        self.stage('review', claim, decision='pass')
        self.assertEqual(self.state()['tasks']['a']['status'], 'done')
        self.assertEqual([t['id'] for t in self.cli('next')['ready']], ['b'])

    def test_parallel_claim_processes_never_duplicate_or_exceed_capacity(self):
        self.initialize(self.plan([self.task(f't{i}') for i in range(8)], max_parallel=3))
        with ThreadPoolExecutor(max_workers=5) as workers:
            batches = list(workers.map(lambda i: self.claim(3, f'fixture-{i}'), range(5)))
        claimed = [item for batch in batches for item in batch]
        self.assertEqual(len(claimed), 3)
        self.assertEqual(len({t['id'] for t in claimed}), 3)
        self.assertEqual(sum(t['status'] == 'running' for t in self.state()['tasks'].values()), 3)

    def test_shared_external_resource_has_one_writer(self):
        tasks = [self.task('a', resources=['editor:fixture-game']),
                 self.task('b', resources=['editor:fixture-game'])]
        self.initialize(self.plan(tasks))
        self.assertEqual(len(self.claim(3)), 1)
        self.assertEqual(self.claim(3), [])

    def test_parent_child_path_reservations_conflict(self):
        tasks = [self.task('a', writes=['Work/tree', 'Evidence/a'], outputs=['Work/tree/a.txt']),
                 self.task('b', writes=['Work/tree/b.txt', 'Evidence/b'], outputs=['Work/tree/b.txt'])]
        self.initialize(self.plan(tasks))
        self.assertEqual(len(self.claim(3)), 1)

    def test_case_alias_path_reservations_conflict(self):
        tasks = [self.task('a', writes=['Work/FILE.txt', 'Evidence/a'], outputs=['Work/FILE.txt']),
                 self.task('b', writes=['work/file.txt', 'Evidence/b'], outputs=['work/file.txt'])]
        self.initialize(self.plan(tasks))
        self.assertEqual(len(self.claim(3)), 1)

    def test_sibling_path_names_are_not_false_prefix_conflicts(self):
        tasks = [self.task('a', writes=['Work/foo', 'Evidence/a'], outputs=['Work/foo/a.txt']),
                 self.task('b', writes=['Work/foobar', 'Evidence/b'], outputs=['Work/foobar/b.txt'])]
        self.initialize(self.plan(tasks))
        self.assertEqual(len(self.claim(3)), 2)

    def test_submitted_task_retains_scope_until_final_review(self):
        tasks = [self.task('a', resources=['dcc:asset']), self.task('b', resources=['dcc:asset'])]
        self.initialize(self.plan(tasks))
        claim = self.claim()[0]
        self.bind(claim)
        self.cli('submit', '--result', self.result_file(claim))
        self.assertEqual(self.claim(3), [])
        self.finish(claim)
        self.assertEqual([t['id'] for t in self.claim(3)], ['b'])

    def test_invalid_paths_are_rejected_before_state_write(self):
        for index, path in enumerate(('../escape', '/absolute', '.git/index', '.game-design/state/parallel.json',
                                      '.claude/agents/override.md', '.codex/config.toml', '.game-design', '.', 'Work/*.txt',
                                      'Work/file.txt.', 'Work/file.txt ', 'Work/CON', 'Work/AUX.txt', 'Work/LPT1.dat')):
            with self.subTest(path=path):
                self.project = self.base / f'bad-path-{index}'
                self.project.mkdir()
                task = self.task(writes=[path], outputs=[path])
                self.initialize(self.plan([task]), expected=2)
                self.assertFalse((self.project / '.game-design/state/parallel.json').exists())

    def test_cycle_unknown_dependency_and_role_are_rejected(self):
        variants = [
            [self.task('a', depends_on=['b']), self.task('b', depends_on=['a'])],
            [self.task('a', depends_on=['missing'])],
            [self.task('a', role='invented-missing-role')],
        ]
        for index, tasks in enumerate(variants):
            with self.subTest(index=index):
                self.project = self.base / f'bad-dag-{index}'
                self.project.mkdir()
                self.initialize(self.plan(tasks), expected=2)
                self.assertFalse((self.project / '.game-design/state/parallel.json').exists())

    def test_missing_input_blocks_claim_without_running(self):
        self.initialize(self.plan([self.task(inputs=['Inputs/missing.txt'])]))
        self.assertEqual(self.cli('next')['ready'], [])
        self.assertEqual(self.claim(), [])
        self.put('Inputs/missing.txt', 'now available')
        self.assertEqual([t['id'] for t in self.claim()], ['a'])

    def test_implementation_requires_mode_and_human_gate(self):
        variants = [
            self.plan([self.task(effect='implementation')]),
            self.plan([self.task(effect='implementation')], mode='implementation'),
        ]
        for index, plan in enumerate(variants):
            with self.subTest(index=index):
                self.project = self.base / f'bad-mode-{index}'
                self.project.mkdir()
                self.initialize(plan, expected=2)

    def test_human_gate_stays_pending_until_evidenced_decision(self):
        task = self.task(effect='implementation', gates=['direction'])
        self.initialize(self.plan([task], mode='implementation', gates=[{'id': 'direction'}]))
        self.assertEqual(self.cli('next')['ready'], [])
        self.assertEqual(self.claim(), [])
        self.put('Evidence/human-direction.txt', 'Fixture-only explicit decision record')
        self.cli('approve-gate', '--gate', 'direction', '--actor', 'human-fixture',
                 '--evidence', 'Evidence/human-direction.txt')
        self.assertEqual([t['id'] for t in self.cli('next')['ready']], ['a'])

    def test_bind_and_submit_require_current_token_and_real_run_binding(self):
        self.initialize()
        claim = self.claim()[0]
        self.cli('bind', '--id', 'a', '--token', 'wrong-token', '--run-id', 'fixture', expected=2)
        result = self.result_file(claim)
        self.cli('submit', '--result', result, expected=2)
        self.bind(claim)
        self.cli('submit', '--result', result)

    def test_hash_mismatch_and_out_of_scope_artifacts_are_rejected(self):
        self.initialize()
        claim = self.claim()[0]
        self.bind(claim)
        result = self.result_file(claim)
        value = json.loads(result.read_text())
        value['artifacts'][0]['sha256'] = '0' * 64
        result.write_text(json.dumps(value))
        before = self.state_file.read_bytes()
        self.cli('submit', '--result', result, expected=2)
        self.assertEqual(self.state_file.read_bytes(), before)
        result = self.result_file(claim, artifact='Other/unclaimed.txt')
        self.cli('submit', '--result', result, expected=2)

    def test_report_evidence_must_be_within_worker_scope(self):
        self.initialize()
        claim = self.claim()[0]
        self.bind(claim)
        self.put('Evidence/outside.txt')
        result = self.result_file(claim, evidence=['Evidence/outside.txt'])
        self.cli('submit', '--result', result, expected=2)

    def test_missing_expected_output_is_rejected(self):
        task = self.task(outputs=['Work/a.txt', 'Work/extra.txt'], writes=['Work', 'Evidence/a'])
        self.initialize(self.plan([task]))
        claim = self.claim()[0]
        self.bind(claim)
        self.cli('submit', '--result', self.result_file(claim), expected=2)

    def test_changed_frozen_input_rejects_submission(self):
        self.put('Inputs/spec.txt', 'revision one')
        self.initialize(self.plan([self.task(inputs=['Inputs/spec.txt'])]))
        claim = self.claim()[0]
        self.bind(claim)
        result = self.result_file(claim)
        self.put('Inputs/spec.txt', 'revision two')
        self.cli('submit', '--result', result, expected=2)

    def test_declared_input_output_update_preserves_baseline_and_completes(self):
        original = b'existing authored source revision one\n'
        self.put('Work/a.txt', original)
        self.initialize(self.plan([self.task(inputs=['Work/a.txt'])]))
        claim = self.claim()[0]
        self.bind(claim)
        self.cli('submit', '--result', self.result_file(claim))
        self.finish(claim)
        self.assertEqual(self.state()['tasks']['a']['status'], 'done')
        self.assertEqual((self.project / 'Work/a.txt').read_bytes(), b'fixture output for a\n')
        self.assertIn(digest(original), json.dumps(self.state()['tasks']['a']))

    def test_owned_dependency_revision_can_be_updated_and_consumed_downstream(self):
        tasks = [self.task(), self.task('b', depends_on=['a'], inputs=['Work/a.txt'],
                                       writes=['Work/a.txt', 'Evidence/b'], outputs=['Work/a.txt']),
                 self.task('c', depends_on=['b'], inputs=['Work/a.txt'])]
        self.initialize(self.plan(tasks))
        parent = self.claim()[0]
        self.bind(parent)
        self.cli('submit', '--result', self.result_file(parent))
        self.finish(parent)
        reviser = self.claim()[0]
        self.assertEqual(reviser['id'], 'b')
        self.bind(reviser)
        self.cli('submit', '--result', self.result_file(reviser, artifact='Work/a.txt'))
        self.finish(reviser)
        self.assertEqual((self.project / 'Work/a.txt').read_bytes(), b'fixture output for b\n')
        self.assertEqual([t['id'] for t in self.cli('next')['ready']], ['c'])

    def test_changed_output_invalidates_integrate_and_review(self):
        claim = self.submitted()
        self.put('Work/a.txt', 'changed after submit')
        self.stage('integrate', claim, expected=2)
        # Restore exact submitted bytes, finish integration/validation, then mutate.
        self.put('Work/a.txt', 'fixture output for a\n')
        self.stage('integrate', claim)
        self.stage('validate', claim, decision='pass')
        self.put('Work/a.txt', 'changed after validation')
        self.stage('review', claim, decision='pass', expected=2)
        self.assertNotEqual(self.state()['tasks']['a']['status'], 'done')

    def test_author_integrator_qa_and_reviewer_are_distinct(self):
        claim = self.submitted()
        author = 'fixture-author-run-a'
        self.stage('integrate', claim, actor=author, expected=2)
        self.stage('integrate', claim, actor='integrator-run')
        for actor in (author, 'integrator-run'):
            self.stage('validate', claim, actor=actor, decision='pass', expected=2)
        self.stage('validate', claim, actor='qa-run', decision='pass')
        for actor in (author, 'integrator-run', 'qa-run'):
            self.stage('review', claim, actor=actor, decision='pass', expected=2)
        self.stage('review', claim, actor='reviewer-run', decision='pass')
        self.assertEqual(self.state()['tasks']['a']['status'], 'done')

    def test_missing_evidence_does_not_advance_stage(self):
        claim = self.submitted()
        self.cli('integrate', '--id', 'a', '--actor', 'integrator-run',
                 '--evidence', 'Evidence/absent.txt', expected=2)
        self.assertEqual(self.state()['tasks']['a']['status'], 'submitted')

    def test_failed_or_not_run_validation_blocks_completion(self):
        for index, decision in enumerate(('fail', 'not_run')):
            with self.subTest(decision=decision):
                self.project = self.base / f'validation-{index}'
                self.project.mkdir()
                self.state_file = self.project / '.game-design/state/parallel.json'
                claim = self.submitted()
                self.stage('integrate', claim)
                self.stage('validate', claim, decision=decision)
                self.assertEqual(self.state()['tasks']['a']['status'], 'blocked')
                self.stage('review', claim, decision='pass', expected=2)

    def test_review_changes_requested_is_not_done(self):
        claim = self.submitted()
        self.stage('integrate', claim)
        self.stage('validate', claim, decision='pass')
        self.stage('review', claim, decision='changes_requested')
        self.assertEqual(self.state()['tasks']['a']['status'], 'blocked')

    def test_expired_lease_keeps_reservation_until_explicit_stopped_recovery(self):
        tasks = [self.task('a', resources=['editor:shared']), self.task('b', resources=['editor:shared'])]
        self.initialize(self.plan(tasks))
        claim = self.claim()[0]
        self.bind(claim)
        value = self.state()
        value['tasks']['a']['lease_until'] = time.time() - 30
        self.state_file.write_text(json.dumps(value))
        self.assertEqual(self.claim(3), [])
        self.cli('heartbeat', '--id', 'a', '--token', claim['claim_token'], expected=2)
        self.cli('submit', '--result', self.result_file(claim), expected=2)
        self.put('Evidence/worker-stopped.txt', 'Fixture worker process stopped; no live agent in this test')
        args = ['recover', '--id', 'a', '--token', claim['claim_token'],
                '--evidence', 'Evidence/worker-stopped.txt', '--reason', 'fixture recovery']
        self.cli(*args, expected=2)
        self.cli(*args, '--stopped')
        renewed = self.claim()[0]
        self.assertNotEqual(renewed['claim_token'], claim['claim_token'])
        self.assertGreater(renewed['attempt'], claim['attempt'])
        self.cli('submit', '--result', self.result_file(claim), expected=2)

    def test_heartbeat_extends_live_lease(self):
        self.initialize()
        claim = self.claim()[0]
        self.bind(claim)
        before = self.state()['tasks']['a']['lease_until']
        self.cli('heartbeat', '--id', 'a', '--token', claim['claim_token'])
        self.assertGreaterEqual(self.state()['tasks']['a']['lease_until'], before)

    def test_isolated_workspace_outputs_need_explicit_main_project_integration(self):
        workspace = self.base / 'isolated worktree fixture'
        workspace.mkdir()
        self.initialize(self.plan([self.task(workspace=str(workspace))]))
        claim = self.claim()[0]
        self.bind(claim)
        self.cli('submit', '--result', self.result_file(claim, workspace=workspace))
        self.stage('integrate', claim, expected=2)
        self.put('Work/a.txt', (workspace / 'Work/a.txt').read_bytes())
        self.put('Evidence/a/author.txt', (workspace / 'Evidence/a/author.txt').read_bytes())
        self.finish(claim)
        self.assertEqual(self.state()['tasks']['a']['status'], 'done')

    def test_symlink_output_is_rejected(self):
        self.initialize()
        claim = self.claim()[0]
        self.bind(claim)
        result = self.result_file(claim)
        external = self.base / 'external.txt'
        external.write_text('external source')
        output = self.project / 'Work/a.txt'
        output.unlink()
        output.symlink_to(external)
        value = json.loads(result.read_text())
        value['artifacts'][0]['sha256'] = digest(external.read_bytes())
        result.write_text(json.dumps(value))
        self.cli('submit', '--result', result, expected=2)

    def test_changed_completed_dependency_does_not_unlock_new_work(self):
        self.initialize(self.plan([self.task(), self.task('b', depends_on=['a'])]))
        claim = self.claim()[0]
        self.bind(claim)
        self.cli('submit', '--result', self.result_file(claim))
        self.finish(claim)
        self.put('Work/a.txt', 'changed after final approval')
        self.assertEqual(self.cli('next')['ready'], [])
        self.assertEqual(self.claim(), [])



    def test_modified_parent_review_evidence_does_not_unlock_successor(self):
        self.initialize(self.plan([self.task(), self.task('b', depends_on=['a'])]))
        claim = self.claim()[0]
        self.bind(claim)
        self.cli('submit', '--result', self.result_file(claim))
        self.finish(claim)
        self.put('Evidence/stages/a-review.txt', 'modified after final independent approval')
        self.assertEqual(self.cli('next')['ready'], [])
        self.assertEqual(self.claim(), [])

    def test_mutable_child_scope_does_not_exempt_parent_review_evidence(self):
        child_task = self.task('b', depends_on=['a'], writes=['Work/b.txt', 'Evidence'])
        self.initialize(self.plan([self.task(), child_task]))
        parent = self.claim()[0]
        self.bind(parent)
        self.cli('submit', '--result', self.result_file(parent))
        self.finish(parent)
        child = self.claim()[0]
        self.bind(child)
        self.put('Evidence/stages/a-review.txt', 'changed parent review under a broad mutable child scope')
        self.cli('submit', '--result', self.result_file(child), expected=2)

    def test_dependency_change_after_child_claim_rejects_submission(self):
        self.initialize(self.plan([self.task(), self.task('b', depends_on=['a'])]))
        parent = self.claim()[0]
        self.bind(parent)
        self.cli('submit', '--result', self.result_file(parent))
        self.finish(parent)
        child = self.claim()[0]
        self.bind(child)
        self.put('Work/a.txt', 'parent changed while child is executing')
        self.cli('submit', '--result', self.result_file(child), expected=2)

    def test_completed_design_queue_promotes_with_evidence_and_new_gate_pending(self):
        profile = self.project / '.game-design/state/project.json'
        profile.parent.mkdir(parents=True)
        profile.write_text(json.dumps({'mode': 'design-only'}))
        original = self.task()
        self.initialize(self.plan([original]))
        claim = self.claim()[0]
        self.bind(claim)
        self.cli('submit', '--result', self.result_file(claim))
        self.finish(claim)
        expanded = self.plan([original, self.task('b', effect='implementation', gates=['direction'],
                                                depends_on=['a'])],
                             mode='implementation', gates=[{'id': 'direction'}])
        self.plan_file.write_text(json.dumps(expanded))
        self.put('Evidence/mode-promotion.txt', 'Fixture-only human decision to enter implementation')
        args = ['extend', '--plan', self.plan_file, '--reason', 'approved fixture mode promotion',
                '--evidence', 'Evidence/mode-promotion.txt']
        self.cli(*args, expected=2)  # Existing project profile has not changed yet.
        profile.write_text(json.dumps({'mode': 'implementation'}))
        self.cli(*args)
        self.assertEqual(self.state()['mode'], 'implementation')
        self.assertEqual(self.state()['tasks']['a']['status'], 'done')
        self.assertEqual(self.cli('next')['ready'], [])
        self.put('Evidence/direction-new.txt', 'Fixture-only approval of new implementation scope')
        self.cli('approve-gate', '--gate', 'direction', '--actor', 'human-fixture',
                 '--evidence', 'Evidence/direction-new.txt')
        self.assertEqual([t['id'] for t in self.cli('next')['ready']], ['b'])

    def test_mode_promotion_preserves_unfinished_design_queue(self):
        original = self.task()
        self.initialize(self.plan([original]))
        expanded = self.plan([original, self.task('b', effect='implementation', gates=['direction'],
                                                depends_on=['a'])],
                             mode='implementation', gates=[{'id': 'direction'}])
        self.plan_file.write_text(json.dumps(expanded))
        self.put('Evidence/mode-promotion.txt', 'Fixture-only promotion request before design finishes')
        before = self.state_file.read_bytes()
        self.cli('extend', '--plan', self.plan_file, '--reason', 'premature fixture promotion',
                 '--evidence', 'Evidence/mode-promotion.txt', expected=2)
        self.assertEqual(self.state_file.read_bytes(), before)

    def test_modified_gate_evidence_revokes_readiness(self):
        task = self.task(effect='implementation', gates=['direction'])
        self.initialize(self.plan([task], mode='implementation', gates=[{'id': 'direction'}]))
        self.put('Evidence/human-direction.txt', 'Fixture-only original direction decision')
        self.cli('approve-gate', '--gate', 'direction', '--actor', 'human-fixture',
                 '--evidence', 'Evidence/human-direction.txt')
        self.assertEqual([t['id'] for t in self.cli('next')['ready']], ['a'])
        self.put('Evidence/human-direction.txt', 'changed decision file after approval')
        self.assertEqual(self.cli('next')['ready'], [])
        self.assertEqual(self.claim(), [])

    def test_extend_preserves_live_claim_and_requires_prior_tasks_unchanged(self):
        original = self.task()
        self.initialize(self.plan([original]))
        claim = self.claim()[0]
        self.bind(claim)
        self.put('Evidence/extend.txt', 'Fixture-only added follow-up task decision')
        expanded = self.plan([original, self.task('b', depends_on=['a'])])
        self.plan_file.write_text(json.dumps(expanded))
        self.cli('extend', '--plan', self.plan_file, '--reason', 'add fixture follow-up',
                 '--evidence', 'Evidence/extend.txt')
        self.assertEqual(self.state()['tasks']['a']['claim_token'], claim['claim_token'])
        self.assertEqual(self.state()['tasks']['a']['status'], 'running')
        self.assertEqual(self.cli('next')['ready'], [])
        self.cli('submit', '--result', self.result_file(claim))
        self.finish(claim)
        self.assertEqual([t['id'] for t in self.cli('next')['ready']], ['b'])
        changed = copy.deepcopy(expanded)
        changed['tasks'][0]['writes'].append('Other/new-scope')
        self.plan_file.write_text(json.dumps(changed))
        before = self.state_file.read_bytes()
        self.cli('extend', '--plan', self.plan_file, '--reason', 'invalid changed prior task',
                 '--evidence', 'Evidence/extend.txt', expected=2)
        self.assertEqual(self.state_file.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
