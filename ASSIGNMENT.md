# Project 5: Building an Animation with MCP

**Due: Tuesday 11:59 pm**
Prerequisites: run the course setup wizard during class.

In this project you will create an awesome animation and learn about MCPs and sandboxes in the process! We've built enough pelicans riding bicycles though, so think about something you want to animate instead – no pelicans riding bicycles please :-). We'll feature some of the most exciting results in class! The project has three parts, and each one ends in an animation built through the Blender MCP server. In Part 1 your Project 4 agent gains Blender's tools over MCP and gains the ability to see images. In Part 2 you will use OpenCode CLI with DeepSeek V4.1-flash on the UW Purple API to build a second animation. If you have your own AI subscription, Part 3 offers you the option to create an animation through that route. You will write the rules for what the agent may do, and Blender runs where you choose: inside a sandbox hosted on GitHub Codespaces, or installed on your own laptop.

## Choosing where Blender runs

Choose one:

* Run Blender virtually through GitHub codespace: open your codespace in VS Code using the Wizard. Blender is already running inside the container, and the Blender MCP server named in RULES.md is already pointed at it. The codespace is the sandbox: nothing an agent does there reaches your laptop.
* Run Blender locally on your laptop: install Blender from [blender.org](https://www.blender.org), then install the Blender MCP addon named in RULES.md and start the server as RULES.md shows. Your harness and the CLIs run on your laptop too, with the same key from the wizard. Note that your agent is not sandboxed in this route.

## Part 1: your harness builds an animation with Sonnet 5

1. Clone your Project 4 harness repo, in its own folder, and copy the starter's skills/ folder into it, as in Project 4.
2. Connect your harness to Blender. An MCP server is a program that offers tools over a pipe. Your harness asks it for its list, offers those tools to the model next to read_file, write_file and execute_file, and forwards a call to the server when the model picks one. Ask the LiteLLM chat for it with the following prompt:
   * "Read harness.py and RULES.md. At startup, connect to the Blender MCP server named in RULES.md, list its tools, and add each one to the tool list beside read_file, write_file, and execute_file. Route a call to a Blender tool to the server and append every call and its reply to trace.jsonl. Change nothing else."
3. We want the model to see what it created so it knows how to iterate. Some models have image support, including Sonnet 5. We need to enable it through the harness. Ask the LiteLLM chat for it with the following prompt:
   * "Read harness.py. When a tool result contains an image, pass it to the model as an image part of the tool result instead of text, in the shape the model API takes. Keep the text parts as they are. Change nothing else."
4. Check it: start the harness, which runs Sonnet 5 through the course gateway. The first line of trace.jsonl lists the server's tools by name. Ask for a torus, then ask the model what the scene looks like: the next lines show the calls and their replies, and you should see a torus in the Blender window.
5. Build your animation with your harness: anything you can describe in one sentence, built from primitives. Ask for a static image, iterate until satisfied, then ask for it to be animated.
6. Render it. Ask your harness with the following prompt:
   * "Render the animation with the Workbench engine, one PNG per frame, into part1/frames, then join the frames into part1/scene.mp4 with ffmpeg."

## Part 2: OpenCode builds an animation with DeepSeek v4.1 Flash

1. If not already, follow the Wizard or setup instructions to install and configure OpenCode with Purple API.
2. Build a second animation using DeepSeek v4.1 Flash on OpenCode. Ask for a static image, iterate until satisfied, then ask for it to be animated.
3. Once you're satisfied with your animation, ask OpenCode to export with the following prompt:
   * "Render the animation with the Workbench engine, one PNG per frame, into part2/frames, then join the frames into part2/scene.mp4 with ffmpeg."
4. Run checker.py to prepare your submission, then submit to Canvas.

## Part 3: your own subscription (optional)

If you have your own AI subscription, use its CLI agent, Claude Code, Codex, Gemini CLI or another, with Blender in your codespace or on your laptop:

* Add the Blender MCP server named in RULES.md to your agent's MCP configuration, the way its docs show.
* Create another scene and watch your agent build it in real time.

## Turnin

By Tuesday 11:59 pm:

* Upload the bundle checker.py wrote to the Project 5 assignment in Canvas. There should be a minimum of 2 animations, but more can be submitted for voting.

## Grading

A model will autograde your submission. It checks that each step of Parts 1 and 2 was properly followed. Every check is pass or fail. It does not judge whether your scene is beautiful, code style, prompt wording, or how many tries it took. Part 3 is not graded.
