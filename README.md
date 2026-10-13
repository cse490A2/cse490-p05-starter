# Project 5 starter: the codespace

Everything for the build lives in this codespace: Blender, its server, the LiteLLM chat in VS
Code, and a place for your agent. Your laptop runs nothing else.

## What is here

| file | what it is |
|---|---|
| ASSIGNMENT.md | the handout, the same text as Canvas; the editor opens it on every start |
| RULES.md | the Blender server: how to start it, its tools, and the two kinds of call your gate refuses |
| skills/blender-scene/SKILL.md | the skill your agent follows to plan, build, animate and render a scene |
| fixtures/scene_brief.md | a page for the scene you invent; fill it in before you /plan |
| .vscode/mcp.json | the same server for VS Code's own MCP support, the fallback named in the handout |
| checker.py | your copy of the grader's checks; writes the submission bundle to submission/ |
| smoke.sh | tells you whether the codespace is ready |

## Where your agent goes

Clone your Project 4 harness repo into this workspace, in its own folder, and copy skills/ from
here into it. Your agent runs from that folder; its trace.jsonl, PLAN.md and transcript.md land
there, and checker.py finds them. The codespace already holds your course key and the gateway
address in the environment, so the harness runs without a .env file.

## Every open arranges the screen

ASSIGNMENT.md on the left, Blender's window beside it, the chat on the right, the terminal
below. Lost it? F1, then "CSE 490: Arrange the workspace". The window is the codespace desktop
on port 6080; if the tab is blank, open the Ports tab, right-click 6080, Preview in Editor
(password vscode).

The handout in Canvas is the assignment. This file is only the map.
