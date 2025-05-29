"""
【schema.py の役割】
-----------------------------------------------------
- FastAPIのAPIエンドポイントで使う、リクエスト/レスポンスのデータ構造を定義。
- `pydantic` を使って構造を明示し、自動バリデーション・ドキュメント生成に活用。
- このファイルでは `/ask` API の入力（質問）と出力（回答）形式を定義する。
"""

from pydantic import BaseModel

# 質問形式定義
class QuestionInput(BaseModel):
    question: str

# 返答形式定義
class AnswerResponse(BaseModel):
    answer: str