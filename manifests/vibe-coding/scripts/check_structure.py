#!/usr/bin/env python3
"""Offline, read-only code-structure checks and reviewable baseline/snapshot candidates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from structure_contract import ContractError, load_contract  # noqa: E402
from structure_check import analyze, check_report  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('check', 'baseline', 'snapshot'))
    parser.add_argument('--root', default='.')
    parser.add_argument('--contract', default='architecture/structure.json')
    parser.add_argument('--baseline', help='explicit, reviewed debt baseline (check only)')
    args = parser.parse_args(argv)
    try:
        root = Path(args.root).resolve()
        if not root.is_dir(): raise ContractError('Project root must be an existing directory')
        if args.baseline and args.command != 'check':
            raise ContractError('--baseline applies only to check; candidates do not silently renew debt')
        contract, sha = load_contract(root, args.contract)
        report = analyze(root, contract, sha)
        if args.command == 'check':
            output = check_report(root, contract, sha, report, args.baseline)
            status = 2 if report['blockers'] else 1 if output['status'] == 'fail' else 0
        elif report['blockers']:
            output = {'schema_version': 1, 'status': 'blocked', 'blockers': report['blockers'], 'read_only': True}
            status = 2
        elif args.command == 'baseline':
            output = {'schema_version': 1, 'contract_sha256': sha, 'findings': report['findings']}
            status = 0
        else:
            output, status = report['topology'], 0
    except (ContractError, OSError, ValueError) as exc:
        output = {'schema_version': 1, 'status': 'error', 'read_only': True, 'error': str(exc)}
        status = 2
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
