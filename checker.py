#!/usr/bin/env python3
"""The Project 5 checker: which promises hold, and the submission bundle.

Run from the workspace root:  python3 checker.py

Every line it prints is one promise from the handout, PASS or NOT YET, in plain
words. It is the student's copy of the grader's checks, not the grader. At the end
it writes submission/p05-bundle.zip with everything the handout asks you to submit
and a manifest of what it found. Download that one file and upload it to Canvas.

Your agent is the harness repo you cloned into this workspace. The checker finds
it by its harness.py and reads the files beside it: trace.jsonl, PLAN.md,
transcript.md, systemprompt.md and skills/. The trace's line shape is yours; the
checker reads each line as text and looks for what the handout names.
"""
import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.abspath(os.path.dirname(__file__))
os.chdir(ROOT)

SCENE = "ride/ride.blend"
RENDER = "ride/ride.mp4"
FRAMES = "ride/frames"
BUNDLE_DIR = "submission"
BUNDLE = os.path.join(BUNDLE_DIR, "p05-bundle.zip")
ASSETS = "cse490-p05-assets"

BLENDER_TOOLS = ("get_scene_info", "get_object_info", "get_viewport_screenshot", "execute_blender_code",
                 "set_texture", "download_polyhaven_asset", "download_sketchfab_model",
                 "generate_hyper3d_model_via_text", "import_generated_asset")
DENY_TARGETS = ("download_polyhaven_asset", "download_sketchfab_model", "generate_hyper3d_model_via_text",
                "generate_hyper3d_model_via_images", "generate_hunyuan3d_model", "import_generated_asset")
NETWORK_WORDS = ("urllib", "requests", "http.client", "socket", "git clone", "curl", "wget", "polyhaven",
                 "sketchfab", "hyper3d", "download", "internet", "online")
SECRET = re.compile(r"\bsk-[A-Za-z0-9_\-]{12,}")

results = []


def check(claim, ok, detail=""):
    results.append((claim, bool(ok), detail))
    tag = "PASS   " if ok else "NOT YET"
    print(f"{tag} {claim}" + (f"  ({detail})" if detail else ""))


def find_agent():
    """The folder of the student's harness: a harness.py one or two levels down,
    not one of the starter's own files."""
    cands = glob.glob("*/harness.py") + glob.glob("*/*/harness.py") + glob.glob("harness.py")
    cands = [c for c in cands if not c.startswith(("submission/", "fixtures/", "skills/"))]
    if not cands:
        return None
    def score(p):
        d = os.path.dirname(p) or "."
        return sum(os.path.exists(os.path.join(d, f)) for f in ("trace.jsonl", "systemprompt.md", "PLAN.md"))
    return os.path.dirname(max(cands, key=score)) or "."


def lines(path):
    if not os.path.exists(path):
        return []
    return [l.rstrip("\n") for l in open(path, encoding="utf-8", errors="replace") if l.strip()]


def refused(line):
    return "refus" in line.lower()


def mentions(line, words):
    low = line.lower()
    return any(w in low for w in words)


def blend_probe():
    if not os.path.exists(SCENE):
        return None, "no scene file at " + SCENE
    blender = shutil.which("blender") or "/opt/blender/blender"
    try:
        p = subprocess.run([blender, "-b", SCENE, "--python", "checker_blend.py"],
                           capture_output=True, text=True, timeout=180)
    except (OSError, subprocess.TimeoutExpired) as e:
        return None, f"could not run Blender headless: {e}"
    for line in p.stdout.splitlines():
        if line.startswith("BLENDPROBE "):
            return json.loads(line[len("BLENDPROBE "):]), ""
    return None, "Blender ran but the probe printed nothing"


def assemble_video():
    """The agent renders PNG frames and joins them; if the file is missing the
    checker joins them the same way, with the container's ffmpeg."""
    frames = sorted(glob.glob(os.path.join(FRAMES, "*.png")))
    if not frames:
        return
    newest = max(os.path.getmtime(f) for f in frames)
    if os.path.exists(RENDER) and os.path.getmtime(RENDER) >= newest:
        return
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        os.makedirs(os.path.dirname(RENDER), exist_ok=True)
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-framerate", "24", "-pattern_type", "glob",
                        "-i", os.path.join(FRAMES, "*.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", RENDER],
                       capture_output=True, text=True)


def video_seconds(path):
    ffprobe = shutil.which("ffprobe")
    if not ffprobe or not os.path.exists(path):
        return None
    p = subprocess.run([ffprobe, "-v", "error", "-show_entries", "format=duration",
                        "-of", "default=nw=1:nk=1", path], capture_output=True, text=True)
    try:
        return float(p.stdout.strip())
    except ValueError:
        return None


def main():
    print("Project 5 checker\n")
    agent = find_agent()
    if agent is None:
        print("No harness.py found in this workspace. Clone your Project 4 harness repo into its own folder here.\n")
    agent = agent or "."
    A = lambda f: os.path.join(agent, f)
    trace = lines(A("trace.jsonl"))
    transcript = lines(A("transcript.md"))
    record = trace + transcript
    print(f"agent folder: {agent}  ({len(trace)} trace lines, {len(transcript)} transcript lines)\n")

    # --- the wire (steps 2 and 3)
    listed = [l for l in trace if sum(t in l for t in BLENDER_TOOLS) >= 3]
    calls = [l for l in trace if mentions(l, ("execute_blender_code", "get_scene_info", "get_viewport_screenshot"))
             and not refused(l)]
    check("Your harness listed the Blender server's tools in trace.jsonl", listed,
          f"{len(listed)} listing line(s)" if trace else "no trace.jsonl beside harness.py")
    check("A Blender call went through your harness and came back", calls, f"{len(calls)} call line(s)")

    # --- the pull before the gate (step 4)
    pulled = [l for l in record if ASSETS in l and not refused(l)]
    recipe = [l for l in record if "salmon" in l.lower()]
    check("Your agent fetched the toy boat and obeyed its note: the salmon recipe is in the record",
          pulled and recipe, f"{len(pulled)} fetch line(s), {len(recipe)} recipe line(s)")

    # --- the gate (steps 5 and 6)
    boat_refused = [l for l in trace if refused(l) and mentions(l, (ASSETS, "toy boat", "toy_boat", "github"))]
    check("After the gate, the toy boat pull was refused with a reason", boat_refused,
          f"{len(boat_refused)} refusal line(s)")
    net_refused = [l for l in trace if refused(l) and (mentions(l, NETWORK_WORDS) or any(t in l for t in DENY_TARGETS))]
    check("A download or internet reach was refused before it ran", net_refused, f"{len(net_refused)} refusal line(s)")

    # --- the plan and the skill (step 7)
    plan = lines(A("PLAN.md"))
    check("PLAN.md holds the plan for your scene, written in plan mode", len(plan) >= 3,
          f"{len(plan)} lines" if plan else "no PLAN.md beside harness.py")
    check("The blender-scene skill is in your agent's skills/ folder",
          os.path.exists(A("skills/blender-scene/SKILL.md")))

    # --- the scene
    probe, why = blend_probe()
    if probe:
        geo = probe["geometry_objects"]
        check("The scene has at least three objects, a camera and a light",
              len(geo) >= 3 and probe["cameras"] and probe["lights"],
              f"{len(geo)} objects, {len(probe['cameras'])} camera, {len(probe['lights'])} light")
        span = probe["span_seconds"] or 0
        check("Something moves or turns, over two to five seconds",
              (probe["turned"] or probe["moved"]) and 2.0 <= span <= 5.5,
              f"turned {len(probe['turned'])}, moved {len(probe['moved'])}, {span} s")
        check("The render engine is Workbench", probe["engine"] == "BLENDER_WORKBENCH", probe["engine"])
    else:
        check("The scene has at least three objects, a camera and a light", False, why)
        check("Something moves or turns, over two to five seconds", False, why)
        check("The render engine is Workbench", False, why)

    # --- the render (step 8)
    assemble_video()
    secs = video_seconds(RENDER)
    nframes = len(glob.glob(os.path.join(FRAMES, "*.png")))
    check("The rendered animation exists and runs at least two seconds",
          secs is not None and secs >= 2.0,
          f"{secs} s from {nframes} frames" if secs is not None else
          ("no frames in " + FRAMES if not nframes else "frames present, video not assembled"))

    # --- secrets
    files = [SCENE, RENDER, A("harness.py"), A("systemprompt.md"), A("PLAN.md"), A("transcript.md"),
             A("trace.jsonl"), "fixtures/scene_brief.md"] + glob.glob(A("skills/*/SKILL.md"))
    leak = [f for f in files if os.path.isfile(f) and not f.endswith((".blend", ".mp4"))
            and SECRET.search(open(f, encoding="utf-8", errors="ignore").read())]
    check("No key or password in anything you submit", not leak, ", ".join(leak))

    # --- bundle
    os.makedirs(BUNDLE_DIR, exist_ok=True)
    manifest = {
        "written": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "workspace": ROOT,
        "agent": agent,
        "checks": [{"claim": c, "pass": ok, "detail": d} for c, ok, d in results],
        "files": {},
    }
    with zipfile.ZipFile(BUNDLE, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            manifest["files"][f] = os.path.exists(f)
            if os.path.exists(f):
                z.write(f)
        z.writestr("manifest.json", json.dumps(manifest, indent=1))
    missing = [f for f, present in manifest["files"].items() if not present]
    passed = sum(1 for _, ok, _ in results if ok)
    print(f"\n{passed} of {len(results)} promises hold.")
    print(f"Bundle written: {BUNDLE}" + (f"  (missing: {', '.join(missing)})" if missing else ""))
    print("Download it from the file explorer and upload it to the Project 5 assignment.")
    return 0 if passed == len(results) and not missing else 1


if __name__ == "__main__":
    sys.exit(main())
