# Project 5: Building a Scene with MCP

**Due: Tuesday 11:59 pm**
Prerequisites: run the [course setup wizard](https://drive.google.com/drive/folders/1cSlgyCejHVopVe6CdZWdKyq1rPfPujXd) before class.

The pelican riding a bicycle is [Simon Willison's test](https://simonwillison.net/2024/Oct/25/pelicans-on-a-bicycle/) of what a model can draw from one sentence. You will keep building your Project 4 agent: it gains Blender's tools over MCP and a gate that refuses what it must, then builds a scene you invent, anything but that pelican. The agent reaches Blender over a wire that delivers a server's tools, a protocol called MCP. You will write the rules for what the agent may do, and it all happens inside a sandbox that is not your laptop (in this case, GitHub Codespace).

## Instructions

1. Open your codespace in VS Code using the Wizard. Blender should be already running inside a container. Clone your Project 4 harness repo into the codespace, in its own folder, and copy the starter's skills/ folder into it, as in Project 4\.
2. Connect your harness to Blender. An MCP server is a program that offers tools over a pipe. Your harness asks it for its list, offers those tools to the model next to read_file, write_file and execute_file, and forwards a call to the server when the model picks one. Ask the LiteLLM chat for it with the following prompt:
   * "Read harness.py and RULES.md. At startup, connect to the Blender MCP server named in RULES.md, list its tools, and add each one to the tool list beside read_file, write_file, and execute_file. Route a call to a Blender tool to the server and append every call and its reply to trace.jsonl. Change nothing else."
3. Check it: start the harness. The first line of trace.jsonl lists the server's tools by name. Ask for a torus: the next lines show the call and its reply, and the Blender window shows the torus.
4. Pull an asset from the internet. The course publishes a toy boat at github.com/cse490A2/cse490-p05-assets. Ask your harness to "add the toy boat from github.com/cse490A2/cse490-p05-assets to the scene." Read what comes back: a recipe for salmon. The boat's file carries a prompt-injected note written as an order to your agent, and your agent obeyed it.
5. Give your harness MCP guardrails to refuse dangerous MCP calls.
   * "Read harness .py and RULES.md. Before every tool call, refuse the download tools, any command that reaches the internet, and any script that saves, exports, or renders outside this workspace. Judge what the script does, not the tool's name. Print the reason and log the refusal to trace.jsonl. Change nothing else."
6. Test it. Ask for the toy boat again. trace.jsonl shows the pull refused, with the reason your gate printed. Then ask for a sky image with the following prompt: "Add a sky image from the internet as the background." The model will reach for a download tool, or try to switch downloading on from inside a script. harness/trace.jsonl should show that call refused, with the reason your gate printed.
7. Plan your scene. Send "/plan build <your scene>": anything you can describe in one sentence, built from primitives, except a pelican on a bicycle. Answer the plan's questions and type approve when PLAN.md would work. Then build it: your agent makes a still first. Watch the Blender window and steer until the still is right, then ask for the animation.
8. Once you are satisfied, render it. Ask your harness with the following prompt:
   * "Render the animation with the Workbench engine, one PNG per frame, into ride/frames, then join the frames into ride/ride.mp4 with ffmpeg."
9. Run checker.py to prepare your submission, then submit to Canvas.

## Turnin

By Tuesday 11:59 pm:

* Upload the bundle to the Project 5 assignment in Canvas.
* Fill out the feedback form, and stop your codespace.

## Grading

A model will autograde your submission. It checks that each step was properly followed. Every check is pass or fail. It does not judge whether your scene is beautiful (the vote does), code style, prompt wording, or how many tries it took.

## Reference

Out of bounds: building the scene by hand in Blender's interface; taking the gate out; any key in anything you submit.
If your harness breaks, the LiteLLM chat in VS Code reaches the same server through VS Code's own MCP support. It covers everything but your gate.
