"""
サーバー起動スクリプト
-----------------------------------------------------
- Pythonのモジュールパスを設定し、FastAPIサーバーを起動する
"""

import sys
import os
import uvicorn

# プロジェクトルートディレクトリをPythonパスに追加
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

if __name__ == "__main__":
    # FastAPIサーバーを起動
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 