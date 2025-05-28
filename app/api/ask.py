"""
【ask.py の役割】
-----------------------------------------------------
- FastAPI のルーティング（エンドポイント）を定義する。
- /ask エンドポイントでユーザーの質問を受け取り、
  ベクトル検索 → Gemini回答生成 → 回答を返す、というRAGの流れを実行。
"""

# FastAPIのルーティングを管理するためのクラス
from fastapi import APIRouter
# 入出力データ型（schema）を読み込み
from models.schema import QuestionInput, AnswerResponse
# ベクトル検索サービスをインポート（関連文書を探す）
from services.search_service import search_related_docs
# 生成サービスをインポート（回答を生成する）
from services.generate_service import generate_answer

# FastAPIのルーターインスタンスを作成
router = APIRouter()

# POSTリクエスト /ask を受け取るルートを定義
@router.post("/ask", response_model=AnswerResponse)
def ask_question(input: QuestionInput):
    # ベクトル検索：関連文書を取得
    related_docs = search_related_docs(input.question)

    # Geminiで回答を生成
    answer = generate_answer(related_docs, input.question)

    # 回答を JSON として返す（FastAPIが自動的にJSONに変換）
    return {"answer": answer}
