#!/usr/bin/env bash
# Per-codespace setup, run once when the codespace is created (postCreateCommand). Every
# install - Blender, its server, the desktop, OpenCode, the harness packages - is already in the
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
PROFILE_LINE='[ -z "${LITELLM_API_KEY:-}" ] && [ -r "$HOME/.config/cse490/key" ] && export LITELLM_API_KEY="$(cat "$HOME/.config/cse490/key")"; export LITELLM_BASE_URL="${LITELLM_BASE_URL:-https://llmproxy.cs.washington.edu}" HARNESS_MODEL="${HARNESS_MODEL:-external/sonnet-5}"'
for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
  grep -q 'LITELLM_BASE_URL' "$rc" 2>/dev/null || echo "$PROFILE_LINE" >> "$rc"
done

log "the Purple API values reach every shell: the harness reads PURPLE_API_KEY, PURPLE_BASE_URL and PURPLE_MODEL"
PURPLE_LINE='[ -z "${PURPLE_API_KEY:-}" ] && [ -r "$HOME/.config/cse490/purple-key" ] && export PURPLE_API_KEY="$(cat "$HOME/.config/cse490/purple-key")"; export PURPLE_BASE_URL="${PURPLE_BASE_URL:-https://apim-n1ai-usw2-065882797.azure-api.net/openai/v1}"; export PURPLE_MODEL="${PURPLE_MODEL:-DeepSeek-V4.1-Flash}"'
for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
  grep -q 'PURPLE_BASE_URL' "$rc" 2>/dev/null || echo "$PURPLE_LINE" >> "$rc"
done
if [ -n "${PURPLE_API_KEY:-}" ]; then
  mkdir -p "$HOME/.config/cse490" && chmod 700 "$HOME/.config/cse490"
  printf '%s' "$PURPLE_API_KEY" > "$HOME/.config/cse490/purple-key" && chmod 600 "$HOME/.config/cse490/purple-key"
fi

log "the Blender window connects by itself at the port's bare address"
# The desktop feature serves noVNC; its front page is a connect form. The editor's auto-preview
# opens the bare address, so that page becomes a redirect to the auto-connecting one.
for d in /usr/local/novnc/noVNC-*; do
  [ -d "$d" ] || continue
  printf '%s' '<!doctype html><meta http-equiv="refresh" content="0; url=vnc.html?autoconnect=true&resize=scale&password=vscode"><title>Blender window</title>' \
    | sudo tee "$d/index.html" >/dev/null && echo "auto-connect page in $d"
done

log "OpenCode is present"
# The image installs OpenCode (Dockerfile). Until the registry image students pull is rebuilt
# from this Dockerfile - devcontainer.json pulls ghcr.io/arian-shamaei/cse490-p05-blender, the
# workflow publishes ghcr.io/cse490a2/cse490-p05-blender, which is private (2026-10-23) - an
# older image may arrive without it; then the installer runs here, once, about ten seconds.
export PATH="$HOME/.opencode/bin:$PATH"
if ! command -v opencode >/dev/null 2>&1; then
  curl -fsSL https://opencode.ai/install | bash >/tmp/opencode-install.log 2>&1 && echo "opencode installed at create time" || echo "opencode install FAILED: see /tmp/opencode-install.log"
fi
opencode --version 2>/dev/null | tail -1

log "OpenCode finds its model, your key by name, and the Blender server in its own config"
# Part 2 runs the OpenCode CLI. Its model is DeepSeek V4.1 Flash on the UW Purple API, an
# OpenAI-compatible endpoint behind Azure API Management that reads the key from an api-key
# header. The values below are the owner's working config of 2026-10-23 (opencode.json on the
# course machine); CONFIRM FOR STUDENTS before the project opens. The key is named, never
# written: OpenCode reads PURPLE_API_KEY from the environment at run time. When that secret is
# absent the config falls back to the course gateway with a stand-in model, so a TA can test
# the Part 2 steps today.
PURPLE_BASE_URL="${PURPLE_BASE_URL:-https://apim-n1ai-usw2-065882797.azure-api.net/openai/v1}"
PURPLE_MODEL="${PURPLE_MODEL:-DeepSeek-V4.1-Flash}"     # the model id Purple serves
GATEWAY_STAND_IN="external/deepseek.v3.2"              # until Purple's key reaches the codespace
if [ -n "${PURPLE_API_KEY:-}" ]; then
  mkdir -p "$HOME/.config/cse490" && printf '%s' "$PURPLE_API_KEY" > "$HOME/.config/cse490/purple-key" && chmod 600 "$HOME/.config/cse490/purple-key"
  DEFAULT_MODEL="purple/${PURPLE_MODEL}"
  echo "Purple key present: OpenCode starts on ${DEFAULT_MODEL}"
else
  DEFAULT_MODEL="uw/${GATEWAY_STAND_IN}"
  echo "no PURPLE_API_KEY secret: Part 1's harness and OpenCode both need it (GitHub Settings, Codespaces, Secrets; then restart the codespace); OpenCode starts on the course gateway's ${GATEWAY_STAND_IN} until it is set"
fi
mkdir -p "$HOME/.config/opencode"
cat > "$HOME/.config/opencode/opencode.json" <<EOF2
{
  "\$schema": "https://opencode.ai/config.json",
  "model": "${DEFAULT_MODEL}",
  "provider": {
    "purple": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "UW Purple API",
      "options": {
        "baseURL": "${PURPLE_BASE_URL}",
        "headers": { "api-key": "{env:PURPLE_API_KEY}" }
      },
      "models": {
        "${PURPLE_MODEL}": {
          "name": "DeepSeek V4.1 Flash (UW Purple)",
          "tool_call": true,
          "attachment": true,
          "modalities": { "input": ["text", "image"], "output": ["text"] },
          "limit": { "context": 128000, "output": 16384 }
        }
      }
    },
    "uw": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "UW course gateway",
      "options": {
        "baseURL": "${LITELLM_BASE_URL:-https://llmproxy.cs.washington.edu}/v1",
        "apiKey": "{env:LITELLM_API_KEY}"
      },
      "models": {
        "${GATEWAY_STAND_IN}": { "name": "${GATEWAY_STAND_IN} (course gateway, stand-in)", "tool_call": true,
                                 "limit": { "context": 128000, "output": 8000 } }
      }
    }
  },
  "mcp": {
    "blender": {
      "type": "local",
      "command": ["/home/vscode/.local/bin/uvx", "blender-mcp==1.9.1"],
      "environment": {
        "BLENDER_MCP_SAFE_MODE": "1",
        "BLENDER_MCP_DISABLE_TELEMETRY": "true",
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      },
      "enabled": true
    }
  }
}
EOF2
echo "opencode config written to $HOME/.config/opencode/opencode.json"
# every shell finds the Purple key the same way it finds the course key
PURPLE_LINE='[ -z "${PURPLE_API_KEY:-}" ] && [ -r "$HOME/.config/cse490/purple-key" ] && export PURPLE_API_KEY="$(cat "$HOME/.config/cse490/purple-key")"; export PATH="$HOME/.opencode/bin:$PATH"'
for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
  grep -q 'purple-key' "$rc" 2>/dev/null || echo "$PURPLE_LINE" >> "$rc"
done

log "folders the build writes into"
mkdir -p part1/frames part2/frames submission

log "done. Blender's window starts on every codespace start (start-blender.sh)."
