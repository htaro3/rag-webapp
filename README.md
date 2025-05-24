# RAG Web Application

このプロジェクトは、Retrieval Augmented Generation (RAG)を利用したWebアプリケーションです。

## 機能
- ドキュメントのアップロード
- ドキュメントの検索
- RAGを利用した質問応答

## 技術スタック
- Backend: FastAPI
- Frontend: React
- Vector Database: Chroma
- LLM: Gemini API

## セットアップ方法

1. リポジトリをクローン
```bash
git clone [repository-url]
cd rag-webapp
```

2. 仮想環境の作成とアクティベート
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

4. 環境変数の設定
```bash
cp .env.example .env
# .envファイルを編集して必要な環境変数を設定
```

5. アプリケーションの起動
```bash
uvicorn app.main:app --reload
```

## 開発者向け情報

プロジェクトの構造：
```
rag-webapp/
├── backend/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── services/
│   └── main.py
├── frontend/
│   ├── src/
├── shared_data/
│   ├── .txt
│   └── chroma_db/
├── .env
├── .gitignore
└── requirements.txt
``` 