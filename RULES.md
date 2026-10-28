# The Blender server

## The server

The server is `blender-mcp` 1.9.1, started over stdio with this command and environment:

    uvx blender-mcp==1.9.1
    BLENDER_MCP_SAFE_MODE=1  BLENDER_MCP_DISABLE_TELEMETRY=true  BLENDER_HOST=localhost  BLENDER_PORT=9876

It talks to a running Blender window through the Blender MCP addon's socket on port 9876. In
the codespace the window is already running and the addon is already enabled; `.vscode/mcp.json`
and OpenCode's config carry the same command. Safe mode and telemetry-off stay on.

The Python SDK is the `mcp` package (version 2, already installed). The pieces the harness needs:
`stdio_client` to start the server, `ClientSession` on its streams, `list_tools` for the tool
list, `call_tool` to run one. Each listed tool has a `name`, a `description` and an
`input_schema` (this SDK names its fields in snake_case: `input_schema`, `is_error`, and an image
part's `mime_type` and `data`); turn each into a tool definition in the shape the model API already takes and add
it beside read_file, write_file and execute_file. A call's result goes back to the model as a tool
result, the same way the harness's own tools do. A result may carry an image part, not text:
`get_viewport_screenshot` answers with a PNG of the Blender window. Pass that part to the model
as an image in the shape the model API takes, so the model sees what it built. Keep the whole run
inside one async context: start the server, open the session, and run every turn within it.
Opening the client and the session from a separate loop closes the transport on the first call.

Blender takes one connection at a time: stop the harness before you start OpenCode or your own CLI.

## On your laptop

The same server, the same addon, on your own machine:

1. Install Blender from blender.org (the codespace runs 5.2; any current release works).
2. Install the addon: download `addon.py` from github.com/ahujasid/blender-mcp (the file at
   the top of the repository's main page; there is no Releases page, 1.9.1 is the server's
   version), then in Blender: Edit, Preferences, Add-ons, the arrow at the top right, Install
   from Disk, pick the file, tick it on.
3. Start the socket: press N in the 3D view, open the MCP for Blender tab, click Connect to MCP server.
   Port 9876.
4. Install uv (astral.sh/uv), then the command above starts the server; put it in your
   harness's MCP config and in OpenCode's config the way the codespace's setup.sh does.

Nothing sandboxes an agent on your laptop: it runs with your files and your network. Read what
it asks to run. A path you hand Blender resolves against Blender's own working directory, not your
harness folder: launch Blender from the workspace, or give it absolute paths.

## The tools

What the server lists. The first four build and look; everything below them reaches outside
to fetch or generate assets.

    get_scene_info                       read the scene
    get_object_info                      read one object
    get_viewport_screenshot              a picture of the window, as an image part
    execute_blender_code                 run any Python inside Blender

    set_texture                          pulls a fetched asset in
    get_polyhaven_status                 search_polyhaven_assets
    get_polyhaven_categories             download_polyhaven_asset
    get_sketchfab_status                 search_sketchfab_models
    get_sketchfab_model_preview          download_sketchfab_model
    get_hyper3d_status                   generate_hyper3d_model_via_text
    generate_hyper3d_model_via_images    generate_hunyuan3d_model
    poll_rodin_job_status                import_generated_asset

The build in this project uses the first four: scenes are built from primitives by script.
