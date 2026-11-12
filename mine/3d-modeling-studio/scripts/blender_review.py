#!/usr/bin/env python3
"""Render eight inspection views in a temporary scene without saving the input file."""

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Vector


VIEWS = {
    'front': (0, -1, 0), 'back': (0, 1, 0),
    'left': (-1, 0, 0), 'right': (1, 0, 0),
    'top': (0, 0, 1), 'bottom': (0, 0, -1),
    'three_quarter_front': (1, -1, 0.65),
    'three_quarter_back': (-1, 1, 0.65),
}


def sha256(path):
    with open(path, 'rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--collection', required=True, help='Explicit asset-only collection')
    parser.add_argument('--mode', choices=('clay', 'material'), default='clay')
    parser.add_argument('--views', default=','.join(VIEWS))
    parser.add_argument('--resolution', type=int, default=768)
    parser.add_argument('--samples', type=int, default=32)
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    args = parser.parse_args(argv)
    names = args.views.split(',')
    if not names or any(name not in VIEWS for name in names) or len(names) != len(set(names)):
        parser.error('views must be unique comma-separated names from: ' + ','.join(VIEWS))
    if not 64 <= args.resolution <= 8192 or not 1 <= args.samples <= 4096:
        parser.error('resolution must be 64..8192 and samples 1..4096')
    collection = bpy.data.collections.get(args.collection)
    if collection is None:
        raise ValueError(f'collection does not exist: {args.collection}')
    asset_objects = [o for o in collection.all_objects if o.type in {'MESH', 'CURVE', 'SURFACE', 'FONT'}]
    if not asset_objects:
        raise ValueError('asset collection has no supported render geometry')
    source_scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    # Bounds use viewport-evaluated objects; render subdivision and instances may differ.
    corners = []
    for obj in asset_objects:
        evaluated = obj.evaluated_get(depsgraph)
        corners.extend(evaluated.matrix_world @ Vector(corner) for corner in evaluated.bound_box)
    if not corners or not all(math.isfinite(c) for p in corners for c in p):
        raise ValueError('invalid bounds')
    low = Vector(tuple(min(p[i] for p in corners) for i in range(3)))
    high = Vector(tuple(max(p[i] for p in corners) for i in range(3)))
    center = (low + high) / 2
    radius = max((p - center).length for p in corners)
    if radius <= 1e-9:
        raise ValueError('zero-size asset bounds')
    source = Path(bpy.data.filepath).resolve() if bpy.data.filepath else None
    before = sha256(source) if source and source.is_file() else None
    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    image_paths = [output / (name + '.png') for name in names]
    manifest_path = output / 'review-manifest.json'
    if any(path.exists() for path in [*image_paths, manifest_path]):
        raise FileExistsError('review outputs already exist; choose a new version directory')

    scene = bpy.data.scenes.new('MODEL_REVIEW_TEMP')
    scene.collection.children.link(collection)
    try:
        scene.frame_set(source_scene.frame_current)
        scene.render.engine = 'CYCLES'
        scene.cycles.device = 'CPU'
        scene.cycles.samples = args.samples
        scene.cycles.use_denoising = True
        scene.render.resolution_x = scene.render.resolution_y = args.resolution
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = 'PNG'
        scene.render.image_settings.color_mode = 'RGBA'
        scene.render.film_transparent = False
        # Explicit review setup, not color-matched final lookdev.
        scene.view_settings.view_transform = 'Standard'
        scene.view_settings.look = 'None'
        scene.view_settings.exposure = 0
        scene.view_settings.gamma = 1
        world = bpy.data.worlds.new('MODEL_REVIEW_WORLD')
        world.use_nodes = True
        world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.065, 0.065, 0.065, 1)
        world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.35
        scene.world = world
        if args.mode == 'clay':
            material = bpy.data.materials.new('MODEL_REVIEW_CLAY')
            material.use_nodes = True
            shader = material.node_tree.nodes.get('Principled BSDF')
            shader.inputs['Base Color'].default_value = (0.46, 0.46, 0.46, 1)
            shader.inputs['Roughness'].default_value = 0.62
            scene.view_layers[0].material_override = material
        camera_data = bpy.data.cameras.new('MODEL_REVIEW_CAMERA')
        camera = bpy.data.objects.new('MODEL_REVIEW_CAMERA', camera_data)
        scene.collection.objects.link(camera)
        scene.camera = camera
        camera_data.clip_start = max(radius * 0.001, 1e-6)
        camera_data.clip_end = radius * 100
        camera_data.lens = 50
        camera_data.sensor_fit = 'HORIZONTAL'
        camera_data.sensor_width = 36

        lights = []
        for index, relative in enumerate(((2, -3, 4), (-3, -1, 2), (0, 3, 3))):
            data = bpy.data.lights.new(f'MODEL_REVIEW_LIGHT_{index}', 'AREA')
            light = bpy.data.objects.new(data.name, data)
            scene.collection.objects.link(light)
            lights.append((light, Vector(relative).normalized(), (1.0, 0.6, 0.9)[index]))

        files = []
        for name, path in zip(names, image_paths):
            direction = Vector(VIEWS[name]).normalized()
            rotation = (-direction).to_track_quat('-Z', 'Y')
            camera.rotation_euler = rotation.to_euler()
            camera_data.type = 'PERSP' if name.startswith('three_quarter') else 'ORTHO'
            camera_data.ortho_scale = radius * 2.3
            # Fit a bounding sphere; unlike width-only fitting this protects long diagonals.
            distance = radius / math.sin(camera_data.angle_x / 2) * 1.15
            camera.location = center + direction * distance
            for light, relative, strength in lights:
                light.location = center + rotation @ relative * radius * 4
                light.rotation_euler = (center - light.location).to_track_quat('-Z', 'Y').to_euler()
                light.data.energy = 70 * radius * radius * strength
                light.data.shape = 'DISK'
                light.data.size = radius * 3
            scene.render.filepath = str(path)
            bpy.ops.render.render(write_still=True, scene=scene.name)
            if not path.is_file() or not path.stat().st_size:
                raise RuntimeError(f'render produced no image: {path}')
            files.append({'path': path.name, 'view': name, 'mode': args.mode,
                          'sha256': sha256(path), 'projection': camera_data.type})
    finally:
        # No save operation is performed, even on render failure.
        bpy.data.scenes.remove(scene)
    after = sha256(source) if before else None
    if before != after:
        raise RuntimeError('input blend file changed during review')
    record = {'schema_version': 1, 'kind': 'blender-review-images',
              'source': str(source) if source else None, 'source_sha256': before,
              'source_unchanged': before == after, 'blender_version': bpy.app.version_string,
              'frame': source_scene.frame_current, 'collection': args.collection,
              'resolution': args.resolution, 'samples': args.samples,
              'visual_review_status': 'pending', 'files': files,
              'limitations': ['not_final_lighting_or_color_match', 'not_wireframe',
                              'not_turntable_or_deformation_test', 'viewport_bounds_only',
                              'dependencies_outside_collection_may_differ',
                              'collection_instances_hair_volumes_not_supported']}
    temporary = manifest_path.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temporary, manifest_path)
    print(f'REVIEW IMAGES {len(files)} visual_review=pending output={output}', flush=True)


if __name__ == '__main__':
    main()
