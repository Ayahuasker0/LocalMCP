import asyncio
import os
import json
from pathlib import Path

from ollama import AsyncClient
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp_manager import MCPManager


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SERVER_JAR = (
    PROJECT_ROOT
    / "mcp-servers"
    / "system-server"
    / "target"
    / "system-server-0.0.1-SNAPSHOT.jar"
)

MODEL = "qwen3:8b"

MAX_TOOL_ROUNDS = 67


class MCPAgent:

    def __init__(self, manager: MCPManager):
        self.manager = manager
        self.llm = AsyncClient(host="http://localhost:11434")

        # Get all tools discovered from MCP servers
        self.tools = manager.get_tools()

        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI coding assistant with access "
                    "to local MCP tools. "
                    "When asked to search code, use search_project_code. "
                    "When asked about Git, use the Git tools. "
                    "Never invent tool results."
                )
            }
        ]

        print(
            "[DEBUG] Agent tools:",
            [tool["function"]["name"] for tool in self.tools]
        )

    async def chat(self, user_message: str):
        """Process user input through the agent loop."""

        self.messages.append({
            "role": "user",
            "content": user_message
        })

        for round_number in range(MAX_TOOL_ROUNDS):

            import json

            print("\n[DEBUG] Tools sent to Ollama:")
            print(json.dumps(self.tools, indent=2))

            response = await self.llm.chat(
                model=MODEL,
                messages=self.messages,
                tools=self.tools
            )
            print("\n[DEBUG] LLM response:")
            print("Content:", response.message.content)
            print("Tool calls:", response.message.tool_calls)

            self.messages.append(response.message)

            tool_calls = response.message.tool_calls or []

            # No tool calls -> final answer
            if not tool_calls:
                return response.message.content

            print(
                f"\n[Tool round {round_number + 1}]"
            )

            # Execute requested MCP tools
            for tool_call in tool_calls:

                name = tool_call.function.name
                arguments = tool_call.function.arguments

                print(f"Calling {name}({arguments})")

                try:
                    result = await self.manager.call_tool(
                        name,
                        arguments
                    )

                    content = "\n".join(
                        item.text
                        for item in result.content
                        if item.type == "text"
                    )

                    if result.is_error:
                        content = f"Tool error: {content}"

                except Exception as e:
                    content = f"Tool execution failed: {e}"

                self.messages.append({
                    "role": "tool",
                    "tool_name": name,
                    "content": content
                })

                print(f"Result: {content}")

        return (
            "Maximum tool rounds reached. "
            "Unable to complete the request."
        )


async def main():

    manager = MCPManager()

    try:
        await manager.connect(
            name="system",
            command="java",
            args=[
                "-jar",
                str(
                    PROJECT_ROOT
                    / "mcp-servers/system-server/target/"
                    "system-server-0.0.1-SNAPSHOT.jar"
                )
            ]
        )

        await manager.connect(
            name="git",
            command="java",
            args=[
                "-jar",
                str(
                    PROJECT_ROOT
                    / "mcp-servers/git-server/target/"
                    "git-server-0.0.1-SNAPSHOT.jar"
                )
            ],
            cwd=str(PROJECT_ROOT)
        )

        await manager.connect(
            name="project",
            command="java",
            args=[
                "-jar",
                str(
                    PROJECT_ROOT
                    / "mcp-servers"
                    / "project-server"
                    / "target"
                    / "project-server-0.0.1-SNAPSHOT.jar"
                )
            ],
            cwd=str(PROJECT_ROOT),
            env={
                **os.environ,
                "PROJECT_ROOT": str(PROJECT_ROOT)
            }
        )


        agent = MCPAgent(manager)

        print("\nAvailable tools:")
        for tool in manager.get_tools():
            print("-", tool["function"]["name"])

        while True:

            user_input = await asyncio.to_thread(
                input,
                "\nYou: "
            )

            if user_input.lower() in ("exit", "quit"):
                break

            if not user_input.strip():
                continue

            answer = await agent.chat(user_input)

            print(f"\nAssistant: {answer}")

    finally:
        await manager.close()

if __name__ == "__main__":
    asyncio.run(main())