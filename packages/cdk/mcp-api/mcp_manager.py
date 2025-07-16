"""
MCPマネージャーモジュール

Model Context Protocol (MCP) サーバーの管理とツールの読み込みを担当。
"""

import json
import logging
from typing import List, Dict, Any

from strands.tools.mcp import MCPAgentTool, MCPClient
from mcp import stdio_client, StdioServerParameters

from config import UV_ENV


class McpServerConfig:
    command: str
    args: List[str]
    env: Dict[str, str]

    def __init__(self, config: Dict[Any, Any]) -> None:
        self.command = config["command"]

        if "args" in config:
            self.args = config["args"]
        else:
            self.args = []

        if "env" in config:
            self.env = config["env"]
        else:
            self.env = {}


def safe_parse_mcp_json() -> List[McpServerConfig]:
    """安全にmcp.jsonファイルをパースする。

    mcp.jsonファイルからMCPサーバーの設定を読み込み、
    必要な情報を抽出してリスト形式で返す。

    Returns:
        List[Dict[str, Any]]: MCPサーバー設定のリスト

    Raises:
        Exception: mcpServersが定義されていない場合
    """
    res: List[McpServerConfig] = []

    with open("mcp.json", "r") as f:
        mcp_json = json.loads(f.read())

        if "mcpServers" not in mcp_json:
            raise Exception("mcpServers not defined in mcp.json")

        mcp_servers = mcp_json["mcpServers"]
        mcp_server_names = mcp_servers.keys()

        for server_name in mcp_server_names:
            server = mcp_servers[server_name]
            res.append(McpServerConfig(server))

    return res


def make_mcp_client(server: McpServerConfig) -> MCPClient:
    """サーバー設定からMCPクライアントを作成する。

    指定されたサーバー設定に基づいて、MCPクライアントを初期化する。

    Args:
        server: サーバー設定情報（command, args, envを含む）

    Returns:
        MCPClient: 初期化されたMCPクライアント
    """

    def spawn():
        """サーバープロセスを生成する内部関数。"""
        return stdio_client(
            StdioServerParameters(
                command=server.command,
                args=server.args,
                env={
                    **UV_ENV,
                    **server.env,
                },
            )
        )

    return MCPClient(spawn)


def load_mcp_tools() -> List[MCPAgentTool]:
    """すべてのMCPツールを読み込む。

    mcp.jsonからサーバー設定を読み込み、各サーバーに接続して
    利用可能なツールを取得する。

    Returns:
        List[Any]: 読み込まれたすべてのMCPツールのリスト
    """
    try:
        mcp_servers = safe_parse_mcp_json()
        mcp_clients = [make_mcp_client(s) for s in mcp_servers]

        for c in mcp_clients:
            c.start()

        # sum関数の型エラー回避
        empty_list: List[MCPAgentTool] = []

        # Flatten the tools
        mcp_tools = sum([c.list_tools_sync() for c in mcp_clients], empty_list)

        logging.info(f"Loaded {len(mcp_tools)} MCP tools")
        return mcp_tools
    except Exception as e:
        logging.error(f"Failed to load MCP tools: {e}")
        return []
