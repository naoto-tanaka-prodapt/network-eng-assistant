from typing import List, Optional
from pydantic import BaseModel, Field
from agents import Agent


class GuideBasisItem(BaseModel):
    start_page: str = Field(..., description="参照したガイドチャンクの開始ページ")
    last_page: str = Field(..., description="参照したガイドチャンクの終了ページ")
    chapter: str = Field(..., description="参照したガイドチャンクの章")
    note: Optional[str] = Field(
        default=None,
        description="何の根拠として使ったか(例: '測定値の解釈', '挙動からの切り分け観点')"
    )

class AnalysisOutput(BaseModel):
    """
    Step: Analysing the problem — determining root cause from measurements and system behaviour
    """
    root_cause: str = Field(
        ...,
        description="観測結果から最も合理的に説明できる最小単位の原因"
    )
    reasoning: str = Field(
        ...,
        description="観測(測定/挙動)→解釈→結論の短い説明。"
    )
    guide_basis: List[GuideBasisItem] = Field(
        ...,
        description="本出力の根拠として参照したガイドchunk(最低1つ)"
    )


ANALYZE_SYSTEM_PROMPT = """あなたはネットワークトラブルシューティング支援システムの Analyse Agent です。

目的：
Location Agent が提示したテスト項目に対して、
ネットワークエンジニアが実施・観測した内容(測定値・ログ・挙動)を自然文で入力するので、
その観測結果を解釈し、測定値とシステム挙動に基づいて根本原因(root cause)を特定してください。

制約(重要):
- 修正手順・設定変更・対処案・次に実施すべきテストは提示しない(Action/Localizationの担当)。
- 観測されていない事実を断定しない。推測が混ざる場合は reasoning 内で「仮定」と明記すること。
- ガイド抜粋に根拠がある解釈を優先し、ガイド外の独自知識を混ぜない。
- 根本原因は可能な限り「1つ」に絞る。どうしても絞りきれない場合は、
  reasoning に不確実性と追加で必要となる観測(何が足りないか)を文章で短く書く
  ※ただし、追加観測の“手順”は書かない(何が不足かの説明のみ)。

出力要件：
- 出力は必ず JSON のみ。
- JSONは必ず次の3キーのみを含むこと:
  1) root_cause: 観測結果に基づく根本原因(簡潔に)
  2) reasoning: 観測(測定/挙動)→解釈→結論を短く説明(未観測の断定は禁止)
  3) guide_basis: 根拠としたガイド抜粋の一覧(最低1つ)
     - 各要素は start_page / last_page / chapter / note を含むこと
     - start_page/last_page/chapter は、入力で渡されたガイド抜粋のメタ情報をそのまま使うこと
     - note には「どの観測の解釈に使ったか」を短く書くこと

追加ルール：
- 余計なキーは絶対に出力しない。
- Markdownや説明文、前置きは出力しない(JSONのみ)。
"""

ANALYZE_USER_PROMPT = """
以下がもともとの課題です:

{manual}

以下がネットワークエンジニアがテスト事項に対して確認した内容です

{locating_response}


以下が検索されたマニュアル抜粋です:

{manual}
"""

create_analyze_agent = Agent(
    name="Analyze_Agent",
    instructions=ANALYZE_SYSTEM_PROMPT,
    model="gpt-4.1",
    output_type=AnalysisOutput,
)