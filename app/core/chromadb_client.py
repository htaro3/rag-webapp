"""
【chromadb_client.pyの役割】
-----------------------------------------------------
- 本ファイルは、ベクトルデータベースの初期設定を行う専用モジュール。
- アプリ内のどこからでも import することで、
    ・ベクトルの保存先（VECTOR_DB_DIR）を一元管理
    ・検索対象コレクション（VECTOR_COLLECTION_NAME）を共通利用
- DBは shared_data/chroma_db にローカル永続化される。
- 意味ベクトルの登録・検索のすべてはこの collection に対して行う。
"""

import chromadb
from chromadb.config import Settings
from app.core.config import VECTOR_DB_DIR, VECTOR_COLLECTION_NAME

# chromadbの初期化
client = chromadb.PersistentClient(
    path=VECTOR_DB_DIR,  # ベクトルDBの保存先（.envで設定）
    settings=Settings(anonymized_telemetry=False)  # 使用状況の送信を無効化
)

def get_collection():
    """rag_docsコレクションを取得、無ければ自動作成"""
    return client.get_or_create_collection(VECTOR_COLLECTION_NAME)

# rag_docsを取得、無ければ自動作成
collection = get_collection()