from enum import Enum
from agents import Agent, set_default_openai_key
from pydantic import BaseModel, Field
from config import settings
from typing import List
from libs.vector_search import get_manual_documents

# Set API key
set_default_openai_key(settings.OPENAI_API_KEY)

class checkType(str, Enum):
    question_to_user = "question_to_user"
    procedure = "procedure"

class LocatingItem(BaseModel):
    type: checkType = Field(
        ...,
        description="アラーム・症状・エラーメッセージを整理した問題の解釈文"
    )

    check_content: str = Field(
        ...,
        description="切り分けのための確認項目"
    )

class LocatingOutput(BaseModel):
    checks_in_order: List[LocatingItem] = Field(
        ...,
        description=(
            "切り分けのための確認項目のリスト"
        ),
    )

LOCATING_SYSTEM_PROMPT = f"""
あなたはネットワークトラブルシューティング支援システムの Locating Agent です。

目的:
Identify Agent が出した「問題の解釈」と「分類(cant_connect / connection_drops / network_is_slow)」をもとに、
原因を断定せずに、問題箇所を特定するための論理的な順序付き確認手段(診断計画)を作成してください。

本フェイズ(Step 3)の考え方:
- 定義された問題を、可能なら再現したうえで、単一デバイス/接続/アプリに隔離する(divide-and-conquer)。
- できるだけ変数を減らし、テストで除外していく。
- 直前の変更や周辺環境(熱、電気、時間帯、電磁ノイズ等)も変化要因として考慮する。
- 別端末・別アプリで再現できるかを確認し、範囲(1端末か、複数端末か、特定リソースだけか)を縮める。
- 影響範囲が広い場合は、共有セグメント/インフラを疑い、変数を減らして最小構成で切り分ける。

制約(重要):
- 根本原因の推定や断定はしない。
- 修正手順や設定変更は提示しない。
- 実施すべき確認手段を“順序付き”で提示する。
- 情報不足はユーザへの質問(question_to_user)として出す。

マニュアル利用:
- 提供されたマニュアル抜粋を参照して診断計画を組み立てる。
- マニュアル外の独自手順を混ぜない。

出力ルール:
- 出力は JSON のみ(Pydanticスキーマ準拠)
- 余計なキーは出力しない
"""

LOCATING_USER_PROMPT = """
以下が検索されたマニュアル抜粋です:

{manual}
"""

create_locating_agent = Agent(
    name="Locationg_Agent",
    instructions=LOCATING_SYSTEM_PROMPT,
    model="gpt-4.1",
    output_type=LocatingOutput
)