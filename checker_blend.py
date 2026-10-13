# Runs inside Blender, headless:  blender -b scene/scene.blend --python checker_blend.py
# Prints one JSON line describing the scene. checker.py reads it. Nothing here is a
# verdict; the verdicts are in checker.py so their wording lives in one place.
import json
import sys

import bpy

scene = bpy.context.scene
fps = scene.render.fps / scene.render.fps_base
first, last = scene.frame_start, scene.frame_end
geometry = [o for o in bpy.data.objects if o.type in {"MESH", "CURVE", "FONT", "SURFACE", "META"}]
cameras = [o for o in bpy.data.objects if o.type == "CAMERA"]
lights = [o for o in bpy.data.objects if o.type == "LIGHT"]


def is_ground(o):
    if o.type != "MESH" or not o.data:
        return False
    name = o.name.lower()
    if any(k in name for k in ("ground", "floor", "plane", "terrain", "road", "sand")):
        return True
    dims = o.dimensions
    return dims.z < 0.05 * max(dims.x, dims.y, 1e-6)


def snapshot(frame):
    scene.frame_set(frame)
    out = {}
    for o in bpy.data.objects:
        m = o.matrix_world
        out[o.name] = {
            "loc": [round(v, 4) for v in m.to_translation()],
            "rot": [round(v, 4) for v in m.to_euler()],
        }
    return out


a, b = snapshot(first), snapshot(last)
moved = [n for n in a if a[n]["loc"] != b[n]["loc"]]
turned = [n for n in a if a[n]["rot"] != b[n]["rot"]]

report = {
    "fps": fps,
    "frame_start": first,
    "frame_end": last,
    "span_seconds": round((last - first) / fps, 3) if fps else None,
    "engine": scene.render.engine,
    "resolution": [scene.render.resolution_x, scene.render.resolution_y],
    "geometry_objects": [o.name for o in geometry if not is_ground(o)],
    "ground_objects": [o.name for o in geometry if is_ground(o)],
    "cameras": [o.name for o in cameras],
    "lights": [o.name for o in lights],
    "moved": moved,
    "turned": turned,
    "all_objects": sorted(o.name for o in bpy.data.objects),
}
sys.stdout.write("BLENDPROBE " + json.dumps(report) + "\n")
sys.stdout.flush()
