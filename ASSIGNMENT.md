# Project 5: Building an Animation with MCP

**Due: Tuesday 11:59 pm**
Prerequisites: run the course setup wizard during class.

In this project you will create an awesome animation and learn about MCPs and sandboxes in the process! We've built enough pelicans riding bicycles though, so think about something you want to animate instead – no pelicans riding bicycles please :-). We'll feature some of the most exciting results in class! The project has two parts, and each one ends in an animation built through the Blender MCP server. In Part 1 your Project 4 agent gains Blender's tools over MCP and gains the ability to see images, inside a sandbox hosted on GitHub Codespaces. Part 2 is optional: you hand the same Blender server to an industrial-strength agent, OpenCode with DeepSeek V4.1-flash on the UW Purple API or your own AI subscription's CLI, and build a second animation with Blender in your codespace or installed on your own laptop.

## Part 1: your harness builds an animation with DeepSeek

Open your codespace in VS Code using the Wizard. Blender is already running inside the container, and the Blender MCP server named in RULES.md is already pointed at it. The codespace is the sandbox: nothing an agent does there reaches your laptop.

1. Clone your Project 4 harness repo, in its own folder, and copy the starter's skills/ folder into it, as in Project 4. Point the harness at the UW Purple API as the setup instructions show: the endpoint, your Purple key, and the api-key header.
2. Connect your harness to Blender. An MCP server is a program that offers tools over a pipe. Your harness asks it for its list, offers those tools to the model next to read_file, write_file and execute_file, and forwards a call to the server when the model picks one. Ask the LiteLLM chat for it with the following prompt:
   1. "Read harness.py and RULES.md. At startup, connect to the Blender MCP server named in RULES.md, list its tools, and add each one to the tool list beside read_file, write_file, and execute_file. Route a call to a Blender tool to the server and append every call and its reply to trace.jsonl. Change nothing else."
3. We want the model to see what it created so it knows how to iterate. Some models have image support, including DeepSeek V4.1-flash. We need to enable it through the harness. Ask the LiteLLM chat for it with the following prompt:
   1. "Read harness.py. When a tool result contains an image, pass it to the model as an image part of the tool result instead of text, in the shape the model API takes. Keep the text parts as they are. Change nothing else."
4. Check it: start the harness, which runs DeepSeek V4.1-flash on the UW Purple API. The first line of trace.jsonl lists the server's tools by name. Ask for a torus, then ask the model what the scene looks like: the next lines show the calls and their replies, and you should see a torus in the Blender window.
5. Build your animation with your harness: anything you can describe in one sentence, built from primitives. Ask for a static image, iterate until satisfied, then ask for it to be animated.
6. Render it. Ask your harness with the following prompt:
   1. "Render the animation with the Workbench engine, one PNG per frame, into part1/frames, then join the frames into part1/scene.mp4 with ffmpeg."

## Part 2 (optional): a CLI agent builds a second animation

Part 1 showed what a harness does from the inside. Part 2 hands the same Blender server to a finished agent, so you can compare your own harness with an industrial-strength one. OpenCode is the default because it is open source and runs on the UW Purple API with the course setup; Claude Code, Codex or Gemini CLI do the same on your own subscription.

Choose where Blender runs:

* In your codespace: the same Blender and MCP server as Part 1.
* On your laptop: install Blender from blender.org, then install the Blender MCP addon named in RULES.md and start the server as RULES.md shows. The CLI runs on your laptop too, with the same key from the wizard. Note that your agent is not sandboxed in this route.
Choose your agent:

* OpenCode with DeepSeek V4.1-flash on the UW Purple API: if not already, follow the Wizard or setup instructions to install and configure OpenCode with Purple API.
* Your own AI subscription's CLI agent, Claude Code, Codex, Gemini CLI or another: add the Blender MCP server named in RULES.md to your agent's MCP configuration, the way its docs show.
1. Build a second animation with your agent. Ask for a static image, iterate until satisfied, then ask for it to be animated.
2. Once you're satisfied with your animation, ask your agent to export with the following prompt:
   1. "Render the animation with the Workbench engine, one PNG per frame, into part2/frames, then join the frames into part2/scene.mp4 with ffmpeg."

## Turnin

By Tuesday 11:59 pm:

* Run checker.py to prepare your submission, then upload the bundle it wrote to the Project 5 assignment in Canvas: your Part 1 animation, and your Part 2 animation if you made one. More can be submitted for voting.

## Grading

A model will autograde your submission. It checks that each step of Part 1 was properly followed. Every check is pass or fail. It does not judge whether your scene is beautiful, code style, prompt wording, or how many tries it took. Part 2 is not graded.

