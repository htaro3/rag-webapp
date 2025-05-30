"""
【upload.py の役割】
-----------------------------------------------------
- ファイルアップロードを処理するエンドポイント
- アップロードされたファイルを保存し、ベクトルDBに登録
"""

import os
import shutil
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from pathlib import Path

from app.models.schema import DeleteFilesRequest, FileListResponse, FileInfoResponse
from app.services.embed_service import embed_content

router = APIRouter()

# アップロードされたファイルを保存するディレクトリ
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    テキストファイルをアップロードしてベクトルDBに保存
    """
    # .txtファイルのみ受け付ける
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=400, 
            detail="テキストファイル(.txt)のみアップロード可能です"
        )
    
    # ファイルパスを作成
    file_path = UPLOAD_DIR / file.filename
    
    # 既に同名のファイルが存在する場合は上書き
    if file_path.exists():
        file_path.unlink()
    
    # ファイルを保存
    with file_path.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # ファイルの内容を読み込む
    content = file_path.read_text(encoding="utf-8")
    
    # ベクトルDBに保存
    embed_content(content, file.filename)
    
    return {"message": f"ファイル '{file.filename}' がアップロードされ、ベクトルDBに登録されました"}

@router.get("/files", response_model=FileListResponse)
async def list_files():
    """
    アップロードされたファイル一覧を取得
    """
    files = []
    for file_path in UPLOAD_DIR.glob("*.txt"):
        size = file_path.stat().st_size
        modified = file_path.stat().st_mtime
        files.append({
            "filename": file_path.name,
            "size": size,
            "modified": modified
        })
    
    # 更新日時の新しい順にソート
    files.sort(key=lambda x: x["modified"], reverse=True)
    
    return {"files": files}

@router.get("/files/{filename}", response_class=PlainTextResponse)
async def get_file_content(filename: str):
    """
    指定されたファイルの内容を取得
    """
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"ファイル '{filename}' が見つかりません"
        )
    
    # ファイル内容を読み込んで返す
    content = file_path.read_text(encoding="utf-8")
    return content

@router.delete("/files", response_model=FileInfoResponse)
async def delete_files(request: DeleteFilesRequest):
    """
    指定されたファイルを削除し、ベクトルDBからも削除
    """
    if not request.filenames:
        raise HTTPException(
            status_code=400,
            detail="削除するファイル名が指定されていません"
        )
    
    deleted_files = []
    failed_files = []
    
    for filename in request.filenames:
        file_path = UPLOAD_DIR / filename
        
        if not file_path.exists():
            failed_files.append(filename)
            continue
        
        try:
            # ファイルを削除
            file_path.unlink()
            
            # ベクトルDBからも削除（これはサービス層で実装する必要があります）
            from app.services.embed_service import delete_from_vectordb
            delete_from_vectordb(filename)
            
            deleted_files.append(filename)
        except Exception as e:
            print(f"Error deleting {filename}: {e}")
            failed_files.append(filename)
    
    return {
        "message": f"{len(deleted_files)}個のファイルが削除されました",
        "deleted_files": deleted_files,
        "failed_files": failed_files
    }
