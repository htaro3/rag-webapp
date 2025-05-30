"""
【generate_service.py の役割】
-----------------------------------------------------
- このファイルは、検索で見つかった文書（文脈）とユーザーの質問を元に、
  生成AIを使って自然な回答文を生成する役割を担う。
"""

import google.generativeai as genai
from app.core.config import LLM_API_KEY, LLM_GEN_MODEL

# APIキーの設定
genai.configure(api_key=LLM_API_KEY)

# 関連文章と質問を渡して、自然文で回答を作る
def generate_answer(context_docs: list[str], question: str) -> str:
    # 関連文章を1つのテキスト結合
    context = "\n\n".join(context_docs).strip()

    # QAペアが含まれているかチェック
    contains_qa_pairs = "質問:" in context and "回答:" in context
    contains_original_query = "元の質問:" in context
    
    # LLMに渡すプロンプトを作成
    if contains_qa_pairs:
        if contains_original_query:
            # 改良版QA用プロンプト（元の質問情報を活用）
            prompt = f"""
            以下の関連QAデータと、ユーザーの新しい質問を見て、適切な回答を作成してください。

            #関連QAデータ:
            {context}

            #ユーザーの質問:
            {question}

            #指示:
            1. 「元の質問」と「ユーザーの質問」の類似性を考慮して、最も関連性の高いQAペアを特定してください。
            2. 特に「元の質問」がユーザーの質問と似ている場合は、その回答を重視してください。
            3. 回答は具体的かつ正確に作成し、複数のQAペアから情報を組み合わせても構いません。
            4. 関連QAデータにない情報は含めないでください。
            5. マニュアルやガイドラインの正確な手順や連絡先など、具体的な情報を優先して回答に含めてください。
            """
        else:
            # 標準QA用プロンプト
            prompt = f"""
            以下の関連QAデータと、ユーザーの新しい質問を見て、適切な回答を作成してください。

            #関連QAデータ:
            {context}

            #ユーザーの質問:
            {question}

            #指示:
            1. 上記の関連QAデータを参考にして、ユーザーの質問に対する最適な回答を作成してください。
            2. 関連QAデータに直接回答がない場合は、類似の質問と回答を参考にしてください。
            3. 回答は具体的で簡潔に、かつ正確であるようにしてください。
            4. 関連QAデータにない情報は含めないでください。
            5. マニュアルやガイドラインの正確な手順や連絡先など、具体的な情報を優先して回答に含めてください。
            """
    else:
        # 通常テキスト用プロンプト
        prompt = f"""
        以下の関連文章をもとに、ユーザーの質問に回答してください。
        #関連文章:
        {context}
        
        #ユーザーの質問:
        {question}
        
        #関連文書の内容に沿って、正確かつ簡潔に答えてください。具体的な手順や連絡先など、実用的な情報を優先して含めてください。
        """
    
    # モデルの指定とパラメータ設定
    model = genai.GenerativeModel(
        LLM_GEN_MODEL,
        generation_config={
            "temperature": 0.2,  # より事実に基づいた回答のため低めの温度設定
            "top_p": 0.95,
            "top_k": 40,
        }
    )

    # プロンプトをモデルに渡して、回答を生成
    response = model.generate_content(prompt)

    # 生成された回答を返す
    return response.text.strip() if hasattr(response, "text") else "回答を生成できませんでした。"
