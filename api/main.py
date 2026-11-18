import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# The agent module uses flat imports (from mcp_manager import ...),
# so put its directory on sys.path to import it as a package.
sys.path.insert(0, str(PROJECT_ROOT / "agent"))

from agent_loop import MCPAgent  # noqa: E402
from mcp_manager import MCPManager  # noqa: E402


def _jar(server: str) -> str:
    return str(
        PROJECT_ROOT
        / "mcp-servers"
        / f"{server}-server"
        / "target"
        / f"{server}-server-0.0.1-SNAPSHOT.jar"
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    manager = MCPManager()
    try:
        await manager.connect(
            name="system",
            command="java",
            args=["-jar", _jar("system")],
        )
        await manager.connect(
            name="git",
            command="java",
            args=["-jar", _jar("git")],
            cwd=str(PROJECT_ROOT),
        )
        await manager.connect(
            name="project",
            command="java",
            args=["-jar", _jar("project")],
            cwd=str(PROJECT_ROOT),
            env={**os.environ, "PROJECT_ROOT": str(PROJECT_ROOT)},
        )
        app.state.agent = MCPAgent(manager)
    except Exception:
        await manager.close()
        raise
    yield
    await manager.close()


app = FastAPI(
    title="Local MCP Agent API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.routes.chat import router  # noqa: E402

app.include_router(router, prefix="/api")
