---
name: blender-scene
description: Plan, build, animate and render a 3D scene in Blender through the Blender tools. Use when a message starts with /plan build, or asks to add, build, animate, render or import something in the scene.
---

# blender-scene

The steps, in order. Each one leaves something a reader can check.

1. Take the scene as a /plan message. If it did not arrive as one, ask the user to send it as /plan.
2. In plan mode, read fixtures/scene_brief.md if it exists and ask the user what you need to know. Write PLAN.md: the objects, each built from primitives (cubes, cylinders, spheres, cones, planes), the one camera and one light, the motion, and the frame range. Two to five seconds at 24 frames a second.
3. Wait for the user to type approve. Build nothing before that.
4. Build one object or one motion per execute_blender_code script. Keep each script short; a long one is cut off on its way back. Every path you hand Blender is absolute, from the workspace root: Blender resolves a relative path against its own folder and says nothing.
5. After each script, save the scene to scene/scene.blend. The Blender window shows the result; say what changed in one line.
6. When the user asks to see the scene, render a still: engine BLENDER_WORKBENCH, 640 x 360, PNG to scene/still.png.
7. Animate with keyframes on separate objects. Never join moving parts into one mesh; the grader reads motion per object.
8. When the user asks for the render: engine BLENDER_WORKBENCH, 640 x 360, one PNG per frame into scene/frames/ (file path scene/frames/f_####), the full frame range. Then join the frames with the installed ffmpeg into scene/scene.mp4, 24 frames a second, H.264, yuv420p, through a short Python file run with execute. Nothing is written anywhere else.
9. Write transcript.md: the /plan message, your questions and the answers, PLAN.md, the approve, every Blender call in order, and where the still and the render landed.
