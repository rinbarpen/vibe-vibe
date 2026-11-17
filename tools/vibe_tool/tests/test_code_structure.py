"""Executable local structure governance, cross-language boundaries and distribution."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from vibe_tool.discovery import resolve_manifest
from vibe_tool.manifest_update import render_manifest
from vibe_tool.setup import setup, check

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / 'manifests/vibe-coding'
SCRIPT = 'scripts/check_structure.py'
ASSETS = (SCRIPT, 'scripts/structure_contract.py', 'scripts/structure_imports.py',
          'scripts/structure_check.py', 'references/code-structure.md',
          'references/code-structure.example.json', 'references/code-structure-workflow.json',
          'references/code-structure-workflow.svg')


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '.vibe-tool/backups/' not in p.as_posix()}


class Fixture(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix='vibe structure ')
        self.addCleanup(directory.cleanup)
        self.temp = Path(directory.name).resolve()
        patch = mock.patch.dict(os.environ, {'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONUTF8': '1',
                    'PYTHONPATH': str(ROOT / 'tools/vibe_tool/src'),
                    'VIBE_PROJECTS_FILE': str(self.temp / 'projects.json')})
        patch.start(); self.addCleanup(patch.stop)
        self.root = self.temp / 'project'
        self.root.mkdir()
        self.put('docs/architecture.md', '# Module responsibilities\n')
        self.config = {'schema_version': 1, 'source_roots': ['src'],
                       'snapshot': 'architecture/structure-snapshot.json',
                       'modules': [self.module('core'), self.module('app', ['core'])]}
        self.put('src/core/api.py', 'VALUE = 1\n')
        self.put('src/core/private.py', 'SECRET = 1\n')
        self.put('src/app/main.py', 'from core.api import VALUE\n')
        self.save_config()

    def module(self, name, dependencies=()):
        return {'name': name, 'paths': ['src/' + name], 'responsibility': name + ' business responsibility',
                'allowed_dependencies': list(dependencies), 'import_prefixes': [name],
                'public_paths': ['src/' + name + '/api.py'] if name == 'core' else [], 'entrypoints': [],
                'docs': ['docs/architecture.md']}

    def put(self, path, text):
        p = self.root / path; p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8'); return p

    def save_config(self):
        self.put('architecture/structure.json', json.dumps(self.config))

    def command(self, command='check', *extra, script=None, root=None):
        return subprocess.run([sys.executable, script or MANIFEST / SCRIPT, command,
                               '--root', root or self.root, *map(str, extra)],
                              capture_output=True, text=True, timeout=90, cwd=self.temp)

    def output(self, result, status=0):
        self.assertEqual(result.returncode, status, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def snapshot(self):
        data = self.output(self.command('snapshot'))
        self.put(self.config['snapshot'], json.dumps(data))
        return data

    def baseline(self):
        data = self.output(self.command('baseline'))
        self.put('architecture/debt.json', json.dumps(data))
        return data

    def native(self, covered, edges):
        self.config['dependency_evidence'] = 'architecture/native.json'
        self.save_config()
        sources = {p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in (self.root / 'src').rglob('*') if p.is_file()}
        self.put('architecture/native.json', json.dumps({'schema_version': 1,
                 'producer': 'fixture native compiler dependency export', 'source_sha256': sources,
                 'covered_files': covered, 'edges': [{'from': a, 'to': b} for a, b in edges]}))


class StructureTests(Fixture):
    def test_clean_local_project_needs_no_git_host_or_dependencies(self):
        self.snapshot()
        before = hashes(self.root)
        data = self.output(self.command())
        self.assertEqual(data['status'], 'pass')
        self.assertTrue(data['read_only'])
        self.assertEqual(hashes(self.root), before)
        self.assertEqual(len(data['coverage']['built_in_static_files']), 3)
        self.assertEqual(data['coverage']['unparsed_files'], [])

    def test_candidates_are_stdout_only_and_drift_requires_review(self):
        before = hashes(self.root)
        self.output(self.command('baseline')); self.output(self.command('snapshot'))
        self.assertEqual(hashes(self.root), before)
        self.assertTrue(self.output(self.command(), 1)['structure_drift'])
        self.snapshot(); self.put('src/app/extra.py', 'x = 1\n')
        data = self.output(self.command(), 1)
        self.assertTrue(data['structure_drift'])
        self.assertFalse(data['new_findings'])

    def test_source_body_changes_do_not_force_topology_renewal(self):
        self.snapshot(); self.put('src/app/main.py', 'from core.api import VALUE\n\nprint(VALUE)\n')
        self.output(self.command())

    def test_forbidden_dependency_and_private_api_are_separate(self):
        self.config['modules'][1]['allowed_dependencies'] = []
        self.save_config(); self.put('src/app/main.py', 'from core.private import SECRET\n')
        self.snapshot()
        data = self.output(self.command(), 1)
        self.assertEqual({f['rule'] for f in data['new_findings']}, {'forbidden-dependency', 'private-import'})

    def test_cycle_uses_actual_imports_not_allowed_dependency_graph(self):
        self.config['modules'][0]['allowed_dependencies'] = ['app']
        self.save_config(); self.snapshot(); self.output(self.command())
        self.put('src/core/api.py', 'import app.main\n')
        self.snapshot(); data = self.output(self.command(), 1)
        self.assertIn('dependency-cycle', {f['rule'] for f in data['new_findings']})

    def test_baseline_keeps_unchanged_debt_but_changed_violation_is_new(self):
        self.config['modules'][1]['allowed_dependencies'] = []
        self.save_config(); self.snapshot(); baseline = self.baseline()
        self.assertEqual(len(baseline['findings']), 1)
        result = self.output(self.command('check', '--baseline', 'architecture/debt.json'))
        self.assertEqual(len(result['existing_debt']), 1)
        self.put('src/app/main.py', 'from core.api import VALUE\n# changed violating file\n')
        data = self.output(self.command('check', '--baseline', 'architecture/debt.json'), 1)
        self.assertEqual(len(data['new_findings']), 1)

    def test_size_baseline_allows_reduction_but_not_growth(self):
        self.config['max_lines'] = 1; self.save_config()
        self.put('src/app/main.py', 'a=1\nb=2\nc=3\n'); self.snapshot(); self.baseline()
        self.output(self.command('check', '--baseline', 'architecture/debt.json'))
        self.put('src/app/main.py', 'a=1\nb=2\n')
        self.output(self.command('check', '--baseline', 'architecture/debt.json'))
        self.put('src/app/main.py', 'a=1\nb=2\nc=3\nd=4\n')
        self.assertEqual(self.output(self.command('check', '--baseline', 'architecture/debt.json'), 1)
                         ['new_findings'][0]['value'], 4)

    def test_baseline_does_not_suppress_topology_drift_or_contract_changes(self):
        self.snapshot(); self.baseline(); self.put('src/app/new.py', 'x=1\n')
        self.assertTrue(self.output(self.command('check', '--baseline', 'architecture/debt.json'), 1)['structure_drift'])
        self.config['max_lines'] = 100; self.save_config()
        self.assertIn('hash mismatch', self.output(self.command('check', '--baseline', 'architecture/debt.json'), 2)['error'])

    def test_resolved_debt_is_reported_not_silently_recreated(self):
        self.config['max_lines'] = 1; self.save_config()
        self.put('src/app/main.py', 'a=1\nb=2\n'); self.snapshot(); self.baseline()
        self.put('src/app/main.py', 'a=1\n')
        data = self.output(self.command('check', '--baseline', 'architecture/debt.json'))
        self.assertEqual(len(data['resolved_baseline_ids']), 1)

    def test_python_relative_import_and_static_from_alias(self):
        self.put('src/app/main.py', 'from ..core.api import VALUE\n')
        self.snapshot(); self.output(self.command())
        self.put('src/app/main.py', 'from ..core import private\n')
        self.snapshot(); self.assertEqual(self.output(self.command(), 1)['new_findings'][0]['rule'], 'private-import')

    def test_cross_language_static_declarations_and_private_boundaries(self):
        cases = [
            ('typescript', 'main.ts', 'api.ts', 'private.ts', 'core',
             "import type { X } from '../core/api'; export { X } from '../core/api';", "const x = require('../core/private');"),
            ('javascript', 'main.js', 'api.js', 'private.js', '@app/core',
             "// import x from '../core/private'\nimport '../core/api.js';", "import('../core/private.js');"),
            ('go', 'main.go', 'api.go', 'private/api.go', 'example/core',
             'package app\nimport ( c "example/core" )', 'package app\nimport _ "example/core/private"'),
            ('rust', 'main.rs', 'api.rs', 'private.rs', 'crate::core',
             '// include!("private.rs");\nuse crate::core::{api::{Thing as T}}; const S: &str = "use crate::core::private::Thing;";', 'use crate::core::private::Thing;'),
            ('java', 'Main.java', 'Api.java', 'Private.java', 'org.example.core',
             'import org.example.core.Api;', 'import static org.example.core.Private.value;'),
        ]
        for language, main, api, private, prefix, good, bad in cases:
            with self.subTest(language=language):
                shutil.rmtree(self.root / 'src')
                self.put('src/app/' + main, good)
                self.put('src/core/' + api, ''); self.put('src/core/' + private, '')
                self.config['modules'][0]['import_prefixes'] = [prefix]
                self.config['modules'][0]['public_paths'] = ['src/core' if language == 'go' else 'src/core/' + api]
                self.config['modules'][1]['public_paths'] = []; self.save_config()
                self.snapshot(); self.output(self.command())
                self.put('src/app/' + main, bad); self.snapshot()
                self.assertIn('private-import', {f['rule'] for f in self.output(self.command(), 1)['new_findings']})

    def test_missing_ownership_and_unsupported_or_computed_imports_block_candidates(self):
        cases = [('src/unowned/x.py', 'x=1'), ('src/app/main.py', 'def bad('),
                 ('src/app/x.cs', 'using Core;'), ('src/app/main.ts', 'import(name);'),
                 ('src/app/main.py', 'importlib.import_module(name)')]
        for name, content in cases:
            with self.subTest(path=name, content=content):
                old = (self.root / name).read_bytes() if (self.root / name).exists() else None
                self.put(name, content)
                self.assertEqual(self.output(self.command('baseline'), 2)['status'], 'blocked')
                if old is None: (self.root / name).unlink()
                else: (self.root / name).write_bytes(old)

    def test_native_evidence_covers_other_languages_and_is_hash_bound(self):
        self.put('src/app/Other.cs', 'using Core;')
        self.native(['src/app/Other.cs'], [('src/app/Other.cs', 'src/core/private.py')])
        self.snapshot(); data = self.output(self.command(), 1)
        self.assertEqual(data['coverage']['native_evidence_files'], ['src/app/Other.cs'])
        self.assertIn('private-import', {f['rule'] for f in data['new_findings']})
        self.put('src/app/Other.cs', 'using OtherCore;')
        self.assertIn('stale/incomplete', self.output(self.command(), 2)['error'])

    def test_required_paths_missing_and_bad_contracts_fail_not_skip(self):
        self.snapshot()
        for field, value in [('schema_version', 2), ('surprise', True), ('max_lines', True),
                             ('source_roots', ['../outside'])]:
            previous = dict(self.config); self.config[field] = value; self.save_config()
            self.output(self.command(), 2)
            self.config = previous; self.save_config()
        (self.root / 'docs/architecture.md').unlink()
        self.assertEqual(self.output(self.command(), 2)['status'], 'blocked')

    def test_overlapping_modules_unknown_dependencies_and_missing_contract_are_errors(self):
        self.config['modules'][1]['paths'] = ['src/core/nested']; self.save_config()
        self.assertIn('Overlapping', self.output(self.command(), 2)['error'])
        self.config['modules'][1]['paths'] = ['src/app']; self.config['modules'][1]['allowed_dependencies'] = ['unknown']
        self.save_config(); self.output(self.command(), 2)
        (self.root / 'architecture/structure.json').unlink(); self.output(self.command(), 2)

    @unittest.skipIf(os.name == 'nt', 'symlink creation may need Windows privileges')
    def test_symlinks_are_rejected_and_external_files_not_read(self):
        outside = self.temp / 'outside.py'; outside.write_text('secret=1\n')
        (self.root / 'src/app/link.py').symlink_to(outside)
        self.assertIn('Symlink', self.output(self.command(), 2)['error'])

    def test_cache_exclusion_does_not_hide_rust_src_bin(self):
        self.put('src/app/__pycache__/ignored.py', 'def bad(')
        self.put('src/app/bin/tool.rs', 'fn main() {}')
        self.snapshot(); data = self.output(self.command())
        self.assertIn('src/app/bin/tool.rs', data['inventory'])
        self.assertNotIn('src/app/__pycache__/ignored.py', data['inventory'])

    def test_root_source_scope_and_file_module_do_not_force_src_layout(self):
        shutil.rmtree(self.root / 'src')
        self.put('main.py', 'print(1)\n')
        module = self.module('root'); module.update(paths=['main.py'], public_paths=['main.py'], import_prefixes=[])
        self.config.update(source_roots=['.'], modules=[module]); self.save_config()
        self.snapshot(); self.output(self.command())


    def test_unmapped_alias_blocks_until_local_or_external_prefix_is_explicit(self):
        self.put('src/app/main.ts', "import { X } from '@app/core/api';")
        self.output(self.command('snapshot'), 2)
        self.config['modules'][0]['import_prefixes'].append('@app/core'); self.save_config()
        self.snapshot(); self.output(self.command())
        self.put('src/app/main.ts', "import React from 'react';")
        self.output(self.command(), 2)
        self.config['external_prefixes'] = ['react']; self.save_config()
        self.snapshot(); self.output(self.command())

    def test_bad_baseline_and_native_edge_types_are_controlled_errors(self):
        self.snapshot(); self.baseline()
        self.put('architecture/debt.json', '{"schema_version":1,"findings":false}')
        self.output(self.command('check', '--baseline', 'architecture/debt.json'), 2)
        self.native(['src/app/main.py'], [])
        p = self.root / 'architecture/native.json'; data = json.loads(p.read_text())
        data['edges'] = [{'from': [], 'to': 'src/core/api.py'}]
        p.write_text(json.dumps(data))
        result = self.command(); self.output(result, 2)
        self.assertNotIn('Traceback', result.stderr)

    def test_entrypoint_and_public_api_moves_cannot_be_baselined_away(self):
        self.config['modules'][1]['entrypoints'] = ['src/app/main.py']; self.save_config()
        self.snapshot(); self.baseline()
        (self.root / 'src/app/main.py').rename(self.root / 'src/app/moved.py')
        self.output(self.command('check', '--baseline', 'architecture/debt.json'), 2)



class DeliveryTests(Fixture):
    def sources(self):
        repo = self.temp / 'sources'
        path = repo / 'manifests/vibe-coding'
        path.parent.mkdir(parents=True)
        shutil.copytree(MANIFEST, path, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        (path / 'skills.txt').write_text('# Unrelated skill dependencies omitted in offline fixture.\n')
        (repo / 'skills').mkdir(); (repo / 'mine').mkdir()
        return repo

    def install(self, source):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(setup(source, 'vibe-coding', self.root, agent='generic', provider='git'), 0)

    def render(self, root, *extra):
        return subprocess.run([sys.executable, root / 'scripts/render_codegraph_workflow.py',
                               '--source', root / 'references/code-structure-workflow.json',
                               '--output', root / 'references/code-structure-workflow.svg', *extra],
                              text=True, capture_output=True, timeout=45)

    def test_portable_install_has_complete_runtime_and_preserves_project_state(self):
        self.snapshot(); self.baseline(); self.put('README.md', '# Existing business project\n')
        state = hashes(self.root / 'architecture')
        source = self.sources(); self.install(source)
        self.assertEqual(hashes(self.root / 'architecture'), state)
        for name in ASSETS:
            if not name.endswith('.md'):
                self.assertEqual((self.root / name).read_bytes(), (MANIFEST / name).read_bytes())
        command = self.root / 'rules/vibe-coding/commands/structure-check/COMMAND.md'
        self.assertTrue(command.is_file())
        self.assertTrue((self.root / 'rules/vibe-coding/rules/vibe-coding-structure.md').is_file())
        self.output(self.command(script=self.root / SCRIPT))
        self.output(self.command(script=self.root / 'rules/vibe-coding' / SCRIPT))
        self.assertEqual(self.render(self.root, '--check').returncode, 0)
        self.assertEqual((self.root / 'README.md').read_text(), '# Existing business project\n')
        with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(check(self.root), 0)

    def test_portable_refresh_and_standalone_restore_preserve_contract_debt_snapshot(self):
        source = self.sources(); self.snapshot(); self.baseline(); self.install(source)
        state = hashes(self.root / 'architecture'); before = hashes(self.root)
        script = source / 'manifests/vibe-coding/scripts/structure_check.py'
        script.write_text(script.read_text() + '\n# refreshed fixture\n')
        self.install(source)
        self.assertEqual(hashes(self.root / 'architecture'), state)
        self.assertEqual((self.root / 'scripts/structure_check.py').read_bytes(), script.read_bytes())
        restore = sorted((self.root / '.vibe-tool/backups').glob('*/restore.py'))[-1]
        r = subprocess.run([sys.executable, restore], capture_output=True, text=True, timeout=45)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(hashes(self.root), before)
        self.output(self.command(script=self.root / SCRIPT))

    @unittest.skipIf(os.name == 'nt', 'legacy shell installer is optional; native portable path tested on Windows')
    def test_legacy_init_add_update_ship_runtime_without_owning_architecture_data(self):
        source = self.sources(); self.snapshot(); self.baseline()
        state = hashes(self.root / 'architecture')
        env = dict(os.environ, VIBE_HOME=str(source))
        for operation in ('init', 'add'):
            def cli(*args):
                return subprocess.run([sys.executable, '-m', 'vibe_tool', *args], cwd=source,
                                      env=env, capture_output=True, text=True, timeout=90)
            args = [operation, 'vibe-coding'] if operation == 'init' else ['add', 'manifest', 'vibe-coding']
            r = cli(*args, str(self.root), '--provider=git')
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            for name in ASSETS: self.assertEqual((self.root / name).read_bytes(), (MANIFEST / name).read_bytes())
            self.output(self.command(script=self.root / SCRIPT))
            before = hashes(self.root)
            script = self.root / 'scripts/structure_check.py'; script.write_text('# old installed tool\n')
            r = cli('update', 'manifest', 'vibe-coding', str(self.root))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(script.read_bytes(), (MANIFEST / 'scripts/structure_check.py').read_bytes())
            self.assertEqual(hashes(self.root / 'architecture'), state)
            restore = sorted((self.root / '.vibe-tool/backups').glob('*/restore.py'))[-1]
            r = subprocess.run([sys.executable, restore], capture_output=True, text=True, timeout=45)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(script.read_text(), '# old installed tool\n')
            script.write_bytes((MANIFEST / 'scripts/structure_check.py').read_bytes())
            self.assertEqual(hashes(self.root), before)
        stage = self.temp / 'rendered'
        paths = render_manifest(resolve_manifest(source / 'manifests', 'vibe-coding'),
                                stage, self.root, {'provider': 'git'})
        self.assertTrue(set(map(Path, ASSETS)) <= set(paths))
        self.assertFalse(any(str(p).startswith('architecture/') for p in paths))

    def test_diagram_generation_and_missing_changed_inputs_are_read_only(self):
        self.assertEqual(self.render(MANIFEST, '--check').returncode, 0)
        source = self.sources() / 'manifests/vibe-coding'
        before = hashes(source)
        self.assertEqual(self.render(source).returncode, 0)
        self.assertEqual(hashes(source), before)
        (source / 'references/code-structure-workflow.svg').unlink()
        before = hashes(source)
        self.assertEqual(self.render(source, '--check').returncode, 1)
        self.assertEqual(hashes(source), before)
        self.assertEqual(self.render(source).returncode, 0)
        data = json.loads((source / 'references/code-structure-workflow.json').read_text())
        data['nodes'][0]['detail'] += ' changed'
        (source / 'references/code-structure-workflow.json').write_text(json.dumps(data))
        before = hashes(source)
        self.assertEqual(self.render(source, '--check').returncode, 1)
        self.assertEqual(hashes(source), before)

    def test_cli_does_not_write_import_caches_without_environment_flag(self):
        source = self.sources() / 'manifests/vibe-coding'
        self.snapshot(); before = hashes(source)
        env = dict(os.environ); env.pop('PYTHONDONTWRITEBYTECODE', None)
        r = subprocess.run([sys.executable, source / SCRIPT, 'check', '--root', self.root],
                           env=env, capture_output=True, text=True, timeout=45)
        self.output(r)
        self.assertEqual(hashes(source), before)

    @unittest.skipIf(os.name == 'nt', 'quality helper is POSIX; direct Python checker is cross-platform')
    def test_quality_helper_propagates_structure_failure(self):
        self.snapshot(); source = self.sources() / 'manifests/vibe-coding'
        (self.root / 'scripts').mkdir()
        for name in ASSETS[:4]: shutil.copy2(source / name, self.root / name)
        command = ['bash', source / 'scripts/vibe-quality-gate.sh']
        r = subprocess.run(command, cwd=self.root, capture_output=True, text=True, timeout=45)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.put('src/app/new.py', 'x=1\n')
        r = subprocess.run(command, cwd=self.root, capture_output=True, text=True, timeout=45)
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn('"structure_drift": true', r.stdout)
        (self.root / 'architecture/structure.json').unlink()
        r = subprocess.run(command, cwd=self.root, capture_output=True, text=True, timeout=45)
        self.assertIn('not configured', r.stdout)
