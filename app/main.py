"""
【main.py の役割】
-----------------------------------------------------
- FastAPIアプリ本体を起動するエントリーポイント。
- ルーティング（api/ask.pyで定義したAPI）をこのアプリに統合する。
- uvicornでこのファイルを実行することで、サーバーが起動する。
"""

# FastAPI本体のクラスをインポート（Webアプリの土台）
from fastapi import FastAPI
# api/ask.py で定義したルーター（/askエンドポイント）を読み込む
from api.ask import router as ask_router

# FastAPIアプリケーションのインスタンスを作成
app = FastAPI(
    title="RAG API",                                # ドキュメントタイトル
    description="検索拡張生成 (RAG) によるAI回答API", # ドキュメント説明
    version="1.0.0"                                 # バージョン表記
)

# APIルーターをアプリに組み込み（prefixなし → /ask）
app.include_router(ask_router)
