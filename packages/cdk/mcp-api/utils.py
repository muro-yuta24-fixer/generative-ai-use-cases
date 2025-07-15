import json
import logging
import pathlib
import shutil
from typing import Any, Dict, List, Optional
from uuid import uuid4

from config import WORKSPACE_DIR


def stream_chunk(text: str, trace: Optional[str]) -> str:
    return json.dumps({"text": text, "trace": trace}, ensure_ascii=False) + "\n"


def is_message(event: Dict[str, Any]) -> bool:
    return "message" in event


def is_assistant(event: Dict[str, Any]) -> bool:
    return event["message"]["role"] == "assistant"


def extract_text(event: Dict[str, Any]) -> Optional[str]:
    contents = event["message"]["content"]

    for c in contents:
        if "text" in c:
            return c["text"]
    return None


def extract_tool_use(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    contents = event["message"]["content"]

    for c in contents:
        if "toolUse" in c:
            tool_use = c["toolUse"]
            return {"name": tool_use["name"], "input": tool_use["input"]}
    return None


def extract_tool_result(event: Dict[str, Any]) -> str:
    res = ""

    contents = event["message"]["content"]

    for c in contents:
        if "toolResult" in c:
            res_contents = c["toolResult"]["content"]

            for t in res_contents:
                if "text" in t:
                    res += t["text"]
    return res


def create_session_id() -> str:
    return str(uuid4())


def create_ws_directory() -> None:
    logging.info("Create ws directory")
    pathlib.Path(WORKSPACE_DIR).mkdir(exist_ok=True)


def clean_ws_directory() -> None:
    logging.info("Clean ws directory...")
    shutil.rmtree(WORKSPACE_DIR)


def convert_unrecorded_message_to_strands_messages(
    messages: List[Dict[str, str]],
) -> List[Dict[str, Any]]:
    return list(
        map(lambda m: {"role": m.role, "content": [{"text": m.content}]}, messages)
    )

