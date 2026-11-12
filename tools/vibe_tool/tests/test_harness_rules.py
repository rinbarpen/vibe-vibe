"""No editor runtime required: portable contracts, scope fidelity and lifecycle tests."""
import contextlib
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
from urllib.parse import urlsplit

from vibe_tool.discovery import discover_manifests, resolve_manifest
from vibe_tool.harness_rules import compile_bundle
from vibe_tool.portable import render
from vibe_tool.project_sync import update_project
from vibe_tool.setup import check, setup

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / 'tools/vibe_tool/src'


class HarnessRulesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='neutral harness 项目 ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'source'
        self.manifest = self.repo / 'manifests/plain'
        self.write(self.manifest / 'AGENTS.md', '# Business contract\nKeep the original evaluation gate.\n[Guide](references/guide.md)\n')
        self.write(self.manifest / 'rules/core.md', '---\nalways: true\npaths: ["src/**"]\nwhen: project entry\n---\n# Core rule\nDo not change the scientific gate.\n[Guide](../references/guide.md)\n')
        self.write(self.manifest / 'rules/tests.mdc', '---\ndescription: tests only\nglobs: ["tests/**/*.py"]\nalwaysApply: false\n---\n# Conditional rule\nRun the selected tests.\n')
        self.write(self.manifest / 'references/guide.md', '# Guide\n')
        self.write(self.repo / 'skills/example/SKILL.md', '# Example\n')
        self.write(self.manifest / 'skills.txt', 'example\n')
        (self.repo / 'mine').mkdir()
        self.target = self.root / 'target'
        self.env = patch.dict(os.environ, VIBE_PROJECTS_FILE=str(self.root/'registry.json'), PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')
        self.env.start(); self.addCleanup(self.env.stop)

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text, encoding='utf-8'); return path

    def install(self, harness='generic'):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(setup(self.repo, 'plain', self.target, agent=harness), 0)

    def test_discovery_has_no_claude_or_cursor_prerequisite(self):
        self.assertEqual(resolve_manifest(self.repo/'manifests','plain').name, 'plain')
        self.assertFalse((self.manifest/'CLAUDE.md').exists())
        self.assertFalse((self.manifest/'.cursor').exists())
        self.install()
        self.assertFalse((self.target/'.cursor').exists())
        self.assertFalse((self.target/'.cursorrules').exists())
        self.assertFalse(list(self.target.rglob('*.mdc')))
        self.assertIn('PROJECT_RULES.md', json.loads((self.target/'.vibe-setup.json').read_text())['files'])
        self.assertIn('rules/plain/INDEX.md', (self.target/'AGENTS.md').read_text())

    def test_generic_reader_follows_real_plain_files_and_scopes(self):
        self.install()
        index = self.target/'rules/plain/INDEX.md'
        metadata = json.loads((index.parent/'rules.json').read_text())
        entries = {r['file']:r for r in metadata['rules']}
        self.assertIs(entries['rules/core.md']['always'], True)
        self.assertEqual(entries['rules/core.md']['paths_expression'], '["src/**"]')
        self.assertIs(entries['rules/tests.md']['always'], False)
        self.assertEqual(entries['rules/tests.md']['paths_expression'], '["tests/**/*.py"]')
        self.assertEqual(entries['rules/tests.md']['when'], 'tests only')
        for rule in entries.values():
            file = index.parent/rule['file']; self.assertTrue(file.is_file())
            self.assertFalse(file.read_text().startswith('---'))
            self.assertIn('Applicability:', file.read_text())
            self.assertIn('source', rule)
        self.assertIn('original evaluation gate', (index.parent/'CONTRACT.md').read_text())
        self.assertIn('Do not change the scientific gate.', (index.parent/'rules/core.md').read_text())
        for file in (self.target/'PROJECT_RULES.md', index, index.parent/'CONTRACT.md', index.parent/'rules/core.md'):
            for value in re.findall(r'\]\(([^)]+)\)', file.read_text()):
                parts = urlsplit(value)
                if not parts.scheme and parts.path:
                    self.assertTrue((file.parent/parts.path).resolve().is_file(), (file,value))

    def test_canonical_rule_links_and_support_indexes_rebase_once(self):
        self.write(self.manifest/'AGENTS.md', '# Contract\n[Core](rules/core.md)\n[Guide index](references/INDEX.md)\n')
        self.write(self.manifest/'references/INDEX.md', '# Guide index\n[Guide](guide.md)\n')
        self.install()
        bundle=self.target/'rules/plain'
        for file in (self.target/'AGENTS.vibe-plain.md', bundle/'CONTRACT.md', bundle/'references/INDEX.md'):
            for link in re.findall(r'\]\(([^)]+)\)',file.read_text()):
                self.assertTrue((file.parent/link).is_file(),(file,link))
                self.assertNotIn('rules/plain/rules/plain',link)

    def test_project_rules_only_contract_refreshes_all_selected_host_entries(self):
        (self.manifest/'AGENTS.md').unlink()
        self.write(self.manifest/'PROJECT_RULES.md','# Plain contract v1\n')
        self.install('both')
        self.write(self.manifest/'PROJECT_RULES.md','# Plain contract v2\n')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(update_project(self.repo,self.target),0);check(self.target)
        self.assertIn('v2',(self.target/'rules/plain/CONTRACT.md').read_text())
        for host in ('AGENTS','CLAUDE'):
            self.assertIn('rules/plain/INDEX.md',(self.target/(host+'.md')).read_text())
            self.assertIn('rules/plain/CONTRACT.md',(self.target/(host+'.vibe-plain.md')).read_text())

    def test_old_editor_tracking_retires_without_deleting_files_and_restore_is_exact(self):
        self.install()
        old=self.write(self.target/'.cursor/rules/tests.mdc','User-kept legacy body\n')
        state=json.loads((self.target/'.vibe-setup.json').read_text())
        state['files']['.cursor/rules/tests.mdc']={'owner':'plain','sha256':hashlib.sha256(old.read_bytes()).hexdigest()}
        (self.target/'.vibe-setup.json').write_text(json.dumps(state))
        def snapshot():
            return {p.relative_to(self.target).as_posix():p.read_bytes() for p in self.target.rglob('*')
                    if p.is_file() and '.vibe-tool/backups/' not in p.relative_to(self.target).as_posix()}
        before=snapshot()
        self.write(self.manifest/'rules/tests.mdc','---\nalwaysApply: false\nglobs: "tests/**"\n---\nChanged source\n')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(update_project(self.repo,self.target),0);check(self.target)
        self.assertEqual(old.read_text(),'User-kept legacy body\n')
        self.assertNotIn('.cursor/rules/tests.mdc',json.loads((self.target/'.vibe-setup.json').read_text())['files'])
        backups=sorted((self.target/'.vibe-tool/backups').iterdir())
        result=subprocess.run([sys.executable,'-B',str(backups[-1]/'restore.py')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(snapshot(),before)

    def test_plain_markdown_overrides_same_name_legacy_source(self):
        self.write(self.manifest/'rules/core.mdc', '---\nalwaysApply: false\n---\nOld client-only input\n')
        self.install()
        content=(self.target/'rules/plain/rules/core.md').read_text()
        self.assertIn('Do not change the scientific gate.',content)
        self.assertNotIn('Old client-only input',content)

    def test_scope_raw_multiline_unknown_and_nested_rule_preserved(self):
        raw='description: |\n  nested task\nglobs:\n  - "src/**"\n  - "lib/**"\nalwaysApply: unexpected'
        self.write(self.manifest/'rules/nested/extra.mdc','---\n'+raw+'\n---\nNested rule body\n')
        self.install()
        bundle=self.target/'rules/plain';rows=json.loads((bundle/'rules.json').read_text())['rules']
        row=next(r for r in rows if r['file']=='rules/nested/extra.md')
        self.assertIsNone(row['always']);self.assertEqual(row['frontmatter_raw'],raw)
        self.assertIn('manual scope review',(bundle/row['file']).read_text())
        file=bundle/row['file'];link=re.search(r'\[rule index\]\(([^)]+)\)',file.read_text())[1]
        self.assertEqual((file.parent/link).resolve(),(bundle/'INDEX.md').resolve())

    def test_named_host_entries_remain_optional_and_refer_to_same_rules(self):
        for host in ('codex','claude','both'):
            with self.subTest(host=host):
                self.target=self.root/host;self.install(host)
                self.assertFalse((self.target/'.cursor').exists())
                for entry in ('AGENTS.md','CLAUDE.md'):
                    if (self.target/entry).exists():
                        self.assertIn('rules/plain/INDEX.md',(self.target/entry).read_text())
                self.assertIn('Business contract',(self.target/'rules/plain/CONTRACT.md').read_text())

    def test_project_rules_only_manifest_can_be_used_by_any_named_mode(self):
        (self.manifest/'AGENTS.md').unlink()
        self.write(self.manifest/'PROJECT_RULES.md','# Standalone ordinary Markdown contract\n')
        self.install('both')
        self.assertTrue((self.target/'AGENTS.md').is_file());self.assertTrue((self.target/'CLAUDE.md').is_file())
        self.assertIn('Standalone ordinary Markdown contract',(self.target/'rules/plain/CONTRACT.md').read_text())

    def test_selected_scenario_rules_not_all_scenarios(self):
        for scenario in ('selected','other'):
            self.write(self.manifest/f'scenarios/{scenario}/rules/{scenario}.md','---\nalways: false\nwhen: '+scenario+'\n---\n'+scenario+' condition\n')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(setup(self.repo,'plain',self.target,agent='generic',scenario='selected'),0)
        self.assertTrue((self.target/'rules/plain/rules/selected.md').exists())
        self.assertFalse((self.target/'rules/plain/rules/other.md').exists())

    def test_update_keeps_user_entry_text_and_independent_rules(self):
        self.install()
        self.write(self.target/'rules/user-owned.md','User policy\n')
        (self.target/'PROJECT_RULES.md').write_text((self.target/'PROJECT_RULES.md').read_text()+'\nUser context\n')
        self.write(self.manifest/'rules/core.md','---\nalways: true\n---\nChanged rule v2\n')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(update_project(self.repo,self.target),0);check(self.target)
        self.assertIn('User context',(self.target/'PROJECT_RULES.md').read_text())
        self.assertEqual((self.target/'rules/user-owned.md').read_text(),'User policy\n')
        self.assertIn('Changed rule v2',(self.target/'rules/plain/rules/core.md').read_text())

    def test_multiple_manifest_indexes_merge_once_and_refresh_together(self):
        self.install()
        other=self.repo/'manifests/other'
        self.write(other/'AGENTS.md','# Other business gate\n');self.write(other/'rules/other.md','Other rule\n')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(setup(self.repo,'other',self.target,agent='generic'),0)
            self.assertEqual(update_project(self.repo,self.target),0);check(self.target)
        text=(self.target/'PROJECT_RULES.md').read_text()
        self.assertEqual(text.count('<!-- vibe:rules:plain:begin -->'),1)
        self.assertEqual(text.count('<!-- vibe:rules:other:begin -->'),1)

    def test_local_neutral_rule_edit_blocks_update_before_writes(self):
        self.install();rule=self.target/'rules/plain/rules/core.md';rule.write_text('User rule edit\n')
        before={p.relative_to(self.target).as_posix():p.read_bytes() for p in self.target.rglob('*') if p.is_file()}
        with self.assertRaisesRegex(ValueError,'Local edit'):
            update_project(self.repo,self.target)
        self.assertEqual({p.relative_to(self.target).as_posix():p.read_bytes() for p in self.target.rglob('*') if p.is_file()},before)

    def test_historical_init_unchanged_and_setup_adds_portable_entry(self):
        from vibe_tool.manifest import init_manifest
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(init_manifest(self.repo/'manifests','plain',self.target),0)
        old=(self.target/'.cursor/rules/tests.mdc').read_bytes()
        self.assertFalse((self.target/'PROJECT_RULES.md').exists())
        self.install()
        self.assertEqual((self.target/'.cursor/rules/tests.mdc').read_bytes(),old)
        self.assertTrue((self.target/'PROJECT_RULES.md').is_file())
        self.assertTrue((self.target/'rules/plain/rules/tests.md').is_file())


class RealManifestRulesTests(unittest.TestCase):
    def test_every_manifest_and_scenario_has_neutral_rules_with_original_scope(self):
        for manifest in discover_manifests(ROOT/'manifests'):
            for scenario in ('', *manifest.scenarios):
                with self.subTest(manifest=manifest.name,scenario=scenario),tempfile.TemporaryDirectory() as directory:
                    stage=Path(directory)/'stage'
                    render(manifest,stage,Path(directory)/'project',{'provider':'git','scenario':scenario})
                    self.assertFalse((stage/'.cursor').exists())
                    self.assertFalse((stage/'.cursorrules').exists())
                    self.assertTrue((stage/'PROJECT_RULES.md').is_file())
                    bundle=stage/'rules'/manifest.name
                    rows=json.loads((bundle/'rules.json').read_text(encoding='utf-8'))['rules']
                    for row in rows:
                        self.assertTrue((bundle/row['file']).is_file())
                        self.assertNotIn('.mdc',row['file'])
                        if not row['source'].startswith('generated/') and row['source']!='.cursorrules':
                            source=manifest.path/row['source']
                            self.assertEqual(row['source_sha256'],hashlib.sha256(source.read_bytes()).hexdigest())
                            self.assertIn('always',row);self.assertIn('frontmatter_raw',row)


if __name__=='__main__':
    unittest.main()
