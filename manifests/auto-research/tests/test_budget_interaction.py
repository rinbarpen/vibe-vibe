"""Budget interaction consistency and installed-layout checks; no external jobs or approvals."""
from __future__ import annotations
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest

MANIFEST = Path(__file__).resolve().parents[1]
REPO = MANIFEST.parents[1]
sys.path.insert(0, str(MANIFEST / 'scripts'))
sys.path.insert(0, str(REPO / 'tools/vibe_tool/src'))
import experiment_stats as es
from vibe_tool.manifest import init_manifest, add_manifest


def sample():
    plan = json.loads((MANIFEST / 'templates/EXPERIMENT_SETUP.json.example').read_text())
    plan['cost_unit'] = 'USD'
    for experiment in plan['experiments']:
        experiment['estimated_cost'] = 1
        experiment['estimated_gpu_hours'] = 2
    return es.expand(plan), {'sanity_passed': True, 'code_review': 'PASS',
                             'spent_cost': 0, 'spent_gpu_hours': 0}


def receipt(matrix, state, **scope):
    request = es.decision_request(matrix, state, **scope)
    subject = request['subject']
    return {
        'interaction_contract': request['interaction_contract'],
        'decision_id': request['decision_id'], 'subject_hash': request['subject_hash'],
        'decision': 'approve', 'plan_hash': subject['plan_hash'],
        'max_cost': subject['max_cost'], 'max_gpu_hours': subject['max_gpu_hours'],
        'review_unavailable_acknowledged': subject['review_unavailable_acknowledged'],
        'approved_by': 'fixture-human', 'approved_at': '2026-11-08T00:00:00Z',
        'response_source': {'kind': 'structured_input', 'reference': 'fixture://message/1',
                            'response_id': 'fixture-response-1'},
    }


def run_cli(directory, *args):
    return subprocess.run([sys.executable, str(directory / 'scripts/experiment_stats.py'), *map(str, args)],
                          cwd=directory, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
                          capture_output=True, text=True)


def snapshot(root):
    return {str(path.relative_to(root)): path.read_bytes()
            for path in root.rglob('*') if path.is_file()}


def test_new_template_opts_in_and_legacy_does_not_migrate():
    matrix, state = sample()
    assert matrix['interaction_contract'] == es.INTERACTION_CONTRACT
    old = copy.deepcopy(matrix)
    old.pop('interaction_contract')
    old_approval = {'plan_hash': old['plan_hash'], 'max_cost': 3, 'max_gpu_hours': 6,
                    'approved_by': 'fixture', 'approved_at': 'fixture'}
    before = copy.deepcopy((old, old_approval, state))
    assert es.gate(old, old_approval, state)['allowed']
    assert (old, old_approval, state) == before
    assert not es.gate(matrix, old_approval, state)['allowed']


def test_request_is_stable_reviewable_and_never_an_approval():
    matrix, state = sample()
    before = copy.deepcopy((matrix, state))
    first = es.decision_request(matrix, state)
    assert first == es.decision_request(matrix, state)
    assert first['status'] == 'awaiting_decision'
    assert first['choices'] == ['approve', 'revise', 'cancel']
    assert first['on_no_response'] == 'wait'
    assert first['subject']['matrix_hash'] == es.digest(matrix)
    assert first['subject']['cost_unit'] == 'USD'
    assert 'approved_by' not in first and 'decision' not in first
    assert (matrix, state) == before


@pytest.mark.parametrize('choice', [None, 'pending', 'revise', 'cancel', 'yes', True])
def test_only_explicit_approve_opens_gate(choice):
    matrix, state = sample()
    approval = receipt(matrix, state)
    approval['decision'] = choice
    result = es.gate(matrix, approval, state)
    assert not result['allowed'] and result['launch_performed'] is False
    assert result['decision_status'] in {'awaiting_decision', 'revise', 'cancel'}


def test_no_response_and_repeated_approval_checks_are_read_only():
    matrix, state = sample()
    assert es.gate(matrix, {}, state)['decision_status'] == 'awaiting_decision'
    approval = receipt(matrix, state)
    before = copy.deepcopy((matrix, approval, state))
    results = [es.gate(matrix, approval, state) for _ in range(3)]
    assert results[0] == results[1] == results[2]
    assert results[0]['allowed'] and results[0]['launch_performed'] is False
    assert (matrix, approval, state) == before


@pytest.mark.parametrize('change', ['plan', 'matrix_command', 'ceiling', 'review', 'paid', 'suite'])
def test_subject_changes_invalidate_old_receipt(change):
    matrix, state = sample()
    approval = receipt(matrix, state)
    scope = {}
    if change == 'plan': matrix['plan_hash'] = 'changed'
    elif change == 'matrix_command': matrix['runs'][0]['command'].append('--changed')
    elif change == 'ceiling': approval['max_cost'] += 10
    elif change == 'review': state['code_review'] = 'WARN'
    elif change == 'paid': scope['paid'] = True
    elif change == 'suite': scope.update(paid=True, full_suite=False)
    result = es.gate(matrix, approval, state, **scope)
    assert not result['allowed'] and result['decision_status'] == 'stale'


@pytest.mark.parametrize('source', [None, {}, {'kind': 'structured_input'},
    {'kind': 'structured_input', 'reference': 'fixture', 'response_id': '  '},
    {'kind': 'auto_timeout', 'reference': 'fixture', 'response_id': 'fixture'}])
def test_missing_or_nonhuman_source_fails(source):
    matrix, state = sample()
    approval = receipt(matrix, state)
    approval['response_source'] = source
    result = es.gate(matrix, approval, state)
    assert not result['allowed'] and result['decision_status'] == 'invalid'


def test_revised_materials_require_a_new_decision_and_source():
    matrix, state = sample()
    approval = receipt(matrix, state)
    matrix['max_parallel'] += 1
    assert not es.gate(matrix, approval, state)['allowed']
    updated = receipt(matrix, state)
    updated['response_source']['response_id'] = 'fixture-response-2'
    assert updated['decision_id'] != approval['decision_id']
    assert es.gate(matrix, updated, state)['allowed']


def test_review_unavailable_requires_explicit_ack_and_remaining_budget():
    matrix, state = sample()
    state['code_review'] = 'REVIEW_UNAVAILABLE'
    approval = receipt(matrix, state)
    approval['review_unavailable_acknowledged'] = 'true'
    assert not es.gate(matrix, approval, state)['allowed']
    approval['review_unavailable_acknowledged'] = True
    assert es.gate(matrix, approval, state)['allowed']
    state.update(spent_cost=1, remaining_estimated_cost=2,
                 spent_gpu_hours=2, remaining_estimated_gpu_hours=4)
    assert es.gate(matrix, approval, state)['allowed']
    state['spent_cost'] = 2
    assert not es.gate(matrix, approval, state)['allowed']


def test_free_sanity_is_not_a_business_approval_and_paid_sanity_is_scoped():
    matrix, state = sample()
    assert es.gate(matrix, {}, state, full_suite=False)['allowed']
    assert not es.gate(matrix, {}, state, paid=True, full_suite=False)['allowed']
    approval = receipt(matrix, state, paid=True, full_suite=False)
    assert es.gate(matrix, approval, state, paid=True, full_suite=False)['allowed']
    assert not es.gate(matrix, approval, state)['allowed']


def test_invalid_contract_limits_units_and_equal_numeric_values():
    matrix, state = sample()
    with pytest.raises(es.Invalid): es.decision_request(matrix, state, max_cost=float('nan'))
    with pytest.raises(es.Invalid): es.decision_request(matrix, state, max_gpu_hours=-1)
    matrix['cost_unit'] = 'not_applicable'
    with pytest.raises(es.Invalid): es.decision_request(matrix, state)
    matrix['cost_unit'] = 'USD'
    assert es.decision_request(matrix, state, max_cost=3) == es.decision_request(matrix, state, max_cost=3.0)
    plan = json.loads((MANIFEST / 'templates/EXPERIMENT_SETUP.json.example').read_text())
    plan['interaction_contract'] = 'unknown'
    with pytest.raises(es.Invalid): es.expand(plan)
    matrix['interaction_contract'] = 'unknown'
    with pytest.raises(es.Invalid): es.decision_request(matrix, state)
    assert not es.gate(matrix, receipt(sample()[0], state), state)['allowed']


def test_cli_writes_request_not_approval_and_gate_does_not_mutate_files(tmp_path):
    matrix, state = sample()
    files = {'matrix.json': matrix, 'state.json': state, 'approval.json': receipt(matrix, state)}
    for name, value in files.items(): (tmp_path / name).write_text(json.dumps(value))
    request_path = tmp_path / 'request.json'
    result = run_cli(MANIFEST, 'decision-request', tmp_path / 'matrix.json', '--state',
                     tmp_path / 'state.json', '--output', request_path)
    assert result.returncode == 0, result.stderr
    request = json.loads(request_path.read_text())
    assert request['status'] == 'awaiting_decision' and 'approved_by' not in request
    before = snapshot(tmp_path)
    args = ['gate', tmp_path / 'matrix.json', '--approval', tmp_path / 'approval.json', '--state', tmp_path / 'state.json']
    for _ in range(2):
        result = run_cli(MANIFEST, *args)
        assert result.returncode == 0 and json.loads(result.stdout)['launch_performed'] is False
    assert snapshot(tmp_path) == before
    files['approval.json']['decision'] = 'pending'
    (tmp_path / 'approval.json').write_text(json.dumps(files['approval.json']))
    result = run_cli(MANIFEST, *args)
    assert result.returncode == 1 and not json.loads(result.stdout)['allowed']


def render(directory, *extra):
    return subprocess.run([sys.executable, str(directory / 'scripts/render_idea_workflow.py'),
        '--source', str(directory / 'references/budget-workflow.json'),
        '--output', str(directory / 'references/budget-workflow.svg'), *extra],
        capture_output=True, text=True)


def test_budget_svg_is_current_parseable_and_check_is_read_only():
    paths = [MANIFEST / 'references/budget-workflow.json', MANIFEST / 'references/budget-workflow.svg']
    before = [path.read_bytes() for path in paths]
    result = render(MANIFEST, '--check')
    assert result.returncode == 0, result.stderr
    assert [path.read_bytes() for path in paths] == before
    assert ET.fromstring(before[1]).tag == '{http://www.w3.org/2000/svg}svg'


def test_graph_missing_drift_and_bad_reference_are_read_only(tmp_path):
    target = tmp_path / 'project'
    shutil.copytree(MANIFEST, target, ignore=shutil.ignore_patterns('__pycache__'))
    output = target / 'references/budget-workflow.svg'
    source = target / 'references/budget-workflow.json'
    output.unlink()
    before = snapshot(target)
    assert render(target, '--check').returncode == 1
    assert snapshot(target) == before
    assert render(target).returncode == 0
    data = json.loads(source.read_text()); data['title'] += ' changed'
    source.write_text(json.dumps(data))
    before = snapshot(target)
    assert render(target, '--check').returncode == 1
    assert snapshot(target) == before
    data['edges'][0]['to'] = 'missing'
    source.write_text(json.dumps(data))
    before = snapshot(target)
    assert render(target, '--check').returncode == 2
    assert snapshot(target) == before


@pytest.mark.parametrize('operation', [init_manifest, add_manifest])
def test_installation_has_contract_runtime_and_reproducible_diagram(tmp_path, operation):
    # Isolate manifest resources from unrelated installed skill dependencies.
    repository = tmp_path / 'repository'
    source = repository / 'manifests/auto-research'
    shutil.copytree(MANIFEST, source, ignore=shutil.ignore_patterns('__pycache__'))
    (source / 'skills.txt').write_text('')
    target = tmp_path / (operation.__name__ + ' project with spaces')
    if operation is add_manifest:
        target.mkdir(); (target / 'user-data.md').write_text('preserve user data')
    with contextlib.redirect_stdout(io.StringIO()):
        assert operation(repository / 'manifests', 'auto-research', target) == 0
    assert render(target).returncode == 0
    assert render(target, '--check').returncode == 0
    for name in ('human-interaction.md', 'budget-workflow.json', 'budget-workflow.svg'):
        assert (target / 'references' / name).read_bytes() == (MANIFEST / 'references' / name).read_bytes()
    for document in ('README.md', 'AGENTS.md', 'CLAUDE.md', 'references/human-interaction.md'):
        path = target / document
        for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' not in link and not link.startswith('#'):
                assert (path.parent / link.split('#')[0]).exists(), (document, link)
    matrix, state = sample()
    for name, value in [('matrix.json', matrix), ('state.json', state), ('approval.json', receipt(matrix, state))]:
        (target / name).write_text(json.dumps(value))
    result = run_cli(target, 'decision-request', 'matrix.json', '--state', 'state.json', '--output', 'request.json')
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads((target / 'request.json').read_text())['status'] == 'awaiting_decision'
    result = run_cli(target, 'gate', 'matrix.json', '--state', 'state.json', '--approval', 'approval.json')
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)['launch_performed'] is False
    if operation is add_manifest:
        assert (target / 'user-data.md').read_text() == 'preserve user data'
