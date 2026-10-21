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

    def __init__(self, session: ClientSession):
        self.session = session
        self.llm = AsyncClient(host="http://localhost:11434")
        self.tools = []

        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are a mean but helpful AI development assistant. "
                    "Use MCP tools to inspect the local project. "
                    "Never invent Git information."
                    "Help user to understand what accesses do you have"
                    "Add old school joke in the end of every result"
                )
            }
        ]

    if False: ''' Commented it out because of decisions is to be made by mcp_manager
    async def initialize(self):
        """Discover available MCP tools."""

        response = await self.session.list_tools()

        for tool in response.tools:
            self.tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema
                }
            })

        print("\nAvailable MCP tools:")

        for tool in self.tools:
            print(f"  - {tool['function']['name']}")
    '''
    async def chat(self, user_message: str):
        """Process user input through the agent loop."""

        self.messages.append({
            "role": "user",
            "content": user_message
        })

        for round_number in range(MAX_TOOL_ROUNDS):

            response = await self.llm.chat(
                model=MODEL,
                messages=self.messages,
                tools=self.tools
            )

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
                    result = await self.session.call_tool(
                        name,
                        arguments
                    )

                    content = "\n".join(
                        item.text
                        for item in result.content
                        if item.type == "text"
                    )

                    if result.isError:
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