import asyncio
import json
from pathlib import Path

from ollama import AsyncClient
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SERVER_JAR = (
    PROJECT_ROOT
    / "mcp-servers"
    / "system-server"
    / "target"
    / "system-server-0.0.1-SNAPSHOT.jar"
)

MODEL = "qwen3:8b"


async def main():

    llm = AsyncClient(host="http://localhost:11434")

    server_params = StdioServerParameters(
        command="java",
        args=["-jar", str(SERVER_JAR)]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            # Discover MCP tools
            tools_response = await session.list_tools()

            # Convert MCP tools to Ollama tool definitions
            tools = []

            for tool in tools_response.tools:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.inputSchema
                    }
                })

            print("Available tools:", [t["function"]["name"] for t in tools])

            messages = [
                {
                    "role": "user",
                    "content": "What is 125 multiplied by 37? Use the calculator."
                }
            ]

            # Ask LLM
            response = await llm.chat(
                model=MODEL,
                messages=messages,
                tools=tools
            )

            messages.append(response.message)

            # Execute requested tools
            for tool_call in response.message.tool_calls or []:

                name = tool_call.function.name
                arguments = tool_call.function.arguments

                print(f"Executing: {name}({arguments})")

                result = await session.call_tool(
                    name,
                    arguments=arguments
                )

                content = "\n".join(
                    item.text
                    for item in result.content
                    if item.type == "text"
                )

                messages.append({
                    "role": "tool",
                    "tool_name": name,
                    "content": content
                })

            # Send tool results back to LLM
            final_response = await llm.chat(
                model=MODEL,
                messages=messages
            )

            print("\nAssistant:", final_response.message.content)


if __name__ == "__main__":
    asyncio.run(main())