#!/usr/bin/env bash
# Per-codespace setup, run once when the codespace is created (postCreateCommand). Every
# install - Blender, its server, the desktop, Claude Code, the harness packages - is already
# in the published image (.devcontainer/Dockerfile, built by .github/workflows/image.yml).
# What is left is what belongs to this student: the key, the shell profile, Claude Code's
# first-run answers, the workspace folders.
set -uo pipefail
export PATH="$HOME/.local/bin:$PATH"

log() { printf '\n== %s\n' "$*"; }

log "what the image brought"
blender --version | head -1; uvx --version; claude --version || true

log "the course key, kept private inside the container for shells the secret does not reach"
# Codespaces hands secrets to the editor's terminal and to this setup step, but not to an
# SSH session (instructor play-test, 2026-09-12). A copy under the home folder, readable by
# this user only, lets every shell find it.
if [ -n "${LITELLM_API_KEY:-}" ]; then
  mkdir -p "$HOME/.config/cse490" && chmod 700 "$HOME/.config/cse490"
  printf '%s' "$LITELLM_API_KEY" > "$HOME/.config/cse490/key" && chmod 600 "$HOME/.config/cse490/key"
fi

log "Claude Code talks to the course gateway with the course key, from every shell"
PROFILE_LINE='[ -z "${LITELLM_API_KEY:-}" ] && [ -r "$HOME/.config/cse490/key" ] && export LITELLM_API_KEY="$(cat "$HOME/.config/cse490/key")"; export ANTHROPIC_BASE_URL="${LITELLM_BASE_URL:-https://llmproxy.cs.washington.edu}" ANTHROPIC_AUTH_TOKEN="$LITELLM_API_KEY" ANTHROPIC_MODEL="${ANTHROPIC_MODEL:-external/sonnet-5}" ANTHROPIC_SMALL_FAST_MODEL="${ANTHROPIC_SMALL_FAST_MODEL:-external/haiku-4-5-20251001}" CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS=1'
for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
  grep -q 'ANTHROPIC_AUTH_TOKEN' "$rc" 2>/dev/null || echo "$PROFILE_LINE" >> "$rc"
done

log "Claude Code first-run answers, so the first launch lands on the prompt"
python3 - <<'PY'
import json, os, pathlib
cfg = pathlib.Path.home() / ".claude.json"
data = {}
if cfg.exists():
    try:
        data = json.loads(cfg.read_text())
    except json.JSONDecodeError:
        data = {}
ws = os.environ.get("CODESPACE_VSCODE_FOLDER") or os.getcwd()
data.setdefault("hasCompletedOnboarding", True)
data.setdefault("theme", "dark")
data.setdefault("shiftEnterKeyBindingInstalled", True)
data.setdefault("hasAcknowledgedCostThreshold", True)
proj = data.setdefault("projects", {}).setdefault(ws, {})
proj.setdefault("hasCompletedProjectOnboarding", True)
enabled = proj.setdefault("enabledMcpjsonServers", [])
if "blender" not in enabled:
    enabled.append("blender")
cfg.write_text(json.dumps(data, indent=1))
print("wrote", cfg, "for", ws)
PY

log "the Blender window connects by itself at the port's bare address"
# The desktop feature serves noVNC; its front page is a connect form. The editor's auto-preview
# opens the bare address, so that page becomes a redirect to the auto-connecting one.
for d in /usr/local/novnc/noVNC-*; do
  [ -d "$d" ] || continue
  printf '%s' '<!doctype html><meta http-equiv="refresh" content="0; url=vnc.html?autoconnect=true&resize=scale&password=vscode"><title>Blender window</title>' \
    | sudo tee "$d/index.html" >/dev/null && echo "auto-connect page in $d"
done

log "folders the build writes into"
mkdir -p ride ride/frames submission record

log "done. Blender's window starts on every codespace start (start-blender.sh)."
