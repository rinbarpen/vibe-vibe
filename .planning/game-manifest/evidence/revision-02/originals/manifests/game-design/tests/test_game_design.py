"""Contract/fixture tests; deliberately not engine-runtime acceptance tests."""
import copy
import contextlib
import hashlib
import importlib.util
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
import xml.etree.ElementTree as ET

HOME = Path(__file__).resolve().parents[1]
ROOT = HOME.parents[1]
SCRIPTS = HOME / 'scripts'
sys.dont_write_bytecode = True
sys.path.insert(0, str(SCRIPTS))
from game_design import load_catalog, detect, render_adapters, check_project
import game_design
import install_manifest
from restore_install import restore


def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file() and not p.is_symlink()}


class GameDesignTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='game design test ')
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.project = self.base / 'project with spaces'
        self.project.mkdir()
        self.catalog = load_catalog()

    def write(self, name, value):
        path = self.project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding='utf-8')
        return path

    def cli(self, *args, cwd=None):
        env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1',
               'PYTHONPATH': str(ROOT / 'tools/vibe_tool/src'), 'VIBE_HOME': str(ROOT)}
        return subprocess.run([sys.executable, *map(str, args)], cwd=cwd or ROOT,
                              env=env, text=True, capture_output=True)

    def install(self, *flags):
        p = self.cli(SCRIPTS / 'install_manifest.py', self.project, *flags)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        return p

    def test_catalog_and_generated_guides(self):
        self.assertEqual(len(self.catalog['engines']), 23)
        self.assertEqual(render_adapters(self.catalog, True)['status'], 'ok')
        self.assertEqual((HOME / 'CLAUDE.md').read_bytes(), (HOME / 'AGENTS.md').read_bytes())
        for engine in self.catalog['engines']:
            self.assertEqual(engine['runtime_validation'], 'not_run')

    def test_renderer_is_canonical_copy(self):
        self.assertEqual((SCRIPTS / 'render_workflow.py').read_bytes(),
                         (ROOT / 'scripts/render-manifest-workflow.py').read_bytes())

    def test_unrecognized_and_read_only(self):
        for name, content in [('package.json', '{}'), ('Cargo.toml', '[package]\nname="x"'),
                              ('project.json', '{}'), ('game.json', '{"properties":{}}')]:
            self.write(name, content)
        before = snapshot(self.project)
        self.assertEqual(detect(self.project, self.catalog)['status'], 'unrecognized')
        self.assertEqual(snapshot(self.project), before)

    def test_ambiguous_does_not_choose(self):
        self.write('project.godot', 'config_version=5')
        self.write('sample.uproject', '{}')
        result = detect(self.project, self.catalog)
        self.assertEqual(result['status'], 'ambiguous')
        self.assertEqual(len(result['candidates']), 2)
        p = self.cli(SCRIPTS / 'game_design.py', 'detect', '--project', self.project)
        self.assertEqual(p.returncode, 1)

    def test_subproject_must_be_explicit(self):
        self.write('nested/project.godot', 'config_version=5')
        self.assertEqual(detect(self.project, self.catalog)['status'], 'unrecognized')
        self.assertEqual(detect(self.project / 'nested', self.catalog)['candidates'][0]['engine'], 'godot')

    def test_symlink_detection_is_ignored(self):
        external = self.base / 'external'
        external.mkdir()
        (external / 'ProjectVersion.txt').write_text('x')
        self.write('Assets/file.txt', 'x')
        (self.project / 'ProjectSettings').symlink_to(external, target_is_directory=True)
        self.assertEqual(detect(self.project, self.catalog)['status'], 'unrecognized')

    def test_catalog_rejects_incomplete_and_traversal(self):
        original = game_design.HOME
        local = self.base / 'copy'
        (local / 'references').mkdir(parents=True)
        game_design.HOME = local
        try:
            for change in ('duplicate', 'empty', 'traversal', 'runtime'):
                data = copy.deepcopy(self.catalog)
                if change == 'duplicate':
                    data['engines'].append(data['engines'][0])
                elif change == 'empty':
                    data['engines'][0]['build'] = ''
                elif change == 'runtime':
                    data['engines'][0]['runtime_validation'] = 'pass'
                else:
                    data['engines'][0]['detection'] = {'files': ['../project.godot']}
                (local / 'references/engines.json').write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    load_catalog()
        finally:
            game_design.HOME = original

    def test_guide_check_read_only_when_missing_or_changed(self):
        original = game_design.HOME
        local = self.base / 'copy'
        (local / 'references/adapters').mkdir(parents=True)
        game_design.HOME = local
        try:
            self.assertEqual(render_adapters(self.catalog, True)['status'], 'drift')
            self.assertEqual(snapshot(local), {})
            render_adapters(self.catalog)
            (local / 'references/adapters/godot.md').write_text('drift')
            before = snapshot(local)
            self.assertEqual(render_adapters(self.catalog, True)['status'], 'drift')
            self.assertEqual(snapshot(local), before)
        finally:
            game_design.HOME = original

    def test_native_dry_run_does_not_create_target(self):
        target = self.base / 'not created'
        p = self.cli(SCRIPTS / 'install_manifest.py', target, '-n')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertFalse(target.exists())

    def test_new_install_and_idempotence(self):
        self.install()
        self.assertTrue((self.project / '.game-design/references/engines.json').is_file())
        self.assertTrue((self.project / '.game-design/references/workflow.svg').is_file())
        before = snapshot(self.project)
        self.install()
        self.assertEqual(snapshot(self.project), before)
        self.assertEqual(check_project(self.project, self.catalog)['status'], 'pending')

    def test_existing_root_and_state_preserved_even_force(self):
        self.write('CLAUDE.md', '# Existing owner\n')
        self.write('Assets/keep.txt', 'game asset')
        self.write('README.md', 'my game')
        self.write('.game-design/state/status.md', 'existing state')
        self.install('--force')
        self.assertEqual((self.project / 'CLAUDE.md').read_text(), '# Existing owner\n')
        self.assertEqual((self.project / 'Assets/keep.txt').read_text(), 'game asset')
        self.assertEqual((self.project / 'README.md').read_text(), 'my game')
        self.assertEqual((self.project / '.game-design/state/status.md').read_text(), 'existing state')
        ledger = json.loads((self.project / '.game-design/install.json').read_text())
        self.assertNotIn('CLAUDE.md', ledger['files'])

    def test_unowned_payload_preserved_even_force(self):
        self.write('.game-design/references/adapters/godot.md', 'custom adapter')
        self.install('-f')
        self.assertEqual((self.project / '.game-design/references/adapters/godot.md').read_text(), 'custom adapter')

    def test_symlink_install_fails_before_any_write(self):
        external = self.base / 'external'
        external.mkdir()
        (self.project / '.game-design').symlink_to(external, target_is_directory=True)
        p = self.cli(SCRIPTS / 'install_manifest.py', self.project)
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse((self.project / 'CLAUDE.md').exists())
        self.assertEqual(snapshot(external), {})

    def test_parent_file_preflight(self):
        self.write('.game-design/references', 'file not directory')
        p = self.cli(SCRIPTS / 'install_manifest.py', self.project)
        self.assertNotEqual(p.returncode, 0)
        self.assertFalse((self.project / 'CLAUDE.md').exists())

    def test_malformed_ledger_preflight(self):
        self.write('.game-design/install.json', '{bad json')
        before = snapshot(self.project)
        p = self.cli(SCRIPTS / 'install_manifest.py', self.project)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(snapshot(self.project), before)

    def test_force_backup_and_standalone_rollback(self):
        self.install()
        path = self.project / '.game-design/references/adapter-contract.md'
        path.write_text('customized managed file')
        self.write('.game-design/state/status.md', 'game in progress')
        self.write('.game-design/deliverables/GDD.md', 'user design')
        result = self.install('-f')
        restore_path = Path(re.search(r"Rollback: python3 '([^']+)'", result.stdout)[1])
        p = self.cli(restore_path, '--check')
        self.assertEqual(p.returncode, 0, p.stderr)
        p = self.cli(restore_path)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(path.read_text(), 'customized managed file')
        self.assertEqual((self.project / '.game-design/state/status.md').read_text(), 'game in progress')
        self.assertEqual((self.project / '.game-design/deliverables/GDD.md').read_text(), 'user design')
        self.assertEqual(self.cli(restore_path).returncode, 0)  # idempotent restore

    def test_post_install_edit_blocks_rollback(self):
        result = self.install()
        restore_path = Path(re.search(r"Rollback: python3 '([^']+)'", result.stdout)[1])
        self.write('CLAUDE.md', 'new edit after install')
        before = snapshot(self.project)
        p = self.cli(restore_path)
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(snapshot(self.project), before)

    def test_in_process_failure_rolls_back_written_paths(self):
        original = install_manifest.atomic
        counter = 0
        def failing(path, data, mode=0o644):
            nonlocal counter
            # Failure after first payload, not while writing transaction evidence.
            if 'backups' not in path.parts:
                counter += 1
                if counter == 2:
                    raise OSError('injected write failure')
            return original(path, data, mode)
        install_manifest.atomic = failing
        try:
            with self.assertRaises(OSError), contextlib.redirect_stdout(io.StringIO()):
                install_manifest.install(self.project)
            self.assertFalse((self.project / 'CLAUDE.md').exists())
            self.assertFalse((self.project / 'AGENTS.md').exists())
        finally:
            install_manifest.atomic = original

    def test_installed_links_and_rendering(self):
        self.install()
        runtime = self.project / '.game-design'
        for doc in runtime.rglob('*.md'):
            for link in re.findall(r'\]\(([^)]+)\)', doc.read_text()):
                if '://' not in link and not link.startswith('#'):
                    self.assertTrue((doc.parent / link.split('#')[0]).exists(), f'{doc}: {link}')
        before = snapshot(self.project)
        for args in [
            [runtime / 'scripts/game_design.py', 'check-catalog'],
            [runtime / 'scripts/game_design.py', 'render-adapters', '--check'],
            [runtime / 'scripts/render_workflow.py', '--source', runtime / 'references/workflow.json',
             '--output', runtime / 'references/workflow.svg', '--check']]:
            p = self.cli(*args, cwd=self.project)
            self.assertEqual(p.returncode, 0, p.stderr + p.stdout)
        self.assertEqual(snapshot(self.project), before)

    def test_workflow_has_branches_and_svg_is_current(self):
        data = json.loads((HOME / 'references/workflow.json').read_text())
        ids = {node['id'] for node in data['nodes']}
        self.assertTrue({'direction','slicegate','releasegate','change','dependency','rollback'} <= ids)
        self.assertTrue(any(e['from']=='direction' and e['to']=='done' for e in data['edges']))
        ET.parse(HOME / 'references/workflow.svg')
        p = self.cli(SCRIPTS / 'render_workflow.py', '--source', HOME / 'references/workflow.json',
                     '--output', HOME / 'references/workflow.svg', '--check')
        self.assertEqual(p.returncode, 0, p.stderr)

    def test_workflow_drift_is_read_only(self):
        output = self.project / 'drift.svg'
        output.write_text('changed')
        p = self.cli(SCRIPTS / 'render_workflow.py', '--source', HOME / 'references/workflow.json',
                     '--output', output, '--check')
        self.assertEqual(p.returncode, 1)
        self.assertEqual(output.read_text(), 'changed')

    def test_unknown_engine_and_project_fail_cleanly(self):
        p = self.cli(SCRIPTS / 'game_design.py', 'adapter', '--engine', 'unknown')
        self.assertEqual(p.returncode, 2)
        p = self.cli(SCRIPTS / 'game_design.py', 'detect', '--project', self.project / 'absent')
        self.assertEqual(p.returncode, 2)

    def test_project_selection_conflict(self):
        self.install()
        path = self.project / '.game-design/state/project.json'
        state = json.loads(path.read_text())
        state.update(engine='unity',engine_version='recorded',targets=['desktop'])
        path.write_text(json.dumps(state))
        self.write('project.godot', 'config_version=5')
        with self.assertRaises(ValueError):
            check_project(self.project, self.catalog)

    def test_configured_project_still_has_no_runtime_pass(self):
        self.install()
        path = self.project / '.game-design/state/project.json'
        state = json.loads(path.read_text())
        state.update(engine='godot', engine_version='recorded', targets=['desktop'],
                     budgets={'frame_time_ms': 16.67, 'memory_mb': 256, 'download_mb': 50})
        path.write_text(json.dumps(state))
        result = check_project(self.project, self.catalog)
        self.assertEqual(result['status'], 'configured')
        self.assertEqual(result['runtime_validation'], 'not_run')

    def test_rollback_rejects_changed_destination_type(self):
        result = self.install()
        restore_path = Path(re.search(r"Rollback: python3 '([^']+)'", result.stdout)[1])
        doc = self.project / 'AGENTS.md'
        doc.unlink()
        doc.mkdir()
        p = self.cli(restore_path)
        self.assertNotEqual(p.returncode, 0)
        self.assertTrue((self.project / 'CLAUDE.md').is_file())

    def test_project_budget_and_enum_validation(self):
        self.install()
        path = self.project / '.game-design/state/project.json'
        original = json.loads(path.read_text())
        for field, value in [('engine','missing'),('mode','auto-publish'),('targets','all'),('engine_version',None)]:
            state = copy.deepcopy(original)
            state[field] = value
            path.write_text(json.dumps(state))
            with self.assertRaises(ValueError):
                check_project(self.project, self.catalog)
        for value in (-1,0,True,float('inf')):
            state = copy.deepcopy(original)
            state['budgets']['frame_time_ms'] = value
            path.write_text(json.dumps(state))
            with self.assertRaises(ValueError):
                check_project(self.project, self.catalog)

    def test_vibe_discovery_init_add_and_dry_run(self):
        p = self.cli('-m','vibe_tool','list','manifests','--json')
        self.assertEqual(p.returncode, 0, p.stderr)
        manifest = next(x for x in json.loads(p.stdout) if x['name']=='game-design')
        self.assertTrue(manifest['has_init_script'])
        target = self.base / 'vibe init target'
        p = self.cli('-m','vibe_tool','init','game-design',target,'--dry-run')
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertFalse(target.exists())
        p = self.cli('-m','vibe_tool','init','game-design',target)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue((target / '.game-design/references/workflow.svg').is_file())
        p = self.cli('-m','vibe_tool','add','manifest','game-design',target,'--force')
        self.assertEqual(p.returncode, 0, p.stderr)
        record = json.loads((target / '.vibe-tool/installations.json').read_text())
        self.assertIn('game-design', json.dumps(record))


# A positive fixture for every adapter; these are format hints, never runtime tests.
FIXTURES = {
 'unity': {'ProjectSettings/ProjectVersion.txt':'m_EditorVersion: test', 'Assets/.keep':''},
 'unreal': {'Game.uproject':'{}'}, 'godot': {'project.godot':'config_version=5'},
 'cocos': {'package.json':'{"creator":{"version":"3.8.0"}}'},
 'phaser': {'package.json':'{"dependencies":{"phaser":"test"}}'},
 'pixi': {'package.json':'{"dependencies":{"pixi.js":"test"}}'},
 'three': {'package.json':'{"devDependencies":{"three":"test"}}'},
 'babylon': {'package.json':'{"dependencies":{"@babylonjs/core":"test"}}'},
 'playcanvas': {'package.json':'{"dependencies":{"playcanvas":"test"}}'},
 'gamemaker': {'Game.yyp':'{}'},'construct': {'Game.c3p':'fixture container'},
 'gdevelop': {'mygame.json':'{"gdVersion":{},"layouts":[],"properties":{}}'},
 'renpy': {'game/options.rpy':'define config.name = "test"'},
 'rpgmaker': {'Game.rmmzproject':'RPGMZ'},'defold': {'game.project':'[project]'},
 'love': {'main.lua':'function love.load() end','conf.lua':'function love.conf(t) end'},
 'monogame': {'Game.csproj':'<PackageReference Include="MonoGame.Framework.DesktopGL" />'},
 'libgdx': {'build.gradle':'implementation "com.badlogicgames.gdx:gdx:test"'},
 'bevy': {'Cargo.toml':'[dependencies]\nbevy = "test"'},
 'raylib': {'CMakeLists.txt':'find_package(raylib REQUIRED)'},
 'roblox': {'game.rbxlx':'<roblox></roblox>'},
 'o3de': {'project.json':'{"project_name":"test","engine":"test"}'},
 'stride': {'Game.sdpkg':'!Package'}
}

def fixture_test(id, files):
    def run(self):
        for name, content in files.items():
            self.write(name, content)
        before = snapshot(self.project)
        result = detect(self.project, self.catalog)
        self.assertEqual(result['status'], 'detected', result)
        self.assertEqual([x['engine'] for x in result['candidates']], [id])
        self.assertEqual(result['runtime_validation'], 'not_run')
        self.assertEqual(snapshot(self.project), before)
    return run
for id, files in FIXTURES.items():
    setattr(GameDesignTests, 'test_detect_' + id, fixture_test(id,files))

if __name__ == '__main__':
    unittest.main()
