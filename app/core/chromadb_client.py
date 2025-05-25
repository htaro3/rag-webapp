"""
【chromadb_client.pyの役割】
-----------------------------------------------------
- 本ファイルは、ベクトルデータベース（chromadb）の初期設定を行う専用モジュール。
- アプリ内のどこからでも import することで、
    ベクトルの保存先（DB_PATH）を一元管理
    検索対象コレクション（rag_docs）を共通利用
- DBは shared_data/chroma_db にローカル永続化される。
- 意味ベクトルの登録・検索のすべてはこの collection に対して行う。
"""

import os
import chromadb
from chromadb.config import Settings

# ベクトルDBの保存先
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "shared_data", "chroma_db")

# chromadb内で扱うコレクション名
COLLECTION_NAME = "rag_docs"

# chromadbの初期化
client = chromadb.PersistentClient (
    path = DB_PATH,                                  # データベース保存先
    settings = Settings(anonymized_telemetry=False)  # 使用状況の匿名送信を無効化
    )

# rag_docsを取得、無ければ自動作成
collction = client.get_or_crate_collection(COLLECTION_NAME)