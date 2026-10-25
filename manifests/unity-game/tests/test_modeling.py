"""Optional DCC integration stays installable without activating external services."""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / 'manifests/unity-game'
PACKAGE = ROOT / 'mine/unity-game-development'


class ModelingIntegrationTests(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run([sys.executable, '-B', '-m', 'vibe_tool', *map(str, args)],
                              cwd=ROOT, capture_output=True, text=True, timeout=90,
                              env={**os.environ, 'VIBE_HOME': str(ROOT), 'PYTHONPATH': str(ROOT / 'tools/vibe_tool/src'), 'PYTHONDONTWRITEBYTECODE': '1'})

    def test_modeling_catalog_is_optional_and_assigns_source_import_and_review(self):
        catalog = json.loads((PACKAGE / 'references/skill-map.json').read_text())
        production = next(s for s in catalog['stages'] if s['id'] == 'production')
        branch = next(s for s in production['subskills'] if s['name'] == 'unity-game-modeling')
        self.assertEqual(branch['software_routes'], ['mcp', 'external-skill', 'blender-cli', 'gui'])
        self.assertEqual([n['name'] for n in branch['subskills']], [
            'unity-game-model-design', 'unity-game-model-build', 'unity-game-model-surface',
            'unity-game-model-rig-export', 'unity-game-model-review'])
        self.assertEqual(branch['subskills'][-1]['roles'], ['game-reviewer'])
        self.assertIn('model-artist', production['execution']['roles'])
        self.assertIn('unity-game-model-rig-export', catalog['role_skills']['technical-artist'])

    def test_public_init_archives_helpers_without_enabling_mcp(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'new game with spaces'
            preview = self.cli('init', 'unity-game', target, '--dry-run')
            self.assertEqual(preview.returncode, 0, preview.stderr)
            self.assertFalse(target.exists())
            installed = self.cli('init', 'unity-game', target)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            files = ('scripts/dcc_cli.py', 'templates/Blender/export_model.py',
                     'templates/Blender/README.md', 'references/external-tools.md',
                     'references/external-tools/mcp.example.json', 'templates/model-brief.md',
                     'templates/model-delivery.md', 'templates/external-tool-session.md')
            for relative in files:
                self.assertEqual((target / '.unity-game' / relative).read_bytes(), (MANIFEST / relative).read_bytes())
            for name in ('mcp.json', '.mcp.json', '.codex/config.toml', '.claude/settings.json'):
                self.assertFalse((target / name).exists(), name)
            for name in ('.claude/agents/model-artist.md', '.codex/agents/model-artist.toml'):
                self.assertEqual((target / name).read_bytes(), (MANIFEST / name).read_bytes())

    def test_force_preserves_existing_mcp_source_assets_and_user_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'existing game'
            originals = {
                'mcp.json': '{"mcpServers":{"existing":{"command":"user-tool"}}}',
                '.mcp.json': '{"custom":true}',
                'Art/source.blend': 'existing editable scene',
                'Assets/Models/robot.fbx': 'existing model',
                'Assets/Models/robot.fbx.meta': 'guid: existing-guid',
                '.agents/skills/unity-game-development/custom.md': 'custom instructions',
                '.unity-game/deliverables/model-brief.md': 'user filled brief',
                '.unity-game/state/status.md': 'actual project state',
            }
            shutil.copytree(PACKAGE, target / '.agents/skills/unity-game-development')
            for relative, text in originals.items():
                p = target / relative
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(text)
            for _ in range(2):
                result = self.cli('add', 'manifest', 'unity-game', target, '--force')
                self.assertEqual(result.returncode, 0, result.stderr)
                for relative, text in originals.items():
                    self.assertEqual((target / relative).read_text(), text)

    def test_optional_mcp_examples_are_pinned_stdio_not_installer_configuration(self):
        servers = json.loads((MANIFEST / 'references/external-tools/mcp.example.json').read_text())['mcpServers']
        self.assertEqual(set(servers), {'blender', 'unityMCP'})
        self.assertEqual(servers['blender']['args'], ['--from', 'mcp-for-blender==2.2.4', 'mcp-for-blender'])
        self.assertIn('git+https://github.com/CoplayDev/unity-mcp@v10.3.0#subdirectory=Server', servers['unityMCP']['args'])
        self.assertEqual(servers['unityMCP']['args'][-2:], ['--transport', 'stdio'])
        for server in servers.values():
            self.assertEqual(server['command'], 'uvx')
            self.assertNotIn('url', server)

    def test_installed_helper_missing_blender_records_not_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / 'game'
            result = self.cli('init', 'unity-game', target)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = target / 'Evidence/not-installed'
            run = subprocess.run([sys.executable, '-B', str(target / '.unity-game/scripts/dcc_cli.py'),
                                  'doctor', '--blender', str(target / 'missing-blender'), '--output-dir', str(output)],
                                 cwd=target, text=True, capture_output=True, timeout=30)
            self.assertEqual(run.returncode, 2, run.stderr)
            record = json.loads((output / 'result.json').read_text())
            self.assertEqual(record['status'], 'not_run')
            self.assertIn('missing_blender', record['reason'])
            self.assertFalse(list(output.glob('*.blend')))


if __name__ == '__main__':
    unittest.main()
