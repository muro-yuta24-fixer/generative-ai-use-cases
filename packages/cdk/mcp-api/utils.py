"""ユーティリティモジュール

ストリーミング処理やメッセージ処理のヘルパー関数を提供するモジュール。
"""
import json
import logging
import pathlib
import shutil
from typing import Any, Dict, List, Optional
from uuid import uuid4

from config import WORKSPACE_DIR


def stream_chunk(text: str, trace: Optional[str]) -> str:
    """ストリーミングチャンクを作成する。
    
    テキストとトレース情報をJSON形式でシリアライズする。
    
    Args:
        text: ストリーミングするテキスト
        trace: トレース情報（オプション）
        
    Returns:
        str: JSON形式のストリーミングチャンク
    """
    return json.dumps({"text": text, "trace": trace}, ensure_ascii=False) + "\n"


def is_message(event: Dict[str, Any]) -> bool:
    """イベントがメッセージかどうかを判定する。
    
    Args:
        event: イベントディクショナリ
        
    Returns:
        bool: メッセージの場合True
    """
    return "message" in event


def is_assistant(event: Dict[str, Any]) -> bool:
    """メッセージがアシスタントからのものか判定する。
    
    Args:
        event: イベントディクショナリ
        
    Returns:
        bool: アシスタントメッセージの場合True
    """
    return event["message"]["role"] == "assistant"


def extract_text(event: Dict[str, Any]) -> Optional[str]:
    """イベントからテキストを抽出する。
    
    メッセージのコンテンツからテキスト部分を探して返す。
    
    Args:
        event: イベントディクショナリ
        
    Returns:
        Optional[str]: テキストがあればその内容、なければNone
    """
    contents = event["message"]["content"]

    for c in contents:
        if "text" in c:
            return c["text"]
    return None


def extract_tool_use(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """イベントからツール使用情報を抽出する。
    
    メッセージのコンテンツからツール使用情報を探して返す。
    
    Args:
        event: イベントディクショナリ
        
    Returns:
        Optional[Dict[str, Any]]: ツール名と入力を含む辞書、またはNone
    """
    contents = event["message"]["content"]

    for c in contents:
        if "toolUse" in c:
            tool_use = c["toolUse"]
            return {"name": tool_use["name"], "input": tool_use["input"]}
    return None


def extract_tool_result(event: Dict[str, Any]) -> str:
    """イベントからツール実行結果を抽出する。
    
    メッセージのコンテンツからツール実行結果を取得して連結する。
    
    Args:
        event: イベントディクショナリ
        
    Returns:
        str: ツール実行結果のテキスト
    """
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
    """新しいセッションIDを生成する。
    
    UUID4を使用して一意のセッションIDを生成する。
    
    Returns:
        str: 生成されたセッションID
    """
    return str(uuid4())


def create_ws_directory() -> None:
    """作業ディレクトリを作成する。
    
    Lambda環境でファイルを一時保存するためのディレクトリを作成する。
    """
    logging.info("Create ws directory")
    pathlib.Path(WORKSPACE_DIR).mkdir(exist_ok=True)


def clean_ws_directory() -> None:
    """作業ディレクトリを削除する。
    
    セッション終了時に作業ディレクトリとその内容を削除する。
    """
    logging.info("Clean ws directory...")
    shutil.rmtree(WORKSPACE_DIR)


def convert_unrecorded_message_to_strands_messages(
    messages: List[Dict[str, str]],
) -> List[Dict[str, Any]]:
    """メッセージフォーマットを変換する。
    
    UnrecordedMessage形式からStrandsライブラリが期待する形式に変換する。
    
    Args:
        messages: UnrecordedMessageのリスト
        
    Returns:
        List[Dict[str, Any]]: Strands形式のメッセージリスト
    """
    return list(
        map(lambda m: {"role": m.role, "content": [{"text": m.content}]}, messages)
    )

