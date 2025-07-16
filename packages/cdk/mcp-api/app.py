"""メインアプリケーションモジュール

FastAPIを使用したMCP APIサーバーのエントリポイント。
"""

import uvicorn
import logging
from fastapi import FastAPI, Response, status

from routers import mcp_server_controller, streaming
from mcp_manager import load_mcp_tools

app = FastAPI()
"""メインのFastAPIアプリケーションインスタンス。"""

# Shared MCP clients
app.state.mcp_tools = None
"""共有MCPツールのストレージ。アプリケーション全体で利用。"""


@app.get("/")
async def healthcheck():
    """ヘルスチェックエンドポイント。

    サーバーの稼働状態を確認するためのエンドポイント。

    Returns:
        Response: HTTP 200 OKステータスのレスポンス
    """
    return Response(status_code=status.HTTP_200_OK)


app.include_router(streaming.router)
app.include_router(mcp_server_controller.router)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Pre-load MCP tools at startup
    app.state.mcp_tools = load_mcp_tools()

    uvicorn.run(app, host="0.0.0.0", port=8080)
