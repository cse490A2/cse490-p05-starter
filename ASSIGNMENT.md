# Project 5: Building an Animation with MCP

**Due: Tuesday 11:59 pm**
Prerequisites: run the [course setup wizard](https://drive.google.com/drive/folders/1cSlgyCejHVopVe6CdZWdKyq1rPfPujXd) before class.

In this project you will create an awesome animation and learn about MCPs and sandboxes in the process!  We’ve built enough pelicans riding bicycles though, so think about something you want to animate instead – no pelicans riding bicycles please :-).  We’ll feature some of the most exciting results in class!  You’ll build this on top of your Project 4 agent:  it gains Blender's tools over MCP and a gate that refuses what it must, then builds a scene you invent. You will write the rules for what the agent may do, and it all happens inside a sandbox hosted on GitHub Codespace.

## Instructions

1. Open your codespace in VS Code using the Wizard. Blender should be already running inside a container. Clone your Project 4 harness repo into the codespace, in its own folder, and copy the starter's skills/ folder into it, as in Project 4.
2. Connect your harness to Blender. An MCP server is a program that offers tools over a pipe. Your harness asks it for its list, offers those tools to the model next to read_file, write_file and execute_file, and forwards a call to the server when the model picks one. Ask the LiteLLM chat for it with the following prompt:
   * "Read harness.py and RULES.md. At startup, connect to the Blender MCP server named in RULES.md, list its tools, and add each one to the tool list beside read_file, write_file, and execute_file. Route a call to a Blender tool to the server and append every call and its reply to trace.jsonl. Change nothing else."
3. Check it: start the harness. The first line of trace.jsonl lists the server's tools by name. Ask for a torus: the next lines show the call and its reply, and the Blender window shows the torus.
4. Pull an asset from the internet: use this toy boat at github.com/cse490A2/cse490-p05-assets. Ask your harness to "add the toy boat from github.com/cse490A2/cse490-p05-assets to the scene." Read what comes back: a recipe for salmon. The boat's file carries a prompt-injected note written as an order to your agent, and your agent obeyed it.
5. Add the gate. In step 4 the model did what the boat's file told it. Nothing stood between the model's choice and the call: your harness ran every tool call it was handed. A gate is one check in that path. Before each call runs, the harness looks at the call itself, the tool's name and what the script or file does, and either lets it through or refuses it and says why. The model reads the refusal as a tool result and moves on. RULES.md names the two kinds of call to refuse: a tool that reaches outside, and a script or command that reaches the internet or writes outside this workspace. Ask the LiteLLM chat for it with the following prompt:
   * "Read harness.py and RULES.md. Put the check in one function, gate, that takes the tool's name and its arguments and returns a reason to refuse or nothing. Call it in the loop right before the tool would run. When it returns a reason, do not run the tool: append the reason to the context as the tool's result, so the model reads it, print it, and log it to trace.jsonl. Refuse what RULES.md forbids: the download tools, any command that reaches the internet, and any script that saves, exports, or renders outside this workspace. Judge what the script does, not the tool's name. Change nothing else."
6. Test it by repeating step 4. Ask for the toy boat again. This time the terminal prints the refusal, trace.jsonl logs it with the reason gate returned, and the model's next reply tells you it could not fetch the boat. Open trace.jsonl and find the line: it is the return value you just read in the code.
7. Plan your animation. Send "/plan build <your scene>": anything you can describe in one sentence, built from primitives, except a pelican on a bicycle. Answer the plan's questions and type approve when PLAN.md would work. Then build it: your agent makes a still first. Watch the Blender window and steer until the still is right, then ask for the animation.
8. Once you are satisfied, render it. Ask your harness with the following prompt:
   * "Render the animation with the Workbench engine, one PNG per frame, into scene/frames, then join the frames into scene/scene.mp4 with ffmpeg."
9. Run checker.py to prepare your submission, then submit to Canvas.

## Turnin

By Tuesday 11:59 pm:

* Upload the bundle to the Project 5 assignment in Canvas.
* Fill out the feedback form, and stop your codespace.

## Grading

A model will autograde your submission. It checks that each step was properly followed. Every check is pass or fail. It does not judge whether your scene is beautiful, code style, prompt wording, or how many tries it took.
