"""Evaluate module ownership, boundaries, cycles, size budgets and topology drift."""
from __future__ import annotations

import json

from structure_contract import (ContractError, collect, digest, fields, load_json,
                                owner, strings, under, within)
from structure_imports import references, resolve


def finding(rule, path, detail, fingerprint='', value=1):
    identity = digest(json.dumps([rule, path, detail], ensure_ascii=False).encode())
    return {'id': identity, 'rule': rule, 'path': path, 'detail': detail,
            'fingerprint': fingerprint, 'value': value}


def native_evidence(root, contract, files):
    if 'dependency_evidence' not in contract:
        return set(), []
    data = load_json(within(root, contract['dependency_evidence']))
    fields(data, {'schema_version', 'producer', 'source_sha256', 'covered_files', 'edges'},
           {'schema_version', 'producer', 'source_sha256', 'covered_files', 'edges'}, 'dependency evidence')
    if type(data['schema_version']) is not int or data['schema_version'] != 1 or not isinstance(data['producer'], str) or not data['producer'].strip():
        raise ContractError('Native dependency evidence needs schema_version 1 and a producer command/description')
    expected = {p: f['sha256'] for p, f in files.items()}
    if data['source_sha256'] != expected:
        raise ContractError('Native dependency evidence source hashes are stale/incomplete; regenerate with actual native tools')
    covered = set(strings(data['covered_files'], 'covered_files', False))
    if covered - set(files):
        raise ContractError('Native evidence covers files outside current source inventory')
    if not isinstance(data['edges'], list):
        raise ContractError('Native evidence edges must be a list')
    edges = []
    for edge in data['edges']:
        fields(edge, {'from', 'to'}, {'from', 'to'}, 'native edge')
        source, target = edge['from'], edge['to']
        if not isinstance(source, str) or source not in covered:
            raise ContractError('Native edge source must be in covered_files')
        if not within(root, target).exists() or owner(target, contract) is None:
            raise ContractError(f'Native edge target must exist in a managed module: {target}')
        edges.append((source, target))
    return covered, edges


def components(graph):
    """Small module graphs; iterative reachability avoids recursion limits."""
    reach = {}
    for start in graph:
        seen, pending = set(), [start]
        while pending:
            node = pending.pop()
            if node in seen: continue
            seen.add(node); pending.extend(graph[node] - seen)
        reach[start] = seen
    remaining, result = set(graph), []
    while remaining:
        first = min(remaining)
        group = {n for n in remaining if n in reach[first] and first in reach[n]}
        remaining -= group
        if len(group) > 1: result.append(sorted(group))
    return result


def analyze(root, contract, contract_sha):
    files, skipped = collect(root, contract)
    findings, blockers, imported, parsed = [], [], [], []
    for module in contract['modules']:
        for field in ('paths', 'entrypoints', 'public_paths', 'docs'):
            for name in module[field]:
                p = within(root, name)
                if not p.exists()  or (field == 'docs' and not p.is_file()):
                    blockers.append(f"{module['name']}: missing/invalid {field} path {name}")
    covered, native = native_evidence(root, contract, files)
    for path, meta in files.items():
        module = owner(path, contract)
        if module is None:
            blockers.append(f'Unowned source file requires a module declaration: {path}')
            continue
        limit = module.get('max_lines', contract.get('max_lines'))
        if limit is not None and meta['lines'] > limit:
            findings.append(finding('max-lines', path, f'Module {module["name"]}; limit {limit}', value=meta['lines']))
        if path in covered:
            continue
        try:
            refs = references(path, meta['text'])
            for kind, spec in refs:
                target = resolve(root, path, kind, spec, contract)
                if target is not None:
                    imported.append((path, target))
            parsed.append(path)
        except ContractError as exc:
            blockers.append(str(exc))
    imported += native
    edges = sorted(set(imported))
    graph = {m['name']: set() for m in contract['modules']}
    for source, target in edges:
        a, b = owner(source, contract), owner(target, contract)
        if a is None:
            blockers.append(f'Unowned dependency source: {source}'); continue
        if b is None:
            blockers.append(f'Unowned local dependency target: {source} -> {target}'); continue
        if a['name'] == b['name']: continue
        graph[a['name']].add(b['name'])
        fingerprint = files[source]['sha256']
        if b['name'] not in a['allowed_dependencies']:
            findings.append(finding('forbidden-dependency', source,
                                    f'{a["name"]} -> {b["name"]}: {target}', fingerprint))
        if not any(target == public or (within(root, target).is_file() and under(target, public))
                   for public in b['public_paths']):
            findings.append(finding('private-import', source,
                                    f'{b["name"]} private path: {target}', fingerprint))
    for group in components(graph):
        cycle_edges = sorted((a, b) for a in group for b in graph[a] if b in group)
        contexts = {p: f['sha256'] for p, f in files.items()
                    if owner(p, contract) and owner(p, contract)['name'] in group}
        findings.append(finding('dependency-cycle', ','.join(group),
                                json.dumps(cycle_edges), digest(json.dumps(contexts, sort_keys=True).encode())))
    # File membership, public/entrypoint declarations and actual direct edges are
    # the reviewable structural surface. Source-body edits alone do not drift it.
    topology = {'schema_version': 1, 'contract_sha256': contract_sha,
                'files': {p: owner(p, contract)['name'] if owner(p, contract) else None for p in files},
                'edges': [{'from': a, 'to': b} for a, b in edges],
                'modules': {m['name']: {k: m[k] for k in ('paths', 'public_paths', 'entrypoints', 'docs')}
                            for m in contract['modules']}}
    unique = {f['id']: f for f in findings}
    return {'findings': sorted(unique.values(), key=lambda f: (f['rule'], f['path'], f['detail'])),
            'blockers': sorted(set(blockers)), 'topology': topology,
            'inventory': {p: {'sha256': f['sha256'], 'lines': f['lines']} for p, f in files.items()},
            'coverage': {'built_in_static_files': sorted(parsed), 'unparsed_files': sorted(set(files) - covered - set(parsed)), 'native_evidence_files': sorted(covered),
                         'excluded_directories_or_files': skipped,
                         'limits': 'Static declaration subset only; external packages, runtime/reflection/macros and architectural intent require native tools/tests and AI review. No code is executed.'}}


def apply_baseline(root, name, report, contract_sha):
    baseline = load_json(within(root, name))
    fields(baseline, {'schema_version', 'contract_sha256', 'findings'},
           {'schema_version', 'contract_sha256', 'findings'}, 'baseline')
    if type(baseline['schema_version']) is not int or baseline['schema_version'] != 1 or baseline['contract_sha256'] != contract_sha:
        raise ContractError('Baseline schema/contract hash mismatch; review contract changes before renewing debt')
    if not isinstance(baseline['findings'], list):
        raise ContractError('Baseline findings must be a list')
    previous = {}
    for entry in baseline['findings']:
        fields(entry, {'id', 'rule', 'path', 'detail', 'fingerprint', 'value'},
               {'id', 'rule', 'path', 'detail', 'fingerprint', 'value'}, 'baseline finding')
        if (not all(isinstance(entry[k], str) for k in ('id', 'rule', 'path', 'detail', 'fingerprint'))
                or type(entry['value']) is not int or entry['value'] < 1 or entry['id'] in previous):
            raise ContractError('Malformed or duplicate baseline finding')
        expected = finding(entry['rule'], entry['path'], entry['detail'])['id']
        if entry['id'] != expected:
            raise ContractError('Baseline finding identity mismatch')
        previous[entry['id']] = entry
    known, new = [], []
    for item in report['findings']:
        old = previous.get(item['id'])
        accepted = (old is not None and item['value'] <= old['value']
                    and item['fingerprint'] == old['fingerprint'])
        (known if accepted else new).append(item)
    return known, new, sorted(set(previous) - {f['id'] for f in report['findings']})


def check_report(root, contract, sha, report, baseline=None):
    known, new, stale = [], report['findings'], []
    if baseline:
        known, new, stale = apply_baseline(root, baseline, report, sha)
    snapshot_path = within(root, contract['snapshot'])
    drift = True
    if snapshot_path.exists():
        saved = load_json(snapshot_path)
        fields(saved, {'schema_version', 'contract_sha256', 'files', 'edges', 'modules'},
               {'schema_version', 'contract_sha256', 'files', 'edges', 'modules'}, 'snapshot')
        if type(saved['schema_version']) is not int or saved['schema_version'] != 1:
            raise ContractError('Unsupported snapshot schema_version')
        drift = saved != report['topology']
    return {'schema_version': 1, 'command': 'check', 'read_only': True, 'contract_sha256': sha,
            'status': 'blocked' if report['blockers'] else 'fail' if new or drift else 'pass',
            'new_findings': new, 'existing_debt': known, 'resolved_baseline_ids': stale,
            'structure_drift': drift, 'snapshot': contract['snapshot'],
            'blockers': report['blockers'], 'coverage': report['coverage'],
            'inventory': report['inventory'], 'topology': report['topology']}
