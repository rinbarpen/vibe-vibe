#!/usr/bin/env python3
"""Expand approved experiment matrices and aggregate traceable local results; never launches jobs."""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
from urllib.parse import urlparse
import statistics
import sys
from research_workflow import Invalid, read, save, atomic, relative


INTERACTION_CONTRACT = "budget-decision-v1"


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def seeds(value):
    if not isinstance(value,list) or not value or any(type(x) is not int for x in value) or len(value)!=len(set(value)):
        raise Invalid('seeds must be a non-empty list of distinct integers')
    return value

def validate(plan):
    if plan.get('version')!=1: raise Invalid('Unknown experiment version')
    if plan.get('interaction_contract') not in (None, INTERACTION_CONTRACT):
        raise Invalid('Unknown budget interaction contract')
    seeds(plan.get('seeds',[42]))
    if type(plan.get('max_parallel',4)) is not int or plan.get('max_parallel',4)<1: raise Invalid('max_parallel must be positive')
    metrics=plan.get('metrics',{})
    if not metrics: raise Invalid('Declare metrics')
    for m,v in metrics.items():
        if v.get('direction') not in {'maximize','minimize'} or not isinstance(v.get('unit'),str):
            raise Invalid('Metric direction/unit required: '+m)
    experiments=plan.get('experiments',[])
    ids=[e['id'] for e in experiments]
    if not ids or len(ids)!=len(set(ids)): raise Invalid('Experiment IDs must be nonempty and unique')
    for e in experiments:
        seeds(e.get('seeds',plan.get('seeds',[42])))
        for field in ('datasets','protocol','comparison_group','command','claim_ids'):
            if not e.get(field): raise Invalid('Missing '+field+' for '+e['id'])
        if not isinstance(e['command'],list) or not all(isinstance(s,str) for s in e['command']): raise Invalid('command must be an argv list')
        if len(e['datasets'])!=len(set(e['datasets'])): raise Invalid('Duplicate dataset')
        if e.get('kind') not in {'baseline','main','ablation','sanity'}: raise Invalid('Unknown experiment kind')
        if e.get('baseline') and e['baseline'] not in ids: raise Invalid('Unknown baseline')
        if e.get('source_kind','reproduced') not in {'reproduced','checkpoint_evaluated'}: raise Invalid('Paper-reported values belong in the literature table, not execution matrix')
        for dep in e.get('depends_on',[]):
            if dep not in ids: raise Invalid('Missing experiment dependency')
        if any(not isinstance(v,list) or not v for v in e.get('grid',{}).values()): raise Invalid('Grid axes must be nonempty arrays')
        for key in ('estimated_cost','estimated_gpu_hours'):
            value=e.get(key,0)
            if not isinstance(value,(int,float)) or not math.isfinite(value) or value<0: raise Invalid('Invalid '+key)
    graph={e['id']:e.get('depends_on',[]) for e in experiments}
    def visit(n,stack):
        if n in stack: raise Invalid('Experiment dependency cycle')
        for child in graph[n]: visit(child,stack+[n])
    for n in graph: visit(n,[])
    return plan


def expand(plan):
    validate(plan); runs=[]
    for e in plan['experiments']:
        keys=sorted(e.get('grid',{}))
        configs=list(itertools.product(*(e['grid'][k] for k in keys)))
        for dataset in e['datasets']:
            for values in configs:
                params=dict(zip(keys,values))
                for seed in e.get('seeds',plan.get('seeds',[42])):
                    identity={'experiment_id':e['id'],'dataset':dataset,'protocol':e['protocol'],'parameters':params,'seed':seed}
                    config_hash=digest({'experiment':e,'identity':identity,'metrics':plan['metrics']})
                    run_id=e['id']+'-'+digest(identity)[:16]
                    slots={'seed':seed,'dataset':dataset,'run_id':run_id,**params}
                    try: command=[part.format_map(slots) for part in e['command']]
                    except (KeyError,ValueError) as exc: raise Invalid('Unresolved command placeholder: '+str(exc))
                    runs.append({**identity,'run_id':run_id,'config_hash':config_hash,'command':command,
                                 'kind':e['kind'],'source_kind':e.get('source_kind','reproduced'),
                                 'comparison_group':e['comparison_group'],'baseline':e.get('baseline'),
                                 'depends_on':e.get('depends_on',[]),'claim_ids':e['claim_ids'],
                                 'estimated_cost':e.get('estimated_cost',0),'estimated_gpu_hours':e.get('estimated_gpu_hours',0)})
    if len({r['run_id'] for r in runs})!=len(runs): raise Invalid('Duplicate matrix cells')
    provider=plan.get('provider','local')
    queue=provider=='ssh' and (len(runs)>=10 or any(r['depends_on'] for r in runs))
    matrix = {'version':1,'plan_hash':digest(plan),'provider':provider,'route':'experiment-queue' if queue else 'run-experiment',
            'max_parallel':plan.get('max_parallel',4),'metrics':plan['metrics'],'runs':runs,
            'estimated_cost':sum(r['estimated_cost'] for r in runs),'estimated_gpu_hours':sum(r['estimated_gpu_hours'] for r in runs)}
    if plan.get('interaction_contract'):
        matrix.update(interaction_contract=INTERACTION_CONTRACT, cost_unit=plan.get('cost_unit', 'not_applicable'))
    return matrix


def design_review(plan, today=None):
    validate(plan); issues=[]; today=today or dt.date.today()
    search=plan.get('baseline_search',{})
    if not search.get('queries') or not search.get('candidates'): issues.append('Baseline search queries/candidates missing')
    try:
        age=(today-dt.date.fromisoformat(search['searched_at'])).days
        if age<0 or age>plan.get('baseline_refresh_days',30): issues.append('Baseline search requires refresh')
    except (KeyError,ValueError): issues.append('Baseline search date missing/invalid')
    candidates=search.get('candidates',[])
    for c in candidates:
        for key in ('id','paper_url','decision','reason','published_at'):
            if not c.get(key): issues.append('Candidate missing '+key)
        for link in ('paper_url', 'code_url'):
            if c.get(link) and urlparse(c[link]).scheme not in {'http','https'}: issues.append('Candidate needs source URL: '+link)
        if c.get('decision') not in {'include','exclude','literature_only'}: issues.append('Unknown baseline decision')
        if c.get('decision')=='include' and not (c.get('code_url') and c.get('revision') and c.get('protocol')):
            issues.append('Included baseline needs official implementation, revision and protocol')
    included={c.get('id') for c in candidates if c.get('decision')=='include'}
    for e in plan['experiments']:
        if e['kind']=='baseline' and e.get('baseline_candidate') not in included: issues.append('Baseline run lacks selected search candidate: '+e['id'])
        if e['kind']=='ablation':
            for key in ('changes','controls','hypothesis','interpretation'):
                if not e.get(key): issues.append('Ablation '+e['id']+' missing '+key)
    ids={e['id'] for e in plan['experiments']}
    subjects=plan.get('coverage_subjects',[])
    if not subjects: issues.append('Declare claim/component/confound coverage subjects')
    for subject in subjects:
        row=next((r for r in plan.get('coverage',[]) if r.get('subject')==subject),None)
        if not row: issues.append('Uncovered subject: '+subject); continue
        if row.get('status')=='covered':
            if not row.get('experiments') or any(x not in ids for x in row['experiments']): issues.append('Invalid coverage links: '+subject)
        elif row.get('status') in {'deferred','not_applicable'}:
            if not row.get('reason'): issues.append('Coverage exception needs reason: '+subject)
        else: issues.append('Invalid coverage state: '+subject)
    return {'valid':not issues,'issues':issues,'note':'Structural checks only; freshness and scientific coverage require source-grounded researcher review.'}


def decision_request(matrix, state, paid=False, full_suite=True, max_cost=None, max_gpu_hours=None):
    """Prepare reviewable input, never an approval. Response provenance belongs to the host."""
    if matrix.get('interaction_contract') not in (None, INTERACTION_CONTRACT):
        raise Invalid('Unknown budget interaction contract')
    limits = {}
    for metric, limit, supplied, spent_key in (
        ('estimated_cost', 'max_cost', max_cost, 'spent_cost'),
        ('estimated_gpu_hours', 'max_gpu_hours', max_gpu_hours, 'spent_gpu_hours'),
    ):
        remaining = state.get('remaining_' + metric, matrix[metric])
        spent = state.get(spent_key, 0)
        if not numeric(remaining) or remaining < 0 or not numeric(spent) or spent < 0:
            raise Invalid('Invalid measured/remaining budget')
        value = spent + remaining if supplied is None else supplied
        if not numeric(value) or value < 0:
            raise Invalid('finite nonnegative ' + limit + ' required')
        limits[limit] = float(value)
    unit = matrix.get('cost_unit', 'not_applicable')
    if not isinstance(unit, str) or not unit.strip() or (limits['max_cost'] > 0 and unit == 'not_applicable'):
        raise Invalid('Declare cost_unit before requesting a nonzero cost budget')
    subject = {
        'plan_hash': matrix['plan_hash'], 'matrix_hash': digest(matrix), **limits,
        'cost_unit': unit, 'code_review': state.get('code_review', 'not_run'),
        'paid': bool(paid), 'full_suite': bool(full_suite),
        'review_unavailable_acknowledged': state.get('code_review') == 'REVIEW_UNAVAILABLE',
    }
    subject_hash = digest(subject)
    return {
        'interaction_contract': INTERACTION_CONTRACT,
        'decision_id': 'budget-' + subject_hash[:20], 'subject_hash': subject_hash,
        'subject': subject, 'status': 'awaiting_decision',
        'question': '是否批准这份冻结矩阵、资源上限，以及所列审查状态与风险？',
        'choices': ['approve', 'revise', 'cancel'], 'on_no_response': 'wait',
        'resume': 'execution/runs/approval: recheck gate and actual run state before existing run/queue',
    }


def decision_check(matrix, approval, state, paid, full_suite):
    """Check receipt consistency, not human identity or authenticity of its source reference."""
    if matrix.get('interaction_contract', INTERACTION_CONTRACT) != INTERACTION_CONTRACT:
        return 'invalid', ['unknown budget interaction contract']
    choice = approval.get('decision')
    if choice != 'approve':
        status = choice if choice in ('revise', 'cancel') else 'awaiting_decision'
        return status, ['explicit approve response required; no response keeps this gate waiting']
    if approval.get('interaction_contract') != INTERACTION_CONTRACT:
        return 'invalid', ['versioned decision receipt required']
    try:
        request = decision_request(matrix, state, paid, full_suite,
                                   approval.get('max_cost'), approval.get('max_gpu_hours'))
    except (Invalid, KeyError, TypeError) as exc:
        return 'invalid', [str(exc)]
    if (approval.get('subject_hash') != request['subject_hash'] or
            approval.get('decision_id') != request['decision_id']):
        return 'stale', ['decision subject changed; request a new response']
    if request['subject']['review_unavailable_acknowledged'] and approval.get('review_unavailable_acknowledged') is not True:
        return 'invalid', ['explicit review unavailability acknowledgement required']
    source = approval.get('response_source')
    if (not isinstance(source, dict) or source.get('kind') not in
            ('structured_input', 'chat_message', 'external_approval') or
            any(not isinstance(source.get(key), str) or not source[key].strip()
                for key in ('reference', 'response_id'))):
        return 'invalid', ['host response source reference and response_id required']
    if any(not isinstance(approval.get(key), str) or not approval[key].strip()
           for key in ('approved_by', 'approved_at')):
        return 'invalid', ['human response identity and date required']
    return 'approved', []


def gate(matrix, approval, state, paid=False, full_suite=True):
    issues=[]
    decision_status = None
    if full_suite and not state.get('sanity_passed'): issues.append('sanity not passed')
    if full_suite or paid:
        if matrix.get('interaction_contract') or approval.get('interaction_contract'):
            decision_status, decision_issues = decision_check(matrix, approval, state, paid, full_suite)
            issues.extend(decision_issues)
        if approval.get('plan_hash')!=matrix['plan_hash'] or not approval.get('approved_by') or not approval.get('approved_at'):
            issues.append('explicit approval for current plan required')
        if state.get('code_review')=='REVIEW_UNAVAILABLE' and not approval.get('review_unavailable_acknowledged'):
            issues.append('review unavailability must be acknowledged')
        if state.get('code_review') not in {'PASS','WARN','REVIEW_UNAVAILABLE'} and full_suite: issues.append('code review unresolved')
        for metric,limit in [('estimated_cost','max_cost'),('estimated_gpu_hours','max_gpu_hours')]:
            spent_key='spent_cost' if limit=='max_cost' else 'spent_gpu_hours'
            ceiling=approval.get(limit)
            if not numeric(ceiling) or ceiling<0: issues.append('finite approved '+limit+' required'); continue
            remaining=state.get('remaining_'+metric,matrix[metric])
            spent=state.get(spent_key,0)
            if not numeric(remaining) or remaining<0 or not numeric(spent) or spent<0:
                issues.append('Invalid measured/remaining budget'); continue
            if spent+remaining>ceiling: issues.append(limit+' exceeded')
    selected=state.get('experiment_id')
    if selected:
        dependencies={d for r in matrix['runs'] if r['experiment_id']==selected for d in r['depends_on']}
        for dep in dependencies:
            if state.get('experiments',{}).get(dep)!='completed': issues.append('dependency not successful: '+dep)
    result = {'allowed':not issues,'issues':issues,'launch_performed':False}
    if decision_status is not None:
        result['decision_status'] = decision_status
    return result


def numeric(v):
    return type(v) in (int,float) and math.isfinite(v)

def aggregate(matrix, records, root):
    runs={r['run_id']:r for r in matrix['runs']}; attempts={}; seen=set()
    for rec in records:
        if rec.get('run_id') not in runs: raise Invalid('Unknown run in result record')
        rid=rec['run_id']; attempt=rec.get('attempt')
        if type(attempt) is not int or attempt<1 or (rid,attempt) in seen: raise Invalid('Duplicate/invalid attempt')
        seen.add((rid,attempt))
        if rec.get('config_hash')!=runs[rid]['config_hash']: raise Invalid('Result config differs from planned run')
        if rec.get('status') not in {'completed','failed','blocked','cancelled','running'}: raise Invalid('Unknown run status')
        for field in ('command','code_revision','environment','started_at','stdout_path','stderr_path'):
            if not rec.get(field): raise Invalid('Run record missing '+field)
        if rec['command']!=runs[rid]['command']: raise Invalid('Executed command differs from frozen run')
        if rec['status']!='running' and not rec.get('ended_at'): raise Invalid('Terminal attempt requires ended_at')
        for field in ('started_at','ended_at'):
            if rec.get(field):
                try: dt.datetime.fromisoformat(rec[field])
                except ValueError: raise Invalid('Invalid run timestamp: '+field)
        if rec.get('ended_at') and dt.datetime.fromisoformat(rec['ended_at']) < dt.datetime.fromisoformat(rec['started_at']):
            raise Invalid('Run ended before start')
        for field in ('stdout_path','stderr_path'):
            if not (root/relative(root,rec[field])).is_file(): raise Invalid('Missing run log: '+field)
        attempts.setdefault(rid,[]).append(rec)
    rows=[]; groups={}
    for rid,run in runs.items():
        versions=sorted(attempts.get(rid,[]),key=lambda r:r['attempt'])
        rec=versions[-1] if versions else {'status':'missing'}
        row={**run,'status':rec['status'],'attempt':rec.get('attempt'),'audit':rec.get('audit','REVIEW_UNAVAILABLE'),'metrics':{},'issues':[]}
        if rec['status']=='completed':
            if rec.get('exit_code')!=0 or not rec.get('result_path'): raise Invalid('Completed run needs zero exit and result path')
            path=root/relative(root,rec['result_path'])
            if not path.is_file(): raise Invalid('Missing original result: '+str(path))
            if path.suffix=='.csv':
                with path.open(newline='',encoding='utf-8') as f: data=list(csv.DictReader(f))
                if len(data)!=1: raise Invalid('CSV result must contain exactly one metric row')
                values={k:float(v) for k,v in data[0].items()}
            else:
                data=read(path); values=data.get('metrics',data)
            for metric in matrix['metrics']:
                v=values.get(metric)
                if not numeric(v): row['issues'].append('Missing/non-finite metric: '+metric)
                else: row['metrics'][metric]=v
            if row['issues']: row['status']='invalid'
            row['result_path']=rec['result_path']; row['result_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        audit=row['audit']
        if audit not in {'PASS','WARN','FAIL','REVIEW_UNAVAILABLE'}: raise Invalid('Unknown audit state')
        row['evidence_status']='ineligible' if row['status']!='completed' or audit=='FAIL' else ('eligible' if audit=='PASS' else 'provisional')
        rows.append(row)
        key=(run['experiment_id'],run['dataset'],run['protocol'],run['comparison_group'],digest(run['parameters']),run['source_kind'])
        groups.setdefault(key,[]).append(row)
    summaries=[]
    for key,entries in sorted(groups.items()):
        for metric,spec in matrix['metrics'].items():
            good=[r for r in entries if r['status']=='completed' and metric in r['metrics']]
            values=[r['metrics'][metric] for r in good]
            summaries.append({'experiment_id':key[0],'dataset':key[1],'protocol':key[2],'comparison_group':key[3],
                              'parameters':entries[0]['parameters'],'source_kind':key[5],'metric':metric,**spec,
                              'planned_n':len(entries),'successful_n':len(values),'seeds':[r['seed'] for r in good],
                              'mean':statistics.mean(values) if values else None,
                              'std':statistics.stdev(values) if len(values)>1 else None,
                              'complete':len(values)==len(entries)})
    comparisons=[]
    for row in rows:
        if not row.get('baseline') or row['status']!='completed': continue
        candidates=[b for b in rows if b['experiment_id']==row['baseline'] and b['dataset']==row['dataset'] and b['protocol']==row['protocol'] and b['comparison_group']==row['comparison_group'] and b['seed']==row['seed'] and b['source_kind']==row['source_kind'] and b['status']=='completed']
        if len(candidates)!=1:
            comparisons.append({'run_id':row['run_id'],'status':'unpaired','reason':'Missing or ambiguous comparable baseline for this seed; separate comparison_group for each baseline configuration.'}); continue
        baseline=candidates[0]
        for metric,spec in matrix['metrics'].items():
            if metric not in row['metrics'] or metric not in baseline['metrics']: continue
            value=row['metrics'][metric]; base=baseline['metrics'][metric]; delta=value-base
            comparisons.append({'run_id':row['run_id'],'baseline_run_id':baseline['run_id'],'seed':row['seed'],'metric':metric,
                                'status':'paired','evidence_status':'ineligible' if 'ineligible' in {row['evidence_status'],baseline['evidence_status']} else ('provisional' if 'provisional' in {row['evidence_status'],baseline['evidence_status']} else 'eligible'),'delta':delta,'relative_change':delta/abs(base) if base else None,
                                'improvement':delta if spec['direction']=='maximize' else -delta})
    paired_groups={}
    for comparison in comparisons:
        if comparison['status']!='paired': continue
        run=runs[comparison['run_id']]
        key=(run['experiment_id'],run['baseline'],run['dataset'],run['protocol'],run['comparison_group'],digest(run['parameters']),comparison['metric'])
        paired_groups.setdefault(key,[]).append(comparison)
    paired_summary=[]
    for key,items in sorted(paired_groups.items()):
        deltas=[i['delta'] for i in items]
        paired_summary.append({'experiment_id':key[0],'baseline':key[1],'dataset':key[2],'protocol':key[3],
                               'comparison_group':key[4],'parameters':runs[items[0]['run_id']]['parameters'],'metric':key[6],
                               'paired_n':len(items),'seeds':[i['seed'] for i in items],
                               'mean_delta':statistics.mean(deltas),'std_delta':statistics.stdev(deltas) if len(deltas)>1 else None})
    return {'version':1,'plan_hash':matrix['plan_hash'],'paired_summary':paired_summary,'attempts':records,'runs':rows,'summary':summaries,'comparisons':comparisons,
            'incomplete_runs':[r['run_id'] for r in rows if r['status']!='completed'],
            'note':'No significance claim; one seed has no cross-seed standard deviation. Audit FAIL is retained but ineligible for writing.'}


def write_report(report, output):
    save(output,report)
    for key in ('summary','comparisons','paired_summary'):
        values=report[key]; keys=sorted({k for row in values for k in row})
        buf=io.StringIO(); writer=csv.DictWriter(buf,fieldnames=keys); writer.writeheader()
        for row in values: writer.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in row.items()})
        atomic(output.with_name(output.stem+'-'+key+'.csv'),buf.getvalue())


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='action',required=True)
    for name in ['expand','design-review']:
        s=sub.add_parser(name); s.add_argument('plan',type=Path); s.add_argument('--output',type=Path,required=True)
    g=sub.add_parser('gate'); g.add_argument('matrix',type=Path); g.add_argument('--approval',type=Path,required=True); g.add_argument('--state',type=Path,required=True); g.add_argument('--paid',action='store_true'); g.add_argument('--sanity-only',action='store_true')
    d=sub.add_parser('decision-request'); d.add_argument('matrix',type=Path); d.add_argument('--state',type=Path,required=True); d.add_argument('--output',type=Path,required=True); d.add_argument('--paid',action='store_true'); d.add_argument('--sanity-only',action='store_true'); d.add_argument('--max-cost',type=float); d.add_argument('--max-gpu-hours',type=float)
    s=sub.add_parser('summarize'); s.add_argument('matrix',type=Path); s.add_argument('--records',type=Path,required=True); s.add_argument('--content-root',type=Path,default=Path('.')); s.add_argument('--output',type=Path,required=True)
    a=p.parse_args(argv)
    try:
        if a.action=='expand': result=expand(read(a.plan)); save(a.output,result)
        elif a.action=='design-review': result=design_review(read(a.plan)); save(a.output,result)
        elif a.action=='decision-request':
            result=decision_request(read(a.matrix),read(a.state),a.paid,not a.sanity_only,a.max_cost,a.max_gpu_hours); save(a.output,result)
        elif a.action=='gate': result=gate(read(a.matrix),read(a.approval),read(a.state),a.paid,not a.sanity_only)
        else: result=aggregate(read(a.matrix),read(a.records),a.content_root.resolve()); write_report(result,a.output)
        print(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False))
        return 1 if result.get('valid') is False or result.get('allowed') is False or result.get('incomplete_runs') else 0
    except (Invalid,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'error':str(exc)})); return 1
    except OSError as exc:
        print(json.dumps({'error':str(exc)})); return 2

if __name__=='__main__': sys.exit(main())
