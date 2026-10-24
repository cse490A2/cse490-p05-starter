# Project 5 starter

Everything for the build lives here: Blender, its MCP server, the LiteLLM chat in VS Code,
the OpenCode CLI, and a place for your agent. In a codespace it is all installed; on your
laptop, RULES.md says what to install.

## What is here

| file | what it is |
|---|---|
| ASSIGNMENT.md | the handout, the same text as Canvas; the editor opens it on every start |
| RULES.md | the Blender server: how to start it, in the codespace or on your laptop, and its tools |
| skills/blender-scene/SKILL.md | the skill your agent follows to plan, build, animate and render a scene |
| fixtures/scene_brief.md | a page for the scene you invent; fill it in before you /plan |
| .vscode/mcp.json | the same server for VS Code's own MCP support |
| checker.py | your copy of the grader's checks; writes the submission bundle to submission/ |
| smoke.sh | tells you whether the codespace is ready |

## Where your agent goes

Clone your Project 4 harness repo into this workspace, in its own folder, and copy skills/ from
here into it. Your agent runs from that folder; its trace.jsonl and transcript.md land there,
and checker.py finds them. The codespace already holds your course key and the gateway
address in the environment, so the harness runs without a .env file. The harness model is
Sonnet 5 (HARNESS_MODEL in the environment).

## Part 1, Part 2, Part 3

Part 1 is your harness's work: it gains the Blender tools, passes the server's pictures back to
the model as images, builds your animation and renders it into part1/. Part 2 is OpenCode's:
`opencode` in the terminal starts the OpenCode CLI. Setup pointed it at DeepSeek V4.1 Flash on
the UW Purple API when the PURPLE_API_KEY secret exists, and at the course gateway otherwise,
and at the same Blender server your harness uses. Stop your harness (Ctrl+C) before you start
OpenCode: Blender takes one connection at a time. OpenCode renders into part2/. Part 3 is
optional: your own CLI agent with the Blender server from RULES.md added to its MCP
configuration, into part3/ if you want it in the bundle.

checker.py bundles trace.jsonl, every part's scene.mp4, and OpenCode's record of the build
(its session, exported as JSON) and tells you which of the handout's promises hold.

## Every open arranges the screen

ASSIGNMENT.md on the left, Blender's window beside it, the chat on the right, the terminal
below. Lost it? F1, then "CSE 490: Arrange the workspace". The window is the codespace desktop
on port 6080; if the tab is blank, open the Ports tab, right-click 6080, Preview in Editor
(password vscode).

The handout in Canvas is the assignment. This file is only the map.
