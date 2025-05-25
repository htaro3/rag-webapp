# app/core/config.py

import os
from dotenv import load_dotenv

# .envファイルの読み込み（GEMINI_API_KEYなど）
load_dotenv()

# 環境変数からAPIキーを取得
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# キーが設定されていなければエラーで停止
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEYが.envに設定されていません")
