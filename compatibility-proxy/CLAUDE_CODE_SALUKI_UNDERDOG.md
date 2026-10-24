# LocalMCP — Underdog Saluki + Claude Code CLI

Run **Claude Code CLI with a locally hosted Underdog Saluki model**, and give it access to three Java/Spring Boot **MCP servers** for system, Git, and project operations.

> This guide consolidates the setup from our LocalMCP work. It documents both the direct Ollama connection and the compatibility-proxy workaround we used. The proxy source and exact JAR filenames were not supplied with the README, so check those against your checkout.

## Architecture

```text
Claude Code CLI (`claude --model saluki`)
          |
          | Anthropic-compatible HTTP API
          v
Compatibility proxy (127.0.0.1:8000) [when needed]
          |
          v
Ollama (127.0.0.1:11434)
          |
          v
Underdog Saluki 27B Q4_K_M

Claude Code CLI
    |-- MCP: system-server  (Java/Spring Boot, stdio)
    |-- MCP: git-server     (Java/Spring Boot, stdio)
    `-- MCP: project-server (Java/Spring Boot, stdio)
```

## 1. Requirements

Ubuntu/Linux, Java **21**, Maven, Git, Ollama, and Claude Code CLI. The 27B Q4 model is comparatively large; sufficient RAM/VRAM and possibly CPU offloading are needed.

```bash
sudo apt update
sudo apt install -y openjdk-21-jdk maven git curl
java -version
mvn -version
```

Verify Maven is actually using JDK 21 (`mvn -version`), not an older JDK.

## 2. Install Ollama and pull Saluki

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
ollama pull hf.co/ConwayResearch/Underdog-Saluki-27B-1.0:Q4_K_M
ollama run hf.co/ConwayResearch/Underdog-Saluki-27B-1.0:Q4_K_M
```

In another terminal, verify the API and installed models:

```bash
curl http://127.0.0.1:11434/api/tags
```

### Optional: give the model a short local name

The launch commands below use **`saluki`**. Create that alias once:

```bash
cat > /tmp/Saluki.Modelfile <<'MODEL'
FROM hf.co/ConwayResearch/Underdog-Saluki-27B-1.0:Q4_K_M
MODEL
ollama create saluki -f /tmp/Saluki.Modelfile
ollama run saluki
```

If you already created the `saluki` model earlier, skip this step. Confirm with `ollama list`.

## 3. Install Claude Code CLI

```bash
curl -fsSL https://claude.ai/install.sh | bash
claude --version
```

If `claude` is not found, restart your terminal and verify the CLI install directory is on `PATH`.

## 4. Build the Java MCP servers

From the **LocalMCP repository root**:

```bash
(cd mcp-servers/system-server  && mvn clean package)
(cd mcp-servers/git-server     && mvn clean package)
(cd mcp-servers/project-server && mvn clean package)
```

Find the executable JARs:

```bash
find mcp-servers -path '*/target/*.jar' -type f
```

Use the executable Spring Boot JAR for each server; exclude `original-*.jar` if present. **Do not manually launch the MCP servers for normal Claude Code use**: Claude Code starts them as stdio subprocesses from `.mcp.json`.

## 5. Configure Claude Code MCP servers

Create **`.mcp.json` in the repository root**. Replace `/ABS/PATH/TO/LocalMCP` and each `SERVER_JAR.jar` with your actual absolute paths from step 4:

```json
{
  "mcpServers": {
    "system": {
      "command": "java",
      "args": ["-jar", "/ABS/PATH/TO/LocalMCP/mcp-servers/system-server/target/SYSTEM_SERVER_JAR.jar"]
    },
    "git": {
      "command": "java",
      "args": ["-jar", "/ABS/PATH/TO/LocalMCP/mcp-servers/git-server/target/GIT_SERVER_JAR.jar"],
      "cwd": "/ABS/PATH/TO/LocalMCP"
    },
    "project": {
      "command": "java",
      "args": ["-jar", "/ABS/PATH/TO/LocalMCP/mcp-servers/project-server/target/PROJECT_SERVER_JAR.jar"],
      "env": {
        "PROJECT_ROOT": "/ABS/PATH/TO/LocalMCP"
      }
    }
  }
}
```

**Important — Git working directory:** the Git server implementation originally resolved the repository with `System.getProperty("user.dir")`. Some MCP launchers may not honor a `cwd` property in `.mcp.json`. For reliable behavior, **launch `claude` from the repository root**, or configure a wrapper script that `cd`s into that directory before executing `java -jar`. Do not rely on `cwd` alone without testing.

**Important — project root:** our project-server setup used `PROJECT_ROOT=/home/tarust/PycharmProjects/LocalMCP`; update it if the checkout lives elsewhere.

After starting Claude Code, run **`/mcp`** to check the servers and approve any required trust prompts.

## 6. Connect Claude Code directly to Ollama (try first)

Ollama provides an Anthropic-compatible endpoint in supported versions. From the repository root:

```bash
export ANTHROPIC_BASE_URL=http://127.0.0.1:11434
export ANTHROPIC_AUTH_TOKEN=ollama
export ANTHROPIC_API_KEY=""
claude --model saluki
```

If you did not create the alias, substitute the full Ollama model identifier for `saluki`.

### Alternative: Ollama's Claude launcher

```bash
ollama launch claude
```

This is a separate Ollama-managed integration path; the manual environment-variable approach above is easier to combine with the compatibility proxy.

## 7. Compatibility proxy (workaround used in our setup)

We also used a small **FastAPI / Uvicorn / HTTPX** proxy on **port 8000** to adapt Claude Code requests for Ollama. Its purpose was to normalize unsupported request details (including reasoning-effort values such as `high` and system-message formatting) before forwarding to Ollama.

> This section assumes the previously created proxy implementation is saved as `compatibility-proxy/proxy.py`. The uploaded README did not contain that source file. Do not run this section until it exists; the package install alone does not implement the proxy.

In terminal A:

```bash
cd compatibility-proxy
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn httpx
uvicorn proxy:app --host 127.0.0.1 --port 8000
```

In terminal B, from the LocalMCP root:

```bash
export ANTHROPIC_BASE_URL=http://127.0.0.1:8000
export ANTHROPIC_AUTH_TOKEN=ollama
export ANTHROPIC_API_KEY=""
claude --model saluki
```

**Use one base URL at a time:** `:11434` for direct Ollama or `:8000` for the compatibility proxy. The proxy must implement the Anthropic-compatible routes Claude Code calls; simply forwarding requests to Ollama's native `/api/chat` is not sufficient.

## 8. Daily startup

Once installed and built:

**Terminal A — Ollama** (if not already running as a service):

```bash
ollama serve
```

**Terminal B — proxy** (only if required):

```bash
cd /ABS/PATH/TO/LocalMCP/compatibility-proxy
source .venv/bin/activate
uvicorn proxy:app --host 127.0.0.1 --port 8000
```

**Terminal C — Claude Code**:

```bash
cd /ABS/PATH/TO/LocalMCP
export ANTHROPIC_BASE_URL=http://127.0.0.1:8000  # change to :11434 for direct mode
export ANTHROPIC_AUTH_TOKEN=ollama
export ANTHROPIC_API_KEY=""
claude --model saluki
```

Inside Claude Code:

```text
/mcp
```

Check that `system`, `git`, and `project` are connected, then try a read-only task such as asking Claude to summarize the repository structure.

## 9. Troubleshooting

| Symptom | Check / fix |
|---|---|
| `release version 21 not supported` | `mvn -version`; set `JAVA_HOME` to JDK 21 and rebuild. |
| `model not found` | `ollama list`; create the `saluki` alias or use the exact pulled model ID. |
| Cannot reach `localhost:11434` | Start `ollama serve` or check the Ollama service. |
| Cannot reach `localhost:8000` | Start the compatibility proxy, or switch `ANTHROPIC_BASE_URL` to `:11434`. |
| `Error loading ASGI app` | Confirm `compatibility-proxy/proxy.py` exists and exposes `app`. |
| MCP server disconnects | Verify the JAR path, Java 21, and that MCP stdio is not polluted by application logs. |
| Git tools operate on wrong repository | Launch Claude from the repo root; use a `cd` wrapper for the Git server if needed. |
| Project tools cannot locate files | Verify the `PROJECT_ROOT` environment variable. |
| CLI reports unsupported reasoning/system-message format | Use the compatibility proxy implementation that normalizes those fields. |
| Saluki runs slowly / out of memory | Check `ollama ps`, GPU/RAM utilization, and model quantization. |

## 10. Legacy Python agent (optional)

The original LocalMCP project also supported a **Python agent** using `qwen3:8b` by default. That path is separate from Claude Code CLI:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r agent/requirements.txt
python agent/agent_loop.py
```

If you use the legacy agent, its model and MCP subprocess configuration must be updated separately; the Claude Code environment variables do not automatically reconfigure `agent_loop.py`.

## Notes

- Keep Ollama and the proxy bound to loopback unless you deliberately configure network access and authentication.
- `.mcp.json` contains local absolute paths; update it when moving the repository.
- The exact proxy implementation and executable JAR names should be verified against your local files before calling this setup fully reproducible.
