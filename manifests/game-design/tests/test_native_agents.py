"""Native role distribution and user-file preservation, not vendor-discovery tests."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HOME=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True;sys.path.insert(0,str(HOME/'scripts'))
import install_manifest
import render_agents


def snapshot(root):return {str(p.relative_to(root)):p.read_bytes() for p in root.rglob('*') if p.is_file() and not p.is_symlink()}

class NativeAgentTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='native-agent-install-');self.addCleanup(self.temp.cleanup)
        self.project=Path(self.temp.name)/'project';self.project.mkdir()
    def install(self,force=False):
        with contextlib.redirect_stdout(io.StringIO()):install_manifest.install(self.project,force)
    def run_cli(self,*argv):return subprocess.run([sys.executable,*map(str,argv)],text=True,capture_output=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
    def test_source_role_formats_match(self):
        data=render_agents.load_roles();self.assertEqual(len(data['roles']),12)
        try:import tomllib
        except ImportError:self.skipTest('native TOML parser is stdlib on Python 3.11+')
        for role in data['roles']:
            cid=role['id'];md=(HOME/'.claude/agents'/f'{cid}.md').read_text()
            body=md.split('---\n',2)[2].strip()
            codex=tomllib.loads((HOME/'.codex/agents'/f'{cid}.toml').read_text())
            self.assertEqual(body,codex['developer_instructions'].strip())
            self.assertNotIn('model',codex)
    def test_installed_native_roots_and_readonly_renderer(self):
        self.install()
        self.assertEqual(len(list((self.project/'.claude/agents').glob('game-design-*.md'))),12)
        self.assertEqual(len(list((self.project/'.codex/agents').glob('game-design-*.toml'))),12)
        before=snapshot(self.project)
        result=self.run_cli(self.project/'.game-design/scripts/render_agents.py','--check')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(before,snapshot(self.project))
        self.assertFalse((self.project/'.game-design/.codex').exists())
    def test_user_native_role_and_config_preserved_even_force(self):
        target=self.project/'.codex/agents/game-design-designer.toml';target.parent.mkdir(parents=True)
        target.write_text('name = "my custom designer"\n');config=self.project/'.codex/config.toml';config.write_text('# user configuration\n')
        self.install(True)
        self.assertEqual(target.read_text(),'name = "my custom designer"\n')
        self.assertEqual(config.read_text(),'# user configuration\n')
        ledger=json.loads((self.project/'.game-design/install.json').read_text())
        self.assertNotIn('.codex/agents/game-design-designer.toml',ledger['files'])
    def test_managed_role_rollback_preserves_live_scheduler_state(self):
        self.install();role=self.project/'.claude/agents/game-design-qa.md';role.write_text('# customized managed QA\n')
        state=self.project/'.game-design/state/parallel.json';state.write_text('{"live fixture": true}\n')
        self.install(True)
        self.assertNotEqual(role.read_text(),'# customized managed QA\n')
        backups=sorted((self.project/'.game-design/backups').iterdir())
        last=max(backups,key=lambda p:p.stat().st_mtime_ns)
        result=self.run_cli(last/'restore.py');self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(role.read_text(),'# customized managed QA\n')
        self.assertEqual(state.read_text(),'{"live fixture": true}\n')
    def test_symlink_native_directory_rejected_before_any_payload(self):
        outside=Path(self.temp.name)/'outside';outside.mkdir()
        (self.project/'.claude').symlink_to(outside,target_is_directory=True)
        with self.assertRaises(ValueError),contextlib.redirect_stdout(io.StringIO()):install_manifest.install(self.project)
        self.assertFalse((self.project/'CLAUDE.md').exists())
        self.assertEqual(snapshot(outside),{})

if __name__=='__main__':unittest.main()
