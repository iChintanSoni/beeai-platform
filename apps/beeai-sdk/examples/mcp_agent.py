# Copyright 2025 © BeeAI a Series of LF Projects, LLC
# SPDX-License-Identifier: Apache-2.0

import json
from collections.abc import AsyncGenerator
from typing import Annotated

from a2a.types import Message
from mcp import ClientSession

from beeai_sdk.a2a.extensions.auth.oauth import OAuthExtensionServer, OAuthExtensionSpec
from beeai_sdk.a2a.extensions.services.mcp import MCPServiceExtensionServer, MCPServiceExtensionSpec
from beeai_sdk.a2a.types import RunYield
from beeai_sdk.server import Server
from beeai_sdk.server.context import RunContext

server = Server()


@server.agent()
async def mcp_agent(
    message: Message,
    context: RunContext,
    oauth: Annotated[OAuthExtensionServer, OAuthExtensionSpec.single_demand()],
    mcp: Annotated[
        MCPServiceExtensionServer,
        MCPServiceExtensionSpec.single_demand(),
    ],
) -> AsyncGenerator[RunYield, Message]:
    """Lists tools"""

    if not mcp:
        yield "MCP extension hasn't been activated, no tools are available"
        return

    async with mcp.create_client() as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool("notion-get-self", {})

        json_data = json.loads(result.content[0].text)
        bot_owner_user_name = json_data.get("bot", {}).get("owner", {}).get("user", {}).get("name")
        yield bot_owner_user_name


if __name__ == "__main__":
    server.run()
