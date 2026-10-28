# Project 5: Building an Animation with MCP

**Due: Tuesday 11:59 pm**
Prerequisites: run the course setup wizard during class.
In this project you will create an awesome animation and learn about MCPs and sandboxes in the process! We've built enough pelicans riding bicycles though, so think about something you want to animate in Part 2 instead – no pelicans riding bicycles please :-). Part 1 builds a set scene, a torus, so the grader can check it. We'll feature some of the most exciting results in class! The project has two parts, and each one ends in an animation built through the Blender MCP server. In Part 1 your Project 4 agent gains Blender's tools over MCP and gains the ability to see images, inside a sandbox hosted on GitHub Codespaces. In Part 2, you hand the same Blender server to an industrial-strength agent, OpenCode with DeepSeek V4.1-flash on the UW Purple API or your own AI subscription's CLI, and build a second animation with Blender in your codespace or installed on your own laptop.

A sandbox is an isolated computing environment where untrusted code, such as code a model generates, can run without affecting the host machine. In this project, the sandbox is GitHub Codespaces: a virtual machine in the cloud in which your harness will run. It doesn't have access to your laptop or any of the files you don't give it. For the harness to 'talk' to Blender, we will use MCP, or Model Context Protocol, a standard created by Anthropic. It consists of the host (what you're interacting with), the server (exposes data and tools), and the client (manages the connection to the server). Blender, the MCP server, and the client all run in your codespace.

## Part 1: your harness builds an animation with DeepSeek

Open your codespace in VS Code, the way the setup guide's step 5 shows. Blender is already running inside the container, and the Blender MCP server named in RULES.md, a file at the top of the starter, is already pointed at it. The codespace is the sandbox: nothing an agent does there reaches your laptop.

1. Your Project 4 harness is in the codespace's harness folder, pointed at the UW Purple API, with the starter's skills/blender-scene beside your own skills: setup step 6 did that. Check that harness.py, systemprompt.md and skills/ are there before you go on.
2. Connect your harness to Blender. An MCP server is a program that offers tools over a pipe. Your harness asks it for its list, offers those tools to the model next to read_file, write_file and execute_file, and forwards a call to the server when the model picks one. Ask the LiteLLM chat in VS Code (setup step 3) for it with the following prompt:
   1. "Read harness.py and RULES.md. At startup, connect to the Blender MCP server named in RULES.md, list its tools, and add each one to the tool list beside read_file, write_file, and execute_file. Write the server's tool list, by name, as the first line of trace.jsonl. Route a call to a Blender tool to the server and append every call and its reply to trace.jsonl. Change nothing else."
3. We want the model to see what it created so it knows how to iterate. Some models have image support, including DeepSeek V4.1-flash. We need to enable it through the harness. Ask the LiteLLM chat for it with the following prompt:
   1. "Read harness.py. When a tool result contains an image, pass it to the model as an image part of the tool result instead of text, in the shape the model API takes. Keep the text parts as they are. Change nothing else."
4. Check it: in the codespace terminal, inside harness/, run python3 harness.py. It runs DeepSeek V4.1-flash on the UW Purple API. The first line of trace.jsonl lists the server's tools by name.
5. Test it out by prompting your model to create a torus, upright and spinning along the z axis. If Blender crashes along the way, run \`bash .devcontainer/start-blender.sh\` in the codespace terminal: it starts Blender and its server again. The scene in memory is gone, so ask your harness to save the .blend file as it builds.
6. Render it. Ask your harness with the following prompt:
   1. "Render the animation with the Workbench engine, one PNG per frame, into part1/frames, then join the frames into part1/scene.mp4 with ffmpeg."

## Part 2: a CLI agent builds a second animation

Part 1 showed what your harness can do. Now we hand the same Blender server to a finished agent, so you can compare your own harness with an industrial-strength one. OpenCode is the default because it is open source and runs on the UW Purple API with the course setup; Codex also works, but Claude Code is not compatible with the Purple API.
Choose where Blender runs:

* Option A (easier):  In your codespace: the same Blender and MCP server as Part 1.
* Option B (harder but may give better results):  On your laptop: install Blender from [blender.org](https://www.blender.org), then install the Blender MCP addon named in RULES.md and start the server as RULES.md shows. The CLI runs on your laptop too, with your Purple key. This will run faster, but it will take more disk-space on your laptop and your agent is not sandboxed in this route. Before Turnin, drag your part2/scene.mp4 into the codespace's part2/ folder, so checker.py finds it.

Choose your agent:

* Option A (free):  OpenCode with DeepSeek V4.1-flash on the UW Purple API: if not already, follow the Wizard or setup instructions to install and configure OpenCode with Purple API.
* Option B (your subscription plan):  Your own AI subscription's CLI agent, Claude Code, Codex or another: add the Blender MCP server named in RULES.md to your agent's MCP configuration, the way its docs show.

Complete the following:

1. Stop your harness first (Ctrl+C in its terminal): Blender takes one connection at a time. Then, in the terminal at the starter's top folder, start your agent (opencode for Option A) and build a second animation with it. You may choose to start by first building the scene, iterate until satisfied, then ask for it to be animated.
2. Once you're satisfied with your animation, ask your agent to export with the following prompt:
   1. "Render the animation with the Workbench engine, one PNG per frame, into part2/frames, then join the frames into part2/scene.mp4 with ffmpeg."

## Turnin

By Tuesday 11:59 pm:

* In the codespace terminal, at the starter's top folder, run python3 checker.py: it writes submission/p05-bundle.zip. Upload that file to the Project 5 assignment in Canvas: your Part 1 torus animation and your Part 2 animation. More can be submitted for voting.

## Grading

A model will autograde your submission. It checks that each step of Part 1 was properly followed. Every check is pass or fail. It does not judge whether your scene is beautiful, code style, prompt wording, or how many tries it took.
