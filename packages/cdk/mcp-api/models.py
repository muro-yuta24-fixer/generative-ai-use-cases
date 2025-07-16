"""データモデル定義モジュール

APIリクエスト/レスポンスのデータモデルを定義するモジュール。
Pydanticを使用してバリデーションとシリアライゼーションを行う。
"""
from pydantic import BaseModel
from typing import List


class UnrecordedMessage(BaseModel):
    """メッセージモデル。
    
    LLMとの会話履歴に含まれる各メッセージを表現。
    
    Attributes:
        role: メッセージの送信者ロール（'user'または'assistant'）
        content: メッセージの内容
    """
    role: str
    content: str


class Model(BaseModel):
    """モデル設定。
    
    使用するLLMモデルの設定情報。
    
    Attributes:
        modelId: BedrockモデルID
        region: AWSリージョン
    """
    modelId: str
    region: str


class StreamingRequest(BaseModel):
    """ストリーミングリクエストモデル。
    
    ストリーミングAPIエンドポイントへのリクエストデータ。
    
    Attributes:
        systemPrompt: システムプロンプト（LLMの挙動を制御）
        userPrompt: ユーザーからの現在のプロンプト
        messages: 過去の会話履歴
        model: 使用するモデルの設定
    """
    systemPrompt: str
    userPrompt: str
    messages: List[UnrecordedMessage]
    model: Model

