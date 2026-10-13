// CSE 490 workspace: the screen a student sees on every open of the Project 5
// codespace, arranged by an extension because nothing in a config file can do it
// (editor tabs, sidebars and panel placement are workbench state).
//
// On activation, and on the command "CSE 490: Arrange the workspace":
//   1. close every editor tab
//   2. open ASSIGNMENT.md on the left, focused, and Blender's window beside it:
//      the codespace desktop on port 6080, shown in the editor's own browser tab
//      (the wizard made that port public, so the tab needs no sign-in)
//   3. open the chat in the right-hand sidebar
//   4. focus a terminal below
const vscode = require("vscode");

const BLENDER_PORT = 6080;
const BLENDER_PAGE = "vnc.html?autoconnect=true&resize=scale&password=vscode";

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function tryCommand(id, ...args) {
  try {
    await vscode.commands.executeCommand(id, ...args);
    return true;
  } catch (e) {
    return false;
  }
}

// Blender's window beside the assignment. asExternalUri forwards the port and
// returns its address on this codespace; the built-in Simple Browser shows it
// as an editor tab. If that tab cannot open, the address goes to the system browser.
async function showBlender(output) {
  let base;
  try {
    base = await vscode.env.asExternalUri(vscode.Uri.parse("http://localhost:" + BLENDER_PORT + "/"));
  } catch (e) {
    output.appendLine("port " + BLENDER_PORT + " could not be forwarded: " + e);
    return;
  }
  const url = base.toString(true).replace(/\/?$/, "/") + BLENDER_PAGE;
  output.appendLine("blender window at " + base.toString(true));
  const inEditor = await tryCommand("simpleBrowser.api.open", vscode.Uri.parse(url), {
    viewColumn: vscode.ViewColumn.Two,
    preserveFocus: true,
  });
  if (!inEditor) {
    output.appendLine("no browser tab in this editor; opening the system browser");
    await vscode.env.openExternal(vscode.Uri.parse(url));
  }
}

async function arrange(output) {
  output.appendLine(new Date().toISOString() + " arranging the workspace");
  await tryCommand("workbench.action.closeAllEditors");

  // The chat on the right: VS Code's chat view, where the LiteLLM extension answers.
  // The extension may still be starting; a second try after a pause covers it.
  let chat = await tryCommand("workbench.action.chat.open");
  if (!chat) {
    await sleep(3000);
    chat = await tryCommand("workbench.action.chat.open");
  }
  output.appendLine("chat panel: " + (chat ? "opened" : "not available"));

  // The assignment on the left, focused: the answer to "where do I start".
  const folders = vscode.workspace.workspaceFolders || [];
  if (folders.length) {
    const asg = vscode.Uri.joinPath(folders[0].uri, "ASSIGNMENT.md");
    try {
      await vscode.workspace.fs.stat(asg);
      await vscode.commands.executeCommand("vscode.open", asg, { viewColumn: vscode.ViewColumn.One, preview: false });
      output.appendLine("assignment opened");
    } catch (e) {
      output.appendLine("no ASSIGNMENT.md in the workspace");
    }
  }

  // Blender's window beside it.
  await showBlender(output);

  // the explorer, not the extensions view, on the left
  await tryCommand("workbench.view.explorer");

  // The terminal below, for the student's harness.
  if (!vscode.window.terminals.length) {
    vscode.window.createTerminal({ name: "harness" });
  }
  await tryCommand("workbench.action.terminal.focus");
  output.appendLine("done");
}

let arranged = false;

function activate(context) {
  const output = vscode.window.createOutputChannel("CSE 490 workspace");
  context.subscriptions.push(output);
  context.subscriptions.push(
    vscode.commands.registerCommand("cse490.layout", () => arrange(output))
  );
  if (!arranged) {
    arranged = true;
    // let the workbench finish restoring its own state before rearranging it
    setTimeout(() => arrange(output).catch((e) => output.appendLine("error: " + e)), 2500);
  }
}

function deactivate() {}

module.exports = { activate, deactivate };
