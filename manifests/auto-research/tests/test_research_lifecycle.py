from __future__ import annotations
import copy
import datetime as dt
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
import pytest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import research_workflow as rw
import experiment_stats as es

@pytest.fixture
def project(tmp_path):
    rw.init(tmp_path)
    rw.git(tmp_path,'config','user.name','Fixture Researcher')
    rw.git(tmp_path,'config','user.email','fixture@example.test')
    cfg=rw.config(tmp_path)
    # Existing transition fixtures exercise legacy mode, not scientific attestation.
    cfg['enforce_stage_contracts']=False
    for stage in cfg['stages']:
        if stage.get('contract_revision'):stage['required_evidence']=stage['id'] in {'submission/submit/receipt','revision/decision/receipt','revision/revise/resubmit','acceptance/decision/confirm'}
    for role,request in cfg['roles'].items():
        cfg['bindings'][role]={'provider':'fixture','model_id':'fixture-'+role,'service_profile':request['service_profile'],
                               'reasoning_effort':request['reasoning_effort'],'available':True,'verified_at':'2026-09-19'}
    rw.save(tmp_path/rw.RUNTIME/'settings.json',cfg)
    return tmp_path

def checkpoint(root,stage='startup',state='started',**kwargs):
    values=dict(stage=stage,state=state,cycle='cycle-001',role='planner',actual_model='fixture-planner',summary='fixture decision',next='continue',
                artifact=[],input=[],run_id=[],command=None,submission_id=None,revision_id=None)
    values.update(kwargs)
    return rw.checkpoint(root,SimpleNamespace(**values))


def test_defaults_three_levels_and_requested_models(project):
    cfg=rw.config(project)
    assert len([s for s in cfg['stages'] if s['level']==1])==11
    assert {s['level'] for s in cfg['stages']}=={1,2,3}
    assert cfg['seeds']==[42]
    assert cfg['roles']['research']['service_profile']=='pro'
    assert cfg['roles']['planner']['reasoning_effort']=='medium'
    assert cfg['roles']['executor']['requested_model']=='gpt-5.6-luna'
    assert cfg['roles']['writer']['requested_model']=='gpt-5.5'
    assert cfg['writing_policy']['scene']=='research'
    assert cfg['writing_policy']['engine']=='latex'
    assert cfg['writing_policy']['languages']==['zh','en']
    assert cfg['writing_policy']['uncertainty_reporting']['default']=='omit_95_ci'
    assert cfg['writing_policy']['defensive_writing']['default']=='disabled'
    assert cfg['writing_policy']['latex_template']['style_files']=='immutable'
    assert set(cfg['phase_details']) == {s['id'] for s in cfg['stages'] if s['level']==1}
    for phase_id, detail in cfg['phase_details'].items():
        assert detail['goal'] and detail['inputs'] and detail['outputs']
        assert detail['activities'] and detail['gates'] and detail['checkpoint']
        assert detail['roles'] and detail['returns']
        assert all(isinstance(value, str) for value in detail['returns'].values())
    for role in cfg['roles']: assert rw.route(cfg,role)['binding']['model_id']=='fixture-'+role
    cfg['bindings']['planner']['reasoning_effort']='high'
    with pytest.raises(rw.Invalid): rw.route(cfg,'planner')


def test_checkpoint_git_isolation_and_snapshots(project):
    (project/'unrelated.txt').write_text('keep me')
    rw.git(project,'add','unrelated.txt')
    (project/'unrelated.txt').write_text('also keep unstaged')
    (project/'PLAN.md').write_text('first plan')
    result=checkpoint(project,artifact=['PLAN.md'])
    assert 'unrelated.txt' not in rw.git(project,'show','--format=','--name-only',result['commit']).splitlines()
    assert rw.git(project,'diff','--cached','--name-only')=='unrelated.txt'
    assert rw.git(project,'show',':unrelated.txt')=='keep me'
    assert (project/'unrelated.txt').read_text()=='also keep unstaged'
    (project/'PLAN.md').write_text('revised plan')
    checkpoint(project,state='revised',artifact=['PLAN.md'])
    snapshots=list((project/'refine-logs/history').rglob('PLAN.md'))
    assert {p.read_text() for p in snapshots}=={'first plan','revised plan'}
    assert len(rw.events(project))==2


def test_hierarchy_failure_resume_and_new_cycle(project):
    with pytest.raises(rw.Invalid): checkpoint(project,'startup/scope')
    checkpoint(project)
    checkpoint(project,'startup/scope')
    checkpoint(project,'startup/scope/question')
    checkpoint(project,'startup/scope/question','failed',summary='negative result, execution error')
    with pytest.raises(rw.Invalid): checkpoint(project,'startup/scope/question','completed')
    checkpoint(project,'startup/scope/question','resumed')
    checkpoint(project,'startup/scope/question','completed',summary='completed; hypothesis unsupported')
    checkpoint(project,'startup/scope/constraints','skipped',summary='fixture not applicable')
    checkpoint(project,'startup/scope','completed')
    with pytest.raises(rw.Invalid): checkpoint(project,state='completed')
    checkpoint(project,'startup/roadmap','skipped',summary='already documented')
    checkpoint(project,state='completed')
    with pytest.raises(rw.Invalid): checkpoint(project)
    checkpoint(project,cycle='cycle-002')
    assert rw.latest(project,'cycle-002')['startup']['execution_id']!=rw.latest(project,'cycle-001')['startup']['execution_id']


def test_pending_commit_failure_and_recovery(project,monkeypatch):
    original=rw.git
    def fail(root,*args,**kwargs):
        if args[0]=='commit': raise rw.Invalid('simulated git hook failure')
        return original(root,*args,**kwargs)
    monkeypatch.setattr(rw,'git',fail)
    with pytest.raises(rw.Invalid): checkpoint(project)
    pending=project/rw.RUNTIME/'local/pending.json'
    assert pending.exists()
    assert len(rw.events(project))==1
    monkeypatch.setattr(rw,'git',original)
    journal=rw.read(pending)
    result=rw.finish_pending(project,journal)
    assert len(rw.events(project))==1
    # Crash after successful commit but before clearing pending.
    rw.save(pending,journal)
    again=rw.finish_pending(project,journal)
    assert result['commit']==again['commit']
    # Branch bootstrap adds one empty baseline commit before the checkpoint.
    assert rw.git(project,'rev-list','--count','HEAD')=='2'


def test_missing_binding_can_be_recorded(project):
    cfg=rw.config(project); cfg['bindings']={}; rw.save(project/rw.RUNTIME/'settings.json',cfg)
    with pytest.raises(rw.Invalid): checkpoint(project)
    checkpoint(project,state='blocked',actual_model=None,summary='blocked_model_unavailable: binding missing')
    assert rw.latest(project,'cycle-001')['startup']['state']=='blocked'


def test_no_identity_mutation(tmp_path):
    rw.init(tmp_path)
    assert not rw.git(tmp_path,'config','--local','--get','user.name',check=False)
    original=(tmp_path/rw.RUNTIME/'settings.json').read_bytes()
    rw.init(tmp_path)
    assert (tmp_path/rw.RUNTIME/'settings.json').read_bytes()==original


@pytest.mark.parametrize('filename,content',[('key.txt','api_key=123456789abcdef'),('large.txt','x'*200)])
def test_sensitive_and_large_files_blocked(project,filename,content):
    cfg=rw.config(project); cfg['max_git_file_bytes']=100; rw.save(project/rw.RUNTIME/'settings.json',cfg)
    (project/filename).write_text(content)
    with pytest.raises(rw.Invalid): checkpoint(project,artifact=[filename])
    assert not rw.events(project)


def test_path_escape_and_wrong_model(project):
    with pytest.raises(rw.Invalid): checkpoint(project,artifact=['../elsewhere'])
    with pytest.raises(rw.Invalid): checkpoint(project,actual_model='different-model')

def test_isolated_workspace_verify_promote_close(project):
    (project/'seed.txt').write_text('baseline')
    rw.git(project,'add','seed.txt'); rw.git(project,'commit','-m','fixture baseline')
    rw.branch_init(project,'cycle-001','research')
    started=rw.workspace_start(project,'cycle-001','startup','attempt-001')
    wt=Path(started['worktree'])
    assert wt.is_dir() and wt!=project
    (wt/'seed.txt').write_text('candidate')
    assert (project/'seed.txt').read_text()=='baseline'
    verified=rw.workspace_verify(project,started['id'],["python -c \"from pathlib import Path; assert Path('seed.txt').read_text() == 'candidate'\""])
    assert verified['status']=='verified'
    rw.git(project,'switch',started['target_branch'])
    promoted=rw.workspace_promote(project,started['id'])
    assert promoted['status']=='promoted'
    assert (project/'seed.txt').read_text()=='candidate'
    closed=rw.workspace_close(project,started['id'])
    assert closed['status']=='closed' and not wt.exists()
    assert rw.workspace_status(project,started['id'])['state']=='closed'

def test_failed_workspace_verification_retains_attempt(project):
    (project/'seed.txt').write_text('baseline')
    rw.git(project,'add','seed.txt'); rw.git(project,'commit','-m','fixture baseline')
    rw.branch_init(project,'cycle-001','research')
    started=rw.workspace_start(project,'cycle-001','startup','attempt-001')
    wt=Path(started['worktree']); (wt/'seed.txt').write_text('candidate')
    result=rw.workspace_verify(project,started['id'],['exit 7'])
    assert result['status']=='verification_failed'
    with pytest.raises(rw.Invalid): rw.workspace_promote(project,started['id'])
    assert wt.is_dir() and rw.workspace_status(project,started['id'])['state']=='verification_failed'

def test_workspace_detects_root_drift(project):
    (project/'seed.txt').write_text('baseline')
    rw.git(project,'add','seed.txt'); rw.git(project,'commit','-m','fixture baseline')
    rw.branch_init(project,'cycle-001','research')
    started=rw.workspace_start(project,'cycle-001','startup','attempt-001')
    (Path(started['worktree'])/'seed.txt').write_text('candidate')
    (project/'seed.txt').write_text('out-of-band change')
    result=rw.workspace_verify(project,started['id'],['true'])
    assert result['status']=='verification_failed'
    assert result['verification']['baseline_drift']['changed_tracked']==['seed.txt']


def test_end_to_end_all_stages_submission_revision_acceptance(project):
    cfg=rw.config(project)
    # Exercise entire real stage topology using clearly marked fixture evidence.
    (project/'fixture-evidence.md').write_text('FIXTURE: simulated receipt/decision, not a real submission or acceptance')
    def visit(stage):
        checkpoint(project,stage['id'],submission_id='fixture-sub-001',revision_id='fixture-rev-001')
        for child in cfg['stages']:
            if child['parent_id']==stage['id']: visit(child)
        if stage.get('required_evidence'):
            with pytest.raises(rw.Invalid): checkpoint(project,stage['id'],'completed')
        checkpoint(project,stage['id'],'completed',artifact=['fixture-evidence.md'] if stage.get('required_evidence') else [],
                   submission_id='fixture-sub-001',revision_id='fixture-rev-001')
    for s in cfg['stages']:
        if s['level']==1: visit(s)
    assert all(s['state']=='completed' for s in rw.status(project,'cycle-001')['stages'])
    assert len(rw.events(project))==2*len(cfg['stages'])
    # baseline + checkpoint commits + stage merge commits + branch-log commits
    assert int(rw.git(project,'rev-list','--count','HEAD'))==1+4*len(cfg['stages'])


def experiment_plan():
    p=rw.read(ROOT/'templates/EXPERIMENT_SETUP.json.example')
    p['baseline_search']['searched_at']=dt.date.today().isoformat()
    for c in p['baseline_search']['candidates']:
        c['paper_url']='https://example.test/paper';c['code_url']='https://example.test/code'
    return p


def test_seed_matrix_and_routing():
    p=experiment_plan(); m=es.expand(p)
    assert len(m['runs'])==3 and {r['seed'] for r in m['runs']}=={42}
    assert m['route']=='run-experiment'
    p['seeds']=[42,43,44]; assert len(es.expand(p)['runs'])==9
    p['provider']='ssh'; assert es.expand(p)['route']=='experiment-queue'
    p['provider']='modal'; assert es.expand(p)['route']=='run-experiment'
    p['seeds']=[42,42]
    with pytest.raises(rw.Invalid): es.expand(p)


def test_design_coverage_and_source_records():
    p=experiment_plan(); assert es.design_review(p)['valid']
    p['coverage']=[]; assert not es.design_review(p)['valid']
    p=experiment_plan(); p['baseline_search']['searched_at']='2000-01-01'
    assert not es.design_review(p)['valid']
    p=experiment_plan(); p['experiments'][-1].pop('controls')
    assert not es.design_review(p)['valid']


def test_budget_sanity_and_review_unavailable():
    m=es.expand(experiment_plan())
    state={'sanity_passed':True,'code_review':'REVIEW_UNAVAILABLE','spent_cost':0,'spent_gpu_hours':0}
    approval={'plan_hash':m['plan_hash'],'approved_by':'fixture-user','approved_at':'fixture','max_cost':0,'max_gpu_hours':0}
    assert not es.gate(m,approval,state)['allowed']
    approval['review_unavailable_acknowledged']=True
    assert es.gate(m,approval,state)['allowed']
    state['spent_cost']=1; assert not es.gate(m,approval,state)['allowed']
    assert es.gate(m,{},state,full_suite=False)['allowed']
    assert not es.gate(m,{},state,paid=True,full_suite=False)['allowed']
    state['spent_cost']=0;state['sanity_passed']=False
    assert not es.gate(m,approval,state)['allowed']
    state['sanity_passed']=True; state['experiment_id']='main';state['experiments']={'baseline':'stuck'}
    assert not es.gate(m,approval,state)['allowed']


def completed_records(matrix,root):
    records=[]
    for i,run in enumerate(matrix['runs']):
        path=f'result-{i}.json';rw.save(root/path,{'metrics':{'accuracy':float(i)}})
        (root/f'out-{i}.log').write_text('fixture stdout'); (root/f'err-{i}.log').write_text('')
        records.append({'command':run['command'],'code_revision':'fixture-commit','environment':'fixture-local','started_at':'2026-09-19T01:00:00+00:00','ended_at':'2026-09-19T01:01:00+00:00','stdout_path':f'out-{i}.log','stderr_path':f'err-{i}.log','run_id':run['run_id'],'attempt':1,'config_hash':run['config_hash'],
                        'status':'completed','exit_code':0,'result_path':path,'audit':'PASS'})
    return records


def test_single_seed_zero_baseline_and_audit(tmp_path):
    m=es.expand(experiment_plan()); records=completed_records(m,tmp_path)
    records[1]['audit']='FAIL'; records[2]['audit']='REVIEW_UNAVAILABLE'
    report=es.aggregate(m,records,tmp_path)
    assert all(s['std'] is None for s in report['summary'])
    assert report['comparisons'][0]['relative_change'] is None
    assert report['runs'][1]['evidence_status']=='ineligible'
    assert report['runs'][2]['evidence_status']=='provisional'
    assert len(report['summary'])==3  # audit never removes raw results


def test_multiseed_attempt_failures_and_missing(tmp_path):
    p=experiment_plan();p['seeds']=[42,43];m=es.expand(p);records=completed_records(m,tmp_path)
    report=es.aggregate(m,records,tmp_path)
    assert all(s['successful_n']==2 and s['std'] is not None for s in report['summary'])
    retry=copy.deepcopy(records[0]);retry.update(attempt=2,status='failed',exit_code=1)
    report=es.aggregate(m,records+[retry],tmp_path)
    assert report['runs'][0]['status']=='failed' and len(report['attempts'])==7
    assert report['summary'][0]['successful_n'] in (1,2)
    report=es.aggregate(m,records[:-1],tmp_path)
    assert report['incomplete_runs']==[m['runs'][-1]['run_id']]
    with pytest.raises(rw.Invalid): es.aggregate(m,records+[records[0]],tmp_path)
    records[0]['config_hash']='old'
    with pytest.raises(rw.Invalid): es.aggregate(m,records,tmp_path)


def test_metric_direction_protocol_and_missing_source(tmp_path):
    p=experiment_plan();p['metrics']['accuracy']['direction']='minimize'
    m=es.expand(p);records=completed_records(m,tmp_path)
    r=es.aggregate(m,records,tmp_path)
    assert r['comparisons'][0]['improvement']==-1
    m['runs'][1]['protocol']='other'
    assert es.aggregate(m,records,tmp_path)['comparisons'][0]['status']=='unpaired'
    (tmp_path/records[0]['result_path']).unlink()
    with pytest.raises(rw.Invalid): es.aggregate(m,records,tmp_path)


def test_csv_nonfinite_and_reports(tmp_path):
    m=es.expand(experiment_plan());records=completed_records(m,tmp_path)
    (tmp_path/'metric.csv').write_text('accuracy\n0.8\n')
    records[0]['result_path']='metric.csv'
    r=es.aggregate(m,records,tmp_path);es.write_report(r,tmp_path/'summary.json')
    assert (tmp_path/'summary-summary.csv').exists()
    assert rw.read(tmp_path/'summary.json')['runs'][0]['metrics']['accuracy']==0.8
    (tmp_path/'metric.csv').write_text('accuracy\nnan\n')
    assert es.aggregate(m,records,tmp_path)['runs'][0]['status']=='invalid'


def test_installer_preserves_runtime_and_help(tmp_path):
    script=ROOT/'scripts/init-auto-research.sh'
    p=subprocess.run(['bash',str(script),str(tmp_path)],capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    for name in ['research_workflow.py','experiment_stats.py','writing_plan.py','latex_template_gate.py']: assert (tmp_path/'scripts'/name).exists()
    (tmp_path/'CLAUDE.md').write_text('user changes')
    (tmp_path/'.auto-research/keep.json').write_text('{"keep":true}')
    subprocess.run(['bash',str(script),str(tmp_path)],check=True,capture_output=True)
    assert (tmp_path/'CLAUDE.md').read_text()=='user changes'
    subprocess.run(['bash',str(script),str(tmp_path),'--force'],check=True,capture_output=True)
    assert (tmp_path/'.auto-research/keep.json').exists()
    p=subprocess.run(['bash',str(script),'--help'],capture_output=True,text=True)
    assert p.returncode==0 and not p.stderr


def test_latex_template_manifest_and_immutable_styles(tmp_path):
    template=tmp_path/'vendor'/'venue'; template.mkdir(parents=True)
    (template/'main.tex').write_text('\\documentclass{venue}\n')
    (template/'references.bib').write_text('@article{fixture, title={Fixture}}\n')
    (template/'figures').mkdir(); (template/'tables').mkdir()
    (template/'venue.cls').write_text('% official fixture class\n')
    requirements=tmp_path/'requirements.json'
    rw.save(requirements, {'venue':'fixture-venue','source_url':'https://example.test/guide',
                           'checked_at':'2026-09-19','required_files':['main.tex','references.bib','figures/','tables/'],
                           'style_globs':['**/*.cls','**/*.sty']})
    gate=ROOT/'scripts/latex_template_gate.py'
    manifest=tmp_path/'.auto-research/writing/latex/template-manifest.json'
    p=subprocess.run([sys.executable,str(gate),'--project-root',str(tmp_path),'manifest',
                      '--template-root','vendor/venue','--requirements','requirements.json',
                      '--output','.auto-research/writing/latex/template-manifest.json'],capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    p=subprocess.run([sys.executable,str(gate),'--project-root',str(tmp_path),'verify','--manifest',
                      str(manifest.relative_to(tmp_path))],capture_output=True,text=True)
    assert p.returncode==0,p.stderr
    (template/'venue.cls').write_text('% modified fixture class\n')
    p=subprocess.run([sys.executable,str(gate),'--project-root',str(tmp_path),'verify','--manifest',
                      str(manifest.relative_to(tmp_path))],capture_output=True,text=True)
    assert p.returncode==1 and 'sha256_changed' in p.stderr


def test_stats_cli_pipeline(tmp_path):
    setup=tmp_path/'setup.json';matrix=tmp_path/'matrix.json';records=tmp_path/'records.json'
    rw.save(setup,experiment_plan())
    cli=[sys.executable,str(ROOT/'scripts/experiment_stats.py')]
    p=subprocess.run(cli+['expand',str(setup),'--output',str(matrix)],capture_output=True,text=True)
    assert p.returncode==0,p.stdout
    rw.save(records,completed_records(rw.read(matrix),tmp_path))
    p=subprocess.run(cli+['summarize',str(matrix),'--records',str(records),'--content-root',str(tmp_path),'--output',str(tmp_path/'stats.json')],capture_output=True,text=True)
    assert p.returncode==0,p.stdout


def test_archive_verification_and_checkpoint(project):
    data=project/'large.bin';data.write_bytes(b'fixture weights\x00')
    index={'version':1,'kind':'archive_index','artifacts':[{'path':'large.bin','bytes':data.stat().st_size,
            'sha256':rw.hashlib.sha256(data.read_bytes()).hexdigest(),'availability':'local_only','created_at':'fixture','checked_at':'fixture'}]}
    rw.save(project/'archive.json',index)
    assert rw.verify_archive(project,index)['valid']
    checkpoint(project,artifact=['archive.json'])
    assert 'large.bin' not in rw.git(project,'ls-tree','-r','--name-only','HEAD')
    data.write_bytes(b'changed')
    with pytest.raises(rw.Invalid): checkpoint(project,state='revised',artifact=['archive.json'])


def test_pending_artifact_change_does_not_commit(project,monkeypatch):
    (project/'PLAN.md').write_text('approved')
    original=rw.git
    def fail(root,*args,**kwargs):
        if args[0]=='commit': raise rw.Invalid('fixture failure')
        return original(root,*args,**kwargs)
    monkeypatch.setattr(rw,'git',fail)
    with pytest.raises(rw.Invalid): checkpoint(project,artifact=['PLAN.md'])
    monkeypatch.setattr(rw,'git',original)
    journal=rw.read(project/rw.RUNTIME/'local/pending.json')
    (project/'PLAN.md').write_text('new unrelated edit')
    with pytest.raises(rw.Invalid): rw.finish_pending(project,journal)
    (project/'PLAN.md').write_text('approved')
    assert rw.finish_pending(project,journal)['status']=='committed'


def test_checkpoint_lock_serializes_writers(project):
    with rw.lock(project):
        with pytest.raises(rw.Invalid): checkpoint(project)


def test_stats_rejects_untraced_completion_and_negative_budget(tmp_path):
    m=es.expand(experiment_plan());records=completed_records(m,tmp_path)
    records[0].pop('code_revision')
    with pytest.raises(rw.Invalid): es.aggregate(m,records,tmp_path)
    approval={'plan_hash':m['plan_hash'],'approved_by':'user','approved_at':'fixture','max_cost':1,'max_gpu_hours':1}
    state={'sanity_passed':True,'code_review':'PASS','spent_cost':-1}
    assert not es.gate(m,approval,state)['allowed']


def test_paired_summary_uses_common_seeds(tmp_path):
    p=experiment_plan();p['seeds']=[42,43];m=es.expand(p);records=completed_records(m,tmp_path)
    r=es.aggregate(m,records,tmp_path)
    assert all(s['paired_n']==2 and s['std_delta'] is not None for s in r['paired_summary'])
    records[0]['status']='failed';records[0]['exit_code']=1
    r=es.aggregate(m,records,tmp_path)
    assert all(s['paired_n']==1 and s['std_delta'] is None for s in r['paired_summary'])
