#!/usr/bin/env python3
"""The Project 5 checker: which promises hold, and the submission bundle.

Run from the workspace root:  python3 checker.py

Every line it prints is one promise from the handout, PASS or NOT YET, in plain
words. It is the student's copy of the grader's checks, not the grader. At the end
it writes submission/p05-bundle.zip with everything the handout asks you to submit
and a manifest of what it found. Download that one file and upload it to Canvas.

Part 1 is your harness's work. The checker finds your agent by its harness.py and
reads the files beside it: trace.jsonl, transcript.md, systemprompt.md and skills/.
The trace's line shape is yours; the checker reads each line as text and looks for
what the handout names. The Part 1 render lands in part1/.

Part 2 is OpenCode's work, and OpenCode keeps its own record: its sessions live in
~/.local/share/opencode/opencode.db. The newest session that mentions Blender is
exported with `opencode export <id>` into opencode_session.json beside this file,
and the checks read that copy. The Part 2 render lands in part2/. A Part 3 render,
if you made one, lands in part3/ and rides along in the bundle.
"""
import datetime
import glob
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import zipfile

ROOT = os.path.abspath(os.path.dirname(__file__))
os.chdir(ROOT)

PARTS = ("part1", "part2")                      # graded
EXTRA = sorted(set(os.path.dirname(p) for p in glob.glob("part*/scene.mp4")) - set(PARTS))
BUNDLE_DIR = "submission"
BUNDLE = os.path.join(BUNDLE_DIR, "p05-bundle.zip")
OPENCODE_DB = os.path.expanduser("~/.local/share/opencode/opencode.db")
OPENCODE_COPY = "opencode_session.json"
MIN_FRAMES = 24                                 # one second at 24 frames a second

BLENDER_TOOLS = ("get_scene_info", "get_object_info", "get_viewport_screenshot", "execute_blender_code",
                 "set_texture", "download_polyhaven_asset", "download_sketchfab_model",
                 "generate_hyper3d_model_via_text", "import_generated_asset")
BUILD_TOOLS = ("execute_blender_code", "get_scene_info", "get_viewport_screenshot", "get_object_info")
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
        return sum(os.path.exists(os.path.join(d, f)) for f in ("trace.jsonl", "systemprompt.md", "transcript.md"))
    return os.path.dirname(max(cands, key=score)) or "."


def lines(path):
    if not os.path.exists(path):
        return []
    return [l.rstrip("\n") for l in open(path, encoding="utf-8", errors="replace") if l.strip()]


def mentions(line, words):
    low = line.lower()
    return any(w in low for w in words)


# --- OpenCode's record

def opencode_session():
    """The newest OpenCode session whose parts mention Blender, exported as JSON into
    OPENCODE_COPY. Returns (path or None, why)."""
    if os.path.exists(OPENCODE_COPY) and not os.path.exists(OPENCODE_DB):
        return OPENCODE_COPY, "kept the copy already here"
    if not os.path.exists(OPENCODE_DB):
        return None, "no OpenCode database at " + OPENCODE_DB
    try:
        db = sqlite3.connect(f"file:{OPENCODE_DB}?mode=ro", uri=True)
        rows = db.execute(
            "select s.id, max(s.time_updated) from session s join message m on m.session_id = s.id "
            "join part p on p.message_id = m.id where lower(p.data) like '%blender%' "
            "group by s.id order by 2 desc limit 1").fetchall()
        db.close()
    except sqlite3.Error as e:
        return None, f"could not read the OpenCode database: {e}"
    if not rows or not rows[0][0]:
        return None, "no OpenCode session mentions Blender"
    sid = rows[0][0]
    exe = shutil.which("opencode") or os.path.expanduser("~/.opencode/bin/opencode")
    raw = OPENCODE_COPY + ".raw"
    try:
        # the export is written to a file, not a pipe: through a pipe the CLI exits before
        # the last of a long session has been read (truncated at 64 KB, 2026-10-23)
        with open(raw, "w", encoding="utf-8") as out:
            subprocess.run([exe, "export", sid], stdout=out, stderr=subprocess.DEVNULL, timeout=300)
        text = open(raw, encoding="utf-8", errors="replace").read()
        data = json.loads(text[text.find("{"):])
    except (OSError, subprocess.TimeoutExpired, ValueError) as e:
        return None, f"opencode export {sid} failed: {e}"
    finally:
        if os.path.exists(raw):
            os.remove(raw)
    with open(OPENCODE_COPY, "w", encoding="utf-8") as f:
        json.dump(trim(data), f, indent=1)
    return OPENCODE_COPY, sid


def trim(obj, limit=20000):
    """The export carries every tool output in full, screenshots included, tens of
    megabytes for one build. The record keeps every message and part; a string longer
    than the limit is cut and marked, so the grader still reads every call and script."""
    if isinstance(obj, dict):
        return {k: trim(v, limit) for k, v in obj.items()}
    if isinstance(obj, list):
        return [trim(v, limit) for v in obj]
    if isinstance(obj, str) and len(obj) > limit:
        return obj[:limit] + f" ...[cut, {len(obj) - limit} more characters]"
    return obj


def session_parts(path):
    """Every part of every message in the exported session, flattened."""
    try:
        data = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError):
        return {}, []
    info = data.get("info", {}) if isinstance(data, dict) else {}
    parts = []
    for m in (data.get("messages", []) if isinstance(data, dict) else []):
        for part in m.get("parts", []):
            part = dict(part)
            part["_role"] = m.get("info", {}).get("role", "")
            parts.append(part)
    return info, parts


# --- the renders

def assemble_video(part):
    """The agent renders PNG frames and joins them; if the file is missing the
    checker joins them the same way, with the container's ffmpeg."""
    frames = sorted(glob.glob(os.path.join(part, "frames", "*.png")))
    if not frames:
        return
    render = os.path.join(part, "scene.mp4")
    newest = max(os.path.getmtime(f) for f in frames)
    if os.path.exists(render) and os.path.getmtime(render) >= newest:
        return
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-framerate", "24", "-pattern_type", "glob",
                        "-i", os.path.join(part, "frames", "*.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", render],
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


def render_check(part, who):
    assemble_video(part)
    render = os.path.join(part, "scene.mp4")
    nframes = len(glob.glob(os.path.join(part, "frames", "*.png")))
    secs = video_seconds(render)
    have = os.path.exists(render) and os.path.getsize(render) > 0
    ok = have and nframes >= MIN_FRAMES
    detail = (f"{nframes} frames" + (f", {secs:.1f} s" if secs is not None else "")) if have \
        else (f"no {render}; {nframes} frames in {part}/frames" if nframes else f"nothing in {part}/")
    check(f"{who} rendered an animation into {part}/scene.mp4 with at least {MIN_FRAMES} frames", ok, detail)
    return have


def main():
    print("Project 5 checker\n")
    agent = find_agent()
    if agent is None:
        print("No harness.py found in this workspace. Clone your Project 4 harness repo into its own folder here.\n")
    agent = agent or "."
    A = lambda f: os.path.join(agent, f)
    trace = lines(A("trace.jsonl"))
    print(f"agent folder: {agent}  ({len(trace)} trace lines)\n")

    # --- Part 1: the wire, the eyes, the torus
    listed = [l for l in trace if sum(t in l for t in BLENDER_TOOLS) >= 3]
    check("Your harness listed the Blender server's tools in trace.jsonl", listed,
          f"{len(listed)} listing line(s)" if trace else "no trace.jsonl beside harness.py")
    calls = [l for l in trace if mentions(l, BUILD_TOOLS)]
    check("A Blender call went through your harness and came back", calls, f"{len(calls)} call line(s)")
    seen = [l for l in trace if "image" in l.lower() and mentions(l, ("base64", "image_url", "data:image", "image/png"))]
    check("Your harness passed a picture from the Blender server back to the model as an image",
          seen, f"{len(seen)} line(s) carrying an image")
    torus = [l for l in trace if "torus" in l.lower() and mentions(l, ("execute_blender_code", "primitive"))]
    check("A torus was built through a Blender tool call", torus, f"{len(torus)} line(s)")
    part1 = render_check("part1", "Your harness")

    # --- Part 2: OpenCode's record and render
    sess, why = opencode_session()
    info, parts = session_parts(sess) if sess else ({}, [])
    tool_parts = [p for p in parts if p.get("type") == "tool" and mentions(json.dumps(p), BUILD_TOOLS)]
    model = info.get("model", {}) if isinstance(info.get("model"), dict) else {}
    model_note = f"{model.get('id', '?')} on {model.get('providerID', '?')}" if model else ""
    check("OpenCode built a scene through the Blender server, in its own session",
          len(tool_parts) >= 3,
          (f"{len(tool_parts)} Blender tool call(s), {model_note}" if sess else why))
    asked = [p for p in parts if p.get("type") == "text" and p.get("_role") == "user"
             and mentions(p.get("text", ""), ("part2/frames", "scene.mp4", "workbench"))]
    check("The render was asked of OpenCode", asked, f"{len(asked)} line(s)" if sess else why)
    part2 = render_check("part2", "OpenCode")

    # --- two animations, at least
    extras = [os.path.join(p, "scene.mp4") for p in EXTRA if os.path.exists(os.path.join(p, "scene.mp4"))]
    n_anim = int(part1) + int(part2) + len(extras)
    check("At least two animations are in the bundle", n_anim >= 2,
          f"{n_anim} animation(s)" + (f", extra: {', '.join(extras)}" if extras else ""))

    # --- secrets
    files = [A("harness.py"), A("systemprompt.md"), A("transcript.md"), A("trace.jsonl"), OPENCODE_COPY,
             "fixtures/scene_brief.md"] + glob.glob(A("skills/*/SKILL.md")) \
        + [os.path.join(p, "scene.mp4") for p in PARTS] + extras \
        + [os.path.join(p, "still.png") for p in PARTS if os.path.exists(os.path.join(p, "still.png"))]
    leak = [f for f in files if os.path.isfile(f) and not f.endswith((".blend", ".mp4", ".png"))
            and SECRET.search(open(f, encoding="utf-8", errors="ignore").read())]
    check("No key or password in anything you submit", not leak, ", ".join(leak))

    # --- bundle
    os.makedirs(BUNDLE_DIR, exist_ok=True)
    manifest = {
        "written": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "workspace": ROOT,
        "agent": agent,
        "opencode_model": model_note,
        "checks": [{"claim": c, "pass": ok, "detail": d} for c, ok, d in results],
        "files": {},
    }
    with zipfile.ZipFile(BUNDLE, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            manifest["files"][f] = os.path.exists(f)
            if os.path.exists(f):
                z.write(f)
        z.writestr("manifest.json", json.dumps(manifest, indent=1))
    required = [A("trace.jsonl"), OPENCODE_COPY] + [os.path.join(p, "scene.mp4") for p in PARTS]
    missing = [f for f in required if not manifest["files"].get(f)]
    passed = sum(1 for _, ok, _ in results if ok)
    print(f"\n{passed} of {len(results)} promises hold.")
    print(f"Bundle written: {BUNDLE}" + (f"  (missing: {', '.join(missing)})" if missing else ""))
    print("Download it from the file explorer and upload it to the Project 5 assignment.")
    return 0 if passed == len(results) and not missing else 1


if __name__ == "__main__":
    sys.exit(main())
