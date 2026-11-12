#!/usr/bin/env python3
"""Validate delivery records and hashes, not artistic merit or native file semantics."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys


PROFILES = {'portfolio', 'product', 'realtime', 'animation', 'print', 'cad'}
ROLES = {'source', 'exchange', 'preview', 'qa_report', 'review_record',
         'roundtrip_record', 'texture', 'cache', 'script', 'other'}
REQUIRED = {'source', 'exchange', 'preview', 'qa_report', 'review_record', 'roundtrip_record'}
EVIDENCE_ROLES = {'technical_review': 'qa_report', 'visual_review': 'review_record',
                  'roundtrip': 'roundtrip_record'}


def sha256(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def validate(data, root, stage='final'):
    """Return explicit errors/warnings; never modify input records or asset files."""
    errors, warnings = [], []
    if not isinstance(data, dict):
        return ['manifest must be an object'], warnings
    if type(data.get('schema_version')) is not int or data['schema_version'] != 1:
        errors.append('schema_version must be integer 1')
    if not isinstance(data.get('asset_name'), str) or not data['asset_name'].strip():
        errors.append('asset_name must be nonempty')
    if not isinstance(data.get('profile'), str) or data['profile'] not in PROFILES:
        errors.append('profile is not supported')
    software = data.get('software')
    if not isinstance(software, list):
        errors.append('software must be a list')
    elif stage == 'final' and (not software or any(
            not isinstance(s, dict) or any(not isinstance(s.get(k), str) or not s[k].strip()
                                          for k in ('name', 'version')) for s in software)):
        errors.append('final delivery requires software names and actual versions')
    files = data.get('files')
    if not isinstance(files, list):
        errors.append('files must be a list')
        files = []
    by_path, roles = {}, set()
    root = Path(root).resolve()
    for index, item in enumerate(files):
        label = f'files[{index}]'
        if not isinstance(item, dict):
            errors.append(f'{label} must be an object')
            continue
        relative, role, checksum = item.get('path'), item.get('role'), item.get('sha256')
        if not isinstance(relative, str) or not relative.strip():
            errors.append(f'{label}.path must be nonempty')
            continue
        if not isinstance(role, str) or role not in ROLES:
            errors.append(f'{label}.role is invalid')
            continue
        if relative in by_path:
            errors.append(f'duplicate path: {relative}')
            continue
        by_path[relative] = item
        roles.add(role)
        path = Path(relative)
        if path.is_absolute() or '..' in path.parts:
            errors.append(f'path must stay relative to delivery root: {relative}')
            continue
        resolved = (root / path).resolve()
        if not resolved.is_relative_to(root):
            errors.append(f'path resolves outside delivery root: {relative}')
            continue
        if not resolved.is_file() or resolved.stat().st_size == 0:
            errors.append(f'missing or empty file: {relative}')
            continue
        if not isinstance(checksum, str) or not re.fullmatch(r'[a-fA-F0-9]{64}', checksum):
            errors.append(f'missing or invalid sha256: {relative}')
        elif sha256(resolved) != checksum.lower():
            errors.append(f'sha256 mismatch: {relative}')
        if role == 'qa_report':
            try:
                audit = json.loads(resolved.read_text(encoding='utf-8'))
            except (ValueError, UnicodeError):
                audit = None  # Other applications may use text/PDF reports.
            if isinstance(audit, dict) and audit.get('kind') == 'blender-mesh-audit':
                if audit.get('status') != 'pass' or audit.get('source_unchanged') is not True:
                    errors.append(f'Blender audit is failed or source changed: {relative}')
                source_hashes = {s.get('sha256', '').lower() for s in files
                                 if isinstance(s, dict) and s.get('role') == 'source'
                                 and isinstance(s.get('sha256'), str)}
                if (not isinstance(audit.get('source_sha256'), str)
                        or audit['source_sha256'] not in source_hashes):
                    errors.append(f'Blender audit does not bind a delivered source hash: {relative}')
    if stage == 'final':
        for role in sorted(REQUIRED - roles):
            errors.append(f'missing required file role: {role}')
    for field, evidence_role in EVIDENCE_ROLES.items():
        review = data.get(field)
        if not isinstance(review, dict):
            errors.append(f'{field} must be an object')
            continue
        status = review.get('status')
        if status not in ('pending', 'accepted', 'revise'):
            errors.append(f'{field}.status must be pending, accepted or revise')
        evidence = review.get('evidence')
        if not isinstance(evidence, list) or any(not isinstance(v, str) for v in evidence):
            errors.append(f'{field}.evidence must be a list of paths')
            evidence = []
        for path in evidence:
            if path not in by_path or by_path[path]['role'] != evidence_role:
                errors.append(f'{field} evidence is not a listed {evidence_role}: {path}')
        if stage == 'final' and (status != 'accepted' or not evidence):
            errors.append(f'{field} needs accepted status and recorded evidence')
        elif status != 'accepted':
            warnings.append(f'{field} remains {status}')
    visual = data.get('visual_review', {})
    issues = visual.get('issues') if isinstance(visual, dict) else None
    if not isinstance(issues, list):
        errors.append('visual_review.issues must be a list')
    else:
        for index, issue in enumerate(issues):
            if (not isinstance(issue, dict) or issue.get('severity') not in ('critical', 'major', 'minor')
                    or issue.get('status') not in ('open', 'closed', 'accepted')):
                errors.append(f'visual_review.issues[{index}] has invalid severity or status')
            elif (stage == 'final' and issue['severity'] in ('critical', 'major')
                  and issue['status'] != 'closed'):
                errors.append(f'unclosed {issue["severity"]} issue: {issue.get("id", index)}')
    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--root', type=Path, help='Defaults to manifest parent')
    parser.add_argument('--stage', choices=('draft', 'final'), default='final')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if args.report and args.report.resolve() == args.manifest.resolve():
        parser.error('report must differ from manifest')
    try:
        data = json.loads(args.manifest.read_text(encoding='utf-8'))
        errors, warnings = validate(data, args.root or args.manifest.parent, args.stage)
    except (OSError, ValueError) as exc:
        errors, warnings = [f'manifest read failed: {exc}'], []
    result = {'schema_version': 1, 'kind': 'delivery-record-check',
              'stage': args.stage, 'status': 'fail' if errors else 'pass',
              'errors': errors, 'warnings': warnings,
              'limits': 'Checks recorded evidence and files; does not certify art or native file validity.'}
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    print(rendered, end='')
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.report.with_suffix(args.report.suffix + '.tmp')
        temporary.write_text(rendered, encoding='utf-8')
        os.replace(temporary, args.report)
    return 2 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
