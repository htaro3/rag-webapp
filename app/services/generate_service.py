"""
【generate_service.py の役割】
-----------------------------------------------------
- このファイルは、検索で見つかった文書（文脈）とユーザーの質問を元に、
  生成AIを使って自然な回答文を生成する役割を担う。
"""

import google.generativeai as genai
from core.config import GEMINI_API_KEY, LLM_GEN_MODEL

# APIキーの設定
genai.configure(api_key = GEMINI_API_KEY)

# 関連文章と質問を渡して、自然文で回答を作る
def generate_answer(context_docs: list[str], question: str) -> str:
    # 関連文章を1つのテキスト結合
    context = "\n".join(context_docs).strip()

    # LLMに渡すプロンプトを作成
    prompt = f"""
    以下の関連文章をもとに、ユーザーの質問に回答してください。
    #関連文章:
    {context}
    
    #ユーザーの質問:
    {question}

    #関連文書の内容に沿って、正確かつ簡潔に答えてください。
    """
    # モデルの指定
    model = genai.GenerativeModel(LLM_GEN_MODEL)

    # プロンプトをモデルに渡して、回答を生成
    response = model.generate_content(prompt)

    # 生成された回答を返す
    return response.text.strip() if hasattr(response, "text") else "回答を生成できませんでした。"
