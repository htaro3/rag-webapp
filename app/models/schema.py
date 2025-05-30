"""
【schema.py の役割】
-----------------------------------------------------
- FastAPIのAPIエンドポイントで使う、リクエスト/レスポンスのデータ構造を定義。
- `pydantic` を使って構造を明示し、自動バリデーション・ドキュメント生成に活用。
- このファイルでは `/ask` API の入力（質問）と出力（回答）形式を定義する。
"""

from typing import List, Optional
from pydantic import BaseModel

# 質問形式定義
class QuestionInput(BaseModel):
    question: str

# 返答形式定義
class AnswerResponse(BaseModel):
    answer: str

# ファイル情報
class FileInfo(BaseModel):
    filename: str
    size: int
    modified: float

# ファイル一覧レスポンス
class FileListResponse(BaseModel):
    files: List[FileInfo]

# ファイル削除リクエスト
class DeleteFilesRequest(BaseModel):
    filenames: List[str]

# ファイル操作結果レスポンス
class FileInfoResponse(BaseModel):
    message: str
    deleted_files: Optional[List[str]] = None
    failed_files: Optional[List[str]] = None