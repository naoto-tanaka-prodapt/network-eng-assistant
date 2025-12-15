from enum import Enum
from agents import Agent, set_default_openai_key
from pydantic import BaseModel, Field
from typing import List
from config import settings

set_default_openai_key(settings.OPENAI_API_KEY)

class MediaHint(str, Enum):
    physical = "physical"
    switch = "switch"
    network = "network"
    unknown = "unknown"

class IdentificationOutput(BaseModel):
    facts: str = Field(
        ...,
        description="入力から読み取れる事実（アラーム/症状/エラー/観測）を短文で列挙。推測は禁止。"
    )
    extracted_keywords: List[str] = Field(
        ...,
        description="検索に使えるキーワード（機器/ポート/プロトコル/手法）。重複なし。"
    )
    media_hint: MediaHint = Field(
        ...,
        description="physical/network/switch の当たり（入力に根拠が無ければ unknown）"
    )

IDENTIFY_SYSTEM_PROMPT = """
あなたはネットワークトラブルシューティング支援システムの Identify Agent です。

目的：
ユーザ入力（アラーム/症状/エラーメッセージ）を解釈し、「何が起きている問題か」を定義する。
あなたの役割は Identify(問題定義とキーワード抽出)まで。原因分析・対処提案・テスト手順の提案は禁止。

実施内容：
1) 入力から読み取れる事実(facts)を列挙（推測しない）
2) media_hintはphysical/network/switch のどこに問題かの当たり。入力に根拠が無ければ unknown。
3) extracted_keywordsは入力された情報をもとに検索に使えるキーワードを抽出する。最大10個。

厳守：
- 入力にないことは書かない。
- 原因推定、対処提案、コマンド提示、詳細なテスト手順の提案は禁止
- 出力は指定スキーマに一致する JSON のみ
"""

IDENTIFY_USER_PROMPT = """
以下がネットワークエンジニアが入力したアラーム、症状、エラーメッセージです:
{error_message}
"""

create_identify_agent = Agent(
    name="Identify_Agent",
    instructions=IDENTIFY_SYSTEM_PROMPT,
    model="gpt-4.1",
    output_type=IdentificationOutput
)
