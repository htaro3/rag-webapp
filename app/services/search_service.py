"""
【search_service.py の役割】
-----------------------------------------------------
- このファイルは、ユーザーの質問をベクトル化し、
  ベクトルDB（chromadb）から"意味が近い文書"を検索して返す処理を行う。
- 後続の回答生成（generate_service.py）に渡す「関連文書リスト」を作成する。
"""

import google.generativeai as genai
from core.config import LLM_API_KEY, LLM_EMBED_MODEL
from core.chromadb_client import collection

# APIキーの設定
genai.configure(api_key=LLM_API_KEY)

# ユーザの質問をベクトル検索し、関連文書を返す
def search_related_docs(query: str, top_k: int = 3) -> list[str]:

    # 質問をベクトル化
    embeding = genai.embed_context(
          model=LLM_EMBED_MODEL,
        context = query,                        # ベクトル化する文章
        task_type = "retrieval_query"           # ベクトル化のタスク
    )["embedding"]

    # ベクトルDBから関連文書を検索
    results = collection.query(
        query_embeddings = [embeding],          # ベクトル化した質問
        n_results = top_k,                      # 返す結果の数
        include = ["documents", "metadatas"]    # 文章本体とメタ情報を返す
    )

    # 関連文書が無ければ空リストを返す
    if not results["metadatas"] or not results["metadatas"][0]:
        return []

    # 検出されたメタ情報から、関連文書IDを取り出す（重複排除）
    doc_ids = {meta["document_id"] for meta in results["metadatas"][0]}

    # 文書IDごとに全文チャンクを取得
    related_docs = []
    for doc_id in doc_ids:
        items = collection.get(where = {"document_id": doc_id})
        related_docs.extend(items["documents"])

    return related_docs
