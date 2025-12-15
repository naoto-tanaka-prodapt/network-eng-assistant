from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field
from agents import Agent


class GuideBasisItem(BaseModel):
    start_page: str = Field(..., description="参照したガイドチャンクの開始ページ")
    last_page: str = Field(..., description="参照したガイドチャンクの終了ページ")
    chapter: str = Field(..., description="参照したガイドチャンクの章")
    note: Optional[str] = Field(
        default=None,
        description="何の根拠として使ったか(例: '安全確認', 'テスト手順', '判断基準')"
    )


class SafetyCheckItem(BaseModel):
    content: str = Field(..., description="作業前/作業中に必ず実施する安全確認項目")
    guide_basis: GuideBasisItem = Field(
        ...,
        description="この安全確認の根拠として参照したガイドchunk"
    )


class LocatingItem(BaseModel):
    test_content: str = Field(..., description="切り分けのための確認項目（マニュアルに基づく）")
    purpose: str = Field(
        ...,
        description="この確認で何を切り分けたいか"
    )
    ask_back: str = Field(
        ...,
        description="ユーザが次に返すべき観測/結果"
    )
    # 各項目を“どこから引いたか”を必須にする
    guide_basis: GuideBasisItem = Field(
        ...,
        description="この項目の根拠として参照したガイドchunk"
    )


class LocatingOutput(BaseModel):
    """
    Step: Locating — using tests to isolate the fault and narrow impacted components.
    """
    safety_checks: List[SafetyCheckItem] = Field(
        ...,
        description="必須安全チェック。漏れ防止のため必ず出す。"
    )
    test_in_order: List[LocatingItem] = Field(
        ...,
        description="test、確認項目。"
    )


# ---- Prompts ----
LOCATING_SYSTEM_PROMPT = """
あなたはネットワークトラブルシューティング支援システムの Locating Agent です。

目的:
Identify の結果(事実/キーワード/media_hint)をもとに、
「テストを使用して障害を切り分け、影響を受けるコンポーネントを絞り込む」ための
論理的な順序付き確認手段(診断計画)を作成してください。

制約(重要):
- 根本原因の推定や断定はしない。
- 修正手順や設定変更の提案はしない。
- すべて「確認手段」として順序付きで出す。

マニュアル利用(最重要):
- 提供されたマニュアル抜粋の範囲に基づく内容のみを出す。
- マニュアルに根拠がない確認手段(独自手順/独自テスト名/独自判断基準)は出さない。
- すべての safety/checks には、参照した根拠(guide_basis: start_page/last_page/chapter)を必ず付ける。
- guide_basis.note には、何の根拠として使ったかを短く書く(例: '安全確認', 'テスト手順', '判断基準')。

出力要件(必須):
出力JSONは次の3項目を必ず含むこと。
1) safety_checks: 安全確認の配列
2) checks_in_order: テスト手段の配列

出力ルール:
- 出力は JSON のみ (Pydanticスキーマ準拠)
- 余計なキー、Markdown、説明文、前置きは禁止
"""

LOCATING_USER_PROMPT = """
以下が Identify Agent の出力(事実)です:
{facts}

以下が検索されたマニュアル抜粋です:
{manual}
"""


create_locating_agent = Agent(
    name="Locating_Agent",
    instructions=LOCATING_SYSTEM_PROMPT,
    model="gpt-4.1",
    output_type=LocatingOutput,
)
