import logging
from typing import Dict, List
from fastapi import APIRouter, Request, Response, status
from pydantic import BaseModel

from mcp_manager import McpServerConfig, make_mcp_client

router = APIRouter()


class McpServerAddRequest(BaseModel):
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]


@router.post("/mcp-server")
async def add_mcp_server(request: McpServerAddRequest, req: Request):
    mcp_server_config = McpServerConfig(
        {
            "command": request.command,
            "args": request.args,
            "env": request.env,
        }
    )

    mcp_client = make_mcp_client(mcp_server_config)

    mcp_client.start()

    new_tools = mcp_client.list_tools_sync()

    if req.app.state.mcp_tools is None:
        req.app.state.mcp_tools = []

    req.app.state.mcp_tools += new_tools

    logging.info(f"Loaded {len(new_tools)} MCP tools from {request.name}")

    # return {
    #     "message": f"Successfully loaded {len(new_tools)} MCP tools",
    # }
    return Response(
        content={
            "message": f"Successfully loaded {len(new_tools)} MCP tools",
        },
        status_code=status.HTTP_201_CREATED,
    )
