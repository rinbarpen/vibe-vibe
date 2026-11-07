#!/usr/bin/env python3
"""Read-only local Git/LFS and game-version audit; does not initialize, lock, commit, fetch or push."""
import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys

BINARY={'.blend','.fbx','.glb','.uasset','.umap','.psd','.aseprite','.wav','.flac','.png','.jpg','.ogg','.mp4'}
LOCKABLE={'.blend','.uasset','.umap','.psd','.aseprite','.fbx'}
CACHES={'Library','Temp','Obj','Intermediate','DerivedDataCache','.godot','node_modules','target','__pycache__'}
VERSION_FIELDS=('client_version','build_id','content_version','save_schema','network_protocol',
                'toolchain_revision','design_revision','source_commit')


def inspect(project,large_mb):
    if not project.is_dir():raise ValueError('project directory missing')
    records=[]
    def git(*args,stdin=None):
        command=['git',*args]
        try:
            proc=subprocess.run(command,cwd=project,input=stdin,capture_output=True,text=True,timeout=20,
                                env={**os.environ,'GIT_OPTIONAL_LOCKS':'0','GIT_TERMINAL_PROMPT':'0'})
            result={'command':command,'stdin':stdin or '', 'stdout':proc.stdout,'stderr':proc.stderr,'exit_status':proc.returncode}
        except (OSError,subprocess.TimeoutExpired) as exc:
            result={'command':command,'stdin':stdin or '', 'stdout':'','stderr':str(exc),'exit_status':None}
        records.append(result)
        return result
    head=git('rev-parse','--show-toplevel')
    if head['exit_status'] != 0:
        return {'status':'not_versioned','vcs':'git','commands':records,
                'next':'Select existing Git/LFS, Perforce, or manual snapshot policy; this command makes no repository changes.'}
    revision=git('rev-parse','HEAD'); branch=git('rev-parse','--abbrev-ref','HEAD')
    status=git('status','--porcelain=v1','-z','--','.')
    tracked=git('ls-files','-z','--','.')
    if status['exit_status'] != 0 or tracked['exit_status'] != 0:raise ValueError('git project inspection failed')
    paths=[p for p in tracked['stdout'].split('\0') if p]
    caches=sorted(p for p in paths if Path(p).parts and Path(p).parts[0] in CACHES)
    large=[];locks=[];binaries=[]
    for name in paths:
        path=project/name
        # Never follow source-tree symlinks while inspecting file sizes.
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p.is_relative_to(project)):continue
        if path.suffix.lower() in LOCKABLE:locks.append(name)
        if path.suffix.lower() in BINARY:binaries.append(name)
        if path.is_file() and path.suffix.lower() in BINARY and path.stat().st_size>large_mb*1024*1024:large.append(name)
    filters={}
    if binaries:
        attrs=git('check-attr','-z','--stdin','filter',stdin='\0'.join(binaries)+'\0')
        if attrs['exit_status'] != 0:raise ValueError('git attribute inspection failed')
        values=attrs['stdout'].split('\0')
        filters={values[i]:values[i+2] for i in range(0,len(values)-2,3)}
    lfs=git('lfs','version')
    pending=[];warnings=[]
    commit_hash=revision['stdout'].strip() if revision['exit_status']==0 else None
    if commit_hash is None:pending.append('initial commit: no verified HEAD yet')
    if caches:warnings.append('Potential generated-cache root paths are tracked; confirm engine/path policy before changing tracking. Names alone do not prove generated data.')
    uncovered=[name for name in large if filters.get(name)!='lfs']
    if uncovered:warnings.append('Large binary files lack LFS filtering; choose policy before migrating history.')
    if locks:pending.append('Record single-writer/lock policy for non-mergeable assets; tool has not acquired locks.')
    if lfs['exit_status'] != 0 and any(value=='lfs' for value in filters.values()):warnings.append('LFS filters found but local git-lfs is missing.')
    metadata=project/'.game-design/state/version.json'
    versions={}
    if metadata.is_file():
        versions=json.loads(metadata.read_text(encoding='utf-8'))
        if not isinstance(versions,dict) or type(versions.get('schema_version')) is not int or versions['schema_version']!=1:
            raise ValueError('version metadata schema_version must be 1')
        for field in VERSION_FIELDS:
            value=versions.get(field)
            if value is not None and (not isinstance(value,str) or not value.strip()):raise ValueError('version values must be non-empty strings or null')
            if value is None:pending.append('version: '+field)
        commit=versions.get('source_commit')
        if commit is not None and commit_hash is not None and commit!=commit_hash:warnings.append('Declared source_commit differs from inspected HEAD.')
    else:pending.append('game version metadata: .game-design/state/version.json')
    return {'status':'review_required' if warnings or pending else 'inspected','vcs':'git',
            'repository':head['stdout'].strip(),'project':str(project),'head':commit_hash,
            'branch':branch['stdout'].strip() if branch['exit_status']==0 else None,'working_tree_changed':bool(status['stdout']),
            'tracked_count':len(paths),'tracked_caches':caches,'large_binaries_without_lfs':uncovered,
            'single_writer_candidates':locks,'versions':versions,'warnings':warnings,'pending':pending,
            'commands':records,'note':'Read-only local policy signals, not proof of backup, LFS object availability, CI success, or release approval.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,default=Path('.'));p.add_argument('--large-mb',type=float,default=10)
    args=p.parse_args()
    if not math.isfinite(args.large_mb) or args.large_mb<=0:p.error('--large-mb must be finite and positive')
    try:
        result=inspect(args.project.resolve(),args.large_mb)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 1 if result['status']=='not_versioned' else 0
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({'status':'error','error':str(exc)},ensure_ascii=False),file=sys.stderr);return 2

if __name__=='__main__':sys.exit(main())
