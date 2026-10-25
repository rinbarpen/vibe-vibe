#!/usr/bin/env python3
"""Check recorded game-test evidence; this command never launches or plays a game.

Exit 0: recorded required cases pass (and independent review if requested).
Exit 1: failed cases, invalid/stale evidence or requested review changes.
Exit 2: planned/simulated/incomplete execution, or required review not performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

CHANNELS = {'project-harness', 'mcp', 'desktop-skill', 'browser-skill', 'device-tool'}
STATUSES = {'passed', 'failed', 'not_run'}
INPUT_KINDS = {'key_down', 'key_up', 'pointer_down', 'pointer_up', 'pointer_move', 'scroll',
               'touch_down', 'touch_up', 'touch_move', 'gamepad_down', 'gamepad_up', 'gamepad_axis', 'text'}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def required_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + ' must be nonempty text')
    return value


def json_object(path):
    data = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or type(data.get('schema_version')) is not int or data.get('schema_version') != 1:
        raise ValueError('Expected schema_version=1 JSON object: ' + str(path))
    return data


def file_evidence(entry, base, *, local=True):
    if not isinstance(entry, dict):
        raise ValueError('Evidence entry must be an object')
    relative = required_text(entry.get('path'), 'evidence.path')
    path = (base / relative).resolve()
    if local and not path.is_relative_to(base):
        raise ValueError('Evidence must remain inside the session directory: ' + relative)
    if not path.is_file() or not path.stat().st_size:
        raise ValueError('Missing/empty evidence: ' + str(path))
    actual = digest(path)
    if actual != entry.get('sha256'):
        raise ValueError('Evidence hash mismatch: ' + str(path))
    return {'path': str(path), 'sha256': actual, 'bytes': path.stat().st_size}


def input_balance(events):
    if not isinstance(events, list):
        raise ValueError('input_events must be an array')
    held, axes, last_time = set(), {}, -1
    for event in events:
        if not isinstance(event, dict):
            raise ValueError('input event must be an object')
        kind = required_text(event.get('kind'), 'input event kind')
        if kind not in INPUT_KINDS:
            raise ValueError('Unknown normalized input event: ' + kind)
        at = event.get('t_ms')
        if type(at) not in (int, float) or not last_time <= at < float('inf') or at < 0:
            raise ValueError('input event times must be finite, nonnegative and ordered')
        last_time = at
        if kind.endswith(('_down', '_up')):
            code = required_text(event.get('code'), 'input event code')
            key = (kind.rsplit('_', 1)[0], code)
            if kind.endswith('_down'):
                if key in held:
                    raise ValueError('Duplicate held input: ' + str(key))
                held.add(key)
            else:
                if key not in held:
                    raise ValueError('Input release without matching press: ' + str(key))
                held.remove(key)
        elif kind == 'gamepad_axis':
            code = required_text(event.get('code'), 'gamepad axis code')
            value = event.get('value')
            if type(value) not in (int, float) or not -1 <= value <= 1:
                raise ValueError('Gamepad axis value must be finite in [-1,1]')
            axes[code] = value
        elif kind == 'text':
            required_text(event.get('text'), 'text input content')
    if any(value != 0 for value in axes.values()):
        raise ValueError('Unreleased gamepad axes')
    if held:
        raise ValueError('Unreleased held inputs: ' + str(sorted(held)))


def check(session_path: Path, review_path: Path | None = None, require_review=False):
    session_path = session_path.expanduser().resolve()
    session = json_object(session_path)
    run_id = required_text(session.get('run_id'), 'run_id')
    game = session.get('game')
    execution = session.get('execution')
    if not isinstance(game, dict) or not isinstance(execution, dict):
        raise ValueError('game and execution must be objects')
    revision = required_text(game.get('revision'), 'game.revision')
    kind = execution.get('kind')
    if kind not in ('real_game', 'simulation', 'planned'):
        raise ValueError('execution.kind must be real_game, simulation or planned')
    cases = session.get('cases')
    if not isinstance(cases, list) or not cases:
        raise ValueError('At least one explicit test case is required')
    result = {'schema_version': 1, 'operation': 'check_recorded_evidence', 'run_id': run_id,
              'session': str(session_path), 'session_sha256': digest(session_path), 'revision': revision,
              'validation_status': 'passed', 'status': 'not_run', 'reason': 'execution_not_performed',
              'execution_kind': kind, 'counts': {s: 0 for s in STATUSES}, 'evidence_files': [],
              'review_status': 'not_run', 'review_verdict': None,
              'limitation': 'This verifies recorded file contracts, not truth of observations, fun, image correctness or physical execution.'}
    if kind == 'real_game':
        if execution.get('channel') not in CHANNELS:
            raise ValueError('Unknown actual execution channel')
        required_text(execution.get('tool'), 'execution.tool (actual tool or skill path)')
        required_text(execution.get('environment'), 'execution.environment')
        required_text(execution.get('tester'), 'execution.tester')
    ids, required_count, required_missing, failed, observed = set(), 0, 0, 0, 0
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError('case must be an object')
        ident = required_text(case.get('id'), 'case.id')
        if ident in ids:
            raise ValueError('Duplicate case ID: ' + ident)
        ids.add(ident)
        if type(case.get('required')) is not bool:
            raise ValueError('case.required must be boolean')
        status = case.get('status')
        if status not in STATUSES:
            raise ValueError('Unknown case status: ' + ident)
        result['counts'][status] += 1
        required_text(case.get('expected'), 'case.expected')
        if case['required']:
            required_count += 1
            required_missing += status == 'not_run'
        failed += status == 'failed'
        if kind != 'real_game' and status != 'not_run':
            raise ValueError('Planned/simulated cases must stay not_run for real-game coverage: ' + ident)
        if status == 'not_run':
            required_text(case.get('reason'), 'case.reason for not_run')
            continue
        observed += 1
        required_text(case.get('actual'), 'case.actual')
        steps = case.get('steps')
        if not isinstance(steps, list) or not steps or any(not isinstance(x, str) or not x.strip() for x in steps):
            raise ValueError('Executed cases need actual ordered action/observation steps: ' + ident)
        scope = case.get('scope', 'gameplay')
        if scope not in ('startup', 'gameplay', 'visual'):
            raise ValueError('Unknown case scope: ' + ident)
        if scope != 'startup' and case.get('normal_input') is not True:
            raise ValueError('Normal-input gameplay coverage needs actual normal input: ' + ident)
        evidence = case.get('evidence')
        if not isinstance(evidence, list) or not evidence:
            raise ValueError('Executed cases need actual evidence: ' + ident)
        for entry in evidence:
            required_text(entry.get('kind') if isinstance(entry, dict) else None, 'evidence.kind')
            result['evidence_files'].append(file_evidence(entry, session_path.parent))
        input_balance(case.get('input_events', []))
        if case.get('input_events') and not any(not x['kind'].endswith('_up') for x in case['input_events']):
            raise ValueError('Input sequence contains no actual action')
    if required_count == 0:
        raise ValueError('At least one required case is needed for a passing session')
    if observed:
        if not isinstance(game.get('build'), dict):
            raise ValueError('Executed session needs exact game.build path and sha256')
        result['build'] = file_evidence(game['build'], session_path.parent, local=False)
        build_kind = game['build'].get('kind', 'file')
        if build_kind not in ('file', 'manifest'):
            raise ValueError('game.build.kind must be file or manifest')
        if build_kind == 'manifest':
            manifest_path = Path(result['build']['path'])
            manifest = json_object(manifest_path)
            entries = manifest.get('files')
            if not isinstance(entries, list) or not entries:
                raise ValueError('Build manifest needs nonempty files')
            inventory, seen = [], set()
            for entry in entries:
                record = file_evidence(entry, manifest_path.parent)
                if record['path'] in seen or record['path'] == str(manifest_path):
                    raise ValueError('Build manifest entries must be unique and exclude self')
                seen.add(record['path'])
                inventory.append(record)
            result['build']['manifest_files'] = inventory
    if kind == 'real_game' and observed:
        if failed:
            result.update(status='failed', reason='observed_test_failure')
        elif required_missing:
            result.update(status='not_run', reason='required_cases_not_run')
        else:
            result.update(status='passed', reason='recorded_required_cases_passed')
    if review_path is not None:
        review_path = review_path.expanduser().resolve()
        review = json_object(review_path)
        if review.get('review_status') not in ('not_run', 'pending', 'completed'):
            raise ValueError('Invalid review_status')
        result['review_status'] = review['review_status']
        if review['review_status'] == 'completed':
            if review.get('reviewed_session_sha256') != result['session_sha256'] or review.get('reviewed_revision') != revision:
                raise ValueError('Stale review: session hash/revision changed')
            reviewer = required_text(review.get('reviewer'), 'reviewer identity/context').strip()
            if review.get('independent_context') is not True or reviewer in tuple(x.strip() for x in (execution.get('tester'), execution.get('implementation_actor')) if isinstance(x, str)):
                raise ValueError('Review needs an independent context, distinct from tester')
            verdict = review.get('verdict')
            if verdict not in ('passed', 'changes_requested', 'blocked'):
                raise ValueError('Invalid completed review verdict')
            if verdict == 'passed' and review.get('approved_revision') != revision:
                raise ValueError('Passed review must approve this exact revision')
            if verdict == 'passed' and result['status'] != 'passed':
                raise ValueError('Review cannot pass missing/failed required game tests')
            result.update(review_verdict=verdict, review=str(review_path), review_sha256=digest(review_path))
            if verdict != 'passed':
                result.update(status='failed' if verdict == 'changes_requested' or result['status'] == 'failed' else 'not_run', reason='review_' + verdict)
    if require_review and result['review_status'] != 'completed':
        result.update(status='failed' if result['status'] == 'failed' else 'not_run', reason='independent_review_not_completed')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('check', help='Read-only hash/status/review check; not a game runner')
    p.add_argument('--session', required=True, type=Path)
    p.add_argument('--review', type=Path)
    p.add_argument('--require-review', action='store_true')
    args = parser.parse_args(argv)
    try:
        result = check(args.session, args.review, args.require_review)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result = {'operation': 'check_recorded_evidence', 'validation_status': 'failed', 'status': 'failed', 'reason': str(exc)}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return {'passed': 0, 'failed': 1, 'not_run': 2}[result['status']]


if __name__ == '__main__':
    sys.exit(main())
