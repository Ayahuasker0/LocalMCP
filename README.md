# LocalMCP

A local AI agent that uses **Ollama** for language-model inference and connects to **Java Spring Boot MCP servers** to work with system, Git, and project tools.

## Architecture

```text
User
  |
  v
Python agent (agent/agent_loop.py)
  |-- Ollama (qwen3:8b) — local LLM
  |-- system-server — system tools
  |-- git-server — Git operations
  `-- project-server — project tools
```

The MCP servers are built as executable Spring Boot JARs. The Python agent is the entry point.

## Prerequisites

- **Java 21 JDK**
- **Maven** (`mvn`)
- **Python 3** and `pip` (preferably in a virtual environment)
- **Git**
- **Ollama** with the `qwen3:8b` model

The commands below target Ubuntu/Linux. Run them from the **LocalMCP repository root** unless a step explicitly changes directories.

## 1. Install Java and Maven

```bash
sudo apt update
sudo apt install -y openjdk-21-jdk maven python3 python3-venv python3-pip git
```

Check the installed versions:

```bash
java -version
mvn -version
python3 --version
```

Ensure Maven uses **JDK 21**. If several Java versions are installed, check `JAVA_HOME` and your active Java selection.

## 2. Install Ollama and download the model

Install Ollama using its official installer:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Download the model:

```bash
ollama pull qwen3:8b
```

Verify that it works:

```bash
ollama run qwen3:8b
```

Exit the interactive model session when finished. The model size can be changed depending on available hardware, but the agent configuration must then use the same model name.

**Ollama must be running when the agent starts.** On installations without an active Ollama service, start it in a separate terminal:

```bash
ollama serve
```

## 3. Build the MCP servers

From the repository root:

```bash
(cd mcp-servers/system-server && mvn clean package)
(cd mcp-servers/git-server && mvn clean package)
(cd mcp-servers/project-server && mvn clean package)
```

Each command should produce a JAR under the corresponding server's `target/` directory.

> **Important:** If you rebuild a server, restart the agent so it can launch the updated JAR.

## 4. Install Python dependencies

From the repository root, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r agent/requirements.txt
```

## 5. Check agent configuration

Before starting, review the Python agent's MCP server launch configuration and confirm that:

- The configured model is `qwen3:8b`.
- Ollama is reachable at the endpoint expected by the agent.
- Each MCP server command points to the JAR actually generated in `mcp-servers/<server>/target/`.
- The Java processes have the intended working directories.

The uploaded README does not specify configuration variable names or a config file, so this guide does not assume any particular environment-variable interface.

### Git MCP server: working directory matters

In the current implementation, JGit opens the repository using:

```java
System.getProperty("user.dir")
```

**Launch the Git MCP server with the target Git repository root as its working directory.** Set that working directory in the Python client's subprocess configuration; otherwise Git operations may target the wrong directory or fail.

## 6. Start the agent

Make sure Ollama is running and the three server JARs have been built. From the repository root:

```bash
source .venv/bin/activate
python agent/agent_loop.py
```

The Python agent should start and connect to the configured MCP servers. You can then interact with it in the terminal.

## Project layout

```text
LocalMCP/
├── agent/
│   ├── agent_loop.py
│   └── requirements.txt
├── mcp-servers/
│   ├── system-server/
│   ├── git-server/
│   └── project-server/
└── README.md
```

Only the main files and directories needed for setup are shown.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| `release version 21 not supported` | Maven is using an older JDK. Check `mvn -version` and `JAVA_HOME`. |
| `java: command not found` | Install JDK 21 and verify your `PATH`. |
| `mvn: command not found` | Install Maven. |
| Python package import error | Activate `.venv` and reinstall `agent/requirements.txt`. |
| Ollama connection refused | Ensure Ollama is running; check `ollama serve` or the installed service. |
| Ollama model not found | Run `ollama pull qwen3:8b` and check the model name in agent configuration. |
| MCP server JAR not found | Rebuild that server and verify the JAR path configured in the agent. |
| Git tools use the wrong repository | Set the Git server process working directory to the intended repository root. |
| Spring Boot server fails to start | Inspect the complete `Caused by:` chain in the Java stack trace and verify its required configuration. |

## Quick start (after initial installation)

From the repository root:

```bash
# Start Ollama separately if it is not already running.
source .venv/bin/activate
python agent/agent_loop.py
```

## Notes

- The default model in this guide is **`qwen3:8b`**.
- The agent runs locally; Ollama inference does not require a cloud-hosted model.
- Build commands, server startup, and model selection may need adjustment if the project's implementation changes.
