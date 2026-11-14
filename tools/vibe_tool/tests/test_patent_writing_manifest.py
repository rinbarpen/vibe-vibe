"""Writing/patent: real-source, offline setup and installed workflow contracts."""
from __future__ import annotations

import contextlib
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

from vibe_tool.discovery import resolve_manifest, resolve_skill
from vibe_tool.project_sync import update_project
from vibe_tool.setup import check, setup

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / 'manifests/writing'


def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and '.vibe-tool/backups/' not in p.as_posix()}


def links_resolve(test, document):
    text = re.sub(r'```[^\n]*\n.*?```', '', document.read_text(encoding='utf-8'), flags=re.S)
    for href in re.findall(r'\]\(([^)]+)\)', text):
        part = urlsplit(href)
        if part.scheme or part.netloc or not part.path:
            continue
        test.assertTrue((document.parent / unquote(part.path)).exists(), f'{document}: {href}')


class PatentWritingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='patent 写作 tests ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'source repo'
        shutil.copytree(MANIFEST, self.repo / 'manifests/writing')
        (self.repo / 'skills').mkdir()
        for name in ('chinese-patent', 'omnidraw'):
            shutil.copytree(ROOT / 'mine' / name, self.repo / 'mine' / name,
                            ignore=shutil.ignore_patterns('__pycache__', '.git', '*.pyc'))
        self.target = self.root / 'business 专利 project'
        self.registry = self.root / 'registry/projects.json'
        env = patch.dict(os.environ, {'VIBE_PROJECTS_FILE': str(self.registry), 'PYTHONDONTWRITEBYTECODE': '1'})
        env.start(); self.addCleanup(env.stop)

    def install(self, **kwargs):
        with contextlib.redirect_stdout(io.StringIO()):
            return setup(self.repo, 'writing', self.target,
                         agent=kwargs.pop('agent', 'generic'),
                         scenario=kwargs.pop('scenario', 'patent'), **kwargs)

    def render(self, base=None, *flags):
        base = base or self.target
        return subprocess.run([sys.executable, str(base / 'scripts/render_patent_workflow.py'),
                               '--source', str(base / 'references/patent-workflow.json'),
                               '--output', str(base / 'references/patent-workflow.svg'), *flags],
                              capture_output=True, text=True)

    def backups(self):
        return sorted((self.target / '.vibe-tool/backups').iterdir())

    def test_discovery_dependencies_and_shared_host_contract(self):
        manifest = resolve_manifest(ROOT / 'manifests', 'writing')
        self.assertEqual(manifest.scenarios, ['patent'])
        self.assertEqual(manifest.required_skills, ['chinese-patent', 'omnidraw'])
        for name in manifest.required_skills:
            self.assertEqual(resolve_skill((ROOT / 'skills', ROOT / 'mine'), name).name, name)
        self.assertEqual((MANIFEST / 'AGENTS.md').read_bytes(), (MANIFEST / 'CLAUDE.md').read_bytes())
        with (MANIFEST / 'templates/claim-support.csv').open(encoding='utf-8') as source:
            self.assertEqual(len(next(csv.reader(source))), 10)

    def test_source_and_installed_links_workflow_and_scenario(self):
        for p in MANIFEST.rglob('*.md'):
            links_resolve(self, p)
        self.assertEqual(self.install(), 0)
        for relative in ('README.md', 'AGENTS.vibe-writing.md', 'rules/writing/CONTRACT.md',
                         'rules/writing/INDEX.md', 'rules/writing/rules/patent.md',
                         'references/patent-guide.md'):
            links_resolve(self, self.target / relative)
        metadata = json.loads((self.target / 'rules/writing/rules.json').read_text())
        self.assertEqual(len(metadata['rules']), 1)
        rule = metadata['rules'][0]
        self.assertEqual(rule['source'], 'scenarios/patent/rules/patent.md')
        self.assertIs(rule['always'], True)
        self.assertFalse((self.target / '.cursor').exists())
        self.assertFalse((self.target / 'MANIFEST.md').exists())  # Business state is created at task start.
        for base in (self.target, self.target / 'rules/writing'):
            before = snapshot(base)
            result = self.render(base, '--check')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(snapshot(base), before)
            result = self.render(base)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(snapshot(base), before)
        ET.parse(self.target / 'references/patent-workflow.svg')

    def test_workflow_routes_fact_wait_scope_rework_and_rollback(self):
        data = json.loads((MANIFEST / 'references/patent-workflow.json').read_text())
        nodes = {n['id']: n for n in data['nodes']}
        for name in ('facts', 'scope', 'handback'):
            self.assertEqual(nodes[name]['kind'], 'human')
            self.assertTrue(nodes[name]['trigger'])
            self.assertTrue(nodes[name]['resume'])
            self.assertIn('waiting-', nodes[name]['detail'])
        edges = {(e['from'], e['to']): e for e in data['edges']}
        for pair in (('facts', 'intake'), ('scope', 'plan'), ('review', 'draft'),
                     ('review', 'figures'), ('review', 'plan'), ('rollback', 'review')):
            self.assertEqual(edges[pair]['kind'], 'rework')
        svg = ET.parse(MANIFEST / 'references/patent-workflow.svg')
        paths = svg.findall('.//{http://www.w3.org/2000/svg}path')
        arrow = next(p for p in paths if p.attrib.get('data-from') == 'intake'
                     and p.attrib.get('data-to') == 'facts')
        self.assertTrue(arrow.attrib['d'].endswith('H 860'))  # Enters facing edge, not behind card.

    def test_complete_skill_bundles_and_both_host_copies(self):
        self.assertEqual(self.install(agent='both'), 0)
        relatives = ('SKILL.md', 'chinese-patent-plan/SKILL.md', 'chinese-patent-drawer/SKILL.md',
                     'chinese-patent-writer/SKILL.md', 'chinese-patent-review/SKILL.md',
                     'drawio/SKILL.md', 'rules/review-checklist.md',
                     'templates/patent_spec_template.html', 'scripts/html_to_docx.py')
        for host in ('.agents', '.claude'):
            package = self.target / host / 'skills/chinese-patent'
            for relative in relatives:
                self.assertEqual((package / relative).read_bytes(),
                                 (ROOT / 'mine/chinese-patent' / relative).read_bytes())
            self.assertTrue((self.target / host / 'skills/omnidraw/SKILL.md').is_file())
            self.assertFalse(any(p.is_symlink() for p in (self.target / host / 'skills').rglob('*')))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check(self.target), 0)
        state = json.loads((self.target / '.vibe-setup.json').read_text())
        self.assertEqual(state['manifests']['writing']['options']['scenario'], 'patent')

    def test_dry_run_new_and_existing_targets_are_read_only(self):
        self.assertEqual(self.install(dry_run=True), 0)
        self.assertFalse(self.target.exists())
        self.assertFalse(self.registry.exists())
        self.target.mkdir()
        (self.target / 'AGENTS.md').write_text('Existing instructions\n')
        before = snapshot(self.root)
        self.assertEqual(self.install(dry_run=True), 0)
        self.assertEqual(snapshot(self.root), before)

    def test_existing_content_ledger_and_noop_are_preserved(self):
        self.target.mkdir()
        originals = {'AGENTS.md': 'Existing project constraints\n', 'README.md': 'User README',
                     'MANIFEST.md': 'User output ledger', 'drafts/说明书.html': 'User draft'}
        for name, text in originals.items():
            p = self.target / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
        self.assertEqual(self.install(), 0)
        for name in originals.keys() - {'AGENTS.md'}:
            self.assertEqual((self.target / name).read_text(), originals[name])
        self.assertTrue((self.target / 'AGENTS.md').read_text().startswith(originals['AGENTS.md']))
        before, backups = snapshot(self.target), self.backups()
        self.assertEqual(self.install(), 0)
        self.assertEqual(snapshot(self.target), before)
        self.assertEqual(self.backups(), backups)
        self.assertEqual((self.target / 'AGENTS.md').read_text().count('<!-- vibe:setup:writing:begin -->'), 1)

    def test_missing_dependency_and_unknown_scenario_write_nothing(self):
        with self.assertRaisesRegex(ValueError, 'Unknown or repeated scenario'):
            self.install(scenario='patnet')
        shutil.rmtree(self.repo / 'mine/chinese-patent')
        with self.assertRaises(ValueError):
            self.install()
        self.assertFalse(self.target.exists())

    def test_no_selected_scenario_does_not_enable_patent_rules(self):
        self.assertEqual(self.install(scenario=''), 0)
        rules = json.loads((self.target / 'rules/writing/rules.json').read_text())
        self.assertEqual(rules['rules'], [])
        self.assertFalse((self.target / 'rules/writing/rules/patent.md').exists())

    def test_user_edits_are_preserved_before_any_write(self):
        self.assertEqual(self.install(), 0)
        p = self.target / 'references/patent-guide.md'
        p.write_text('User customization\n')
        before = snapshot(self.target)
        with self.assertRaisesRegex(ValueError, 'Changed or missing'):
            check(self.target)
        with self.assertRaisesRegex(ValueError, 'Preserved local conflicts'):
            self.install()
        self.assertEqual(snapshot(self.target), before)

    def test_workflow_missing_drift_and_invalid_reference_fail_read_only(self):
        self.assertEqual(self.install(), 0)
        source = self.target / 'references/patent-workflow.json'
        svg = source.with_suffix('.svg')
        svg.unlink()
        before = snapshot(self.target)
        self.assertEqual(self.render(None, '--check').returncode, 1)
        self.assertEqual(snapshot(self.target), before)
        self.assertEqual(self.render().returncode, 0)
        data = json.loads(source.read_text()); data['title'] += ' changed'
        source.write_text(json.dumps(data))
        before = snapshot(self.target)
        self.assertEqual(self.render(None, '--check').returncode, 1)
        self.assertEqual(snapshot(self.target), before)
        data['edges'][0]['to'] = 'missing_node'
        source.write_text(json.dumps(data))
        before = snapshot(self.target)
        result = self.render(None, '--check')
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('unknown node', result.stderr)
        self.assertEqual(snapshot(self.target), before)

    def test_project_refresh_and_standalone_rollback_preserve_business_data(self):
        self.assertEqual(self.install(agent='both'), 0)
        ledger = self.target / 'MANIFEST.md'; ledger.write_text('Live business ledger\n')
        draft = self.target / 'drafts/v1/说明书.html'
        draft.parent.mkdir(parents=True); draft.write_text('Live draft\n')
        before = snapshot(self.target)
        p = self.repo / 'manifests/writing/references/patent-guide.md'
        p.write_text(p.read_text() + '\nUpdated source guidance.\n')
        backups = set(self.backups())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(update_project(self.repo, self.target, dry_run=True), 0)
        self.assertEqual(snapshot(self.target), before)
        self.assertEqual(set(self.backups()), backups)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(update_project(self.repo, self.target), 0)
            self.assertEqual(check(self.target), 0)
        for relative in ('references/patent-guide.md', 'rules/writing/references/patent-guide.md'):
            self.assertTrue((self.target / relative).read_text().endswith('Updated source guidance.\n'))
        self.assertEqual(ledger.read_text(), 'Live business ledger\n')
        self.assertEqual(draft.read_text(), 'Live draft\n')
        backup, = set(self.backups()) - backups
        result = subprocess.run([sys.executable, str(backup / 'restore.py')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(self.target), before)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check(self.target), 0)

    def test_initial_install_rollback_restores_existing_project(self):
        self.target.mkdir()
        (self.target / 'AGENTS.md').write_text('Original rules\n')
        (self.target / '交底.txt').write_text('Original disclosure\n')
        before = snapshot(self.target)
        self.assertEqual(self.install(), 0)
        backup, = self.backups()
        result = subprocess.run([sys.executable, str(backup / 'restore.py')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(snapshot(self.target), before)


if __name__ == '__main__':
    unittest.main()
