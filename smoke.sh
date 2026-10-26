#!/usr/bin/env bash
# The checks that the codespace is ready for the build. Run: bash smoke.sh
export PATH="$HOME/.local/bin:$PATH"
# an SSH session does not receive Codespaces secrets; the setup step kept a private copy
[ -z "${LITELLM_API_KEY:-}" ] && [ -r "$HOME/.config/cse490/key" ] && export LITELLM_API_KEY="$(cat "$HOME/.config/cse490/key")"
ok=0; bad=0
pass() { echo "OK      $*"; ok=$((ok+1)); }
fail() { echo "MISSING $*"; bad=$((bad+1)); }

python3 --version >/dev/null 2>&1 && pass "python $(python3 --version 2>&1 | cut -d' ' -f2)" || fail "python"
command -v uvx >/dev/null 2>&1 && pass "uv $(uvx --version 2>&1 | cut -d' ' -f2)" || fail "uv (rerun: bash .devcontainer/setup.sh)"
command -v blender >/dev/null 2>&1 && pass "blender $(blender --version 2>/dev/null | head -1 | cut -d' ' -f2)" || fail "blender"

# after a restart Blender takes about a minute to come up; wait for its socket rather than fail
if python3 - <<'EOF'
import socket, sys, time
for _ in range(90):
    s = socket.socket(); s.settimeout(1)
    try:
        s.connect(("localhost", 9876)); sys.exit(0)
    except Exception:
        time.sleep(1)
    finally:
        s.close()
sys.exit(1)
EOF
then pass "Blender server listening on localhost:9876"
else fail "Blender server on 9876 (is the Blender window up? bash .devcontainer/start-blender.sh)"
fi

if [ -n "${LITELLM_API_KEY:-}" ]; then pass "course key present as a secret"; else fail "LITELLM_API_KEY secret (GitHub Settings, Codespaces, Secrets; then restart the codespace)"; fi

code=$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer ${LITELLM_API_KEY:-none}" "${LITELLM_BASE_URL:-https://llmproxy.cs.washington.edu}/v1/models")
[ "$code" = "200" ] && pass "gateway answers to your key" || fail "gateway (HTTP $code)"

[ -n "${HARNESS_MODEL:-}" ] && pass "harness model $HARNESS_MODEL" || fail "HARNESS_MODEL (set by the codespace)"

ls "$HOME/.vscode-remote/extensions" "$HOME/.vscode-server/extensions" 2>/dev/null | grep -q "vivswan.litellm-vscode-chat" && pass "LiteLLM chat extension installed in the codespace" || fail "LiteLLM chat extension (Extensions panel: install LiteLLM Provider for GitHub Copilot Chat)"

export PATH="$HOME/.opencode/bin:$PATH"
command -v opencode >/dev/null 2>&1 && pass "opencode $(opencode --version 2>/dev/null | tail -1)" || fail "opencode (the image installs it; rebuild the codespace)"
grep -q '"purple"' "$HOME/.config/opencode/opencode.json" 2>/dev/null && grep -q '"blender"' "$HOME/.config/opencode/opencode.json" && pass "opencode config names the Purple API and the Blender server" || fail "opencode config (rerun: bash .devcontainer/setup.sh)"
[ -z "${PURPLE_API_KEY:-}" ] && [ -r "$HOME/.config/cse490/purple-key" ] && export PURPLE_API_KEY="$(cat "$HOME/.config/cse490/purple-key")"
if [ -n "${PURPLE_API_KEY:-}" ]; then pass "Purple API key present"; else fail "PURPLE_API_KEY secret: your harness and OpenCode both need it (GitHub Settings, Codespaces, Secrets; then restart the codespace)"; fi
pcode=$(curl -s -o /dev/null -w '%{http_code}' -X POST -H "api-key: ${PURPLE_API_KEY:-none}" -H "Content-Type: application/json" -d '{"model":"'"${PURPLE_MODEL:-DeepSeek-V4.1-Flash}"'","messages":[{"role":"user","content":"ok"}],"max_tokens":1}' "${PURPLE_BASE_URL:-https://apim-n1ai-usw2-065882797.azure-api.net/openai/v1}/chat/completions")
[ "$pcode" = "200" ] && pass "Purple API answers to your key" || fail "Purple API (HTTP $pcode; 403 with a message about quota means today's allowance is spent, it resets at midnight UTC)"

echo; echo "$ok ok, $bad missing"
[ "$bad" -eq 0 ]
