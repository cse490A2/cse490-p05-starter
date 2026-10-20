# Project 5 starter: the codespace

Everything for the build lives in this codespace: Blender, its server, the LiteLLM chat in VS
Code, the OpenAI Codex CLI, and a place for your agent. Your laptop runs nothing else.

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
here into it. Your agent runs from that folder; its trace.jsonl and transcript.md land there,
and checker.py finds them. The codespace already holds your course key and the gateway
address in the environment, so the harness runs without a .env file.

## Codex, then your own tools

The torus and the gate are your harness's work. The animation is Codex's: `codex` in the terminal
starts the OpenAI Codex CLI. Setup pointed it at the UW Purple API (endpoint, model and key
pending; the course gateway until then) and at the same Blender server your harness uses, and
`/mcp` inside Codex lists that server. Stop your harness (Ctrl+C) before you start Codex: Blender
takes one connection at a time. The handout's optional section lets a student with a Claude Code
or Codex subscription use it instead, with the Blender server named in RULES.md added to its MCP
configuration. checker.py bundles the newest session file it finds, Codex's or Claude Code's, as
the record of the build.

## Every open arranges the screen

ASSIGNMENT.md on the left, Blender's window beside it, the chat on the right, the terminal
below. Lost it? F1, then "CSE 490: Arrange the workspace". The window is the codespace desktop
on port 6080; if the tab is blank, open the Ports tab, right-click 6080, Preview in Editor
(password vscode).

The handout in Canvas is the assignment. This file is only the map.
