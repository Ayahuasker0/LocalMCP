import asyncio
import json
from pathlib import Path

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


async def main():

    if not SERVER_JAR.exists():
        raise FileNotFoundError(
            f"MCP server JAR not found: {SERVER_JAR}"
        )

    server_params = StdioServerParameters(
        command="java",
        args=[
            "-agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=*:5005",
            "-jar",
            str(SERVER_JAR)
        ]
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            # 1. Initialize the MCP connection
            await session.initialize()

            print("Connected to MCP server!")

            # 2. Discover tools
            tools = await session.list_tools()

            print("\nAvailable tools:")

            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # 3. Execute calculator
            result = await session.call_tool(
                "calculate",
                arguments={
                    "a": 125,
                    "b": 37,
                    "operation": "multiply"
                }
            )

            print("\nCalculator result:")
            print(result)

            # 4. Get system information
            result = await session.call_tool(
                "get_system_info",
                arguments={}
            )

            print("\nSystem information:")
            print(result)

            # 5. Get current time
            result = await session.call_tool(
                "get_current_time",
                arguments={}
            )

            print("\nCurrent time:")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())