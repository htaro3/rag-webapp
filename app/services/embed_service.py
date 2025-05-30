"""
【embed_service.py の役割】
-----------------------------------------------------
- テキストコンテンツをベクトル化して、ベクトルDBに保存する
- ベクトルDBからドキュメントを削除する
"""

import os
import re
from typing import List, Dict, Tuple

# ベクトルDBクライアント
from app.core.chromadb_client import collection
# Google AI APIの設定
from app.core.config import LLM_EMBED_MODEL
import google.generativeai as genai

# チャンクサイズの設定
MAX_CHUNK_SIZE = 400
CHUNK_OVERLAP = 50

def detect_qa_format(text: str) -> bool:
    """テキストがQA形式かどうかを検出する"""
    # QA形式の可能性が高いパターン
    qa_patterns = [
        r'Q\d*[:：].*\nA\d*[:：]',  # Q1: ... A1:
        r'Q[:：].*\nA[:：]',        # Q: ... A:
        r'質問\d*[:：].*\n回答\d*[:：]',  # 質問1: ... 回答1:
        r'質問[:：].*\n回答[:：]',        # 質問: ... 回答:
        r'^\s*問[:：].*\n\s*答[:：]',     # 問: ... 答:
        r'###\s*Q[:：].*\nA[:：]',       # ### Q: ... A:
        r'申請方法|アクセス|方法|利用|手続き|手順|ガイド|フロー', # 社内手続き関連キーワード
    ]
    
    for pattern in qa_patterns:
        if re.search(pattern, text, re.MULTILINE):
            return True
    
    return False

def split_qa_into_chunks(text: str) -> List[Dict]:
    """QA形式のテキストを質問と回答のペアごとにチャンク化する"""
    # 異なるQAの区切り記号を検出（---などの区切り線）
    sections = re.split(r'\n---\n', text)
    chunks = []
    
    for section in sections:
        # 複数のQAパターンに対応
        qa_matches = re.search(r'(?:###\s*)?(?:Q\d*[:：]|質問\d*[:：]|問[:：])(.*?)(?:\n)(?:A\d*[:：]|回答\d*[:：]|答[:：])(.*?)(?:\n|$)', section, re.DOTALL)
        
        if qa_matches:
            question = qa_matches.group(1).strip()
            answer = qa_matches.group(2).strip()
            
            # QAペアをメタデータ付きで保存
            chunks.append({
                "text": f"質問: {question}\n回答: {answer}",
                "metadata": {
                    "content_type": "qa_pair", 
                    "question": question,
                    "answer": answer
                }
            })
        else:
            # 従来のパターンでも試す
            qa_splits = re.split(r'(?:^|\n)(?:###\s*)?(?:Q\d*[:：]|質問\d*[:：]|問[:：])', section)
            
            # 最初の分割が空の場合は除去
            if qa_splits and not qa_splits[0].strip():
                qa_splits = qa_splits[1:]
            
            for qa_text in qa_splits:
                if not qa_text.strip():
                    continue
                    
                # 回答部分を分離
                parts = re.split(r'(?:^|\n)(?:A\d*[:：]|回答\d*[:：]|答[:：])', qa_text, 1)
                
                if len(parts) == 2:
                    question = parts[0].strip()
                    answer = parts[1].strip()
                    
                    # QAペアをメタデータ付きで保存
                    chunks.append({
                        "text": f"質問: {question}\n回答: {answer}",
                        "metadata": {
                            "content_type": "qa_pair", 
                            "question": question,
                            "answer": answer
                        }
                    })
                else:
                    # 回答部分が見つからない場合は通常のテキストとして扱う
                    chunks.append({
                        "text": qa_text.strip(),
                        "metadata": {"content_type": "text"}
                    })
    
    return chunks

def split_into_chunks(text: str, max_len=MAX_CHUNK_SIZE, overlap=CHUNK_OVERLAP) -> List[str]:
    """テキストをチャンクに分割する"""
    sentences = text.split("。")
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) <= max_len:
            current += sentence + "。"
        else:
            chunks.append(current.strip())
            current = current[-overlap:] + sentence + "。"
    if current:
        chunks.append(current.strip())
    return chunks

def embed_content(content: str, filename: str) -> int:
    """
    テキストコンテンツをベクトル化して保存する
    
    Args:
        content: 埋め込むテキストコンテンツ
        filename: ファイル名（ドキュメントID生成に使用）
    
    Returns:
        生成されたチャンク数
    """
    # 文書IDはファイル名ベースで定義
    document_id = os.path.splitext(filename)[0]
    
    # コンテンツをチャンクに分割
    chunks = split_into_chunks(content)
    
    # 各チャンクをベクトル化して登録
    for idx, chunk in enumerate(chunks):
        result = genai.embed_content(
            model=LLM_EMBED_MODEL,
            content=chunk,
            task_type="retrieval_document"
        )
        collection.add(
            documents=[chunk],
            ids=[f"{document_id}_chunk_{idx}"],
            metadatas=[{"document_id": document_id, "filename": filename}],
            embeddings=[result["embedding"]]
        )
    
    return len(chunks)

def delete_from_vectordb(filename: str) -> int:
    """
    ファイル名に関連するすべてのチャンクをベクトルDBから削除する
    
    Args:
        filename: 削除するファイル名
    
    Returns:
        削除されたチャンク数
    """
    # ファイル名からドキュメントIDを生成
    document_id = os.path.splitext(filename)[0]
    
    # ドキュメントIDに関連するすべてのチャンクを検索
    results = collection.get(
        where={"document_id": document_id}
    )
    
    # 削除するIDのリストを作成
    ids_to_delete = results["ids"]
    
    # IDリストが空でなければ削除を実行
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
    
    return len(ids_to_delete) 