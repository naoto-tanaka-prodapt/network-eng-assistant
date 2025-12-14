from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from agents import Agent


class CheckType(str, Enum):
    question_to_user = "question_to_user"
    procedure = "procedure"


class GuideBasisItem(BaseModel):
    start_page: str = Field(..., description="参照したガイドチャンクの開始ページ")
    last_page: str = Field(..., description="参照したガイドチャンクの終了ページ")
    chapter: str = Field(..., description="参照したガイドチャンクの章")
    note: Optional[str] = Field(
        default=None,
        description="何の根拠として使ったか(例: '検証観点', '副作用チェック')"
    )


class ValidateItem(BaseModel):
    type: CheckType = Field(..., description="項目の種類(ユーザへの確認質問 / 検証手順)")
    check_content: str = Field(..., description="検証のための確認内容(順序付きで使用)")


class ValidateOutput(BaseModel):
    """
    Step: Validating and documenting results — ensuring no secondary issues remain
    (最小出力:検証手順＋ユーザ確認＋根拠)
    """
    validation_steps: List[ValidateItem] = Field(
        ...,
        description="解決確認と副作用検証のための順序付き手順"
    )
    guide_basis: List[GuideBasisItem] = Field(
        ...,
        description="本出力の根拠として参照したガイドchunk(最低1つ)"
    )


VALIDATE_SYSTEM_PROMPT = """あなたはネットワークトラブルシューティング支援システムの Validate Agent(Verification)です。

目的:
Action Agent が提示した是正措置(fix_steps)を実施した後に、
「問題が解決したこと」と「副作用(secondary issues)が残っていないこと」を確認するための
検証手順を、論理的な順序で提示してください。

制約(重要):
- 新しい修正案や設定変更は提示しない(Actionの担当)。
- 原因の再推定はしない(Analysisの担当)。
- ここで出すのは「確認・検証」のみ。
- 検証は必ず「元の症状(problem_interpretation)が解消したか」を中心にする。
- さらに「副作用が出ていないか」の観点も含める(secondary issues)。

RAG利用(必須):
- ガイド抜粋に基づく検証観点・手順のみを提示する(ガイド外の独自手順を混ぜない)。

出力要件:
- 出力は必ず JSON のみ。
- JSONは次の2キーのみを含むこと:
  1) validation_steps: 検証手順のリスト(順序付き)
     - 各要素は { type, check_content }
     - type は procedure または question_to_user
     - procedure: 実行すべき検証ステップ
     - question_to_user: ユーザに確認すべき質問(体感・再現・影響など)
  2) guide_basis: 根拠にしたガイド抜粋の一覧(最低1つ)
     - 各要素は start_page / last_page / chapter / note を含むこと
     - start_page/last_page/chapter は入力で渡されたガイド抜粋のメタ情報をそのまま使うこと
     - note には「検証」「副作用チェック」など用途を短く書くこと

禁止事項:
- 余計なキーを出力しない。
- Markdownや説明文、前置きは出力しない(JSONのみ)。
"""

VALIDATE_USER_PROMPT = """
以下が問題です

{problem_interpretation}


以下がAnalyze Agentで特定した原因です

{root_cause}


以下が検索されたマニュアル抜粋です:

{manual}
"""

create_validate_agent = Agent(
    name="Validate_Agent",
    instructions=VALIDATE_SYSTEM_PROMPT,
    model="gpt-4.1",
    output_type=ValidateOutput,
)
