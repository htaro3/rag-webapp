"""
【core/config.py】
- .envファイルを読み込み、アプリ全体で共通使用する設定値を取得するモジュール
- モデル名やAPIキー、DBパスなどを.envに一元化してコード内のハードコーディングを避ける
"""

import os
from dotenv import load_dotenv

# .envファイルの読み込み（API_KEYなど）
load_dotenv()

# 環境変数からAPIキー・モデル設定
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_EMBED_MODEL = os.getenv("LLM_EMBED_MODEL")
LLM_GEN_MODEL = os.getenv("LLM_GEN_MODEL")
VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR")
VECTOR_COLLECTION_NAME = os.getenv("VECTOR_COLLECTION_NAME")

# 必須項目のバリデーション
for name, value in {
    "LLM_API_KEY": LLM_API_KEY,
    "LLM_EMBED_MODEL": LLM_EMBED_MODEL,
    "LLM_GEN_MODEL": LLM_GEN_MODEL,
    "VECTOR_DB_DIR": VECTOR_DB_DIR,
    "VECTOR_COLLECTION_NAME": VECTOR_COLLECTION_NAME,
}.items():
    if not value:
        raise ValueError(f"{name} が .env に設定されていません。")