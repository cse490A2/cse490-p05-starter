# Spec: teach the harness the wire

Hand this file to Claude Code together with your `harness.py` from Project 3.
It describes what the harness must do afterward. Claude Code writes the code.

Work on a copy: leave `harness/harness.py` exactly as it came from Project 3, copy it
to `harness/harness_mcp.py`, and make every change below in the copy. The student
keeps the original to compare against, and the grader reads the difference.

## What changes

The harness keeps its shape from week three: assemble context, call the model,
parse the reply, run a tool, record the result, stop at the turn cap. One thing
is new: some of its tools now come from an MCP server instead of from its own
tool dict.

## Connecting to a server

- Use the official Python SDK, package `mcp` (version 2 or later, already in
  `requirements.txt`). Start the server over stdio with the same command
  `.mcp.json` uses: `uvx blender-mcp==1.9.1`, with the environment variables
  `BLENDER_MCP_SAFE_MODE=1` and `BLENDER_MCP_DISABLE_TELEMETRY=true`.
- At startup, ask the server for its tools (`list_tools`). Each tool has a
  `name`, a `description`, and an `input_schema` (older examples call it
  `inputSchema`; that name no longer exists in the current SDK). Turn each one
  into a tool definition in the format the model API expects, and add them to
  the tools the model is offered.
- When the model calls one of them, forward it to the server (`call_tool`) and
  hand the result text back to the model as the tool result, the same way the
  harness already does for its own tools.

- Keep the whole run inside one async context: start the server, open the session,
  and run every turn within it. Entering the client and the session by hand from a
  separate loop closes the transport on the first call (a first-try failure seen in
  the dry run).

## The gate stays in front of every call

The week-three gate runs before any tool call, server tools included. It
checks a file path, and the server's tools carry none, so as written it refuses
every one of them. Replace its decision with the one the student wrote in
`hooks/gate.py`: import `offends` from that file and call it with the tool's
name and arguments before every server call; a non-empty return is the refusal
reason. The same function is the hook Claude Code runs, so both clients obey
one rule. A refusal is a normal tool result that says why; the model reads it
and moves on. The forbidden-tool names are listed in `RULES.md`.

## The trace

Every event lands in `harness/trace.jsonl`, one JSON object per line, as in
week three. New event kinds:

    {"event": "tools_listed", "server": "blender", "tools": ["get_scene_info", ...]}
    {"event": "tool_call", "tool": "...", "args": {...}, "result": "..."}
    {"event": "refused", "tool": "...", "reason": "..."}

## Settings that save you time

- The harness's model this week is `internal/Qwen3.6-35B-A3B` through the course
  gateway, in place of week three's. Read it from the `HARNESS_MODEL` environment
  variable, which the codespace sets, with that name as the fallback. It is the course's
  own hosted model: the harness re-sends the whole conversation every turn, and this one
  draws on no budget; it places a torus as well as any of them. Any other name from the
  gateway's list works too: ask `GET /v1/models` with your key, and set `HARNESS_MODEL`
  to the name exactly as listed, prefix included. Qwen returns a `reasoning_content`
  field beside each reply; ignore it. Claude Code keeps its own model, and `/model` with
  any listed name switches it.
- Ask the gateway for up to 8192 output tokens per reply. The default cuts a
  long Blender script in half.
- Retry a call once on an HTTP 502; the gateway drops single replies that run
  past about three minutes.
- Put one line in the system prompt: build in small steps, one object or one
  motion per script.
