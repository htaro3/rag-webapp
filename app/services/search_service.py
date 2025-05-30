"""
【search_service.py の役割】
-----------------------------------------------------
- このファイルは、ユーザーの質問をベクトル化し、
  ベクトルDB（chromadb）から"意味が近い文書"を検索して返す処理を行う。
- 後続の回答生成（generate_service.py）に渡す「関連文書リスト」を作成する。
"""

import google.generativeai as genai
import re
from app.core.config import LLM_API_KEY, LLM_EMBED_MODEL
from app.core.chromadb_client import collection, client

# APIキーの設定
genai.configure(api_key=LLM_API_KEY)

def normalize_question(question: str) -> str:
    """質問文の正規化（末尾の？を削除したり、キーワードを抽出）"""
    # 末尾の？や！、。などを削除
    normalized = re.sub(r'[？！。\?!\.]+$', '', question.strip())
    return normalized

def extract_keywords(text: str) -> list:
    """重要なキーワードを抽出する"""
    # 日本語特有の助詞や接続詞を削除するパターン
    stop_words = ['は', 'が', 'の', 'に', 'を', 'で', 'と', 'や', 'へ', 'から', 'より', 'まで', 'について']
    
    # まず、全体を1つのキーワードとして保持
    keywords = [text]
    
    # スペースやカンマで区切られた単語を取得
    words = re.split(r'[\s,、　]+', text)
    
    # 2文字以上の単語を重要とみなす（ストップワードを除く）
    for word in words:
        if len(word) > 1 and word not in stop_words and word not in keywords:
            keywords.append(word)
    
    # キーワードをさらに分解（「有給休暇」→「有給」「休暇」など）
    additional_keywords = []
    for word in keywords.copy():
        if len(word) >= 4:  # 4文字以上の単語を分解
            # 前半と後半に分割（例: 「有給休暇」→「有給」と「休暇」）
            half_length = len(word) // 2
            first_half = word[:half_length]
            second_half = word[half_length:]
            
            # 分割した単語が2文字以上なら追加
            if len(first_half) >= 2 and first_half not in stop_words and first_half not in keywords:
                additional_keywords.append(first_half)
            if len(second_half) >= 2 and second_half not in stop_words and second_half not in keywords:
                additional_keywords.append(second_half)
    
    keywords.extend(additional_keywords)
    return keywords

def get_keyword_priority(keyword: str) -> float:
    """キーワードの重要度を判定する"""
    # 短いキーワードは重要度を下げる
    if len(keyword) <= 2:
        return 0.5
    # 一般的すぎる単語は重要度を下げる
    common_words = ['手続', 'ガイド', '方法', 'マニュアル', '利用', '申請']
    if keyword in common_words:
        return 0.7
    # 長いキーワードは重要度を上げる
    if len(keyword) >= 4:
        return 1.5
    # デフォルトの重要度
    return 1.0

# 直接ファイル名検索を行う関数
def search_by_filename(keywords: list) -> list:
    """キーワードに一致するファイル名を持つドキュメントを検索"""
    matched_docs = []
    matched_ids = set()
    
    # 全ドキュメントを一度に取得
    try:
        all_docs = collection.get()
        if not all_docs["ids"]:
            print("コレクションにドキュメントが見つかりませんでした")
            return []
            
        print(f"コレクション内のドキュメント総数: {len(all_docs['ids'])}")
        
        # 短すぎるキーワードをフィルタリング（3文字未満は除外）
        important_keywords = [kw for kw in keywords if len(kw) >= 3]
        
        # 重要なキーワードがない場合は元のキーワードの先頭3つを使用
        if not important_keywords and keywords:
            important_keywords = sorted(keywords, key=lambda x: len(x), reverse=True)[:3]
        
        # 各ドキュメントのファイル名と内容をチェック
        for i, metadata in enumerate(all_docs["metadatas"]):
            filename = metadata.get("filename", "")
            doc_id = all_docs["ids"][i]
            document_text = all_docs["documents"][i]
            
            # ファイル名と文書内容の両方でマッチングスコアを計算
            filename_matches = []
            content_matches = []
            
            # マッチするキーワードを保存
            for keyword in important_keywords:
                # キーワードの重要度
                priority = get_keyword_priority(keyword)
                
                # ファイル名に含まれるか
                if keyword.lower() in filename.lower():
                    filename_matches.append((keyword, priority))
                
                # 文書内容に含まれるか（QAドキュメントの場合は質問部分を重視）
                if keyword.lower() in document_text.lower():
                    # QAペアで質問部分に含まれる場合はさらに重要度を上げる
                    if "### Q:" in document_text and "### Q:" + keyword in document_text:
                        content_matches.append((keyword, priority * 1.5))
                    else:
                        content_matches.append((keyword, priority))
            
            # スコア計算
            if filename_matches or content_matches:
                # ファイル名マッチのスコア（最大50点）
                filename_score = sum(priority * 15 for _, priority in filename_matches)
                filename_score = min(filename_score, 50)
                
                # 内容マッチのスコア（最大20点）
                content_score = sum(priority * 5 for _, priority in content_matches)
                content_score = min(content_score, 20)
                
                # 基本スコア
                base_score = 10
                
                # 合計スコア（最大80点）
                total_score = base_score + filename_score + content_score
                
                if doc_id not in matched_ids:
                    matched_ids.add(doc_id)
                    matched_docs.append({
                        "text": document_text,
                        "metadata": metadata,
                        "score": total_score
                    })
                    
                    # マッチしたキーワードをログ出力
                    if filename_matches:
                        keywords_str = ', '.join([k for k, _ in filename_matches])
                        print(f"ファイル名キーワード '{keywords_str}' が '{filename}' に一致")
    except Exception as e:
        print(f"ファイル名検索エラー: {e}")
    
    return matched_docs

# ユーザの質問をベクトル検索し、関連文書を返す
def search_related_docs(query: str, top_k: int = 5) -> list[str]:
    # 質問を正規化
    normalized_query = normalize_question(query)
    
    # キーワード抽出
    keywords = extract_keywords(normalized_query)
    print(f"検索キーワード: {keywords}")  # デバッグ用
    
    # コレクションの状態を確認
    try:
        collection_info = collection.get()
        print(f"コレクションの状態: {len(collection_info['ids'])}件のドキュメントが登録済み")
    except Exception as e:
        print(f"コレクション情報取得エラー: {e}")
    
    # 結果を格納するリスト
    scored_docs = []
    
    # 1. まずファイル名に基づく直接検索
    filename_matches = search_by_filename(keywords)
    scored_docs.extend(filename_matches)
    
    # 2. 次にベクトル検索
    try:
        # 質問をベクトル化
        embeding = genai.embed_content(
            model=LLM_EMBED_MODEL,
            content = normalized_query,             # ベクトル化する文章
            task_type = "retrieval_query"           # ベクトル化のタスク
        )["embedding"]

        # ベクトルDBから関連文書を検索
        results = collection.query(
            query_embeddings = [embeding],          # ベクトル化した質問
            n_results = top_k * 3,                  # 結果数を増やして多様性を確保
            include = ["documents", "metadatas", "distances"]    # 文章本体とメタ情報、距離情報を返す
        )
        
        # 検索結果があれば処理
        if results["metadatas"] and results["metadatas"][0]:
            print(f"ベクトル検索結果: {len(results['metadatas'][0])}件")
            
            # 各検索結果をスコア付きでリストに追加
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i]
                
                # ベクトル距離からスコアを計算（距離が小さいほど関連性が高い）
                # 一般的にchromadbの距離は0〜2の範囲に収まることが多い
                distance = results["distances"][0][i] if "distances" in results else 0
                vector_score = max(0, 30 - (distance * 20))  # 距離が0なら30点、距離が1.5以上なら0点
                
                # キーワードマッチングスコア（最大20点）
                keyword_matches = sum(1 for kw in keywords if kw.lower() in doc.lower())
                keyword_score = min(keyword_matches * 4, 20)
                
                # 順位スコア（最大10点）- 上位結果ほど信頼性が高い
                rank_score = max(0, 10 - i)
                
                # 合計スコア（最大60点）
                score = vector_score + keyword_score + rank_score
                
                # QAペアの場合ボーナススコア
                if meta.get("content_type") == "qa_pair":
                    score += 5
                
                # すでに同じドキュメントがあるか確認
                doc_id = meta.get("document_id", "")
                is_duplicate = any(
                    d["metadata"].get("document_id", "") == doc_id 
                    for d in scored_docs
                )
                
                if not is_duplicate:
                    # 質問と元の質問の情報を追加
                    scored_docs.append({
                        "text": f"元の質問: {meta.get('question', '')}\n{doc}" if meta.get("content_type") == "qa_pair" else doc,
                        "metadata": meta,
                        "score": score
                    })
    except Exception as e:
        print(f"ベクトル検索中にエラーが発生しました: {e}")
    
    # スコア順に並べ替え
    scored_docs.sort(key=lambda x: x["score"], reverse=True)
    
    # 関連文書が無ければ空リストを返す
    if not scored_docs:
        print("関連文書が見つかりませんでした")
        return []
    
    # スコア付きの結果をログ出力
    print(f"検索結果 {len(scored_docs)} 件:")
    for i, doc in enumerate(scored_docs[:top_k]):
        doc_preview = doc["text"][:50].replace("\n", " ")
        filename = doc["metadata"].get("filename", "不明")
        print(f"  {i+1}. スコア:{doc['score']} - [{filename}] {doc_preview}...")
    
    # テキストだけのリストに変換して返す
    return [doc["text"] for doc in scored_docs[:top_k]]
