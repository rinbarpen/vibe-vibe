"""Create deterministic regression fixtures, not production-quality model examples."""

import argparse
from pathlib import Path
import sys

import bpy


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    collection = bpy.data.collections.new('ASSET')
    bpy.context.scene.collection.children.link(collection)
    return collection


def move(obj, collection, name):
    obj.name = name
    for original in list(obj.users_collection):
        original.objects.unlink(obj)
    collection.objects.link(obj)
    return obj


def cube(collection):
    bpy.ops.mesh.primitive_cube_add()
    return move(bpy.context.object, collection, 'Body')


def save(output, name):
    bpy.ops.wm.save_as_mainfile(filepath=str(output / name))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--highpoly', action='store_true', help='Also generate a million-triangle evaluation fixture')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    output = Path(args.output_dir).resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError('fixture output directory must be empty')
    output.mkdir(parents=True, exist_ok=True)
    collection = reset()
    obj = cube(collection)
    sub = obj.modifiers.new('TestSubdivision', 'SUBSURF')
    sub.levels = sub.render_levels = 1
    save(output, 'good.blend')

    collection = reset()
    mesh = bpy.data.meshes.new('OpenQuad')
    mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], [], [(0, 1, 2, 3)])
    obj = bpy.data.objects.new('OpenQuad', mesh)
    collection.objects.link(obj)
    save(output, 'open.blend')

    collection = reset()
    obj = cube(collection)
    for layer in list(obj.data.uv_layers):
        obj.data.uv_layers.remove(layer)
    save(output, 'no-uv.blend')

    collection = reset()
    obj = cube(collection)
    missing = bpy.data.images.new('MissingTexture', width=32, height=32)
    missing.source = 'FILE'
    missing.filepath = '//missing-texture-TEST.png'
    material = bpy.data.materials.new('MissingTextureMaterial')
    material.use_nodes = True
    texture = material.node_tree.nodes.new('ShaderNodeTexImage')
    texture.image = missing
    obj.data.materials.append(material)
    save(output, 'missing-texture.blend')

    collection = reset()
    mesh = bpy.data.meshes.new('DegenerateTriangle')
    mesh.from_pydata([(0, 0, 0), (1, 0, 0), (2, 0, 0)], [], [(0, 1, 2)])
    collection.objects.link(bpy.data.objects.new('DegenerateTriangle', mesh))
    save(output, 'degenerate.blend')

    collection = reset()
    body = cube(collection)
    body.scale = (1.5, 0.8, 1.1)
    bpy.context.view_layer.objects.active = body
    body.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bevel = body.modifiers.new('EdgeRadius', 'BEVEL')
    bevel.width = 0.12
    bevel.segments = 4
    body.modifiers.new('WeightedNormal', 'WEIGHTED_NORMAL')
    bpy.ops.mesh.primitive_torus_add(major_segments=64, minor_segments=16,
                                   major_radius=0.55, minor_radius=0.09,
                                   location=(0, -0.85, 0), rotation=(1.57079632679, 0, 0))
    ring = move(bpy.context.object, collection, 'FrontRing')
    for face in ring.data.polygons:
        face.use_smooth = True
    # Asymmetric marker makes front/back inspection meaningful.
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.18,
                                       location=(1.0, -0.85, 0.65))
    move(bpy.context.object, collection, 'OrientationMarker')
    save(output, 'render.blend')

    if args.highpoly:
        collection = reset()
        bpy.ops.mesh.primitive_uv_sphere_add(segments=512, ring_count=256)
        obj = move(bpy.context.object, collection, 'DenseEvaluationFixture')
        sub = obj.modifiers.new('DenseSubdivision', 'SUBSURF')
        sub.levels = sub.render_levels = 1
        save(output, 'highpoly.blend')
    print('FIXTURES CREATED ' + str(output), flush=True)


if __name__ == '__main__':
    main()
