#!/usr/bin/env python3
"""Stdlib Blender copy-and-run adapter; never installs Blender or modifies the input.
Exit codes: 0 passed, 1 failed, 2 not_run. Output directories must be new.
A script receives --job job.json and writes asset-result.json (see Blender template).
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from urllib.parse import unquote, unquote_to_bytes, urlsplit


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def atomic_json(path, value):
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def process(command, directory, prefix, timeout):
    record = {'command': command, 'exit_code': None, 'timed_out': False}
    started = time.monotonic()
    with (directory / (prefix + '-stdout.txt')).open('wb') as out, (directory / (prefix + '-stderr.txt')).open('wb') as err:
        try:
            proc = subprocess.Popen(command, stdout=out, stderr=err, shell=False,
                                    start_new_session=os.name != 'nt')
            try:
                record['exit_code'] = proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                record['timed_out'] = True
                if os.name == 'nt':
                    try:
                        subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
                    except (OSError, subprocess.TimeoutExpired):
                        pass
                    if proc.poll() is None:
                        proc.kill()
                else:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                record['exit_code'] = proc.wait()
        except OSError as exc:
            record['launch_error'] = str(exc)
    record['duration_seconds'] = round(time.monotonic() - started, 3)
    return record


def blender_path(explicit):
    specified = explicit or os.environ.get('BLENDER_BINARY') or shutil.which('blender')
    if not specified:
        raise ValueError('missing_blender: set --blender or BLENDER_BINARY, or put Blender on PATH')
    candidate = Path(specified).expanduser().resolve()
    if not candidate.is_file():
        raise ValueError('missing_blender: ' + str(candidate))
    return candidate


def gltf_dependencies(path, directory, source_copy):
    """Resolve core glTF buffers/images into a self-contained evidence bundle.

    This checks URI closure and buffer lengths, not topology/schema conformance.
    No network fetching: references must be embedded data or files in output_dir.
    """
    document = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(document, dict) or not isinstance(document.get('asset'), dict) or document['asset'].get('version') != '2.0':
        raise ValueError('invalid_gltf_document')
    references = []
    for kind in ('buffers', 'images'):
        entries = document.get(kind, [])
        if not isinstance(entries, list):
            raise ValueError('invalid_gltf_references')
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise ValueError('invalid_gltf_reference')
            uri = entry.get('uri')
            if uri is None and kind == 'images' and type(entry.get('bufferView')) is int:
                views = document.get('bufferViews', [])
                view = entry['bufferView']
                if not isinstance(views, list) or not 0 <= view < len(views) or not isinstance(views[view], dict):
                    raise ValueError('invalid_gltf_image_buffer_view')
                buffer = views[view].get('buffer')
                buffers = document.get('buffers', [])
                if type(buffer) is not int or not isinstance(buffers, list) or not 0 <= buffer < len(buffers):
                    raise ValueError('invalid_gltf_image_buffer_view')
                continue  # The enclosing buffer URI is checked in the buffers pass.
            if not isinstance(uri, str) or not uri:
                raise ValueError('missing_gltf_dependency_uri')
            reference = {'export': str(path), 'reference': f'{kind}/{index}/uri', 'source_uri': uri}
            if uri.lower().startswith('data:'):
                try:
                    metadata, body = uri[5:].split(',', 1)
                    raw = unquote_to_bytes(body)
                    if metadata.lower().endswith(';base64'):
                        raw = base64.b64decode(raw, validate=True)
                except (ValueError, TypeError) as exc:
                    raise ValueError('invalid_gltf_data_uri') from exc
                reference.update(embedded=True, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())
            else:
                parsed = urlsplit(uri)
                decoded = unquote(parsed.path)
                if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or not decoded or '\\' in decoded or '\x00' in decoded or Path(decoded).is_absolute():
                    raise ValueError('gltf_dependency_not_local')
                dependency = (path.parent / decoded).resolve()
                if not dependency.is_relative_to(directory) or dependency == source_copy:
                    raise ValueError('gltf_dependency_outside_bundle')
                if not dependency.is_file() or not dependency.stat().st_size:
                    raise ValueError('missing_gltf_dependency: ' + str(dependency))
                reference.update(path=str(dependency), role='dependency', bytes=dependency.stat().st_size,
                                 sha256=digest(dependency), embedded=False)
            if not reference['bytes']:
                raise ValueError('empty_gltf_dependency')
            if kind == 'buffers':
                length = entry.get('byteLength')
                if type(length) is not int or length <= 0 or reference['bytes'] < length:
                    raise ValueError('gltf_buffer_length_mismatch')
            references.append(reference)
    return references


def verify_assets(directory, source_copy):
    report = json.loads((directory / 'asset-result.json').read_text(encoding='utf-8'))
    if not isinstance(report, dict) or report.get('status') != 'passed':
        raise ValueError('asset_report_not_passed')
    audit = report.get('audit')
    if not isinstance(audit, dict) or type(audit.get('mesh_count')) is not int or audit['mesh_count'] <= 0:
        raise ValueError('missing_mesh_audit')
    if type(audit.get('triangles')) is not int or audit['triangles'] <= 0:
        raise ValueError('missing_triangle_audit')
    entries = report.get('artifacts')
    if not isinstance(entries, list) or not entries:
        raise ValueError('missing_artifacts')
    verified, seen, roles = [], set(), set()
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get('path'), str):
            raise ValueError('invalid_artifact_entry')
        path = (directory / entry['path']).resolve()
        if not path.is_relative_to(directory) or path == source_copy or path in seen:
            raise ValueError('artifact_not_unique_local_output')
        if path.suffix.lower() not in ('.blend', '.fbx', '.glb', '.gltf', '.bin', '.png', '.jpg', '.jpeg', '.ktx', '.ktx2', '.webp', '.avif', '.dds', '.tga', '.tif', '.tiff', '.exr', '.hdr', '.bmp'):
            raise ValueError('unexpected_artifact_type')
        if not path.is_file() or not path.stat().st_size:
            raise ValueError('missing_or_empty_artifact: ' + str(path))
        actual = digest(path)
        if actual != entry.get('sha256'):
            raise ValueError('artifact_hash_mismatch: ' + str(path))
        role = entry.get('role')
        if role == 'project' and path.suffix.lower() == '.blend':
            roles.add('project')
        if role == 'export' and path.suffix.lower() in ('.fbx', '.glb', '.gltf'):
            roles.add('export')
        seen.add(path)
        verified.append({'path': str(path), 'role': role, 'sha256': actual, 'bytes': path.stat().st_size})
    if not {'project', 'export'} <= roles:
        raise ValueError('required_project_and_export_missing')
    dependencies = []
    for record in list(verified):
        if record['role'] == 'export' and Path(record['path']).suffix.lower() == '.gltf':
            dependencies.extend(gltf_dependencies(Path(record['path']), directory, source_copy))
    for reference in dependencies:
        if not reference['embedded'] and Path(reference['path']) not in seen:
            seen.add(Path(reference['path']))
            verified.append({key: reference[key] for key in ('path', 'role', 'sha256', 'bytes')})
    return {'audit': audit, 'artifacts': verified, 'gltf_dependencies': dependencies,
            'gltf_dependency_status': 'verified' if dependencies or any(Path(r['path']).suffix.lower() == '.gltf' for r in verified) else 'not_applicable'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    for name in ('doctor', 'run'):
        p = sub.add_parser(name)
        p.add_argument('--blender')
        p.add_argument('--output-dir', required=name == 'run')
        p.add_argument('--timeout', type=float, default=300)
        if name == 'run':
            source_group = p.add_mutually_exclusive_group(required=True)
            source_group.add_argument('--project')
            source_group.add_argument('--new', action='store_true', help='Run an explicit creation script in a factory-startup workspace')
            p.add_argument('--script', required=True)
            p.add_argument('--settings', help='JSON object consumed by the chosen Blender script')
    args = parser.parse_args(argv)
    if not 0 < args.timeout < float('inf'):
        parser.error('--timeout must be finite and positive')
    temporary = None
    if args.output_dir:
        directory = Path(args.output_dir).expanduser().resolve()
        try:
            directory.mkdir(parents=True, exist_ok=False)
        except OSError as exc:
            print(json.dumps({'status': 'not_run', 'reason': 'output_directory_not_fresh', 'detail': str(exc)}))
            return 2
    else:
        temporary = tempfile.TemporaryDirectory(prefix='unity-game-blender-doctor-')
        directory = Path(temporary.name)
    result = {'status': 'not_run', 'operation': args.operation, 'output_dir': str(directory)}
    lock, source, before = None, None, None
    launched = False
    try:
        executable = blender_path(args.blender)
        probe = process([str(executable), '--version'], directory, 'version', min(30, args.timeout))
        result['version_probe'] = probe
        version_text = (directory / 'version-stdout.txt').read_text(encoding='utf-8', errors='replace')
        match = re.search(r'^Blender\s+(\d+\.\d+(?:\.\d+)?)(?:\s|$)', version_text, re.M)
        if probe['exit_code'] != 0 or probe['timed_out'] or not match:
            raise ValueError('blender_version_unverified')
        result.update(blender=str(executable), blender_version=match[1])
        if args.operation == 'doctor':
            result.update(status='passed', reason='blender_found')
        else:
            source = Path(args.project).expanduser().resolve() if args.project else None
            script = Path(args.script).expanduser().resolve()
            if source is not None and (source.suffix.lower() != '.blend' or not source.is_file()):
                raise ValueError('missing_blend_project')
            if script.suffix.lower() != '.py' or not script.is_file():
                raise ValueError('missing_python_script')
            settings = json.loads(Path(args.settings).read_text(encoding='utf-8')) if args.settings else {}
            if not isinstance(settings, dict):
                raise ValueError('settings_must_be_object')
            copied = None
            if source is not None:
                lock_path = Path(tempfile.gettempdir()) / ('unity-game-dcc-' + hashlib.sha256(os.fsencode(str(source))).hexdigest() + '.lock')
                try:
                    fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                except FileExistsError as exc:
                    raise ValueError('source_busy: active or stale lock ' + str(lock_path)) from exc
                lock = lock_path
                with os.fdopen(fd, 'w') as stream:
                    stream.write(str(os.getpid()) + '\n' + str(source))
                before = digest(source)
                result['source'] = {'path': str(source), 'sha256_before': before}
                copied = directory / 'source-copy.blend'
                shutil.copy2(source, copied)
                if digest(copied) != before:
                    raise ValueError('source_copy_hash_mismatch')
            else:
                result['source'] = {'create_new': True}
            # Copy the executable script too, freezing its exact content for the evidence bundle.
            script_copy = directory / 'operation.py'
            shutil.copy2(script, script_copy)
            result['script'] = {'path': str(script), 'sha256': digest(script_copy)}
            atomic_json(directory / 'job.json', {'schema_version': 1, 'create_new': args.new, 'source_copy': str(copied) if copied else None,
                        'output_dir': str(directory), 'settings': settings})
            command = [str(executable), '--disable-autoexec', '--background']
            command += [str(copied)] if copied else ['--factory-startup']
            command += ['--python-exit-code', '1',
                       '--python', str(script_copy), '--', '--job', str(directory / 'job.json')]
            launched = True
            result['process'] = process(command, directory, 'run', args.timeout)
            proc = result['process']
            if proc['timed_out']:
                raise ValueError('blender_timeout')
            if proc['exit_code'] != 0:
                raise ValueError('blender_exit_failure')
            result.update(verify_assets(directory, copied))
            result.update(status='passed', reason='artifacts_verified')
    except (OSError, ValueError, TypeError, KeyError) as exc:
        result.update(status='failed' if launched else 'not_run', reason=str(exc))
    finally:
        if before is not None:
            try:
                after = digest(source)
                result['source'].update(sha256_after=after, unchanged=before == after)
                if before != after:
                    result.update(status='failed', reason='original_source_changed')
            except OSError as exc:
                result.update(status='failed', reason='original_source_unavailable', detail=str(exc))
        if lock is not None:
            lock.unlink()
        atomic_json(directory / 'result.json', result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if temporary:
            temporary.cleanup()
    return {'passed': 0, 'failed': 1, 'not_run': 2}[result['status']]


if __name__ == '__main__':
    sys.exit(main())
