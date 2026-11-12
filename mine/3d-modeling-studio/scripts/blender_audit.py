#!/usr/bin/env python3
"""Read-only mesh/texture screening inside Blender; see execution-and-delivery.md."""

import argparse
from array import array
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import bpy


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--collection', help='Restrict to this collection and its children')
    parser.add_argument('--closed-solid', action='store_true')
    parser.add_argument('--require-uv', action='store_true')
    parser.add_argument('--max-triangles', type=int, default=0, help='0 means no budget set')
    parser.add_argument('--area-epsilon', type=float, default=1e-12,
                        help='Degenerate face threshold, local Blender units squared')
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    args = parser.parse_args(argv)
    if args.max_triangles < 0 or not math.isfinite(args.area_epsilon) or args.area_epsilon < 0:
        parser.error('budgets and epsilon must be finite and nonnegative')
    return args


def digest(path):
    with open(path, 'rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def metrics(mesh, matrix, epsilon):
    usage = array('I', [0]) * len(mesh.edges)
    used_vertices = bytearray(len(mesh.vertices))
    bad_coordinates = 0
    world_min = [float('inf')] * 3
    world_max = [-float('inf')] * 3
    for vertex in mesh.vertices:
        world = matrix @ vertex.co
        if not all(math.isfinite(c) for c in (*vertex.co, *world)):
            bad_coordinates += 1
            continue
        for axis in range(3):
            world_min[axis] = min(world_min[axis], world[axis])
            world_max[axis] = max(world_max[axis], world[axis])
    degenerate = triangles = 0
    for face in mesh.polygons:
        triangles += max(0, len(face.vertices) - 2)
        if not math.isfinite(face.area) or face.area <= epsilon:
            degenerate += 1
        for vertex_index in face.vertices:
            used_vertices[vertex_index] = 1
        for loop_index in face.loop_indices:
            usage[mesh.loops[loop_index].edge_index] += 1
    return {
        'vertices': len(mesh.vertices), 'edges': len(mesh.edges),
        'faces': len(mesh.polygons), 'triangles': triangles,
        'triangle_count_method': 'sum(max(face_vertex_count - 2, 0))',
        'nonfinite_vertices': bad_coordinates,
        'boundary_edges': sum(n == 1 for n in usage),
        'edges_over_two_faces': sum(n > 2 for n in usage),
        'loose_edges': sum(n == 0 for n in usage),
        'vertices_unused_by_faces': used_vertices.count(0),
        'degenerate_faces_local_area': degenerate,
        'uv_layers': [layer.name for layer in mesh.uv_layers],
        'bounds_world': {'min': world_min, 'max': world_max}
        if len(mesh.vertices) > bad_coordinates else None,
    }


def main():
    args = arguments()
    source = Path(bpy.data.filepath).resolve() if bpy.data.filepath else None
    output = Path(args.output).resolve()
    if source and output == source:
        raise ValueError('report output must differ from the input blend file')
    before = digest(source) if source and source.is_file() else None
    report = {
        'schema_version': 1, 'kind': 'blender-mesh-audit',
        'blender_version': bpy.app.version_string,
        'source': str(source) if source else None, 'source_sha256': before,
        'units': {'system': bpy.context.scene.unit_settings.system,
                  'scale_length': bpy.context.scene.unit_settings.scale_length},
        'scope': 'current view layer; original MESH objects; viewport evaluation',
        'collection': args.collection, 'objects': [], 'issues': [],
        'not_checked': ['self_intersection', 'vertex_manifoldness', 'wall_thickness',
                        'uv_overlap_or_distortion', 'deformation', 'artistic_quality',
                        'render_subdivision', 'instances', 'non_mesh_geometry',
                        'non_image_dependencies'],
    }

    def issue(severity, code, obj=None, **extra):
        report['issues'].append({'severity': severity, 'code': code, 'object': obj, **extra})

    if args.collection:
        collection = bpy.data.collections.get(args.collection)
        if collection is None:
            raise ValueError(f'collection does not exist: {args.collection}')
        allowed = {obj.name for obj in collection.all_objects}
    else:
        allowed = None
    objects = [obj for obj in bpy.context.view_layer.objects
               if obj.type == 'MESH' and (allowed is None or obj.name in allowed)]
    if not objects:
        issue('error', 'no_mesh_objects')
    depsgraph = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in sorted(objects, key=lambda item: item.name):
        base = metrics(obj.data, obj.matrix_world, args.area_epsilon)
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
        if mesh is None:
            issue('error', 'evaluation_produced_no_mesh', obj.name)
            continue
        try:
            result = metrics(mesh, evaluated.matrix_world, args.area_epsilon)
        finally:
            evaluated.to_mesh_clear()
        determinant = obj.matrix_world.determinant()
        record = {'name': obj.name, 'base': base, 'evaluated': result,
                  'matrix_determinant': determinant if math.isfinite(determinant) else None,
                  'modifiers': [{'name': m.name, 'type': m.type,
                                 'viewport': m.show_viewport, 'render': m.show_render}
                                for m in obj.modifiers]}
        report['objects'].append(record)
        total += result['triangles']
        if not math.isfinite(determinant) or abs(determinant) < 1e-15:
            issue('error', 'singular_or_nonfinite_transform', obj.name)
        elif determinant < 0:
            issue('warning', 'mirrored_transform_check_normals', obj.name)
        for stage, stats in (('base', base), ('evaluated', result)):
            if not stats['faces']:
                issue('warning' if stage == 'base' and result['faces'] else 'error',
                      'empty_mesh', obj.name, stage=stage)
            for field in ('nonfinite_vertices', 'degenerate_faces_local_area'):
                if stats[field]:
                    issue('error', field, obj.name, stage=stage, count=stats[field])
            for field in ('boundary_edges', 'edges_over_two_faces', 'loose_edges',
                          'vertices_unused_by_faces'):
                if stats[field]:
                    issue('error' if args.closed_solid else 'warning', field,
                          obj.name, stage=stage, count=stats[field])
            if not stats['uv_layers']:
                issue('error' if args.require_uv else 'warning', 'no_uv_layer',
                      obj.name, stage=stage)
    if args.max_triangles and total > args.max_triangles:
        issue('error', 'triangle_budget_exceeded', actual=total, maximum=args.max_triangles)

    # Conservative scene-wide image check, not a claim of complete dependency traversal.
    for image in bpy.data.images:
        if image.source == 'VIEWER' or image.type == 'RENDER_RESULT':
            continue
        if image.packed_file or len(getattr(image, 'packed_files', [])):
            continue
        if image.source == 'GENERATED':
            continue
        if image.source != 'FILE' or '<UDIM>' in image.filepath or '<UVTILE>' in image.filepath:
            issue('warning', 'image_sequence_or_tiles_need_manual_check', image.name)
            continue
        resolved = bpy.path.abspath(image.filepath, library=image.library)
        if not resolved or not Path(resolved).is_file():
            issue('error', 'missing_image', image.name, path=resolved)

    after = digest(source) if before else None
    if before != after:
        issue('error', 'source_file_changed_during_audit')
    report['source_unchanged'] = before == after
    report['evaluated_triangle_total'] = total
    report['status'] = 'fail' if any(i['severity'] == 'error' for i in report['issues']) else 'pass'
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + '.tmp')
    temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + '\n',
                         encoding='utf-8')
    os.replace(temporary, output)
    print(f'AUDIT {report["status"].upper()} objects={len(report["objects"])} '
          f'triangles={total} issues={len(report["issues"])} output={output}', flush=True)
    if report['status'] == 'fail':
        raise RuntimeError('mesh audit found errors; read the JSON report')


if __name__ == '__main__':
    main()
