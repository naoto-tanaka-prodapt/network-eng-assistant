from typing import List, Optional
from pydantic import BaseModel, Field
from agents import Agent


class GuideBasisItem(BaseModel):
    start_page: str = Field(..., description="参照したガイドチャンクの開始ページ")
    last_page: str = Field(..., description="参照したガイドチャンクの終了ページ")
    chapter: str = Field(..., description="参照したガイドチャンクの章")
    note: Optional[str] = Field(
        default=None,
        description="何の根拠として使ったか(例: '安全確認', '手順', 'ロールバック')"
    )

class ActionOutput(BaseModel):
    """
    Step: Taking corrective action — applying fixes and verifying their effectiveness
    ※本課題では safety/stability/rollback を必須にする
    """
    # 是正措置(実施順)
    fix_steps: List[str] = Field(
        ...,
        description="実施すべき是正措置(順序付き)。設定変更や作業手順を含む場合は簡潔に。"
    )

    # 安全確認(必須)
    safety_checks: List[str] = Field(
        ...,
        description="作業前/作業中に必ず実施する安全確認(必須)。"
    )

    # 影響評価(必須)
    impact_assessment: str = Field(
        ...,
        description="影響範囲・影響度・実施タイミング等の評価(必須)。"
    )

    # ロールバック(必須)
    rollback_plan: List[str] = Field(
        ...,
        description="失敗時に元に戻す手順(必須)。"
    )

    # 根拠(必須)
    guide_basis: List[GuideBasisItem] = Field(
        ...,
        description="本出力の根拠として参照したガイドchunk(最低1つ)"
    )



ACTION_SYSTEM_PROMPT = """
あなたはネットワークトラブルシューティング支援システムの Action Agent です。

目的:
Analyse Agent が特定した root cause(根本原因)と、その根拠(測定・挙動)を入力として、
是正措置(corrective action)を提案してください。
ただし本システムは “retrieval assistant” であるため、ガイド抜粋に基づく内容のみを提示します。

制約(重要):
- ガイド抜粋に根拠がない是正措置は提示しない。
- 原因の再推定はしない(Analysisの担当)。
- 「論理的順序」を守る(準備→実施→(必要なら最小の確認))。
- システム安定性と安全を最優先する(安全確認・影響評価・ロールバックを必ず含める)。

出力要件(必須):
出力JSONは必ず次の5項目を含むこと。空は不可。
1) fix_steps: 是正措置の手順(順序付き)
2) safety_checks: 作業前/作業中の安全確認(必須)
3) impact_assessment: 影響評価(必須)
4) rollback_plan: 失敗時に元に戻す手順(必須)
5) guide_basis: 根拠にしたガイド抜粋の一覧(最低1つ)

根拠の出し方:
- guide_basis には、参照したガイド抜粋の start_page / last_page / chapter を必ず入れる。
- note には、どの出力(安全確認/手順/ロールバック等)の根拠に使ったかを短く書く。

禁止事項:
- 余計なキーを出力しない。
- Markdownや説明文、前置きは出力しない(JSONのみ)。
"""

ACTION_USER_PROMPT = """
以下がAnalyze Agentで特定した原因です

{root_cause}


以下が検索されたマニュアル抜粋です:

{manual}
"""

create_action_agent = Agent(
    name="Action_Agent",
    instructions=ACTION_SYSTEM_PROMPT,
    model="gpt-4.1",
    output_type=ActionOutput,
)
