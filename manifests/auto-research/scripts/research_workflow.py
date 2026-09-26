#!/usr/bin/env python3
"""Local research lifecycle ledger. No model calls, deployments or remote Git pushes."""
from __future__ import annotations
import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid

RUNTIME = Path('.auto-research/lifecycle')
BRANCH_LOG = RUNTIME / 'branches.jsonl'
BRANCH_STATE = RUNTIME / 'local/branch-state.json'
WORKSPACE_DIR = RUNTIME / 'local/workspaces'
STATES = {'started', 'completed', 'failed', 'blocked', 'paused', 'resumed', 'skipped', 'revised'}
TERMINAL = {'completed', 'skipped'}
ACTIVE = {'started', 'resumed', 'revised'}

class Invalid(ValueError):
    pass

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)

def save(path, value):
    atomic(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n')

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def git(root, *args, check=True):
    p = subprocess.run(['git', '--literal-pathspecs', '-C', str(root), *args], capture_output=True, text=True)
    if check and p.returncode:
        raise Invalid(p.stderr.strip() or p.stdout.strip() or 'Git command failed')
    return p.stdout.strip()

def relative(root, name):
    p = Path(name)
    if p.is_absolute() or '..' in p.parts or not p.parts or p.parts[0] == '.git':
        raise Invalid('Expected a project-relative artifact path: ' + str(name))
    resolved = (root / p).resolve()
    if not resolved.is_relative_to(root): raise Invalid('Artifact escapes project: ' + str(name))
    if (root / p).is_symlink(): raise Invalid('Register the actual artifact, not a symlink: ' + str(name))
    return p.as_posix()

@contextlib.contextmanager
def lock(root):
    path = root / RUNTIME / 'local' / 'lock'
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as f:
        try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError: raise Invalid('Another checkpoint writer is active; retry after it finishes')
        try: yield
        finally: fcntl.flock(f, fcntl.LOCK_UN)

def config(root):
    cfg = read(root / RUNTIME / 'settings.json')
    if cfg.get('version') != 1: raise Invalid('Unknown lifecycle version')
    ids = {s['id'] for s in cfg['stages']}
    if len(ids) != len(cfg['stages']): raise Invalid('Duplicate stage ID')
    for s in cfg['stages']:
        if s['level'] not in (1,2,3): raise Invalid('Only three lifecycle levels are supported')
        if s['parent_id'] and s['parent_id'] not in ids: raise Invalid('Missing parent stage')
        if s['parent_id']:
            parent = next(x for x in cfg['stages'] if x['id'] == s['parent_id'])
            if parent['level'] != s['level'] - 1: raise Invalid('Invalid stage hierarchy')
        elif s['level'] != 1: raise Invalid('Non-root stage requires parent')
    b = cfg.get('branching')
    if b is not None:
        if not isinstance(b, dict): raise Invalid('branching must be an object')
        if b.get('merge_strategy', 'no-ff') != 'no-ff': raise Invalid('Only no-ff branch merges are supported')
        for key in ('integration_branch','branch_template','cycle_branch_template'):
            if not b.get(key): raise Invalid('Missing branching.' + key)
    policy = cfg.get('writing_policy')
    if policy is not None:
        if not isinstance(policy, dict) or policy.get('scene') != 'research':
            raise Invalid('writing_policy.scene must be research')
        if set(policy.get('languages', [])) != {'zh', 'en'}:
            raise Invalid('writing_policy.languages must include zh and en')
        if policy.get('engine') != 'latex': raise Invalid('research writing engine must be latex')
        ci = policy.get('uncertainty_reporting', {})
        if ci.get('default') != 'omit_95_ci': raise Invalid('research default must omit 95 CI')
        if policy.get('defensive_writing', {}).get('default') != 'disabled':
            raise Invalid('research defensive writing must be disabled by default')
        template = policy.get('latex_template', {})
        if template.get('style_files') != 'immutable' or not template.get('template_manifest'):
            raise Invalid('LaTeX template styles must be immutable and manifested')
    return cfg

def events(root):
    p = root / RUNTIME / 'events.jsonl'
    return [json.loads(line) for line in p.read_text().splitlines() if line.strip()] if p.exists() else []

def replace_event(root, replacement):
    path = root / RUNTIME / 'events.jsonl'
    rows = events(root)
    for index, event in enumerate(rows):
        if event.get('checkpoint_id') == replacement.get('checkpoint_id'):
            rows[index] = replacement
            atomic(path, ''.join(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n' for row in rows))
            return
    raise Invalid('Pending checkpoint event not found: ' + str(replacement.get('checkpoint_id')))

def committed(root, checkpoint_id):
    return git(root, 'log', '--all', '--format=%H', '--fixed-strings', '--grep=Checkpoint-ID: ' + checkpoint_id, check=False).splitlines()

def latest(root, cycle):
    result = {}
    for e in events(root):
        if e['cycle'] == cycle: result[e['stage_id']] = e
    return result

def route(cfg, role, actual=None):
    requested = cfg['roles'].get(role)
    binding = cfg.get('bindings', {}).get(role)
    if not requested or not binding or not binding.get('available') or not binding.get('verified_at'):
        raise Invalid('blocked_model_unavailable: explicit verified binding required for ' + role)
    if not binding.get('provider') or not binding.get('model_id'):
        raise Invalid('blocked_model_unavailable: provider/model_id required')
    if binding.get('reasoning_effort') != requested.get('reasoning_effort') or binding.get('service_profile') != requested.get('service_profile'):
        raise Invalid('blocked_model_unavailable: binding does not match requested effort/profile')
    if actual is not None and actual != binding['model_id']:
        raise Invalid('Actual model differs from verified role binding')
    return {'requested': requested, 'binding': binding}

def branching_cfg(cfg):
    b = cfg.get('branching') or {}
    return b if b.get('enabled', False) else None

def branch_slug(value, label='branch value'):
    value = re.sub(r'[^a-zA-Z0-9]+', '-', str(value).strip()).strip('-').lower()
    if not value: raise Invalid('Empty ' + label)
    if len(value) > 63: raise Invalid(label + ' exceeds 63 characters')
    return value

def branch_ref_ok(name):
    if not name or name.startswith('-') or name.endswith('/') or name.endswith('.'):
        raise Invalid('Invalid branch name: ' + name)
    if any(token in name for token in ('..', '@{', '\\', ' ', '~', '^', ':', '?', '*', '[')):
        raise Invalid('Invalid branch name: ' + name)
    if not re.fullmatch(r'[a-zA-Z0-9._/-]+', name): raise Invalid('Invalid branch name: ' + name)
    return name

def current_branch(root):
    return git(root, 'branch', '--show-current', check=False) or 'HEAD'

def branch_exists(root, name):
    return subprocess.run(
        ['git', '--literal-pathspecs', '-C', str(root), 'show-ref', '--verify', '--quiet', 'refs/heads/' + name],
        capture_output=True, text=True,
    ).returncode == 0

def branch_state(root):
    path = root / BRANCH_STATE
    if path.exists(): return read(path)
    return {'version': 1, 'idea_slug': None, 'cycle': None, 'base_branch': None,
            'integration_branch': None, 'current_branch': current_branch(root), 'stages': {}}

def save_branch_state(root, state):
    save(root / BRANCH_STATE, state)

def branch_events(root):
    path = root / BRANCH_LOG
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()] if path.exists() else []

def append_branch_event(root, event):
    path = root / BRANCH_LOG
    old = path.read_text(encoding='utf-8') if path.exists() else ''
    atomic(path, old + json.dumps(event, ensure_ascii=False, sort_keys=True) + '\n')

def commit_branch_log(root, message):
    git(root, 'add', '--', str(BRANCH_LOG))
    git(root, 'commit', '--only', '-m', message, '--', str(BRANCH_LOG))

def branch_names(cfg, idea, stage_id):
    b = branching_cfg(cfg)
    if not b: raise Invalid('Branching is disabled in lifecycle settings')
    idea = branch_slug(idea, 'idea slug')
    parts = stage_id.split('/')
    stage = branch_slug(parts[0], 'stage')
    substage = branch_slug('-'.join(parts[1:]) if len(parts) > 1 else 'root', 'substage')
    work = b.get('branch_template', '{idea}/{stage}/{substage}').format(idea=idea, stage=stage, substage=substage)
    integration = b.get('cycle_branch_template', '{idea}/cycle/integration').format(idea=idea)
    return branch_ref_ok(work), branch_ref_ok(integration)

def branch_target(cfg, idea, stage_id):
    st = next(s for s in cfg['stages'] if s['id'] == stage_id)
    if st['parent_id']:
        parent, _ = branch_names(cfg, idea, st['parent_id'])
        return parent
    return branch_names(cfg, idea, stage_id)[1]

def require_clean(root, action):
    dirty = '\n'.join(line for line in git(root, 'status', '--porcelain', '--untracked-files=all', check=False).splitlines()
                        if not line.startswith('?? '))
    if dirty: raise Invalid('Cannot ' + action + ' with uncommitted changes; reconcile the working tree first')

def _branch_init_unlocked(root, cfg, cycle, idea=None):
    b = branching_cfg(cfg)
    if not b: return None
    state = branch_state(root)
    idea = branch_slug(idea or state.get('idea_slug') or b.get('idea_slug') or 'research', 'idea slug')
    base = branch_ref_ok(b.get('integration_branch', 'main'))
    _, integration = branch_names(cfg, idea, cfg['stages'][0]['id'])
    if state.get('cycle') == cycle and state.get('integration_branch') == integration and branch_exists(root, integration):
        state.update({'idea_slug': idea, 'base_branch': base, 'current_branch': current_branch(root)})
        save_branch_state(root, state)
        return state
    if not git(root, 'rev-parse', '--verify', 'HEAD', check=False):
        for key in ('user.name','user.email'):
            if not git(root, 'config', '--get', key, check=False):
                raise Invalid('Configure project Git ' + key + ' before initializing branches')
        git(root, 'commit', '--allow-empty', '--only', '-m', f'research[{cycle}]: initialize branch baseline')
    if not branch_exists(root, base):
        if current_branch(root) != base: git(root, 'branch', base, current_branch(root))
    if not branch_exists(root, integration): git(root, 'branch', integration, base)
    git(root, 'switch', integration)
    state.update({'idea_slug': idea, 'cycle': cycle, 'base_branch': base,
                  'integration_branch': integration, 'current_branch': integration})
    save_branch_state(root, state)
    return state

def branch_init(root, cycle='cycle-001', idea=None):
    with lock(root):
        cfg = config(root)
        state = _branch_init_unlocked(root, cfg, cycle, idea)
        if state is None: return {'status': 'disabled'}
        append_branch_event(root, {'event':'cycle_initialized','time':now(),'cycle':cycle,
                                   'idea_slug':state['idea_slug'],'base_branch':state['base_branch'],
                                   'integration_branch':state['integration_branch']})
        commit_branch_log(root, f'research[{cycle}]: initialize branches')
        return {'status':'initialized','cycle':cycle,'idea_slug':state['idea_slug'],
                'base_branch':state['base_branch'],'integration_branch':state['integration_branch'],
                'current_branch':current_branch(root)}

def _branch_start_unlocked(root, cfg, cycle, stage_id, idea=None):
    if stage_id not in {s['id'] for s in cfg['stages']}: raise Invalid('Unknown stage: ' + stage_id)
    state = _branch_init_unlocked(root, cfg, cycle, idea)
    if state is None: return {'status':'disabled'}
    idea = state['idea_slug']; work, _ = branch_names(cfg, idea, stage_id)
    target = branch_target(cfg, idea, stage_id)
    if not branch_exists(root, target): raise Invalid('Parent branch does not exist: ' + target)
    if not branch_exists(root, work):
        if current_branch(root) != target: git(root, 'switch', target)
        git(root, 'switch', '-c', work)
    else: git(root, 'switch', work)
    state['current_branch'] = work
    state['stages'].setdefault(stage_id, {}).update({'branch':work,'target_branch':target,'cycle':cycle})
    save_branch_state(root, state)
    append_branch_event(root, {'event':'stage_started','time':now(),'cycle':cycle,'stage_id':stage_id,
                               'branch':work,'parent_branch':target})
    return {'status':'started','stage_id':stage_id,'branch':work,'parent_branch':target}

def branch_start(root, cycle, stage_id, idea=None):
    with lock(root):
        result = _branch_start_unlocked(root, config(root), cycle, stage_id, idea)
        if result.get('status') != 'disabled': commit_branch_log(root, f'research[{stage_id}]: start branch')
        return result

def _merge_stage_unlocked(root, cfg, cycle, stage_id, checkpoint_id=None):
    b = branching_cfg(cfg)
    if not b: return {'status':'disabled'}
    state = branch_state(root); idea = state.get('idea_slug') or b.get('idea_slug') or 'research'
    work, _ = branch_names(cfg, idea, stage_id); target = branch_target(cfg, idea, stage_id)
    record = state['stages'].setdefault(stage_id, {})
    if record.get('merged_commit'): return {'status':'already-merged','merge_commit':record['merged_commit']}
    if not branch_exists(root, work): raise Invalid('Stage branch does not exist: ' + work)
    if not branch_exists(root, target): raise Invalid('Merge target branch does not exist: ' + target)
    require_clean(root, 'merge stage branch')
    if current_branch(root) != target: git(root, 'switch', target)
    git(root, 'merge', '--no-ff', '--no-edit', work, check=True)
    merge_commit = git(root, 'rev-parse', 'HEAD')
    append_branch_event(root, {'event':'stage_merged','time':now(),'cycle':cycle,'stage_id':stage_id,
                               'branch':work,'target_branch':target,'merge_commit':merge_commit,
                               'checkpoint_id':checkpoint_id})
    commit_branch_log(root, f'research[{stage_id}]: merge branch')
    state['current_branch'] = target
    record.update({'branch':work,'target_branch':target,'merged_commit':merge_commit,'merge_commit':merge_commit})
    save_branch_state(root, state)
    return {'status':'merged','branch':work,'target_branch':target,'merge_commit':merge_commit}

def branch_merge(root, cycle, stage_id):
    with lock(root):
        cfg = config(root); state = latest(root, cycle); event = state.get(stage_id)
        if not event or event.get('state') not in TERMINAL: raise Invalid('Stage must be completed or skipped before merge')
        return _merge_stage_unlocked(root, cfg, cycle, stage_id, event.get('checkpoint_id'))

def branch_close(root, cycle):
    with lock(root):
        cfg = config(root); b = branching_cfg(cfg)
        if not b: return {'status':'disabled'}
        state = branch_state(root); integration = state.get('integration_branch')
        base = state.get('base_branch') or b.get('integration_branch','main')
        if not integration or not branch_exists(root, integration): raise Invalid('Cycle integration branch is not initialized')
        require_clean(root, 'close research cycle')
        if not branch_exists(root, base): git(root, 'branch', base, integration)
        if current_branch(root) != base: git(root, 'switch', base)
        if current_branch(root) != integration: git(root, 'merge', '--no-ff', '--no-edit', integration)
        merge_commit = git(root, 'rev-parse', 'HEAD')
        append_branch_event(root, {'event':'cycle_closed','time':now(),'cycle':cycle,
                                   'integration_branch':integration,'base_branch':base,
                                   'merge_commit':merge_commit})
        commit_branch_log(root, f'research[{cycle}]: close cycle')
        state['current_branch'] = base; state['closed_commit'] = merge_commit; save_branch_state(root, state)
        return {'status':'closed','cycle':cycle,'integration_branch':integration,'base_branch':base,'merge_commit':merge_commit}

def branch_revision(root, cycle, kind, identifier):
    with lock(root):
        cfg = config(root); b = branching_cfg(cfg)
        if not b: return {'status':'disabled'}
        state = branch_state(root); idea = state.get('idea_slug') or b.get('idea_slug') or 'research'
        identifier = branch_slug(identifier, kind + ' id')
        template = b.get(kind + '_branch_template', '{idea}/' + kind + '/{' + kind + '_id}')
        name = template.format(idea=idea, submission_id=identifier, revision_id=identifier)
        name = branch_ref_ok(name)
        source = current_branch(root)
        require_clean(root, 'create ' + kind + ' branch')
        if not branch_exists(root, name): git(root, 'switch', '-c', name)
        else: git(root, 'switch', name)
        append_branch_event(root, {'event':kind + '_branch_started','time':now(),'cycle':cycle,
                                   'branch':name,'source_branch':source,'identifier':identifier})
        commit_branch_log(root, f'research[{kind}]: start {identifier}')
        state['current_branch'] = name; save_branch_state(root, state)
        return {'status':'started','kind':kind,'branch':name,'source_branch':source,'identifier':identifier}

def branch_status(root, cycle):
    cfg = config(root); b = branching_cfg(cfg)
    if not b: return {'status':'disabled'}
    state = branch_state(root)
    return {'status':'ok','cycle':cycle,'current_branch':current_branch(root),
            'base_branch':state.get('base_branch') or b.get('integration_branch','main'),
            'integration_branch':state.get('integration_branch'),
            'idea_slug':state.get('idea_slug') or b.get('idea_slug'),
            'stages':state.get('stages',{}),'events':len(branch_events(root))}

def workspace_record_path(root, identifier):
    identifier=branch_slug(identifier,'attempt id')
    return root/WORKSPACE_DIR/(identifier+'.json')

def workspace_record(root, identifier):
    path=workspace_record_path(root,identifier)
    if not path.is_file(): raise Invalid('Unknown workspace attempt: '+identifier)
    return read(path)

def workspace_manifest(root):
    """Hash every tracked file and enumerate untracked files at the baseline."""
    tracked=git(root,'ls-files','-z').split('\0')
    files={}
    for name in filter(None,tracked):
        path=root/name
        if path.is_file(): files[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    untracked=[line[3:] for line in git(root,'status','--porcelain','--untracked-files=all').splitlines() if line.startswith('?? ')]
    return {'tracked':files,'untracked':sorted(untracked)}

def workspace_events(root, record):
    record.setdefault('history',[]).append({'time':now(),'state':record['state'],
                                              'changed':record.get('changed',[]),
                                              'verification':record.get('verification')})
    save(workspace_record_path(root,record['id']),record)

def workspace_start(root, cycle, stage_id, attempt):
    cfg=config(root)
    if not branching_cfg(cfg): raise Invalid('Workspace iterations require lifecycle branching enabled')
    require_clean(root,'start workspace iteration')
    if stage_id not in {s['id'] for s in cfg['stages']}: raise Invalid('Unknown stage: '+stage_id)
    attempt=branch_slug(attempt,'attempt id')
    identifier=branch_slug(cycle+'-'+stage_id.replace('/','-')+'-'+attempt,'workspace id')
    path=workspace_record_path(root,identifier)
    if path.exists(): raise Invalid('Workspace attempt already exists: '+identifier)
    state=branch_state(root); idea=state.get('idea_slug') or branching_cfg(cfg).get('idea_slug') or 'research'
    target=branch_names(cfg,idea,stage_id)[0]
    if not branch_exists(root,target):
        parent=branch_target(cfg,idea,stage_id)
        if not branch_exists(root,parent): raise Invalid('Initialize parent lifecycle branch before starting an iteration')
        git(root,'branch',target,parent)
    base=target
    branch=branch_ref_ok(f'{branch_slug(idea)}/iterations/{branch_slug(cycle)}/{branch_slug(stage_id.replace("/","-"))}/{attempt}')
    if branch_exists(root,branch): raise Invalid('Workspace branch already exists: '+branch)
    worktree=(root/'.auto-research/workspaces'/identifier).resolve()
    worktree.parent.mkdir(parents=True,exist_ok=True)
    baseline_manifest=workspace_manifest(root)
    git(root,'worktree','add','-b',branch,str(worktree),base)
    record={'version':1,'id':identifier,'cycle':cycle,'stage_id':stage_id,'attempt':attempt,
            'branch':branch,'target_branch':target,'baseline_commit':git(root,'rev-parse',base),
            'worktree':str(worktree),'baseline':baseline_manifest,'state':'active',
            'changed':[],'verification':None,'created_at':now(),'history':[]}
    save(path,record); workspace_events(root,record)
    return {'status':'started','id':identifier,'branch':branch,'target_branch':target,
            'baseline_commit':record['baseline_commit'],'worktree':str(worktree)}

def workspace_diff(root, record):
    wt=Path(record['worktree'])
    if not wt.is_dir(): raise Invalid('Workspace directory is missing; record retained')
    base=record['baseline_commit']
    committed=git(wt,'diff','--name-status',base+'...HEAD').splitlines()
    working=git(wt,'status','--porcelain','--untracked-files=all').splitlines()
    changes=sorted(set(committed+[line[3:] for line in working]))
    return changes

def workspace_baseline_drift(root, record):
    current=workspace_manifest(root); baseline=record['baseline']
    before,after=baseline['tracked'],current['tracked']
    changed=sorted(name for name in set(before)|set(after) if before.get(name)!=after.get(name))
    untracked=sorted(name for name in set(current['untracked'])-set(baseline['untracked'])
                     if not name.startswith('.auto-research/workspaces/'))
    return {'clean':not changed and not untracked,'changed_tracked':changed,'new_untracked':untracked}

def workspace_status(root, identifier):
    record=workspace_record(root,identifier)
    changes=workspace_diff(root,record) if record['state'] not in {'closed'} else record.get('changed',[])
    return {'id':identifier,'state':record['state'],'cycle':record['cycle'],'stage_id':record['stage_id'],
            'attempt':record['attempt'],'baseline_commit':record['baseline_commit'],'branch':record['branch'],
            'worktree':record['worktree'],'changed':changes,'baseline_drift':workspace_baseline_drift(root,record) if record['state']!='closed' else None,
            'verification':record.get('verification')}

def workspace_verify(root, identifier, commands):
    record=workspace_record(root,identifier)
    if record['state']!='active': raise Invalid('Only active workspaces can be verified')
    wt=Path(record['worktree']); results=[]
    if not commands: raise Invalid('At least one --command is required for verification')
    for command in commands:
        proc=subprocess.run(command,shell=True,cwd=wt,capture_output=True,text=True)
        results.append({'command':command,'exit_status':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr})
    record['changed']=workspace_diff(root,record)
    drift=workspace_baseline_drift(root,record)
    record['verification']={'time':now(),'commands':results,'passed':all(x['exit_status']==0 for x in results) and drift['clean'],
                            'baseline_drift':drift}
    if record['verification']['passed']:
        if git(wt,'status','--porcelain','--untracked-files=all'):
            for key in ('user.name','user.email'):
                if not git(wt,'config','--get',key,check=False):
                    raise Invalid('Configure project Git '+key+' before promoting an iteration')
            git(wt,'add','-A')
            git(wt,'commit','-m',f"research[{record['stage_id']}]: iteration {record['attempt']} verified")
        if git(wt,'rev-parse','HEAD')==record['baseline_commit']:
            raise Invalid('Verified iteration contains no committed changes')
    record['state']='verified' if record['verification']['passed'] else 'verification_failed'
    workspace_events(root,record)
    return {'status':record['state'],'id':identifier,'changed':record['changed'],'verification':record['verification']}

def workspace_promote(root, identifier):
    record=workspace_record(root,identifier)
    if record['state']!='verified' or not record.get('verification',{}).get('passed'):
        raise Invalid('Workspace must pass verification before promotion')
    require_clean(root,'promote workspace')
    if not workspace_baseline_drift(root,record)['clean']:
        raise Invalid('Project workspace drifted from iteration baseline; preserve attempt and create a fresh iteration')
    if current_branch(root)!=record['target_branch']:
        raise Invalid('Switch to target branch '+record['target_branch']+' before promotion')
    if git(root,'merge-base',record['baseline_commit'],'HEAD')!=record['baseline_commit']:
        raise Invalid('Target branch diverged from iteration baseline; create a fresh attempt')
    git(root,'merge','--no-ff','--no-edit',record['branch'])
    record['state']='promoted'; record['promoted_commit']=git(root,'rev-parse','HEAD')
    record['changed']=workspace_diff(root,record); workspace_events(root,record)
    return {'status':'promoted','id':identifier,'target_branch':record['target_branch'],'commit':record['promoted_commit']}

def workspace_close(root, identifier):
    record=workspace_record(root,identifier)
    if record['state']=='active': raise Invalid('Verify or retain the active workspace before closing')
    wt=Path(record['worktree'])
    if wt.exists():
        registered=git(root,'worktree','list','--porcelain')
        if str(wt) not in registered: raise Invalid('Workspace path is not registered as a Git worktree')
        dirty=git(wt,'status','--porcelain','--untracked-files=all')
        if dirty: raise Invalid('Workspace has uncommitted changes; preserve it and commit or archive before closing')
        git(root,'worktree','remove',str(wt))
    record['state']='closed'; workspace_events(root,record)
    return {'status':'closed','id':identifier,'branch_retained':record['branch'],'record':str(workspace_record_path(root,identifier))}

def init(root):
    root.mkdir(parents=True, exist_ok=True)
    repo = git(root, 'rev-parse', '--show-toplevel', check=False)
    if repo and Path(repo).resolve() != root:
        raise Invalid('Initialize at the research Git root, not inside an enclosing repository')
    if not repo: git(root, 'init')
    with lock(root):
        settings = root / RUNTIME / 'settings.json'
        if not settings.exists():
            defaults = Path(__file__).resolve().parents[1] / 'lifecycle/defaults.json'
            save(settings, read(defaults))
        ignore = root / RUNTIME / '.gitignore'
        if not ignore.exists(): atomic(ignore, 'local/\n')
        for d in ['refine-logs/history','logs/runs','results']: (root / d).mkdir(parents=True, exist_ok=True)
    return {'status': 'initialized', 'settings': str(settings), 'models': 'bindings must be verified by execution host'}

SECRET = re.compile(r'(?:sk-[A-Za-z0-9_-]{16,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY|(?:api[_-]?key|token|password)\s*[=:]\s*["\']?[^\s"\']{8,})', re.I)

def check_text(text):
    if SECRET.search(text): raise Invalid('Potential credential detected; register a redacted copy')

def verify_archive(root, index):
    if index.get('version') != 1 or index.get('kind') != 'archive_index':
        raise Invalid('Expected version 1 archive_index')
    if not index.get('artifacts'): raise Invalid('Archive index is empty')
    for item in index['artifacts']:
        location=item.get('path','')
        if '://' in location: raise Invalid('Remote archive must be mounted locally for verification')
        path=Path(location)
        if not path.is_absolute(): path=root/path
        if not path.is_file(): raise Invalid('Archive is not readable: '+location)
        if item.get('availability') not in {'local_only','archived'}: raise Invalid('Declare archive availability')
        if not item.get('checked_at') or not item.get('created_at'): raise Invalid('Archive timestamps required')
        sha=hashlib.sha256()
        with path.open('rb') as stream:
            for chunk in iter(lambda:stream.read(1024*1024), b''): sha.update(chunk)
        if sha.hexdigest()!=item.get('sha256') or path.stat().st_size!=item.get('bytes'):
            raise Invalid('Archive checksum/size mismatch: '+location)
    return {'valid':True,'verified_artifacts':len(index['artifacts'])}


def checkpoint(root, a):
    with lock(root):
        pending = root / RUNTIME / 'local/pending.json'
        if pending.exists(): raise Invalid('Pending checkpoint exists; run resume before creating another')
        cfg = config(root)
        check_text(json.dumps(cfg))
        stages = {s['id']: s for s in cfg['stages']}
        if a.stage not in stages: raise Invalid('Unknown stage: ' + a.stage)
        if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}', a.cycle): raise Invalid('Invalid cycle ID')
        st = stages[a.stage]; state = latest(root, a.cycle); prior = state.get(a.stage)
        if a.state == 'started' and prior: raise Invalid('Stage already exists in cycle; resume or use a new cycle')
        if a.state not in {'started','skipped'} and not prior and not (a.state == 'blocked' and a.summary.startswith('blocked_model_unavailable')): raise Invalid('Record started before this transition')
        if prior and prior['state'] in TERMINAL: raise Invalid('Terminal stage requires a new cycle')
        if a.state == 'resumed' and prior['state'] not in {'paused','failed','blocked'}: raise Invalid('Resume requires paused/failed/blocked state')
        if a.state not in {'started','skipped','resumed'} and prior and prior['state'] not in ACTIVE:
            raise Invalid('Resume inactive stage before further transitions')
        if st['parent_id'] and state.get(st['parent_id'],{}).get('state') not in ACTIVE:
            raise Invalid('Start/resume parent stage first')
        if a.state == 'completed':
            children = [s for s in cfg['stages'] if s['parent_id'] == a.stage]
            if any(state.get(s['id'],{}).get('state') not in TERMINAL for s in children):
                raise Invalid('Complete or explicitly skip all child stages first')
            if st.get('required_evidence') and not a.artifact: raise Invalid('Receipt/decision evidence required')
            if cfg.get('enforce_stage_contracts') and st['level'] == 3:
                from stage_contract import check_stage
                checked=check_stage(root,st,set(a.artifact))
                if checked['status'] != 'pass': raise Invalid('; '.join(checked['errors']))

        if not a.summary or not a.next: raise Invalid('Summary/reason and next action are required')
        # A missing model is itself recordable; all other events need verified execution identity.
        model = {'requested': cfg['roles'].get(a.role), 'actual_model': a.actual_model}
        if a.state == 'blocked' and a.summary.startswith('blocked_model_unavailable'):
            pass
        else:
            model.update(route(cfg, a.role, a.actual_model))
            if not a.actual_model: raise Invalid('Actual execution model is required')
        if git(root, 'diff', '--name-only', '--diff-filter=U'): raise Invalid('Resolve Git conflicts before checkpointing')
        for key in ('user.name','user.email'):
            if not git(root,'config','--get',key,check=False): raise Invalid('Configure project Git ' + key)
        branch_meta = None
        if branching_cfg(cfg):
            if git(root, 'rev-parse', '--verify', 'HEAD', check=False):
                branch_meta = _branch_start_unlocked(root, cfg, a.cycle, a.stage)
            else:
                branch_meta = {'status':'pending-bootstrap','branch':None}
        registered = sorted(set(relative(root,n) for n in a.artifact))
        records=[]; cp='cp-' + uuid.uuid4().hex
        snapshot=[]
        for name in registered:
            p=root/name
            if not p.is_file(): raise Invalid('Missing artifact: '+name)
            if p.stat().st_size > cfg['max_git_file_bytes']: raise Invalid('Large artifact: register an archive index instead: '+name)
            try: content=p.read_text(encoding='utf-8')
            except UnicodeError: raise Invalid('Binary artifact: register archive index instead: '+name)
            check_text(content)
            if p.suffix == '.json':
                try: candidate=json.loads(content)
                except json.JSONDecodeError: candidate=None
                if isinstance(candidate,dict) and candidate.get('kind')=='archive_index': verify_archive(root,candidate)
            records.append({'path':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
            if a.state == 'revised' or p.suffix in {'.md','.json','.yaml','.yml','.toml'}:
                dest=f'refine-logs/history/{a.cycle}/{cp}/{name}'
                snapshot.append((dest,content))
        event={'checkpoint_id':cp,'stage_id':a.stage,'parent_id':st['parent_id'],'level':st['level'],
               'execution_id':prior['execution_id'] if prior else 'exec-'+uuid.uuid4().hex,
               'cycle':a.cycle,'state':a.state,'time':now(),'role':a.role,'model':model,
               'summary':a.summary,'next':a.next,'inputs':a.input,'artifacts':records,
               'command':a.command,'run_ids':a.run_id,'submission_id':a.submission_id,'revision_id':a.revision_id,
               'branch':branch_meta.get('branch') if branch_meta else None,
               'integration_branch':(branch_state(root).get('integration_branch') if branch_meta else None)}
        check_text(json.dumps(event))
        paths=registered+[str(RUNTIME/'events.jsonl'),str(RUNTIME/'settings.json'),str(RUNTIME/'.gitignore')]+[p for p,_ in snapshot]
        if branch_meta: paths.append(str(BRANCH_LOG))
        # Existing unrelated index entries remain untouched: commit --only uses an explicit pathspec.
        msg=f'research[{a.stage}]: {a.state}\n\nCheckpoint-ID: {cp}\nCycle: {a.cycle}\n{a.summary}'
        journal={'checkpoint_id':cp,'paths':paths,'message':msg,'event':event,'snapshots':snapshot}
        save(pending,journal)
        return finish_pending(root,journal)

def finish_pending(root,journal):
    cp=journal['checkpoint_id']; p=root/RUNTIME/'events.jsonl'
    commits=committed(root,cp)
    if not commits:
        cfg = config(root)
        old=p.read_text(encoding='utf-8') if p.exists() else ''
        if not any(e['checkpoint_id']==cp for e in events(root)):
            atomic(p,old+json.dumps(journal['event'],ensure_ascii=False,sort_keys=True)+'\n')
        if branching_cfg(cfg) and not git(root, 'rev-parse', '--verify', 'HEAD', check=False):
            for key in ('user.name','user.email'):
                if not git(root, 'config', '--get', key, check=False):
                    raise Invalid('Configure project Git ' + key + ' before initializing branches')
            git(root, 'commit', '--allow-empty', '--only', '-m', f"research[{journal['event']['cycle']}]: initialize branch baseline")
            branch_meta = _branch_start_unlocked(root, cfg, journal['event']['cycle'], journal['event']['stage_id'])
            journal['event']['branch'] = branch_meta.get('branch')
            journal['event']['integration_branch'] = branch_state(root).get('integration_branch')
            if str(BRANCH_LOG) not in journal['paths']: journal['paths'].append(str(BRANCH_LOG))
            replace_event(root, journal['event'])
            save(root / RUNTIME / 'local/pending.json', journal)
        for name,content in journal['snapshots']: atomic(root/name,content)
        paths=journal['paths']
        for record in journal['event']['artifacts']:
            artifact=root/record['path']
            if not artifact.is_file() or hashlib.sha256(artifact.read_bytes()).hexdigest()!=record['sha256']:
                raise Invalid('Pending artifact changed; restore recorded artifact before resume: '+record['path'])
        git(root,'add','--',*paths)
        git(root,'commit','--only','-m',journal['message'],'--',*paths)
        commits=committed(root,cp)
    if not commits: raise Invalid('Checkpoint commit not found')
    branch_merge_result = None
    if journal['event'].get('state') in TERMINAL and branching_cfg(config(root)):
        branch_merge_result = _merge_stage_unlocked(
            root, config(root), journal['event']['cycle'], journal['event']['stage_id'], cp
        )
    (root/RUNTIME/'local/pending.json').unlink(missing_ok=True)
    result = {'checkpoint_id':cp,'commit':commits[0],'status':'committed'}
    if branch_merge_result is not None: result['branch_merge'] = branch_merge_result
    return result

def status(root,cycle):
    cfg=config(root); state=latest(root,cycle)
    pending=root/RUNTIME/'local/pending.json'
    return {'cycle':cycle,'pending_checkpoint':read(pending)['checkpoint_id'] if pending.exists() else None,
            'stages':[{'id':s['id'],'parent_id':s['parent_id'],'level':s['level'],
                       'state':state.get(s['id'],{}).get('state','not_started')} for s in cfg['stages']]}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--project-root',type=Path,default=Path('.'))
    sub=p.add_subparsers(dest='action',required=True)
    sub.add_parser('init')
    ap=sub.add_parser('archive-check'); ap.add_argument('index',type=Path)
    for name in ['status','resume']:
        sp=sub.add_parser(name); sp.add_argument('--cycle',default='cycle-001')
    rp=sub.add_parser('route'); rp.add_argument('role',choices=['research','planner','executor','writer'])
    bp=sub.add_parser('branch'); bps=bp.add_subparsers(dest='branch_action',required=True)
    bi=bps.add_parser('init'); bi.add_argument('--cycle',default='cycle-001'); bi.add_argument('--idea')
    bs=bps.add_parser('start'); bs.add_argument('--cycle',default='cycle-001'); bs.add_argument('--stage',required=True); bs.add_argument('--idea')
    bm=bps.add_parser('merge'); bm.add_argument('--cycle',default='cycle-001'); bm.add_argument('--stage',required=True)
    bc=bps.add_parser('close'); bc.add_argument('--cycle',default='cycle-001')
    br=bps.add_parser('revision'); br.add_argument('--cycle',default='cycle-001'); br.add_argument('--kind',choices=['submission','revision'],required=True); br.add_argument('--id',dest='identifier',required=True)
    bstatus=bps.add_parser('status'); bstatus.add_argument('--cycle',default='cycle-001')
    wp=sub.add_parser('workspace'); wps=wp.add_subparsers(dest='workspace_action',required=True)
    ws=wps.add_parser('start'); ws.add_argument('--cycle',default='cycle-001'); ws.add_argument('--stage',required=True); ws.add_argument('--attempt',required=True)
    wst=wps.add_parser('status'); wst.add_argument('id')
    wv=wps.add_parser('verify'); wv.add_argument('id'); wv.add_argument('--command',action='append',default=[])
    wprom=wps.add_parser('promote'); wprom.add_argument('id')
    wcl=wps.add_parser('close'); wcl.add_argument('id')
    cp=sub.add_parser('checkpoint')
    cp.add_argument('--stage',required=True); cp.add_argument('--state',choices=sorted(STATES),required=True)
    cp.add_argument('--cycle',default='cycle-001'); cp.add_argument('--role',choices=['research','planner','executor','writer'],required=True)
    cp.add_argument('--actual-model'); cp.add_argument('--summary',required=True); cp.add_argument('--next',required=True)
    for key in ['artifact','input','run-id']: cp.add_argument('--'+key,action='append',default=[])
    for key in ['command','submission-id','revision-id']: cp.add_argument('--'+key)
    a=p.parse_args(argv); root=a.project_root.resolve()
    try:
        if a.action=='init': result=init(root)
        elif a.action=='archive-check': result=verify_archive(root,read(a.index))
        elif a.action=='route': result=route(config(root),a.role)
        elif a.action=='status': result=status(root,a.cycle)
        elif a.action=='checkpoint': result=checkpoint(root,a)
        elif a.action=='branch':
            if a.branch_action=='init': result=branch_init(root,a.cycle,a.idea)
            elif a.branch_action=='start': result=branch_start(root,a.cycle,a.stage,a.idea)
            elif a.branch_action=='merge': result=branch_merge(root,a.cycle,a.stage)
            elif a.branch_action=='close': result=branch_close(root,a.cycle)
            elif a.branch_action=='revision': result=branch_revision(root,a.cycle,a.kind,a.identifier)
            else: result=branch_status(root,a.cycle)
        elif a.action=='workspace':
            if a.workspace_action=='start': result=workspace_start(root,a.cycle,a.stage,a.attempt)
            elif a.workspace_action=='status': result=workspace_status(root,a.id)
            elif a.workspace_action=='verify': result=workspace_verify(root,a.id,a.command)
            elif a.workspace_action=='promote': result=workspace_promote(root,a.id)
            else: result=workspace_close(root,a.id)
        else:
            with lock(root):
                pending=root/RUNTIME/'local/pending.json'
                result=finish_pending(root,read(pending)) if pending.exists() else status(root,a.cycle)
                result['resume_instruction']='Reconcile recorded run IDs with live process/queue and output files before launching; do not infer completion from tracker alone.'
        print(json.dumps(result,ensure_ascii=False,indent=2)); return 0
    except (Invalid, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({'status':'blocked','error':str(exc)},ensure_ascii=False)); return 1
    except OSError as exc:
        print(json.dumps({'status':'tool_error','error':str(exc)},ensure_ascii=False)); return 2

if __name__=='__main__': sys.exit(main())
