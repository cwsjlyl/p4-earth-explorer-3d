"""
Batch entry script for Headless Blender 3D asset generation.
Run with: blender --background --python blender-scripts/build_all.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUT_DIR = os.path.join(PROJECT_ROOT, "public", "models")

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

os.makedirs(OUT_DIR, exist_ok=True)

import gen_earth_cutaway
import gen_drill_pod
import gen_rock_samples


def main():
    print("=== [Blender Pipeline] Building P4 Science 3D Assets ===")
    earth_path = os.path.join(OUT_DIR, "earth_cutaway.glb")
    pod_path = os.path.join(OUT_DIR, "drill_pod.glb")
    rocks_path = os.path.join(OUT_DIR, "rock_samples.glb")

    gen_earth_cutaway.build(earth_path)
    gen_drill_pod.build(pod_path)
    gen_rock_samples.build(rocks_path)

    for p in (earth_path, pod_path, rocks_path):
        size_kb = os.path.getsize(p) / 1024.0
        print(f"[OK] Generated {os.path.basename(p)} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
