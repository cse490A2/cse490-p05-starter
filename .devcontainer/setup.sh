#!/usr/bin/env bash
# Per-codespace setup, run once when the codespace is created (postCreateCommand). Every
# install - Blender, its server, the desktop, the harness packages - is already in the
# published image (.devcontainer/Dockerfile, built by .github/workflows/image.yml). What is
# left is what belongs to this student: the key, the shell profile, the workspace folders.
set -uo pipefail
export PATH="$HOME/.local/bin:$PATH"

log() { printf '\n== %s\n' "$*"; }

log "what the image brought"
blender --version | head -1; uvx --version

log "the course key, kept private inside the container for shells the secret does not reach"
# Codespaces hands secrets to the editor's terminal and to this setup step, but not to an
# SSH session (instructor play-test, 2026-09-12). A copy under the home folder, readable by
# this user only, lets every shell find it.
if [ -n "${LITELLM_API_KEY:-}" ]; then
  mkdir -p "$HOME/.config/cse490" && chmod 700 "$HOME/.config/cse490"
  printf '%s' "$LITELLM_API_KEY" > "$HOME/.config/cse490/key" && chmod 600 "$HOME/.config/cse490/key"
fi

log "the harness finds its key and the gateway from every shell"
PROFILE_LINE='[ -z "${LITELLM_API_KEY:-}" ] && [ -r "$HOME/.config/cse490/key" ] && export LITELLM_API_KEY="$(cat "$HOME/.config/cse490/key")"; export LITELLM_BASE_URL="${LITELLM_BASE_URL:-https://llmproxy.cs.washington.edu}" HARNESS_MODEL="${HARNESS_MODEL:-external/haiku-5-5}"'
for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
  grep -q 'LITELLM_BASE_URL' "$rc" 2>/dev/null || echo "$PROFILE_LINE" >> "$rc"
done

log "the Blender window connects by itself at the port's bare address"
# The desktop feature serves noVNC; its front page is a connect form. The editor's auto-preview
# opens the bare address, so that page becomes a redirect to the auto-connecting one.
for d in /usr/local/novnc/noVNC-*; do
  [ -d "$d" ] || continue
  printf '%s' '<!doctype html><meta http-equiv="refresh" content="0; url=vnc.html?autoconnect=true&resize=scale&password=vscode"><title>Blender window</title>' \
    | sudo tee "$d/index.html" >/dev/null && echo "auto-connect page in $d"
done

log "folders the build writes into"
mkdir -p ride ride/frames submission

log "done. Blender's window starts on every codespace start (start-blender.sh)."
