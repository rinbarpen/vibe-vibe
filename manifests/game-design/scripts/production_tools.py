#!/usr/bin/env python3
"""Query game genres and fine-grained work packages; validate/render catalog documentation."""
import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile

HOME=Path(__file__).resolve().parents[1]
IDENTIFIER=re.compile(r'[A-Za-z][A-Za-z0-9_-]*\Z')

def text(value,label):
    if not isinstance(value,str) or not value.strip():raise ValueError(label+' requires non-empty text')

def strings(value,label,empty=False):
    if not isinstance(value,list) or (not value and not empty):raise ValueError(label+' requires a list')
    for entry in value:text(entry,label)

def identifier(value,label,seen):
    text(value,label)
    if not IDENTIFIER.fullmatch(value) or value in seen:raise ValueError(label+' invalid/duplicate ID: '+value)
    seen.add(value)

def load_data():
    genres=json.loads((HOME/'references/genres.json').read_text(encoding='utf-8'))
    production=json.loads((HOME/'references/production.json').read_text(encoding='utf-8'))
    for data,key in ((genres,'genres'),(production,'areas')):
        if (not isinstance(data,dict) or type(data.get('schema_version')) is not int or data['schema_version']!=1
                or not isinstance(data.get(key),list) or not data[key]):raise ValueError('invalid '+key+' catalog')
    ids=set()
    for genre in genres['genres']:
        identifier(genre.get('id'),'genre',ids);text(genre.get('name'),'genre name')
        for field in ('loop','systems','deliverables','acceptance','risks'):strings(genre.get(field),field)
    areas=set();tasks={}
    for area in production['areas']:
        identifier(area.get('id'),'area',areas);text(area.get('name'),'area name')
        if not isinstance(area.get('tasks'),list) or not area['tasks']:raise ValueError('area tasks required')
        for task in area['tasks']:
            tid=task.get('id');identifier(tid,'task',set(tasks));tasks[tid]=task
            for field in ('name','owner','applicability'):text(task.get(field),field)
            for field in ('inputs','actions','outputs','acceptance','rollback'):strings(task.get(field),field)
            strings(task.get('depends_on'),'depends_on',True)
            if len(set(task['depends_on']))!=len(task['depends_on']):raise ValueError('duplicate dependency')
    indegree={tid:0 for tid in tasks};children={tid:[] for tid in tasks}
    for tid,task in tasks.items():
        for dependency in task['depends_on']:
            if dependency not in tasks or dependency==tid:raise ValueError('unknown/self task dependency: '+tid+' -> '+dependency)
            indegree[tid]+=1;children[dependency].append(tid)
    ready=sorted(tid for tid in tasks if not indegree[tid]);order=[]
    while ready:
        tid=ready.pop(0);order.append(tid)
        for child in children[tid]:
            indegree[child]-=1
            if indegree[child]==0:ready.append(child);ready.sort()
    if len(order)!=len(tasks):raise ValueError('task dependency cycle')
    return genres,production,order

def render(genres,production,check=False):
    # One fact source; task and genre details remain queryable without loading the whole manual.
    g=['# 可组合游戏类型档案','',
       '> 从 [genres.json](genres.json) 生成。类型档案表示设计/验收覆盖，运行时仍需实际证据。','',
       '将 1–3 个类型作为体验组合，而不是强制单选。2D/2.5D/3D、平台、输入、联网、商业模式与内容生产方式分别记录；例如“3D 在线合作生存＋建造＋肉鸽”是多轴配置，不是新引擎。',
       '', '混合类型先确定主循环与支柱，再合并系统/数值/输入/存档/联网约束，冲突交设计审查，不机械叠加清单。每个专项需求连接 REQ-ID、工作包和测试证据。','',
       '填写 [类型画像模板](../templates/genre-profile.md)。实现排期仍遵循 [阶段契约](lifecycle.md)。','',
       '| ID | 类型 | 核心循环 |','|---|---|---|']
    for item in genres['genres']:g.append(f'| `{item["id"]}` | {item["name"]} | {"；".join(item["loop"])} |')
    for item in genres['genres']:
        g += ['',f'## {item["id"]} — {item["name"]}','']
        for key,label in [('loop','核心循环'),('systems','细系统'),('deliverables','设计产物'),('acceptance','可观察验收'),('risks','风险')]:
            g += [f'### {label}','']+['- '+v for v in item[key]]+['']
    p=['# 游戏制作粗细工作包','',
       '> 从 [production.json](production.json) 生成。每包定义输入、执行、产物、验收、依赖及返工；状态由项目证据记录。','',
       '生命周期回答“现在处于哪一阶段”；专业工作包回答“由谁、具体做什么、怎么验收”。任务依赖是生产 DAG，验证失败的返工不是新的 DAG 依赖。',
       '', '按项目挑选适用工作包；不适用需给理由与依赖影响。design-only 可完成规格/计划，实际建模、导出、工程实现、设备测试、发布仍待 implementation 或相应明确要求。缺软件/设备记 not_run；缺决定等待人；技术问题由 AI 先实验。',
       '', '角色表示职责；作者自检与独立审查分别记录。共享场景/模型单写者，版本/资产恢复点沿 [版本管理](version-management.md) 与 [建模流程](modeling.md)；工作包使用 [模板](../templates/work-package.md)。','',
       '| 领域 ID | 粗环节 | 细工作包数量 |','|---|---|---|']
    for area in production['areas']:p.append(f'| `{area["id"]}` | {area["name"]} | {len(area["tasks"])} |')
    for area in production['areas']:
        p += ['',f'## {area["id"]} — {area["name"]}','']
        for task in area['tasks']:
            p += [f'### {task["id"]} — {task["name"]}','',f'职责：{task["owner"]}',f'适用：{task["applicability"]}',f'依赖：{", ".join(task["depends_on"]) or "无前置工作包"}','']
            for key,label in [('inputs','输入'),('actions','执行'),('outputs','产物'),('acceptance','验收'),('rollback','返工/回退')]:
                p += [f'**{label}**']+['- '+v for v in task[key]]+['']
    expected={HOME/'references/genres.md':'\n'.join(g)+'\n',HOME/'references/production.md':'\n'.join(p)+'\n'}
    drift=[]
    for path,content in expected.items():
        if not path.is_file() or path.read_bytes()!=content.encode():
            drift.append(str(path.relative_to(HOME)))
            if not check:
                path.parent.mkdir(parents=True,exist_ok=True)
                fd,temp=tempfile.mkstemp(dir=path.parent,prefix='.'+path.name)
                try:
                    with os.fdopen(fd,'w',encoding='utf-8') as out:out.write(content)
                    os.replace(temp,path)
                finally:
                    if os.path.exists(temp):os.unlink(temp)
    return {'status':'drift' if check and drift else 'ok','changed':drift}

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    for name in ('genres','areas','check-production'):sub.add_parser(name)
    p=sub.add_parser('genre');p.add_argument('--id',required=True)
    p=sub.add_parser('work');group=p.add_mutually_exclusive_group(required=True);group.add_argument('--id');group.add_argument('--area')
    p=sub.add_parser('render-production');p.add_argument('--check',action='store_true')
    args=parser.parse_args()
    try:
        genres,production,order=load_data();rc=0
        if args.command=='genres':result=[{'id':g['id'],'name':g['name']} for g in genres['genres']]
        elif args.command=='areas':result=[{'id':a['id'],'name':a['name'],'tasks':len(a['tasks'])} for a in production['areas']]
        elif args.command=='genre':
            result=next((g for g in genres['genres'] if g['id']==args.id),None)
            if result is None:raise ValueError('unknown genre: '+args.id)
        elif args.command=='work':
            result=next((a for a in production['areas'] if a['id']==args.area),None) if args.area else next((t for a in production['areas'] for t in a['tasks'] if t['id']==args.id),None)
            if result is None:raise ValueError('unknown area/task')
        elif args.command=='render-production':result=render(genres,production,args.check);rc=int(result['status']=='drift')
        else:result={'status':'ok','genres':len(genres['genres']),'areas':len(production['areas']),'tasks':len(order),'topological_order':order}
        print(json.dumps(result,ensure_ascii=False,indent=2));return rc
    except (OSError,ValueError,TypeError,KeyError,AttributeError) as exc:
        print(json.dumps({'status':'error','error':str(exc)},ensure_ascii=False),file=sys.stderr);return 2

if __name__=='__main__':sys.exit(main())
