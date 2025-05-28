"""
【upload.py の役割】
-----------------------------------------------------
- ユーザーがアップロードした.txtファイルを受け取り、
  保存 → チャンク分割 → ベクトル化 → ベクトルDB登録 を行う。
"""

import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from core.config import VECTOR_DB_DIR, VECTOR_COLLECTION_NAME
from core.chromadb_client import collection
import google.generativeai as genai
from core.config import LLM_API_KEY, LLM_EMBED_MODEL



# 初期化
genai.configure(api_key=LLM_API_KEY)
router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# チャンク分割関数
def split_into_chunks(text: str, max_len=400, overlap=50) -> list[str]:
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

@router.post("/upload")
async def upload_text_file(file: UploadFile = File(...)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="テキストファイル(.txt)のみ対応しています。")

    # 保存
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # ファイル読み込み
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # 文書IDはファイル名ベースで定義
    document_id = os.path.splitext(file.filename)[0]
    chunks = split_into_chunks(raw_text)

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
            metadatas=[{"document_id": document_id}],
            embeddings=[result["embedding"]]
        )

    return {"message": f"{file.filename} をアップロード・登録しました。チャンク数: {len(chunks)}"}
