#!/usr/bin/env python3
"""Persistent host-driven subagent scheduling, not an LLM runner or filesystem sandbox.

Python 3.10+ stdlib. Atomic single-state transactions + OS process lock. Host agents
perform spawn/stop/integrate/test/review; this tool checks claims, hashes and evidence.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import copy
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import sys
import time
import uuid

from game_design import atomic_write
from production_tools import load_data

HOME=Path(__file__).resolve().parents[1]
STATE='.game-design/state/parallel.json'
LOCK='.game-design/state/.parallel.lock'
ID=re.compile(r'[A-Za-z][A-Za-z0-9_-]*\Z')
RESERVED={'.git','.claude','.codex'}
HELD={'running','submitted','integrated','validated','blocked'}


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for value in iter(lambda:stream.read(1024*1024),b''):h.update(value)
    return h.hexdigest()


def nonempty(value,label):
    if not isinstance(value,str) or not value.strip():raise ValueError(label+' requires text')
    return value


def ident(value,label):
    nonempty(value,label)
    if not ID.fullmatch(value):raise ValueError(label+' requires a stable ASCII identifier')
    return value


def relative(value,write=False):
    nonempty(value,'path')
    if '\\' in value or ':' in value or any(c in value for c in '*?[]\x00\n\r'):
        raise ValueError('use literal project-relative paths, not globs or drive paths')
    path=PurePosixPath(value)
    if path.is_absolute() or value.strip('/') in ('','.') or any(x in ('','.','..') for x in value.rstrip('/').split('/')):
        raise ValueError('invalid or escaping project-relative path: '+value)
    for part in path.parts:
        stem=part.split('.')[0].casefold()
        if part.endswith((' ','.')) or stem in {'con','prn','aux','nul'} or re.fullmatch(r'(?:com|lpt)[1-9]',stem):
            raise ValueError('ambiguous/reserved cross-platform filename')
    if write and (path.parts[0].casefold() in RESERVED or
                  overlaps(path.as_posix(),'.game-design/state')):
        raise ValueError('worker scope includes reserved coordinator/host state')
    return path.as_posix()


def local(root,value):
    path=root
    for part in PurePosixPath(relative(value)).parts:
        path=path/part
        if path.is_symlink():raise ValueError('symlink path: '+value)
    return path


def overlaps(a,b):
    # Conservative across case-sensitive and case-insensitive target platforms.
    ap=PurePosixPath(a.casefold());bp=PurePosixPath(b.casefold())
    return ap==bp or ap.is_relative_to(bp) or bp.is_relative_to(ap)


def covered(path,task):return any(overlaps(path,scope) and PurePosixPath(path.casefold()).is_relative_to(PurePosixPath(scope.casefold())) for scope in task['writes'])


def hashes(root,paths):
    result={}
    for name in paths:
        path=local(root,name)
        if not path.is_file() or path.stat().st_size==0:raise ValueError('missing/empty file: '+name)
        result[name]=digest(path)
    return result


def same_hashes(root,expected):
    if hashes(root,list(expected))!=expected:raise ValueError('frozen input/artifact hash changed')


def definitions():
    _,production,_=load_data()
    from render_agents import load_roles
    source=load_roles()
    roles={r['id']:r for r in source['roles']}
    packages={t['id']:(area['id'],t) for area in production['areas'] for t in area['tasks']}
    return roles,packages


def validate_plan(root,plan):
    if not isinstance(plan,dict) or type(plan.get('schema_version')) is not int or plan['schema_version']!=1:raise ValueError('plan schema_version must be 1')
    if plan.get('mode') not in ('design-only','implementation'):raise ValueError('plan mode required')
    count=plan.get('max_parallel',3);lease=plan.get('lease_seconds',1800)
    if type(count) is not int or not 1<=count<=64:raise ValueError('max_parallel must be 1..64; host must cap actual capacity')
    if type(lease) not in (int,float) or not math.isfinite(lease) or not 1<=lease<=86400:raise ValueError('lease_seconds must be finite, 1..86400')
    profile=root/'.game-design/state/project.json'
    if profile.is_file() and json.loads(profile.read_text()).get('mode')!=plan['mode']:raise ValueError('plan mode conflicts with existing project profile')
    roles,packages=definitions();gates={}
    for gate in plan.get('gates',[]):
        gid=ident(gate.get('id'),'gate ID')
        if gid in gates:raise ValueError('duplicate gate')
        gates[gid]={'status':'pending'} # External plan text never pre-approves a human decision.
    waivers=plan.get('waivers',{})
    if not isinstance(waivers,dict):raise ValueError('waivers must map omitted package IDs to reasons')
    for pid,reason in waivers.items():
        if pid not in packages:raise ValueError('unknown waived package')
        nonempty(reason,'waiver reason/alternative input')
    tasks={};selected={}
    if not isinstance(plan.get('tasks'),list) or not plan['tasks']:raise ValueError('plan tasks required')
    for entry in plan['tasks']:
        task=copy.deepcopy(entry);tid=ident(task.get('id'),'task ID')
        if tid in tasks:raise ValueError('duplicate task ID')
        package=task.get('package_id')
        if package is not None:
            if package not in packages or package in selected:raise ValueError('unknown or duplicate package_id')
            selected[package]=tid
            if not task.get('role'):
                area=packages[package][0]
                task['role']=next((key for key,role in roles.items() if area in role['areas']),None)
        else:nonempty(task.get('custom_reason'),'project-specific task reason')
        if task.get('role') not in roles:raise ValueError('unknown native role')
        if task.get('effect') not in ('design','implementation'):raise ValueError('task effect required')
        for key in ('depends_on','writes','resources','inputs','outputs','gates'):
            values=task.get(key,[])
            if not isinstance(values,list) or any(not isinstance(x,str) or not x.strip() for x in values) or len(set(values))!=len(values):raise ValueError('invalid/duplicate task '+key)
            task[key]=values
        if not task['writes'] or not task['outputs']:raise ValueError('explicit writes and outputs required')
        for key in ('writes','inputs','outputs'):task[key]=[relative(x,write=key!='inputs') for x in task[key]]
        if any(not covered(path,task) for path in task['outputs']):raise ValueError('output outside declared writes')
        for scope in task['writes']:local(root,scope)
        if any(g not in gates for g in task['gates']):raise ValueError('unknown human gate')
        if task['effect']=='implementation' and (plan['mode']!='implementation' or not task['gates']):raise ValueError('implementation tasks require implementation mode and explicit human gates')
        workspace=Path(task.get('workspace',str(root))).expanduser()
        if not workspace.is_absolute():workspace=root/workspace
        workspace=workspace.resolve()
        if not workspace.is_dir():raise ValueError('task workspace must already exist; host creates isolated worktrees')
        task.update(workspace=str(workspace),status='pending',attempt=0,claim_token=None,run_id=None,worker=None,lease_until=None,
                    input_hashes={},artifact_hashes={},history=[],stages={})
        tasks[tid]=task
    indegree={t:0 for t in tasks};children={t:[] for t in tasks}
    for tid,task in tasks.items():
        for dep in task['depends_on']:
            if dep not in tasks or dep==tid:raise ValueError('unknown/self task dependency')
            indegree[tid]+=1;children[dep].append(tid)
        if task.get('package_id'):
            for dependency in packages[task['package_id']][1]['depends_on']:
                if dependency in selected:
                    if selected[dependency] not in task['depends_on']:raise ValueError('selected package dependency omitted from project DAG')
                elif dependency not in waivers:raise ValueError('omitted package dependency needs explicit waiver: '+dependency)
    ready=sorted(k for k,n in indegree.items() if not n);order=[]
    while ready:
        key=ready.pop(0);order.append(key)
        for child in children[key]:
            indegree[child]-=1
            if indegree[child]==0:ready.append(child);ready.sort()
    if len(order)!=len(tasks):raise ValueError('project dependency cycle')
    return {'schema_version':1,'revision':0,'plan_id':uuid.uuid4().hex,'mode':plan['mode'],'max_parallel':count,'lease_seconds':lease,
            'gates':gates,'waivers':waivers,'tasks':tasks,'order':order,'events':[]}


@contextmanager
def transaction_lock(root):
    path=local(root,LOCK);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a+b') as stream:
        if os.name=='nt':
            import msvcrt
            stream.seek(0)
            if not stream.read(1):stream.write(b'0');stream.flush()
            stream.seek(0);msvcrt.locking(stream.fileno(),msvcrt.LK_LOCK,1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(),fcntl.LOCK_EX)
        try:yield
        finally:
            if os.name=='nt':stream.seek(0);msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(stream.fileno(),fcntl.LOCK_UN)


def read_state(root):
    value=json.loads(local(root,STATE).read_text(encoding='utf-8'))
    if value.get('schema_version')!=1 or not isinstance(value.get('tasks'),dict):raise ValueError('invalid parallel state')
    return value


def save(root,state,event,task=None):
    state['revision']+=1
    state['events'].append({'revision':state['revision'],'time':time.time(),'event':event,'task':task})
    atomic_write(local(root,STATE),(json.dumps(state,ensure_ascii=False,indent=2)+'\n').encode())


def conflict(task,other):
    if {x.casefold() for x in task['resources']} & {x.casefold() for x in other['resources']}:return True
    return (any(overlaps(a,b) for a in task['writes'] for b in other['writes'])
            or any(overlaps(a,b) for a in task['inputs'] for b in other['writes'])
            or any(overlaps(a,b) for a in task['writes'] for b in other['inputs']))


def next_tasks(root,state,limit=None):
    running=sum(t['status']=='running' for t in state['tasks'].values())
    capacity=max(0,state['max_parallel']-running)
    if limit is not None:capacity=min(capacity,limit)
    held=[t for t in state['tasks'].values() if t['status'] in HELD]
    ready=[];blocked={}
    for tid in state['order']:
        task=state['tasks'][tid]
        if task['status']!='pending':continue
        reasons=[]
        for dep in task['depends_on']:
            parent=state['tasks'][dep]
            if parent['status']!='done':reasons.append('dependency not independently reviewed: '+dep)
            else:
                try:immutable(root,parent,state)
                except (OSError,ValueError) as exc:reasons.append('dependency changed: '+dep+': '+str(exc))
        for gate in task['gates']:
            value=state['gates'][gate]
            if value['status']!='approved':reasons.append('waiting_human: '+gate)
            else:
                ref=value['evidence']
                try:same_hashes(root,{ref['path']:ref['sha256']})
                except (OSError,ValueError):reasons.append('human decision evidence changed: '+gate)
        try:hashes(Path(task['workspace']),task['inputs'])
        except (OSError,ValueError) as exc:reasons.append('waiting_dependency: '+str(exc))
        if any(conflict(task,owner) for owner in held+ready):reasons.append('write/resource reservation conflict')
        if not reasons and len(ready)<capacity:ready.append(copy.deepcopy(task))
        else:blocked[tid]=reasons or ['parallel capacity reached']
    return {'ready':ready,'blocked':blocked,'capacity':capacity}


def claimed(state,tid,token,live=True):
    if tid not in state['tasks']:raise ValueError('unknown task')
    task=state['tasks'][tid]
    if task['claim_token']!=token or not token:raise ValueError('stale/invalid claim token')
    if live and (task['status']!='running' or task['lease_until']<=time.time()):raise ValueError('task is not live; expiry retains reservation until host stop/recovery')
    return task


def evidence(root,value):
    path=local(root,relative(value))
    if not path.is_file() or path.stat().st_size==0:raise ValueError('non-empty stage evidence required')
    return {'path':relative(value),'sha256':digest(path)}


def immutable(root,task,state,exempt=(),seen=None):
    # A successor may intentionally revise an owned input/output in place.
    # Its baseline is checked at claim; readonly dependencies remain frozen.
    seen=set() if seen is None else seen
    key=(task['id'],tuple(sorted(exempt)))
    if key in seen:return
    seen.add(key)
    def check(expected,extra=()):
        skip=tuple(exempt)+tuple(extra)
        same_hashes(root,{p:h for p,h in expected.items() if not any(covered(p,{'writes':[s]}) for s in skip)})
    check(task['input_hashes'],task['writes']);check(task['artifact_hashes'])
    for ref in task.get('result',{}).get('verified_evidence',[]):
        values={ref['path']:ref['sha256']}
        if ref['path'] in task['artifact_hashes']:check(values)
        else:same_hashes(root,values)
    for gid in task['gates']:
        gate=state['gates'][gid]
        if gate['status']!='approved':raise ValueError('human gate not approved')
        ref=gate['evidence'];same_hashes(root,{ref['path']:ref['sha256']})
    for stage in task['stages'].values():
        ref=stage['evidence'];same_hashes(root,{ref['path']:ref['sha256']})
    for tid in task['depends_on']:
        parent=state['tasks'][tid]
        if parent['status']!='done':raise ValueError('dependency no longer approved')
        immutable(root,parent,state,tuple(exempt)+tuple(task['writes']),seen)


def execute(root,args):
    if args.operation=='init':
        plan=json.loads(Path(args.plan).read_text(encoding='utf-8'));prepared=validate_plan(root,plan)
        if args.dry_run:return {'status':'preview','tasks':len(prepared['tasks']),'writes':False}
        with transaction_lock(root):
            if local(root,STATE).exists():raise ValueError('parallel state already exists; preserve it and extend through a new approved plan revision')
            save(root,prepared,'init')
        return prepared
    if args.operation in ('status','next'):
        state=read_state(root)
        return state if args.operation=='status' else next_tasks(root,state)
    with transaction_lock(root):
        state=read_state(root);operation=args.operation
        if operation=='extend':
            nonempty(args.reason,'replan reason')
            ref=evidence(root,args.evidence)
            proposed=validate_plan(root,json.loads(Path(args.plan).read_text(encoding='utf-8')))
            static=('id','package_id','custom_reason','role','depends_on','writes','resources','inputs','outputs','effect','gates','workspace')
            old_mode=state['mode']
            if proposed['mode']!=old_mode and not (old_mode=='design-only' and proposed['mode']=='implementation'
                    and all(t['status']=='done' for t in state['tasks'].values())):
                raise ValueError('mode promotion requires all design tasks reviewed; other mode changes need a new explicit scope')
            if not set(state['gates'])<=set(proposed['gates']):raise ValueError('extend preserves existing human gates')
            for tid,task in state['tasks'].items():
                if tid not in proposed['tasks'] or any(task.get(k)!=proposed['tasks'][tid].get(k) for k in static):raise ValueError('extend preserves existing task definitions; create a new task for changed work')
            added=sorted(set(proposed['tasks'])-set(state['tasks']))
            if args.dry_run:return {'status':'preview','added':added,'writes':False}
            for tid in added:state['tasks'][tid]=proposed['tasks'][tid]
            for gid in proposed['gates']:state['gates'].setdefault(gid,proposed['gates'][gid])
            state.update(mode=proposed['mode'],order=proposed['order'],waivers=proposed['waivers'],max_parallel=proposed['max_parallel'],lease_seconds=proposed['lease_seconds'])
            state.setdefault('replans',[]).append({'reason':args.reason,'evidence':ref,'added':added,'old_mode':old_mode,'new_mode':state['mode'],'time':time.time()})
            save(root,state,operation);return {'added':added,'revision':state['revision']}
        if operation=='claim':
            if args.limit is not None and args.limit<=0:raise ValueError('claim limit must be positive')
            jobs=next_tasks(root,state,args.limit)['ready'];nonempty(args.worker,'worker prefix')
            for job in jobs:
                task=state['tasks'][job['id']]
                task.update(status='running',attempt=task['attempt']+1,claim_token=uuid.uuid4().hex,
                            worker=args.worker+':'+task['id'],lease_until=time.time()+state['lease_seconds'],run_id=None,
                            input_hashes=hashes(Path(task['workspace']),task['inputs']))
            if jobs:save(root,state,'claim')
            return {'claimed':[state['tasks'][j['id']] for j in jobs],'revision':state['revision']}
        if operation=='approve-gate':
            if args.gate not in state['gates']:raise ValueError('unknown gate')
            nonempty(args.actor,'human decision identity')
            state['gates'][args.gate]={'status':'approved','actor':args.actor,'evidence':evidence(root,args.evidence)}
            save(root,state,operation);return state['gates'][args.gate]
        if operation in ('bind','heartbeat','recover'):
            task=claimed(state,args.id,args.token,live=operation!='recover')
            if operation=='bind':
                nonempty(args.run_id,'actual host run ID')
                if task['run_id'] is not None and task['run_id']!=args.run_id:raise ValueError('claim already bound to another run')
                if any(t['run_id']==args.run_id and t['id']!=task['id'] for t in state['tasks'].values()):raise ValueError('host run ID already used')
                task['run_id']=args.run_id
            elif operation=='heartbeat':task['lease_until']=time.time()+state['lease_seconds']
            else:
                if not args.stopped:raise ValueError('host must first stop the original worker and confirm --stopped')
                nonempty(args.reason,'recovery reason');ref=evidence(root,args.evidence)
                if task['status']=='done':raise ValueError('completed work needs a new plan, not automatic recovery')
                task['history'].append({key:copy.deepcopy(task.get(key)) for key in ('attempt','claim_token','run_id','worker','status','input_hashes','artifact_hashes','stages','result')})
                task['history'][-1].update(stop_evidence=ref,reason=args.reason)
                task.update(status='pending',claim_token=None,run_id=None,worker=None,lease_until=None,input_hashes={},artifact_hashes={},stages={})
                task.pop('result',None)
            save(root,state,operation,task['id']);return task
        if operation=='submit':
            result=json.loads(Path(args.result).read_text(encoding='utf-8'))
            task=claimed(state,result.get('task_id'),result.get('claim_token'))
            if task['run_id'] is None:raise ValueError('bind an actual host worker run before collecting its result')
            nonempty(result.get('summary'),'result summary')
            if result.get('status') not in ('submitted','failed','blocked'):raise ValueError('invalid worker result status')
            worker=Path(task['workspace'])
            same_hashes(worker,{p:h for p,h in task['input_hashes'].items() if not covered(p,task)})
            for tid in task['depends_on']:
                parent=state['tasks'][tid]
                if parent['status']!='done':raise ValueError('dependency no longer approved')
                immutable(root,parent,state,task['writes'])
            entries=result.get('artifacts');refs=result.get('evidence');tests=result.get('tests')
            if not isinstance(entries,list) or not isinstance(refs,list) or not refs or not isinstance(tests,list) or not tests:raise ValueError('artifacts, evidence, and verification records required')
            actual={}
            for entry in entries:
                path=relative(entry['path'],write=True)
                if path in actual or not covered(path,task):raise ValueError('duplicate/out-of-scope result artifact')
                sha=digest(local(worker,path))
                if sha!=entry.get('sha256'):raise ValueError('worker artifact digest mismatch')
                actual[path]=sha
            if result['status']=='submitted' and not set(task['outputs'])<=actual.keys():raise ValueError('declared outputs missing from result')
            verified_refs=[]
            for ref in refs:
                path=relative(ref,write=True)
                if not covered(path,task):raise ValueError('worker evidence outside write scope')
                verified_refs.append(evidence(worker,path))
            for test in tests:
                nonempty(test.get('name'),'test name');nonempty(test.get('command'),'test command/operation')
                if test.get('status') not in ('pass','fail','not_run'):raise ValueError('invalid test status')
                code=test.get('exit_status')
                if code is not None and type(code) is not int:raise ValueError('literal exit_status must be int or null')
                if test['status']=='pass' and code is None:raise ValueError('pass needs a literal command exit status')
            task.update(status='submitted' if result['status']=='submitted' else 'blocked',artifact_hashes=actual,
                        result={**result,'verified_evidence':verified_refs},lease_until=None)
            save(root,state,operation,task['id']);return task
        task=state['tasks'].get(args.id)
        if task is None:raise ValueError('unknown task')
        nonempty(args.actor,'stage actor run ID')
        if args.actor==task['run_id'] or args.actor==task['worker']:raise ValueError('author may not integrate, validate, or independently review own work')
        if operation=='integrate':
            if task['status']!='submitted':raise ValueError('integration requires submitted work')
            immutable(root,task,state);task['status']='integrated'
        elif operation=='validate':
            if task['status']!='integrated':raise ValueError('validation requires integrated work')
            if args.actor==task['stages']['integrate']['actor']:raise ValueError('QA must be a distinct context from integration')
            immutable(root,task,state);task['status']='validated' if args.decision=='pass' else 'blocked'
        elif operation=='review':
            if task['status']!='validated':raise ValueError('independent review requires validated work')
            if args.actor in {s['actor'] for s in task['stages'].values()}:raise ValueError('reviewer must differ from integrator and QA')
            immutable(root,task,state);task['status']='done' if args.decision=='pass' else 'blocked'
        else:raise ValueError('unknown operation')
        task['stages'][operation]={'actor':args.actor,'decision':getattr(args,'decision','integrated'),'evidence':evidence(root,args.evidence),
                                   'artifact_hashes':dict(task['artifact_hashes']),'time':time.time()}
        save(root,state,operation,task['id']);return task


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--project',type=Path,default=Path('.'))
    sub=p.add_subparsers(dest='operation',required=True)
    init=sub.add_parser('init');init.add_argument('--plan',required=True);init.add_argument('--dry-run',action='store_true')
    extend=sub.add_parser('extend');extend.add_argument('--plan',required=True);extend.add_argument('--reason',required=True);extend.add_argument('--evidence',required=True);extend.add_argument('--dry-run',action='store_true')
    for name in ('status','next'):sub.add_parser(name)
    claim=sub.add_parser('claim');claim.add_argument('--worker',required=True);claim.add_argument('--limit',type=int)
    gate=sub.add_parser('approve-gate');gate.add_argument('--gate',required=True);gate.add_argument('--actor',required=True);gate.add_argument('--evidence',required=True)
    for name in ('bind','heartbeat','recover'):
        cmd=sub.add_parser(name);cmd.add_argument('--id',required=True);cmd.add_argument('--token',required=True)
        if name=='bind':cmd.add_argument('--run-id',required=True)
        if name=='recover':
            cmd.add_argument('--stopped',action='store_true');cmd.add_argument('--evidence',required=True);cmd.add_argument('--reason',required=True)
    submit=sub.add_parser('submit');submit.add_argument('--result',required=True)
    for name in ('integrate','validate','review'):
        cmd=sub.add_parser(name);cmd.add_argument('--id',required=True);cmd.add_argument('--actor',required=True);cmd.add_argument('--evidence',required=True)
        if name!='integrate':cmd.add_argument('--decision',required=True,choices=('pass','fail','not_run') if name=='validate' else ('pass','changes_requested','not_run'))
    args=p.parse_args()
    try:
        root=args.project.expanduser().resolve()
        if not root.is_dir():raise ValueError('project directory missing')
        print(json.dumps(execute(root,args),ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError,TypeError,KeyError,AttributeError) as exc:
        print(json.dumps({'status':'error','error':str(exc)},ensure_ascii=False),file=sys.stderr);return 2

if __name__=='__main__':sys.exit(main())
