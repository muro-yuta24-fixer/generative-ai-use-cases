import uvicorn
import logging
from fastapi import FastAPI, Response, status

from routers import streaming
from mcp_manager import load_mcp_tools

app = FastAPI()

# Shared MCP clients
app.state.mcp_tools = None


@app.get("/")
async def healthcheck():
    return Response(status_code=status.HTTP_200_OK)


app.include_router(streaming.router)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Pre-load MCP tools at startup
    app.state.mcp_tools = load_mcp_tools()

    uvicorn.run(app, host="0.0.0.0", port=8080)
