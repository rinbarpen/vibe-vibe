"""Fake-Blender semantics only; these tests do not establish bpy/FBX runtime validity."""
import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('unity_game_dcc', ROOT / 'scripts/dcc_cli.py')
cli = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cli)
FAKE = r'''
import hashlib, json, os
from pathlib import Path
import sys, time
if '--version' in sys.argv:
    print('Blender 4.5.3' if os.environ.get('DCC_MODE') != 'bad_version' else 'unknown')
    sys.exit(0)
job = json.loads(Path(sys.argv[sys.argv.index('--job')+1]).read_text())
out = Path(job['output_dir'])
mode = os.environ.get('DCC_MODE', 'ok')
if mode == 'timeout': time.sleep(10)
if mode == 'exit': sys.exit(3)
if mode == 'missing': sys.exit(0)
if mode == 'empty_report':
    (out/'asset-result.json').write_text('{}')
    sys.exit(0)
entries = []
for name, role in [('model.blend', 'project'), ('model.gltf' if mode.startswith('gltf_') else 'model.fbx', 'export')]:
    p = out/name
    p.write_bytes(b'' if mode == 'empty_asset' else name.encode())
    entries.append({'path':name, 'role':role, 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
if mode.startswith('gltf_'):
    document = {'asset': {'version': '2.0'}, 'buffers': [{'uri': 'mesh.bin', 'byteLength': 4}],
                'images': [{'uri': 'textures/surface.png'}]}
    (out/'mesh.bin').write_bytes(b'ABCD')
    (out/'textures').mkdir()
    (out/'textures/surface.png').write_bytes(b'image fixture')
    if mode == 'gltf_missing_buffer': (out/'mesh.bin').unlink()
    if mode == 'gltf_missing_texture': (out/'textures/surface.png').unlink()
    if mode == 'gltf_remote': document['buffers'][0]['uri'] = 'https://example.invalid/mesh.bin'
    if mode == 'gltf_escape': document['buffers'][0]['uri'] = '../source model.blend'
    if mode == 'gltf_source_copy': document['buffers'][0]['uri'] = 'source-copy.blend'
    if mode == 'gltf_bad_length': document['buffers'][0]['byteLength'] = 400
    if mode in ('gltf_data_uri', 'gltf_bad_data_uri'):
        document['buffers'][0]['uri'] = 'data:application/octet-stream;base64,QUJDRA=='
        document['images'][0]['uri'] = 'data:image/png;base64,aW1hZ2U='
        if mode == 'gltf_bad_data_uri': document['buffers'][0]['uri'] = 'data:application/octet-stream;base64,$$notbase64'
    if mode == 'gltf_percent_uri':
        (out/'mesh.bin').rename(out/'nested mesh.bin')
        document['buffers'][0]['uri'] = 'nested%20mesh.bin'
    if mode == 'gltf_symlink_escape':
        (out/'mesh.bin').unlink()
        (out/'mesh.bin').symlink_to(os.environ['DCC_SOURCE'])
    if mode == 'gltf_buffer_view_image':
        document['bufferViews'] = [{'buffer': 0, 'byteOffset': 0, 'byteLength': 4}]
        document['images'] = [{'bufferView': 0, 'mimeType': 'image/png'}]
    if mode == 'gltf_explicit_dependencies':
        for name in ('mesh.bin', 'textures/surface.png'):
            p = out/name
            entries.append({'path': name, 'role': 'dependency', 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    p = out/'model.gltf'
    p.write_text(json.dumps(document))
    entries[1]['sha256'] = hashlib.sha256(p.read_bytes()).hexdigest()
if mode == 'bad_hash': entries[0]['sha256'] = '0'*64
if mode == 'source_as_asset': entries[0]['path'] = 'source-copy.blend'
if mode == 'traversal': entries[0]['path'] = '../outside.blend'
if mode == 'source_changed':
    Path(os.environ['DCC_SOURCE']).write_bytes(b'changed')
report = {'status':'passed', 'audit':{'mesh_count':1, 'triangles':12}, 'artifacts':entries}
if mode == 'no_mesh': report['audit']['mesh_count'] = 0
if mode == 'no_triangles': report['audit']['triangles'] = 0
if mode == 'no_export': report['artifacts'] = entries[:1]
(out/'asset-result.json').write_text(json.dumps(report))
'''


@unittest.skipIf(os.name == 'nt', 'POSIX fake executable fixture')
class DccTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='dcc adapter tests ')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source model.blend'
        self.source.write_bytes(b'fake original blend')
        self.script = self.root / 'chosen script.py'
        self.script.write_text('# fake modeling operation')
        self.blender = self.root / 'fake blender'
        self.blender.write_text('#!' + sys.executable + '\n' + FAKE)
        self.blender.chmod(self.blender.stat().st_mode | stat.S_IXUSR)
        self.number = 0

    def call(self, mode='ok', operation='run', extra=(), new=False):
        self.number += 1
        out = self.root / ('run ' + str(self.number))
        args = [operation, '--blender', str(self.blender), '--output-dir', str(out), '--timeout', '1']
        if operation == 'run':
            args += ['--script', str(self.script)]
            args += ['--new'] if new else ['--project', str(self.source)]
        args += list(extra)
        with mock.patch.dict(os.environ, {'DCC_MODE': mode, 'DCC_SOURCE': str(self.source)}), contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(args)
        return code, json.loads((out / 'result.json').read_text()), out

    def test_doctor(self):
        code, result, _ = self.call(operation='doctor')
        self.assertEqual(code, 0)
        self.assertEqual(result['blender_version'], '4.5.3')

    def test_missing_blender(self):
        code, result, _ = self.call(extra=['--blender', str(self.root / 'missing')])
        self.assertEqual(code, 2)
        self.assertEqual(result['status'], 'not_run')

    def test_invalid_version(self):
        code, result, _ = self.call(mode='bad_version')
        self.assertEqual(code, 2)
        self.assertEqual(result['reason'], 'blender_version_unverified')

    def test_copy_preserves_original_and_records_commands(self):
        before = cli.digest(self.source)
        code, result, out = self.call()
        self.assertEqual(code, 0)
        self.assertEqual(cli.digest(self.source), before)
        self.assertTrue(result['source']['unchanged'])
        self.assertEqual((out / 'source-copy.blend').read_bytes(), self.source.read_bytes())
        command = result['process']['command']
        self.assertIn('--disable-autoexec', command)
        self.assertIn('--python-exit-code', command)
        self.assertNotIn(str(self.source), command)
        self.assertEqual(command[command.index('--python') + 1], str(out / 'operation.py'))
        self.assertEqual(result['script']['sha256'], cli.digest(self.script))
        self.assertTrue((out / 'run-stdout.txt').is_file())
        self.assertTrue((out / 'run-stderr.txt').is_file())
        self.assertEqual(len(result['artifacts']), 2)

    def test_new_requires_explicit_script_and_carries_settings(self):
        settings = self.root / 'settings.json'
        settings.write_text('{"target_triangles": 1200}')
        code, result, out = self.call(new=True, extra=['--settings', str(settings)])
        self.assertEqual(code, 0)
        self.assertIn('--factory-startup', result['process']['command'])
        job = json.loads((out / 'job.json').read_text())
        self.assertTrue(job['create_new'])
        self.assertIsNone(job['source_copy'])
        self.assertEqual(job['settings']['target_triangles'], 1200)
        self.assertFalse((out / 'source-copy.blend').exists())

    def test_gltf_dependencies_are_local_hashed_and_deduplicated(self):
        for mode in ('gltf_ok', 'gltf_percent_uri', 'gltf_explicit_dependencies'):
            with self.subTest(mode=mode):
                code, result, out = self.call(mode=mode)
                self.assertEqual(0, code, result)
                self.assertEqual('verified', result['gltf_dependency_status'])
                self.assertEqual(4, len(result['artifacts']))
                self.assertEqual(2, len(result['gltf_dependencies']))
                for record in result['gltf_dependencies']:
                    self.assertFalse(record['embedded'])
                    self.assertEqual(cli.digest(Path(record['path'])), record['sha256'])
                    self.assertTrue(Path(record['path']).is_relative_to(out))
                    self.assertIn('source_uri', record)

    def test_gltf_embedded_data_dependencies_need_no_external_files(self):
        code, result, _ = self.call(mode='gltf_data_uri')
        self.assertEqual(0, code, result)
        self.assertEqual(2, len(result['artifacts']))
        self.assertTrue(all(record['embedded'] for record in result['gltf_dependencies']))
        buffer = result['gltf_dependencies'][0]
        self.assertEqual(4, buffer['bytes'])
        self.assertEqual(hashlib.sha256(b'ABCD').hexdigest(), buffer['sha256'])

    def test_gltf_buffer_view_image_uses_verified_buffer(self):
        code, result, _ = self.call(mode='gltf_buffer_view_image')
        self.assertEqual(0, code, result)
        self.assertEqual(1, len(result['gltf_dependencies']))
        self.assertEqual(3, len(result['artifacts']))

    def test_gltf_missing_remote_or_outside_dependencies_fail(self):
        for mode in ('gltf_missing_buffer', 'gltf_missing_texture', 'gltf_remote', 'gltf_escape',
                     'gltf_source_copy', 'gltf_bad_length', 'gltf_bad_data_uri', 'gltf_symlink_escape'):
            with self.subTest(mode=mode):
                code, result, _ = self.call(mode=mode)
                self.assertEqual(1, code)
                self.assertEqual('failed', result['status'])
                self.assertTrue(any(reason in result['reason'] for reason in
                                    ('missing_gltf_dependency', 'gltf_dependency_', 'gltf_buffer_length_mismatch', 'invalid_gltf_data_uri')),
                                result)

    def test_no_false_pass(self):
        for mode in ['missing', 'empty_report', 'empty_asset', 'bad_hash', 'source_as_asset',
                     'traversal', 'no_mesh', 'no_triangles', 'no_export', 'exit']:
            with self.subTest(mode=mode):
                code, result, _ = self.call(mode=mode)
                self.assertEqual(code, 1)
                self.assertEqual(result['status'], 'failed')

    def test_timeout(self):
        code, result, _ = self.call(mode='timeout', extra=['--timeout', '.1'])
        self.assertEqual(code, 1)
        self.assertEqual(result['reason'], 'blender_timeout')
        self.assertTrue(result['process']['timed_out'])

    def test_original_change_is_failed(self):
        code, result, _ = self.call(mode='source_changed')
        self.assertEqual(code, 1)
        self.assertFalse(result['source']['unchanged'])
        self.assertEqual(result['reason'], 'original_source_changed')

    def test_existing_output_preserved(self):
        out = self.root / 'existing'
        out.mkdir()
        sentinel = out / 'result.json'
        sentinel.write_text('existing evidence')
        with contextlib.redirect_stdout(io.StringIO()):
            code = cli.main(['run', '--project', str(self.source), '--script', str(self.script), '--output-dir', str(out)])
        self.assertEqual(code, 2)
        self.assertEqual(sentinel.read_text(), 'existing evidence')

    def test_source_lock(self):
        lock = Path(tempfile.gettempdir()) / ('unity-game-dcc-' + hashlib.sha256(os.fsencode(str(self.source.resolve()))).hexdigest() + '.lock')
        lock.write_text('other run')
        try:
            code, result, _ = self.call()
            self.assertEqual(code, 2)
            self.assertIn('source_busy', result['reason'])
            self.assertTrue(lock.exists())
        finally:
            lock.unlink()

    def test_explicit_env_and_path_resolution(self):
        with mock.patch.dict(os.environ, {'BLENDER_BINARY': str(self.blender)}):
            self.assertEqual(cli.blender_path(None), self.blender)
            with self.assertRaisesRegex(ValueError, 'missing_blender'):
                cli.blender_path(str(self.root / 'missing'))
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(cli.shutil, 'which', return_value=str(self.blender)):
            self.assertEqual(cli.blender_path(None), self.blender)

    def test_nonfinite_nonpositive_timeout_rejected_before_creating_output(self):
        for value in ['0', '-1', 'nan', 'inf', '-inf']:
            with self.subTest(timeout=value):
                output = self.root / ('invalid-timeout-' + value)
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                    cli.main(['doctor', '--timeout=' + value, '--output-dir', str(output)])
                self.assertEqual(caught.exception.code, 2)
                self.assertFalse(output.exists())

    def test_invalid_settings_and_project(self):
        settings = self.root / 'settings.json'
        settings.write_text('[]')
        code, result, _ = self.call(extra=['--settings', str(settings)])
        self.assertEqual(code, 2)
        self.assertEqual(result['reason'], 'settings_must_be_object')
        code, result, _ = self.call(extra=['--project', str(self.root / 'absent.blend')])
        self.assertEqual(code, 2)
        self.assertEqual(result['reason'], 'missing_blend_project')


class TemplateTextureAuditTests(unittest.TestCase):
    """Execute only pure helper ASTs; no bpy/Blender runtime validity is implied."""
    def setUp(self):
        template = ROOT / 'templates/Blender/export_model.py'
        tree = ast.parse(template.read_text(encoding='utf-8'))
        helpers = ast.Module(body=[node for node in tree.body if isinstance(node, ast.FunctionDef)
                                  and node.name in ('collect_material_images', 'audit_texture_references')],
                             type_ignores=[])
        namespace = {'Path': Path, 'bpy': SimpleNamespace(path=SimpleNamespace(
            abspath=lambda path, library=None: path))}
        exec(compile(helpers, str(template), 'exec'), namespace)
        self.collect = namespace['collect_material_images']
        self.audit = namespace['audit_texture_references']

    def image(self, name='texture', filepath='/missing/texture.png', packed=True):
        image = mock.Mock()
        image.name = name
        image.filepath = filepath
        image.library = None
        image.packed_file = packed
        image.source = 'FILE'
        return image

    def material(self, nodes):
        return SimpleNamespace(use_nodes=True, node_tree=SimpleNamespace(nodes=nodes))

    def test_direct_image(self):
        image = self.image()
        result = self.collect([self.material([SimpleNamespace(type='TEX_IMAGE', image=image)])])
        self.assertEqual(result, {image})
        self.assertTrue(self.audit(result)[0]['exists'])

    def test_nested_image_and_shared_group(self):
        image = self.image()
        nested = SimpleNamespace(nodes=[SimpleNamespace(type='TEX_IMAGE', image=image)])
        inner = SimpleNamespace(nodes=[SimpleNamespace(type='GROUP', node_tree=nested)])
        result = self.collect([self.material([SimpleNamespace(type='GROUP', node_tree=inner),
                                             SimpleNamespace(type='GROUP', node_tree=nested)])])
        self.assertEqual(result, {image})
        self.assertEqual(len(self.audit(result)), 1)

    def test_missing_nested_texture_blocks_export(self):
        image = self.image(packed=False)
        nested = SimpleNamespace(nodes=[SimpleNamespace(type='TEX_IMAGE', image=image)])
        images = self.collect([self.material([SimpleNamespace(type='GROUP', node_tree=nested)])])
        with self.assertRaisesRegex(ValueError, 'Missing referenced textures'):
            self.audit(images)

    def test_cycle_and_empty_group_terminate(self):
        image = self.image()
        tree = SimpleNamespace(nodes=[])
        tree.nodes.extend([SimpleNamespace(type='GROUP', node_tree=tree),
                           SimpleNamespace(type='GROUP', node_tree=None),
                           SimpleNamespace(type='TEX_IMAGE', image=image),
                           SimpleNamespace(type='TEX_IMAGE', image=None)])
        self.assertEqual(self.collect([SimpleNamespace(use_nodes=True, node_tree=tree)]), {image})


if __name__ == '__main__':
    unittest.main()
