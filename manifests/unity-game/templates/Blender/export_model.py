"""Run inside Blender through dcc_cli.py; exports meshes from the COPIED scene.
No objects are deleted, modifiers applied to source data, or dependencies installed.
Settings JSON: {"objects": ["Cube"], "render_preview": false}.
Omit objects to export all meshes; an explicit list must name existing mesh objects.
Preview is opt-in and requires a configured scene camera/render settings.
Review topology/material/texture reports and validate the FBX in Unity separately.
API references: https://docs.blender.org/api/current/bpy.ops.export_scene.html
https://docs.blender.org/api/current/bpy.ops.wm.html
https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

import bpy
import bmesh
from mathutils import Vector


def atomic_json(path, value):
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def artifact(path, role):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(data)
    return {'path': path.name, 'role': role, 'sha256': h.hexdigest()}


def collect_material_images(materials):
    """Include nested shader groups once, including shared or cyclic node trees."""
    images, visited = set(), set()

    def visit(tree):
        if tree is None or id(tree) in visited:
            return
        visited.add(id(tree))
        for node in tree.nodes:
            if node.type == 'TEX_IMAGE' and node.image:
                images.add(node.image)
            elif node.type == 'GROUP':
                visit(node.node_tree)

    for material in materials:
        if material.use_nodes:
            visit(material.node_tree)
    return images


def audit_texture_references(images):
    textures = []
    for image in sorted(images, key=lambda x: x.name):
        path = bpy.path.abspath(image.filepath, library=image.library)
        packed = bool(image.packed_file)
        textures.append({'name': image.name, 'path': path, 'packed': packed,
                         'source': image.source, 'exists': packed or Path(path).is_file()})
    if any(not texture['exists'] for texture in textures):
        raise ValueError('Missing referenced textures; pack dependencies or repath only the copied scene')
    return textures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--job', required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    job = json.loads(Path(args.job).read_text(encoding='utf-8'))
    directory = Path(job['output_dir']).resolve()
    if job.get('create_new') or not job.get('source_copy'):
        raise ValueError('This export-only template needs --project; --new requires an explicit modeling script')
    if Path(bpy.data.filepath).resolve() != Path(job['source_copy']).resolve():
        raise ValueError('Expected copied scene, not the original source')
    settings = job.get('settings', {})
    names = settings.get('objects')
    if names is not None and (not isinstance(names, list) or not names or
                              any(not isinstance(n, str) for n in names) or len(set(names)) != len(names)):
        raise ValueError('objects must be a nonempty list of unique names')
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH' and (names is None or o.name in names)]
    if names is not None and {o.name for o in meshes} != set(names):
        raise ValueError('Some requested meshes are absent from this scene')
    if not meshes:
        raise ValueError('No mesh objects to export')
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    # Operate only on the copied scene. FBX exports selected meshes and does not modify them.
    bpy.ops.object.select_all(action='DESELECT')
    details, corners = [], []
    for obj in meshes:
        obj.hide_set(False)
        obj.select_set(True)
        obj.data.calc_loop_triangles()
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            non_manifold = sum(not e.is_manifold for e in bm.edges)
        finally:
            bm.free()
        material_names = [slot.material.name if slot.material else None for slot in obj.material_slots]
        corners.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
        details.append({'name': obj.name, 'vertices': len(obj.data.vertices),
                        'triangles': len(obj.data.loop_triangles), 'material_slots': material_names,
                        'non_manifold_edges': non_manifold,
                        'negative_scale': obj.matrix_world.determinant() < 0})
    if sum(d['triangles'] for d in details) <= 0:
        raise ValueError('No triangles to export')
    materials = {slot.material for obj in meshes for slot in obj.material_slots if slot.material}
    textures = audit_texture_references(collect_material_images(materials))
    blend = directory / 'model.blend'
    fbx = directory / 'model.fbx'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend))
    bpy.ops.export_scene.fbx(filepath=str(fbx), use_selection=True, object_types={'MESH'},
                             axis_forward='-Z', axis_up='Y', add_leaf_bones=False,
                             bake_anim=False, path_mode='COPY', embed_textures=True)
    artifacts = [artifact(blend, 'project'), artifact(fbx, 'export')]
    if settings.get('render_preview', False):
        if not bpy.context.scene.camera:
            raise ValueError('Preview requested but scene has no configured camera')
        preview = directory / 'preview.png'
        bpy.context.scene.render.image_settings.file_format = 'PNG'
        bpy.context.scene.render.filepath = str(preview)
        bpy.ops.render.render(write_still=True)
        artifacts.append(artifact(preview, 'preview'))
    atomic_json(directory / 'asset-result.json', {
        'status': 'passed', 'audit': {
            'mesh_count': len(meshes), 'triangles': sum(d['triangles'] for d in details),
            'objects': details, 'textures': textures,
            'bounds_world': {'min': [min(v[i] for v in corners) for i in range(3)],
                             'max': [max(v[i] for v in corners) for i in range(3)]},
            'units': {'system': bpy.context.scene.unit_settings.system,
                      'scale_length': bpy.context.scene.unit_settings.scale_length},
            'limitations': ['Topology metrics use base meshes, not evaluated modifiers.',
                            'FBX runtime, Unity materials, rigging and device budgets require independent review.']},
        'artifacts': artifacts})


if __name__ == '__main__':
    main()
