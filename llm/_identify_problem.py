# from enum import Enum
# from pydantic import BaseModel, Field
# from config import settings
# from langchain_openai import ChatOpenAI
# from langchain_core.documents import Document
# from langchain_core.runnables import RunnablePassthrough, RunnableLambda
# from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
# from langchain_core.prompts import ChatPromptTemplate
# from libs.vector_search import format_context_from_docs

# # Create a ChatOpenAI model
# model = ChatOpenAI(model="gpt-4.1", api_key=settings.OPENAI_API_KEY)

# # -------------------------
# # Pydantic schema
# # -------------------------
# class ComplaintType(str, Enum):
#     cant_connect = "cant_connect"
#     connection_drops = "connection_drops"
#     network_is_slow = "network_is_slow"

# class IdentificationOutput(BaseModel):
#     problem_interpretation: str = Field(
#         ...,
#         description="アラーム・症状・エラーメッセージを整理した問題の解釈文"
#     )

#     complaint_type: ComplaintType = Field(
#         ...,
#         description="問題分類(cant_connect / connection_drops / network_is_slow)"
#     )

# PROMPT_TEMPLATE = """
# あなたはネットワークトラブルシューティング支援システムのIdentify Agentです。

# 目的：
# ユーザから入力されたアラーム、症状、エラーメッセージを解釈し、「何が起きている問題なのか」を明確に定義してください。
# あなたの役割は「問題の特定（解釈）」までです。原因分析や対処方法の提案は行ってはいけません。

# 実施内容：
# 1. 入力文に含まれるアラーム、症状、エラーメッセージを読み取り、それらを整理して、簡潔で検証可能な問題の解釈文を作成する
# 2. 問題を以下のいずれか1つに分類する
#    - cant_connect(接続できない)
#    - connection_drops(接続が切れる/不安定)
#    - network_is_slow(通信が遅い)

# 注意事項：
# - 推測や断定はせず、入力内容から読み取れる範囲で整理すること
# - 分類が迷わしい場合は、最も近いものを選ぶこと

# 出力ルール：
# - 出力は必ず JSON のみとする
# - 指定されたスキーマ以外のキーや説明文を含めない

# User issue:
# {query}

# {format_instructions}
# """

# def identify_problem(query: str):
#     parser = PydanticOutputParser(pydantic_object=IdentificationOutput)
#     prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE).partial(format_instructions=parser.get_format_instructions())

#     chain = (
#         {
#             "query": RunnablePassthrough()
#         }
#         | prompt
#         | model
#         | parser
#     )

#     response = chain.invoke(query)
#     return response