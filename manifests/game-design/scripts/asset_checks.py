#!/usr/bin/env python3
"""Read-only asset provenance/file checks; not a DCC, aesthetic, or engine-import test."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            value.update(chunk)
    return value.hexdigest()


def local(root, value):
    if not isinstance(value,str) or not value or '\\' in value:
        raise ValueError('asset/evidence path must be a non-empty project-relative path')
    rel = Path(value)
    if rel.is_absolute() or '..' in rel.parts:
        raise ValueError('asset/evidence path escapes project')
    path = root
    for part in rel.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError('symlink asset/evidence path: '+value)
    return path


def inspect(root, manifest):
    if not root.is_dir():
        raise ValueError('project directory missing')
    data = json.loads(manifest.read_text(encoding='utf-8'))
    if not isinstance(data,dict) or type(data.get('schema_version')) is not int or data['schema_version'] != 1:
        raise ValueError('asset manifest schema_version must be 1')
    if not isinstance(data.get('assets'),list) or not data['assets']:
        raise ValueError('asset manifest requires a non-empty assets list')
    seen, files, errors, pending = set(), [], [], []
    for entry in data['assets']:
        if not isinstance(entry,dict) or not isinstance(entry.get('id'),str) or not entry['id'].strip() or entry['id'] in seen:
            raise ValueError('asset IDs must be unique non-empty strings')
        seen.add(entry['id'])
        if not isinstance(entry.get('exports'),list) or not entry['exports']:
            raise ValueError('each asset needs at least one declared export')
        outputs = [{'path':entry.get('source'),'sha256':entry.get('source_sha256'),'role':'source'}]
        source_path = local(root, entry.get('source'))
        exports = set()
        for export in entry['exports']:
            if not isinstance(export,dict):raise ValueError('export must be an object')
            path = local(root,export.get('path'))
            if path == source_path or path in exports:
                raise ValueError('source and unique exports must be separate paths')
            exports.add(path)
            outputs.append({**export,'role':'export'})
        for record in outputs:
            path = local(root, record['path'])
            sha = record.get('sha256')
            if sha is not None and (not isinstance(sha,str) or not re.fullmatch('[0-9a-f]{64}',sha)):
                raise ValueError('sha256 must be a lowercase digest or null')
            if not path.is_file() or path.stat().st_size == 0:
                errors.append(f'{entry["id"]}: missing/empty {record["role"]}: {record["path"]}')
                continue
            actual = digest(path)
            files.append({'asset':entry['id'],'path':record['path'],'role':record['role'],'sha256':actual})
            if sha is None:pending.append(f'{entry["id"]}: record digest for {record["path"]}')
            elif actual != sha:errors.append(f'{entry["id"]}: digest mismatch: {record["path"]}')
        if not isinstance(entry.get('license'),str) or not entry['license'].strip():
            pending.append(entry['id']+': license/provenance')
        for gate in ('engine_import','review'):
            review = entry.get(gate)
            if not isinstance(review,dict) or review.get('status') not in ('not_run','pass','fail','not_applicable'):
                raise ValueError(gate+' requires status not_run/pass/fail/not_applicable')
            evidence = review.get('evidence',[])
            if not isinstance(evidence,list):raise ValueError('evidence must be a list')
            if review['status'] == 'not_run':pending.append(entry['id']+': '+gate)
            if review['status'] == 'fail':errors.append(entry['id']+': '+gate+' recorded fail')
            if review['status'] == 'not_applicable' and not review.get('reason'):
                raise ValueError('not_applicable requires a reason')
            if review['status'] == 'pass' and not evidence:
                errors.append(entry['id']+': '+gate+' pass missing evidence')
            for ref in evidence:
                path = local(root, ref)
                if not path.is_file() or path.stat().st_size == 0:
                    errors.append(entry['id']+': missing review evidence: '+str(ref))
    return {'status':'failed' if errors else 'pending' if pending else 'files_verified',
            'assets':len(seen),'files':files,'errors':errors,'pending':pending,
            'runtime_validation':'not_run','note':'Only bytes/provenance/evidence references checked; recorded review is not re-executed or approved here.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,default=Path('.'))
    p.add_argument('--manifest',type=Path,required=True)
    args=p.parse_args()
    try:
        root=args.project.resolve()
        manifest=args.manifest if args.manifest.is_absolute() else root/args.manifest
        result=inspect(root,manifest)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if result['status']=='files_verified' else 1
    except (OSError,ValueError,TypeError,KeyError) as exc:
        print(json.dumps({'status':'error','error':str(exc)},ensure_ascii=False),file=sys.stderr)
        return 2

if __name__=='__main__':sys.exit(main())
