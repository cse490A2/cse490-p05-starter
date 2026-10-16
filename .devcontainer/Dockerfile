FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# Everything a Project 5 codespace needs, built ONCE by .github/workflows/image.yml and
# published to the registry. A new codespace pulls this image; nothing below runs at
# create time. Versions are pinned here and restated in the course setup checklist.
ARG BLENDER_SERIES=5.2
ARG BLENDER_VERSION=5.2.1
ARG BLENDER_MCP_VERSION=1.9.1

# Runtime libraries the Linux tarball expects from the OS, plus Mesa's software rasterizer
# (llvmpipe, in libgl1-mesa-dri) so the GUI runs on a machine with no GPU; Python 3.12 from
# Ubuntu (the dev-container Python feature compiles one from source, three minutes a
# codespace); ffmpeg for the checker and the scene video.
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      libgl1 libglx-mesa0 libgl1-mesa-dri libegl1 libgles2 libglu1-mesa mesa-utils \
      libx11-6 libxi6 libxxf86vm1 libxfixes3 libxrender1 libxkbcommon0 libxrandr2 libxcursor1 libxinerama1 \
      libsm6 libice6 libdbus-1-3 libpulse0 libgomp1 \
      python3 python3-pip python3-venv \
      ffmpeg xz-utils ca-certificates curl gnupg \
 && rm -rf /var/lib/apt/lists/*

# download.blender.org answers 403 to non-browser clients (instructor play-test, 2026-09-12);
# the OCF mirror serves the same file, and the browser user agent is the fallback.
RUN set -eux; \
    f="blender-${BLENDER_VERSION}-linux-x64.tar.xz"; \
    ( curl -fsSL -o /tmp/b.tar.xz "https://mirrors.ocf.berkeley.edu/blender/release/Blender${BLENDER_SERIES}/${f}" \
      || curl -fsSL -A "Mozilla/5.0" -o /tmp/b.tar.xz "https://download.blender.org/release/Blender${BLENDER_SERIES}/${f}" ); \
    mkdir -p /opt/blender; \
    tar -xJf /tmp/b.tar.xz -C /opt/blender --strip-components=1; \
    rm /tmp/b.tar.xz; \
    ln -s /opt/blender/blender /usr/local/bin/blender; \
    /opt/blender/blender --version

# The harness's Python packages (the same file the workspace carries)
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt

# As the codespace user: uv, the MCP for Blender server warmed into uv's cache, and the
# add-on installed into Blender's add-ons folder. enable_addon.py enables it at every launch.
USER vscode
ENV PATH="/home/vscode/.local/bin:${PATH}"
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
 && timeout 180 uvx "blender-mcp==${BLENDER_MCP_VERSION}" --help >/dev/null 2>&1 || true
RUN mkdir -p "/home/vscode/.config/blender/${BLENDER_SERIES}/scripts/addons" \
 && uvx "blender-mcp==${BLENDER_MCP_VERSION}" install-addon || true
# The OpenAI Codex CLI, the agent that builds the animation (owner direction 2026-10-15). The
# standalone installer puts the binary in ~/.local/bin and its releases under ~/.codex; no Node.
# setup.sh writes its config at create time: the course gateway over the Responses API, the key
# by name, and the Blender server.
RUN curl -fsSL https://chatgpt.com/codex/install.sh | CODEX_NON_INTERACTIVE=1 sh \
 && codex --version
USER root
