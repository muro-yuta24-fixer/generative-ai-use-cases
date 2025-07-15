import logging

import boto3
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from strands import Agent
from strands.models import BedrockModel

from app import (
    FIXED_SYSTEM_PROMPT,
    StreamingRequest,
    clean_ws_directory,
    convert_unrecorded_message_to_strands_messages,
    create_session_id,
    create_ws_directory,
    extract_text,
    extract_tool_result,
    extract_tool_use,
    is_assistant,
    is_message,
    load_mcp_tools,
    stream_chunk,
    upload_file_to_s3_and_retrieve_s3_url,
)

router = APIRouter()


@router.post("/streaming")
async def streaming(request: StreamingRequest, req: Request):
    if req.app.state.mcp_tools is None:
        load_mcp_tools()

    async def generate():
        global session_id

        session_id = create_session_id()

        logging.info(f"New session {session_id}")

        create_ws_directory()

        session = boto3.Session(
            region_name=request.model.region,
        )

        bedrock_model = BedrockModel(
            model_id=request.model.modelId, boto_session=session
        )

        agent = Agent(
            system_prompt=f"{request.systemPrompt}\n{FIXED_SYSTEM_PROMPT}",
            messages=convert_unrecorded_message_to_strands_messages(request.messages),
            model=bedrock_model,
            tools=req.app.state.mcp_tools + [upload_file_to_s3_and_retrieve_s3_url],
            callback_handler=None,
        )

        async for event in agent.stream_async(request.userPrompt):
            if is_message(event):
                if is_assistant(event):
                    text = extract_text(event)
                    tool_use = extract_tool_use(event)

                    if text is not None and tool_use is not None:
                        yield stream_chunk("", f"{text}\n")
                        yield stream_chunk(
                            "", f"```\n{tool_use['name']}: {tool_use['input']}\n```\n"
                        )
                    elif text is not None:
                        yield stream_chunk(text, None)
                    else:
                        yield stream_chunk(
                            "", f"```\n{tool_use['name']}: {tool_use['input']}\n```\n"
                        )
                else:
                    tool_result = extract_tool_result(event)
                    if len(tool_result) > 200:
                        tool_result = tool_result[:200] + "..."
                    yield stream_chunk("", f"```\n{tool_result}\n```\n")

        clean_ws_directory()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
    )
