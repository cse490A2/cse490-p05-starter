# The Blender server, and what the gate refuses

## The server

The server is `blender-mcp` 1.9.1, started over stdio with this command and environment:

    uvx blender-mcp==1.9.1
    BLENDER_MCP_SAFE_MODE=1  BLENDER_MCP_DISABLE_TELEMETRY=true  BLENDER_HOST=localhost  BLENDER_PORT=9876

It talks to the Blender window already running in this codespace. Safe mode and telemetry-off
stay on; the grader checks both.

The Python SDK is the `mcp` package (version 2, already installed). The pieces the harness needs:
`stdio_client` to start the server, `ClientSession` on its streams, `list_tools` for the tool
list, `call_tool` to run one. Each listed tool has a `name`, a `description` and an
`inputSchema`; turn each into a tool definition in the shape the model API already takes and add
it beside read_file, write_file and execute. A call's result text goes back to the model as a
tool result, the same way the harness's own tools do. Keep the whole run inside one async
context: start the server, open the session, and run every turn within it. Opening the client
and the session from a separate loop closes the transport on the first call.

## The tools

What the server lists. The first four build and look; everything below them reaches outside.

    get_scene_info                       read the scene
    get_object_info                      read one object
    get_viewport_screenshot              a picture of the window
    execute_blender_code                 run any Python inside Blender

    set_texture                          pulls a fetched asset in
    get_polyhaven_status                 search_polyhaven_assets
    get_polyhaven_categories             download_polyhaven_asset
    get_sketchfab_status                 search_sketchfab_models
    get_sketchfab_model_preview          download_sketchfab_model
    get_hyper3d_status                   generate_hyper3d_model_via_text
    generate_hyper3d_model_via_images    generate_hunyuan3d_model
    poll_rodin_job_status                import_generated_asset

## What the gate refuses

Two kinds of call, judged before the call runs. The reason is printed and logged to
trace.jsonl; the model reads it as a normal tool result and moves on.

1. By name: every tool in the second group. No tool that brings bytes in from the network.
2. By what it does: a script handed to execute_blender_code, a file handed to execute, or text
   handed to write_file that opens a network connection (urllib, requests, http.client, socket,
   git, curl, wget), turns Blender's online access on, or saves, exports or renders to a path
   outside this workspace (/tmp, the home folder, a path with ..).

Everything else runs: the four reading and building tools, and any script that builds,
animates, saves or renders inside the workspace.
