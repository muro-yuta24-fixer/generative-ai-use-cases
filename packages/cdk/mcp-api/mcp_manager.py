import json
import logging
from typing import List, Dict, Any

from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

from config import UV_ENV


def safe_parse_mcp_json() -> List[Dict[str, Any]]:
    res: List[Dict[str, Any]] = []

    with open("mcp.json", "r") as f:
        mcp_json = json.loads(f.read())

        if "mcpServers" not in mcp_json:
            raise Exception("mcpServers not defined in mcp.json")

        mcp_servers = mcp_json["mcpServers"]
        mcp_server_names = mcp_servers.keys()

        for server_name in mcp_server_names:
            server = mcp_servers[server_name]
            res.append(
                {
                    "command": server["command"],
                    "args": server["args"] if "args" in server else [],
                    "env": server["env"] if "env" in server else {},
                }
            )

    return res


def make_mcp_client(server: Dict[str, Any]) -> MCPClient:
    def spawn():
        return stdio_client(
            StdioServerParameters(
                command=server["command"],
                args=server["args"],
                env={
                    **UV_ENV,
                    **server["env"],
                },
            )
        )

    return MCPClient(spawn)


def load_mcp_tools() -> List[Any]:
    try:
        mcp_servers = safe_parse_mcp_json()
        mcp_clients = [make_mcp_client(s) for s in mcp_servers]

        for c in mcp_clients:
            c.start()

        # Flatten the tools
        mcp_tools = sum([c.list_tools_sync() for c in mcp_clients], [])

        logging.info(f"Loaded {len(mcp_tools)} MCP tools")
        return mcp_tools
    except Exception as e:
        logging.error(f"Failed to load MCP tools: {e}")
        return []

