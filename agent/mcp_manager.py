from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPManager:

    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.sessions = {}
        self.tools = {}

    async def connect(
            self,
            name,
            command,
            args,
            cwd=None,
            env=None
    ):

        params = StdioServerParameters(
            command=command,
            args=args,
            cwd=cwd,
            env=env
        )

        read, write = await self.exit_stack.enter_async_context(
            stdio_client(params)
        )

        session = await self.exit_stack.enter_async_context(
            ClientSession(read, write)
        )

        await session.initialize()

        self.sessions[name] = session

        response = await session.list_tools()

        for tool in response.tools:

            if tool.name in self.tools:
                raise ValueError(
                    f"Duplicate MCP tool name: {tool.name}"
                )

            self.tools[tool.name] = {
                "server": name,
                "definition": {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.input_schema
                    }
                }
            }

        print(f"Connected to {name}")

    def get_tools(self):
        return [
            entry["definition"]
            for entry in self.tools.values()
        ]

    async def call_tool(self, name, arguments):

        if name not in self.tools:
            raise ValueError(f"Unknown tool: {name}")

        server_name = self.tools[name]["server"]
        session = self.sessions[server_name]

        return await session.call_tool(
            name,
            arguments=arguments
        )

    async def list_resources(self, server_name):
        session = self.sessions[server_name]
        result = await session.list_resources()
        return result.resources

    async def read_resource(self, server_name, uri):
        session = self.sessions[server_name]
        return await session.read_resource(uri)

    async def list_prompts(self, server_name):
        session = self.sessions[server_name]
        result = await session.list_prompts()
        return result.prompts

    async def get_prompt(self, server_name, name, arguments=None):
        session = self.sessions[server_name]

        return await session.get_prompt(
            name,
            arguments=arguments or {}
        )

    async def close(self):
        await self.exit_stack.aclose()